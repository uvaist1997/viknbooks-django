import math

from django.db.models.aggregates import Sum
from django.http.response import HttpResponse
import xlwt
from xlwt.Formatting import Alignment
from brands.models import Batch,Unit, VoucherNoTable, OpeningStockMaster, OpeningStockMaster_Log, OpeningStockDetails, OpeningStockDetails_Log, OpeningStockDetailsDummy, StockPosting, StockPosting_Log,\
    PriceList, StockRate, StockTrans, GeneralSettings, Product
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v9.openingStock.serializers import OpeningStockMasterSerializer, OpeningStockMasterRestSerializer, OpeningStockDetailsSerializer, OpeningStockDetailsRestSerializer, OpeningStockFilterSerializer, OpeningStockReportSerializer, OpeningStockMaster1RestSerializer
from api.v9.brands.serializers import ListSerializer
from api.v9.openingStock.functions import generate_serializer_errors
from rest_framework import status
from api.v9.openingStock.functions import get_auto_id, get_auto_idMaster
from api.v9.sales.functions import get_auto_stockPostid
from api.v9.purchases.functions import get_auto_StockRateID, get_auto_StockTransID,SetBatch 
import datetime
from django.shortcuts import get_object_or_404
from main.functions import converted_float, get_BranchSettings, get_ModelInstance, get_company, activity_log, list_pagination,get_GeneralSettings,FormatedDate
from api.v9.sales.functions import get_Genrate_VoucherNo
from api.v9.ledgerPosting.functions import convertOrderdDict
from api.v9.sales.serializers import ListSerializerforReport
from django.db import transaction, IntegrityError
import re
import sys
import os
from api.v9.products.functions import update_stock
from main.functions import update_voucher_table
from api.v9.branchs.functions import get_branch_settings
import json


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def create_openingStock(request):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            CreatedUserID = data['CreatedUserID']

            today = datetime.datetime.now()
            BranchID = data["BranchID"]
            VoucherNo = data["VoucherNo"]
            Date = data["Date"]
            as_on_date = data["as_on_date"]
            WarehouseID = data["WarehouseID"]
            Notes = data["Notes"]
            TotalQty = data["TotalQty"]
            GrandTotal = data["GrandTotal"]
            IsActive = data["IsActive"]
            BatchID = data["BatchID"]
            
            message = ""

            Action = "A"

            VoucherType = "OS"

            # VoucherNo Updated
            try:
                PreFix = data['PreFix']
            except:
                PreFix = "OS"

            try:
                Seperator = data['Seperator']
            except:
                Seperator = ""

            try:
                InvoiceNo = data['InvoiceNo']
            except:
                InvoiceNo = 1

            # checking voucher number already exist
            VoucherNoLow = VoucherNo.lower()
            is_voucherExist = False
            insts = OpeningStockMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
            if insts:
                for i in insts:
                    voucher_no = i.VoucherNo
                    voucherNo = voucher_no.lower()
                    if VoucherNoLow == voucherNo:
                        is_voucherExist = True

            check_VoucherNoAutoGenerate = False
            is_OpeningStockOK = True

            if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="VoucherNoAutoGenerate").exists():
                check_VoucherNoAutoGenerate = GeneralSettings.objects.get(
                    BranchID=BranchID, CompanyID=CompanyID, SettingsType="VoucherNoAutoGenerate").SettingsValue

            if is_voucherExist == True and check_VoucherNoAutoGenerate == "True":
                VoucherNo = get_Genrate_VoucherNo(
                    OpeningStockMaster, BranchID, CompanyID, "OS")
                is_OpeningStockOK = True
            elif is_voucherExist == False:
                is_OpeningStockOK = True
            else:
                is_OpeningStockOK = False

            if is_OpeningStockOK:
                update_voucher_table(
                    CompanyID, CreatedUserID, VoucherType, PreFix, Seperator, InvoiceNo)
                OpeningStockMasterID = get_auto_idMaster(
                    OpeningStockMaster, BranchID, CompanyID)

                OpeningStockMaster_Log.objects.create(
                    TransactionID=OpeningStockMasterID,
                    BranchID=BranchID,
                    VoucherNo=VoucherNo,
                    Date=Date,
                    as_on_date=as_on_date,
                    WarehouseID=WarehouseID,
                    Notes=Notes,
                    TotalQty=TotalQty,
                    GrandTotal=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )
                OpeningStockMaster.objects.create(
                    OpeningStockMasterID=OpeningStockMasterID,
                    BranchID=BranchID,
                    VoucherNo=VoucherNo,
                    as_on_date=as_on_date,
                    Date=Date,
                    WarehouseID=WarehouseID,
                    Notes=Notes,
                    TotalQty=TotalQty,
                    GrandTotal=GrandTotal,
                    IsActive=IsActive,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    Action=Action,
                    CompanyID=CompanyID,
                )

                openingStockDetails = data["OpeningStockDetails"]
                for openingStockDetail in openingStockDetails:
                    if openingStockDetail["ProductID"]:
                        ProductID = openingStockDetail["ProductID"]
                        Qty = openingStockDetail["Qty"]
                        PriceListID = openingStockDetail["PriceListID"]
                        Rate = openingStockDetail["Rate"]
                        Amount = openingStockDetail["Amount"]
                        try:
                            BatchCode = openingStockDetail["BatchCode"]
                        except:
                            BatchCode = ""
                        
                        try:
                            ManufactureDate = openingStockDetail['ManufactureDate']
                        except:
                            ManufactureDate = None

                        try:
                            ExpiryDate = openingStockDetail['ExpiryDate']
                        except:
                            ExpiryDate = None
                            
                        MultiFactor = PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=PriceListID).MultiFactor
                        
                        princeList_instance = PriceList.objects.get(
                            CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID)
                        PurchasePrice = princeList_instance.PurchasePrice
                        SalesPrice = princeList_instance.SalesPrice

                        DetailQty = converted_float(MultiFactor) * converted_float(Qty)
                        
                        if ManufactureDate == "":
                            ManufactureDate = None

                        if ExpiryDate == "":
                            ExpiryDate = None

                        if ManufactureDate:
                            ManufactureDate = FormatedDate(ManufactureDate)

                        if ExpiryDate:
                            ExpiryDate = FormatedDate(ExpiryDate)
                        check_EnableProductBatchWise = get_GeneralSettings(CompanyID,BranchID, "EnableProductBatchWise")
                        check_BatchCriteria = get_GeneralSettings(CompanyID,BranchID, "BatchCriteria")
                        if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                            BatchCode, message = SetBatch(CompanyID, check_EnableProductBatchWise, check_BatchCriteria, BranchID, ProductID, PriceListID, SalesPrice, Rate,
                                                            ExpiryDate, ManufactureDate, Qty, WarehouseID, today, CreatedUserID, BatchCode, "create", "PI")

                        if not message == "":
                            error_code = 11111
                            errr = makingerror

                        OpeningStockDetailsID = get_auto_id(
                            OpeningStockDetails, BranchID, CompanyID)

                        log_instance = OpeningStockDetails_Log.objects.create(
                            TransactionID=OpeningStockDetailsID,
                            BranchID=BranchID,
                            OpeningStockMasterID=OpeningStockMasterID,
                            ProductID=ProductID,
                            Qty=Qty,
                            PriceListID=PriceListID,
                            Rate=Rate,
                            Amount=Amount,
                            Action=Action,
                            CompanyID=CompanyID,
                            BatchCode=BatchCode
                        )
                        OpeningStockDetails.objects.create(
                            OpeningStockDetailsID=OpeningStockDetailsID,
                            BranchID=BranchID,
                            OpeningStockMasterID=OpeningStockMasterID,
                            ProductID=ProductID,
                            Qty=Qty,
                            PriceListID=PriceListID,
                            Rate=Rate,
                            Amount=Amount,
                            Action=Action,
                            CompanyID=CompanyID,
                            LogID=log_instance.ID,
                            BatchCode=BatchCode
                        )

                        # priceList = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,DefaultUnit=True,BranchID=BranchID)

                        # PriceListID = priceList.PriceListID
                        # MultiFactor = priceList.MultiFactor
                        MultiFactor = PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=PriceListID).MultiFactor
                        PriceListID = PriceList.objects.get(
                            CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).PriceListID

                        princeList_instance = PriceList.objects.get(
                            CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID)
                        PurchasePrice = princeList_instance.PurchasePrice
                        SalesPrice = princeList_instance.SalesPrice

                        # qty = converted_float(FreeQty) + converted_float(Qty)

                        Qty = converted_float(MultiFactor) * converted_float(Qty)
                        Cost = converted_float(Rate) / converted_float(MultiFactor)

                        # Qy = round(Qty, 4)
                        # Qty = str(Qy)

                        # Ct = round(Cost, 4)
                        # Cost = str(Ct)

                        product_is_Service = Product.objects.get(
                            CompanyID=CompanyID, ProductID=ProductID).is_Service

                        if product_is_Service == False:
                            pricelist, warehouse = get_ModelInstance(
                                CompanyID, BranchID, PriceListID, WarehouseID)

                            VoucherType = "OS"
                            StockPostingID = get_auto_stockPostid(
                                StockPosting, BranchID, CompanyID)
                            StockPosting.objects.create(
                                StockPostingID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=as_on_date,
                                VoucherMasterID=OpeningStockMasterID,
                                VoucherDetailID=OpeningStockDetailsID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                BatchID=BatchCode,
                                WareHouseID=WarehouseID,
                                QtyIn=Qty,
                                Rate=Cost,
                                PriceListID=PriceListID,
                                IsActive=IsActive,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                                pricelist=pricelist,
                                warehouse=warehouse
                            )

                            StockPosting_Log.objects.create(
                                TransactionID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=as_on_date,
                                VoucherMasterID=OpeningStockMasterID,
                                VoucherDetailID=OpeningStockDetailsID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                BatchID=BatchCode,
                                WareHouseID=WarehouseID,
                                QtyIn=Qty,
                                Rate=Cost,
                                PriceListID=PriceListID,
                                IsActive=IsActive,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                            )

                            update_stock(CompanyID, BranchID, ProductID)

                        # if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID).exists():
                        #     stockRateInstance = StockRate.objects.get(
                        #         CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID)

                        #     StockRateID = stockRateInstance.StockRateID
                        #     stockRateInstance.Qty = converted_float(
                        #         stockRateInstance.Qty) + converted_float(Qty)
                        #     stockRateInstance.save()

                        #     StockTransID = get_auto_StockTransID(
                        #         StockTrans, BranchID, CompanyID)
                        #     StockTrans.objects.create(
                        #         StockTransID=StockTransID,
                        #         BranchID=BranchID,
                        #         VoucherType=VoucherType,
                        #         StockRateID=StockRateID,
                        #         DetailID=OpeningStockDetailsID,
                        #         MasterID=OpeningStockMasterID,
                        #         Qty=Qty,
                        #         IsActive=IsActive,
                        #         CompanyID=CompanyID,
                        #     )
                        # else:
                        #     StockRateID = get_auto_StockRateID(
                        #         StockRate, BranchID, CompanyID)
                        #     StockRate.objects.create(
                        #         StockRateID=StockRateID,
                        #         BranchID=BranchID,
                        #         BatchID=BatchID,
                        #         PurchasePrice=PurchasePrice,
                        #         SalesPrice=SalesPrice,
                        #         Qty=Qty,
                        #         Cost=Cost,
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
                        #         DetailID=OpeningStockDetailsID,
                        #         MasterID=OpeningStockMasterID,
                        #         Qty=Qty,
                        #         IsActive=IsActive,
                        #         CompanyID=CompanyID,
                        #     )

                # request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'OpeningStocK',
                #              'Create', 'OpeningStocK created successfully.', 'OpeningStocK saved successfully.')
                response_data = {
                    "StatusCode": 6000,
                    "message": "Open Stock created Successfully!!!",
                }

                return Response(response_data, status=status.HTTP_200_OK)

            else:
                # request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'OpeningStocK',
                                'Create', 'OpeningStocK created Failed.', 'VoucherNo already exist')
                response_data = {
                    "StatusCode": 6001,
                    "message": "VoucherNo already exist.Please Change Your Prefix!"
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

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'OpeningStocK',
                     'Create', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def edit_openingStock(request, pk):
    # try:
    #     with transaction.atomic():
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()

    openStockMaster_instance = None
    openingStockDetails = None
    openingStockDetails_instances = None
    openStockMaster_instance = OpeningStockMaster.objects.get(
        CompanyID=CompanyID, pk=pk)
    OpeningStockMasterID = openStockMaster_instance.OpeningStockMasterID
    BranchID = openStockMaster_instance.BranchID
    VoucherNo = openStockMaster_instance.VoucherNo
    
    message = ''

    Date = data["Date"]
    as_on_date = data["as_on_date"]
    WarehouseID = data["WarehouseID"]
    Notes = data["Notes"]
    TotalQty = data["TotalQty"]
    GrandTotal = data["GrandTotal"]
    IsActive = data["IsActive"]
    BatchID = data["BatchID"]

    Action = 'M'

    OpeningStockMaster_Log.objects.create(
        TransactionID=OpeningStockMasterID,
        BranchID=BranchID,
        VoucherNo=VoucherNo,
        Date=Date,
        as_on_date=as_on_date,
        WarehouseID=WarehouseID,
        Notes=Notes,
        TotalQty=TotalQty,
        GrandTotal=GrandTotal,
        IsActive=IsActive,
        Action=Action,
        CreatedUserID=CreatedUserID,
        CreatedDate=today,
        UpdatedDate=today,
        CompanyID=CompanyID,
    )

    openStockMaster_instance.as_on_date = as_on_date
    openStockMaster_instance.Date = Date
    openStockMaster_instance.WarehouseID = WarehouseID
    openStockMaster_instance.Notes = Notes
    openStockMaster_instance.TotalQty = TotalQty
    openStockMaster_instance.GrandTotal = GrandTotal
    openStockMaster_instance.IsActive = IsActive
    openStockMaster_instance.Action = Action
    openStockMaster_instance.CreatedUserID = CreatedUserID
    openStockMaster_instance.UpdatedDate = today
    openStockMaster_instance.save()

    # if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=OpeningStockMasterID, BranchID=BranchID, VoucherType="OS").exists():
    #     stockPostingInstances = StockPosting.objects.filter(
    #         CompanyID=CompanyID, VoucherMasterID=OpeningStockMasterID, BranchID=BranchID, VoucherType="OS").delete()
    if OpeningStockDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, OpeningStockMasterID=OpeningStockMasterID).exists():
        openingStockInstances = OpeningStockDetails.objects.filter(
            CompanyID=CompanyID, OpeningStockMasterID=OpeningStockMasterID, BranchID=BranchID)
        print(openingStockInstances)
        for i in openingStockInstances:
            BatchCode = i.BatchCode
            print(BatchCode,"Batch code here print")
            if not StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=OpeningStockMasterID, VoucherDetailID=i.OpeningStockDetailsID, BranchID=BranchID, VoucherType="OS").exists():
                StockPosting.objects.filter(
                    CompanyID=CompanyID, VoucherMasterID=OpeningStockMasterID, BranchID=BranchID, VoucherType="OS").delete()
                update_stock(CompanyID, BranchID, i.ProductID)
            instance_MultiFactor = PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=i.PriceListID).MultiFactor

            instance_qty_sum = converted_float(i.Qty)
            instance_Qty = converted_float(
                instance_MultiFactor) * converted_float(instance_qty_sum)
            if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
                batch_ins = Batch.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode)
                StockIn = batch_ins.StockIn
                batch_ins.StockIn = converted_float(
                    StockIn) - converted_float(instance_Qty)
                batch_ins.save()
            if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=OpeningStockMasterID, VoucherDetailID=i.OpeningStockDetailsID, ProductID=i.ProductID, BranchID=BranchID, VoucherType="OS").exists():
                stock_inst = StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=OpeningStockMasterID,
                                                            VoucherDetailID=i.OpeningStockDetailsID, ProductID=i.ProductID, BranchID=BranchID, VoucherType="OS").first()
                stock_inst.QtyIn = converted_float(
                    stock_inst.QtyIn) - converted_float(instance_Qty)
                stock_inst.save()
                update_stock(CompanyID, BranchID, i.ProductID)

    # if StockTrans.objects.filter(CompanyID=CompanyID, BranchID=BranchID, MasterID=OpeningStockMasterID, VoucherType="OS", IsActive=True).exists():
    #     stocktransIns = StockTrans.objects.filter(
    #         CompanyID=CompanyID, BranchID=BranchID, MasterID=OpeningStockMasterID, VoucherType="OS", IsActive=True)
    #     for stocktran in stocktransIns:
    #         StockRateID = stocktran.StockRateID
    #         Qty = stocktran.Qty
    #         stockRateIns = StockRate.objects.get(
    #             BranchID=BranchID, StockRateID=StockRateID, CompanyID=CompanyID)
    #         stockRateIns.Qty = converted_float(stockRateIns.Qty) - converted_float(Qty)
    #         stockRateIns.save()
    #         stocktran.IsActive = False
    #         stocktran.save()

    VoucherType = "OS"

    deleted_datas = data["deleted_data"]
    if deleted_datas:
        for deleted_Data in deleted_datas:
            deleted_pk = deleted_Data['unq_id']
            OpeningStockDetailsID_Deleted = deleted_Data['OpeningStockDetailsID']
            ProductID_Deleted = deleted_Data['ProductID']
            PriceListID_Deleted = deleted_Data['PriceListID']
            Rate_Deleted = deleted_Data['Rate']
            OpeningStockMasterID_Deleted = deleted_Data['OpeningStockMasterID']
            WarehouseID_Deleted = deleted_Data['WarehouseID']

            if not deleted_pk == '' or not deleted_pk == 0:
                if OpeningStockDetails.objects.filter(CompanyID=CompanyID, pk=deleted_pk).exists():
                    deleted_detail = OpeningStockDetails.objects.get(
                        CompanyID=CompanyID, pk=deleted_pk)
                    deleted_BatchCode = deleted_detail.BatchCode
                    deleted_batch = Batch.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, BatchCode=deleted_BatchCode).first()
                    if not StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchID=deleted_BatchCode).exclude(VoucherType="PI").exists():
                        deleted_batch.delete()
                    else:
                        MultiFactor = PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=PriceListID_Deleted).MultiFactor

                        qty_batch = converted_float(deleted_detail.Qty)
                        Qty_batch = converted_float(
                            MultiFactor) * converted_float(qty_batch)

                        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
                            batch_ins = Batch.objects.get(
                                CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode)
                            StockIn = batch_ins.StockIn
                            batch_ins.StockIn = converted_float(
                                StockIn) - converted_float(Qty_batch)
                            batch_ins.save()
                    deleted_detail.delete()

                    if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=OpeningStockMasterID_Deleted, VoucherDetailID=OpeningStockDetailsID_Deleted, ProductID=ProductID_Deleted, BranchID=BranchID, VoucherType="OS").exists():
                        stock_instances_delete = StockPosting.objects.filter(
                            CompanyID=CompanyID, VoucherMasterID=OpeningStockMasterID_Deleted, VoucherDetailID=OpeningStockDetailsID_Deleted, ProductID=ProductID_Deleted, BranchID=BranchID, VoucherType="OS")
                        stock_instances_delete.delete()
                        update_stock(CompanyID, BranchID,
                                        ProductID_Deleted)
                        
                   

            # if PriceList.objects.filter(CompanyID=CompanyID,ProductID=ProductID_Deleted,DefaultUnit=True).exists():
            #     priceList = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID_Deleted,DefaultUnit=True)
            #     MultiFactor = priceList.MultiFactor
            #     Cost = converted_float(Rate_Deleted) /  converted_float(MultiFactor)
            #     Ct = round(Cost,4)
            #     Cost_Deleted = str(Ct)

            #     if not deleted_pk == '' or not deleted_pk == 0:
            #         if OpeningStockDetails.objects.filter(CompanyID=CompanyID,pk=deleted_pk).exists():
            #             deleted_detail = OpeningStockDetails.objects.filter(CompanyID=CompanyID,pk=deleted_pk)
            #             deleted_detail.delete()

            #             if StockRate.objects.filter(CompanyID=CompanyID,ProductID=ProductID_Deleted,PriceListID=PriceListID_Deleted,Cost=Cost_Deleted,WareHouseID=WarehouseID_Deleted).exists():
            #                 stockRate_instance = StockRate.objects.get(CompanyID=CompanyID,ProductID=ProductID_Deleted,PriceListID=PriceListID_Deleted,Cost=Cost_Deleted,WareHouseID=WarehouseID_Deleted)
            #                 StockRateID = stockRate_instance.StockRateID
            #                 if StockTrans.objects.filter(CompanyID=CompanyID,DetailID=OpeningStockDetailsID_Deleted,MasterID=OpeningStockMasterID_Deleted,BranchID=BranchID,
            #                     VoucherType=VoucherType,IsActive=True,StockRateID=StockRateID).exists():
            #                     stockTrans_instance = StockTrans.objects.get(CompanyID=CompanyID,DetailID=OpeningStockDetailsID_Deleted,MasterID=OpeningStockMasterID_Deleted,BranchID=BranchID,
            #                         VoucherType=VoucherType,IsActive=True,StockRateID=StockRateID)
            #                     qty_in_stockTrans = stockTrans_instance.Qty
            #                     stockRate_instance.Qty = converted_float(stockRate_instance.Qty) - converted_float(qty_in_stockTrans)
            #                     stockRate_instance.save()
            #                     stockTrans_instance.IsActive = False
                        # stockTrans_instance.save()

    openingStockDetails = data["OpeningStockDetails"]

    for openingStockDetail in openingStockDetails:
        if openingStockDetail["ProductID"]:
            pk = openingStockDetail["unq_id"]
            detailID = openingStockDetail["detailID"]
            ProductID = openingStockDetail["ProductID"]
            Qty = openingStockDetail["Qty"]
            PriceListID = openingStockDetail["PriceListID"]
            Rate = openingStockDetail["Rate"]
            Amount = openingStockDetail["Amount"]
            try:
                BatchCode = openingStockDetail["BatchCode"]
            except:
                BatchCode = ""
                
            try:
                ManufactureDate = openingStockDetail['ManufactureDate']
            except:
                ManufactureDate = None

            try:
                ExpiryDate = openingStockDetail['ExpiryDate']
            except:
                ExpiryDate = None

            # priceList = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,DefaultUnit=True)

            # PriceListID_DefUnit = priceList.PriceListID
            # MultiFactor = priceList.MultiFactor

            # # PurchasePrice = priceList.PurchasePrice
            # # SalesPrice = priceList.SalesPrice

            # # qty = converted_float(FreeQty) + converted_float(Qty)

            # Qty = converted_float(MultiFactor) * converted_float(Qty)
            # Cost = converted_float(Rate) /  converted_float(MultiFactor)

            # Qy = round(Qty,4)
            # Qty = str(Qy)

            # Ct = round(Cost,4)
            # Cost = str(Ct)

            # princeList_instance = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,PriceListID=PriceListID_DefUnit,BranchID=BranchID)
            # PurchasePrice = princeList_instance.PurchasePrice
            # SalesPrice = princeList_instance.SalesPrice

            product_is_Service = Product.objects.get(
                CompanyID=CompanyID, ProductID=ProductID).is_Service
            MultiFactor = PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=PriceListID).MultiFactor
            PriceListID_DefUnit = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).PriceListID

            princeList_instance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID_DefUnit)
            PurchasePrice = princeList_instance.PurchasePrice
            SalesPrice = princeList_instance.SalesPrice

            # qty = converted_float(FreeQty) + converted_float(Qty)

            Qty = converted_float(MultiFactor) * converted_float(Qty)
            Cost = converted_float(Rate) / converted_float(MultiFactor)
            
            if ManufactureDate == "":
                ManufactureDate = None

            if ExpiryDate == "":
                ExpiryDate = None

            if ManufactureDate:
                ManufactureDate = FormatedDate(ManufactureDate)

            if ExpiryDate:
                ExpiryDate = FormatedDate(ExpiryDate)
            
            check_EnableProductBatchWise = get_GeneralSettings(CompanyID,BranchID, "EnableProductBatchWise")
            check_BatchCriteria = get_GeneralSettings(CompanyID,BranchID, "BatchCriteria")
            
            BatchCode, message = SetBatch(CompanyID, check_EnableProductBatchWise, check_BatchCriteria, BranchID, ProductID, PriceListID, SalesPrice, Rate,
                                            ExpiryDate, ManufactureDate, Qty, WarehouseID, today, CreatedUserID, BatchCode, "update", "PI")

            if not message == "":
                error_code = 11111
                errr = makingerror

            if detailID == 0:
                openingStockDetail_instance = OpeningStockDetails.objects.get(
                    CompanyID=CompanyID, pk=pk)
                OpeningStockDetailsID = openingStockDetail_instance.OpeningStockDetailsID

                log_instance = OpeningStockDetails_Log.objects.create(
                    TransactionID=OpeningStockDetailsID,
                    BranchID=BranchID,
                    OpeningStockMasterID=OpeningStockMasterID,
                    ProductID=ProductID,
                    Qty=Qty,
                    PriceListID=PriceListID,
                    Rate=Rate,
                    Amount=Amount,
                    Action=Action,
                    CompanyID=CompanyID,
                    BatchCode=BatchCode
                )

                openingStockDetail_instance.ProductID = ProductID
                openingStockDetail_instance.Qty = Qty
                openingStockDetail_instance.PriceListID = PriceListID
                openingStockDetail_instance.Rate = Rate
                openingStockDetail_instance.Amount = Amount
                openingStockDetail_instance.Action = Action
                openingStockDetail_instance.BatchCode = BatchCode
                openingStockDetail_instance.save()

                if product_is_Service == False:

                    pricelist, warehouse = get_ModelInstance(
                        CompanyID, BranchID, PriceListID, WarehouseID)
                    if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WarehouseID, VoucherMasterID=OpeningStockMasterID, VoucherDetailID=OpeningStockDetailsID, BranchID=BranchID, VoucherType="OS", ProductID=ProductID).exists():
                        stock_instance = StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WarehouseID, VoucherMasterID=OpeningStockMasterID,
                                                                        VoucherDetailID=OpeningStockDetailsID, BranchID=BranchID, VoucherType="OS", ProductID=ProductID).first()
                        stock_instance.Date = as_on_date
                        stock_instance.QtyIn = Qty
                        stock_instance.Action = Action
                        stock_instance.save()
                        update_stock(CompanyID, BranchID, ProductID)
                    else:
                        StockPostingID = get_auto_stockPostid(
                            StockPosting, BranchID, CompanyID)
                        StockPosting.objects.create(
                            StockPostingID=StockPostingID,
                            BranchID=BranchID,
                            Action=Action,
                            Date=as_on_date,
                            VoucherMasterID=OpeningStockMasterID,
                            VoucherDetailID=OpeningStockDetailsID,
                            VoucherType=VoucherType,
                            ProductID=ProductID,
                            BatchID=BatchID,
                            WareHouseID=WarehouseID,
                            QtyIn=Qty,
                            Rate=Cost,
                            PriceListID=PriceListID_DefUnit,
                            IsActive=IsActive,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                            pricelist=pricelist,
                            warehouse=warehouse
                        )

                        StockPosting_Log.objects.create(
                            TransactionID=StockPostingID,
                            BranchID=BranchID,
                            Action=Action,
                            Date=as_on_date,
                            VoucherMasterID=OpeningStockMasterID,
                            VoucherDetailID=OpeningStockDetailsID,
                            VoucherType=VoucherType,
                            ProductID=ProductID,
                            BatchID=BatchID,
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

                        update_stock(CompanyID, BranchID, ProductID)

            if detailID == 1:
                Action = "A"

                OpeningStockDetailsID = get_auto_id(
                    OpeningStockDetails, BranchID, CompanyID)

                log_instance = OpeningStockDetails_Log.objects.create(
                    TransactionID=OpeningStockDetailsID,
                    BranchID=BranchID,
                    OpeningStockMasterID=OpeningStockMasterID,
                    ProductID=ProductID,
                    Qty=Qty,
                    PriceListID=PriceListID,
                    Rate=Rate,
                    Amount=Amount,
                    Action=Action,
                    CompanyID=CompanyID,
                    BatchCode=BatchCode,
                )

                OpeningStockDetails.objects.create(
                    OpeningStockDetailsID=OpeningStockDetailsID,
                    BranchID=BranchID,
                    OpeningStockMasterID=OpeningStockMasterID,
                    ProductID=ProductID,
                    Qty=Qty,
                    PriceListID=PriceListID,
                    Rate=Rate,
                    Amount=Amount,
                    Action=Action,
                    CompanyID=CompanyID,
                    LogID=log_instance.ID,
                    BatchCode=BatchCode,
                )

                if product_is_Service == False:
                    pricelist, warehouse = get_ModelInstance(
                        CompanyID, BranchID, PriceListID, WarehouseID)

                    StockPostingID = get_auto_stockPostid(
                        StockPosting, BranchID, CompanyID)
                    StockPosting.objects.create(
                        StockPostingID=StockPostingID,
                        BranchID=BranchID,
                        Action=Action,
                        Date=as_on_date,
                        VoucherMasterID=OpeningStockMasterID,
                        VoucherDetailID=OpeningStockDetailsID,
                        VoucherType=VoucherType,
                        ProductID=ProductID,
                        BatchID=BatchID,
                        WareHouseID=WarehouseID,
                        QtyIn=Qty,
                        Rate=Cost,
                        PriceListID=PriceListID_DefUnit,
                        IsActive=IsActive,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                        pricelist=pricelist,
                        warehouse=warehouse
                    )

                    StockPosting_Log.objects.create(
                        TransactionID=StockPostingID,
                        BranchID=BranchID,
                        Action=Action,
                        Date=as_on_date,
                        VoucherMasterID=OpeningStockMasterID,
                        VoucherDetailID=OpeningStockDetailsID,
                        VoucherType=VoucherType,
                        ProductID=ProductID,
                        BatchID=BatchID,
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

                    update_stock(CompanyID, BranchID, ProductID)

            # priceList = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,DefaultUnit=True,BranchID=BranchID)

            # PriceListID = priceList.PriceListID
            # MultiFactor = priceList.MultiFactor

            # MultiFactor = PriceList.objects.get(
            #     CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).MultiFactor
            # PriceListID = PriceList.objects.get(
            #     CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True, BranchID=BranchID).PriceListID

            # princeList_instance = PriceList.objects.get(
            #     CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID, BranchID=BranchID)
            # PurchasePrice = princeList_instance.PurchasePrice
            # SalesPrice = princeList_instance.SalesPrice

            # # qty = converted_float(FreeQty) + converted_float(Qty)

            # Qty = converted_float(MultiFactor) * converted_float(Qty)
            # Cost = converted_float(Rate) / converted_float(MultiFactor)

            # Qy = round(Qty, 4)
            # Qty = str(Qy)

            # Ct = round(Cost, 4)
            # Cost = str(Ct)

            # if product_is_Service == False:
            #     VoucherType = "OS"
            #     StockPostingID = get_auto_stockPostid(
            #         StockPosting, BranchID, CompanyID)
            #     StockPosting.objects.create(
            #         StockPostingID=StockPostingID,
            #         BranchID=BranchID,
            #         Action=Action,
            #         Date=Date,
            #         VoucherMasterID=OpeningStockMasterID,
            #         VoucherType=VoucherType,
            #         ProductID=ProductID,
            #         BatchID=BatchID,
            #         WareHouseID=WarehouseID,
            #         QtyIn=Qty,
            #         Rate=Cost,
            #         PriceListID=PriceListID,
            #         IsActive=IsActive,
            #         CreatedDate=today,
            #         UpdatedDate=today,
            #         CreatedUserID=CreatedUserID,
            #         CompanyID=CompanyID,
            #     )

            #     StockPosting_Log.objects.create(
            #         TransactionID=StockPostingID,
            #         BranchID=BranchID,
            #         Action=Action,
            #         Date=Date,
            #         VoucherMasterID=OpeningStockMasterID,
            #         VoucherType=VoucherType,
            #         ProductID=ProductID,
            #         BatchID=BatchID,
            #         WareHouseID=WarehouseID,
            #         QtyIn=Qty,
            #         Rate=Cost,
            #         PriceListID=PriceListID,
            #         IsActive=IsActive,
            #         CreatedDate=today,
            #         UpdatedDate=today,
            #         CreatedUserID=CreatedUserID,
            #         CompanyID=CompanyID,
            #     )

            #     update_stock(CompanyID,BranchID,ProductID)

            # if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID).exists():
            #     stockRateInstance = StockRate.objects.filter(
            #         CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID).first()

            #     StockRateID = stockRateInstance.StockRateID
            #     stockRateInstance.Qty = converted_float(
            #         stockRateInstance.Qty) + converted_float(Qty)
            #     stockRateInstance.save()

            #     StockTransID = get_auto_StockTransID(
            #         StockTrans, BranchID, CompanyID)
            #     StockTrans.objects.create(
            #         StockTransID=StockTransID,
            #         BranchID=BranchID,
            #         VoucherType=VoucherType,
            #         StockRateID=StockRateID,
            #         DetailID=OpeningStockDetailsID,
            #         MasterID=OpeningStockMasterID,
            #         Qty=Qty,
            #         IsActive=IsActive,
            #         CompanyID=CompanyID,
            #     )
            # else:
            #     StockRateID = get_auto_StockRateID(
            #         StockRate, BranchID, CompanyID)
            #     StockRate.objects.create(
            #         StockRateID=StockRateID,
            #         BranchID=BranchID,
            #         BatchID=BatchID,
            #         PurchasePrice=PurchasePrice,
            #         SalesPrice=SalesPrice,
            #         Qty=Qty,
            #         Cost=Cost,
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
            #         DetailID=OpeningStockDetailsID,
            #         MasterID=OpeningStockMasterID,
            #         Qty=Qty,
            #         IsActive=IsActive,
            #         CompanyID=CompanyID,
            #     )

    # request , company, log_type, user, source, action, message, description
    # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'OpeningStocK',
    #              'Edit', 'OpeningStocK Updated successfully.', 'OpeningStocK Updated successfully.')
    response_data = {
        "StatusCode": 6000,
        "message": "Open Stock Updated Successfully!!!",
    }

    return Response(response_data, status=status.HTTP_200_OK)
    # except Exception as e:
    #     exc_type, exc_obj, exc_tb = sys.exc_info()
    #     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    #     err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
    #     response_data = {
    #         "StatusCode": 6001,
    #         "message": "some error occured..please try again"
    #     }

    #     activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'OpeningStocK',
    #                  'Edit', str(e), err_descrb)
    #     return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def openingStocks(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if OpeningStockMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():

            instances = OpeningStockMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)

            serialized = OpeningStockMasterRestSerializer(instances, many=True, context={"CompanyID": CompanyID,
                                                                                         "PriceRounding": PriceRounding})

            # request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'OpeningStocK', 'List View',
            #              'OpeningStocK List Viewed successfully.', 'OpeningStocK List Viewed successfully.')
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'OpeningStocK', 'List View',
            #              'OpeningStocK List Viewed Failed.', 'OpeningStocK List Not Found Under this Branch.')
            response_data = {
                "StatusCode": 6001,
                "message": "Opening Stock Master not found in this branch."
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch you enterd is not valid."
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def opening_stock_pagination(request):
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
            opening_stock_object = OpeningStockMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)

            opening_stock_sort_pagination = list_pagination(
                opening_stock_object,
                items_per_page,
                page_number
            )
            purchase_return_serializer = OpeningStockMaster1RestSerializer(
                opening_stock_sort_pagination,
                many=True,
                context={"request": request, "CompanyID": CompanyID,
                         "PriceRounding": PriceRounding}
            )
            data = purchase_return_serializer.data
            if not data == None:
                response_data = {
                    "StatusCode": 6000,
                    "data": data,
                    "count": len(opening_stock_object)
                }
            else:
                response_data = {
                    "StatusCode": 6001
                }

            return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def openingStock(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    instance = None

    if OpeningStockMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = OpeningStockMaster.objects.get(CompanyID=CompanyID, pk=pk)
        serialized = OpeningStockMasterRestSerializer(instance, context={"CompanyID": CompanyID,
                                                                         "PriceRounding": PriceRounding})

        # request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'OpeningStocK', 'View',
        #              'OpeningStocK Single Page Viewed successfully.', 'OpeningStocK Single Page Viewed successfully.')
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        # request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'OpeningStocK', 'View',
        #              'OpeningStocK Single Page Failed.', 'OpeningStocK List Not Found Under this Branch.')
        response_data = {
            "StatusCode": 6001,
            "message": "Opening Stock Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_openingStockDetails(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    instance = None
    if OpeningStockDetails.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = OpeningStockDetails.objects.get(CompanyID=CompanyID, pk=pk)
        OpeningStockDetailsID = instance.OpeningStockDetailsID
        BranchID = instance.BranchID
        OpeningStockMasterID = instance.OpeningStockMasterID
        ProductID = instance.ProductID
        Qty = instance.Qty
        PriceListID = instance.PriceListID
        Rate = instance.Rate
        Amount = instance.Amount
        Action = "D"

        instance.delete()

        OpeningStockDetails_Log.objects.create(
            TransactionID=OpeningStockDetailsID,
            BranchID=BranchID,
            OpeningStockMasterID=OpeningStockMasterID,
            ProductID=ProductID,
            Qty=Qty,
            PriceListID=PriceListID,
            Rate=Rate,
            Amount=Amount,
            Action=Action,
            CompanyID=CompanyID,
        )

        # request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'OpeningStocK',
                     'Delete', 'OpeningStocK Deleted successfully.', 'OpeningStocK Deleted successfully..')
        response_data = {
            "StatusCode": 6000,
            "message": "Opening Stock Details Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Opening Stock Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_openingStockMaster(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    try:
        selecte_ids = data['selecte_ids']
    except:
        selecte_ids = []
    instance = None
    if selecte_ids:
        if OpeningStockMaster.objects.filter(CompanyID=CompanyID, pk__in=selecte_ids).exists():
            instances = OpeningStockMaster.objects.filter(pk__in=selecte_ids)
    else:
        if OpeningStockMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
            instances = OpeningStockMaster.objects.filter(pk=pk)

    if instances:
        for instance in instances:
            OpeningStockMasterID = instance.OpeningStockMasterID
            BranchID = instance.BranchID
            VoucherNo = instance.VoucherNo
            Date = instance.Date
            WarehouseID = instance.WarehouseID
            Notes = instance.Notes
            TotalQty = instance.TotalQty
            GrandTotal = instance.GrandTotal
            IsActive = instance.IsActive
            Action = "D"

            OpeningStockMaster_Log.objects.create(
                TransactionID=OpeningStockMasterID,
                BranchID=BranchID,
                VoucherNo=VoucherNo,
                Date=Date,
                WarehouseID=WarehouseID,
                Notes=Notes,
                TotalQty=TotalQty,
                GrandTotal=GrandTotal,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )

            instance.delete()

            if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=OpeningStockMasterID, BranchID=BranchID, VoucherType="OS").exists():

                stockPostingInstances = StockPosting.objects.filter(
                    CompanyID=CompanyID, VoucherMasterID=OpeningStockMasterID, BranchID=BranchID, VoucherType="OS")

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
                    update_stock(CompanyID, BranchID, ProductID)

            detail_instances = OpeningStockDetails.objects.filter(
                CompanyID=CompanyID, OpeningStockMasterID=OpeningStockMasterID)

            for detail_instance in detail_instances:
                OpeningStockDetailsID = detail_instance.OpeningStockDetailsID
                BranchID = detail_instance.BranchID
                OpeningStockMasterID = detail_instance.OpeningStockMasterID
                ProductID = detail_instance.ProductID
                Qty = detail_instance.Qty
                PriceListID = detail_instance.PriceListID
                Rate = detail_instance.Rate
                Amount = detail_instance.Amount
                BatchCode = detail_instance.BatchCode
                
                BatchCode = detail_instance.BatchCode
                update_stock(CompanyID, BranchID, ProductID)
                if CompanyID.business_type.Name == "Pharmacy":
                    if not StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchID=BatchCode).exclude(VoucherType="PI").exists():
                        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
                            Batch.objects.filter(
                                CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).delete()
                    else:
                        MultiFactor = PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=PriceListID).MultiFactor

                        qty_batch = converted_float(Qty)
                        Qty_batch = converted_float(MultiFactor) * converted_float(qty_batch)

                        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
                            batch_ins = Batch.objects.get(
                                CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode)
                            StockIn = batch_ins.StockIn
                            batch_ins.StockIn = converted_float(
                                StockIn) - converted_float(Qty_batch)
                            batch_ins.save()
                else:
                    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
                        batch_ins = Batch.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode)
                        StockIn = batch_ins.StockIn
                        batch_ins.StockIn = converted_float(StockIn) - converted_float(Qty)
                        batch_ins.save()

                

                OpeningStockDetails_Log.objects.create(
                    TransactionID=OpeningStockDetailsID,
                    BranchID=BranchID,
                    OpeningStockMasterID=OpeningStockMasterID,
                    ProductID=ProductID,
                    Qty=Qty,
                    PriceListID=PriceListID,
                    Rate=Rate,
                    Amount=Amount,
                    Action=Action,
                    CompanyID=CompanyID,
                )

                detail_instance.delete()

                # if StockTrans.objects.filter(CompanyID=CompanyID, DetailID=OpeningStockDetailsID, MasterID=OpeningStockMasterID, BranchID=BranchID, VoucherType="OS", IsActive=True).exists():
                #     stockTrans_instances = StockTrans.objects.filter(
                #         CompanyID=CompanyID, DetailID=OpeningStockDetailsID, MasterID=OpeningStockMasterID, BranchID=BranchID, VoucherType="OS", IsActive=True)

                #     for i in stockTrans_instances:
                #         stockRateID = i.StockRateID
                #         i.IsActive = False
                #         i.save()

                #         stockRate_instance = StockRate.objects.get(
                #             CompanyID=CompanyID, StockRateID=stockRateID, BranchID=BranchID)
                #         stockRate_instance.Qty = converted_float(
                #             stockRate_instance.Qty) - converted_float(i.Qty)
                #         stockRate_instance.save()

        # request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'OpeningStocK',
                     'Delete', 'OpeningStocK Deleted successfully.', 'OpeningStocK Deleted successfully..')
        response_data = {
            "StatusCode": 6000,
            "title": "Success",
            "message": "Opening Stock Master Deleted Successfully!"
        }
    else:
        # request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'OpeningStocK',
                     'Delete', 'OpeningStocK Deleted Failed.', 'OpeningStocK Not Found Under this Branch.')
        response_data = {
            "StatusCode": 6001,
            "title": "Failed",
            "message": "Opening Stock Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def openingStocks_filter(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    filterValue = data['filterValue']
    GroupID = data['GroupID']

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
        product_instances = None
        productsForAllBranches = get_branch_settings(
            CompanyID, "productsForAllBranches")
        if filterValue == 2:
            if productsForAllBranches == False or productsForAllBranches == "False":
                product_instances = Product.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)
            else:
                product_instances = Product.objects.filter(
                    CompanyID=CompanyID)
            # if product_instances:
            #     product_instances = Product.objects.filter(
            #         CompanyID=CompanyID, BranchID=BranchID)
        else:
            if GroupID:
                if productsForAllBranches == False or productsForAllBranches == "False":
                    product_instances = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductGroupID=GroupID)
                else:
                    product_instances = Product.objects.filter(
                        CompanyID=CompanyID, ProductGroupID=GroupID)
                # if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductGroupID=GroupID).exists():
                #     product_instances = Product.objects.filter(
                #         CompanyID=CompanyID, BranchID=BranchID, ProductGroupID=GroupID)

        if product_instances:
            if page_number and items_per_page:
                party_sort_pagination = list_pagination(
                    product_instances,
                    items_per_page,
                    page_number
                )
            serialized = OpeningStockFilterSerializer(party_sort_pagination, many=True, context={
                                                      "CompanyID": CompanyID, "PriceRounding": PriceRounding})
            orderdDict = serialized.data
            jsnDatas = convertOrderdDict(orderdDict)
            TotalQty = 0
            GrandTotal = 0
            product_list = []
            for i in jsnDatas:
                TotalQty += i['Qty']
                GrandTotal += i['Amount']
                product_list.append({
                    "ProductID": i['ProductID'],
                    "ProductName": i['ProductName'],
                })
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "TotalQty": TotalQty,
                "GrandTotal": GrandTotal,
                "product_list": product_list,
                "count": len(product_instances),
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Products Not Found"
            }
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def openingStocks_report(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    WarehouseIds = data['WarehouseIds']
    try:
        page_number = data['page_no']
    except:
        page_number = ""

    try:
        items_per_page = data['items_per_page']
    except:
        items_per_page = ""

    serialized1 = ListSerializerforReport(data=request.data)

    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        FromDate = serialized1.data['FromDate']
        ToDate = serialized1.data['ToDate']
        test = OpeningStockMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID)
        print(test)
        if OpeningStockMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID,Date__gte=FromDate,Date__lte=ToDate).exists():
            instances = OpeningStockMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID,Date__gte=FromDate,Date__lte=ToDate)
            if WarehouseIds:
                instances = instances.filter(WarehouseID__in=WarehouseIds)

            # Pagination Function START
            counted_datas = instances.count()

            sale_sort_pagination = list_pagination(
                instances,
                items_per_page,
                page_number
            )
            count_divided_datas = math.ceil(
                converted_float(counted_datas) / items_per_page)
            # Pagination Function END

            serialized = OpeningStockReportSerializer(sale_sort_pagination, many=True, context={"CompanyID": CompanyID,
                                                                                                "PriceRounding": PriceRounding})
            # Adding Total
            orderdDict = serialized.data
            jsnDatas = convertOrderdDict(orderdDict)

            # tot_qty = 0
            # tot_grand_total = 0
            # for i in jsnDatas:
            #     qty = i['TotalQty']
            #     grand_total = i['GrandTotal']
            #     tot_qty += qty
            #     tot_grand_total += grand_total

            if count_divided_datas == page_number:
                tot_qty = instances.aggregate(Sum('TotalQty'))[
                    'TotalQty__sum']
                tot_grand_total = instances.aggregate(Sum('GrandTotal'))[
                    'GrandTotal__sum']
                total_dic = {
                    'VoucherNo': "",
                    'Notes': "",
                    'WareHouseName': "Total",
                    'TotalQty': tot_qty,
                    'GrandTotal': tot_grand_total,
                }
                jsnDatas.append(total_dic)

            response_data = {
                "StatusCode": 6000,
                "data": jsnDatas,
                "count": len(instances),
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Opening Stock Master not found in this branch."
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch you enterd is not valid."
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def openingStocks_xls_read(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    excel_files = data['excel_files']

    arr = []
    arr1 = []

    print(len(excel_files), "COUNTexcel_files")
    count = 0
    for i in excel_files:
        arr.append(i["ProductCode"])
        count += 1
        print(count, "UVAIS", i['ProductCode'])

    print("nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn")
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
        product_instances = None
        ProductCode_list = [d['ProductCode'] for d in excel_files]

        print(len(ProductCode_list), "SHAHEEEKAA THAMARASHERY")
        Quantity_ProductCode_list = []
        for d in excel_files:
            a = Product.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductCode=d['ProductCode']).first()
            print(a, d['ProductName'], d['ProductCode'])
            try:
                qty = d['Qty']
            except:
                qty = 0
            try:
                code = d['ProductCode']
            except:
                code = ''

            dic = {
                'Qty': qty,
                'ProductCode': str(code),
            }
            Quantity_ProductCode_list.append(dic)

        if get_BranchSettings(CompanyID, "productsForAllBranches"):
            pricelist_list = PriceList.objects.filter(
                CompanyID=CompanyID)
            product_list = Product.objects.filter(CompanyID=CompanyID)
        else:
            pricelist_list = PriceList.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
            product_list = Product.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)

        # if pricelist_list.exists():
        #     autobarcode_product_id_list = pricelist_list.filter(
        #         AutoBarcode__in=AutoBarcode_list).values_list('ProductID', flat="True")

        if product_list.exists():
            product_instances = product_list.filter(
                ProductCode__in=ProductCode_list)

        if product_instances:
            if page_number and items_per_page:
                party_sort_pagination = list_pagination(
                    product_instances,
                    items_per_page,
                    page_number
                )
            serialized = OpeningStockFilterSerializer(party_sort_pagination, many=True, context={
                                                      "CompanyID": CompanyID, "PriceRounding": PriceRounding})
            jsnDatas = serialized.data
            TotalQty = 0
            GrandTotal = 0
            product_list = []
            count = 0
            for i in jsnDatas:

                Qty = 0
                if i['ProductCode']:
                    try:
                        qty = [
                            item['Qty'] for item in excel_files if item['ProductCode'] == i['ProductCode']]
                        i['Qty'] = qty[0]
                    except:
                        qty = [0]
                    try:
                        rate = [
                            item['Rate'] for item in excel_files if item['ProductCode'] == i['ProductCode']]
                        i['Rate'] = rate[0]
                    except:
                        rate = [0]

                i['Amount'] = converted_float(i['Qty']) * converted_float(i['Rate'])
                TotalQty += i['Qty']
                GrandTotal += i['Amount']
                product_list.append({
                    "ProductID": i['ProductID'],
                    "ProductName": i['ProductName'],
                })
                count += 1
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "TotalQty": TotalQty,
                "GrandTotal": GrandTotal,
                "product_list": product_list,
                "count": len(product_instances),
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Products Not Found"
            }
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def create_openingStock_master_data(request):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            CreatedUserID = data['CreatedUserID']

            today = datetime.datetime.now()
            BranchID = data["BranchID"]
            VoucherNo = data["VoucherNo"]
            Date = data["Date"]
            WarehouseID = data["WarehouseID"]
            Notes = data["Notes"]
            TotalQty = data["TotalQty"]
            GrandTotal = data["GrandTotal"]
            IsActive = data["IsActive"]
            BatchID = data["BatchID"]

            Action = "A"

            VoucherType = "OS"

            # VoucherNo Updated
            try:
                PreFix = data['PreFix']
            except:
                PreFix = "OS"

            try:
                Seperator = data['Seperator']
            except:
                Seperator = ""

            try:
                InvoiceNo = data['InvoiceNo']
            except:
                InvoiceNo = 1

            # checking voucher number already exist
            VoucherNoLow = VoucherNo.lower()
            is_voucherExist = False
            insts = OpeningStockMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
            if insts:
                for i in insts:
                    voucher_no = i.VoucherNo
                    voucherNo = voucher_no.lower()
                    if VoucherNoLow == voucherNo:
                        is_voucherExist = True

            check_VoucherNoAutoGenerate = False
            is_OpeningStockOK = True

            if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="VoucherNoAutoGenerate").exists():
                check_VoucherNoAutoGenerate = GeneralSettings.objects.get(
                    BranchID=BranchID, CompanyID=CompanyID, SettingsType="VoucherNoAutoGenerate").SettingsValue

            if is_voucherExist == True and check_VoucherNoAutoGenerate == "True":
                VoucherNo = get_Genrate_VoucherNo(
                    OpeningStockMaster, BranchID, CompanyID, "OS")
                is_OpeningStockOK = True
            elif is_voucherExist == False:
                is_OpeningStockOK = True
            else:
                is_OpeningStockOK = False

            if is_OpeningStockOK:
                update_voucher_table(
                    CompanyID, CreatedUserID, VoucherType, PreFix, Seperator, InvoiceNo)
                OpeningStockMasterID = get_auto_idMaster(
                    OpeningStockMaster, BranchID, CompanyID)

                OpeningStockMaster_Log.objects.create(
                    TransactionID=OpeningStockMasterID,
                    BranchID=BranchID,
                    VoucherNo=VoucherNo,
                    Date=Date,
                    WarehouseID=WarehouseID,
                    Notes=Notes,
                    TotalQty=TotalQty,
                    GrandTotal=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )
                OpeningStockMaster.objects.create(
                    OpeningStockMasterID=OpeningStockMasterID,
                    BranchID=BranchID,
                    VoucherNo=VoucherNo,
                    Date=Date,
                    WarehouseID=WarehouseID,
                    Notes=Notes,
                    TotalQty=TotalQty,
                    GrandTotal=GrandTotal,
                    IsActive=IsActive,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    Action=Action,
                    CompanyID=CompanyID,
                )

                response_data = {
                    "StatusCode": 6000,
                    "message": "Open Stock created Successfully!!!",
                    "OpeningStockMasterID": OpeningStockMasterID,
                }

                return Response(response_data, status=status.HTTP_200_OK)

            else:
                # request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'OpeningStocK',
                             'Create', 'OpeningStocK created Failed.', 'VoucherNo already exist')
                response_data = {
                    "StatusCode": 6001,
                    "message": "VoucherNo already exist.Please Change Your Prefix!"
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

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'OpeningStocK',
                     'Create', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def create_openingStock_details_data(request):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            CreatedUserID = data['CreatedUserID']

            today = datetime.datetime.now()
            BranchID = data["BranchID"]
            OpeningStockMasterID = data["OpeningStockMasterID"]
            Action = "A"

            BatchID = 1
            IsActive = True

            master_instances = OpeningStockMaster.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, OpeningStockMasterID=OpeningStockMasterID)

            openingStockDetails = data["OpeningStockDetails"]
            for openingStockDetail in openingStockDetails:
                if openingStockDetail["ProductID"]:
                    ProductID = openingStockDetail["ProductID"]
                    Qty = openingStockDetail["Qty"]
                    PriceListID = openingStockDetail["PriceListID"]
                    Rate = openingStockDetail["Rate"]
                    Amount = openingStockDetail["Amount"]

                    OpeningStockDetailsID = get_auto_id(
                        OpeningStockDetails, BranchID, CompanyID)

                    log_instance = OpeningStockDetails_Log.objects.create(
                        TransactionID=OpeningStockDetailsID,
                        BranchID=BranchID,
                        OpeningStockMasterID=OpeningStockMasterID,
                        ProductID=ProductID,
                        Qty=Qty,
                        PriceListID=PriceListID,
                        Rate=Rate,
                        Amount=Amount,
                        Action=Action,
                        CompanyID=CompanyID,
                    )
                    OpeningStockDetails.objects.create(
                        OpeningStockDetailsID=OpeningStockDetailsID,
                        BranchID=BranchID,
                        OpeningStockMasterID=OpeningStockMasterID,
                        ProductID=ProductID,
                        Qty=Qty,
                        PriceListID=PriceListID,
                        Rate=Rate,
                        Amount=Amount,
                        Action=Action,
                        CompanyID=CompanyID,
                        LogID=log_instance.ID
                    )

                    # priceList = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,DefaultUnit=True,BranchID=BranchID)

                    # PriceListID = priceList.PriceListID
                    # MultiFactor = priceList.MultiFactor
                    MultiFactor = PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=PriceListID).MultiFactor
                    PriceListID = PriceList.objects.get(
                        CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).PriceListID

                    princeList_instance = PriceList.objects.get(
                        CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID)
                    PurchasePrice = princeList_instance.PurchasePrice
                    SalesPrice = princeList_instance.SalesPrice

                    Qty = converted_float(MultiFactor) * converted_float(Qty)
                    Cost = converted_float(Rate) / converted_float(MultiFactor)

                    product_is_Service = Product.objects.get(
                        CompanyID=CompanyID, ProductID=ProductID).is_Service

                    if product_is_Service == False:
                        pricelist, warehouse = get_ModelInstance(
                            CompanyID, BranchID, PriceListID, master_instances.WarehouseID)

                        VoucherType = "OS"
                        StockPostingID = get_auto_stockPostid(
                            StockPosting, BranchID, CompanyID)
                        StockPosting.objects.create(
                            StockPostingID=StockPostingID,
                            BranchID=BranchID,
                            Action=Action,
                            Date=master_instances.Date,
                            VoucherMasterID=OpeningStockMasterID,
                            VoucherDetailID=OpeningStockDetailsID,
                            VoucherType=VoucherType,
                            ProductID=ProductID,
                            BatchID=BatchID,
                            WareHouseID=master_instances.WarehouseID,
                            QtyIn=Qty,
                            Rate=Cost,
                            PriceListID=PriceListID,
                            IsActive=IsActive,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                            pricelist=pricelist,
                            warehouse=warehouse
                        )

                        StockPosting_Log.objects.create(
                            TransactionID=StockPostingID,
                            BranchID=BranchID,
                            Action=Action,
                            Date=master_instances.Date,
                            VoucherMasterID=OpeningStockMasterID,
                            VoucherDetailID=OpeningStockDetailsID,
                            VoucherType=VoucherType,
                            ProductID=ProductID,
                            BatchID=BatchID,
                            WareHouseID=master_instances.WarehouseID,
                            QtyIn=Qty,
                            Rate=Cost,
                            PriceListID=PriceListID,
                            IsActive=IsActive,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )

                        update_stock(CompanyID, BranchID, ProductID)

        response_data = {
            "StatusCode": 6000,
            "message": "Open Stock created Successfully!!!",
            "OpeningStockMasterID": OpeningStockMasterID
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again",
            "OpeningStockMasterID": OpeningStockMasterID
        }

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'OpeningStocK',
                     'Create', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def openingStock_web_export_excel(request):
    # content-type of response
    CompanyID = request.GET.get("CompanyID")
    BranchID = request.GET.get("BranchID")

    UserID = request.GET.get("UserID")
    PriceRounding = request.GET.get("PriceRounding")
    details = request.GET.get("details")
    if details:
        details = json.loads(details)

    print('CompanyID,BranchID,FromDate,ToDate')
    response = HttpResponse(content_type='application/ms-excel')

    # decide file name
    response['Content-Disposition'] = 'attachment; filename="Opening Stock.xls"'

    # creating workbook
    wb = xlwt.Workbook(encoding='utf-8')

    # ===============  adding Opening Stock sheet ============
    ws = wb.add_sheet("Opening Stock")

    openingStock_columns = ['ProductCode',
                            'AutoBarcode', 'ProductName', 'Unit', 'Qty', 'Rate']
    # write column headers in sheet

    # xl sheet styles

    center = Alignment()
    center.horz = Alignment.HORZ_CENTER

    # header font
    font = xlwt.Font()
    font.bold = True
    font.height = 11 * 20

    sub_header_style = xlwt.XFStyle()
    sub_header_style.font = font

    value_decimal_style = xlwt.XFStyle()
    value_decimal_style.num_format_str = '0.00'

    row_num = 0
    for openingStock_col_num in range(len(openingStock_columns)):
        ws.write(row_num, openingStock_col_num,
                 openingStock_columns[openingStock_col_num], sub_header_style)

    data_row = 2

    row_num = 1

    # instance = OpeningStockMaster.objects.filter(
    #     CompanyID=CompanyID, BranchID=BranchID)
    # ids = instance.values_list('OpeningStockMasterID', flat=True)
    # details = OpeningStockDetails.objects.filter(
    #     CompanyID=CompanyID, BranchID=BranchID, OpeningStockMasterID__in=ids)
    if details:
        for i in details:
            UnitName = ""
            AutoBarcode = ""
            PriceListID = i["PriceListID"]
            if PriceList.objects.filter(CompanyID=CompanyID,PriceListID=PriceListID).exists():
                price_ins = PriceList.objects.filter(
                    CompanyID=CompanyID, PriceListID=PriceListID).first()
                UnitID = price_ins.UnitID
                AutoBarcode = price_ins.AutoBarcode
                if Unit.objects.filter(CompanyID=CompanyID,UnitID=UnitID).exists():
                    UnitName = Unit.objects.filter(
                        CompanyID=CompanyID, UnitID=UnitID).first().UnitName
            row_num = row_num + 1
            ws.write(row_num, 0, i["ProductCode"])
            ws.write(row_num, 1, AutoBarcode)
            ws.write(row_num, 2, i["ProductName"])
            ws.write(row_num, 3, UnitName)
            ws.write(row_num, 4, i["Qty"])
            ws.write(row_num, 5, i["Rate"])

    wb.save(response)
    return response
