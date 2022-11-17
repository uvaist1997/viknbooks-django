from brands.models import Product,VoucherNoTable,StockPosting, StockPosting_Log, ExcessStockMaster, ExcessStockDetails, ExcessStockMaster_Log, StockRate, PriceList, StockTrans, ExcessStockDetails_Log, ShortageStockMaster, ShortageStockMaster_Log, ShortageStockDetails, ShortageStockDetails_Log,\
    DamageStockMaster, DamageStockMaster_Log, DamageStockDetails, DamageStockDetails_Log, UsedStockMaster, UsedStockMaster_Log, UsedStockDetails, UsedStockDetails_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v8.stockPostings.serializers import StockPostingSerializer,ExcessStockMaster1Serializer,UsedStockMaster1Serializer,ShortageStockMaster1Serializer,DamageStockMaster1Serializer, StockPostingRestSerializer, ExcessStockMasterSerializer, ShortageStockMasterSerializer, DamageStockMasterSerializer, UsedStockMasterSerializer, UsedStockDetailSerializer
from api.v8.brands.serializers import ListSerializer
from api.v8.stockPostings.functions import generate_serializer_errors
from rest_framework import status
from api.v8.stockPostings.functions import get_auto_id, get_auto_excessMasterID, get_auto_excessDetailsID, get_auto_shortageMasterID, get_auto_shortageDetailsID, get_auto_damageMasterID, get_auto_damageDetailsID, get_auto_usedMasterID,\
    get_auto_usedDetailsID
from api.v8.purchases.functions import get_auto_StockRateID, get_auto_StockTransID
import datetime
from main.functions import get_company, activity_log
from api.v8.sales.functions import get_auto_stockPostid
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Prefetch
from django.db import transaction,IntegrityError
import re,sys, os
from api.v8.products.functions import update_stock
from main.functions import update_voucher_table


def call_paginator_all(model_object, page_number, items_per_page):
    paginator = Paginator(model_object, items_per_page)
    content = paginator.page(page_number)
    return content


def list_pagination(list_value, items_per_page, page_no):
    paginator_object = Paginator(list_value, items_per_page)
    get_value = paginator_object.page(page_no).object_list
    return get_value


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_stockPosting(request):
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

        StockPostingID = get_auto_id(StockPosting, BranchID, CompanyID)

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
            CompanyID=CompanyID,
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
            CompanyID=CompanyID,
        )

        data = {"StockPostingID": StockPostingID}
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
@renderer_classes((JSONRenderer,))
def edit_stockPosting(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    serialized = StockPostingSerializer(data=request.data)
    instance = None
    if StockPosting.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = StockPosting.objects.get(CompanyID=CompanyID, pk=pk)

        StockPostingID = instance.StockPostingID
        BranchID = instance.BranchID

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

            data = {"StockPostingID": StockPostingID}
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
            "message": "Stock Posting Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def stockPostings(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']
        if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instances = StockPosting.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
            serialized = StockPostingRestSerializer(instances, many=True)
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Stock Posting Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def stockPosting(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    instance = None
    if StockPosting.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = StockPosting.objects.get(CompanyID=CompanyID, pk=pk)
    if instance:
        serialized = StockPostingRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "StockPosting Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_stockPosting(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    instance = None
    if StockPosting.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = StockPosting.objects.get(CompanyID=CompanyID, pk=pk)
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
            "StatusCode": 6000,
            "message": "Stock Posting Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Stock Posting Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def create_excess_stock(request):
    try:
        with transaction.atomic():
            today = datetime.datetime.now()

            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)

            CreatedUserID = data['CreatedUserID']
            BranchID = data['BranchID']
            VoucherNo = data['VoucherNo']
            Date = data['Date']
            Notes = data['Notes']
            WarehouseID = data['WarehouseID']
            TotalQty = data['TotalQty']
            GrandTotal = data['GrandTotal']

            VoucherType = "ES"

            # VoucherNo Updated
            try:
                PreFix = data['PreFix']
            except:
                PreFix = "ES"

            try:
                Seperator = data['Seperator']
            except:
                Seperator = ""

            try:
                InvoiceNo = data['InvoiceNo']
            except:
                InvoiceNo = 1

            Action = "A"

            if not ExcessStockMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherNo__iexact=VoucherNo).exists():
                update_voucher_table(CompanyID,CreatedUserID,VoucherType,PreFix,Seperator, InvoiceNo)
                ExcessStockMasterID = get_auto_excessMasterID(
                    ExcessStockMaster, BranchID, CompanyID)

                ExcessStockMaster_Log.objects.create(
                    TransactionID=ExcessStockMasterID,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    Date=Date,
                    Notes=Notes,
                    WarehouseID=WarehouseID,
                    TotalQty=TotalQty,
                    GrandTotal=GrandTotal,
                    CreatedDate=today,
                    LastUPDDate=today,
                    CreatedUserID=CreatedUserID,
                    LastUPDUserID=CreatedUserID,
                )
                ExcessStockMaster.objects.create(
                    CompanyID=CompanyID,
                    ExcessStockMasterID=ExcessStockMasterID,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    Date=Date,
                    Notes=Notes,
                    WarehouseID=WarehouseID,
                    TotalQty=TotalQty,
                    GrandTotal=GrandTotal,
                    CreatedDate=today,
                    LastUPDDate=today,
                    CreatedUserID=CreatedUserID,
                    LastUPDUserID=CreatedUserID,

                )

                Details = data["Details"]

                VoucherType = "ES"

                for d in Details:
                    ProductID = d['ProductID']
                    Stock = d['Stock']
                    PriceListID = d['PriceListID']
                    ExcessStock = d['ExcessStock']
                    CostPerItem = d['CostPerItem']

                    ExcessStockDetailsID = get_auto_excessDetailsID(
                        ExcessStockDetails, BranchID, CompanyID)

                    log_instances = ExcessStockDetails_Log.objects.create(
                        TransactionID=ExcessStockDetailsID,
                        BranchID=BranchID,
                        Action=Action,
                        ExcessStockMasterID=ExcessStockMasterID,
                        ProductID=ProductID,
                        Stock=Stock,
                        PriceListID=PriceListID,
                        ExcessStock=ExcessStock,
                        CreatedDate=today,
                        LastUPDDate=today,
                        CreatedUserID=CreatedUserID,
                        LastUPDUserID=CreatedUserID,
                        CostPerItem=CostPerItem,
                        CompanyID=CompanyID,
                    )
                    ExcessStockDetails.objects.create(
                        CompanyID=CompanyID,
                        ExcessStockDetailsID=ExcessStockDetailsID,
                        BranchID=BranchID,
                        Action=Action,
                        ExcessStockMasterID=ExcessStockMasterID,
                        ProductID=ProductID,
                        Stock=Stock,
                        PriceListID=PriceListID,
                        ExcessStock=ExcessStock,
                        CreatedDate=today,
                        LastUPDDate=today,
                        CreatedUserID=CreatedUserID,
                        LastUPDUserID=CreatedUserID,
                        CostPerItem=CostPerItem,
                        LogID=log_instances.ID
                    )

                    product_is_Service = Product.objects.get(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).is_Service
                    MultiFactor = PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).MultiFactor
                    PriceListID_DefUnit = PriceList.objects.get(
                        CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True, BranchID=BranchID).PriceListID

                    princeList_instance = PriceList.objects.get(
                        CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID_DefUnit, BranchID=BranchID)
                    PurchasePrice = princeList_instance.PurchasePrice
                    SalesPrice = princeList_instance.SalesPrice

                    # qty = float(FreeQty) + float(Qty)

                    Qty = float(MultiFactor) * float(ExcessStock)
                    Cost = float(CostPerItem) / float(MultiFactor)

                    StockPostingID = get_auto_stockPostid(
                        StockPosting, BranchID, CompanyID)

                    StockPosting.objects.create(
                        StockPostingID=StockPostingID,
                        BranchID=BranchID,
                        Action=Action,
                        Date=Date,
                        VoucherMasterID=ExcessStockMasterID,
                        VoucherDetailID=ExcessStockDetailsID,
                        VoucherType=VoucherType,
                        ProductID=ProductID,
                        WareHouseID=WarehouseID,
                        QtyIn=Qty,
                        Rate=Cost,
                        PriceListID=PriceListID,
                        IsActive=True,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                    )

                    StockPosting_Log.objects.create(
                        TransactionID=StockPostingID,
                        BranchID=BranchID,
                        Action=Action,
                        Date=Date,
                        VoucherMasterID=ExcessStockMasterID,
                        VoucherDetailID=ExcessStockDetailsID,
                        VoucherType=VoucherType,
                        ProductID=ProductID,
                        WareHouseID=WarehouseID,
                        QtyIn=Qty,
                        Rate=Cost,
                        PriceListID=PriceListID,
                        IsActive=True,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                    )

                    update_stock(CompanyID,BranchID,ProductID)

                    # if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Cost=CostPerItem, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID).exists():
                    #     stockRateInstance = StockRate.objects.get(
                    #         CompanyID=CompanyID, BranchID=BranchID, Cost=CostPerItem, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID)

                    #     StockRateID = stockRateInstance.StockRateID
                    #     stockRateInstance.Qty = float(
                    #         stockRateInstance.Qty) + float(ExcessStock)
                    #     stockRateInstance.save()

                    #     if StockTrans.objects.filter(StockRateID=StockRateID, DetailID=ExcessStockDetailsID, MasterID=ExcessStockMasterID, VoucherType=VoucherType, BranchID=BranchID, IsActive=True).exists():
                    #         stockTra_in = StockTrans.objects.filter(StockRateID=StockRateID, DetailID=ExcessStockDetailsID,
                    #                                                 MasterID=ExcessStockMasterID, VoucherType=VoucherType, BranchID=BranchID, IsActive=True).first()
                    #         stockTra_in.Qty = float(
                    #             stockTra_in.Qty) + float(ExcessStock)
                    #         stockTra_in.save()
                    #     else:
                    #         StockTransID = get_auto_StockTransID(
                    #             StockTrans, BranchID, CompanyID)
                    #         StockTrans.objects.create(
                    #             StockTransID=StockTransID,
                    #             BranchID=BranchID,
                    #             VoucherType=VoucherType,
                    #             StockRateID=StockRateID,
                    #             DetailID=ExcessStockDetailsID,
                    #             MasterID=ExcessStockMasterID,
                    #             Qty=ExcessStock,
                    #             IsActive=True,
                    #             CompanyID=CompanyID,
                    #         )

                    # else:
                    #     StockRateID = get_auto_StockRateID(
                    #         StockRate, BranchID, CompanyID)
                    #     StockRate.objects.create(
                    #         StockRateID=StockRateID,
                    #         BranchID=BranchID,
                    #         PurchasePrice=PurchasePrice,
                    #         SalesPrice=SalesPrice,
                    #         Qty=ExcessStock,
                    #         Cost=CostPerItem,
                    #         ProductID=ProductID,
                    #         WareHouseID=WarehouseID,
                    #         Date=Date,
                    #         PriceListID=PriceListID,
                    #         CreatedUserID=CreatedUserID,
                    #         CreatedDate=today,
                    #         UpdatedDate=today,
                    #         CompanyID=CompanyID,
                    #     )

                    #     StockTransID = get_auto_StockTransID(
                    #         StockTrans, BranchID, CompanyID)
                    #     StockTrans.objects.create(
                    #         StockTransID=StockTransID,
                    #         BranchID=BranchID,
                    #         VoucherType=VoucherType,
                    #         StockRateID=StockRateID,
                    #         DetailID=ExcessStockDetailsID,
                    #         MasterID=ExcessStockMasterID,
                    #         Qty=ExcessStock,
                    #         IsActive=True,
                    #         CompanyID=CompanyID,
                    #     )

                response_data = {
                    "StatusCode": 6000,
                    "message": "Excess Stock Created Successfully!!!"
                }

                return Response(response_data, status=status.HTTP_200_OK)

            else:
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Sales Invoice',
                         'Create', 'Sales Invoice create failed.', 'VoucherNo Already exists.')
                response_data = {
                    "StatusCode": 6001,
                    "message": "VoucherNo Already Exist.Please Change Your Prefix!"
                }

                return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again"
        }

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Excess Stock',
                         'Create', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_excessStock(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    serialized1 = ListSerializer(data=request.data)

    try:
        page_number = data['page_no']
    except:
        page_number = ""

    try:
        items_per_page = data['items_per_page']
    except:
        items_per_page = ""

    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if ExcessStockMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():

            if page_number and items_per_page:
                instances = ExcessStockMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)
                count = len(instances)
                ledger_sort_pagination = list_pagination(
                    instances,
                    items_per_page,
                    page_number
                )
                print(ledger_sort_pagination)
                # serialized = WarehouseRestSerializer(ledger_sort_pagination, many=True)
                # data = serialized.data
            else:
                ledger_sort_pagination = ExcessStockMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)
                count = len(ledger_sort_pagination)
            serialized = ExcessStockMaster1Serializer(ledger_sort_pagination, many=True, context={"CompanyID": CompanyID,
                                                                                                 "PriceRounding": PriceRounding})
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "count": count
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Excess Stock Not Found in this Branch!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_excessStock(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    instance = None
    if ExcessStockMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = ExcessStockMaster.objects.get(CompanyID=CompanyID, pk=pk)
        ExcessStockMasterID = instance.ExcessStockMasterID
        BranchID = instance.BranchID
        Date = instance.Date
        VoucherNo = instance.VoucherNo
        Notes = instance.Notes
        WarehouseID = instance.WarehouseID
        TotalQty = instance.TotalQty
        GrandTotal = instance.GrandTotal
        Action = "D"

        instance.delete()
        ExcessStockMaster_Log.objects.create(
            TransactionID=ExcessStockMasterID,
            BranchID=BranchID,
            Action=Action,
            VoucherNo=VoucherNo,
            Date=Date,
            Notes=Notes,
            WarehouseID=WarehouseID,
            TotalQty=TotalQty,
            GrandTotal=GrandTotal,
            CreatedDate=today,
            LastUPDDate=today,
            CreatedUserID=CreatedUserID,
            LastUPDUserID=CreatedUserID,
        )

        if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=ExcessStockMasterID, BranchID=BranchID, VoucherType="ES").exists():

            stockPostingInstances = StockPosting.objects.filter(
                CompanyID=CompanyID, VoucherMasterID=ExcessStockMasterID, BranchID=BranchID, VoucherType="ES")

            for stockPostingInstance in stockPostingInstances:

                StockPostingID = stockPostingInstance.StockPostingID
                BranchID = stockPostingInstance.BranchID
                Date = stockPostingInstance.Date
                VoucherMasterID = stockPostingInstance.VoucherMasterID
                VoucherDetailID = stockPostingInstance.VoucherDetailID
                VoucherType = stockPostingInstance.VoucherType
                ProductID = stockPostingInstance.ProductID
                BatchID = stockPostingInstance.BatchID
                WareHouseID = stockPostingInstance.WareHouseID
                QtyIn = stockPostingInstance.QtyIn
                QtyOut = stockPostingInstance.QtyOut
                Rate = stockPostingInstance.Rate
                PriceListID = stockPostingInstance.PriceListID
                IsActive = stockPostingInstance.IsActive

                StockPosting_Log.objects.create(
                    TransactionID=StockPostingID,
                    BranchID=BranchID,
                    Action=Action,
                    Date=Date,
                    VoucherMasterID=VoucherMasterID,
                    VoucherDetailID=VoucherDetailID,
                    VoucherType=VoucherType,
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

                stockPostingInstance.delete()

                update_stock(CompanyID,BranchID,ProductID)

        detail_instances = ExcessStockDetails.objects.filter(
            CompanyID=CompanyID, ExcessStockMasterID=ExcessStockMasterID)

        for detail_instance in detail_instances:

            ExcessStockDetailsID = detail_instance.ExcessStockDetailsID
            BranchID = detail_instance.BranchID
            ExcessStockMasterID = detail_instance.ExcessStockMasterID
            ProductID = detail_instance.ProductID
            Stock = detail_instance.Stock
            PriceListID = detail_instance.PriceListID
            ExcessStock = detail_instance.ExcessStock
            CostPerItem = detail_instance.CostPerItem

            ExcessStockDetails_Log.objects.create(
                TransactionID=ExcessStockDetailsID,
                BranchID=BranchID,
                Action=Action,
                ExcessStockMasterID=ExcessStockMasterID,
                ProductID=ProductID,
                Stock=Stock,
                PriceListID=PriceListID,
                ExcessStock=ExcessStock,
                CreatedDate=today,
                LastUPDDate=today,
                CreatedUserID=CreatedUserID,
                LastUPDUserID=CreatedUserID,
                CostPerItem=CostPerItem,
                CompanyID=CompanyID,
            )
            update_stock(CompanyID,BranchID,ProductID)

            detail_instance.delete()

            # if StockTrans.objects.filter(CompanyID=CompanyID,DetailID=PurchaseDetailsID,MasterID=PurchaseMasterID,BranchID=BranchID,VoucherType="PI").exists():
            #     stockTrans_instance = StockTrans.objects.get(CompanyID=CompanyID,DetailID=PurchaseDetailsID,MasterID=PurchaseMasterID,BranchID=BranchID,VoucherType="PI")

            #     stockRateID = stockTrans_instance.StockRateID
            #     stockTrans_instance.IsActive = False
            #     stockTrans_instance.save()

            #     stockRate_instance = StockRate.objects.get(CompanyID=CompanyID,StockRateID=stockRateID,BranchID=BranchID)
            #     stockRate_instance.Qty = stockTrans_instance.Qty
            #     stockRate_instance.save()

            if StockTrans.objects.filter(CompanyID=CompanyID, DetailID=ExcessStockDetailsID, MasterID=ExcessStockMasterID, BranchID=BranchID, VoucherType="ES", IsActive=True).exists():
                stockTrans_instances = StockTrans.objects.filter(
                    CompanyID=CompanyID, DetailID=ExcessStockDetailsID, MasterID=ExcessStockMasterID, BranchID=BranchID, VoucherType="ES", IsActive=True)

                for i in stockTrans_instances:
                    stockRateID = i.StockRateID
                    i.IsActive = False
                    i.save()

                    stockRate_instance = StockRate.objects.get(
                        CompanyID=CompanyID, StockRateID=stockRateID, BranchID=BranchID)
                    stockRate_instance.Qty = i.Qty
                    stockRate_instance.save()
        response_data = {
            "StatusCode": 6000,
            "message": "Excess Stock Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Excess Stock Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def edit_excessStock(request, pk):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            CreatedUserID = data['CreatedUserID']
            today = datetime.datetime.now()

            excessStockMaster_instance = ExcessStockMaster.objects.get(
                pk=pk, CompanyID=CompanyID)
            ExcessStockMasterID = excessStockMaster_instance.ExcessStockMasterID
            BranchID = excessStockMaster_instance.BranchID

            VoucherType = "ES"

            VoucherNo = data['VoucherNo']
            Date = data['Date']
            Notes = data['Notes']
            WarehouseID = data['WarehouseID']
            TotalQty = data['TotalQty']
            GrandTotal = data['GrandTotal']

            Action = "M"

            ExcessStockMaster_Log.objects.create(
                TransactionID=ExcessStockMasterID,
                BranchID=BranchID,
                Action=Action,
                VoucherNo=VoucherNo,
                Date=Date,
                Notes=Notes,
                WarehouseID=WarehouseID,
                TotalQty=TotalQty,
                GrandTotal=GrandTotal,
                CreatedDate=today,
                LastUPDDate=today,
                CreatedUserID=CreatedUserID,
                LastUPDUserID=CreatedUserID,
            )

            # if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=ExcessStockMasterID, BranchID=BranchID, VoucherType=VoucherType).exists():
            #     stockPostingInstances = StockPosting.objects.filter(
            #         CompanyID=CompanyID, VoucherMasterID=ExcessStockMasterID, BranchID=BranchID, VoucherType=VoucherType)
            #     for stockPostingInstance in stockPostingInstances:
            #         stockPostingInstance.delete()

            if ExcessStockDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ExcessStockMasterID=ExcessStockMasterID).exists():
                excessStockInstances = ExcessStockDetails.objects.filter(
                    CompanyID=CompanyID, ExcessStockMasterID=ExcessStockMasterID, BranchID=BranchID)
                for i in excessStockInstances:
                    if not StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=ExcessStockMasterID,VoucherDetailID=i.ExcessStockDetailsID,BranchID=BranchID, VoucherType="ES").exists():
                        StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=ExcessStockMasterID,BranchID=BranchID, VoucherType="ES").delete()
                        update_stock(CompanyID,BranchID,i.ProductID)

                    instance_MultiFactor = PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=i.PriceListID, BranchID=BranchID).MultiFactor

                    instance_qty_sum = float(i.ExcessStock)
                    instance_Qty = float(instance_MultiFactor) * float(instance_qty_sum)
                    if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=ExcessStockMasterID,VoucherDetailID=i.ExcessStockDetailsID,ProductID=i.ProductID,BranchID=BranchID, VoucherType="ES").exists():
                        stock_inst = StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=ExcessStockMasterID,VoucherDetailID=i.ExcessStockDetailsID,ProductID=i.ProductID,BranchID=BranchID, VoucherType="ES").first()
                        stock_inst.QtyIn = float(stock_inst.QtyIn) - float(instance_Qty)
                        stock_inst.save()
                        update_stock(CompanyID,BranchID,i.ProductID)

            # if ExcessStockDetails.objects.filter(ExcessStockMasterID=ExcessStockMasterID, BranchID=BranchID, CompanyID=CompanyID).exists():
            #     excessStockDetails_instances = ExcessStockDetails.objects.filter(
            #         ExcessStockMasterID=ExcessStockMasterID, BranchID=BranchID, CompanyID=CompanyID)
            #     excessStockDetails_instances
            #     for detail in excessStockDetails_instances:
            #         detail.delete()

            # if StockTrans.objects.filter(CompanyID=CompanyID, VoucherType=VoucherType, MasterID=ExcessStockMasterID, BranchID=BranchID, IsActive=True).exists():
            #     trans_ins = StockTrans.objects.filter(
            #         CompanyID=CompanyID, VoucherType=VoucherType, MasterID=ExcessStockMasterID, BranchID=BranchID, IsActive=True)
            #     for stk in trans_ins:
            #         StockRateID = stk.StockRateID
            #         stockQty = stk.Qty

            #         rate_ins = StockRate.objects.filter(
            #             CompanyID=CompanyID, StockRateID=StockRateID, BranchID=BranchID).first()
            #         rate_ins.Qty = float(rate_ins.Qty) - float(stockQty)
            #         rate_ins.save()
            #         stk.IsActive = False
            #         stk.save()
            excessStockMaster_instance.Date = Date
            excessStockMaster_instance.Notes = Notes
            excessStockMaster_instance.WarehouseID = WarehouseID
            excessStockMaster_instance.TotalQty = TotalQty
            excessStockMaster_instance.GrandTotal = GrandTotal
            excessStockMaster_instance.Action = Action
            excessStockMaster_instance.LastUPDDate = today
            excessStockMaster_instance.LastUPDUserID = CreatedUserID

            excessStockMaster_instance.save()

            Details = data["Details"]

            for d in Details:
                if d['id']:
                    pk = d['id']
                ProductID = d['ProductID']
                Stock = d['Stock']
                PriceListID = d['PriceListID']
                ExcessStock = d['ExcessStock']
                CostPerItem = d['CostPerItem']
                detailID = d['detailID']

                product_is_Service = Product.objects.get(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).is_Service
                MultiFactor = PriceList.objects.get(
                    CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).MultiFactor
                PriceListID_DefUnit = PriceList.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True, BranchID=BranchID).PriceListID

                princeList_instance = PriceList.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID_DefUnit, BranchID=BranchID)
                PurchasePrice = princeList_instance.PurchasePrice
                SalesPrice = princeList_instance.SalesPrice

                # qty = float(FreeQty) + float(Qty)

                Qty = float(MultiFactor) * float(ExcessStock)
                Cost = float(CostPerItem) / float(MultiFactor)

                if detailID == 0:
                    excessStockDetail_instance = ExcessStockDetails.objects.get(
                        CompanyID=CompanyID, pk=pk)
                    ExcessStockDetailsID = excessStockDetail_instance.ExcessStockDetailsID

                    log_instance = ExcessStockDetails_Log.objects.create(
                        TransactionID=ExcessStockDetailsID,
                        BranchID=BranchID,
                        Action=Action,
                        ExcessStockMasterID=ExcessStockMasterID,
                        ProductID=ProductID,
                        Stock=Stock,
                        PriceListID=PriceListID,
                        ExcessStock=ExcessStock,
                        CreatedDate=today,
                        LastUPDDate=today,
                        CreatedUserID=CreatedUserID,
                        LastUPDUserID=CreatedUserID,
                        CostPerItem=CostPerItem,
                        CompanyID=CompanyID,
                    )

                    excessStockDetail_instance.ProductID = ProductID
                    excessStockDetail_instance.Stock = Stock
                    excessStockDetail_instance.PriceListID = PriceListID
                    excessStockDetail_instance.CostPerItem = CostPerItem
                    excessStockDetail_instance.ExcessStock = ExcessStock
                    excessStockDetail_instance.Action = Action
                    excessStockDetail_instance.LastUPDDate = today
                    excessStockDetail_instance.save()

                    if product_is_Service == False:
                        if StockPosting.objects.filter(CompanyID=CompanyID,WareHouseID=WarehouseID, VoucherMasterID=ExcessStockMasterID,VoucherDetailID=ExcessStockDetailsID,BranchID=BranchID, VoucherType="ES",ProductID=ProductID).exists():
                            stock_instance = StockPosting.objects.filter(CompanyID=CompanyID,WareHouseID=WarehouseID, VoucherMasterID=ExcessStockMasterID,VoucherDetailID=ExcessStockDetailsID,BranchID=BranchID, VoucherType="ES",ProductID=ProductID).first()
                            stock_instance.QtyIn = Qty
                            stock_instance.Action = Action
                            stock_instance.UpdatedDate = today
                            stock_instance.save()
                            update_stock(CompanyID,BranchID,i.ProductID)
                        else:
                            StockPostingID = get_auto_stockPostid(
                                StockPosting, BranchID, CompanyID)
                            StockPosting.objects.create(
                                StockPostingID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=Date,
                                VoucherMasterID=ExcessStockMasterID,
                                VoucherDetailID=ExcessStockDetailsID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                WareHouseID=WarehouseID,
                                QtyIn=Qty,
                                Rate=Cost,
                                PriceListID=PriceListID_DefUnit,
                                IsActive=IsActive,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                            )

                            StockPosting_Log.objects.create(
                                TransactionID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=Date,
                                VoucherMasterID=ExcessStockMasterID,
                                VoucherDetailID=ExcessStockDetailsID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                WareHouseID=WarehouseID,
                                QtyIn=Qty,
                                Rate=Cost,
                                PriceListID=PriceListID_DefUnit,
                                IsActive=IsActive,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                            )

                            update_stock(CompanyID,BranchID,ProductID)

                if detailID == 1:
                    Action = "A"
                    ExcessStockDetailsID = get_auto_excessDetailsID(
                        ExcessStockDetails, BranchID, CompanyID)

                    log_instance = ExcessStockDetails_Log.objects.create(
                        TransactionID=ExcessStockDetailsID,
                        BranchID=BranchID,
                        Action=Action,
                        ExcessStockMasterID=ExcessStockMasterID,
                        ProductID=ProductID,
                        Stock=Stock,
                        PriceListID=PriceListID,
                        ExcessStock=ExcessStock,
                        CreatedDate=today,
                        LastUPDDate=today,
                        CreatedUserID=CreatedUserID,
                        LastUPDUserID=CreatedUserID,
                        CostPerItem=CostPerItem,
                        CompanyID=CompanyID,
                    )

                    ExcessStockDetails.objects.create(
                        CompanyID=CompanyID,
                        ExcessStockDetailsID=ExcessStockDetailsID,
                        BranchID=BranchID,
                        Action=Action,
                        ExcessStockMasterID=ExcessStockMasterID,
                        ProductID=ProductID,
                        Stock=Stock,
                        PriceListID=PriceListID,
                        ExcessStock=ExcessStock,
                        CreatedDate=today,
                        LastUPDDate=today,
                        CreatedUserID=CreatedUserID,
                        LastUPDUserID=CreatedUserID,
                        CostPerItem=CostPerItem,
                        LogID=log_instance.ID
                    )

                    if product_is_Service == False:
                        StockPostingID = get_auto_stockPostid(
                            StockPosting, BranchID, CompanyID)
                        StockPosting.objects.create(
                            StockPostingID=StockPostingID,
                            BranchID=BranchID,
                            Action=Action,
                            Date=Date,
                            VoucherMasterID=ExcessStockMasterID,
                            VoucherDetailID=ExcessStockDetailsID,
                            VoucherType=VoucherType,
                            ProductID=ProductID,
                            WareHouseID=WarehouseID,
                            QtyIn=Qty,
                            Rate=Cost,
                            PriceListID=PriceListID_DefUnit,
                            IsActive=True,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )

                        StockPosting_Log.objects.create(
                            TransactionID=StockPostingID,
                            BranchID=BranchID,
                            Action=Action,
                            Date=Date,
                            VoucherMasterID=ExcessStockMasterID,
                            VoucherDetailID=ExcessStockDetailsID,
                            VoucherType=VoucherType,
                            ProductID=ProductID,
                            WareHouseID=WarehouseID,
                            QtyIn=Qty,
                            Rate=Cost,
                            PriceListID=PriceListID_DefUnit,
                            IsActive=True,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )

                        update_stock(CompanyID,BranchID,ProductID)

                # pricelist_ins = PriceList.objects.get(
                #     PriceListID=PriceListID, CompanyID=CompanyID, BranchID=BranchID)
                # SalesPrice = pricelist_ins.SalesPrice
                # PurchasePrice = pricelist_ins.PurchasePrice

                # StockPostingID = get_auto_stockPostid(
                #     StockPosting, BranchID, CompanyID)

                # StockPosting.objects.create(
                #     StockPostingID=StockPostingID,
                #     BranchID=BranchID,
                #     Action=Action,
                #     Date=Date,
                #     VoucherMasterID=ExcessStockMasterID,
                #     VoucherType=VoucherType,
                #     ProductID=ProductID,
                #     WareHouseID=WarehouseID,
                #     QtyIn=ExcessStock,
                #     Rate=CostPerItem,
                #     PriceListID=PriceListID,
                #     IsActive=True,
                #     CreatedDate=today,
                #     UpdatedDate=today,
                #     CreatedUserID=CreatedUserID,
                #     CompanyID=CompanyID,
                # )

                # StockPosting_Log.objects.create(
                #     TransactionID=StockPostingID,
                #     BranchID=BranchID,
                #     Action=Action,
                #     Date=Date,
                #     VoucherMasterID=ExcessStockMasterID,
                #     VoucherType=VoucherType,
                #     ProductID=ProductID,
                #     WareHouseID=WarehouseID,
                #     QtyIn=ExcessStock,
                #     Rate=CostPerItem,
                #     PriceListID=PriceListID,
                #     IsActive=True,
                #     CreatedDate=today,
                #     UpdatedDate=today,
                #     CreatedUserID=CreatedUserID,
                #     CompanyID=CompanyID,
                # )

                # update_stock(CompanyID,BranchID,ProductID)

            deleted_datas = data["deleted_data"]
            if deleted_datas:
                for deleted_Data in deleted_datas:
                    deleted_pk = deleted_Data['unq_id']
                    ExcessStockDetailID_Deleted = deleted_Data['ExcessStockDetailID']
                    ProductID_Deleted = deleted_Data['ProductID']
                    PriceListID_Deleted = deleted_Data['PriceListID']
                    Rate_Deleted = deleted_Data['Rate']
                    ExcessStockMasterID_Deleted = deleted_Data['ExcessStockMasterID']
                    WarehouseID_Deleted = deleted_Data['WarehouseID']

                    update_stock(CompanyID,BranchID,ProductID_Deleted)

                    if not deleted_pk == '' or not deleted_pk == 0:
                        if ExcessStockDetails.objects.filter(CompanyID=CompanyID,pk=deleted_pk).exists():
                            deleted_detail = ExcessStockDetails.objects.filter(CompanyID=CompanyID,pk=deleted_pk)
                            deleted_detail.delete()

                            if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=ExcessStockMasterID_Deleted,VoucherDetailID=ExcessStockDetailID_Deleted,ProductID=ProductID_Deleted,BranchID=BranchID, VoucherType="ES").exists():
                                stock_instances_delete = StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=ExcessStockMasterID_Deleted,VoucherDetailID=ExcessStockDetailID_Deleted,ProductID=ProductID_Deleted,BranchID=BranchID, VoucherType="ES")
                                stock_instances_delete.delete()
                                update_stock(CompanyID,BranchID,ProductID_Deleted)

            # deleted_ids = data["deleted_ids"]
            # for d in deleted_ids:
            #     update_stock(CompanyID,BranchID,d)

                # if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Cost=CostPerItem, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID).exists():
                #     stockRateInstance = StockRate.objects.get(
                #         CompanyID=CompanyID, BranchID=BranchID, Cost=CostPerItem, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID)

                #     StockRateID = stockRateInstance.StockRateID
                #     stockRateInstance.Qty = float(
                #         stockRateInstance.Qty) + float(ExcessStock)
                #     stockRateInstance.save()

                #     if StockTrans.objects.filter(StockRateID=StockRateID, DetailID=ExcessStockDetailsID, MasterID=ExcessStockMasterID, VoucherType=VoucherType, BranchID=BranchID, IsActive=True).exists():
                #         stockTra_in = StockTrans.objects.filter(StockRateID=StockRateID, DetailID=ExcessStockDetailsID,
                #                                                 MasterID=ExcessStockMasterID, VoucherType=VoucherType, BranchID=BranchID, IsActive=True).first()
                #         stockTra_in.Qty = float(stockTra_in.Qty) + float(ExcessStock)
                #         stockTra_in.save()
                #     else:
                #         StockTransID = get_auto_StockTransID(
                #             StockTrans, BranchID, CompanyID)
                #         StockTrans.objects.create(
                #             StockTransID=StockTransID,
                #             BranchID=BranchID,
                #             VoucherType=VoucherType,
                #             StockRateID=StockRateID,
                #             DetailID=ExcessStockDetailsID,
                #             MasterID=ExcessStockMasterID,
                #             Qty=ExcessStock,
                #             IsActive=True,
                #             CompanyID=CompanyID,
                #         )

                # else:
                #     StockRateID = get_auto_StockRateID(StockRate, BranchID, CompanyID)
                #     StockRate.objects.create(
                #         StockRateID=StockRateID,
                #         BranchID=BranchID,
                #         PurchasePrice=PurchasePrice,
                #         SalesPrice=SalesPrice,
                #         Qty=ExcessStock,
                #         Cost=CostPerItem,
                #         ProductID=ProductID,
                #         WareHouseID=WarehouseID,
                #         Date=Date,
                #         PriceListID=PriceListID,
                #         CreatedUserID=CreatedUserID,
                #         CreatedDate=today,
                #         UpdatedDate=today,
                #         CompanyID=CompanyID,
                #     )

                #     StockTransID = get_auto_StockTransID(
                #         StockTrans, BranchID, CompanyID)
                #     StockTrans.objects.create(
                #         StockTransID=StockTransID,
                #         BranchID=BranchID,
                #         VoucherType=VoucherType,
                #         StockRateID=StockRateID,
                #         DetailID=ExcessStockDetailsID,
                #         MasterID=ExcessStockMasterID,
                #         Qty=ExcessStock,
                #         IsActive=True,
                #         CompanyID=CompanyID,
                #     )
            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'ExcessStock',
            #              'Edit', 'ExcessStock Updated successfully.', 'ExcessStock Updated successfully.')
            response_data = {
                "StatusCode": 6000,
                "message": "Excess Stock Updated Successfully!!!",
            }

            return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again"
        }

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Excess Stock',
                         'Edit', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def excessStock(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if ExcessStockMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
            instance = ExcessStockMaster.objects.get(
                CompanyID=CompanyID, pk=pk)
            serialized = ExcessStockMasterSerializer(instance, context={"CompanyID": CompanyID,
                                                                        "PriceRounding": PriceRounding})
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Excess Stock Not Found in this Branch!"
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
@transaction.atomic
def create_shortage_stock(request):
    try:
        with transaction.atomic():
            today = datetime.datetime.now()

            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)

            CreatedUserID = data['CreatedUserID']
            BranchID = data['BranchID']
            VoucherNo = data['VoucherNo']
            Date = data['Date']
            Notes = data['Notes']
            WarehouseID = data['WarehouseID']
            TotalQty = data['TotalQty']
            GrandTotal = data['GrandTotal']

            VoucherType = "SS"

            # VoucherNo Updated
            try:
                PreFix = data['PreFix']
            except:
                PreFix = "SS"

            try:
                Seperator = data['Seperator']
            except:
                Seperator = ""

            try:
                InvoiceNo = data['InvoiceNo']
            except:
                InvoiceNo = 1

            Action = "A"

            if not ShortageStockMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherNo__iexact=VoucherNo).exists():
                update_voucher_table(CompanyID,CreatedUserID,VoucherType,PreFix,Seperator, InvoiceNo)
                ShortageStockMasterID = get_auto_shortageMasterID(
                    ShortageStockMaster, BranchID, CompanyID)

                ShortageStockMaster_Log.objects.create(
                    TransactionID=ShortageStockMasterID,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    Date=Date,
                    Notes=Notes,
                    WarehouseID=WarehouseID,
                    TotalQty=TotalQty,
                    GrandTotal=GrandTotal,
                    CreatedDate=today,
                    LastUPDDate=today,
                    CreatedUserID=CreatedUserID,
                    LastUPDUserID=CreatedUserID,
                )

                ShortageStockMaster.objects.create(
                    CompanyID=CompanyID,
                    ShortageStockMasterID=ShortageStockMasterID,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    Date=Date,
                    Notes=Notes,
                    WarehouseID=WarehouseID,
                    TotalQty=TotalQty,
                    GrandTotal=GrandTotal,
                    CreatedDate=today,
                    LastUPDDate=today,
                    CreatedUserID=CreatedUserID,
                    LastUPDUserID=CreatedUserID,
                )

                Details = data["Details"]

                VoucherType = "SS"

                for d in Details:
                    ProductID = d['ProductID']
                    Stock = d['Stock']
                    PriceListID = d['PriceListID']
                    ShortageStock = d['ShortageStock']
                    CostPerItem = d['CostPerItem']

                    ShortageStockDetailsID = get_auto_shortageDetailsID(
                        ShortageStockDetails, BranchID, CompanyID)

                    log_instance = ShortageStockDetails_Log.objects.create(
                        TransactionID=ShortageStockDetailsID,
                        BranchID=BranchID,
                        Action=Action,
                        ShortageStockMasterID=ShortageStockMasterID,
                        ProductID=ProductID,
                        Stock=Stock,
                        PriceListID=PriceListID,
                        ShortageStock=ShortageStock,
                        CreatedDate=today,
                        LastUPDDate=today,
                        CreatedUserID=CreatedUserID,
                        LastUPDUserID=CreatedUserID,
                        CostPerItem=CostPerItem,
                        CompanyID=CompanyID,
                    )

                    ShortageStockDetails.objects.create(
                        CompanyID=CompanyID,
                        ShortageStockDetailsID=ShortageStockDetailsID,
                        BranchID=BranchID,
                        Action=Action,
                        ShortageStockMasterID=ShortageStockMasterID,
                        ProductID=ProductID,
                        Stock=Stock,
                        PriceListID=PriceListID,
                        ShortageStock=ShortageStock,
                        CreatedDate=today,
                        LastUPDDate=today,
                        CreatedUserID=CreatedUserID,
                        LastUPDUserID=CreatedUserID,
                        CostPerItem=CostPerItem,
                        LogID=log_instance.ID
                    )

                    product_is_Service = Product.objects.get(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).is_Service
                    MultiFactor = PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).MultiFactor
                    PriceListID_DefUnit = PriceList.objects.get(
                        CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True, BranchID=BranchID).PriceListID

                    princeList_instance = PriceList.objects.get(
                        CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID_DefUnit, BranchID=BranchID)
                    PurchasePrice = princeList_instance.PurchasePrice
                    SalesPrice = princeList_instance.SalesPrice

                    # qty = float(FreeQty) + float(Qty)

                    Qty = float(MultiFactor) * float(ShortageStock)
                    Cost = float(CostPerItem) / float(MultiFactor)

                    StockPostingID = get_auto_stockPostid(
                        StockPosting, BranchID, CompanyID)

                    StockPosting.objects.create(
                        StockPostingID=StockPostingID,
                        BranchID=BranchID,
                        Action=Action,
                        Date=Date,
                        VoucherMasterID=ShortageStockMasterID,
                        VoucherDetailID=ShortageStockDetailsID,
                        VoucherType=VoucherType,
                        ProductID=ProductID,
                        WareHouseID=WarehouseID,
                        QtyOut=Qty,
                        Rate=Cost,
                        PriceListID=PriceListID,
                        IsActive=True,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                    )

                    StockPosting_Log.objects.create(
                        TransactionID=StockPostingID,
                        BranchID=BranchID,
                        Action=Action,
                        Date=Date,
                        VoucherMasterID=ShortageStockMasterID,
                        VoucherDetailID=ShortageStockDetailsID,
                        VoucherType=VoucherType,
                        ProductID=ProductID,
                        WareHouseID=WarehouseID,
                        QtyOut=Qty,
                        Rate=Cost,
                        PriceListID=PriceListID,
                        IsActive=True,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                    )

                    update_stock(CompanyID,BranchID,ProductID)

                    # if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Cost=CostPerItem, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID).exists():
                    #     stockRateInstance = StockRate.objects.get(
                    #         CompanyID=CompanyID, BranchID=BranchID, Cost=CostPerItem, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID)

                    #     StockRateID = stockRateInstance.StockRateID
                    #     stockRateInstance.Qty = float(
                    #         stockRateInstance.Qty) - float(ShortageStock)
                    #     stockRateInstance.save()

                    #     if StockTrans.objects.filter(StockRateID=StockRateID, DetailID=ShortageStockDetailsID, MasterID=ShortageStockMasterID, VoucherType=VoucherType, BranchID=BranchID, IsActive=True).exists():
                    #         stockTra_in = StockTrans.objects.filter(StockRateID=StockRateID, DetailID=ShortageStockDetailsID,
                    #                                                 MasterID=ShortageStockMasterID, VoucherType=VoucherType, BranchID=BranchID, IsActive=True).first()
                    #         stockTra_in.Qty = float(
                    #             stockTra_in.Qty) - float(ShortageStock)
                    #         stockTra_in.save()
                    #     else:
                    #         StockTransID = get_auto_StockTransID(
                    #             StockTrans, BranchID, CompanyID)
                    #         StockTrans.objects.create(
                    #             StockTransID=StockTransID,
                    #             BranchID=BranchID,
                    #             VoucherType=VoucherType,
                    #             StockRateID=StockRateID,
                    #             DetailID=ShortageStockDetailsID,
                    #             MasterID=ShortageStockMasterID,
                    #             Qty=ShortageStock,
                    #             IsActive=True,
                    #             CompanyID=CompanyID,
                    #         )

                    # else:
                    #     StockRateID = get_auto_StockRateID(
                    #         StockRate, BranchID, CompanyID)
                    #     StockRate.objects.create(
                    #         StockRateID=StockRateID,
                    #         BranchID=BranchID,
                    #         PurchasePrice=PurchasePrice,
                    #         SalesPrice=SalesPrice,
                    #         Qty=ShortageStock,
                    #         Cost=CostPerItem,
                    #         ProductID=ProductID,
                    #         WareHouseID=WarehouseID,
                    #         Date=Date,
                    #         PriceListID=PriceListID,
                    #         CreatedUserID=CreatedUserID,
                    #         CreatedDate=today,
                    #         UpdatedDate=today,
                    #         CompanyID=CompanyID,
                    #     )

                    #     StockTransID = get_auto_StockTransID(
                    #         StockTrans, BranchID, CompanyID)
                    #     StockTrans.objects.create(
                    #         StockTransID=StockTransID,
                    #         BranchID=BranchID,
                    #         VoucherType=VoucherType,
                    #         StockRateID=StockRateID,
                    #         DetailID=ShortageStockDetailsID,
                    #         MasterID=ShortageStockMasterID,
                    #         Qty=ShortageStock,
                    #         IsActive=True,
                    #         CompanyID=CompanyID,
                    #     )

                response_data = {
                    "StatusCode": 6000,
                    "message": "Shortage Stock Created Successfully!!!"
                }

                return Response(response_data, status=status.HTTP_200_OK)

            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "VoucherNo Already Exist.Please Change Your Prefix!"
                }

                return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again"
        }

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Shortage Stock',
                         'Create', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_shortageStock(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    try:
        page_number = data['page_no']
    except:
        page_number = ""

    try:
        items_per_page = data['items_per_page']
    except:
        items_per_page = ""

    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if ShortageStockMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            if page_number and items_per_page:
                instances = ShortageStockMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)
                count = len(instances)
                ledger_sort_pagination = list_pagination(
                    instances,
                    items_per_page,
                    page_number
                )
                print(ledger_sort_pagination)
                # serialized = WarehouseRestSerializer(ledger_sort_pagination, many=True)
                # data = serialized.data
            else:
                ledger_sort_pagination = ShortageStockMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)
                count = len(ledger_sort_pagination)
            serialized = ShortageStockMaster1Serializer(ledger_sort_pagination, many=True, context={"CompanyID": CompanyID,
                                                                                                   "PriceRounding": PriceRounding})
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "count": count
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Shortage Stock Not Found in this Branch!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_shortageStock(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    instance = None
    if ShortageStockMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = ShortageStockMaster.objects.get(CompanyID=CompanyID, pk=pk)
        ShortageStockMasterID = instance.ShortageStockMasterID
        BranchID = instance.BranchID
        Date = instance.Date
        VoucherNo = instance.VoucherNo
        Notes = instance.Notes
        WarehouseID = instance.WarehouseID
        TotalQty = instance.TotalQty
        GrandTotal = instance.GrandTotal
        Action = "D"

        instance.delete()
        ShortageStockMaster_Log.objects.create(
            TransactionID=ShortageStockMasterID,
            BranchID=BranchID,
            Action=Action,
            VoucherNo=VoucherNo,
            Date=Date,
            Notes=Notes,
            WarehouseID=WarehouseID,
            TotalQty=TotalQty,
            GrandTotal=GrandTotal,
            CreatedDate=today,
            LastUPDDate=today,
            CreatedUserID=CreatedUserID,
            LastUPDUserID=CreatedUserID,
        )

        if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=ShortageStockMasterID, BranchID=BranchID, VoucherType="SS").exists():

            stockPostingInstances = StockPosting.objects.filter(
                CompanyID=CompanyID, VoucherMasterID=ShortageStockMasterID, BranchID=BranchID, VoucherType="SS")

            for stockPostingInstance in stockPostingInstances:

                StockPostingID = stockPostingInstance.StockPostingID
                BranchID = stockPostingInstance.BranchID
                Date = stockPostingInstance.Date
                VoucherMasterID = stockPostingInstance.VoucherMasterID
                VoucherDetailID = stockPostingInstance.VoucherDetailID
                VoucherType = stockPostingInstance.VoucherType
                ProductID = stockPostingInstance.ProductID
                BatchID = stockPostingInstance.BatchID
                WareHouseID = stockPostingInstance.WareHouseID
                QtyIn = stockPostingInstance.QtyIn
                QtyOut = stockPostingInstance.QtyOut
                Rate = stockPostingInstance.Rate
                PriceListID = stockPostingInstance.PriceListID
                IsActive = stockPostingInstance.IsActive

                StockPosting_Log.objects.create(
                    TransactionID=StockPostingID,
                    BranchID=BranchID,
                    Action=Action,
                    Date=Date,
                    VoucherMasterID=ShortageStockMasterID,
                    VoucherDetailID=VoucherDetailID,
                    VoucherType=VoucherType,
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

                stockPostingInstance.delete()

                update_stock(CompanyID,BranchID,ProductID)

        detail_instances = ShortageStockDetails.objects.filter(
            CompanyID=CompanyID, ShortageStockMasterID=ShortageStockMasterID)

        for detail_instance in detail_instances:

            ShortageStockDetailsID = detail_instance.ShortageStockDetailsID
            BranchID = detail_instance.BranchID
            ShortageStockMasterID = detail_instance.ShortageStockMasterID
            ProductID = detail_instance.ProductID
            Stock = detail_instance.Stock
            PriceListID = detail_instance.PriceListID
            ShortageStock = detail_instance.ShortageStock
            CostPerItem = detail_instance.CostPerItem

            ShortageStockDetails_Log.objects.create(
                TransactionID=ShortageStockDetailsID,
                BranchID=BranchID,
                Action=Action,
                ShortageStockMasterID=ShortageStockMasterID,
                ProductID=ProductID,
                Stock=Stock,
                PriceListID=PriceListID,
                ShortageStock=ShortageStock,
                CreatedDate=today,
                LastUPDDate=today,
                CreatedUserID=CreatedUserID,
                LastUPDUserID=CreatedUserID,
                CostPerItem=CostPerItem,
                CompanyID=CompanyID,
            )

            update_stock(CompanyID,BranchID,ProductID)
            detail_instance.delete()

            # if StockTrans.objects.filter(CompanyID=CompanyID,DetailID=PurchaseDetailsID,MasterID=PurchaseMasterID,BranchID=BranchID,VoucherType="PI").exists():
            #     stockTrans_instance = StockTrans.objects.get(CompanyID=CompanyID,DetailID=PurchaseDetailsID,MasterID=PurchaseMasterID,BranchID=BranchID,VoucherType="PI")

            #     stockRateID = stockTrans_instance.StockRateID
            #     stockTrans_instance.IsActive = False
            #     stockTrans_instance.save()

            #     stockRate_instance = StockRate.objects.get(CompanyID=CompanyID,StockRateID=stockRateID,BranchID=BranchID)
            #     stockRate_instance.Qty = stockTrans_instance.Qty
            #     stockRate_instance.save()

            if StockTrans.objects.filter(CompanyID=CompanyID, DetailID=ShortageStockDetailsID, MasterID=ShortageStockMasterID, BranchID=BranchID, VoucherType="SS", IsActive=True).exists():
                stockTrans_instances = StockTrans.objects.filter(
                    CompanyID=CompanyID, DetailID=ShortageStockDetailsID, MasterID=ShortageStockMasterID, BranchID=BranchID, VoucherType="SS", IsActive=True)

                for i in stockTrans_instances:
                    stockRateID = i.StockRateID
                    i.IsActive = False
                    i.save()

                    stockRate_instance = StockRate.objects.get(
                        CompanyID=CompanyID, StockRateID=stockRateID, BranchID=BranchID)
                    stockRate_instance.Qty = i.Qty
                    stockRate_instance.save()
        response_data = {
            "StatusCode": 6000,
            "message": "Shortage Stock Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Shortage Stock Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def edit_shortageStock(request, pk):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            CreatedUserID = data['CreatedUserID']
            today = datetime.datetime.now()

            shortageStockMaster_instance = ShortageStockMaster.objects.get(
                pk=pk, CompanyID=CompanyID)
            ShortageStockMasterID = shortageStockMaster_instance.ShortageStockMasterID
            BranchID = shortageStockMaster_instance.BranchID

            VoucherType = "SS"

            VoucherNo = data['VoucherNo']
            Date = data['Date']
            Notes = data['Notes']
            WarehouseID = data['WarehouseID']
            TotalQty = data['TotalQty']
            GrandTotal = data['GrandTotal']

            Action = "M"

            ShortageStockMaster_Log.objects.create(
                TransactionID=ShortageStockMasterID,
                BranchID=BranchID,
                Action=Action,
                VoucherNo=VoucherNo,
                Date=Date,
                Notes=Notes,
                WarehouseID=WarehouseID,
                TotalQty=TotalQty,
                GrandTotal=GrandTotal,
                CreatedDate=today,
                LastUPDDate=today,
                CreatedUserID=CreatedUserID,
                LastUPDUserID=CreatedUserID,
            )

            # if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=ShortageStockMasterID, BranchID=BranchID, VoucherType=VoucherType).exists():
            #     stockPostingInstances = StockPosting.objects.filter(
            #         CompanyID=CompanyID, VoucherMasterID=ShortageStockMasterID, BranchID=BranchID, VoucherType=VoucherType)
            #     for stockPostingInstance in stockPostingInstances:
            #         stockPostingInstance.delete()

            if ShortageStockDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ShortageStockMasterID=ShortageStockMasterID).exists():
                shortageStockInstances = ShortageStockDetails.objects.filter(
                    CompanyID=CompanyID, ShortageStockMasterID=ShortageStockMasterID, BranchID=BranchID)
                for i in shortageStockInstances:
                    if not StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=ShortageStockMasterID,VoucherDetailID=i.ShortageStockDetailsID,BranchID=BranchID, VoucherType="SS").exists():
                        StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=ShortageStockMasterID,BranchID=BranchID, VoucherType="SS").delete()
                        update_stock(CompanyID,BranchID,i.ProductID)

                    instance_MultiFactor = PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=i.PriceListID, BranchID=BranchID).MultiFactor

                    instance_qty_sum = float(i.ShortageStock)
                    instance_Qty = float(instance_MultiFactor) * float(instance_qty_sum)
                    if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=ShortageStockMasterID,VoucherDetailID=i.ShortageStockDetailsID,ProductID=i.ProductID,BranchID=BranchID, VoucherType="SS").exists():
                        stock_inst = StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=ShortageStockMasterID,VoucherDetailID=i.ShortageStockDetailsID,ProductID=i.ProductID,BranchID=BranchID, VoucherType="SS").first()
                        stock_inst.QtyOut = float(stock_inst.QtyOut) - float(instance_Qty)
                        stock_inst.save()
                        update_stock(CompanyID,BranchID,i.ProductID)

            # if ShortageStockDetails.objects.filter(ShortageStockMasterID=ShortageStockMasterID, BranchID=BranchID, CompanyID=CompanyID).exists():
            #     shortageStockDetails_instances = ShortageStockDetails.objects.filter(
            #         ShortageStockMasterID=ShortageStockMasterID, BranchID=BranchID, CompanyID=CompanyID)
            #     for detail in shortageStockDetails_instances:
            #         detail.delete()

            # if StockTrans.objects.filter(CompanyID=CompanyID, VoucherType=VoucherType, MasterID=ShortageStockMasterID, BranchID=BranchID, IsActive=True).exists():
            #     trans_ins = StockTrans.objects.filter(
            #         CompanyID=CompanyID, VoucherType=VoucherType, MasterID=ShortageStockMasterID, BranchID=BranchID, IsActive=True)
            #     for stk in trans_ins:
            #         StockRateID = stk.StockRateID
            #         stockQty = stk.Qty

            #         rate_ins = StockRate.objects.filter(
            #             CompanyID=CompanyID, StockRateID=StockRateID, BranchID=BranchID).first()
            #         rate_ins.Qty = float(rate_ins.Qty) + float(stockQty)
            #         rate_ins.save()
            #         stk.IsActive = False
            #         stk.save()

            shortageStockMaster_instance.Date = Date
            shortageStockMaster_instance.Notes = Notes
            shortageStockMaster_instance.WarehouseID = WarehouseID
            shortageStockMaster_instance.TotalQty = TotalQty
            shortageStockMaster_instance.GrandTotal = GrandTotal
            shortageStockMaster_instance.Action = Action
            shortageStockMaster_instance.LastUPDDate = today
            shortageStockMaster_instance.LastUPDUserID = CreatedUserID

            shortageStockMaster_instance.save()

            Details = data["Details"]

            for d in Details:
                if d['id']:
                    pk = d['id']
                ProductID = d['ProductID']
                Stock = d['Stock']
                PriceListID = d['PriceListID']
                ShortageStock = d['ShortageStock']
                CostPerItem = d['CostPerItem']
                detailID = d['detailID']

                product_is_Service = Product.objects.get(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).is_Service
                MultiFactor = PriceList.objects.get(
                    CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).MultiFactor
                PriceListID_DefUnit = PriceList.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True, BranchID=BranchID).PriceListID

                princeList_instance = PriceList.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID_DefUnit, BranchID=BranchID)
                PurchasePrice = princeList_instance.PurchasePrice
                SalesPrice = princeList_instance.SalesPrice

                # qty = float(FreeQty) + float(Qty)

                Qty = float(MultiFactor) * float(ShortageStock)
                Cost = float(CostPerItem) / float(MultiFactor)

                if detailID == 0:
                    shortageStockDetail_instance = ShortageStockDetails.objects.get(
                        CompanyID=CompanyID, pk=pk)
                    ShortageStockDetailsID = shortageStockDetail_instance.ShortageStockDetailsID

                    log_instance = ShortageStockDetails_Log.objects.create(
                        TransactionID=ShortageStockDetailsID,
                        BranchID=BranchID,
                        Action=Action,
                        ShortageStockMasterID=ShortageStockMasterID,
                        ProductID=ProductID,
                        Stock=Stock,
                        PriceListID=PriceListID,
                        ShortageStock=ShortageStock,
                        CreatedDate=today,
                        LastUPDDate=today,
                        CreatedUserID=CreatedUserID,
                        LastUPDUserID=CreatedUserID,
                        CostPerItem=CostPerItem,
                        CompanyID=CompanyID,
                    )

                    shortageStockDetail_instance.ProductID = ProductID
                    shortageStockDetail_instance.Stock = Stock
                    shortageStockDetail_instance.PriceListID = PriceListID
                    shortageStockDetail_instance.CostPerItem = CostPerItem
                    shortageStockDetail_instance.ShortageStock = ShortageStock
                    shortageStockDetail_instance.Action = Action
                    shortageStockDetail_instance.LastUPDDate = today
                    shortageStockDetail_instance.save()

                    if product_is_Service == False:
                        if StockPosting.objects.filter(CompanyID=CompanyID,WareHouseID=WarehouseID, VoucherMasterID=ShortageStockMasterID,VoucherDetailID=ShortageStockDetailsID,BranchID=BranchID, VoucherType="SS",ProductID=ProductID).exists():
                            stock_instance = StockPosting.objects.filter(CompanyID=CompanyID,WareHouseID=WarehouseID, VoucherMasterID=ShortageStockMasterID,VoucherDetailID=ShortageStockDetailsID,BranchID=BranchID, VoucherType="SS",ProductID=ProductID).first()
                            stock_instance.QtyOut = Qty
                            stock_instance.Action = Action
                            stock_instance.UpdatedDate = today
                            stock_instance.save()
                            update_stock(CompanyID,BranchID,ProductID)
                        else:
                            StockPostingID = get_auto_stockPostid(
                                StockPosting, BranchID, CompanyID)
                            StockPosting.objects.create(
                                StockPostingID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=Date,
                                VoucherMasterID=ShortageStockMasterID,
                                VoucherDetailID=ShortageStockDetailsID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                WareHouseID=WarehouseID,
                                QtyOut=Qty,
                                Rate=Cost,
                                PriceListID=PriceListID_DefUnit,
                                IsActive=IsActive,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                            )

                            StockPosting_Log.objects.create(
                                TransactionID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=Date,
                                VoucherMasterID=ShortageStockMasterID,
                                VoucherDetailID=ShortageStockDetailsID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                WareHouseID=WarehouseID,
                                QtyOut=Qty,
                                Rate=Cost,
                                PriceListID=PriceListID_DefUnit,
                                IsActive=IsActive,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                            )

                            update_stock(CompanyID,BranchID,ProductID)


                if detailID == 1:
                    Action = "A"
                    ShortageStockDetailsID = get_auto_shortageDetailsID(
                        ShortageStockDetails, BranchID, CompanyID)

                    log_instance = ShortageStockDetails_Log.objects.create(
                        TransactionID=ShortageStockDetailsID,
                        BranchID=BranchID,
                        Action=Action,
                        ShortageStockMasterID=ShortageStockMasterID,
                        ProductID=ProductID,
                        Stock=Stock,
                        PriceListID=PriceListID,
                        ShortageStock=ShortageStock,
                        CreatedDate=today,
                        LastUPDDate=today,
                        CreatedUserID=CreatedUserID,
                        LastUPDUserID=CreatedUserID,
                        CostPerItem=CostPerItem,
                        CompanyID=CompanyID,
                    )

                    ShortageStockDetails.objects.create(
                        CompanyID=CompanyID,
                        ShortageStockDetailsID=ShortageStockDetailsID,
                        BranchID=BranchID,
                        Action=Action,
                        ShortageStockMasterID=ShortageStockMasterID,
                        ProductID=ProductID,
                        Stock=Stock,
                        PriceListID=PriceListID,
                        ShortageStock=ShortageStock,
                        CreatedDate=today,
                        LastUPDDate=today,
                        CreatedUserID=CreatedUserID,
                        LastUPDUserID=CreatedUserID,
                        CostPerItem=CostPerItem,
                        LogID=log_instance.ID
                    )

                    if product_is_Service == False:
                        StockPostingID = get_auto_stockPostid(
                            StockPosting, BranchID, CompanyID)
                        StockPosting.objects.create(
                            StockPostingID=StockPostingID,
                            BranchID=BranchID,
                            Action=Action,
                            Date=Date,
                            VoucherMasterID=ShortageStockMasterID,
                            VoucherDetailID=ShortageStockDetailsID,
                            VoucherType=VoucherType,
                            ProductID=ProductID,
                            WareHouseID=WarehouseID,
                            QtyOut=Qty,
                            Rate=Cost,
                            PriceListID=PriceListID_DefUnit,
                            IsActive=True,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )

                        StockPosting_Log.objects.create(
                            TransactionID=StockPostingID,
                            BranchID=BranchID,
                            Action=Action,
                            Date=Date,
                            VoucherMasterID=ShortageStockMasterID,
                            VoucherDetailID=ShortageStockDetailsID,
                            VoucherType=VoucherType,
                            ProductID=ProductID,
                            WareHouseID=WarehouseID,
                            QtyOut=Qty,
                            Rate=Cost,
                            PriceListID=PriceListID_DefUnit,
                            IsActive=True,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )

                        update_stock(CompanyID,BranchID,ProductID)

            deleted_datas = data["deleted_data"]
            if deleted_datas:
                for deleted_Data in deleted_datas:
                    deleted_pk = deleted_Data['unq_id']
                    ShortageStockDetailID_Deleted = deleted_Data['ShortageStockDetailID']
                    ProductID_Deleted = deleted_Data['ProductID']
                    PriceListID_Deleted = deleted_Data['PriceListID']
                    Rate_Deleted = deleted_Data['Rate']
                    ShortageStockMasterID_Deleted = deleted_Data['ShortageStockMasterID']
                    WarehouseID_Deleted = deleted_Data['WarehouseID']

                    if not deleted_pk == '' or not deleted_pk == 0:
                        if ShortageStockDetails.objects.filter(CompanyID=CompanyID,pk=deleted_pk).exists():
                            deleted_detail = ShortageStockDetails.objects.filter(CompanyID=CompanyID,pk=deleted_pk)
                            deleted_detail.delete()

                            if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=ShortageStockMasterID_Deleted,VoucherDetailID=ShortageStockDetailID_Deleted,ProductID=ProductID_Deleted,BranchID=BranchID, VoucherType="SS").exists():
                                stock_instances_delete = StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=ShortageStockMasterID_Deleted,VoucherDetailID=ShortageStockDetailID_Deleted,ProductID=ProductID_Deleted,BranchID=BranchID, VoucherType="SS")
                                stock_instances_delete.delete()

                                update_stock(CompanyID,BranchID,ProductID_Deleted)

            # deleted_ids = data["deleted_ids"]
            # for d in deleted_ids:
            #     update_stock(CompanyID,BranchID,d)

                # if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Cost=CostPerItem, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID).exists():
                #     stockRateInstance = StockRate.objects.get(
                #         CompanyID=CompanyID, BranchID=BranchID, Cost=CostPerItem, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID)

                #     StockRateID = stockRateInstance.StockRateID
                #     stockRateInstance.Qty = float(
                #         stockRateInstance.Qty) + float(ShortageStock)
                #     stockRateInstance.save()

                #     if StockTrans.objects.filter(StockRateID=StockRateID, DetailID=ShortageStockDetailsID, MasterID=ShortageStockMasterID, VoucherType=VoucherType, BranchID=BranchID, IsActive=True).exists():
                #         stockTra_in = StockTrans.objects.filter(StockRateID=StockRateID, DetailID=ShortageStockDetailsID,
                #                                                 MasterID=ShortageStockMasterID, VoucherType=VoucherType, BranchID=BranchID, IsActive=True).first()
                #         stockTra_in.Qty = float(stockTra_in.Qty) + float(ShortageStock)
                #         stockTra_in.save()
                #     else:
                #         StockTransID = get_auto_StockTransID(
                #             StockTrans, BranchID, CompanyID)
                #         StockTrans.objects.create(
                #             StockTransID=StockTransID,
                #             BranchID=BranchID,
                #             VoucherType=VoucherType,
                #             StockRateID=StockRateID,
                #             DetailID=ShortageStockDetailsID,
                #             MasterID=ShortageStockMasterID,
                #             Qty=ShortageStock,
                #             IsActive=True,
                #             CompanyID=CompanyID,
                #         )

                # else:
                #     StockRateID = get_auto_StockRateID(StockRate, BranchID, CompanyID)
                #     StockRate.objects.create(
                #         StockRateID=StockRateID,
                #         BranchID=BranchID,
                #         PurchasePrice=PurchasePrice,
                #         SalesPrice=SalesPrice,
                #         Qty=ShortageStock,
                #         Cost=CostPerItem,
                #         ProductID=ProductID,
                #         WareHouseID=WarehouseID,
                #         Date=Date,
                #         PriceListID=PriceListID,
                #         CreatedUserID=CreatedUserID,
                #         CreatedDate=today,
                #         UpdatedDate=today,
                #         CompanyID=CompanyID,
                #     )

                #     StockTransID = get_auto_StockTransID(
                #         StockTrans, BranchID, CompanyID)
                #     StockTrans.objects.create(
                #         StockTransID=StockTransID,
                #         BranchID=BranchID,
                #         VoucherType=VoucherType,
                #         StockRateID=StockRateID,
                #         DetailID=ShortageStockDetailsID,
                #         MasterID=ShortageStockMasterID,
                #         Qty=ShortageStock,
                #         IsActive=True,
                #         CompanyID=CompanyID,
                #     )
            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'ShortageStock',
            #              'Edit', 'ShortageStock Updated successfully.', 'ShortageStock Updated successfully.')

            response_data = {
                "StatusCode": 6000,
                "message": "Shortage Stock Updated Successfully!!!",
            }

            return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again"
        }

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Shortage Stock',
                         'Edit', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def shortageStock(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if ShortageStockMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
            instance = ShortageStockMaster.objects.get(
                CompanyID=CompanyID, pk=pk)
            serialized = ShortageStockMasterSerializer(instance, context={"CompanyID": CompanyID,
                                                                          "PriceRounding": PriceRounding})
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Shortage Stock Not Found in this Branch!"
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
@transaction.atomic
def create_damage_stock(request):
    try:
        with transaction.atomic():
            today = datetime.datetime.now()

            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)

            CreatedUserID = data['CreatedUserID']
            BranchID = data['BranchID']
            VoucherNo = data['VoucherNo']
            Date = data['Date']
            Notes = data['Notes']
            WarehouseID = data['WarehouseID']
            TotalQty = data['TotalQty']
            GrandTotal = data['GrandTotal']

            VoucherType = "DS"

            # VoucherNo Updated
            try:
                PreFix = data['PreFix']
            except:
                PreFix = "DS"

            try:
                Seperator = data['Seperator']
            except:
                Seperator = ""

            try:
                InvoiceNo = data['InvoiceNo']
            except:
                InvoiceNo = 1

            Action = "A"

            if not DamageStockMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherNo__iexact=VoucherNo).exists():
                update_voucher_table(CompanyID,CreatedUserID,VoucherType,PreFix,Seperator, InvoiceNo)
                DamageStockMasterID = get_auto_damageMasterID(
                    DamageStockMaster, BranchID, CompanyID)

                DamageStockMaster_Log.objects.create(
                    TransactionID=DamageStockMasterID,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    Date=Date,
                    Notes=Notes,
                    WarehouseID=WarehouseID,
                    TotalQty=TotalQty,
                    GrandTotal=GrandTotal,
                    CreatedDate=today,
                    LastUPDDate=today,
                    CreatedUserID=CreatedUserID,
                    LastUPDUserID=CreatedUserID,
                )

                DamageStockMaster.objects.create(
                    CompanyID=CompanyID,
                    DamageStockMasterID=DamageStockMasterID,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    Date=Date,
                    Notes=Notes,
                    WarehouseID=WarehouseID,
                    TotalQty=TotalQty,
                    GrandTotal=GrandTotal,
                    CreatedDate=today,
                    LastUPDDate=today,
                    CreatedUserID=CreatedUserID,
                    LastUPDUserID=CreatedUserID,

                )

                Details = data["Details"]

                VoucherType = "DS"

                for d in Details:
                    ProductID = d['ProductID']
                    Stock = d['Stock']
                    PriceListID = d['PriceListID']
                    DamageStock = d['DamageStock']
                    CostPerItem = d['CostPerItem']

                    DamageStockDetailsID = get_auto_damageDetailsID(
                        DamageStockDetails, BranchID, CompanyID)

                    log_instance = DamageStockDetails_Log.objects.create(
                        TransactionID=DamageStockDetailsID,
                        BranchID=BranchID,
                        Action=Action,
                        DamageStockMasterID=DamageStockMasterID,
                        ProductID=ProductID,
                        Stock=Stock,
                        PriceListID=PriceListID,
                        DamageStock=DamageStock,
                        CreatedDate=today,
                        LastUPDDate=today,
                        CreatedUserID=CreatedUserID,
                        LastUPDUserID=CreatedUserID,
                        CostPerItem=CostPerItem,
                        CompanyID=CompanyID,
                    )

                    DamageStockDetails.objects.create(
                        CompanyID=CompanyID,
                        DamageStockDetailsID=DamageStockDetailsID,
                        BranchID=BranchID,
                        Action=Action,
                        DamageStockMasterID=DamageStockMasterID,
                        ProductID=ProductID,
                        Stock=Stock,
                        PriceListID=PriceListID,
                        DamageStock=DamageStock,
                        CreatedDate=today,
                        LastUPDDate=today,
                        CreatedUserID=CreatedUserID,
                        LastUPDUserID=CreatedUserID,
                        CostPerItem=CostPerItem,
                        LogID=log_instance.ID
                    )

                    product_is_Service = Product.objects.get(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).is_Service
                    MultiFactor = PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).MultiFactor
                    PriceListID_DefUnit = PriceList.objects.get(
                        CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True, BranchID=BranchID).PriceListID

                    princeList_instance = PriceList.objects.get(
                        CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID_DefUnit, BranchID=BranchID)
                    PurchasePrice = princeList_instance.PurchasePrice
                    SalesPrice = princeList_instance.SalesPrice

                    # qty = float(FreeQty) + float(Qty)

                    Qty = float(MultiFactor) * float(DamageStock)
                    Cost = float(CostPerItem) / float(MultiFactor)

                    StockPostingID = get_auto_stockPostid(
                        StockPosting, BranchID, CompanyID)

                    StockPosting.objects.create(
                        StockPostingID=StockPostingID,
                        BranchID=BranchID,
                        Action=Action,
                        Date=Date,
                        VoucherMasterID=DamageStockMasterID,
                        VoucherDetailID=DamageStockDetailsID,
                        VoucherType=VoucherType,
                        ProductID=ProductID,
                        WareHouseID=WarehouseID,
                        QtyOut=Qty,
                        Rate=Cost,
                        PriceListID=PriceListID,
                        IsActive=True,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                    )

                    StockPosting_Log.objects.create(
                        TransactionID=StockPostingID,
                        BranchID=BranchID,
                        Action=Action,
                        Date=Date,
                        VoucherMasterID=DamageStockMasterID,
                        VoucherDetailID=DamageStockDetailsID,
                        VoucherType=VoucherType,
                        ProductID=ProductID,
                        WareHouseID=WarehouseID,
                        QtyOut=Qty,
                        Rate=Cost,
                        PriceListID=PriceListID,
                        IsActive=True,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                    )

                    update_stock(CompanyID,BranchID,ProductID)


                    # if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Cost=CostPerItem, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID).exists():
                    #     stockRateInstance = StockRate.objects.get(
                    #         CompanyID=CompanyID, BranchID=BranchID, Cost=CostPerItem, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID)

                    #     StockRateID = stockRateInstance.StockRateID
                    #     stockRateInstance.Qty = float(
                    #         stockRateInstance.Qty) - float(DamageStock)
                    #     stockRateInstance.save()

                    #     if StockTrans.objects.filter(StockRateID=StockRateID, DetailID=DamageStockDetailsID, MasterID=DamageStockMasterID, VoucherType=VoucherType, BranchID=BranchID, IsActive=True).exists():
                    #         stockTra_in = StockTrans.objects.filter(StockRateID=StockRateID, DetailID=DamageStockDetailsID,
                    #                                                 MasterID=DamageStockMasterID, VoucherType=VoucherType, BranchID=BranchID, IsActive=True).first()
                    #         stockTra_in.Qty = float(
                    #             stockTra_in.Qty) - float(DamageStock)
                    #         stockTra_in.save()
                    #     else:
                    #         StockTransID = get_auto_StockTransID(
                    #             StockTrans, BranchID, CompanyID)
                    #         StockTrans.objects.create(
                    #             StockTransID=StockTransID,
                    #             BranchID=BranchID,
                    #             VoucherType=VoucherType,
                    #             StockRateID=StockRateID,
                    #             DetailID=DamageStockDetailsID,
                    #             MasterID=DamageStockMasterID,
                    #             Qty=DamageStock,
                    #             IsActive=True,
                    #             CompanyID=CompanyID,
                    #         )

                    # else:
                    #     StockRateID = get_auto_StockRateID(
                    #         StockRate, BranchID, CompanyID)
                    #     StockRate.objects.create(
                    #         StockRateID=StockRateID,
                    #         BranchID=BranchID,
                    #         PurchasePrice=PurchasePrice,
                    #         SalesPrice=SalesPrice,
                    #         Qty=DamageStock,
                    #         Cost=CostPerItem,
                    #         ProductID=ProductID,
                    #         WareHouseID=WarehouseID,
                    #         Date=Date,
                    #         PriceListID=PriceListID,
                    #         CreatedUserID=CreatedUserID,
                    #         CreatedDate=today,
                    #         UpdatedDate=today,
                    #         CompanyID=CompanyID,
                    #     )

                    #     StockTransID = get_auto_StockTransID(
                    #         StockTrans, BranchID, CompanyID)
                    #     StockTrans.objects.create(
                    #         StockTransID=StockTransID,
                    #         BranchID=BranchID,
                    #         VoucherType=VoucherType,
                    #         StockRateID=StockRateID,
                    #         DetailID=DamageStockDetailsID,
                    #         MasterID=DamageStockMasterID,
                    #         Qty=DamageStock,
                    #         IsActive=True,
                    #         CompanyID=CompanyID,
                    #     )

                response_data = {
                    "StatusCode": 6000,
                    "message": "Damage Stock Created Successfully!!!"
                }

                return Response(response_data, status=status.HTTP_200_OK)

            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "VoucherNo Already Exist.Please Change Your Prefix!"
                }

                return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again"
        }

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Damage Stock',
                         'Create', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_damageStock(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']

    try:
        page_number = data['page_no']
    except:
        page_number = ""

    try:
        items_per_page = data['items_per_page']
    except:
        items_per_page = ""

    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if DamageStockMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            if page_number and items_per_page:
                instances = DamageStockMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)
                count = len(instances)
                ledger_sort_pagination = list_pagination(
                    instances,
                    items_per_page,
                    page_number
                )
                print(ledger_sort_pagination)
                # serialized = WarehouseRestSerializer(ledger_sort_pagination, many=True)
                # data = serialized.data
            else:
                ledger_sort_pagination = DamageStockMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)
                count = len(ledger_sort_pagination)
            serialized = DamageStockMaster1Serializer(ledger_sort_pagination, many=True, context={"CompanyID": CompanyID,
                                                                                                 "PriceRounding": PriceRounding})
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "count": count
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Damage Stock Not Found in this Branch!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_damageStock(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    instance = None
    if DamageStockMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = DamageStockMaster.objects.get(CompanyID=CompanyID, pk=pk)
        DamageStockMasterID = instance.DamageStockMasterID
        BranchID = instance.BranchID
        Date = instance.Date
        VoucherNo = instance.VoucherNo
        Notes = instance.Notes
        WarehouseID = instance.WarehouseID
        TotalQty = instance.TotalQty
        GrandTotal = instance.GrandTotal
        Action = "D"

        instance.delete()
        DamageStockMaster_Log.objects.create(
            TransactionID=DamageStockMasterID,
            BranchID=BranchID,
            Action=Action,
            VoucherNo=VoucherNo,
            Date=Date,
            Notes=Notes,
            WarehouseID=WarehouseID,
            TotalQty=TotalQty,
            GrandTotal=GrandTotal,
            CreatedDate=today,
            LastUPDDate=today,
            CreatedUserID=CreatedUserID,
            LastUPDUserID=CreatedUserID,
        )

        if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=DamageStockMasterID, BranchID=BranchID, VoucherType="DS").exists():

            stockPostingInstances = StockPosting.objects.filter(
                CompanyID=CompanyID, VoucherMasterID=DamageStockMasterID, BranchID=BranchID, VoucherType="DS")

            for stockPostingInstance in stockPostingInstances:

                StockPostingID = stockPostingInstance.StockPostingID
                BranchID = stockPostingInstance.BranchID
                Date = stockPostingInstance.Date
                VoucherMasterID = stockPostingInstance.VoucherMasterID
                VoucherDetailID = stockPostingInstance.VoucherDetailID
                VoucherType = stockPostingInstance.VoucherType
                ProductID = stockPostingInstance.ProductID
                BatchID = stockPostingInstance.BatchID
                WareHouseID = stockPostingInstance.WareHouseID
                QtyIn = stockPostingInstance.QtyIn
                QtyOut = stockPostingInstance.QtyOut
                Rate = stockPostingInstance.Rate
                PriceListID = stockPostingInstance.PriceListID
                IsActive = stockPostingInstance.IsActive

                StockPosting_Log.objects.create(
                    TransactionID=StockPostingID,
                    BranchID=BranchID,
                    Action=Action,
                    Date=Date,
                    VoucherMasterID=DamageStockMasterID,
                    VoucherDetailID=VoucherDetailID,
                    VoucherType=VoucherType,
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

                stockPostingInstance.delete()

                update_stock(CompanyID,BranchID,ProductID)

        detail_instances = DamageStockDetails.objects.filter(
            CompanyID=CompanyID, DamageStockMasterID=DamageStockMasterID)

        for detail_instance in detail_instances:

            DamageStockDetailsID = detail_instance.DamageStockDetailsID
            BranchID = detail_instance.BranchID
            DamageStockMasterID = detail_instance.DamageStockMasterID
            ProductID = detail_instance.ProductID
            Stock = detail_instance.Stock
            PriceListID = detail_instance.PriceListID
            DamageStock = detail_instance.DamageStock
            CostPerItem = detail_instance.CostPerItem

            DamageStockDetails_Log.objects.create(
                TransactionID=DamageStockDetailsID,
                BranchID=BranchID,
                Action=Action,
                DamageStockMasterID=DamageStockMasterID,
                ProductID=ProductID,
                Stock=Stock,
                PriceListID=PriceListID,
                DamageStock=DamageStock,
                CreatedDate=today,
                LastUPDDate=today,
                CreatedUserID=CreatedUserID,
                LastUPDUserID=CreatedUserID,
                CostPerItem=CostPerItem,
                CompanyID=CompanyID,
            )

            update_stock(CompanyID,BranchID,ProductID)

            detail_instance.delete()

            # if StockTrans.objects.filter(CompanyID=CompanyID,DetailID=PurchaseDetailsID,MasterID=PurchaseMasterID,BranchID=BranchID,VoucherType="PI").exists():
            #     stockTrans_instance = StockTrans.objects.get(CompanyID=CompanyID,DetailID=PurchaseDetailsID,MasterID=PurchaseMasterID,BranchID=BranchID,VoucherType="PI")

            #     stockRateID = stockTrans_instance.StockRateID
            #     stockTrans_instance.IsActive = False
            #     stockTrans_instance.save()

            #     stockRate_instance = StockRate.objects.get(CompanyID=CompanyID,StockRateID=stockRateID,BranchID=BranchID)
            #     stockRate_instance.Qty = stockTrans_instance.Qty
            #     stockRate_instance.save()

            if StockTrans.objects.filter(CompanyID=CompanyID, DetailID=DamageStockDetailsID, MasterID=DamageStockMasterID, BranchID=BranchID, VoucherType="DS", IsActive=True).exists():
                stockTrans_instances = StockTrans.objects.filter(
                    CompanyID=CompanyID, DetailID=DamageStockDetailsID, MasterID=DamageStockMasterID, BranchID=BranchID, VoucherType="DS", IsActive=True)

                for i in stockTrans_instances:
                    stockRateID = i.StockRateID
                    i.IsActive = False
                    i.save()

                    stockRate_instance = StockRate.objects.get(
                        CompanyID=CompanyID, StockRateID=stockRateID, BranchID=BranchID)
                    stockRate_instance.Qty = i.Qty
                    stockRate_instance.save()
        response_data = {
            "StatusCode": 6000,
            "message": "Damage Stock Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Damage Stock Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def edit_damageStock(request, pk):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            CreatedUserID = data['CreatedUserID']
            today = datetime.datetime.now()

            damageStockMaster_instance = DamageStockMaster.objects.get(
                pk=pk, CompanyID=CompanyID)
            DamageStockMasterID = damageStockMaster_instance.DamageStockMasterID
            BranchID = damageStockMaster_instance.BranchID

            VoucherType = "DS"

            VoucherNo = data['VoucherNo']
            Date = data['Date']
            Notes = data['Notes']
            WarehouseID = data['WarehouseID']
            TotalQty = data['TotalQty']
            GrandTotal = data['GrandTotal']

            Action = "M"
            DamageStockMaster_Log.objects.create(
                TransactionID=DamageStockMasterID,
                BranchID=BranchID,
                Action=Action,
                VoucherNo=VoucherNo,
                Date=Date,
                Notes=Notes,
                WarehouseID=WarehouseID,
                TotalQty=TotalQty,
                GrandTotal=GrandTotal,
                CreatedDate=today,
                LastUPDDate=today,
                CreatedUserID=CreatedUserID,
                LastUPDUserID=CreatedUserID,
            )

            # if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=DamageStockMasterID, BranchID=BranchID, VoucherType=VoucherType).exists():
            #     stockPostingInstances = StockPosting.objects.filter(
            #         CompanyID=CompanyID, VoucherMasterID=DamageStockMasterID, BranchID=BranchID, VoucherType=VoucherType)
            #     for stockPostingInstance in stockPostingInstances:
            #         stockPostingInstance.delete()

            if DamageStockDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, DamageStockMasterID=DamageStockMasterID).exists():
                damageStockInstances = DamageStockDetails.objects.filter(
                    CompanyID=CompanyID, DamageStockMasterID=DamageStockMasterID, BranchID=BranchID)
                for i in damageStockInstances:
                    if not StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=DamageStockMasterID,VoucherDetailID=i.DamageStockDetailsID,BranchID=BranchID, VoucherType="DS").exists():
                        StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=DamageStockMasterID,BranchID=BranchID, VoucherType="DS").delete()
                        update_stock(CompanyID,BranchID,i.ProductID)
                    instance_MultiFactor = PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=i.PriceListID, BranchID=BranchID).MultiFactor

                    instance_qty_sum = float(i.DamageStock)
                    instance_Qty = float(instance_MultiFactor) * float(instance_qty_sum)
                    if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=DamageStockMasterID,VoucherDetailID=i.DamageStockDetailsID,ProductID=i.ProductID,BranchID=BranchID, VoucherType="DS").exists():
                        stock_inst = StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=DamageStockMasterID,VoucherDetailID=i.DamageStockDetailsID,ProductID=i.ProductID,BranchID=BranchID, VoucherType="DS").first()
                        stock_inst.QtyOut = float(stock_inst.QtyOut) - float(instance_Qty)
                        stock_inst.save()
                        update_stock(CompanyID,BranchID,i.ProductID)

            # if DamageStockDetails.objects.filter(DamageStockMasterID=DamageStockMasterID, BranchID=BranchID, CompanyID=CompanyID).exists():
            #     damageStockDetails_instances = DamageStockDetails.objects.filter(
            #         DamageStockMasterID=DamageStockMasterID, BranchID=BranchID, CompanyID=CompanyID)
            #     for detail in damageStockDetails_instances:
            #         detail.delete()

            # if StockTrans.objects.filter(CompanyID=CompanyID, VoucherType=VoucherType, MasterID=DamageStockMasterID, BranchID=BranchID, IsActive=True).exists():
            #     trans_ins = StockTrans.objects.filter(
            #         CompanyID=CompanyID, VoucherType=VoucherType, MasterID=DamageStockMasterID, BranchID=BranchID, IsActive=True)
            #     for stk in trans_ins:
            #         StockRateID = stk.StockRateID
            #         stockQty = stk.Qty

            #         rate_ins = StockRate.objects.filter(
            #             CompanyID=CompanyID, StockRateID=StockRateID, BranchID=BranchID).first()
            #         rate_ins.Qty = float(rate_ins.Qty) + float(stockQty)
            #         rate_ins.save()
            #         stk.IsActive = False
            #         stk.save()

            damageStockMaster_instance.Date = Date
            damageStockMaster_instance.Notes = Notes
            damageStockMaster_instance.WarehouseID = WarehouseID
            damageStockMaster_instance.TotalQty = TotalQty
            damageStockMaster_instance.GrandTotal = GrandTotal
            damageStockMaster_instance.Action = Action
            damageStockMaster_instance.LastUPDDate = today
            damageStockMaster_instance.LastUPDUserID = CreatedUserID

            damageStockMaster_instance.save()

            Details = data["Details"]

            for d in Details:
                if d['id']:
                    pk = d['id']
                ProductID = d['ProductID']
                Stock = d['Stock']
                PriceListID = d['PriceListID']
                DamageStock = d['DamageStock']
                CostPerItem = d['CostPerItem']
                detailID = d['detailID']

                product_is_Service = Product.objects.get(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).is_Service
                MultiFactor = PriceList.objects.get(
                    CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).MultiFactor
                PriceListID_DefUnit = PriceList.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True, BranchID=BranchID).PriceListID

                princeList_instance = PriceList.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID_DefUnit, BranchID=BranchID)
                PurchasePrice = princeList_instance.PurchasePrice
                SalesPrice = princeList_instance.SalesPrice

                # qty = float(FreeQty) + float(Qty)

                Qty = float(MultiFactor) * float(DamageStock)
                Cost = float(CostPerItem) / float(MultiFactor)

                if detailID == 0:
                    damageStockDetail_instance = DamageStockDetails.objects.get(
                        CompanyID=CompanyID, pk=pk)
                    DamageStockDetailsID = damageStockDetail_instance.DamageStockDetailsID

                    log_instance = DamageStockDetails_Log.objects.create(
                        TransactionID=DamageStockDetailsID,
                        BranchID=BranchID,
                        Action=Action,
                        DamageStockMasterID=DamageStockMasterID,
                        ProductID=ProductID,
                        Stock=Stock,
                        PriceListID=PriceListID,
                        DamageStock=DamageStock,
                        CreatedDate=today,
                        LastUPDDate=today,
                        CreatedUserID=CreatedUserID,
                        LastUPDUserID=CreatedUserID,
                        CostPerItem=CostPerItem,
                        CompanyID=CompanyID,
                    )

                    damageStockDetail_instance.ProductID = ProductID
                    damageStockDetail_instance.Stock = Stock
                    damageStockDetail_instance.PriceListID = PriceListID
                    damageStockDetail_instance.CostPerItem = CostPerItem
                    damageStockDetail_instance.DamageStock = DamageStock
                    damageStockDetail_instance.Action = Action
                    damageStockDetail_instance.LastUPDDate = today
                    damageStockDetail_instance.save()

                    if product_is_Service == False:
                        if StockPosting.objects.filter(CompanyID=CompanyID,WareHouseID=WarehouseID, VoucherMasterID=DamageStockMasterID,VoucherDetailID=DamageStockDetailsID,BranchID=BranchID, VoucherType="DS",ProductID=ProductID).exists():
                            stock_instance = StockPosting.objects.filter(CompanyID=CompanyID,WareHouseID=WarehouseID, VoucherMasterID=DamageStockMasterID,VoucherDetailID=DamageStockDetailsID,BranchID=BranchID, VoucherType="DS",ProductID=ProductID).first()
                            stock_instance.QtyOut = Qty
                            stock_instance.Action = Action
                            stock_instance.UpdatedDate = today
                            stock_instance.save()
                            update_stock(CompanyID,BranchID,ProductID)
                        else:
                            StockPostingID = get_auto_stockPostid(
                                StockPosting, BranchID, CompanyID)
                            StockPosting.objects.create(
                                StockPostingID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=Date,
                                VoucherMasterID=DamageStockMasterID,
                                VoucherDetailID=DamageStockDetailsID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                WareHouseID=WarehouseID,
                                QtyOut=Qty,
                                Rate=Cost,
                                PriceListID=PriceListID_DefUnit,
                                IsActive=IsActive,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                            )

                            StockPosting_Log.objects.create(
                                TransactionID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=Date,
                                VoucherMasterID=DamageStockMasterID,
                                VoucherDetailID=DamageStockDetailsID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                WareHouseID=WarehouseID,
                                QtyOut=Qty,
                                Rate=Cost,
                                PriceListID=PriceListID_DefUnit,
                                IsActive=IsActive,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                            )

                            update_stock(CompanyID,BranchID,ProductID)

                    

                if detailID == 1:
                    Action = "A"
                    DamageStockDetailsID = get_auto_damageDetailsID(
                        DamageStockDetails, BranchID, CompanyID)

                    log_instance = DamageStockDetails_Log.objects.create(
                        TransactionID=DamageStockDetailsID,
                        BranchID=BranchID,
                        Action=Action,
                        DamageStockMasterID=DamageStockMasterID,
                        ProductID=ProductID,
                        Stock=Stock,
                        PriceListID=PriceListID,
                        DamageStock=DamageStock,
                        CreatedDate=today,
                        LastUPDDate=today,
                        CreatedUserID=CreatedUserID,
                        LastUPDUserID=CreatedUserID,
                        CostPerItem=CostPerItem,
                        CompanyID=CompanyID,
                    )

                    DamageStockDetails.objects.create(
                        CompanyID=CompanyID,
                        DamageStockDetailsID=DamageStockDetailsID,
                        BranchID=BranchID,
                        Action=Action,
                        DamageStockMasterID=DamageStockMasterID,
                        ProductID=ProductID,
                        Stock=Stock,
                        PriceListID=PriceListID,
                        DamageStock=DamageStock,
                        CreatedDate=today,
                        LastUPDDate=today,
                        CreatedUserID=CreatedUserID,
                        LastUPDUserID=CreatedUserID,
                        CostPerItem=CostPerItem,
                        LogID=log_instance.ID
                    )

                    if product_is_Service == False:
                        StockPostingID = get_auto_stockPostid(
                            StockPosting, BranchID, CompanyID)
                        StockPosting.objects.create(
                            StockPostingID=StockPostingID,
                            BranchID=BranchID,
                            Action=Action,
                            Date=Date,
                            VoucherMasterID=DamageStockMasterID,
                            VoucherDetailID=DamageStockDetailsID,
                            VoucherType=VoucherType,
                            ProductID=ProductID,
                            WareHouseID=WarehouseID,
                            QtyOut=Qty,
                            Rate=Cost,
                            PriceListID=PriceListID_DefUnit,
                            IsActive=True,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )

                        StockPosting_Log.objects.create(
                            TransactionID=StockPostingID,
                            BranchID=BranchID,
                            Action=Action,
                            Date=Date,
                            VoucherMasterID=DamageStockMasterID,
                            VoucherDetailID=DamageStockDetailsID,
                            VoucherType=VoucherType,
                            ProductID=ProductID,
                            WareHouseID=WarehouseID,
                            QtyOut=Qty,
                            Rate=Cost,
                            PriceListID=PriceListID_DefUnit,
                            IsActive=True,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )

                        update_stock(CompanyID,BranchID,ProductID)

            deleted_datas = data["deleted_data"]
            if deleted_datas:
                for deleted_Data in deleted_datas:
                    deleted_pk = deleted_Data['unq_id']
                    DamageStockDetailID_Deleted = deleted_Data['DamageStockDetailID']
                    ProductID_Deleted = deleted_Data['ProductID']
                    PriceListID_Deleted = deleted_Data['PriceListID']
                    Rate_Deleted = deleted_Data['Rate']
                    DamageStockMasterID_Deleted = deleted_Data['DamageStockMasterID']
                    WarehouseID_Deleted = deleted_Data['WarehouseID']

                    if not deleted_pk == '' or not deleted_pk == 0:
                        if DamageStockDetails.objects.filter(CompanyID=CompanyID,pk=deleted_pk).exists():
                            deleted_detail = DamageStockDetails.objects.filter(CompanyID=CompanyID,pk=deleted_pk)
                            deleted_detail.delete()

                            if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=DamageStockMasterID_Deleted,VoucherDetailID=DamageStockDetailID_Deleted,ProductID=ProductID_Deleted,BranchID=BranchID, VoucherType="DS").exists():
                                stock_instances_delete = StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=DamageStockMasterID_Deleted,VoucherDetailID=DamageStockDetailID_Deleted,ProductID=ProductID_Deleted,BranchID=BranchID, VoucherType="DS")
                                stock_instances_delete.delete()

                                update_stock(CompanyID,BranchID,ProductID_Deleted)

            # deleted_ids = data["deleted_ids"]
            # for d in deleted_ids:
            #     update_stock(CompanyID,BranchID,d)

                # if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Cost=CostPerItem, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID).exists():
                #     stockRateInstance = StockRate.objects.get(
                #         CompanyID=CompanyID, BranchID=BranchID, Cost=CostPerItem, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID)

                #     StockRateID = stockRateInstance.StockRateID
                #     stockRateInstance.Qty = float(
                #         stockRateInstance.Qty) + float(DamageStock)
                #     stockRateInstance.save()

                #     if StockTrans.objects.filter(StockRateID=StockRateID, DetailID=DamageStockDetailsID, MasterID=DamageStockMasterID, VoucherType=VoucherType, BranchID=BranchID, IsActive=True).exists():
                #         stockTra_in = StockTrans.objects.filter(StockRateID=StockRateID, DetailID=DamageStockDetailsID,
                #                                                 MasterID=DamageStockMasterID, VoucherType=VoucherType, BranchID=BranchID, IsActive=True).first()
                #         stockTra_in.Qty = float(stockTra_in.Qty) + float(DamageStock)
                #         stockTra_in.save()
                #     else:
                #         StockTransID = get_auto_StockTransID(
                #             StockTrans, BranchID, CompanyID)
                #         StockTrans.objects.create(
                #             StockTransID=StockTransID,
                #             BranchID=BranchID,
                #             VoucherType=VoucherType,
                #             StockRateID=StockRateID,
                #             DetailID=DamageStockDetailsID,
                #             MasterID=DamageStockMasterID,
                #             Qty=DamageStock,
                #             IsActive=True,
                #             CompanyID=CompanyID,
                #         )

                # else:
                #     StockRateID = get_auto_StockRateID(StockRate, BranchID, CompanyID)
                #     StockRate.objects.create(
                #         StockRateID=StockRateID,
                #         BranchID=BranchID,
                #         PurchasePrice=PurchasePrice,
                #         SalesPrice=SalesPrice,
                #         Qty=DamageStock,
                #         Cost=CostPerItem,
                #         ProductID=ProductID,
                #         WareHouseID=WarehouseID,
                #         Date=Date,
                #         PriceListID=PriceListID,
                #         CreatedUserID=CreatedUserID,
                #         CreatedDate=today,
                #         UpdatedDate=today,
                #         CompanyID=CompanyID,
                #     )

                #     StockTransID = get_auto_StockTransID(
                #         StockTrans, BranchID, CompanyID)
                #     StockTrans.objects.create(
                #         StockTransID=StockTransID,
                #         BranchID=BranchID,
                #         VoucherType=VoucherType,
                #         StockRateID=StockRateID,
                #         DetailID=DamageStockDetailsID,
                #         MasterID=DamageStockMasterID,
                #         Qty=DamageStock,
                #         IsActive=True,
                #         CompanyID=CompanyID,
                #     )
            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'DamageStock',
            #              'Edit', 'DamageStock Updated successfully.', 'ShortageStock Updated successfully.')

            response_data = {
                "StatusCode": 6000,
                "message": "Damage Stock Updated Successfully!!!",
            }

            return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again"
        }

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Damage Stock',
                         'Edit', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def damageStock(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if DamageStockMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
            instance = DamageStockMaster.objects.get(
                CompanyID=CompanyID, pk=pk)
            serialized = DamageStockMasterSerializer(instance, context={"CompanyID": CompanyID,
                                                                        "PriceRounding": PriceRounding})
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Damage Stock Not Found in this Branch!"
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
@transaction.atomic
def create_used_stock(request):
    try:
        with transaction.atomic():
            today = datetime.datetime.now()

            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)

            CreatedUserID = data['CreatedUserID']
            BranchID = data['BranchID']
            VoucherNo = data['VoucherNo']
            Date = data['Date']
            Notes = data['Notes']
            WarehouseID = data['WarehouseID']
            TotalQty = data['TotalQty']
            GrandTotal = data['GrandTotal']

            VoucherType = "US"

            # VoucherNo Updated
            try:
                PreFix = data['PreFix']
            except:
                PreFix = "US"

            try:
                Seperator = data['Seperator']
            except:
                Seperator = ""

            try:
                InvoiceNo = data['InvoiceNo']
            except:
                InvoiceNo = 1

            Action = "A"

            if not UsedStockMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherNo__iexact=VoucherNo).exists():
                update_voucher_table(CompanyID,CreatedUserID,VoucherType,PreFix,Seperator, InvoiceNo)
                UsedStockMasterID = get_auto_usedMasterID(
                    UsedStockMaster, BranchID, CompanyID)

                UsedStockMaster_Log.objects.create(
                    TransactionID=UsedStockMasterID,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    Date=Date,
                    Notes=Notes,
                    WarehouseID=WarehouseID,
                    TotalQty=TotalQty,
                    GrandTotal=GrandTotal,
                    CreatedDate=today,
                    LastUPDDate=today,
                    CreatedUserID=CreatedUserID,
                    LastUPDUserID=CreatedUserID,
                )

                UsedStockMaster.objects.create(
                    CompanyID=CompanyID,
                    UsedStockMasterID=UsedStockMasterID,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    Date=Date,
                    Notes=Notes,
                    WarehouseID=WarehouseID,
                    TotalQty=TotalQty,
                    GrandTotal=GrandTotal,
                    CreatedDate=today,
                    LastUPDDate=today,
                    CreatedUserID=CreatedUserID,
                    LastUPDUserID=CreatedUserID,

                )

                Details = data["Details"]

                VoucherType = "US"

                for d in Details:
                    ProductID = d['ProductID']
                    Stock = d['Stock']
                    PriceListID = d['PriceListID']
                    UsedStock = d['UsedStock']
                    CostPerItem = d['CostPerItem']

                    UsedStockDetailsID = get_auto_usedDetailsID(
                        UsedStockDetails, BranchID, CompanyID)

                    log_instance = UsedStockDetails_Log.objects.create(
                        TransactionID=UsedStockDetailsID,
                        BranchID=BranchID,
                        Action=Action,
                        UsedStockMasterID=UsedStockMasterID,
                        ProductID=ProductID,
                        Stock=Stock,
                        PriceListID=PriceListID,
                        UsedStock=UsedStock,
                        CreatedDate=today,
                        LastUPDDate=today,
                        CreatedUserID=CreatedUserID,
                        LastUPDUserID=CreatedUserID,
                        CostPerItem=CostPerItem,
                        CompanyID=CompanyID,
                    )

                    UsedStockDetails.objects.create(
                        CompanyID=CompanyID,
                        UsedStockDetailsID=UsedStockDetailsID,
                        BranchID=BranchID,
                        Action=Action,
                        UsedStockMasterID=UsedStockMasterID,
                        ProductID=ProductID,
                        Stock=Stock,
                        PriceListID=PriceListID,
                        UsedStock=UsedStock,
                        CreatedDate=today,
                        LastUPDDate=today,
                        CreatedUserID=CreatedUserID,
                        LastUPDUserID=CreatedUserID,
                        CostPerItem=CostPerItem,
                        LogID=log_instance.ID
                    )

                    product_is_Service = Product.objects.get(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).is_Service
                    MultiFactor = PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).MultiFactor
                    PriceListID_DefUnit = PriceList.objects.get(
                        CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True, BranchID=BranchID).PriceListID

                    princeList_instance = PriceList.objects.get(
                        CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID_DefUnit, BranchID=BranchID)
                    PurchasePrice = princeList_instance.PurchasePrice
                    SalesPrice = princeList_instance.SalesPrice

                    # qty = float(FreeQty) + float(Qty)

                    Qty = float(MultiFactor) * float(UsedStock)
                    Cost = float(CostPerItem) / float(MultiFactor)

                    StockPostingID = get_auto_stockPostid(
                        StockPosting, BranchID, CompanyID)

                    StockPosting.objects.create(
                        StockPostingID=StockPostingID,
                        BranchID=BranchID,
                        Action=Action,
                        Date=Date,
                        VoucherMasterID=UsedStockMasterID,
                        VoucherDetailID=UsedStockDetailsID,
                        VoucherType=VoucherType,
                        ProductID=ProductID,
                        WareHouseID=WarehouseID,
                        QtyOut=Qty,
                        Rate=Cost,
                        PriceListID=PriceListID,
                        IsActive=True,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                    )

                    StockPosting_Log.objects.create(
                        TransactionID=StockPostingID,
                        BranchID=BranchID,
                        Action=Action,
                        Date=Date,
                        VoucherMasterID=UsedStockMasterID,
                        VoucherDetailID=UsedStockDetailsID,
                        VoucherType=VoucherType,
                        ProductID=ProductID,
                        WareHouseID=WarehouseID,
                        QtyOut=Qty,
                        Rate=Cost,
                        PriceListID=PriceListID,
                        IsActive=True,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                    )

                    update_stock(CompanyID,BranchID,ProductID)


                    # if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Cost=CostPerItem, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID).exists():
                    #     stockRateInstance = StockRate.objects.get(
                    #         CompanyID=CompanyID, BranchID=BranchID, Cost=CostPerItem, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID)

                    #     StockRateID = stockRateInstance.StockRateID
                    #     stockRateInstance.Qty = float(
                    #         stockRateInstance.Qty) - float(UsedStock)
                    #     stockRateInstance.save()

                    #     if StockTrans.objects.filter(StockRateID=StockRateID, DetailID=UsedStockDetailsID, MasterID=UsedStockMasterID, VoucherType=VoucherType, BranchID=BranchID, IsActive=True).exists():
                    #         stockTra_in = StockTrans.objects.filter(StockRateID=StockRateID, DetailID=UsedStockDetailsID,
                    #                                                 MasterID=UsedStockMasterID, VoucherType=VoucherType, BranchID=BranchID, IsActive=True).first()
                    #         stockTra_in.Qty = float(stockTra_in.Qty) - float(UsedStock)
                    #         stockTra_in.save()
                    #     else:
                    #         StockTransID = get_auto_StockTransID(
                    #             StockTrans, BranchID, CompanyID)
                    #         StockTrans.objects.create(
                    #             StockTransID=StockTransID,
                    #             BranchID=BranchID,
                    #             VoucherType=VoucherType,
                    #             StockRateID=StockRateID,
                    #             DetailID=UsedStockDetailsID,
                    #             MasterID=UsedStockMasterID,
                    #             Qty=UsedStock,
                    #             IsActive=True,
                    #             CompanyID=CompanyID,
                    #         )

                    # else:
                    #     StockRateID = get_auto_StockRateID(
                    #         StockRate, BranchID, CompanyID)
                    #     StockRate.objects.create(
                    #         StockRateID=StockRateID,
                    #         BranchID=BranchID,
                    #         PurchasePrice=PurchasePrice,
                    #         SalesPrice=SalesPrice,
                    #         Qty=UsedStock,
                    #         Cost=CostPerItem,
                    #         ProductID=ProductID,
                    #         WareHouseID=WarehouseID,
                    #         Date=Date,
                    #         PriceListID=PriceListID,
                    #         CreatedUserID=CreatedUserID,
                    #         CreatedDate=today,
                    #         UpdatedDate=today,
                    #         CompanyID=CompanyID,
                    #     )

                    #     StockTransID = get_auto_StockTransID(
                    #         StockTrans, BranchID, CompanyID)
                    #     StockTrans.objects.create(
                    #         StockTransID=StockTransID,
                    #         BranchID=BranchID,
                    #         VoucherType=VoucherType,
                    #         StockRateID=StockRateID,
                    #         DetailID=UsedStockDetailsID,
                    #         MasterID=UsedStockMasterID,
                    #         Qty=UsedStock,
                    #         IsActive=True,
                    #         CompanyID=CompanyID,
                    #     )

                response_data = {
                    "StatusCode": 6000,
                    "message": "Used Stock Created Successfully!!!"
                }

                return Response(response_data, status=status.HTTP_200_OK)

            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "VoucherNo Already Exist.Please Change Your Prefix!"
                }

                return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again"
        }

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Used Stock',
                         'Create', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_usedStock(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']

    try:
        page_number = data['page_no']
    except:
        page_number = ""

    try:
        items_per_page = data['items_per_page']
    except:
        items_per_page = ""

    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if UsedStockMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():

            if page_number and items_per_page:
                instances = UsedStockMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)
                count = len(instances)
                ledger_sort_pagination = list_pagination(
                    instances,
                    items_per_page,
                    page_number
                )
                print(ledger_sort_pagination)
                # serialized = WarehouseRestSerializer(ledger_sort_pagination, many=True)
                # data = serialized.data
            else:
                ledger_sort_pagination = UsedStockMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)
                count = len(ledger_sort_pagination)
            serialized = UsedStockMaster1Serializer(ledger_sort_pagination, many=True, context={"CompanyID": CompanyID,
                                                                                               "PriceRounding": PriceRounding})
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "count": count
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Used Stock Not Found in this Branch!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_usedStock(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    instance = None
    if UsedStockMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = UsedStockMaster.objects.get(CompanyID=CompanyID, pk=pk)
        UsedStockMasterID = instance.UsedStockMasterID
        BranchID = instance.BranchID
        Date = instance.Date
        VoucherNo = instance.VoucherNo
        Notes = instance.Notes
        WarehouseID = instance.WarehouseID
        TotalQty = instance.TotalQty
        GrandTotal = instance.GrandTotal
        Action = "D"

        instance.delete()
        UsedStockMaster_Log.objects.create(
            TransactionID=UsedStockMasterID,
            BranchID=BranchID,
            Action=Action,
            VoucherNo=VoucherNo,
            Date=Date,
            Notes=Notes,
            WarehouseID=WarehouseID,
            TotalQty=TotalQty,
            GrandTotal=GrandTotal,
            CreatedDate=today,
            LastUPDDate=today,
            CreatedUserID=CreatedUserID,
            LastUPDUserID=CreatedUserID,
        )

        if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=UsedStockMasterID, BranchID=BranchID, VoucherType="US").exists():

            stockPostingInstances = StockPosting.objects.filter(
                CompanyID=CompanyID, VoucherMasterID=UsedStockMasterID, BranchID=BranchID, VoucherType="US")

            for stockPostingInstance in stockPostingInstances:

                StockPostingID = stockPostingInstance.StockPostingID
                BranchID = stockPostingInstance.BranchID
                Date = stockPostingInstance.Date
                VoucherMasterID = stockPostingInstance.VoucherMasterID
                VoucherType = stockPostingInstance.VoucherType
                ProductID = stockPostingInstance.ProductID
                BatchID = stockPostingInstance.BatchID
                WareHouseID = stockPostingInstance.WareHouseID
                QtyIn = stockPostingInstance.QtyIn
                QtyOut = stockPostingInstance.QtyOut
                Rate = stockPostingInstance.Rate
                PriceListID = stockPostingInstance.PriceListID
                IsActive = stockPostingInstance.IsActive

                StockPosting_Log.objects.create(
                    TransactionID=StockPostingID,
                    BranchID=BranchID,
                    Action=Action,
                    Date=Date,
                    VoucherMasterID=UsedStockMasterID,
                    VoucherType=VoucherType,
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

                stockPostingInstance.delete()

                update_stock(CompanyID,BranchID,ProductID)

        detail_instances = UsedStockDetails.objects.filter(
            CompanyID=CompanyID, UsedStockMasterID=UsedStockMasterID)

        for detail_instance in detail_instances:

            UsedStockDetailsID = detail_instance.UsedStockDetailsID
            BranchID = detail_instance.BranchID
            UsedStockMasterID = detail_instance.UsedStockMasterID
            ProductID = detail_instance.ProductID
            Stock = detail_instance.Stock
            PriceListID = detail_instance.PriceListID
            UsedStock = detail_instance.UsedStock
            CostPerItem = detail_instance.CostPerItem

            update_stock(CompanyID,BranchID,ProductID)

            UsedStockDetails_Log.objects.create(
                TransactionID=UsedStockDetailsID,
                BranchID=BranchID,
                Action=Action,
                UsedStockMasterID=UsedStockMasterID,
                ProductID=ProductID,
                Stock=Stock,
                PriceListID=PriceListID,
                UsedStock=UsedStock,
                CreatedDate=today,
                LastUPDDate=today,
                CreatedUserID=CreatedUserID,
                LastUPDUserID=CreatedUserID,
                CostPerItem=CostPerItem,
                CompanyID=CompanyID,
            )

            detail_instance.delete()

            # if StockTrans.objects.filter(CompanyID=CompanyID,DetailID=PurchaseDetailsID,MasterID=PurchaseMasterID,BranchID=BranchID,VoucherType="PI").exists():
            #     stockTrans_instance = StockTrans.objects.get(CompanyID=CompanyID,DetailID=PurchaseDetailsID,MasterID=PurchaseMasterID,BranchID=BranchID,VoucherType="PI")

            #     stockRateID = stockTrans_instance.StockRateID
            #     stockTrans_instance.IsActive = False
            #     stockTrans_instance.save()

            #     stockRate_instance = StockRate.objects.get(CompanyID=CompanyID,StockRateID=stockRateID,BranchID=BranchID)
            #     stockRate_instance.Qty = stockTrans_instance.Qty
            #     stockRate_instance.save()

            if StockTrans.objects.filter(CompanyID=CompanyID, DetailID=UsedStockDetailsID, MasterID=UsedStockMasterID, BranchID=BranchID, VoucherType="US", IsActive=True).exists():
                stockTrans_instances = StockTrans.objects.filter(
                    CompanyID=CompanyID, DetailID=UsedStockDetailsID, MasterID=UsedStockMasterID, BranchID=BranchID, VoucherType="US", IsActive=True)

                for i in stockTrans_instances:
                    stockRateID = i.StockRateID
                    i.IsActive = False
                    i.save()

                    stockRate_instance = StockRate.objects.get(
                        CompanyID=CompanyID, StockRateID=stockRateID, BranchID=BranchID)
                    stockRate_instance.Qty = i.Qty
                    stockRate_instance.save()
        response_data = {
            "StatusCode": 6000,
            "message": "Used Stock Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Used Stock Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def edit_usedStock(request, pk):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            CreatedUserID = data['CreatedUserID']
            today = datetime.datetime.now()

            usedStockMaster_instance = UsedStockMaster.objects.get(
                pk=pk, CompanyID=CompanyID)
            UsedStockMasterID = usedStockMaster_instance.UsedStockMasterID
            BranchID = usedStockMaster_instance.BranchID

            VoucherType = "US"

            VoucherNo = data['VoucherNo']
            Date = data['Date']
            Notes = data['Notes']
            WarehouseID = data['WarehouseID']
            TotalQty = data['TotalQty']
            GrandTotal = data['GrandTotal']

            Action = "M"

            UsedStockMaster_Log.objects.create(
                TransactionID=UsedStockMasterID,
                BranchID=BranchID,
                Action=Action,
                VoucherNo=VoucherNo,
                Date=Date,
                Notes=Notes,
                WarehouseID=WarehouseID,
                TotalQty=TotalQty,
                GrandTotal=GrandTotal,
                CreatedDate=today,
                LastUPDDate=today,
                CreatedUserID=CreatedUserID,
                LastUPDUserID=CreatedUserID,
            )

            # if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=UsedStockMasterID, BranchID=BranchID, VoucherType=VoucherType).exists():
            #     stockPostingInstances = StockPosting.objects.filter(
            #         CompanyID=CompanyID, VoucherMasterID=UsedStockMasterID, BranchID=BranchID, VoucherType=VoucherType)
            #     for stockPostingInstance in stockPostingInstances:
            #         stockPostingInstance.delete()

            if UsedStockDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, UsedStockMasterID=UsedStockMasterID).exists():
                usedStockInstances = UsedStockDetails.objects.filter(
                    CompanyID=CompanyID, UsedStockMasterID=UsedStockMasterID, BranchID=BranchID)
                for i in usedStockInstances:
                    if not StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=UsedStockMasterID,VoucherDetailID=i.UsedStockDetailsID,BranchID=BranchID, VoucherType="US").exists():
                        StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=UsedStockMasterID,BranchID=BranchID, VoucherType="US").delete()
                        update_stock(CompanyID,BranchID,i.ProductID)
                    instance_MultiFactor = PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=i.PriceListID, BranchID=BranchID).MultiFactor

                    instance_qty_sum = float(i.UsedStock)
                    instance_Qty = float(instance_MultiFactor) * float(instance_qty_sum)
                    if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=UsedStockMasterID,VoucherDetailID=i.UsedStockDetailsID,ProductID=i.ProductID,BranchID=BranchID, VoucherType="US").exists():
                        stock_inst = StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=UsedStockMasterID,VoucherDetailID=i.UsedStockDetailsID,ProductID=i.ProductID,BranchID=BranchID, VoucherType="US").first()
                        stock_inst.QtyOut = float(stock_inst.QtyOut) - float(instance_Qty)
                        stock_inst.save()
                        update_stock(CompanyID,BranchID,i.ProductID)

            # if UsedStockDetails.objects.filter(UsedStockMasterID=UsedStockMasterID, BranchID=BranchID, CompanyID=CompanyID).exists():
            #     usedStockDetails_instances = UsedStockDetails.objects.filter(
            #         UsedStockMasterID=UsedStockMasterID, BranchID=BranchID, CompanyID=CompanyID)
            #     for detail in usedStockDetails_instances:
            #         detail.delete()

            # if StockTrans.objects.filter(CompanyID=CompanyID, VoucherType=VoucherType, MasterID=UsedStockMasterID, BranchID=BranchID, IsActive=True).exists():
            #     trans_ins = StockTrans.objects.filter(
            #         CompanyID=CompanyID, VoucherType=VoucherType, MasterID=UsedStockMasterID, BranchID=BranchID, IsActive=True)
            #     for stk in trans_ins:
            #         StockRateID = stk.StockRateID
            #         stockQty = stk.Qty

            #         rate_ins = StockRate.objects.filter(
            #             CompanyID=CompanyID, StockRateID=StockRateID, BranchID=BranchID).first()
            #         rate_ins.Qty = float(rate_ins.Qty) + float(stockQty)
            #         rate_ins.save()
            #         stk.IsActive = False
            #         stk.save()

            usedStockMaster_instance.Date = Date
            usedStockMaster_instance.Notes = Notes
            usedStockMaster_instance.WarehouseID = WarehouseID
            usedStockMaster_instance.TotalQty = TotalQty
            usedStockMaster_instance.GrandTotal = GrandTotal
            usedStockMaster_instance.Action = Action
            usedStockMaster_instance.LastUPDDate = today
            usedStockMaster_instance.LastUPDUserID = CreatedUserID

            usedStockMaster_instance.save()

            Details = data["Details"]

            for d in Details:
                if d['id']:
                    pk = d['id']
                ProductID = d['ProductID']
                Stock = d['Stock']
                PriceListID = d['PriceListID']
                UsedStock = d['UsedStock']
                CostPerItem = d['CostPerItem']
                detailID = d['detailID']

                product_is_Service = Product.objects.get(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).is_Service
                MultiFactor = PriceList.objects.get(
                    CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).MultiFactor
                PriceListID_DefUnit = PriceList.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True, BranchID=BranchID).PriceListID

                princeList_instance = PriceList.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID_DefUnit, BranchID=BranchID)
                PurchasePrice = princeList_instance.PurchasePrice
                SalesPrice = princeList_instance.SalesPrice

                # qty = float(FreeQty) + float(Qty)

                Qty = float(MultiFactor) * float(UsedStock)
                Cost = float(CostPerItem) / float(MultiFactor)

                if detailID == 0:
                    usedStockDetail_instance = UsedStockDetails.objects.get(
                        CompanyID=CompanyID, pk=pk)
                    UsedStockDetailsID = usedStockDetail_instance.UsedStockDetailsID

                    log_instance = UsedStockDetails_Log.objects.create(
                        TransactionID=UsedStockDetailsID,
                        BranchID=BranchID,
                        Action=Action,
                        UsedStockMasterID=UsedStockMasterID,
                        ProductID=ProductID,
                        Stock=Stock,
                        PriceListID=PriceListID,
                        UsedStock=UsedStock,
                        CreatedDate=today,
                        LastUPDDate=today,
                        CreatedUserID=CreatedUserID,
                        LastUPDUserID=CreatedUserID,
                        CostPerItem=CostPerItem,
                        CompanyID=CompanyID,
                    )

                    usedStockDetail_instance.ProductID = ProductID
                    usedStockDetail_instance.Stock = Stock
                    usedStockDetail_instance.PriceListID = PriceListID
                    usedStockDetail_instance.CostPerItem = CostPerItem
                    usedStockDetail_instance.UsedStock = UsedStock
                    usedStockDetail_instance.Action = Action
                    usedStockDetail_instance.LastUPDDate = today
                    usedStockDetail_instance.save()

                    if product_is_Service == False:
                        if StockPosting.objects.filter(CompanyID=CompanyID,WareHouseID=WarehouseID, VoucherMasterID=UsedStockMasterID,VoucherDetailID=UsedStockDetailsID,BranchID=BranchID, VoucherType="US",ProductID=ProductID).exists():
                            stock_instance = StockPosting.objects.filter(CompanyID=CompanyID,WareHouseID=WarehouseID, VoucherMasterID=UsedStockMasterID,VoucherDetailID=UsedStockDetailsID,BranchID=BranchID, VoucherType="US",ProductID=ProductID).first()
                            stock_instance.QtyOut = Qty
                            stock_instance.Action = Action
                            stock_instance.UpdatedDate = today
                            stock_instance.save()
                            update_stock(CompanyID,BranchID,ProductID)
                        else:
                            StockPostingID = get_auto_stockPostid(
                                StockPosting, BranchID, CompanyID)
                            StockPosting.objects.create(
                                StockPostingID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=Date,
                                VoucherMasterID=UsedStockMasterID,
                                VoucherDetailID=UsedStockDetailsID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                WareHouseID=WarehouseID,
                                QtyOut=Qty,
                                Rate=Cost,
                                PriceListID=PriceListID_DefUnit,
                                IsActive=IsActive,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                            )

                            StockPosting_Log.objects.create(
                                TransactionID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=Date,
                                VoucherMasterID=UsedStockMasterID,
                                VoucherDetailID=UsedStockDetailsID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                WareHouseID=WarehouseID,
                                QtyOut=Qty,
                                Rate=Cost,
                                PriceListID=PriceListID_DefUnit,
                                IsActive=IsActive,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                            )

                            update_stock(CompanyID,BranchID,ProductID)

                if detailID == 1:
                    Action = "A"
                    UsedStockDetailsID = get_auto_usedDetailsID(
                        UsedStockDetails, BranchID, CompanyID)

                    log_instance = UsedStockDetails_Log.objects.create(
                        TransactionID=UsedStockDetailsID,
                        BranchID=BranchID,
                        Action=Action,
                        UsedStockMasterID=UsedStockMasterID,
                        ProductID=ProductID,
                        Stock=Stock,
                        PriceListID=PriceListID,
                        UsedStock=UsedStock,
                        CreatedDate=today,
                        LastUPDDate=today,
                        CreatedUserID=CreatedUserID,
                        LastUPDUserID=CreatedUserID,
                        CostPerItem=CostPerItem,
                        CompanyID=CompanyID,
                    )

                    UsedStockDetails.objects.create(
                        CompanyID=CompanyID,
                        UsedStockDetailsID=UsedStockDetailsID,
                        BranchID=BranchID,
                        Action=Action,
                        UsedStockMasterID=UsedStockMasterID,
                        ProductID=ProductID,
                        Stock=Stock,
                        PriceListID=PriceListID,
                        UsedStock=UsedStock,
                        CreatedDate=today,
                        LastUPDDate=today,
                        CreatedUserID=CreatedUserID,
                        LastUPDUserID=CreatedUserID,
                        CostPerItem=CostPerItem,
                        LogID=log_instance.ID
                    )

                    if product_is_Service == False:
                        StockPostingID = get_auto_stockPostid(
                            StockPosting, BranchID, CompanyID)
                        StockPosting.objects.create(
                            StockPostingID=StockPostingID,
                            BranchID=BranchID,
                            Action=Action,
                            Date=Date,
                            VoucherMasterID=UsedStockMasterID,
                            VoucherDetailID=UsedStockDetailsID,
                            VoucherType=VoucherType,
                            ProductID=ProductID,
                            WareHouseID=WarehouseID,
                            QtyOut=Qty,
                            Rate=Cost,
                            PriceListID=PriceListID_DefUnit,
                            IsActive=True,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )

                        StockPosting_Log.objects.create(
                            TransactionID=StockPostingID,
                            BranchID=BranchID,
                            Action=Action,
                            Date=Date,
                            VoucherMasterID=UsedStockMasterID,
                            VoucherDetailID=UsedStockDetailsID,
                            VoucherType=VoucherType,
                            ProductID=ProductID,
                            WareHouseID=WarehouseID,
                            QtyOut=Qty,
                            Rate=Cost,
                            PriceListID=PriceListID_DefUnit,
                            IsActive=True,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )

                        update_stock(CompanyID,BranchID,ProductID)

            deleted_datas = data["deleted_data"]
            if deleted_datas:
                for deleted_Data in deleted_datas:
                    deleted_pk = deleted_Data['unq_id']
                    UsedStockDetailID_Deleted = deleted_Data['UsedStockDetailID']
                    ProductID_Deleted = deleted_Data['ProductID']
                    PriceListID_Deleted = deleted_Data['PriceListID']
                    Rate_Deleted = deleted_Data['Rate']
                    UsedStockMasterID_Deleted = deleted_Data['UsedStockMasterID']
                    WarehouseID_Deleted = deleted_Data['WarehouseID']

                    if not deleted_pk == '' or not deleted_pk == 0:
                        if UsedStockDetails.objects.filter(CompanyID=CompanyID,pk=deleted_pk).exists():
                            deleted_detail = UsedStockDetails.objects.filter(CompanyID=CompanyID,pk=deleted_pk)
                            deleted_detail.delete()

                            if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=UsedStockMasterID_Deleted,VoucherDetailID=UsedStockDetailID_Deleted,ProductID=ProductID_Deleted,BranchID=BranchID, VoucherType="US").exists():
                                stock_instances_delete = StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=UsedStockMasterID_Deleted,VoucherDetailID=UsedStockDetailID_Deleted,ProductID=ProductID_Deleted,BranchID=BranchID, VoucherType="US")
                                stock_instances_delete.delete()
                                update_stock(CompanyID,BranchID,ProductID_Deleted)

            # deleted_ids = data["deleted_ids"]
            # for d in deleted_ids:
            #     update_stock(CompanyID,BranchID,d)

                # if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Cost=CostPerItem, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID).exists():
                #     stockRateInstance = StockRate.objects.get(
                #         CompanyID=CompanyID, BranchID=BranchID, Cost=CostPerItem, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID)

                #     StockRateID = stockRateInstance.StockRateID
                #     stockRateInstance.Qty = float(
                #         stockRateInstance.Qty) + float(UsedStock)
                #     stockRateInstance.save()

                #     if StockTrans.objects.filter(StockRateID=StockRateID, DetailID=UsedStockDetailsID, MasterID=UsedStockMasterID, VoucherType=VoucherType, BranchID=BranchID, IsActive=True).exists():
                #         stockTra_in = StockTrans.objects.filter(StockRateID=StockRateID, DetailID=UsedStockDetailsID,
                #                                                 MasterID=UsedStockMasterID, VoucherType=VoucherType, BranchID=BranchID, IsActive=True).first()
                #         stockTra_in.Qty = float(stockTra_in.Qty) + float(UsedStock)
                #         stockTra_in.save()
                #     else:
                #         StockTransID = get_auto_StockTransID(
                #             StockTrans, BranchID, CompanyID)
                #         StockTrans.objects.create(
                #             StockTransID=StockTransID,
                #             BranchID=BranchID,
                #             VoucherType=VoucherType,
                #             StockRateID=StockRateID,
                #             DetailID=UsedStockDetailsID,
                #             MasterID=UsedStockMasterID,
                #             Qty=UsedStock,
                #             IsActive=True,
                #             CompanyID=CompanyID,
                #         )

                # else:
                #     StockRateID = get_auto_StockRateID(StockRate, BranchID, CompanyID)
                #     StockRate.objects.create(
                #         StockRateID=StockRateID,
                #         BranchID=BranchID,
                #         PurchasePrice=PurchasePrice,
                #         SalesPrice=SalesPrice,
                #         Qty=UsedStock,
                #         Cost=CostPerItem,
                #         ProductID=ProductID,
                #         WareHouseID=WarehouseID,
                #         Date=Date,
                #         PriceListID=PriceListID,
                #         CreatedUserID=CreatedUserID,
                #         CreatedDate=today,
                #         UpdatedDate=today,
                #         CompanyID=CompanyID,
                #     )

                #     StockTransID = get_auto_StockTransID(
                #         StockTrans, BranchID, CompanyID)
                #     StockTrans.objects.create(
                #         StockTransID=StockTransID,
                #         BranchID=BranchID,
                #         VoucherType=VoucherType,
                #         StockRateID=StockRateID,
                #         DetailID=UsedStockDetailsID,
                #         MasterID=UsedStockMasterID,
                #         Qty=UsedStock,
                #         IsActive=True,
                #         CompanyID=CompanyID,
                #     )
            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'UsedStock',
            #              'Edit', 'UsedStock Updated successfully.', 'ShortageStock Updated successfully.')

            response_data = {
                "StatusCode": 6000,
                "message": "Used Stock Updated Successfully!!!",
            }

            return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again"
        }

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Used Stock',
                         'Edit', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def usedStock(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if UsedStockMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
            instance = UsedStockMaster.objects.get(CompanyID=CompanyID, pk=pk)
            serialized = UsedStockMasterSerializer(instance, context={"CompanyID": CompanyID,
                                                                      "PriceRounding": PriceRounding})
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Used Stock Not Found in this Branch!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)
