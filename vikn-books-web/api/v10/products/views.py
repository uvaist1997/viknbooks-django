import datetime
import json
import os
import time
from collections import OrderedDict
import xlrd
import xlwt
from celery.result import AsyncResult
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Max, Prefetch, Q, Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, renderer_classes,authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from xlwt.Formatting import Alignment

from api.v10.branchs.functions import get_branch_settings
from api.v10.brands.serializers import ListSerializer
from api.v10.ledgerPosting.functions import convertOrderdDict
from api.v10.priceLists.serializers import PriceListRestSerializer, PriceListSerializer
from api.v10.products.functions import (
    generate_priceList_serializer_errors,
    generate_serializer_errors,
    get_AllmultyUnits,
    get_Allproducts,
    get_auto_AutoBarcode,
    get_auto_AutoBatchCode,
    get_auto_BatchNo,
    get_auto_id,
    get_auto_priceListid,
    get_auto_ProductBarcode,
    get_ProductCode,
    get_stock,
    query_Allproducts_toExcel,
)
from api.v10.products.serializers import (
    AddItemBarcodeSerializer,
    BarCodeSearchSerializer,
    BatchCodeSearchSerializer,
    ListSerializerforReport,
    ProductbyGrouptSerializer,
    ProductCodeSerializer,
    ProductRestSerializer,
    ProductSearchInvoiceSerializer,
    ProductSearchSerializer,
    ProductSearchShortcutSerializer,
    ProductSearchStockQrySerializer,
    ProductSerializer,
    SingleProductRestSerializer,
    StockSerializer,
    UploadSerializer,
)
from api.v10.products.tasks import import_multyUnit_task, import_product_task
from api.v10.products.utils import in_memory_file_to_temp
from api.v10.workOrder.serializers import Batch_ListSerializer
from brands.models import (
    Activity_Log,
    Batch,
    BranchSettings,
    Brand,
    Brand_Log,
    GeneralSettings,
    PriceList,
    PriceList_Log,
    Product,
    Product_Log,
    ProductBarcode,
    ProductGroup,
    ProductGroup_Log,
    PurchaseDetails,
    PurchaseOrderDetails,
    SalesDetails,
    SalesOrderDetails,
    StockPosting,
    TaxCategory,
    TaxCategory_Log,
    Unit,
    Unit_Log,
)
from main.functions import (
    activity_log,
    convert_to_datetime,
    converted_float,
    get_BranchList,
    get_BranchSettings,
    get_ProductStock,
    get_ProductWareHouseStock,
    get_company,
    get_GeneralSettings,
)
from django.db import IntegrityError, transaction
import sys


@api_view(["POST"])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def check_barcode(request):
    data = request.data
    barcode_arr = data["barcode_arr"]
    arr = barcode_arr.split(",")
    print(arr, "barcode_arr")
    # instance = None
    # if  PriceList.objects.filter(is_deleted=False,pk=pk).exists():
    #     instance = adminpanel_model.Category.objects.get(is_deleted=False,pk=pk)
    # elif ProductBarcode.objects.filter(is_deleted=False,pk=pk).exists():
    #     serialized = CategorySerializer(instance,context={"request":request})

    #     response_data = {
    #         "success" : 6000,
    #         "data" : serialized.data
    # }
    # else:
    #     response_data = {
    #     "success" : 6001,
    #     "message" : 'SundryDebtor is not found'
    # }
    # return Response(response_data,status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def create_product(request):
    try:
        with transaction.atomic():
            today = datetime.datetime.now()
            data = request.data
            CompanyID = data["CompanyID"]
            CompanyID = get_company(CompanyID)
            product_serialized = ProductSerializer(data=request.data)
            ProductImage = data["ProductImage"]
            try:
                ProductImage2 = data["ProductImage2"]
            except:
                ProductImage2 = None
            try:
                ProductImage3 = data["ProductImage3"]
            except:
                ProductImage3 = None
            try:
                ProductImage4 = data["ProductImage4"]
            except:
                ProductImage4 = None
            try:
                ProductImage5 = data["ProductImage5"]
            except:
                ProductImage5 = None
            
            if product_serialized.is_valid():
                CreatedUserID = product_serialized.data["CreatedUserID"]
                BranchID = product_serialized.data["BranchID"]
                ProductName = product_serialized.data["ProductName"]
                DisplayName = product_serialized.data["DisplayName"]
                Description = product_serialized.data["Description"]
                ProductGroupID = product_serialized.data["ProductGroupID"]
                BrandID = product_serialized.data["BrandID"]
                InventoryType = product_serialized.data["InventoryType"]
                VatID = product_serialized.data["VatID"]
                MinimumSalesPrice = product_serialized.data["MinimumSalesPrice"]
                StockMinimum = product_serialized.data["StockMinimum"]
                StockReOrder = product_serialized.data["StockReOrder"]
                StockMaximum = product_serialized.data["StockMaximum"]
                MarginPercent = product_serialized.data["MarginPercent"]
                Active = product_serialized.data["Active"]
                IsRawMaterial = product_serialized.data["IsRawMaterial"]
                IsWeighingScale = product_serialized.data["IsWeighingScale"]
                IsFinishedProduct = product_serialized.data["IsFinishedProduct"]
                IsSales = product_serialized.data["IsSales"]
                IsPurchase = product_serialized.data["IsPurchase"]
                WeighingCalcType = product_serialized.data["WeighingCalcType"]
                PLUNo = product_serialized.data["PLUNo"]
                IsFavourite = product_serialized.data["IsFavourite"]
                GST = product_serialized.data["GST"]
                Tax1 = product_serialized.data["Tax1"]
                Tax2 = product_serialized.data["Tax2"]
                Tax3 = product_serialized.data["Tax3"]
                ProductCode = product_serialized.data["ProductCode"]
                IsKFC = product_serialized.data["IsKFC"]
                HSNCode = product_serialized.data["HSNCode"]
                try:
                    WarrantyType = product_serialized.data["WarrantyType"]
                except:
                    WarrantyType = ""
                try:
                    Warranty = product_serialized.data["Warranty"]
                except:
                    Warranty = ""

                try:
                    is_Service = product_serialized.data["is_Service"]
                except:
                    is_Service = False

                try:
                    is_inclusive = product_serialized.data["is_inclusive"]
                except:
                    is_inclusive = False

                try:
                    priceListDetails = json.loads(data["PriceListDetails"])
                except:
                    priceListDetails = data["PriceListDetails"]
                # =========Barcode Detail=====================
                try:
                    barcodeDetails = json.loads(data["BarcodeDetails"])
                except:
                    barcodeDetails = data["BarcodeDetails"]
                contains_duplicates = False
                barcode_arr = []
                multi_arr = []
                if priceListDetails:
                    for priceListDetail in priceListDetails:
                        Barcode = priceListDetail["Barcode"]
                        UnitID = priceListDetail["UnitID"]
                        if not Barcode == "0":
                            if Barcode != "":
                                bar_dict = {
                                    "Barcode": Barcode,
                                    "UnitID": UnitID,
                                }
                                barcode_arr.append(Barcode)
                                multi_arr.append(bar_dict)

                if barcodeDetails:
                    for i in barcodeDetails:
                        Barcode = i["barcode"]
                        UnitID = i["unit"]
                        if not Barcode == "0":
                            if Barcode != "":
                                bar_dict = {
                                    "Barcode": Barcode,
                                    "UnitID": UnitID,
                                }
                                barcode_arr.append(Barcode)
                                multi_arr.append(bar_dict)

                a_set = set(barcode_arr)
                contains_duplicates = len(barcode_arr) != len(a_set)
                if contains_duplicates == False:
                    if ProductBarcode.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, Barcode__in=barcode_arr
                    ).exists():
                        contains_duplicates = True
                    if get_BranchSettings(CompanyID, "productsForAllBranches"):
                        pricelist_list = PriceList.objects.filter(CompanyID=CompanyID)
                    else:
                        pricelist_list = PriceList.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID
                        )

                    if pricelist_list.filter(Barcode__in=barcode_arr).exists():
                        contains_duplicates = True
                # ==================================
                if not contains_duplicates:
                    Action = "A"

                    ProductID = get_auto_id(Product, BranchID, CompanyID)
                    # ProductCode = get_ProductCode(Product, BranchID,CompanyID)

                    is_nameExist = False
                    is_ProductCodeExist = False

                    # ProductNameLow = ProductName.lower()
                    # ProductCodeLow = ProductCode.lower()

                    productsForAllBranches = get_branch_settings(
                        CompanyID, "productsForAllBranches"
                    )
                    if productsForAllBranches == False or productsForAllBranches == "False":
                        products = Product.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID
                        )
                    else:
                        products = Product.objects.filter(CompanyID=CompanyID)

                    enable_duplicate = get_GeneralSettings(
                        CompanyID, BranchID, "EnableDuplicateProductName"
                    )
                    if (
                        enable_duplicate == False
                        and products.filter(ProductName__iexact=ProductName).exists()
                    ):
                        is_nameExist = True
                    elif enable_duplicate == True and products.filter(ProductName__iexact=ProductName, ProductCode=ProductCode).exists():
                        is_ProductCodeExist = True
                        
                        
                    if products.filter(ProductCode__iexact=ProductCode).exists():
                        is_ProductCodeExist = True

                    # for product in products:
                    #     product_name = product.ProductName
                    #     product_code = product.ProductCode

                    #     productName = product_name.lower()
                    #     productCode = product_code.lower()

                    #     if ProductNameLow == productName:
                    #         is_nameExist = True
                    #     if ProductCodeLow == productCode:
                    #         is_ProductCodeExist = True

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
                            WarrantyType=WarrantyType,
                            Warranty=Warranty,
                            is_Service=is_Service,
                            is_inclusive=is_inclusive,
                            ProductImage=ProductImage,
                            ProductImage2=ProductImage2,
                            ProductImage3=ProductImage3,
                            ProductImage4=ProductImage4,
                            ProductImage5=ProductImage5,
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
                            WarrantyType=WarrantyType,
                            Warranty=Warranty,
                            is_Service=is_Service,
                            is_inclusive=is_inclusive,
                        )

                        # ================BarCode Detail Start ==========
                        try:
                            barcodeDetails = json.loads(data["BarcodeDetails"])
                        except:
                            barcodeDetails = data["BarcodeDetails"]
                        for barcodeDetail in barcodeDetails:
                            # UnitName = priceListDetail['UnitName']
                            Barcode = barcodeDetail["barcode"]
                            if Barcode:
                                UnitID = barcodeDetail["unit"]
                                unit = None
                                if Unit.objects.filter(CompanyID=CompanyID,UnitID=UnitID).exists():
                                    unit = Unit.objects.filter(CompanyID=CompanyID,UnitID=UnitID).first()
                                ProductBarcodeID = get_auto_ProductBarcode(
                                    ProductBarcode, BranchID, CompanyID
                                )
                                # AutoBarcode = get_auto_AutoBarcode(
                                #     PriceList, BranchID, CompanyID)

                                ProductBarcode.objects.create(
                                    ProductBarcodeID=ProductBarcodeID,
                                    BranchID=BranchID,
                                    ProductID=instance,
                                    Barcode=Barcode,
                                    UnitID=unit,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    Action=Action,
                                    CreatedUserID=CreatedUserID,
                                    CompanyID=CompanyID,
                                )
                                # ================BarCode Detail End ==========

                        batch_count = 0
                        for priceListDetail in priceListDetails:
                            # UnitName = priceListDetail['UnitName']
                            UnitID = priceListDetail["UnitID"]
                            SalesPrice = priceListDetail["SalesPrice"]
                            PurchasePrice = priceListDetail["PurchasePrice"]
                            MultiFactor = priceListDetail["MultiFactor"]
                            Barcode = priceListDetail["Barcode"]
                            # AutoBarcode = priceListDetail['AutoBarcode']
                            SalesPrice1 = priceListDetail["SalesPrice1"]
                            SalesPrice2 = priceListDetail["SalesPrice2"]
                            SalesPrice3 = priceListDetail["SalesPrice3"]
                            DefaultUnit = priceListDetail["DefaultUnit"]
                            UnitInSales = priceListDetail["UnitInSales"]
                            UnitInPurchase = priceListDetail["UnitInPurchase"]
                            UnitInReports = priceListDetail["UnitInReports"]
                            MRP = priceListDetail["MRP"]

                            if UnitID:

                                PriceListID = get_auto_priceListid(
                                    PriceList, BranchID, CompanyID
                                )
                                AutoBarcode = get_auto_AutoBarcode(
                                    PriceList, BranchID, CompanyID
                                )

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

                            # if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
                            #     check_EnableProductBatchWise = GeneralSettings.objects.get(
                            #         CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
                            #     if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                            #         if batch_count == 0:
                            #             # BatchNo = get_auto_BatchNo(Batch, BranchID, CompanyID)
                            #             BatchCode = get_auto_AutoBatchCode(
                            #                 Batch, BranchID, CompanyID)
                            #             Batch.objects.create(
                            #                 CompanyID=CompanyID,
                            #                 BranchID=BranchID,
                            #                 ManufactureDate=today,
                            #                 ExpiryDate=today+datetime.timedelta(3650),
                            #                 BatchCode=BatchCode,
                            #                 StockIn=0,
                            #                 StockOut=0,
                            #                 PurchasePrice=PurchasePrice,
                            #                 SalesPrice=SalesPrice,
                            #                 # PurchaseCost=PurchasePrice,
                            #                 PriceListID=PriceListID,
                            #                 ProductID=ProductID,
                            #                 WareHouseID=1,
                            #                 Description=Description,
                            #                 CreatedDate=today,
                            #                 UpdatedDate=today,
                            #                 CreatedUserID=CreatedUserID,
                            #             )
                            #             batch_count += 1

                        # request , company, log_type, user, source, action, message, description
                        activity_log(
                            request._request,
                            CompanyID,
                            "Information",
                            CreatedUserID,
                            "Product",
                            "Create",
                            "Product created successfully.",
                            "Product saved successfully.",
                        )
                        response_data = {
                            "StatusCode": 6000,
                            "message": "Product Created Successfully",
                        }

                        return Response(response_data, status=status.HTTP_200_OK)
                    else:
                        if is_nameExist and is_ProductCodeExist:
                            #  request , company, log_type, user, source, action, message, description
                            activity_log(
                                request._request,
                                CompanyID,
                                "Warning",
                                CreatedUserID,
                                "Product",
                                "Create",
                                "Product created Failed.",
                                "Product Name and ProductCode Already Exist in this Branch.",
                            )
                            response_data = {
                                "StatusCode": 6001,
                                "message": "Product Name and Product Code Already Exist in this Branch",
                            }
                        elif is_nameExist:
                            #  request , company, log_type, user, source, action, message, description
                            activity_log(
                                request._request,
                                CompanyID,
                                "Warning",
                                CreatedUserID,
                                "Product",
                                "Create",
                                "Product created Failed.",
                                "Product Name Already Exist in this Branch.",
                            )
                            response_data = {
                                "StatusCode": 6001,
                                "message": "Product Name Already Exist in this Branch",
                            }
                        elif is_ProductCodeExist:
                            #  request , company, log_type, user, source, action, message, description
                            activity_log(
                                request._request,
                                CompanyID,
                                "Warning",
                                CreatedUserID,
                                "Product",
                                "Create",
                                "Product created Failed.",
                                "Product Code Already Exist in this Branch.",
                            )
                            response_data = {
                                "StatusCode": 6001,
                                "message": "Product Code Already Exist in this Branch",
                            }

                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    response_data = {"StatusCode": 6001, "message": "Barcode is Already Exist"}

                    return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": generate_serializer_errors(product_serialized._errors),
                }

                return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again",
            "err_descrb": err_descrb,
        }

        activity_id = activity_log(
            request._request,
            CompanyID,
            "Error",
            CreatedUserID,
            "Product",
            "Create",
            str(e),
            err_descrb,
        )
        body_params = str(request.data)
        Activity_Log.objects.filter(
            id=activity_id).update(body_params=body_params)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def edit_product(request, pk):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data["CompanyID"]
            CompanyID = get_company(CompanyID)
            CreatedUserID = data["CreatedUserID"]

            today = datetime.datetime.now()
            product_instance = Product.objects.get(CompanyID=CompanyID, pk=pk)
            BranchID = product_instance.BranchID
            ProductID = product_instance.ProductID
            InstanceProductCode = product_instance.ProductCode
            instanceProductName = product_instance.ProductName
            product_serialized = ProductSerializer(data=request.data)
            ProductImage = data["ProductImage"]
            if ProductImage == "" or None:
                ProductImage = None
            if product_serialized.is_valid():
                ProductName = product_serialized.data["ProductName"]
                DisplayName = product_serialized.data["DisplayName"]
                Description = product_serialized.data["Description"]
                ProductGroupID = product_serialized.data["ProductGroupID"]
                BrandID = product_serialized.data["BrandID"]
                InventoryType = product_serialized.data["InventoryType"]
                VatID = product_serialized.data["VatID"]
                MinimumSalesPrice = product_serialized.data["MinimumSalesPrice"]
                StockMinimum = product_serialized.data["StockMinimum"]
                StockReOrder = product_serialized.data["StockReOrder"]
                StockMaximum = product_serialized.data["StockMaximum"]
                MarginPercent = product_serialized.data["MarginPercent"]

                Active = product_serialized.data["Active"]
                IsRawMaterial = product_serialized.data["IsRawMaterial"]
                IsWeighingScale = product_serialized.data["IsWeighingScale"]
                IsFinishedProduct = product_serialized.data["IsFinishedProduct"]
                IsSales = product_serialized.data["IsSales"]
                IsPurchase = product_serialized.data["IsPurchase"]
                WeighingCalcType = product_serialized.data["WeighingCalcType"]
                PLUNo = product_serialized.data["PLUNo"]
                IsFavourite = product_serialized.data["IsFavourite"]
                GST = product_serialized.data["GST"]
                Tax1 = product_serialized.data["Tax1"]
                Tax2 = product_serialized.data["Tax2"]
                Tax3 = product_serialized.data["Tax3"]
                ProductCode = product_serialized.data["ProductCode"]
                IsKFC = product_serialized.data["IsKFC"]
                HSNCode = product_serialized.data["HSNCode"]

                try:
                    WarrantyType = product_serialized.data["WarrantyType"]
                except:
                    WarrantyType = ""
                try:
                    Warranty = product_serialized.data["Warranty"]
                except:
                    Warranty = ""

                try:
                    is_Service = product_serialized.data["is_Service"]
                except:
                    is_Service = False

                try:
                    is_inclusive = product_serialized.data["is_inclusive"]
                except:
                    is_inclusive = False

                try:
                    priceListDetails = json.loads(data["PriceListDetails"])
                except:
                    priceListDetails = data["PriceListDetails"]

                # =========Barcode Detail=====================
                try:
                    barcodeDetails = json.loads(data["BarcodeDetails"])
                except:
                    barcodeDetails = data["BarcodeDetails"]
                contains_duplicates = False
                barcode_arr = []
                multi_arr = []
                if priceListDetails:
                    for priceListDetail in priceListDetails:
                        Barcode = priceListDetail["Barcode"]
                        UnitID = priceListDetail["UnitID"]
                        if not Barcode == "0":
                            if Barcode != "":
                                bar_dict = {
                                    "Barcode": Barcode,
                                    "UnitID": UnitID,
                                }
                                barcode_arr.append(Barcode)
                                multi_arr.append(bar_dict)
                if barcodeDetails:
                    for i in barcodeDetails:
                        Barcode = i["barcode"]
                        UnitID = i["unit"]
                        if not Barcode == "0":
                            if Barcode != "":
                                bar_dict = {
                                    "Barcode": Barcode,
                                    "UnitID": UnitID,
                                }
                                barcode_arr.append(Barcode)
                                multi_arr.append(bar_dict)
                                
                    a_set = set(barcode_arr)

                    contains_duplicates = len(barcode_arr) != len(a_set)
                    if contains_duplicates == False:
                        if (
                            ProductBarcode.objects.filter(
                                CompanyID=CompanyID, BranchID=BranchID, Barcode__in=barcode_arr
                            )
                            .exclude(ProductID=product_instance)
                            .exists()
                        ):
                            contains_duplicates = True

                        if get_BranchSettings(CompanyID, "productsForAllBranches"):
                            pricelist_list = PriceList.objects.filter(CompanyID=CompanyID)
                        else:
                            pricelist_list = PriceList.objects.filter(
                                CompanyID=CompanyID, BranchID=BranchID
                            )

                        if (
                            pricelist_list.filter(Barcode__in=barcode_arr)
                            .exclude(ProductID=product_instance.ProductID)
                            .exists()
                        ):
                            contains_duplicates = True
                    print(contains_duplicates)
                # ==============================
                if not contains_duplicates:

                    Action = "M"

                    is_nameExist = False
                    is_codeExist = False
                    product_ok = True
                    productCode_ok = True

                    # ProductNameLow = ProductName.lower()
                    # ProductCodeLow = ProductCode.lower()

                    products = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID
                    ).exclude(pk=pk)

                    enable_duplicate = get_GeneralSettings(
                        CompanyID, BranchID, "EnableDuplicateProductName"
                    )
                    if (
                        enable_duplicate == False
                        and products.filter(ProductName__iexact=ProductName).exclude(pk=pk).exists()
                    ):
                        is_nameExist = True
                        product_ok = False
                    elif enable_duplicate == True and products.filter(ProductName__iexact=ProductName, BrandID=BrandID).exclude(pk=pk).exists():
                        is_nameExist = True
                        product_ok = False
                    if products.filter(ProductCode__iexact=ProductCode).exists():
                        is_codeExist = True
                        productCode_ok = False
                    # for product in products:
                    #     product_name = product.ProductName
                    #     product_code = str(product.ProductCode)

                    #     productName = product_name.lower()
                    #     productCode = product_code.lower()

                    #     if ProductNameLow == productName:
                    #         is_nameExist = True
                    #         product_ok = False
                    #     if ProductCodeLow == productCode:
                    #         is_codeExist = True
                    #         productCode_ok = False
                    # if instanceProductName.lower() == ProductNameLow:
                    #     product_ok = True
                    # elif is_nameExist == False:
                    #     product_ok = True
                    # if ProductCode.lower() == productCode:
                    #     productCode_ok = False

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
                        product_instance.WarrantyType = WarrantyType
                        product_instance.Warranty = Warranty
                        product_instance.is_Service = is_Service
                        product_instance.is_inclusive = is_inclusive
                        product_instance.ProductCode = ProductCode

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
                            WarrantyType=WarrantyType,
                            Warranty=Warranty,
                            is_Service=is_Service,
                            is_inclusive=is_inclusive,
                        )
                        # ================BarCode Detail Start ==========
                        try:
                            barcodeDetails = json.loads(data["BarcodeDetails"])
                        except:
                            barcodeDetails = data["BarcodeDetails"]
                        barcode_pk_array = []
                        for barcodeDetail in barcodeDetails:
                            Barcode = barcodeDetail["barcode"]
                            if Barcode:
                                UnitID = barcodeDetail["unit"]
                                detailID = barcodeDetail["detailID"]
                                unit = None
                                if UnitID and Unit.objects.filter(CompanyID=CompanyID, UnitID=UnitID).exists():
                                    unit = Unit.objects.filter(
                                        CompanyID=CompanyID, UnitID=UnitID).first()
                                if detailID == 0:
                                    pk = barcodeDetail["id"]
                                    barcode_pk_array.append(pk)
                                    barcode_instance = ProductBarcode.objects.get(
                                        CompanyID=CompanyID, pk=pk
                                    )

                                    barcode_instance.Barcode = Barcode
                                    barcode_instance.UnitID = unit
                                    barcode_instance.Action = Action
                                    barcode_instance.CreatedUserID = CreatedUserID
                                    barcode_instance.UpdatedDate = today

                                    barcode_instance.save()
                                elif detailID == 1:
                                    ProductBarcodeID = get_auto_ProductBarcode(
                                        ProductBarcode, BranchID, CompanyID
                                    )
                                    # AutoBarcode = get_auto_AutoBarcode(
                                    #     PriceList, BranchID, CompanyID)

                                    barcode_instance = ProductBarcode.objects.create(
                                        ProductBarcodeID=ProductBarcodeID,
                                        BranchID=BranchID,
                                        ProductID=product_instance,
                                        Barcode=Barcode,
                                        UnitID=unit,
                                        CreatedDate=today,
                                        UpdatedDate=today,
                                        Action=Action,
                                        CreatedUserID=CreatedUserID,
                                        CompanyID=CompanyID,
                                    )
                                    barcodeId = barcode_instance.id
                                    barcode_pk_array.append(barcodeId)
                                # ================BarCode Detail End ==========

                        try:
                            deleted_datas = data["deleted_data"]
                        except:
                            deleted_datas = []

                        if deleted_datas:
                            for deleted_Data in deleted_datas:
                                deleted_pk = deleted_Data["unq_id"]
                                if (
                                    deleted_pk
                                    and PriceList.objects.filter(pk=deleted_pk).exists()
                                ):
                                    priceLists_instance = PriceList.objects.get(
                                        pk=deleted_pk
                                    ).delete()

                        try:
                            priceListDetails = json.loads(data["PriceListDetails"])
                        except:
                            priceListDetails = data["PriceListDetails"]
                        print(priceListDetails)
                        pk_array = []

                        for priceListDetail in priceListDetails:
                            detailID = priceListDetail["detailID"]
                            if detailID == 0:
                                pk = priceListDetail["id"]
                            UnitID = priceListDetail["UnitID"]
                            SalesPrice = priceListDetail["SalesPrice"]
                            PurchasePrice = priceListDetail["PurchasePrice"]
                            MultiFactor = priceListDetail["MultiFactor"]
                            Barcode = priceListDetail["Barcode"]
                            SalesPrice1 = priceListDetail["SalesPrice1"]
                            SalesPrice2 = priceListDetail["SalesPrice2"]
                            SalesPrice3 = priceListDetail["SalesPrice3"]
                            DefaultUnit = priceListDetail["DefaultUnit"]
                            UnitInSales = priceListDetail["UnitInSales"]
                            UnitInPurchase = priceListDetail["UnitInPurchase"]
                            UnitInReports = priceListDetail["UnitInReports"]
                            MRP = priceListDetail["MRP"]

                            if UnitID:
                                if SalesPrice1 == "":
                                    SalesPrice1 = 0
                                if SalesPrice2 == "":
                                    SalesPrice2 = 0
                                if SalesPrice3 == "":
                                    SalesPrice3 = 0

                                if detailID == 0 and PriceList.objects.filter(pk=pk).exists():
                                    pk_array.append(pk)
                                    print("===============================||")
                                    print(pk)
                                    priceLists_instance = PriceList.objects.get(pk=pk)

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
                                        PriceList, BranchID, CompanyID
                                    )
                                    AutoBarcode = get_auto_AutoBarcode(
                                        PriceList, BranchID, CompanyID
                                    )

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
                                CompanyID=CompanyID, ProductID=ProductID
                            ).exclude(pk__in=pk_array)

                            for PD in price_ToDelete:
                                PD.delete()

                            product_barcode_ToDelete = ProductBarcode.objects.filter(
                                CompanyID=CompanyID, ProductID=product_instance, BranchID=BranchID
                            ).exclude(pk__in=barcode_pk_array)

                            for PBD in product_barcode_ToDelete:
                                PBD.delete()

                        # request , company, log_type, user, source, action, message, description
                        activity_log(
                            request._request,
                            CompanyID,
                            "Information",
                            CreatedUserID,
                            "Product",
                            "Edit",
                            "Product Updated successfully.",
                            "Product Updated successfully.",
                        )

                        response_data = {
                            "StatusCode": 6000,
                            "message": "Product Updated Successfully!!!",
                        }

                        return Response(response_data, status=status.HTTP_200_OK)

                    else:
                        if not product_ok and not productCode_ok:
                            activity_log(
                                request._request,
                                CompanyID,
                                "Warning",
                                CreatedUserID,
                                "Product",
                                "Edit",
                                "Product Updated Failed.",
                                "Product Code and Product Name Already exist with this Branch",
                            )
                            response_data = {
                                "StatusCode": 6001,
                                "message": "Product Name and Product Code Already exist with this Branch",
                            }
                            return Response(response_data, status=status.HTTP_200_OK)
                        elif not product_ok:
                            # request , company, log_type, user, source, action, message, description
                            activity_log(
                                request._request,
                                CompanyID,
                                "Warning",
                                CreatedUserID,
                                "Product",
                                "Edit",
                                "Product Updated Failed.",
                                "Product Name Already exist with this Branch",
                            )
                            response_data = {
                                "StatusCode": 6001,
                                "message": "Product Name Already exist with this Branch",
                            }
                            return Response(response_data, status=status.HTTP_200_OK)
                        elif not productCode_ok:
                            # request , company, log_type, user, source, action, message, description
                            activity_log(
                                request._request,
                                CompanyID,
                                "Warning",
                                CreatedUserID,
                                "Product",
                                "Edit",
                                "Product Updated Failed.",
                                "Product Code Already exist with this Branch",
                            )
                            response_data = {
                                "StatusCode": 6001,
                                "message": "Product Code Already exist with this Branch",
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
                            product_instance.WarrantyType = WarrantyType
                            product_instance.Warranty = Warranty
                            product_instance.is_Service = is_Service
                            product_instance.is_inclusive = is_inclusive
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
                                WarrantyType=WarrantyType,
                                Warranty=Warranty,
                                is_Service=is_Service,
                                is_inclusive=is_inclusive,
                            )

                            try:
                                priceListDetails = json.loads(data["PriceListDetails"])
                            except:
                                priceListDetails = data["PriceListDetails"]

                            pk_array = []

                            for priceListDetail in priceListDetails:

                                pk = priceListDetail["id"]
                                UnitID = priceListDetail["UnitID"]
                                SalesPrice = priceListDetail["SalesPrice"]
                                PurchasePrice = priceListDetail["PurchasePrice"]
                                MultiFactor = priceListDetail["MultiFactor"]
                                Barcode = priceListDetail["Barcode"]
                                SalesPrice1 = priceListDetail["SalesPrice1"]
                                SalesPrice2 = priceListDetail["SalesPrice2"]
                                SalesPrice3 = priceListDetail["SalesPrice3"]
                                DefaultUnit = priceListDetail["DefaultUnit"]
                                UnitInSales = priceListDetail["UnitInSales"]
                                UnitInPurchase = priceListDetail["UnitInPurchase"]
                                UnitInReports = priceListDetail["UnitInReports"]
                                detailID = priceListDetail["detailID"]

                                if SalesPrice1 == "":
                                    SalesPrice1 = 0
                                if SalesPrice2 == "":
                                    SalesPrice2 = 0
                                if SalesPrice3 == "":
                                    SalesPrice3 = 0

                                if detailID == 0:

                                    pk_array.append(pk)

                                    priceLists_instance = PriceList.objects.get(
                                        CompanyID=CompanyID, pk=pk
                                    )

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
                                        PriceList, BranchID, CompanyID
                                    )
                                    AutoBarcode = get_auto_AutoBarcode(
                                        PriceList, BranchID, CompanyID
                                    )

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
                                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
                            ).exclude(pk__in=pk_array)

                            for PD in price_ToDelete:
                                PD.delete()

                            # request , company, log_type, user, source, action, message, description
                            activity_log(
                                request._request,
                                CompanyID,
                                "Information",
                                CreatedUserID,
                                "Product",
                                "Edit",
                                "Product Updated successfully.",
                                "Product Updated successfully.",
                            )
                            response_data = {
                                "StatusCode": 6000,
                                "message": "Product Updated Successfully!!!",
                            }

                            return Response(response_data, status=status.HTTP_200_OK)
                else:
                    response_data = {"StatusCode": 6001, "message": "Barcode is alredy exists"}
                    return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": generate_serializer_errors(product_serialized._errors),
                }
                return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again",
            "err_descrb": err_descrb,
        }

        activity_id = activity_log(
            request._request,
            CompanyID,
            "Error",
            CreatedUserID,
            "Product",
            "edit",
            str(e),
            err_descrb,
        )
        body_params = str(request.data)
        Activity_Log.objects.filter(
            id=activity_id).update(body_params=body_params)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def products(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]
    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data["BranchID"]
        if Product.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Active=True
        ).exists():
            instances = Product.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Active=True
            )
            serialized = ProductRestSerializer(
                instances,
                many=True,
                context={
                    "request": request,
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                },
            )

            # request , company, log_type, user, source, action, message, description
            activity_log(
                request._request,
                CompanyID,
                "Information",
                CreatedUserID,
                "Product",
                "List",
                "Product List Viewed successfully.",
                "Product List Viewed successfully.",
            )
            response_data = {"StatusCode": 6000, "data": serialized.data}

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # request , company, log_type, user, source, action, message, description
            activity_log(
                request._request,
                CompanyID,
                "Warning",
                CreatedUserID,
                "Product",
                "List",
                "Product List Viewed Failed.",
                "Product Not Found in this Branch!",
            )
            response_data = {
                "StatusCode": 6001,
                "message": "Product Not Found in this Branch!!",
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def product(request, pk):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]
    if Product.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = Product.objects.get(CompanyID=CompanyID, pk=pk)
        serialized = SingleProductRestSerializer(
            instance,
            context={
                "request": request,
                "CompanyID": CompanyID,
                "PriceRounding": PriceRounding,
            },
        )

        # request , company, log_type, user, source, action, message, description
        activity_log(
            request._request,
            CompanyID,
            "Information",
            CreatedUserID,
            "Product",
            "View",
            "Product Single Viewed successfully.",
            "Product Single Viewed successfully.",
        )
        response_data = {"StatusCode": 6000, "data": serialized.data}
    else:
        # request , company, log_type, user, source, action, message, description
        activity_log(
            request._request,
            CompanyID,
            "Warning",
            CreatedUserID,
            "Product",
            "View",
            "Product Single Viewed Failed.",
            "Product Not Found.",
        )
        response_data = {"StatusCode": 6001, "message": "Product Not Found!"}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def get_single_product_barcode(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]
    BarCode = data["BarCode"]
    BranchID = data["BranchID"]

    if get_BranchSettings(CompanyID, "productsForAllBranches"):
        pricelist_list = PriceList.objects.filter(CompanyID=CompanyID)
    else:
        pricelist_list = PriceList.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID
        )

    if pricelist_list.filter(AutoBarcode=BarCode).exists():
        ProductID = pricelist_list.get(AutoBarcode=BarCode).ProductID
        instance = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID)
        serialized = SingleProductRestSerializer(
            instance,
            context={
                "request": request,
                "CompanyID": CompanyID,
                "PriceRounding": PriceRounding,
            },
        )
        response_data = {"StatusCode": 6000, "data": serialized.data}
    elif pricelist_list.filter(Barcode=BarCode).exists():
        ProductID = pricelist_list.filter(Barcode=BarCode).first().ProductID
        instance = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID)
        serialized = SingleProductRestSerializer(
            instance,
            context={
                "request": request,
                "CompanyID": CompanyID,
                "PriceRounding": PriceRounding,
            },
        )
        response_data = {"StatusCode": 6000, "data": serialized.data}
    elif Product.objects.filter(
        CompanyID=CompanyID, ProductCode=BarCode, BranchID=BranchID
    ).exists():
        ProductID = Product.objects.get(
            CompanyID=CompanyID, BranchID=BranchID, ProductCode=BarCode
        ).ProductID
        instance = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID)
        serialized = SingleProductRestSerializer(
            instance,
            context={
                "request": request,
                "CompanyID": CompanyID,
                "PriceRounding": PriceRounding,
            },
        )
        response_data = {"StatusCode": 6000, "data": serialized.data}
    else:
        response_data = {"StatusCode": 6001, "message": "Product Not Found!"}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def delete_product(request, pk):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]

    today = datetime.datetime.now()
    product_instance = None
    priceLists_instance = None
    purchaseDetails_exist = None
    purchaseOrderDetails_exist = None
    salesDetails_exist = None
    salesOrderDetails_exist = None
    stockPostings_exist = None

    try:
        selecte_ids = data["selecte_ids"]
    except:
        selecte_ids = []

    if selecte_ids:
        if Product.objects.filter(CompanyID=CompanyID, pk__in=selecte_ids).exists():
            instances = Product.objects.filter(pk__in=selecte_ids)
    else:
        if Product.objects.filter(CompanyID=CompanyID, pk=pk).exists():
            instances = Product.objects.filter(pk=pk)

    # if Product.objects.filter(CompanyID=CompanyID, pk=pk).exists():
    #     product_instance = Product.objects.get(CompanyID=CompanyID, pk=pk)
    if instances:
        for product_instance in instances:
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
            WarrantyType = product_instance.WarrantyType
            Warranty = product_instance.Warranty
            is_Service = product_instance.is_Service
            is_inclusive = product_instance.is_inclusive

            Action = "D"

            purchaseDetails_exist = PurchaseDetails.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID
            ).exists()
            purchaseOrderDetails_exist = PurchaseOrderDetails.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID
            ).exists()
            salesDetails_exist = SalesDetails.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID
            ).exists()
            salesOrderDetails_exist = SalesOrderDetails.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID
            ).exists()
            stockPostings_exist = StockPosting.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID
            ).exists()

            if (
                not purchaseDetails_exist
                and not purchaseOrderDetails_exist
                and not salesDetails_exist
                and not salesOrderDetails_exist
                and not stockPostings_exist
            ):

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
                    WarrantyType=WarrantyType,
                    Warranty=Warranty,
                    is_Service=is_Service,
                    is_inclusive=is_inclusive,
                )

                priceLists_instances = PriceList.objects.filter(
                    CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
                )

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
                # request , company, log_type, user, source, action, message, description
                activity_log(
                    request._request,
                    CompanyID,
                    "Information",
                    CreatedUserID,
                    "Product",
                    "Deleted",
                    "Product Deleted successfully.",
                    "Product Deleted successfully.",
                )

                response_data = {
                    "StatusCode": 6000,
                    "title": "Success",
                    "message": "Product Deleted Successfully!",
                }

            else:
                # request , company, log_type, user, source, action, message, description
                activity_log(
                    request._request,
                    CompanyID,
                    "Warning",
                    CreatedUserID,
                    "Product",
                    "Deleted",
                    "Product Deleted Failed.",
                    "You Cant Delete this Product,this ProductID is using somewhere",
                )
                response_data = {
                    "StatusCode": 6001,
                    "title": "Failed",
                    "message": "You Cant Delete this Product,this ProductID is using somewhere!!",
                }
    else:
        response_data = {
            "StatusCode": 6001,
            "title": "Failed",
            "message": "Product Not Fount!",
        }
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def upload_product(request):
    today = datetime.datetime.now()

    data = request.data
    # serializer = UploadSerializer(data=request.data)
    # if serializer.is_valid():
    BranchID = data["BranchID"]
    CompanyID = data["CompanyID"]
    CreatedUserID = data["CreatedUserID"]
    input_excel = data["file"]
    Type = data["Type"]

    filepath = os.path.join(settings.MEDIA_ROOT, in_memory_file_to_temp(input_excel))

    filepath_url = os.path.join(settings.MEDIA_ROOT, filepath)
    if Type == "Product":
        task = import_product_task.delay(
            filepath_url, CompanyID, CreatedUserID, BranchID, Type
        )
    elif Type == "Multy Unit":
        task = import_multyUnit_task.delay(
            filepath_url, CompanyID, CreatedUserID, BranchID, Type
        )
    task_id = task.id
    # request , company, log_type, user, source, action, message, description
    CompanyID = get_company(CompanyID)
    activity_log(
        request._request,
        CompanyID,
        "Information",
        CreatedUserID,
        "Product",
        "Uploaded",
        "Product Uploaded successfully.",
        "Product Uploaded successfully.",
    )
    response_data = {
        "StatusCode": 6000,
        "task_id": task_id,
        "message": "Product Uploaded Successfully!!!",
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def get_progress(request, task_id):
    result = AsyncResult(task_id)
    response_data = {
        "state": result.state,
        "details": result.info,
        "task_id": task_id,
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
@authentication_classes((JWTTokenUserAuthentication,))
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


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def products_test(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]

    page_number = data["page_no"]
    items_per_page = data["items_per_page"]

    try:
        productsForAllBranches = data["productsForAllBranches"]
    except:
        productsForAllBranches = False

    try:
        WarehouseID = data["WarehouseID"]
    except:
        WarehouseID = 1

    try:
        GroupID = data["GroupID"]
    except:
        GroupID = 0

    try:
        CategoryID = data["CategoryID"]
    except:
        CategoryID = 0

    try:
        BrandID = data["BrandID"]
    except:
        BrandID = 0

    try:
        TaxID = data["TaxID"]
    except:
        TaxID = 0

    try:
        tax_type = data["tax_type"]
    except:
        tax_type = ""

    StatusCode = 6000

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data["BranchID"]
        if page_number and items_per_page:
            if productsForAllBranches:
                product_object = Product.objects.filter(
                    CompanyID=CompanyID, Active=True
                )
            else:
                product_object = Product.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, Active=True
                )
            if product_object:
                if GroupID > 0:
                    if product_object.filter(ProductGroupID=GroupID).exists():
                        product_object = product_object.filter(ProductGroupID=GroupID)
                    else:
                        StatusCode = 6001
                elif CategoryID > 0:
                    if ProductGroup.objects.filter(
                        CategoryID=CategoryID, CompanyID=CompanyID, BranchID=BranchID
                    ).exists():
                        group_instances = ProductGroup.objects.filter(
                            CategoryID=CategoryID,
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                        )
                        grp_ids = group_instances.values_list(
                            "ProductGroupID", flat=True
                        )
                        product_object = product_object.filter(
                            ProductGroupID__in=grp_ids
                        )
                    else:
                        StatusCode = 6001
                # if not productsForAllBranches:
                if BrandID > 0:
                    if product_object.filter(BrandID=BrandID).exists():
                        product_object = product_object.filter(BrandID=BrandID)
                    else:
                        StatusCode = 6001

                if TaxID > 0:
                    if tax_type == "GST":
                        if product_object.filter(GST=TaxID).exists():
                            product_object = product_object.filter(GST=TaxID)
                        else:
                            StatusCode = 6001
                    elif tax_type == "VAT":
                        if product_object.filter(VatID=TaxID).exists():
                            product_object = product_object.filter(VatID=TaxID)
                        else:
                            StatusCode = 6001

                product_sort_pagination = list_pagination(
                    product_object, items_per_page, page_number
                )
                product_serializer = ProductRestSerializer(
                    product_sort_pagination,
                    many=True,
                    context={
                        "request": request,
                        "CompanyID": CompanyID,
                        "PriceRounding": PriceRounding,
                        "WarehouseID": WarehouseID,
                    },
                )
                data = product_serializer.data

                ShowDescription = False
                ShowProductImage = False
                ShowDisplayName = False
                ShowGroupName = False
                ShowBrandName = False
                ShowTaxName = False
                if GeneralSettings.objects.filter(
                    CompanyID=CompanyID, SettingsType="ShowDescription"
                ).exists():
                    general_ins = GeneralSettings.objects.filter(
                        CompanyID=CompanyID, SettingsType="ShowDescription"
                    ).first()
                    ShowDescription = general_ins.SettingsValue

                if GeneralSettings.objects.filter(
                    CompanyID=CompanyID, SettingsType="ShowProductImage"
                ).exists():
                    general_ins = GeneralSettings.objects.filter(
                        CompanyID=CompanyID, SettingsType="ShowProductImage"
                    ).first()
                    ShowProductImage = general_ins.SettingsValue

                if GeneralSettings.objects.filter(
                    CompanyID=CompanyID, SettingsType="ShowDisplayName"
                ).exists():
                    general_ins = GeneralSettings.objects.filter(
                        CompanyID=CompanyID, SettingsType="ShowDisplayName"
                    ).first()
                    ShowDisplayName = general_ins.SettingsValue

                if GeneralSettings.objects.filter(
                    CompanyID=CompanyID, SettingsType="ShowGroupName"
                ).exists():
                    general_ins = GeneralSettings.objects.filter(
                        CompanyID=CompanyID, SettingsType="ShowGroupName"
                    ).first()
                    ShowGroupName = general_ins.SettingsValue

                if GeneralSettings.objects.filter(
                    CompanyID=CompanyID, SettingsType="ShowBrandName"
                ).exists():
                    general_ins = GeneralSettings.objects.filter(
                        CompanyID=CompanyID, SettingsType="ShowBrandName"
                    ).first()
                    ShowBrandName = general_ins.SettingsValue

                if GeneralSettings.objects.filter(
                    CompanyID=CompanyID, SettingsType="ShowTaxName"
                ).exists():
                    general_ins = GeneralSettings.objects.filter(
                        CompanyID=CompanyID, SettingsType="ShowTaxName"
                    ).first()
                    ShowTaxName = general_ins.SettingsValue

                if not data == None and StatusCode == 6000:
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
                    response_data = {"StatusCode": 6001}
            else:
                response_data = {"StatusCode": 6001}
    else:
        response_data = {"StatusCode": 6001}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def products_test_invoice(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]

    page_number = data["page_no"]
    items_per_page = data["items_per_page"]
    try:
        WarehouseID = data["WarehouseID"]
    except:
        WarehouseID = 1
        
    try:
        Type = data['type']
    except:
        Type = "all"

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data["BranchID"]

        if page_number and items_per_page:
            product_object = Product.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Active=True
            )
            if Type == "Sales":
                product_object = product_object.filter(IsSales=True)
            elif Type == "Purchase":
                product_object = product_object.filter(IsPurchase=True)
            product_sort_pagination = list_pagination(
                product_object, items_per_page, page_number
            )
            product_serializer = ProductSearchInvoiceSerializer(
                product_sort_pagination,
                many=True,
                context={
                    "request": request,
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                    "WarehouseID": WarehouseID,
                },
            )
            data = product_serializer.data

            ShowDescription = False
            ShowProductImage = False
            ShowDisplayName = False
            ShowGroupName = False
            ShowBrandName = False
            ShowTaxName = False
            if GeneralSettings.objects.filter(
                CompanyID=CompanyID, SettingsType="ShowDescription"
            ).exists():
                general_ins = GeneralSettings.objects.filter(
                    CompanyID=CompanyID, SettingsType="ShowDescription"
                ).first()
                ShowDescription = general_ins.SettingsValue

            if GeneralSettings.objects.filter(
                CompanyID=CompanyID, SettingsType="ShowProductImage"
            ).exists():
                general_ins = GeneralSettings.objects.filter(
                    CompanyID=CompanyID, SettingsType="ShowProductImage"
                ).first()
                ShowProductImage = general_ins.SettingsValue

            if GeneralSettings.objects.filter(
                CompanyID=CompanyID, SettingsType="ShowDisplayName"
            ).exists():
                general_ins = GeneralSettings.objects.filter(
                    CompanyID=CompanyID, SettingsType="ShowDisplayName"
                ).first()
                ShowDisplayName = general_ins.SettingsValue

            if GeneralSettings.objects.filter(
                CompanyID=CompanyID, SettingsType="ShowGroupName"
            ).exists():
                general_ins = GeneralSettings.objects.filter(
                    CompanyID=CompanyID, SettingsType="ShowGroupName"
                ).first()
                ShowGroupName = general_ins.SettingsValue

            if GeneralSettings.objects.filter(
                CompanyID=CompanyID, SettingsType="ShowBrandName"
            ).exists():
                general_ins = GeneralSettings.objects.filter(
                    CompanyID=CompanyID, SettingsType="ShowBrandName"
                ).first()
                ShowBrandName = general_ins.SettingsValue

            if GeneralSettings.objects.filter(
                CompanyID=CompanyID, SettingsType="ShowTaxName"
            ).exists():
                general_ins = GeneralSettings.objects.filter(
                    CompanyID=CompanyID, SettingsType="ShowTaxName"
                ).first()
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
        response_data = {"StatusCode": 6001}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def products_search(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]
    product_name = data["product_name"]
    length = data["length"]
    try:
        type = data["type"]
    except:
        type = "any"

    try:
        Date = data["Date"]
    except:
        Date = ""

    try:
        WarehouseID = data["WarehouseID"]
    except:
        WarehouseID = 1

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data["BranchID"]
        check_EnableProductBatchWise = False
        check_AllowNegativeStockSales = False
        if GeneralSettings.objects.filter(
            CompanyID=CompanyID,
            BranchID=BranchID,
            SettingsType="AllowNegativeStockSales",
        ).exists():
            check_AllowNegativeStockSales = GeneralSettings.objects.get(
                BranchID=BranchID,
                CompanyID=CompanyID,
                SettingsType="AllowNegativeStockSales",
            ).SettingsValue
        if type == "Sales":
            if Product.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Active=True, IsSales=True
            ).exists():
                if length < 3:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        Active=True,
                        ProductName__icontains=product_name,
                        IsSales=True,
                    )[:10]
                else:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        Active=True,
                        ProductName__icontains=product_name,
                        IsSales=True,
                    )

                product_ids = []
                for p in instances:
                    Stock = 0
                    ProductID = p.ProductID
                    is_Service = p.is_Service
                    check_EnableProductBatchWise = False
                    if GeneralSettings.objects.filter(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        SettingsType="EnableProductBatchWise",
                    ).exists():
                        check_EnableProductBatchWise = GeneralSettings.objects.get(
                            BranchID=BranchID,
                            CompanyID=CompanyID,
                            SettingsType="EnableProductBatchWise",
                        ).SettingsValue
                    if (
                        check_EnableProductBatchWise == "True"
                        or check_EnableProductBatchWise == True
                    ):
                        if Batch.objects.filter(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            ProductID=ProductID,
                            WareHouseID=WarehouseID,
                        ).exists():
                            Batch_ins = Batch.objects.filter(
                                CompanyID=CompanyID,
                                BranchID=BranchID,
                                ProductID=ProductID,
                                WareHouseID=WarehouseID,
                            )
                            total_stockIN = 0
                            total_stockOUT = 0
                            for b in Batch_ins:
                                batch_pricelistID = b.PriceListID
                                batch_MultiFactor = PriceList.objects.get(
                                    CompanyID=CompanyID, PriceListID=batch_pricelistID
                                ).MultiFactor
                                total_stockIN += converted_float(
                                    b.StockIn
                                ) / converted_float(batch_MultiFactor)
                                total_stockOUT += converted_float(
                                    b.StockOut
                                ) / converted_float(batch_MultiFactor)

                            Stock = converted_float(total_stockIN) - converted_float(
                                total_stockOUT
                            )
                        elif StockPosting.objects.filter(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            ProductID=ProductID,
                            WareHouseID=WarehouseID,
                        ):
                            stock_ins = StockPosting.objects.filter(
                                CompanyID=CompanyID,
                                BranchID=BranchID,
                                ProductID=ProductID,
                                WareHouseID=WarehouseID,
                            )
                            total_stockIN = 0
                            total_stockOUT = 0
                            for s in stock_ins:
                                total_stockIN += converted_float(s.QtyIn)
                                total_stockOUT += converted_float(s.QtyOut)

                            Stock = converted_float(total_stockIN) - converted_float(
                                total_stockOUT
                            )
                    else:
                        if StockPosting.objects.filter(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            ProductID=ProductID,
                            WareHouseID=WarehouseID,
                        ):
                            stock_ins = StockPosting.objects.filter(
                                CompanyID=CompanyID,
                                BranchID=BranchID,
                                ProductID=ProductID,
                                WareHouseID=WarehouseID,
                            )
                            total_stockIN = 0
                            total_stockOUT = 0
                            for s in stock_ins:
                                total_stockIN += converted_float(s.QtyIn)
                                total_stockOUT += converted_float(s.QtyOut)

                            Stock = converted_float(total_stockIN) - converted_float(
                                total_stockOUT
                            )
                    if (
                        check_EnableProductBatchWise == "True"
                        or check_EnableProductBatchWise == True
                    ):
                        if GeneralSettings.objects.filter(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            SettingsType="ShowNegativeBatchInSales",
                        ).exists():
                            check_ShowNegativeBatchInSales = (
                                GeneralSettings.objects.get(
                                    BranchID=BranchID,
                                    CompanyID=CompanyID,
                                    SettingsType="ShowNegativeBatchInSales",
                                ).SettingsValue
                            )
                            if (
                                check_ShowNegativeBatchInSales == "False"
                                or check_ShowNegativeBatchInSales == False
                            ):
                                if Stock > 0 or is_Service == True:
                                    product_ids.append(ProductID)
                            else:
                                product_ids.append(ProductID)
                    # else:
                    if (
                        check_AllowNegativeStockSales == "False"
                        or check_AllowNegativeStockSales == False
                    ):

                        if Stock > 0 or is_Service == True:
                            product_ids.append(ProductID)
                        # else:
                        #     product_ids.append(ProductID)
                    else:
                        product_ids.append(ProductID)

                # if check_AllowNegativeStockSales == "True" or check_AllowNegativeStockSales == True and check_EnableProductBatchWise == "False" or check_EnableProductBatchWise == False:
                #     instances12 = Product.objects.filter(
                #         CompanyID=CompanyID, BranchID=BranchID)
                #     for i in instances12:
                #         product_ids.append(i.ProductID)

                if product_ids:
                    if length < 3:
                        instances = Product.objects.filter(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            ProductID__in=product_ids,
                        )
                        for i in instances:
                            print(i.ProductName, "ProductName1")
                    # elif:
                    #     instances = StockPosting.objects.filter(
                    #         CompanyID=CompanyID, BranchID=BranchID, ProductID__in=product_ids)
                    else:
                        instances = instances.filter(ProductID__in=product_ids)
                        for i in instances:
                            print(i.ProductName, "ProductName2")
                    serialized = ProductRestSerializer(
                        instances,
                        many=True,
                        context={
                            "request": request,
                            "CompanyID": CompanyID,
                            "PriceRounding": PriceRounding,
                            "WarehouseID": WarehouseID,
                        },
                    )

                    # request , company, log_type, user, source, action, message, description
                    # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product', 'List', 'Product List Viewed successfully.', 'Product List Viewed successfully.')
                    response_data = {"StatusCode": 6000, "data": serialized.data}

                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Product Not Found with Stock!!",
                    }

                    return Response(response_data, status=status.HTTP_200_OK)
            else:
                # request , company, log_type, user, source, action, message, description
                activity_log(
                    request._request,
                    CompanyID,
                    "Warning",
                    CreatedUserID,
                    "Product",
                    "List",
                    "Product List Viewed Failed.",
                    "Product Not Found in this Branch!",
                )
                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Not Found in this Branch!!",
                }

                return Response(response_data, status=status.HTTP_200_OK)
        elif type == "Purchase":

            if Product.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Active=True, IsPurchase=True
            ).exists():
                if length < 3:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        Active=True,
                        ProductName__icontains=product_name,
                        IsPurchase=True,
                    )[:10]

                else:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        Active=True,
                        ProductName__icontains=product_name,
                        IsPurchase=True,
                    )
                serialized = ProductRestSerializer(
                    instances,
                    many=True,
                    context={
                        "request": request,
                        "CompanyID": CompanyID,
                        "PriceRounding": PriceRounding,
                        "WarehouseID": WarehouseID,
                    },
                )
                # if page_number and items_per_page:

                #     product_object = Product.objects.filter(
                #         CompanyID=CompanyID, BranchID=BranchID, Active=True)

                # request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product', 'List', 'Product List Viewed successfully.', 'Product List Viewed successfully.')
                response_data = {"StatusCode": 6000, "data": serialized.data}

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                activity_log(
                    request._request,
                    CompanyID,
                    "Warning",
                    CreatedUserID,
                    "Product",
                    "List",
                    "Product List Viewed Failed.",
                    "Product Not Found in this Branch!",
                )
                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Not Found in this Branch!!",
                }

                return Response(response_data, status=status.HTTP_200_OK)
        elif type == "WorkOrder":
            if Product.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, is_Service=False
            ).exists():
                if length < 3:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        ProductName__icontains=product_name,
                        is_Service=False,
                    )[:10]
                else:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        ProductName__icontains=product_name,
                        is_Service=False,
                    )
                serialized = ProductRestSerializer(
                    instances,
                    many=True,
                    context={
                        "request": request,
                        "CompanyID": CompanyID,
                        "PriceRounding": PriceRounding,
                        "WarehouseID": WarehouseID,
                    },
                )

                # request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product', 'List', 'Product List Viewed successfully.', 'Product List Viewed successfully.')
                response_data = {"StatusCode": 6000, "data": serialized.data}

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                # request , company, log_type, user, source, action, message, description
                activity_log(
                    request._request,
                    CompanyID,
                    "Warning",
                    CreatedUserID,
                    "Product",
                    "List",
                    "Product List Viewed Failed.",
                    "Product Not Found in this Branch!",
                )
                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Not Found in this Branch!!",
                }

                return Response(response_data, status=status.HTTP_200_OK)
        else:
            if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
                if length < 3:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        ProductName__icontains=product_name,
                    )[:10]
                else:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        ProductName__icontains=product_name,
                    )
                serialized = ProductRestSerializer(
                    instances,
                    many=True,
                    context={
                        "request": request,
                        "CompanyID": CompanyID,
                        "PriceRounding": PriceRounding,
                        "WarehouseID": WarehouseID,
                        "type": type,
                        "Date": Date,
                    },
                )

                # request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product', 'List', 'Product List Viewed successfully.', 'Product List Viewed successfully.')
                response_data = {"StatusCode": 6000, "data": serialized.data}

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                # request , company, log_type, user, source, action, message, description
                activity_log(
                    request._request,
                    CompanyID,
                    "Warning",
                    CreatedUserID,
                    "Product",
                    "List",
                    "Product List Viewed Failed.",
                    "Product Not Found in this Branch!",
                )
                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Not Found in this Branch!!",
                }

                return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def products_search_invoice(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]
    product_name = data["product_name"]
    length = data["length"]
    try:
        type = data["type"]
    except:
        type = "any"

    try:
        Date = data["Date"]
    except:
        Date = ""

    try:
        WarehouseID = data["WarehouseID"]
    except:
        WarehouseID = 1

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data["BranchID"]
        check_EnableProductBatchWise = False
        if type == "Sales":
            if Product.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Active=True, IsSales=True
            ).exists():
                if length < 3:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        Active=True,
                        ProductName__icontains=product_name,
                        IsSales=True,
                    )[:10]
                else:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        Active=True,
                        ProductName__icontains=product_name,
                        IsSales=True,
                    )

                product_ids = []
                for p in instances:
                    Stock = 0
                    ProductID = p.ProductID
                    check_EnableProductBatchWise = False
                    if GeneralSettings.objects.filter(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        SettingsType="EnableProductBatchWise",
                    ).exists():
                        check_EnableProductBatchWise = GeneralSettings.objects.get(
                            BranchID=BranchID,
                            CompanyID=CompanyID,
                            SettingsType="EnableProductBatchWise",
                        ).SettingsValue
                    if (
                        check_EnableProductBatchWise == "True"
                        or check_EnableProductBatchWise == True
                    ):
                        if Batch.objects.filter(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            ProductID=ProductID,
                            WareHouseID=WarehouseID,
                        ).exists():
                            Batch_ins = Batch.objects.filter(
                                CompanyID=CompanyID,
                                BranchID=BranchID,
                                ProductID=ProductID,
                                WareHouseID=WarehouseID,
                            )
                            total_stockIN = 0
                            total_stockOUT = 0
                            for b in Batch_ins:
                                batch_pricelistID = b.PriceListID
                                batch_MultiFactor = PriceList.objects.get(
                                    CompanyID=CompanyID, PriceListID=batch_pricelistID
                                ).MultiFactor
                                total_stockIN += converted_float(
                                    b.StockIn
                                ) / converted_float(batch_MultiFactor)
                                total_stockOUT += converted_float(
                                    b.StockOut
                                ) / converted_float(batch_MultiFactor)

                            Stock = converted_float(total_stockIN) - converted_float(
                                total_stockOUT
                            )
                        elif StockPosting.objects.filter(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            ProductID=ProductID,
                            WareHouseID=WarehouseID,
                        ):
                            stock_ins = StockPosting.objects.filter(
                                CompanyID=CompanyID,
                                BranchID=BranchID,
                                ProductID=ProductID,
                                WareHouseID=WarehouseID,
                            )
                            total_stockIN = 0
                            total_stockOUT = 0
                            for s in stock_ins:
                                total_stockIN += converted_float(s.QtyIn)
                                total_stockOUT += converted_float(s.QtyOut)

                            Stock = converted_float(total_stockIN) - converted_float(
                                total_stockOUT
                            )
                    else:
                        if StockPosting.objects.filter(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            ProductID=ProductID,
                            WareHouseID=WarehouseID,
                        ):
                            stock_ins = StockPosting.objects.filter(
                                CompanyID=CompanyID,
                                BranchID=BranchID,
                                ProductID=ProductID,
                                WareHouseID=WarehouseID,
                            )
                            total_stockIN = 0
                            total_stockOUT = 0
                            for s in stock_ins:
                                total_stockIN += converted_float(s.QtyIn)
                                total_stockOUT += converted_float(s.QtyOut)

                            Stock = converted_float(total_stockIN) - converted_float(
                                total_stockOUT
                            )
                    if (
                        check_EnableProductBatchWise == "True"
                        or check_EnableProductBatchWise == True
                    ):
                        if GeneralSettings.objects.filter(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            SettingsType="ShowNegativeBatchInSales",
                        ).exists():
                            check_ShowNegativeBatchInSales = (
                                GeneralSettings.objects.get(
                                    BranchID=BranchID,
                                    CompanyID=CompanyID,
                                    SettingsType="ShowNegativeBatchInSales",
                                ).SettingsValue
                            )
                            if (
                                check_ShowNegativeBatchInSales == "False"
                                or check_ShowNegativeBatchInSales == False
                            ):
                                if Stock > 0:
                                    product_ids.append(ProductID)
                            else:
                                product_ids.append(ProductID)
                    else:
                        check_AllowNegativeStockSales = False
                        if GeneralSettings.objects.filter(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            SettingsType="AllowNegativeStockSales",
                        ).exists():
                            check_AllowNegativeStockSales = GeneralSettings.objects.get(
                                BranchID=BranchID,
                                CompanyID=CompanyID,
                                SettingsType="AllowNegativeStockSales",
                            ).SettingsValue
                        if (
                            check_AllowNegativeStockSales == "False"
                            or check_AllowNegativeStockSales == False
                        ):
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
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            ProductID__in=product_ids,
                        )
                    else:
                        instances = instances.filter(ProductID__in=product_ids)
                    serialized = ProductSearchInvoiceSerializer(
                        instances,
                        many=True,
                        context={
                            "request": request,
                            "CompanyID": CompanyID,
                            "PriceRounding": PriceRounding,
                            "WarehouseID": WarehouseID,
                        },
                    )

                    # request , company, log_type, user, source, action, message, description
                    # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product', 'List', 'Product List Viewed successfully.', 'Product List Viewed successfully.')
                    response_data = {"StatusCode": 6000, "data": serialized.data}

                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Product Not Found with Stock!!",
                    }

                    return Response(response_data, status=status.HTTP_200_OK)
            else:
                # request , company, log_type, user, source, action, message, description
                activity_log(
                    request._request,
                    CompanyID,
                    "Warning",
                    CreatedUserID,
                    "Product",
                    "List",
                    "Product List Viewed Failed.",
                    "Product Not Found in this Branch!",
                )
                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Not Found in this Branch!!",
                }

                return Response(response_data, status=status.HTTP_200_OK)
        elif type == "Purchase":

            if Product.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Active=True, IsPurchase=True
            ).exists():
                if length < 3:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        Active=True,
                        ProductName__icontains=product_name,
                        IsPurchase=True,
                    )[:10]

                else:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        Active=True,
                        ProductName__icontains=product_name,
                        IsPurchase=True,
                    )
                serialized = ProductSearchInvoiceSerializer(
                    instances,
                    many=True,
                    context={
                        "request": request,
                        "CompanyID": CompanyID,
                        "PriceRounding": PriceRounding,
                        "WarehouseID": WarehouseID,
                    },
                )

                # request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product', 'List', 'Product List Viewed successfully.', 'Product List Viewed successfully.')
                response_data = {"StatusCode": 6000, "data": serialized.data}

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                # request , company, log_type, user, source, action, message, description
                activity_log(
                    request._request,
                    CompanyID,
                    "Warning",
                    CreatedUserID,
                    "Product",
                    "List",
                    "Product List Viewed Failed.",
                    "Product Not Found in this Branch!",
                )
                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Not Found in this Branch!!",
                }

                return Response(response_data, status=status.HTTP_200_OK)
        elif type == "WorkOrder":
            if Product.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, is_Service=False
            ).exists():
                if length < 3:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        ProductName__icontains=product_name,
                        is_Service=False,
                    )[:10]
                else:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        ProductName__icontains=product_name,
                        is_Service=False,
                    )
                serialized = ProductSearchInvoiceSerializer(
                    instances,
                    many=True,
                    context={
                        "request": request,
                        "CompanyID": CompanyID,
                        "PriceRounding": PriceRounding,
                        "WarehouseID": WarehouseID,
                    },
                )

                # request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product', 'List', 'Product List Viewed successfully.', 'Product List Viewed successfully.')
                response_data = {"StatusCode": 6000, "data": serialized.data}

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                # request , company, log_type, user, source, action, message, description
                activity_log(
                    request._request,
                    CompanyID,
                    "Warning",
                    CreatedUserID,
                    "Product",
                    "List",
                    "Product List Viewed Failed.",
                    "Product Not Found in this Branch!",
                )
                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Not Found in this Branch!!",
                }

                return Response(response_data, status=status.HTTP_200_OK)
        else:

            if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
                if length < 3:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        ProductName__icontains=product_name,
                    )[:10]
                else:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        ProductName__icontains=product_name,
                    )
                serialized = ProductSearchInvoiceSerializer(
                    instances,
                    many=True,
                    context={
                        "request": request,
                        "CompanyID": CompanyID,
                        "PriceRounding": PriceRounding,
                        "WarehouseID": WarehouseID,
                        "type": type,
                        "Date": Date,
                    },
                )

                # request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product', 'List', 'Product List Viewed successfully.', 'Product List Viewed successfully.')
                response_data = {"StatusCode": 6000, "data": serialized.data}

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                # request , company, log_type, user, source, action, message, description
                activity_log(
                    request._request,
                    CompanyID,
                    "Warning",
                    CreatedUserID,
                    "Product",
                    "List",
                    "Product List Viewed Failed.",
                    "Product Not Found in this Branch!",
                )
                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Not Found in this Branch!!",
                }

                return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def products_search_shortcut(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]
    product_name = data["product_name"]
    WarehouseID = data["WarehouseID"]
    length = data["length"]

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data["BranchID"]
        if WarehouseID:
            if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
                if length < 3:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID
                    )
                    instances = instances.filter(
                        (Q(ProductName__icontains=product_name))
                        | (Q(ProductCode__icontains=product_name))
                    )[:10]
                else:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID
                    )
                    instances = instances.filter(
                        (Q(ProductName__icontains=product_name))
                        | (Q(ProductCode__icontains=product_name))
                    )
                serialized = ProductSearchShortcutSerializer(
                    instances,
                    many=True,
                    context={
                        "request": request,
                        "CompanyID": CompanyID,
                        "PriceRounding": PriceRounding,
                        "WarehouseID": WarehouseID,
                        "product_name": "product_name",
                    },
                )

                # request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product', 'List', 'Product List Viewed successfully.', 'Product List Viewed successfully.')
        else:
            if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
                if length < 3:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID
                    )
                    instances = instances.filter(
                        (Q(ProductName__icontains=product_name))
                        | (Q(ProductCode__icontains=product_name))
                    )[:10]
                else:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID
                    )
                    instances = instances.filter(
                        (Q(ProductName__icontains=product_name))
                        | (Q(ProductCode__icontains=product_name))
                    )
                serialized = ProductSearchShortcutSerializer(
                    instances,
                    many=True,
                    context={
                        "request": request,
                        "CompanyID": CompanyID,
                        "PriceRounding": PriceRounding,
                        "product_name": "product_name",
                    },
                )

        response_data = {"StatusCode": 6000, "data": serialized.data}

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def products_search_shortcut_barcode(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]
    product_name = data["product_name"]
    WarehouseID = data["WarehouseID"]
    length = data["length"]

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data["BranchID"]
        if WarehouseID:
            if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
                instances = Product.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID
                )
                if Product.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductCode=product_name
                ).exists():
                    if length < 3:
                        instances = Product.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID
                        )
                        instances = instances.filter(
                            (Q(ProductName__icontains=product_name))
                            | (Q(ProductCode__icontains=product_name))
                        )[:10]
                    else:
                        instances = Product.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID
                        )
                        instances = instances.filter(
                            (Q(ProductName__icontains=product_name))
                            | (Q(ProductCode__icontains=product_name))
                        )
                    serialized = ProductSearchShortcutSerializer(
                        instances,
                        many=True,
                        context={
                            "request": request,
                            "CompanyID": CompanyID,
                            "PriceRounding": PriceRounding,
                            "WarehouseID": WarehouseID,
                            "product_name": product_name,
                        },
                    )
                    data = serialized.data
                else:
                    serialized = ProductSearchShortcutSerializer(
                        instances,
                        many=True,
                        context={
                            "request": request,
                            "CompanyID": CompanyID,
                            "PriceRounding": PriceRounding,
                            "WarehouseID": WarehouseID,
                            "product_name": product_name,
                        },
                    )
                    data = []
                    # 435345
                    print(serialized.data, "1751")
                    print(type(serialized.data), "1751")
                    for i in serialized.data:
                        if i["DefBarcode"] == str(product_name):
                            print("qwerty")
                            DefBarcode = i["DefBarcode"]
                            ProductName = i["ProductName"]
                            ProductCode = i["ProductCode"]
                            PurchasePrice = i["PurchasePrice"]
                            SalesPrice = i["SalesPrice"]
                            Quantity = i["Quantity"]
                            dic = {
                                "DefBarcode": DefBarcode,
                                "ProductName": ProductName,
                                "ProductCode": ProductCode,
                                "PurchasePrice": PurchasePrice,
                                "SalesPrice": SalesPrice,
                                "Quantity": Quantity,
                            }
                            data.append(dic)
                # request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product', 'List', 'Product List Viewed successfully.', 'Product List Viewed successfully.')
        else:
            if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
                instances = Product.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID
                )
                if Product.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductCode=product_name
                ).exists():
                    if length < 3:
                        instances = Product.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID
                        )
                        instances = instances.filter(
                            (Q(ProductName__icontains=product_name))
                            | (Q(ProductCode__icontains=product_name))
                        )[:10]
                    else:
                        instances = Product.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID
                        )
                        instances = instances.filter(
                            (Q(ProductName__icontains=product_name))
                            | (Q(ProductCode__icontains=product_name))
                        )
                    serialized = ProductSearchShortcutSerializer(
                        instances,
                        many=True,
                        context={
                            "request": request,
                            "CompanyID": CompanyID,
                            "PriceRounding": PriceRounding,
                            "product_name": "product_name",
                        },
                    )
                    data = serialized.data
                else:
                    serialized = ProductSearchShortcutSerializer(
                        instances,
                        many=True,
                        context={
                            "request": request,
                            "CompanyID": CompanyID,
                            "PriceRounding": PriceRounding,
                            "product_name": "product_name",
                        },
                    )
                    data = []
                    # 435345
                    print(serialized.data, "1751")
                    print(type(serialized.data), "1751")
                    for i in serialized.data:
                        if i["DefBarcode"] == str(product_name):
                            print("qwerty")
                            DefBarcode = i["DefBarcode"]
                            ProductName = i["ProductName"]
                            ProductCode = i["ProductCode"]
                            PurchasePrice = i["PurchasePrice"]
                            SalesPrice = i["SalesPrice"]
                            Quantity = i["Quantity"]
                            dic = {
                                "DefBarcode": DefBarcode,
                                "ProductName": ProductName,
                                "ProductCode": ProductCode,
                                "PurchasePrice": PurchasePrice,
                                "SalesPrice": SalesPrice,
                                "Quantity": Quantity,
                            }
                            data.append(dic)

                # request , company, log_type, user, source, action, message, description
                activity_log(
                    request._request,
                    CompanyID,
                    "Information",
                    CreatedUserID,
                    "Product",
                    "List",
                    "Product List Viewed successfully.",
                    "Product List Viewed successfully.",
                )
        response_data = {"StatusCode": 6000, "data": data}

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def list_productsUnderGroups(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]
    GroupIDs = data["GroupIDs"]
    try:
        WarehouseID = data["WarehouseID"]
    except:
        WarehouseID = 1

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data["BranchID"]
        if Product.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, ProductGroupID__in=GroupIDs
        ).exists():
            instances = Product.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductGroupID__in=GroupIDs
            )
            serialized = ProductbyGrouptSerializer(
                instances,
                many=True,
                context={
                    "request": request,
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                    "WarehouseID": WarehouseID,
                },
            )

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Product Not Found under this Groups",
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def list_productsbyBarcode(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    PriceRounding = data["PriceRounding"]
    Barcode = data["Barcode"]
    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data["BranchID"]
        if get_BranchSettings(CompanyID, "productsForAllBranches"):
            pricelist_list = PriceList.objects.filter(CompanyID=CompanyID)
        else:
            pricelist_list = PriceList.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID
            )

        if PriceList.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, AutoBarcode=Barcode
        ).exists():
            ProductID = (
                PriceList.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, AutoBarcode=Barcode
                )
                .first()
                .ProductID
            )

            if Product.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID
            ).exists():
                instance = Product.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID
                )
                serialized = ProductbyGrouptSerializer(
                    instance,
                    context={
                        "request": request,
                        "CompanyID": CompanyID,
                        "PriceRounding": PriceRounding,
                    },
                )

                response_data = {
                    "StatusCode": 6000,
                    "data": serialized.data,
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Not Found under this Barcode",
                }

                return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Product Not Found under this Barcode",
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def get_product_barcode(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    BranchID = data["BranchID"]
    BarCode = data["BarCode"]
    PriceRounding = data["PriceRounding"]
    try:
        WarehouseID = data["WarehouseID"]
    except:
        WarehouseID = 1
    check_EnableProductBatchWise = False
    if GeneralSettings.objects.filter(
        CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise"
    ).exists():
        check_EnableProductBatchWise = GeneralSettings.objects.get(
            BranchID=BranchID,
            CompanyID=CompanyID,
            SettingsType="EnableProductBatchWise",
        ).SettingsValue
    if BarCode.isnumeric():
        if (
            check_EnableProductBatchWise == "True"
            or check_EnableProductBatchWise == True
        ):
            if Batch.objects.filter(
                CompanyID=CompanyID, BatchCode=BarCode, BranchID=BranchID
            ).exists():
                ProductID = Batch.objects.get(
                    CompanyID=CompanyID, BatchCode=BarCode, BranchID=BranchID
                ).ProductID

                if Product.objects.filter(
                    CompanyID=CompanyID, ProductID=ProductID
                ).exists():
                    instance = Product.objects.get(
                        CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
                    )
                    batch_ins = Batch.objects.get(
                        CompanyID=CompanyID, BranchID=BranchID, BatchCode=BarCode
                    )

                    batch_pricelistID = batch_ins.PriceListID
                    serialized = AddItemBarcodeSerializer(
                        instance,
                        context={
                            "request": request,
                            "CompanyID": CompanyID,
                            "PriceRounding": PriceRounding,
                            "BarCode": BarCode,
                            "WarehouseID": WarehouseID,
                        },
                    )

                    batch_MultiFactor = PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=batch_pricelistID
                    ).MultiFactor
                    StockIn = batch_ins.StockIn
                    StockOut = batch_ins.StockOut
                    # StockIn = converted_float(btach_StockIn) / converted_float(batch_MultiFactor)
                    # StockOut = converted_float(btach_StockOut) / converted_float(batch_MultiFactor)
                    stock = converted_float(StockIn) - converted_float(StockOut)
                    response_data = {
                        "StatusCode": 6000,
                        "data": serialized.data,
                        "BatchCode": BarCode,
                        "Stock": stock,
                    }
                else:
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Product Not Found!",
                    }
            elif PriceList.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, AutoBarcode=BarCode
            ).exists():
                ProductID = PriceList.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, AutoBarcode=BarCode
                ).ProductID
                instance = Product.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
                )
                serialized = AddItemBarcodeSerializer(
                    instance,
                    context={
                        "request": request,
                        "CompanyID": CompanyID,
                        "PriceRounding": PriceRounding,
                        "BarCode": BarCode,
                        "WarehouseID": WarehouseID,
                    },
                )
                response_data = {"StatusCode": 6000, "data": serialized.data}
            elif PriceList.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Barcode=BarCode
            ).exists():
                ProductID = (
                    PriceList.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, Barcode=BarCode
                    )
                    .first()
                    .ProductID
                )
                instance = Product.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
                )
                serialized = AddItemBarcodeSerializer(
                    instance,
                    context={
                        "request": request,
                        "CompanyID": CompanyID,
                        "PriceRounding": PriceRounding,
                        "BarCode": BarCode,
                        "WarehouseID": WarehouseID,
                    },
                )
                response_data = {"StatusCode": 6000, "data": serialized.data}
            elif ProductBarcode.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Barcode=BarCode
            ).exists():

                instance = ProductBarcode.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, Barcode=BarCode
                ).first()
                serialized = AddItemBarcodeSerializer(
                    instance.ProductID,
                    context={
                        "request": request,
                        "CompanyID": CompanyID,
                        "PriceRounding": PriceRounding,
                        "BarCode": BarCode,
                        "WarehouseID": WarehouseID,
                    },
                )
                response_data = {"StatusCode": 6000, "data": serialized.data}

            elif Product.objects.filter(
                CompanyID=CompanyID, ProductCode=BarCode, BranchID=BranchID
            ).exists():
                ProductID = Product.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, ProductCode=BarCode
                ).ProductID
                instance = Product.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
                )
                serialized = AddItemBarcodeSerializer(
                    instance,
                    context={
                        "request": request,
                        "CompanyID": CompanyID,
                        "PriceRounding": PriceRounding,
                        "BarCode": BarCode,
                        "WarehouseID": WarehouseID,
                    },
                )
                response_data = {"StatusCode": 6000, "data": serialized.data}
            else:
                response_data = {"StatusCode": 6001, "message": "Product Not Found!"}

        elif PriceList.objects.filter(
            CompanyID=CompanyID, AutoBarcode=BarCode
        ).exists():
            ProductID = PriceList.objects.get(
                CompanyID=CompanyID, AutoBarcode=BarCode
            ).ProductID
            instance = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID)
            serialized = AddItemBarcodeSerializer(
                instance,
                context={
                    "request": request,
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                    "BarCode": BarCode,
                    "WarehouseID": WarehouseID,
                },
            )
            response_data = {"StatusCode": 6000, "data": serialized.data}
        elif PriceList.objects.filter(CompanyID=CompanyID, Barcode=BarCode).exists():
            ProductID = (
                PriceList.objects.filter(CompanyID=CompanyID, Barcode=BarCode)
                .first()
                .ProductID
            )
            instance = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID)
            serialized = AddItemBarcodeSerializer(
                instance,
                context={
                    "request": request,
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                    "BarCode": BarCode,
                    "WarehouseID": WarehouseID,
                },
            )
            response_data = {"StatusCode": 6000, "data": serialized.data}
        elif ProductBarcode.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Barcode=BarCode
        ).exists():

            instance = ProductBarcode.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Barcode=BarCode
            ).first()
            serialized = AddItemBarcodeSerializer(
                instance.ProductID,
                context={
                    "request": request,
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                    "BarCode": BarCode,
                    "WarehouseID": WarehouseID,
                },
            )
            response_data = {"StatusCode": 6000, "data": serialized.data}

        elif Product.objects.filter(CompanyID=CompanyID, ProductCode=BarCode).exists():
            ProductID = Product.objects.get(
                CompanyID=CompanyID, ProductCode=BarCode
            ).ProductID
            instance = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID)
            serialized = AddItemBarcodeSerializer(
                instance,
                context={
                    "request": request,
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                    "BarCode": BarCode,
                    "WarehouseID": WarehouseID,
                },
            )
            response_data = {"StatusCode": 6000, "data": serialized.data}
        else:
            response_data = {"StatusCode": 6001, "message": "Product Not Found!"}

    else:
        if Product.objects.filter(CompanyID=CompanyID, ProductCode=BarCode).exists():
            ProductID = Product.objects.get(
                CompanyID=CompanyID, ProductCode=BarCode
            ).ProductID
            instance = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID)
            serialized = AddItemBarcodeSerializer(
                instance,
                context={
                    "request": request,
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                    "BarCode": BarCode,
                    "WarehouseID": WarehouseID,
                },
            )
            response_data = {"StatusCode": 6000, "data": serialized.data}
        elif PriceList.objects.filter(CompanyID=CompanyID, Barcode=BarCode).exists():
            ProductID = (
                PriceList.objects.filter(CompanyID=CompanyID, Barcode=BarCode)
                .first()
                .ProductID
            )
            instance = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID)
            serialized = AddItemBarcodeSerializer(
                instance,
                context={
                    "request": request,
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                    "BarCode": BarCode,
                    "WarehouseID": WarehouseID,
                },
            )
            response_data = {"StatusCode": 6000, "data": serialized.data}
        elif ProductBarcode.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Barcode=BarCode
        ).exists():

            instance = ProductBarcode.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Barcode=BarCode
            ).first()
            serialized = AddItemBarcodeSerializer(
                instance.ProductID,
                context={
                    "request": request,
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                    "BarCode": BarCode,
                    "WarehouseID": WarehouseID,
                },
            )
            response_data = {"StatusCode": 6000, "data": serialized.data}
        else:
            response_data = {"StatusCode": 6001, "message": "Product Not Found!"}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def products_search_batch(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]
    product_name = data["product_name"]
    length = data["length"]
    type = data["type"]

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data["BranchID"]

        if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            if length < 3:
                instances = Product.objects.filter(
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    ProductName__icontains=product_name,
                )[:10]
            else:
                instances = Product.objects.filter(
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    ProductName__icontains=product_name,
                )

            product_ids = []
            for p in instances:
                ProductID = p.ProductID
                if Batch.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID
                ).exists():
                    batch_ins = Batch.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID
                    )
                    Stock = 0
                    TotalStockIn = 0
                    TotalStockOut = 0
                    for b in batch_ins:
                        TotalStockIn += converted_float(b.StockIn)
                        TotalStockOut += converted_float(b.StockOut)

                    Stock = converted_float(TotalStockIn) - converted_float(
                        TotalStockOut
                    )
                    if converted_float(Stock) > 0:
                        product_ids.append(ProductID)

            instances = Product.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID__in=product_ids
            )

            serialized = ProductRestSerializer(
                instances,
                many=True,
                context={
                    "request": request,
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                },
            )

            response_data = {"StatusCode": 6000, "data": serialized.data}

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Product Not Found in this Branch!!",
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def products_update(request):
    data = request.data
    today = datetime.datetime.now()
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    ShowDescription = data["ShowDescription"]
    ShowProductImage = data["ShowProductImage"]
    ShowDisplayName = data["ShowDisplayName"]
    ShowGroupName = data["ShowGroupName"]
    ShowBrandName = data["ShowBrandName"]
    ShowTaxName = data["ShowTaxName"]

    print("ShowDescription########")
    print(ShowDescription)

    def max_id():
        general_settings_id = GeneralSettings.objects.filter(
            CompanyID=CompanyID
        ).aggregate(Max("GeneralSettingsID"))
        general_settings_id = general_settings_id.get("GeneralSettingsID__max", 0)
        general_settings_id += 1
        return general_settings_id

    if not GeneralSettings.objects.filter(
        CompanyID=CompanyID, SettingsType="ShowDescription"
    ).exists():
        Action = "A"
        GeneralSettings.objects.create(
            CompanyID=CompanyID,
            GeneralSettingsID=max_id(),
            SettingsType="ShowDescription",
            SettingsValue=ShowDescription,
            BranchID=1,
            GroupName="Inventory",
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            Action=Action,
        )
    else:
        Action = "M"
        GeneralSettings.objects.filter(
            CompanyID=CompanyID, SettingsType="ShowDescription"
        ).update(
            SettingsValue=ShowDescription,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            Action=Action,
        )
    if not GeneralSettings.objects.filter(
        CompanyID=CompanyID, SettingsType="ShowProductImage"
    ).exists():
        GeneralSettings.objects.create(
            CompanyID=CompanyID,
            GeneralSettingsID=max_id(),
            SettingsType="ShowProductImage",
            SettingsValue=ShowProductImage,
            BranchID=1,
            GroupName="Inventory",
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            Action=Action,
        )
    else:
        GeneralSettings.objects.filter(
            CompanyID=CompanyID, SettingsType="ShowProductImage"
        ).update(
            SettingsValue=ShowProductImage,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            Action=Action,
        )
    if not GeneralSettings.objects.filter(
        CompanyID=CompanyID, SettingsType="ShowDisplayName"
    ).exists():
        GeneralSettings.objects.create(
            CompanyID=CompanyID,
            GeneralSettingsID=max_id(),
            SettingsType="ShowDisplayName",
            SettingsValue=ShowDisplayName,
            BranchID=1,
            GroupName="Inventory",
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            Action=Action,
        )
    else:
        GeneralSettings.objects.filter(
            CompanyID=CompanyID, SettingsType="ShowDisplayName"
        ).update(
            SettingsValue=ShowDisplayName,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            Action=Action,
        )

    if not GeneralSettings.objects.filter(
        CompanyID=CompanyID, SettingsType="ShowGroupName"
    ).exists():
        GeneralSettings.objects.create(
            CompanyID=CompanyID,
            GeneralSettingsID=max_id(),
            SettingsType="ShowGroupName",
            SettingsValue=ShowGroupName,
            BranchID=1,
            GroupName="Inventory",
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            Action=Action,
        )
    else:
        GeneralSettings.objects.filter(
            CompanyID=CompanyID, SettingsType="ShowGroupName"
        ).update(
            SettingsValue=ShowGroupName,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            Action=Action,
        )
    if not GeneralSettings.objects.filter(
        CompanyID=CompanyID, SettingsType="ShowBrandName"
    ).exists():
        GeneralSettings.objects.create(
            CompanyID=CompanyID,
            GeneralSettingsID=max_id(),
            SettingsType="ShowBrandName",
            SettingsValue=ShowBrandName,
            BranchID=1,
            GroupName="Inventory",
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            Action=Action,
        )
    else:
        GeneralSettings.objects.filter(
            CompanyID=CompanyID, SettingsType="ShowBrandName"
        ).update(
            SettingsValue=ShowBrandName,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            Action=Action,
        )
    if not GeneralSettings.objects.filter(
        CompanyID=CompanyID, SettingsType="ShowTaxName"
    ).exists():
        GeneralSettings.objects.create(
            CompanyID=CompanyID,
            GeneralSettingsID=max_id(),
            SettingsType="ShowTaxName",
            SettingsValue=ShowTaxName,
            BranchID=1,
            GroupName="Inventory",
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            Action=Action,
        )
    else:
        GeneralSettings.objects.filter(
            CompanyID=CompanyID, SettingsType="ShowTaxName"
        ).update(
            SettingsValue=ShowTaxName,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            Action=Action,
        )

    response_data = {
        "StatusCode": 6000,
        "message": "Successfully Updated",
    }

    return Response(response_data, status=status.HTTP_200_OK)


# reportssssssssssssssssssssssssssssssssssssssssssssssssssssss
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def product_analysis_report(request):
    start_time = time.time()
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    PriceRounding = data["PriceRounding"]
    ProductFilter = data["ProductFilter"]
    StockFilter = data["StockFilter"]
    ProductID = data["ProductID"]
    CategoryID = data["CategoryID"]
    GroupID = data["GroupID"]
    WareHouseID = data["WareHouseID"]
    Barcode = data["Barcode"]
    try:
        page_number = data["page_no"]
    except:
        page_number = ""

    try:
        items_per_page = data["items_per_page"]
    except:
        items_per_page = ""

    serialized1 = ListSerializerforReport(data=request.data)

    if serialized1.is_valid():
        BranchID = serialized1.data["BranchID"]
        FromDate = serialized1.data["FromDate"]
        ToDate = serialized1.data["ToDate"]

        stockDatas = []
        stockPosting_instances = None
        StatusCode = 6000
        # warehouse filter

        # stock posting filter using warehouse id
        if WareHouseID > 0:
            if StockPosting.objects.filter(
                CompanyID=CompanyID,
                BranchID=BranchID,
                WareHouseID=WareHouseID,
                Date__gte=FromDate,
                Date__lte=ToDate,
            ).exists():
                stockPosting_instances = StockPosting.objects.filter(
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    WareHouseID=WareHouseID,
                    Date__gte=FromDate,
                    Date__lte=ToDate,
                )
        else:
            # stock posting filter without warehouse id
            if StockPosting.objects.filter(
                CompanyID=CompanyID,
                BranchID=BranchID,
                Date__gte=FromDate,
                Date__lte=ToDate,
            ).exists():
                stockPosting_instances = StockPosting.objects.filter(
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    Date__gte=FromDate,
                    Date__lte=ToDate,
                )

        if stockPosting_instances:
            # if specific product
            if ProductID > 0:
                stockPosting_instances = stockPosting_instances.filter(
                    ProductID=ProductID
                )

            # category filter
            elif CategoryID > 0:
                # product group filter using category id
                if ProductGroup.objects.filter(
                    CategoryID=CategoryID, CompanyID=CompanyID, BranchID=BranchID
                ).exists():
                    group_instances = ProductGroup.objects.filter(
                        CategoryID=CategoryID, CompanyID=CompanyID, BranchID=BranchID
                    )
                    list_product_id = []
                    for group_i in group_instances:
                        ProductGroupID = group_i.ProductGroupID
                        # product filter using product group id
                        if Product.objects.filter(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            ProductGroupID=ProductGroupID,
                        ).exists():
                            # stock posting instances using product id with category
                            cat_prdids = [
                                product
                                for product in Product.objects.filter(
                                    CompanyID=CompanyID,
                                    BranchID=BranchID,
                                    ProductGroupID=ProductGroupID,
                                )
                                .values_list("ProductID", flat=True)
                                .distinct()
                            ]
                            # stock posting instances using product id with category
                            list_product_id += cat_prdids
                    print(">>>>>>>>>>>>>>>>>>>>>")
                    print(list_product_id)
                    stockPosting_instances = stockPosting_instances.filter(
                        ProductID__in=list_product_id
                    )

            # product group filter
            elif GroupID > 0:
                if Product.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductGroupID=GroupID
                ).exists():
                    grp_prdids = [
                        product
                        for product in Product.objects.filter(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            ProductGroupID=GroupID,
                        )
                        .values_list("ProductID", flat=True)
                        .distinct()
                    ]
                    # grp_prdids = []
                    # for product_i in product_instances:
                    #     ProductID = product_i.ProductID
                    #     grp_prdids.append(ProductID)
                    stockPosting_instances = stockPosting_instances.filter(
                        ProductID__in=grp_prdids
                    )

            # barcode filter
            elif Barcode:
                if PriceList.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, AutoBarcode=Barcode
                ).exists():
                    ProductID = PriceList.objects.get(
                        CompanyID=CompanyID, BranchID=BranchID, AutoBarcode=Barcode
                    ).ProductID

                    stockPosting_instances = stockPosting_instances.filter(
                        ProductID=ProductID
                    )
                elif PriceList.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, Barcode=Barcode
                ).exists():
                    ProductID = (
                        PriceList.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, Barcode=Barcode
                        )
                        .first()
                        .ProductID
                    )
                    stockPosting_instances = stockPosting_instances.filter(
                        ProductID=ProductID
                    )
                elif Product.objects.filter(
                    CompanyID=CompanyID, ProductCode=Barcode, BranchID=BranchID
                ).exists():
                    ProductID = Product.objects.get(
                        CompanyID=CompanyID, BranchID=BranchID, ProductCode=Barcode
                    ).ProductID
                    stockPosting_instances = stockPosting_instances.filter(
                        ProductID=ProductID
                    )
                else:
                    StatusCode = 6001

            total_stock_instance = (
                stockPosting_instances.values("ProductID")
                .annotate(TotalStock=Sum("QtyIn") - Sum("QtyOut"))
                .order_by("ProductID")
            )

            # product id with stock
            final_product_instance = list(
                total_stock_instance.values_list("ProductID", flat=True).distinct()
            )

            if page_number and items_per_page:
                product_instances = Product.objects.filter(
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    ProductID__in=final_product_instance,
                )
                product_sort_pagination = list_pagination(
                    product_instances, items_per_page, page_number
                )
            # else:
            #     product_sort_pagination = Product.objects.filter(
            #         CompanyID=CompanyID, BranchID=BranchID, ProductID__in=final_product_instance)
            print("--- %s seconds ---" % (time.time() - start_time))
            stockSerializer = StockSerializer(
                product_sort_pagination,
                many=True,
                context={
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                    "ToDate": ToDate,
                    "FromDate": FromDate,
                },
            )

            jsnDatas = stockSerializer.data
            for i in jsnDatas:
                ProductCode = i["ProductCode"]
                ProductID = i["ProductID"]
                ProductName = i["ProductName"]
                PurchasePrice = i["PurchasePrice"]
                SalesPrice = i["SalesPrice"]
                UnitName = i["UnitName"]
                BaseUnitName = i["BaseUnitName"]
                is_BasicUnit = i["is_BasicUnit"]
                MultiFactor = i["MultiFactor"]

                for t in total_stock_instance:
                    ProductID_inArr = t["ProductID"]

                    CurrentBaseStock = t["TotalStock"]
                    total_stock = CurrentBaseStock
                    if is_BasicUnit == False:
                        if MultiFactor:
                            total_stock = converted_float(
                                CurrentBaseStock
                            ) / converted_float(MultiFactor)

                    if ProductID == ProductID_inArr:
                        TotalAvgValueOpening = 0
                        OpeningAvgRate = 0
                        OpeningStock = 0
                        PurchaseInvoiceStock = 0
                        if StockPosting.objects.filter(
                            ProductID=ProductID, Date__lt=FromDate, CompanyID=CompanyID
                        ).exists():
                            if WareHouseID == 0:
                                stock_instance_OS = StockPosting.objects.filter(
                                    ProductID=ProductID,
                                    Date__lt=FromDate,
                                    CompanyID=CompanyID,
                                ).exclude(VoucherType="ST")
                            else:
                                stock_instance_OS = StockPosting.objects.filter(
                                    ProductID=ProductID,
                                    Date__lt=FromDate,
                                    CompanyID=CompanyID,
                                )
                            OpeningQtyInRate = 0
                            OpeningQtyOutTot = 0
                            OpeningQtyInTot = 0

                            for si in stock_instance_OS:
                                OpeningQtyInRate += converted_float(
                                    si.QtyIn
                                ) * converted_float(si.Rate)
                                OpeningQtyInTot += converted_float(si.QtyIn)
                                OpeningQtyOutTot += converted_float(si.QtyOut)

                            OpeningStock = converted_float(
                                OpeningQtyInTot
                            ) - converted_float(OpeningQtyOutTot)

                            if OpeningQtyInTot > 0:
                                OpeningAvgRate = converted_float(
                                    OpeningQtyInRate
                                ) / converted_float(OpeningQtyInTot)

                            TotalAvgValueOpening += converted_float(
                                OpeningStock
                            ) * converted_float(OpeningAvgRate)

                        # closing stock
                        TotalAvgValueClosing = 0
                        ClosingAvgRate = 0

                        if StockPosting.objects.filter(
                            ProductID=ProductID, Date__lte=ToDate, CompanyID=CompanyID
                        ).exists():
                            if WareHouseID == 0:
                                stock_instance_CS = StockPosting.objects.filter(
                                    ProductID=ProductID,
                                    Date__lte=ToDate,
                                    CompanyID=CompanyID,
                                ).exclude(VoucherType="ST")
                            else:
                                stock_instance_CS = StockPosting.objects.filter(
                                    ProductID=ProductID,
                                    Date__lte=ToDate,
                                    CompanyID=CompanyID,
                                )

                            ClosingQtyInRate = 0
                            ClosingQtyOutTot = 0
                            ClosingQtyInTot = 0
                            ClosingStock = 0
                            for si in stock_instance_CS:
                                ClosingQtyInRate += converted_float(
                                    si.QtyIn
                                ) * converted_float(si.Rate)
                                ClosingQtyInTot += converted_float(si.QtyIn)
                                ClosingQtyOutTot += converted_float(si.QtyOut)

                            ClosingStock = converted_float(
                                ClosingQtyInTot
                            ) - converted_float(ClosingQtyOutTot)

                            if ClosingQtyInTot > 0:
                                ClosingAvgRate = converted_float(
                                    ClosingQtyInRate
                                ) / converted_float(ClosingQtyInTot)

                            TotalAvgValueClosing += converted_float(
                                ClosingStock
                            ) * converted_float(ClosingAvgRate)

                        # purchase
                        TotalAvgValuePurchaseInvoice = 0
                        PurchaseInvoiceAvgRate = 0
                        # product with voucher type pi(purchase invoice)
                        if StockPosting.objects.filter(
                            ProductID=ProductID, CompanyID=CompanyID, VoucherType="PI"
                        ).exists():
                            purchase_invoice_instance = StockPosting.objects.filter(
                                ProductID=ProductID,
                                CompanyID=CompanyID,
                                VoucherType="PI",
                            )

                            PurchaseInvoiceQtyInRate = 0
                            PurchaseInvoiceQtyInTot = 0
                            PurchaseInvoiceStock = 0
                            for pi in purchase_invoice_instance:
                                # purchase rate = qty * rate
                                PurchaseInvoiceQtyInRate += converted_float(
                                    pi.QtyIn
                                ) * converted_float(pi.Rate)
                                # purchase qty
                                PurchaseInvoiceQtyInTot += converted_float(pi.QtyIn)

                            PurchaseReturnsQtyOutRate = 0
                            PurchaseReturnsQtyOutTot = 0
                            PurchaseReturnsStock = 0
                            if StockPosting.objects.filter(
                                ProductID=ProductID,
                                CompanyID=CompanyID,
                                VoucherType="PR",
                            ).exists():
                                purchase_returns_instance = StockPosting.objects.filter(
                                    ProductID=ProductID,
                                    CompanyID=CompanyID,
                                    VoucherType="PR",
                                )
                                for pr in purchase_returns_instance:
                                    PurchaseReturnsQtyOutRate += converted_float(
                                        pr.QtyOut
                                    ) * converted_float(pr.Rate)
                                    PurchaseReturnsQtyOutTot += converted_float(
                                        pr.QtyOut
                                    )

                            PurchaseInvoiceStock = converted_float(
                                PurchaseInvoiceQtyInTot
                            ) - converted_float(PurchaseReturnsQtyOutTot)

                            if PurchaseInvoiceQtyInTot > 0:
                                PurchaseInvoiceAvgRate = converted_float(
                                    PurchaseInvoiceQtyInRate
                                ) / converted_float(PurchaseInvoiceQtyInTot)

                            TotalAvgValuePurchaseInvoice += converted_float(
                                PurchaseInvoiceStock
                            ) * converted_float(PurchaseInvoiceAvgRate)

                        # sales
                        TotalAvgValueSalesInvoice = 0
                        SalesInvoiceAvgRate = 0
                        SalesInvoiceStock = 0
                        # product with voucher type pi(Sales invoice)
                        if StockPosting.objects.filter(
                            ProductID=ProductID, CompanyID=CompanyID, VoucherType="SI"
                        ).exists():
                            sales_invoice_instance = StockPosting.objects.filter(
                                ProductID=ProductID,
                                CompanyID=CompanyID,
                                VoucherType="SI",
                            )

                            SalesInvoiceQtyOutRate = 0
                            SalesInvoiceQtyOutTot = 0
                            SalesInvoiceStock = 0
                            for si in sales_invoice_instance:
                                # sales rate = qty * rate
                                SalesInvoiceQtyOutRate += converted_float(
                                    si.QtyOut
                                ) * converted_float(si.Rate)
                                # sales qty
                                SalesInvoiceQtyOutTot += converted_float(si.QtyOut)

                            SalesReturnsQtyInRate = 0
                            SalesReturnsQtyInTot = 0
                            SalesReturnsStock = 0
                            if StockPosting.objects.filter(
                                ProductID=ProductID,
                                CompanyID=CompanyID,
                                VoucherType="SR",
                            ).exists():
                                sales_returns_instance = StockPosting.objects.filter(
                                    ProductID=ProductID,
                                    CompanyID=CompanyID,
                                    VoucherType="SR",
                                )
                                for sr in sales_returns_instance:
                                    SalesReturnsQtyInRate += converted_float(
                                        sr.QtyIn
                                    ) * converted_float(sr.Rate)
                                    SalesReturnsQtyInTot += converted_float(sr.QtyIn)

                            SalesInvoiceStock = converted_float(
                                SalesInvoiceQtyOutTot
                            ) - converted_float(SalesReturnsQtyInTot)

                            if SalesInvoiceQtyOutTot > 0:
                                SalesInvoiceAvgRate = converted_float(
                                    SalesInvoiceQtyOutRate
                                ) / converted_float(SalesInvoiceQtyOutTot)

                            TotalAvgValueSalesInvoice += converted_float(
                                SalesInvoiceStock
                            ) * converted_float(SalesInvoiceAvgRate)

                        i["CurrentStock"] = total_stock
                        i["CurrentBaseStock"] = CurrentBaseStock
                        # opening stock
                        i["OpeningStock"] = OpeningStock
                        i["OpeningStockValue"] = TotalAvgValueOpening
                        i["OpeningAvgRate"] = OpeningAvgRate
                        # closing stock
                        i["ClosingStock"] = ClosingStock
                        i["ClosingStockValue"] = TotalAvgValueClosing
                        i["ClosingAvgRate"] = ClosingAvgRate
                        # purchase stock
                        i["PurchaseStock"] = PurchaseInvoiceStock
                        i["PurchaseStockValue"] = TotalAvgValuePurchaseInvoice
                        i["PurchaseAvgRate"] = PurchaseInvoiceAvgRate
                        # sales stock
                        i["SalesStock"] = SalesInvoiceStock
                        i["SalesStockValue"] = TotalAvgValueSalesInvoice
                        i["SalesAvgRate"] = SalesInvoiceAvgRate

            if jsnDatas:
                response_data = {
                    "StatusCode": StatusCode,
                    "data": jsnDatas,
                    "count": len(product_instances),
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {"StatusCode": 6001, "message": "No data!"}

                return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "No data During This Time Periods!",
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {"StatusCode": 6001, "message": "please provide valid datas!!!"}

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def products_search_web(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]
    product_name = data["product_name"]
    length = data["length"]

    try:
        type = data["type"]
    except:
        type = "any"

    try:
        Date = data["Date"]
    except:
        Date = ""

    try:
        WarehouseID = data["WarehouseID"]
    except:
        WarehouseID = 1

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data["BranchID"]
        BranchList = get_BranchList(CompanyID, BranchID)
        check_EnableProductBatchWise = False
        check_AllowNegativeStockSales = True
        if GeneralSettings.objects.filter(
            CompanyID=CompanyID,
            BranchID=BranchID,
            SettingsType="AllowNegativeStockSales",
        ).exists():
            check_AllowNegativeStockSales = GeneralSettings.objects.get(
                BranchID=BranchID,
                CompanyID=CompanyID,
                SettingsType="AllowNegativeStockSales",
            ).SettingsValue

        # check_productsForAllBranches = False
        check_productsForAllBranches = get_BranchSettings(
            CompanyID, "productsForAllBranches"
        )

        if (
            check_productsForAllBranches == True
            or check_productsForAllBranches == "True"
        ):
            product_instances = Product.objects.filter(CompanyID=CompanyID)
            stockPosting_instances = StockPosting.objects.filter(CompanyID=CompanyID)
        else:
            product_instances = Product.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID
            )
            stockPosting_instances = StockPosting.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID
            )
        if type == "Sales":
            if product_instances.filter(Active=True, IsSales=True).exists():
                if length < 3:
                    instances = product_instances.filter(
                        Active=True, ProductName__icontains=product_name, IsSales=True
                    )[:10]
                else:
                    instances = product_instances.filter(
                        Active=True, ProductName__icontains=product_name, IsSales=True
                    )

                product_ids = []
                for p in instances:
                    Stock = 0
                    ProductID = p.ProductID
                    is_Service = p.is_Service
                    check_EnableProductBatchWise = False
                    if GeneralSettings.objects.filter(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        SettingsType="EnableProductBatchWise",
                    ).exists():
                        check_EnableProductBatchWise = GeneralSettings.objects.get(
                            BranchID=BranchID,
                            CompanyID=CompanyID,
                            SettingsType="EnableProductBatchWise",
                        ).SettingsValue
                    if (
                        check_EnableProductBatchWise == "True"
                        or check_EnableProductBatchWise == True
                    ):
                        if Batch.objects.filter(
                            CompanyID=CompanyID,
                            BranchID__in=BranchList,
                            ProductID=ProductID,
                            WareHouseID=WarehouseID,
                        ).exists():
                            Batch_ins = Batch.objects.filter(
                                CompanyID=CompanyID,
                                BranchID__in=BranchList,
                                ProductID=ProductID,
                                WareHouseID=WarehouseID,
                            )
                            total_stockIN = 0
                            total_stockOUT = 0
                            for b in Batch_ins:
                                batch_pricelistID = b.PriceListID
                                batch_MultiFactor = PriceList.objects.get(
                                    CompanyID=CompanyID, PriceListID=batch_pricelistID
                                ).MultiFactor
                                total_stockIN += converted_float(b.StockIn)
                                total_stockOUT += converted_float(b.StockOut)

                            Stock = converted_float(total_stockIN) - converted_float(
                                total_stockOUT
                            )
                        elif stockPosting_instances.filter(
                            ProductID=ProductID, WareHouseID=WarehouseID
                        ):
                            stock_ins = stockPosting_instances.filter(
                                ProductID=ProductID, WareHouseID=WarehouseID
                            )
                            total_stockIN = 0
                            total_stockOUT = 0
                            for s in stock_ins:
                                total_stockIN += converted_float(s.QtyIn)
                                total_stockOUT += converted_float(s.QtyOut)

                            Stock = converted_float(total_stockIN) - converted_float(
                                total_stockOUT
                            )
                    else:
                        if stockPosting_instances.filter(
                            ProductID=ProductID, warehouse__WarehouseID=WarehouseID
                        ):
                            stock_ins = stockPosting_instances.filter(
                                ProductID=ProductID, warehouse__WarehouseID=WarehouseID
                            )
                            total_stockIN = stock_ins.aggregate(Sum("QtyIn"))
                            total_stockIN = total_stockIN["QtyIn__sum"]
                            total_stockOUT = stock_ins.aggregate(Sum("QtyOut"))
                            total_stockOUT = total_stockOUT["QtyOut__sum"]

                            Stock = converted_float(total_stockIN) - converted_float(
                                total_stockOUT
                            )
                    if (
                        check_EnableProductBatchWise == "True"
                        or check_EnableProductBatchWise == True
                    ):
                        if GeneralSettings.objects.filter(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            SettingsType="ShowNegativeBatchInSales",
                        ).exists():
                            check_ShowNegativeBatchInSales = (
                                GeneralSettings.objects.get(
                                    BranchID=BranchID,
                                    CompanyID=CompanyID,
                                    SettingsType="ShowNegativeBatchInSales",
                                ).SettingsValue
                            )
                            if (
                                check_ShowNegativeBatchInSales == "False"
                                or check_ShowNegativeBatchInSales == False
                            ):
                                if Stock > 0:
                                    product_ids.append(ProductID)
                            else:
                                product_ids.append(ProductID)
                    # else:
                    if (
                        check_AllowNegativeStockSales == "False"
                        or check_AllowNegativeStockSales == False
                    ):
                        if Stock > 0 or is_Service == True:
                            product_ids.append(ProductID)
                    else:
                        product_ids.append(ProductID)

                if product_ids:
                    if length < 3:
                        instances = product_instances.filter(ProductID__in=product_ids)
                        # for i in instances:
                        #     print(i.ProductName, 'ProductName1')
                    # elif:
                    #     instances = StockPosting.objects.filter(
                    #         CompanyID=CompanyID, BranchID=BranchID, ProductID__in=product_ids)
                    else:
                        instances = instances.filter(ProductID__in=product_ids)
                        # for i in instances:
                        #     print(i.ProductName, 'ProductName2')
                    serialized = ProductSearchSerializer(
                        instances,
                        many=True,
                        context={
                            "request": request,
                            "CompanyID": CompanyID,
                            "PriceRounding": PriceRounding,
                            "WarehouseID": WarehouseID,
                        },
                    )

                    data = serialized.data
                    # request , company, log_type, user, source, action, message, description
                    # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product', 'List', 'Product List Viewed successfully.', 'Product List Viewed successfully.')
                    response_data = {"StatusCode": 6000, "data": data}
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Product Not Found with Stock!!",
                    }

                    return Response(response_data, status=status.HTTP_200_OK)
            else:
                # request , company, log_type, user, source, action, message, description
                activity_log(
                    request._request,
                    CompanyID,
                    "Warning",
                    CreatedUserID,
                    "Product",
                    "List",
                    "Product List Viewed Failed.",
                    "Product Not Found in this Branch!",
                )
                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Not Found in this Branch!!",
                }
                return Response(response_data, status=status.HTTP_200_OK)
        elif type == "Purchase":
            if product_instances.filter(Active=True, IsPurchase=True).exists():
                if length < 3:
                    instances = product_instances.filter(
                        Active=True,
                        ProductName__icontains=product_name,
                        IsPurchase=True,
                    )[:10]

                else:
                    instances = product_instances.filter(
                        Active=True,
                        ProductName__icontains=product_name,
                        IsPurchase=True,
                    )
                serialized = ProductSearchSerializer(
                    instances,
                    many=True,
                    context={
                        "request": request,
                        "CompanyID": CompanyID,
                        "PriceRounding": PriceRounding,
                        "WarehouseID": WarehouseID,
                    },
                )
                # if page_number and items_per_page:

                #     product_object = Product.objects.filter(
                #         CompanyID=CompanyID, BranchID=BranchID, Active=True)

                # request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product', 'List', 'Product List Viewed successfully.', 'Product List Viewed successfully.')
                response_data = {"StatusCode": 6000, "data": serialized.data}

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                activity_log(
                    request._request,
                    CompanyID,
                    "Warning",
                    CreatedUserID,
                    "Product",
                    "List",
                    "Product List Viewed Failed.",
                    "Product Not Found in this Branch!",
                )
                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Not Found in this Branch!!",
                }

                return Response(response_data, status=status.HTTP_200_OK)
        elif type == "WorkOrder_FinishedProducts":
            if product_instances.filter(
                is_Service=False, IsFinishedProduct=True
            ).exists():
                if length < 3:
                    instances = product_instances.filter(
                        ProductName__icontains=product_name,
                        is_Service=False,
                        IsFinishedProduct=True,
                    )[:10]
                else:
                    instances = product_instances.filter(
                        ProductName__icontains=product_name,
                        is_Service=False,
                        IsFinishedProduct=True,
                    )
                serialized = ProductSearchSerializer(
                    instances,
                    many=True,
                    context={
                        "request": request,
                        "CompanyID": CompanyID,
                        "PriceRounding": PriceRounding,
                        "WarehouseID": WarehouseID,
                    },
                )

                # request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product', 'List', 'Product List Viewed successfully.', 'Product List Viewed successfully.')
                response_data = {"StatusCode": 6000, "data": serialized.data}

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                # request , company, log_type, user, source, action, message, description
                activity_log(
                    request._request,
                    CompanyID,
                    "Warning",
                    CreatedUserID,
                    "Product",
                    "List",
                    "Product List Viewed Failed.",
                    "Product Not Found in this Branch!",
                )
                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Not Found in this Branch!!",
                }

                return Response(response_data, status=status.HTTP_200_OK)
        elif type == "WorkOrder_Components":
            if product_instances.filter(is_Service=False, IsRawMaterial=True).exists():
                if length < 3:
                    instances = product_instances.filter(
                        ProductName__icontains=product_name,
                        is_Service=False,
                        IsRawMaterial=True,
                    )[:10]
                else:
                    instances = product_instances.filter(
                        ProductName__icontains=product_name,
                        is_Service=False,
                        IsRawMaterial=True,
                    )
                serialized = ProductSearchSerializer(
                    instances,
                    many=True,
                    context={
                        "request": request,
                        "CompanyID": CompanyID,
                        "PriceRounding": PriceRounding,
                        "WarehouseID": WarehouseID,
                    },
                )

                # request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product', 'List', 'Product List Viewed successfully.', 'Product List Viewed successfully.')
                response_data = {"StatusCode": 6000, "data": serialized.data}

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                # request , company, log_type, user, source, action, message, description
                activity_log(
                    request._request,
                    CompanyID,
                    "Warning",
                    CreatedUserID,
                    "Product",
                    "List",
                    "Product List Viewed Failed.",
                    "Product Not Found in this Branch!",
                )
                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Not Found in this Branch!!",
                }

                return Response(response_data, status=status.HTTP_200_OK)
        else:
            if product_instances.filter(is_Service=False).exists():
                if length < 3:
                    instances = product_instances.filter(
                        ProductName__icontains=product_name, is_Service=False
                    )[:10]
                else:
                    instances = product_instances.filter(
                        ProductName__icontains=product_name, is_Service=False
                    )
                serialized = ProductSearchSerializer(
                    instances,
                    many=True,
                    context={
                        "request": request,
                        "CompanyID": CompanyID,
                        "PriceRounding": PriceRounding,
                        "WarehouseID": WarehouseID,
                        "type": type,
                        "Date": Date,
                    },
                )

                # request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product', 'List', 'Product List Viewed successfully.', 'Product List Viewed successfully.')
                response_data = {"StatusCode": 6000, "data": serialized.data}

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                # request , company, log_type, user, source, action, message, description
                activity_log(
                    request._request,
                    CompanyID,
                    "Warning",
                    CreatedUserID,
                    "Product",
                    "List",
                    "Product List Viewed Failed.",
                    "Product Not Found in this Branch!",
                )
                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Not Found in this Branch!!",
                }

                return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def set_product_tax(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    BranchID = data["BranchID"]
    PriceRounding = data["PriceRounding"]
    ProductID = data["ProductID"]
    ProductGroupID = data["ProductGroupID"]
    TaxID = data["TaxID"]

    try:
        IncluVal = data["IncluVal"]
    except:
        IncluVal = 7

    try:
        val = data["val"]
    except:
        val = 1

    check_VAT = GeneralSettings.objects.get(
        BranchID=BranchID, CompanyID=CompanyID, SettingsType="VAT"
    ).SettingsValue
    check_GST = GeneralSettings.objects.get(
        BranchID=BranchID, CompanyID=CompanyID, SettingsType="GST"
    ).SettingsValue

    if Product.objects.filter(
        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID
    ).exists():
        instance = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID)
        if check_VAT == "true" or check_VAT == "True" or check_VAT == True:
            instance.VatID = TaxID
        elif check_GST == "true" or check_GST == "True" or check_GST == True:
            instance.GST = TaxID
        if not IncluVal == 7:
            inclusive = True
            if IncluVal == 9:
                inclusive = False
            instance.is_inclusive = inclusive
        instance.save()

    elif Product.objects.filter(
        CompanyID=CompanyID, BranchID=BranchID, ProductGroupID=ProductGroupID
    ).exists():
        instances = Product.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, ProductGroupID=ProductGroupID
        )
        for p in instances:
            if check_VAT == "true" or check_VAT == "True" or check_VAT == True:
                p.VatID = TaxID
            elif check_GST == "true" or check_GST == "True" or check_GST == True:
                p.GST = TaxID

            if not IncluVal == 7:
                inclusive = True
                if IncluVal == 9:
                    inclusive = False
                p.is_inclusive = inclusive
            p.save()
    else:
        if val == 3:
            instances = Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID)
            for p in instances:
                if check_VAT == "true" or check_VAT == "True" or check_VAT == True:
                    p.VatID = TaxID
                elif check_GST == "true" or check_GST == "True" or check_GST == True:
                    p.GST = TaxID

                if not IncluVal == 7:
                    inclusive = True
                    if IncluVal == 9:
                        inclusive = False
                    p.is_inclusive = inclusive
                p.save()

    response_data = {
        "StatusCode": 6000,
        # "message": "Branch ID You Enterd is not Valid!!!"
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def search_product_list(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]
    product_name = data["product_name"]
    length = data["length"]

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data["BranchID"]
        if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            if length < 3:
                instances = Product.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID
                )
                instances = instances.filter(
                    (Q(ProductName__icontains=product_name))
                    | (Q(ProductCode__icontains=product_name))
                )[:10]
            else:
                instances = Product.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID
                )
                instances = instances.filter(
                    (Q(ProductName__icontains=product_name))
                    | (Q(ProductCode__icontains=product_name))
                )
            serialized = ProductSearchShortcutSerializer(
                instances,
                many=True,
                context={
                    "request": request,
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                    "product_name": "product_name",
                },
            )

        response_data = {"StatusCode": 6000, "data": serialized.data}

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch You Enterd is not Valid!!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def get_product_batchcode(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    BranchID = data["BranchID"]
    try:
        BatchCode = data["BatchCode"]
    except:
        BatchCode = 0
    PriceRounding = data["PriceRounding"]
    LedgerID = data["LedgerID"]
    try:
        ProductID = data["ProductID"]
    except:
        ProductID = ""

    if Batch.objects.filter(
        CompanyID=CompanyID, BatchCode=BatchCode, BranchID=BranchID, ProductID=ProductID
    ).exists():
        batch_ins = Batch.objects.get(
            CompanyID=CompanyID,
            BatchCode=BatchCode,
            BranchID=BranchID,
            ProductID=ProductID,
        )
        if not ProductID:
            ProductID = batch_ins.ProductID
        if Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID).exists():
            instance = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID)
            serialized = BatchCodeSearchSerializer(
                instance,
                context={
                    "request": request,
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                    "BatchCode": BatchCode,
                    "LedgerID": LedgerID,
                },
            )

            GST = instance.GST
            VatID = instance.VatID
            ProductTaxID = 1
            if not GST == 1:
                ProductTaxID = GST
            if not VatID == 1:
                ProductTaxID = VatID

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "BatchCode": BatchCode,
                "ProductTaxID": ProductTaxID,
            }
        else:
            response_data = {"StatusCode": 6001, "message": "Product Not Found!"}
    else:
        response_data = {"StatusCode": 6001, "message": "Product Not Found!"}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def get_batch_list(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    BranchID = data["BranchID"]
    PriceRounding = data["PriceRounding"]
    BatchCode = data["BatchCode"]
    length = data["length"]

    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        if length < 3:
            instances = Batch.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, BatchCode__icontains=BatchCode
            )[:10]
        else:
            instances = Batch.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, BatchCode__icontains=BatchCode
            )

        serialized = Batch_ListSerializer(
            instances,
            many=True,
            context={
                "request": request,
                "CompanyID": CompanyID,
                "PriceRounding": PriceRounding,
            },
        )

        response_data = {"StatusCode": 6000, "data": serialized.data}

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Batch Not Found in this Branch!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def batch_report(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    BranchID = data["BranchID"]
    PriceRounding = data["PriceRounding"]
    FromDate = data["FromDate"]
    ToDate = data["ToDate"]
    ProductGroupID = data["ProductGroupID"]
    ProductID = data["ProductID"]
    BatchCode = data["BatchCode"]
    page_number = data["page_no"]
    items_per_page = data["items_per_page"]
    print(ProductGroupID)
    is_ok = True
    message = ""
    if Batch.objects.filter(
        CompanyID=CompanyID,
        BranchID=BranchID,
        CreatedDate__date__gte=FromDate,
        CreatedDate__date__lte=ToDate,
    ).exists():
        batch_ins = Batch.objects.filter(
            CompanyID=CompanyID,
            BranchID=BranchID,
            CreatedDate__date__gte=FromDate,
            CreatedDate__date__lte=ToDate,
        )
        product_ids = batch_ins.values_list("ProductID", flat=True)
        if ProductGroupID:
            if Product.objects.filter(
                CompanyID=CompanyID,
                BranchID=BranchID,
                ProductID__in=product_ids,
                ProductGroupID=ProductGroupID,
            ).exists():
                product_ids = Product.objects.filter(
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    ProductID__in=product_ids,
                    ProductGroupID=ProductGroupID,
                ).values_list("ProductID", flat=True)
                batch_ins = batch_ins.filter(ProductID__in=product_ids)
            else:
                is_ok = False
                message = "No Batch found under this Product Group"
        elif ProductID:
            if batch_ins.filter(ProductID=ProductID).exists():
                batch_ins = batch_ins.filter(ProductID=ProductID)
            else:
                is_ok = False
                message = "No Batch found with this Product"
        elif BatchCode:
            if batch_ins.filter(BatchCode=BatchCode).exists():
                batch_ins = batch_ins.filter(BatchCode=BatchCode)
            else:
                is_ok = False
                message = "No Batch found with this Batch Code"

        count = len(batch_ins)
        if page_number and items_per_page:
            batch_ins = list_pagination(batch_ins, items_per_page, page_number)
        serialized = Batch_ListSerializer(
            batch_ins,
            many=True,
            context={
                "request": request,
                "CompanyID": CompanyID,
                "PriceRounding": PriceRounding,
            },
        )
        if is_ok:
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "total_count": count,
            }
        else:
            response_data = {"StatusCode": 6001, "message": message}
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Batch Not Found During this dates",
        }

        return Response(response_data, status=status.HTTP_200_OK)


import pandas as pd


@api_view(["GET"])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def products_export_excel_freeze(request):
    # content-type of response
    CompanyID = request.GET.get("CompanyID")
    BranchID = request.GET.get("BranchID")

    UserID = request.GET.get("UserID")
    PriceRounding = request.GET.get("PriceRounding")

    response = HttpResponse(content_type="application/ms-excel")

    # decide file name
    response["Content-Disposition"] = 'attachment; filename="Products.xls"'

    # creating workbook
    wb = xlwt.Workbook(encoding="utf-8")
    Allproducts = get_Allproducts(CompanyID, UserID, PriceRounding, BranchID, request)
    AllmultyUnits = get_AllmultyUnits(
        CompanyID, UserID, PriceRounding, BranchID, request
    )
    # ===============  adding Products sheet ============
    all_products = wb.add_sheet("Products")
    multy_unit = wb.add_sheet("MultyUnit")

    products_columns = [
        "ProductCode",
        "ProductName",
        "Description",
        "PurchasePrice",
        "SalesPrice",
        "SalesPrice1",
        "SalesPrice2",
        "SalesPrice3",
        "GroupName",
        "Unit",
        "BrandName",
        "VAT",
        "StockMinimum",
        "StockReOrder",
        "StockMaximum",
        "Barcode",
        "AutoBarcode",
    ]
    multy_units_columns = [
        "ProductCode",
        "UnitName",
        "BatchCode",
        "MultiFactor",
        "PurchasePrice",
        "SalesPrice",
        "SalesPrice1",
        "SalesPrice2",
        "SalesPrice3",
        "MRP",
    ]
    # write column headers in sheet

    # xl sheet styles
    df = pd.DataFrame(Allproducts)
    print(df)
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER

    # header font
    font = xlwt.Font()
    font.bold = True
    font.height = 11 * 20

    sub_header_style = xlwt.XFStyle()
    sub_header_style.font = font

    value_decimal_style = xlwt.XFStyle()
    value_decimal_style.num_format_str = "0.00"

    row_num = 0
    for products_col_num in range(len(products_columns)):
        all_products.write(
            row_num,
            products_col_num,
            products_columns[products_col_num],
            sub_header_style,
        )

    for multy_col_num in range(len(multy_units_columns)):
        multy_unit.write(
            row_num, multy_col_num, multy_units_columns[multy_col_num], sub_header_style
        )

    data_row = 2
    try:
        data_multy_units = AllmultyUnits["data"]
    except:
        data_multy_units = None

    try:
        data_products = Allproducts["data"]
    except:
        data_products = None
    row_num = 0
    if data_products:
        for i in data_products:
            row_num = row_num + 1
            all_products.write(row_num, 0, i["ProductCode"])
            all_products.write(row_num, 1, i["ProductName"])
            all_products.write(row_num, 2, i["Description"])
            all_products.write(row_num, 3, i["PurchasePrice"], value_decimal_style)
            all_products.write(row_num, 4, i["SalesPrice"], value_decimal_style)
            all_products.write(row_num, 5, i["DefaultSalesPrice1"])
            all_products.write(row_num, 6, i["DefaultSalesPrice2"])
            all_products.write(row_num, 7, i["DefaultSalesPrice3"])
            all_products.write(row_num, 8, i["ProductGroupName"])
            all_products.write(row_num, 9, i["UnitName"])
            all_products.write(row_num, 10, i["BrandName"])
            all_products.write(row_num, 11, i["VatID"])
            all_products.write(
                row_num, 12, converted_float(i["StockMinimum"]), value_decimal_style
            )
            all_products.write(
                row_num, 13, converted_float(i["StockReOrder"]), value_decimal_style
            )
            all_products.write(
                row_num, 14, converted_float(i["StockMaximum"]), value_decimal_style
            )
            all_products.write(row_num, 15, i["DefBarcode"])
            all_products.write(row_num, 16, i["AutoBarcode"])

    row_num = 1
    if data_multy_units:
        for i in data_multy_units:
            row_num = row_num + 1
            multy_unit.write(row_num, 0, i["ProductCode"])
            multy_unit.write(row_num, 1, i["UnitName"])
            multy_unit.write(row_num, 2, i["BatchCode"])
            multy_unit.write(row_num, 3, i["MultiFactor"])
            multy_unit.write(row_num, 4, i["PurchasePrice"], value_decimal_style)
            multy_unit.write(row_num, 5, i["SalesPrice"], value_decimal_style)
            multy_unit.write(
                row_num, 6, converted_float(i["SalesPrice1"]), value_decimal_style
            )
            multy_unit.write(
                row_num, 7, converted_float(i["SalesPrice2"]), value_decimal_style
            )
            multy_unit.write(
                row_num, 8, converted_float(i["SalesPrice3"]), value_decimal_style
            )
            multy_unit.write(row_num, 9, converted_float(i["MRP"]), value_decimal_style)

    wb.save(response)
    return response


@api_view(["GET"])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def products_export_excel(request):
    # content-type of response
    CompanyID = request.GET.get("CompanyID")
    BranchID = request.GET.get("BranchID")

    UserID = request.GET.get("UserID")
    PriceRounding = request.GET.get("PriceRounding")

    response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    # decide file name
    response["Content-Disposition"] = 'attachment; filename="Products.xls"'
    
    # creating workbook
    df,details = query_Allproducts_toExcel(CompanyID, UserID, PriceRounding, BranchID, request)
    print(df)
    df.to_excel(response,index=False)
    return response


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def productCode_search(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]
    product_name = data["product_name"]
    length = data["length"]
    BranchID = data["BranchID"]

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        # check_productsForAllBranches = False
        check_productsForAllBranches = get_BranchSettings(
            CompanyID, "productsForAllBranches"
        )

        if (
            check_productsForAllBranches == True
            or check_productsForAllBranches == "True"
        ):
            product_instances = Product.objects.filter(
                CompanyID=CompanyID, ProductCode__icontains=product_name
            )
        else:
            product_instances = Product.objects.filter(
                CompanyID=CompanyID,
                BranchID=BranchID,
                ProductCode__icontains=product_name,
            )

        if product_instances:
            if length < 3:
                instances = product_instances[:10]
            else:
                instances = product_instances

            serialized = ProductSearchSerializer(
                instances,
                many=True,
                context={
                    "request": request,
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                },
            )

            # request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product', 'List', 'Product List Viewed successfully.', 'Product List Viewed successfully.')
            response_data = {"StatusCode": 6000, "data": serialized.data}

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # request , company, log_type, user, source, action, message, description
            activity_log(
                request._request,
                CompanyID,
                "Warning",
                CreatedUserID,
                "Product",
                "List",
                "Product List Viewed Failed.",
                "Product Not Found in this Branch!",
            )
            response_data = {
                "StatusCode": 6001,
                "message": "Product Not Found in this Branch!!",
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def products_search_qry(request):
    import time

    start = time.time()
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]
    product_name = data["product_name"]
    length = data["length"]

    try:
        type = data["type"]
    except:
        type = "any"

    try:
        Date = data["Date"]
    except:
        Date = ""

    try:
        WarehouseID = data["WarehouseID"]
    except:
        WarehouseID = 1

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data["BranchID"]
        BranchList = get_BranchList(CompanyID, BranchID)
        check_EnableProductBatchWise = get_GeneralSettings(
            CompanyID, BranchID, "EnableProductBatchWise"
        )
        check_AllowNegativeStockSales = get_GeneralSettings(
            CompanyID, BranchID, "AllowNegativeStockSales"
        )
        AllowNegativeStockInStockTransfer = get_GeneralSettings(
            CompanyID, BranchID, "AllowNegativeStockInStockTransfer"
        )
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>geeeee")
        
        if Product.objects.filter(
            CompanyID=CompanyID,
            BranchID__in=BranchList,
            ProductName__icontains=product_name,
            Active=True,
        ).exists():
            product_instances = Product.objects.filter(
                CompanyID=CompanyID,
                BranchID__in=BranchList,
                ProductName__icontains=product_name,
                Active=True,
            )
            if type == "Sales":
                product_instances = product_instances.filter(IsSales=True)
            elif type == "Purchase":
                product_instances = product_instances.filter(IsPurchase=True)
            elif type == "WorkOrder_FinishedProducts":
                product_instances = product_instances.filter(IsFinishedProduct=True)
            elif type == "WorkOrder_Components":
                product_instances = product_instances.filter(
                    IsRawMaterial=True)
            
            if length < 3:
                product_instances = product_instances.filter()[:10]

            product_ids = product_instances.values_list("ProductID", flat=True)
            batch_ins = None
            stockposting_ins = None
            if check_EnableProductBatchWise:
                if Batch.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID__in=product_ids
                ).exists():
                    batch_ins = Batch.objects.filter(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        ProductID__in=product_ids,
                    )
            price_list_ins = PriceList.objects.filter(
                CompanyID=CompanyID, ProductID__in=product_ids
            )
            if StockPosting.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID__in=product_ids
            ).exists():
                stockposting_ins = StockPosting.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID__in=product_ids
                )
                if WarehouseID:
                    stockposting_ins = stockposting_ins.filter(WareHouseID=WarehouseID)
                    if batch_ins:
                        batch_ins = batch_ins.filter(WareHouseID=WarehouseID)
            final_data = []
            
            for i in product_instances:
                price_list_pro_ins = price_list_ins.filter(
                    ProductID=i.ProductID, DefaultUnit=True
                ).first()
                Barcode = price_list_pro_ins.Barcode
                PurchasePrice = price_list_pro_ins.PurchasePrice
                SalesPrice = price_list_pro_ins.SalesPrice
                Stock = 0
                BatchCode = ""
                if check_EnableProductBatchWise:
                    if batch_ins:
                        batch_ins_pro = batch_ins.filter(ProductID=i.ProductID)
                        try:
                            total_stockIN = converted_float(batch_ins_pro.StockIn)
                        except:
                            total_stockIN = 0
                        try:
                            total_stockOUT = converted_float(batch_ins_pro.StockOut)
                        except:
                            total_stockOUT = 0
                        Stock = converted_float(total_stockIN) - converted_float(
                            total_stockOUT
                        )

                        try:
                            BatchCode = batch_ins_pro.filter().last().BatchCode
                        except:
                            BatchCode = ""
                else:
                    if stockposting_ins:
                        stockposting_ins_pro = stockposting_ins.filter(
                            ProductID=i.ProductID
                        )
                        total_stockIN = stockposting_ins_pro.aggregate(Sum("QtyIn"))
                        total_stockIN = total_stockIN["QtyIn__sum"]
                        total_stockOUT = stockposting_ins_pro.aggregate(Sum("QtyOut"))
                        total_stockOUT = total_stockOUT["QtyOut__sum"]
                        Stock = converted_float(total_stockIN) - converted_float(
                            total_stockOUT
                        )
                product_obj = {
                    "id": i.id,
                    "Description": i.Description,
                    "ProductID": i.ProductID,
                    "ProductCode": i.ProductCode,
                    "Barcode": Barcode,
                    "ProductName": i.ProductName,
                    "Stock": Stock,
                    "HSNCode": i.HSNCode,
                    "PurchasePrice": PurchasePrice,
                    "SalesPrice": SalesPrice,
                    "BatchCode": BatchCode,
                    "StockMaximum": i.StockMaximum,
                    "StockMinimum": i.StockMinimum,
                }
                
                if (i.is_Service == True or i.InventoryType == "Non StockItem"):
                    final_data.append(product_obj)
                elif ((type == "Sales" or type == "WorkOrder_Components") and check_AllowNegativeStockSales):
                    final_data.append(product_obj)
                elif ((type == "Sales" or type == "WorkOrder_Components" or type == "StockTransfer") and Stock > 0):
                    final_data.append(product_obj)
                elif type == "StockTransfer" and AllowNegativeStockInStockTransfer:
                    final_data.append(product_obj)
                elif not type == "Sales" and not type == "WorkOrder_Components" and not type == "StockTransfer":
                    final_data.append(product_obj)
                
                print("final_data")
                print(check_AllowNegativeStockSales)
                print(type)
                print(i.is_Service)
                print(i.InventoryType)
                print(final_data)
                # if (
                #     (type == "StockManagement")
                #     or (type == "StockTransfer" and AllowNegativeStockInStockTransfer)
                #     or type == "Purchase"
                #     or (type == "Sales" and check_AllowNegativeStockSales)
                #     or type == "report"
                #     or type == "taxcategory"
                # ):
                #     final_data.append(product_obj)
                # else:
                #     if (
                #         Stock > 0
                #         or i.is_Service == True
                #         or i.InventoryType == "Non StockItem"
                #     ):
                #         final_data.append(product_obj)

            response_data = {"StatusCode": 6000, "data": final_data}

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {"StatusCode": 6001, "message": "Product Not Found"}
            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!",
        }
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def products_search_app(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]
    product_name = data["product_name"]
    length = data["length"]

    try:
        type = data["type"]
    except:
        type = "any"

    try:
        Date = data["Date"]
    except:
        Date = ""

    try:
        WarehouseID = data["WarehouseID"]
    except:
        WarehouseID = 1

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data["BranchID"]
        BranchList = get_BranchList(CompanyID, BranchID)
        check_EnableProductBatchWise = get_GeneralSettings(
            CompanyID, BranchID, "EnableProductBatchWise"
        )
        check_AllowNegativeStockSales = get_GeneralSettings(
            CompanyID, BranchID, "AllowNegativeStockSales"
        )
        AllowNegativeStockInStockTransfer = get_GeneralSettings(
            CompanyID, BranchID, "AllowNegativeStockInStockTransfer"
        )
        if Product.objects.filter(
            CompanyID=CompanyID,
            BranchID__in=BranchList,
            ProductName__icontains=product_name,
            Active=True,
        ).exists():
            product_instances = Product.objects.filter(
                CompanyID=CompanyID,
                BranchID__in=BranchList,
                ProductName__icontains=product_name,
                Active=True,
            )
            if type == "Sales":
                product_instances = product_instances.filter(IsSales=True)
            elif type == "Purchase":
                product_instances = product_instances.filter(IsPurchase=True)
            elif type == "WorkOrder_FinishedProducts":
                product_instances = product_instances.filter(IsFinishedProduct=True)

            if length < 3:
                product_instances = product_instances.filter()[:10]

            product_ids = product_instances.values_list("ProductID", flat=True)
            batch_ins = None
            stockposting_ins = None
            if check_EnableProductBatchWise:
                if Batch.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID__in=product_ids
                ).exists():
                    batch_ins = Batch.objects.filter(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        ProductID__in=product_ids,
                    )
            price_list_ins = PriceList.objects.filter(
                CompanyID=CompanyID, ProductID__in=product_ids
            )
            if StockPosting.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID__in=product_ids
            ).exists():
                stockposting_ins = StockPosting.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID__in=product_ids
                )
                if WarehouseID:
                    stockposting_ins = stockposting_ins.filter(WareHouseID=WarehouseID)
                    if batch_ins:
                        batch_ins = batch_ins.filter(WareHouseID=WarehouseID)
            final_data = []
            for i in product_instances:
                price_list_pro_ins = price_list_ins.filter(
                    ProductID=i.ProductID, DefaultUnit=True
                ).first()
                DefaultUnitID = price_list_pro_ins.UnitID
                DefaultUnitName = ""
                if Unit.objects.filter(
                    CompanyID=CompanyID, UnitID=DefaultUnitID
                ).exists():
                    DefaultUnitName = (
                        Unit.objects.filter(CompanyID=CompanyID, UnitID=DefaultUnitID)
                        .first()
                        .UnitName
                    )
                Barcode = price_list_pro_ins.Barcode
                PurchasePrice = price_list_pro_ins.PurchasePrice
                SalesPrice = price_list_pro_ins.SalesPrice
                tax_gst = i.GST
                tax_vat = i.VatID
                GST_SalesTax = 0
                SalesTax = 0
                Tax1_SalesTax = 0
                Tax2_SalesTax = 0
                Tax3_SalesTax = 0
                is_GST_inclusive = False
                is_VAT_inclusive = False
                is_TAX1_inclusive = False
                is_TAX2_inclusive = False
                is_TAX3_inclusive = False
                GST_TaxName = ""
                VAT_TaxName = ""
                is_inclusive = i.is_inclusive
                if TaxCategory.objects.filter(
                    CompanyID=CompanyID, TaxID=tax_gst
                ).exists():
                    tax = TaxCategory.objects.get(CompanyID=CompanyID, TaxID=tax_gst)
                    GST_SalesTax = tax.SalesTax
                    is_GST_inclusive = tax.Inclusive
                    GST_TaxName = tax.TaxName
                if TaxCategory.objects.filter(
                    CompanyID=CompanyID, TaxID=tax_vat
                ).exists():
                    tax = TaxCategory.objects.get(CompanyID=CompanyID, TaxID=tax_vat)
                    SalesTax = tax.SalesTax
                    is_VAT_inclusive = tax.Inclusive
                    VAT_TaxName = tax.TaxName

                Stock = 0
                BatchCode = ""
                if check_EnableProductBatchWise:
                    if batch_ins:
                        batch_ins_pro = batch_ins.filter(ProductID=i.ProductID)
                        total_stockIN = converted_float(batch_ins_pro.StockIn)
                        total_stockOUT = converted_float(batch_ins_pro.StockOut)
                        Stock = converted_float(total_stockIN) - converted_float(
                            total_stockOUT
                        )
                        BatchCode = batch_ins_pro.filter().first().BatchCode
                else:
                    if stockposting_ins:
                        stockposting_ins_pro = stockposting_ins.filter(
                            ProductID=i.ProductID
                        )
                        total_stockIN = stockposting_ins_pro.aggregate(Sum("QtyIn"))
                        total_stockIN = total_stockIN["QtyIn__sum"]
                        total_stockOUT = stockposting_ins_pro.aggregate(Sum("QtyOut"))
                        total_stockOUT = total_stockOUT["QtyOut__sum"]
                        Stock = converted_float(total_stockIN) - converted_float(
                            total_stockOUT
                        )
                product_obj = {
                    "id": i.id,
                    "Description": i.Description,
                    "ProductID": i.ProductID,
                    "ProductCode": i.ProductCode,
                    "Barcode": Barcode,
                    "ProductName": i.ProductName,
                    "Stock": Stock,
                    "HSNCode": i.HSNCode,
                    "DefaultPurchasePrice": PurchasePrice,
                    "DefaultSalesPrice": SalesPrice,
                    "BatchCode": BatchCode,
                    "DefaultUnitID": DefaultUnitID,
                    "DefaultUnitName": DefaultUnitName,
                    "GST_SalesTax": GST_SalesTax,
                    "SalesTax": SalesTax,
                    "Tax1_SalesTax": Tax1_SalesTax,
                    "Tax2_SalesTax": Tax2_SalesTax,
                    "Tax3_SalesTax": Tax3_SalesTax,
                    "is_GST_inclusive": is_GST_inclusive,
                    "is_VAT_inclusive": is_VAT_inclusive,
                    "is_TAX1_inclusive": is_TAX1_inclusive,
                    "is_TAX2_inclusive": is_TAX2_inclusive,
                    "is_TAX3_inclusive": is_TAX3_inclusive,
                    "GST_TaxName": GST_TaxName,
                    "VAT_TaxName": VAT_TaxName,
                    "is_inclusive": is_inclusive,
                }
                if (
                    (type == "StockTransfer" and AllowNegativeStockInStockTransfer)
                    or type == "Purchase"
                    or (type == "Sales" and check_AllowNegativeStockSales)
                ):
                    final_data.append(product_obj)
                else:
                    if Stock > 0 or i.is_Service == True:
                        final_data.append(product_obj)

            response_data = {"StatusCode": 6000, "data": final_data}

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {"StatusCode": 6001, "message": "Product Not Found"}
            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!",
        }
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def get_product_details(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    ProductID = data["ProductID"]
    BranchID = data["BranchID"]
    WarehouseID = data["WarehouseID"]
    BatchCode = data["BatchCode"]

    if Product.objects.filter(CompanyID=CompanyID,ProductID=ProductID,Active=True).exists():
        product_instances = Product.objects.filter(CompanyID=CompanyID,ProductID=ProductID,Active=True).first()
        Description = product_instances.Description
        id = product_instances.id
        Stock = get_ProductWareHouseStock(
            CompanyID, BranchID, ProductID, WarehouseID, BatchCode)

        data = {
            "Description": Description,
            "Stock": Stock,
            "id": id
        }
        response_data = {"StatusCode": 6000, "data": data}

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {"StatusCode": 6001,
                            "message": "Product Not Found"}
        return Response(response_data, status=status.HTTP_200_OK)

