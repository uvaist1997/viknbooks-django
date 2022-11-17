from brands.models import Activity_Log, StockManagementDetails_Log,StockManagementDetails,StockManagementMaster_Log,StockManagementMaster,Product, StockAdjustmentMaster, StockAdjustmentMaster_Log, StockAdjustmentDetails, StockAdjustmentDetails_Log, ExcessStockMaster, ExcessStockMaster_Log, ExcessStockDetails,\
    ExcessStockDetails_Log, PriceList, StockPosting, StockPosting_Log, StockRate, StockTrans, ShortageStockMaster, ShortageStockMaster_Log, ShortageStockDetails, ShortageStockDetails_Log, Batch, GeneralSettings
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db import transaction, IntegrityError
from api.v9.stockManagements.serializers import StockManagementSerializer
from api.v9.brands.serializers import ListSerializer
from api.v9.stockAdjustments.functions import generate_serializer_errors, get_VoucherNo
from rest_framework import status
from api.v9.stockManagements.functions import get_stock_type,get_auto_StockDetailsID,get_auto_StockMasterID
import datetime
from main.functions import converted_float, get_ModelInstance, get_company, activity_log,update_voucher_table,get_GeneralSettings
from api.v9.stockPostings.functions import get_auto_excessMasterID, get_auto_excessDetailsID, get_auto_shortageMasterID, get_auto_shortageDetailsID
from api.v9.purchases.functions import get_auto_StockRateID, get_auto_StockTransID
from api.v9.sales.functions import get_auto_stockPostid
from api.v9.products.functions import update_stock
import re
import sys
import os
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from api.v9.sales.functions import SetBatchInStockManagement


def call_paginator_all(model_object, page_number, items_per_page):
    paginator = Paginator(model_object, items_per_page)
    content = paginator.page(page_number)
    return content


def list_pagination(list_value, items_per_page, page_no):
    paginator_object = Paginator(list_value, items_per_page)
    get_value = paginator_object.page(page_no).object_list
    return get_value


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def create_stockManagements(request):
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
            try:
                TotalExcessOrShortage = converted_float(data['TotalExcessOrShortage'])
            except:
                TotalExcessOrShortage = 0
            
            try:
                TotalExcessAmount = converted_float(
                    data['TotalExcessAmount'])
            except:
                TotalExcessAmount = 0
                
            try:
                TotalShortageAmount = converted_float(
                    data['TotalShortageAmount'])
            except:
                TotalShortageAmount = 0
                
            TotalQty = converted_float(data['TotalQty'])
            GrandTotal = converted_float(data['GrandTotal'])
            # StockType = data['StockType']
            # VoucherType = get_stock_type(StockType)
            VoucherType = "SM"

            # VoucherNo Updated
            try:
                PreFix = data['PreFix']
            except:
                PreFix = "SM"

            try:
                Seperator = data['Seperator']
            except:
                Seperator = ""

            try:
                InvoiceNo = data['InvoiceNo']
            except:
                InvoiceNo = 1

            Action = "A"

            if not StockManagementMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherNo__iexact=VoucherNo).exists():
                update_voucher_table(
                    CompanyID, CreatedUserID, VoucherType, PreFix, Seperator, InvoiceNo)
                StockMasterID = get_auto_StockMasterID(
                    StockManagementMaster, BranchID, CompanyID)

                StockManagementMaster_Log.objects.create(
                    TransactionID=StockMasterID,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    Date=Date,
                    Notes=Notes,
                    WarehouseID=WarehouseID,
                    TotalQty=TotalQty,
                    TotalExcessOrShortage=TotalExcessOrShortage,
                    TotalExcessAmount=TotalExcessAmount,
                    TotalShortageAmount=TotalShortageAmount,
                    GrandTotal=GrandTotal,
                    CreatedDate=today,
                    LastUPDDate=today,
                    CreatedUserID=CreatedUserID,
                    LastUPDUserID=CreatedUserID,
                )
                StockManagementMaster.objects.create(
                    CompanyID=CompanyID,
                    StockMasterID=StockMasterID,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    Date=Date,
                    Notes=Notes,
                    WarehouseID=WarehouseID,
                    TotalQty=TotalQty,
                    TotalExcessOrShortage=TotalExcessOrShortage,
                    TotalExcessAmount=TotalExcessAmount,
                    TotalShortageAmount=TotalShortageAmount,
                    GrandTotal=GrandTotal,
                    CreatedDate=today,
                    LastUPDDate=today,
                    CreatedUserID=CreatedUserID,
                    LastUPDUserID=CreatedUserID
                )

                Details = data["Details"]
                for d in Details:
                    ProductID = d['ProductID']
                    PriceListID = d['PriceListID']
                    Qty = converted_float(d['Qty'])
                    Rate = converted_float(d['Rate'])
                    Stock = converted_float(d['Stock'])
                    BatchCode = d['BatchCode']
                    Excess_or_Shortage = converted_float(d['Excess_or_Shortage'])
                    
                    BatchType = "SM"
                    QtyIn = 0
                    QtyOut = 0
                    if converted_float(Excess_or_Shortage) > 0:
                        QtyIn = Excess_or_Shortage
                        BatchType = "ES"
                        BatchQty = QtyIn
                    elif converted_float(Excess_or_Shortage) < 0:
                        QtyOut = abs(Excess_or_Shortage)
                        BatchType = "SS"
                        BatchQty = QtyOut
                    
                    check_EnableProductBatchWise = False
                    MultiFactor = PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=PriceListID).MultiFactor
                    def_pricelists = PriceList.objects.get(
                        CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)

                    PriceListID_DefUnit = def_pricelists.PriceListID
                    PurchasePrice = def_pricelists.PurchasePrice
                    SalesPrice = def_pricelists.SalesPrice

                    Batch_Qty = converted_float(MultiFactor) * converted_float(Qty)
                    Batch_Excess_or_Shortage = converted_float(MultiFactor) * converted_float(Excess_or_Shortage)
                    Batch_Cost = converted_float(Rate) / converted_float(MultiFactor)
                    
                    if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
                        check_EnableProductBatchWise = GeneralSettings.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").SettingsValue
                    
                    # QtyIn = 0
                    # QtyOut = 0
                    # BatchType = ""
                    # BatchQty = ""
                    # if StockType == "0":
                    #     QtyIn = Batch_Qty
                    #     BatchType = "ES"
                    #     BatchQty = QtyIn
                    # elif StockType == "1":
                    #     QtyOut = Batch_Qty
                    #     BatchType = "SS"
                    #     BatchQty = QtyOut
                    # elif StockType == "2":
                    #     if converted_float(Batch_Excess_or_Shortage) > 0:
                    #         QtyIn = Batch_Excess_or_Shortage
                    #         BatchType = "ES"
                    #         BatchQty = QtyIn
                    #     elif converted_float(Batch_Excess_or_Shortage) < 0:
                    #         QtyOut = Batch_Excess_or_Shortage
                    #         BatchType = "SS"
                    #         BatchQty = QtyOut
                            
                    check_BatchCriteria = get_GeneralSettings(CompanyID,BranchID, "BatchCriteria")
                    if check_EnableProductBatchWise == True or check_EnableProductBatchWise == "True":
                        BatchCode = SetBatchInStockManagement(CompanyID, BranchID, Batch_Cost,SalesPrice,ProductID,PriceListID, BatchQty,WarehouseID, BatchCode,CreatedUserID,today, BatchType,check_BatchCriteria)
                            
                    StockDetailsID = get_auto_StockDetailsID(
                        StockManagementDetails, BranchID, CompanyID)

                    log_instances = StockManagementDetails_Log.objects.create(
                        TransactionID=StockDetailsID,
                        BranchID=BranchID,
                        Action=Action,
                        StockMasterID=StockMasterID,
                        ProductID=ProductID,
                        PriceListID=PriceListID,
                        Qty=Qty,
                        Excess_or_Shortage=Excess_or_Shortage,
                        CreatedDate=today,
                        LastUPDDate=today,
                        CreatedUserID=CreatedUserID,
                        LastUPDUserID=CreatedUserID,
                        CostPerItem=Rate,
                        BatchCode=BatchCode,
                        CompanyID=CompanyID,
                        Stock=Stock
                    )
                    
                    StockManagementDetails.objects.create(
                        CompanyID=CompanyID,
                        StockDetailsID=StockDetailsID,
                        BranchID=BranchID,
                        Action=Action,
                        StockMasterID=StockMasterID,
                        ProductID=ProductID,
                        PriceListID=PriceListID,
                        Qty=Qty,
                        Excess_or_Shortage=Excess_or_Shortage,
                        CreatedDate=today,
                        LastUPDDate=today,
                        CreatedUserID=CreatedUserID,
                        LastUPDUserID=CreatedUserID,
                        CostPerItem=Rate,
                        BatchCode=BatchCode,
                        LogID=log_instances.ID,
                        Stock=Stock
                    )

                    product_is_Service = Product.objects.get(
                        CompanyID=CompanyID, ProductID=ProductID).is_Service
                    check_EnableProductBatchWise = False
                    if product_is_Service == False:
                        MultiFactor = PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=PriceListID).MultiFactor
                        def_pricelists = PriceList.objects.get(
                            CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)

                        PriceListID_DefUnit = def_pricelists.PriceListID
                        PurchasePrice = def_pricelists.PurchasePrice
                        SalesPrice = def_pricelists.SalesPrice

                        Qty = converted_float(MultiFactor) * converted_float(Qty)
                        Excess_or_Shortage = converted_float(MultiFactor) * converted_float(Excess_or_Shortage)
                        Cost = converted_float(Rate) / converted_float(MultiFactor)
                        
                        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
                            check_EnableProductBatchWise = GeneralSettings.objects.get(
                                CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").SettingsValue

                        StockPostingID = get_auto_stockPostid(
                            StockPosting, BranchID, CompanyID)

                        pricelist, warehouse = get_ModelInstance(
                            CompanyID, BranchID, PriceListID, WarehouseID)
                        
                        # QtyIn = 0
                        # QtyOut = 0
                        # BatchType = ""
                        # BatchQty = ""
                        # if StockType == "0":
                        #     QtyIn = Qty
                        #     BatchType = "ES"
                        #     BatchQty = QtyIn
                        # elif StockType == "1":
                        #     QtyOut = Qty
                        #     BatchType = "SS"
                        #     BatchQty = QtyOut
                        # elif StockType == "2":
                        #     if converted_float(Excess_or_Shortage) > 0:
                        #         QtyIn = Excess_or_Shortage
                        #         BatchType = "ES"
                        #         BatchQty = QtyIn
                        #     elif converted_float(Excess_or_Shortage) < 0:
                        #         QtyOut = abs(Excess_or_Shortage)
                        #         BatchType = "SS"
                        #         BatchQty = QtyOut
                                
                        
                        if converted_float(QtyIn) > 0 or converted_float(QtyOut) > 0:
                            StockPosting.objects.create(
                                StockPostingID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=Date,
                                VoucherMasterID=StockMasterID,
                                VoucherDetailID=StockDetailsID,
                                VoucherType=BatchType,
                                ProductID=ProductID,
                                WareHouseID=WarehouseID,
                                QtyIn=QtyIn,
                                QtyOut=QtyOut,
                                Rate=Cost,
                                PriceListID=PriceListID,
                                IsActive=True,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                                pricelist=pricelist,
                                BatchID=BatchCode,
                                warehouse=warehouse

                            )
                            StockPosting_Log.objects.create(
                                TransactionID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=Date,
                                VoucherMasterID=StockMasterID,
                                VoucherDetailID=StockDetailsID,
                                VoucherType=BatchType,
                                ProductID=ProductID,
                                WareHouseID=WarehouseID,
                                QtyIn=QtyIn,
                                QtyOut=QtyOut,
                                Rate=Cost,
                                PriceListID=PriceListID,
                                IsActive=True,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                                BatchID=BatchCode,
                            )

                            update_stock(CompanyID, BranchID, ProductID)
                            
                            

                response_data = {
                    "StatusCode": 6000,
                    "message": "Stock Management Created Successfully!!!"
                }

                return Response(response_data, status=status.HTTP_200_OK)

            else:
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Stock Management',
                                'Create', 'Stock Management create failed.', 'VoucherNo Already exists.')
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
            "message": "some error occured..please try again",
            "err_descrb": err_descrb
        }

        activity_id = activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Stock Management',
                     'Create', str(e), err_descrb)
        body_params = str(request.data)
        Activity_Log.objects.filter(
            id=activity_id).update(body_params=body_params)
        return Response(response_data, status=status.HTTP_200_OK)
    
    

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def edit_stockManagement(request,pk):
    try:
        with transaction.atomic():
            today = datetime.datetime.now()
            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            CreatedUserID = data['CreatedUserID']
            BranchID = data['BranchID']
            # VoucherNo = data['VoucherNo']
            Date = data['Date']
            Notes = data['Notes']
            WarehouseID = data['WarehouseID']
            TotalQty = data['TotalQty']
            GrandTotal = data['GrandTotal']
            try:
                TotalExcessOrShortage = data['TotalExcessOrShortage']
            except:
                TotalExcessOrShortage = 0
                
            try:
                TotalExcessAmount = converted_float(
                    data['TotalExcessAmount'])
            except:
                TotalExcessAmount = 0

            try:
                TotalShortageAmount = converted_float(
                    data['TotalShortageAmount'])
            except:
                TotalShortageAmount = 0
            # StockType = data['StockType']
            stockManagement_instance = StockManagementMaster.objects.get(
                CompanyID=CompanyID, pk=pk)

            StockMasterID = stockManagement_instance.StockMasterID
            VoucherNo = stockManagement_instance.VoucherNo
            BranchID = stockManagement_instance.BranchID
            # StockType = stockManagement_instance.StockType
            # VoucherType = get_stock_type(StockType)
            VoucherType = "SM"

            Action = "M"
            
            StockManagementMaster_Log.objects.create(
                TransactionID=StockMasterID,
                BranchID=BranchID,
                Action=Action,
                VoucherNo=VoucherNo,
                Date=Date,
                Notes=Notes,
                WarehouseID=WarehouseID,
                TotalQty=TotalQty,
                GrandTotal=GrandTotal,
                TotalExcessOrShortage=TotalExcessOrShortage,
                TotalExcessAmount=TotalExcessAmount,
                TotalShortageAmount=TotalShortageAmount,
                CreatedDate=today,
                LastUPDDate=today,
                CreatedUserID=CreatedUserID,
                LastUPDUserID=CreatedUserID,
            )
            
            if StockManagementDetails.objects.filter(CompanyID=CompanyID,StockMasterID=StockMasterID,BranchID=BranchID).exists():
                stock_manage_details = StockManagementDetails.objects.filter(CompanyID=CompanyID,StockMasterID=StockMasterID,BranchID=BranchID)
                for i in stock_manage_details:
                    BatchCode = i.BatchCode
                    Qty = i.Qty
                    instance_MultiFactor = PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=i.PriceListID).MultiFactor

                    instance_Qty = converted_float(
                        instance_MultiFactor) * converted_float(Qty)
                    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
                        batch_ins = Batch.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode)
                        StockOut = batch_ins.StockOut
                        if converted_float(i.Excess_or_Shortage) > 0:
                            batch_ins.StockIn = converted_float(
                            batch_ins.StockIn) - converted_float(i.Excess_or_Shortage)
                        elif converted_float(i.Excess_or_Shortage) < 0:
                            batch_ins.StockOut = converted_float(
                            batch_ins.StockOut) - converted_float(i.Excess_or_Shortage)
                        # if StockType == "0":
                        #     batch_ins.StockIn = converted_float(
                        #         batch_ins.StockIn) - converted_float(instance_Qty)
                        # elif StockType == "1":
                        #     batch_ins.StockOut = converted_float(
                        #         batch_ins.StockOut) - converted_float(instance_Qty)
                        # elif StockType == "2":
                        #     if converted_float(i.Excess_or_Shortage) > 0:
                        #         batch_ins.StockIn = converted_float(
                        #         batch_ins.StockIn) - converted_float(i.Excess_or_Shortage)
                        #     elif converted_float(i.Excess_or_Shortage) < 0:
                        #         batch_ins.StockOut = converted_float(
                        #         batch_ins.StockOut) - converted_float(i.Excess_or_Shortage)
                        batch_ins.save()
                        
                    if converted_float(i.Excess_or_Shortage) > 0:
                        BatchType = "ES"
                    elif converted_float(i.Excess_or_Shortage) < 0:
                        BatchType = "SS"
                    if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=StockMasterID, VoucherDetailID=i.StockDetailsID, ProductID=i.ProductID, BranchID=BranchID, VoucherType=BatchType).exists():
                        stock_inst = StockPosting.objects.filter(
                            CompanyID=CompanyID, VoucherMasterID=StockMasterID, VoucherDetailID=i.StockDetailsID, ProductID=i.ProductID, BranchID=BranchID, VoucherType=BatchType).first().delete()
                        # if StockType == "0":
                        #     stock_inst.QtyIn = converted_float(
                        #         stock_inst.QtyIn) - converted_float(instance_Qty)
                        # elif StockType == "1":
                        #     stock_inst.QtyOut = converted_float(
                        #         stock_inst.QtyOut) - converted_float(instance_Qty)
                        # elif StockType == "2":
                        #     if converted_float(i.Excess_or_Shortage) > 0:
                        #         stock_inst.QtyIn = converted_float(
                        #         stock_inst.QtyIn) - converted_float(i.Excess_or_Shortage)
                        #     elif converted_float(i.Excess_or_Shortage) < 0:
                        #         stock_inst.QtyOut = converted_float(
                        #         stock_inst.QtyOut) - abs(converted_float(i.Excess_or_Shortage))
                        # stock_inst.save()
                        update_stock(CompanyID, BranchID, i.ProductID)
            
            stockManagement_instance.Date = Date
            stockManagement_instance.Notes = Notes
            stockManagement_instance.WarehouseID = WarehouseID
            stockManagement_instance.TotalQty = TotalQty
            stockManagement_instance.GrandTotal = GrandTotal
            stockManagement_instance.TotalExcessOrShortage = TotalExcessOrShortage
            stockManagement_instance.TotalExcessAmount = TotalExcessAmount
            stockManagement_instance.TotalShortageAmount = TotalShortageAmount
            stockManagement_instance.save()
            
            deleted_datas = data["deleted_data"]
            if deleted_datas:
                for deleted_Data in deleted_datas:
                    deleted_pk = deleted_Data['unq_id']
                    StockDetailsID = deleted_Data['StockDetailsID']
                    ProductID_Deleted = deleted_Data['ProductID']
                    PriceListID_Deleted = deleted_Data['PriceListID']
                    Rate_Deleted = deleted_Data['Rate']
                    StockMasterID_Deleted = deleted_Data['StockMasterID']
                    WarehouseID_Deleted = deleted_Data['WarehouseID']
                    if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID_Deleted, DefaultUnit=True).exists():
                        priceList = PriceList.objects.get(
                            CompanyID=CompanyID, ProductID=ProductID_Deleted, DefaultUnit=True)
                        MultiFactor = priceList.MultiFactor
                        Cost = converted_float(Rate_Deleted) / converted_float(MultiFactor)
                        Ct = round(Cost, 4)
                        Cost_Deleted = str(Ct)

                        if not deleted_pk == '' or not deleted_pk == 0:
                            # StockType_deleted = StockManagementMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,StockMasterID=StockMasterID).first().StockType
                            # VoucherType_deleted = get_stock_type(StockType_deleted)
                            if StockManagementDetails.objects.filter(CompanyID=CompanyID, pk=deleted_pk).exists():
                                deleted_detail = StockManagementDetails.objects.get(
                                    CompanyID=CompanyID, pk=deleted_pk)
                                deleted_BatchCode = deleted_detail.BatchCode
                                print(deleted_BatchCode)
                                qty_batch = converted_float(deleted_detail.Qty)
                                Qty_batch = converted_float(
                                    MultiFactor) * converted_float(qty_batch)
                                delete_Excess_or_Shortage = converted_float(
                                    MultiFactor) * converted_float(deleted_detail.Excess_or_Shortage)
                                
                                if converted_float(delete_Excess_or_Shortage) > 0:
                                    BatchType = "ES"
                                elif converted_float(delete_Excess_or_Shortage) < 0:
                                    BatchType = "SS"

                                # if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=deleted_BatchCode).exists():
                                #     batch_ins = Batch.objects.get(
                                #     CompanyID=CompanyID, BranchID=BranchID, BatchCode=deleted_BatchCode)
                                #     StockOut = batch_ins.StockOut
                                #     if StockType_deleted == "0":
                                #         batch_ins.StockIn = converted_float(
                                #             batch_ins.StockIn) - converted_float(Qty_batch)
                                #     elif StockType_deleted == "1":
                                #         batch_ins.StockOut = converted_float(
                                #             batch_ins.StockOut) - converted_float(Qty_batch)
                                #     if StockType_deleted == "2":
                                #         if converted_float(delete_Excess_or_Shortage) > 0:
                                #             batch_ins.StockIn = converted_float(
                                #             batch_ins.StockIn) - converted_float(delete_Excess_or_Shortage)
                                #         elif converted_float(delete_Excess_or_Shortage) < 0:
                                #             batch_ins.StockOut = converted_float(
                                #             batch_ins.StockOut) - converted_float(delete_Excess_or_Shortage)
                                #     batch_ins.save()
                                
                                deleted_detail.delete()
                                if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=StockMasterID_Deleted, VoucherDetailID=StockDetailsID, ProductID=ProductID_Deleted, BranchID=BranchID, VoucherType=BatchType).exists():
                                    stock_instances_delete = StockPosting.objects.filter(
                                        CompanyID=CompanyID, VoucherMasterID=StockMasterID_Deleted, VoucherDetailID=StockDetailsID, ProductID=ProductID_Deleted, BranchID=BranchID, VoucherType=BatchType)
                                    stock_instances_delete.delete()
                                    update_stock(
                                        CompanyID, BranchID, ProductID_Deleted)


            Details = data["Details"]
            for d in Details:
                pk = d['unq_id']
                detailID = d['detailID']
                ProductID = d['ProductID']
                PriceListID = d['PriceListID']
                BatchCode = d['BatchCode']
                Qty = converted_float(d['Qty'])
                Rate = converted_float(d['Rate'])
                Stock = converted_float(d['Stock'])
                Excess_or_Shortage = converted_float(d['Excess_or_Shortage'])
                product_is_Service = Product.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID).is_Service
                
                check_EnableProductBatchWise = False
                if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
                    check_EnableProductBatchWise = GeneralSettings.objects.get(
                        CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").SettingsValue
                check_BatchCriteria = get_GeneralSettings(CompanyID,BranchID, "BatchCriteria")
                MultiFactor = PriceList.objects.get(
                    CompanyID=CompanyID, PriceListID=PriceListID).MultiFactor
                def_pricelists = PriceList.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)

                PriceListID_DefUnit = def_pricelists.PriceListID
                PurchasePrice = def_pricelists.PurchasePrice
                SalesPrice = def_pricelists.SalesPrice

                Stock_Qty = converted_float(MultiFactor) * converted_float(Qty)
                Stock_Excess_or_Shortage = converted_float(MultiFactor) * converted_float(Excess_or_Shortage)
                Cost = converted_float(Rate) / converted_float(MultiFactor)
                QtyIn = 0
                QtyOut = 0
                if converted_float(Excess_or_Shortage) > 0:
                    QtyIn = Excess_or_Shortage
                    BatchType = "ES"
                    BatchQty = QtyIn
                elif converted_float(Excess_or_Shortage) < 0:
                    QtyOut = abs(Excess_or_Shortage)
                    BatchType = "SS"
                    BatchQty = QtyOut
                
                
                if detailID == 0:
                    if check_EnableProductBatchWise == True or check_EnableProductBatchWise == "True":
                        BatchCode = SetBatchInStockManagement(CompanyID, BranchID, Rate,SalesPrice,ProductID,PriceListID, BatchQty,WarehouseID, BatchCode,CreatedUserID,today, BatchType,check_BatchCriteria)
                    
                    stockManageDetail_instance = StockManagementDetails.objects.get(
                        CompanyID=CompanyID, pk=pk)
                    StockDetailsID = stockManageDetail_instance.StockDetailsID
                    
                    log_instances = StockManagementDetails_Log.objects.create(
                        TransactionID=StockDetailsID,
                        BranchID=BranchID,
                        Action=Action,
                        StockMasterID=StockMasterID,
                        ProductID=ProductID,
                        PriceListID=PriceListID,
                        Qty=Qty,
                        Excess_or_Shortage=Excess_or_Shortage,
                        CreatedDate=today,
                        LastUPDDate=today,
                        CreatedUserID=CreatedUserID,
                        LastUPDUserID=CreatedUserID,
                        CostPerItem=Rate,
                        CompanyID=CompanyID,
                        BatchCode=BatchCode,
                        Stock=Stock
                    )
                    
                    if converted_float(stockManageDetail_instance.Excess_or_Shortage) > 0:
                        BatchType = "ES"
                    elif converted_float(stockManageDetail_instance.Excess_or_Shortage) < 0:
                        BatchType = "SS"
                    
                    stockManageDetail_instance.ProductID = ProductID
                    stockManageDetail_instance.PriceListID = PriceListID
                    stockManageDetail_instance.BatchCode = BatchCode
                    stockManageDetail_instance.Qty = Qty
                    stockManageDetail_instance.CostPerItem = Rate
                    stockManageDetail_instance.Rate = Rate
                    stockManageDetail_instance.Stock = Stock
                    stockManageDetail_instance.Excess_or_Shortage = Excess_or_Shortage
                    stockManageDetail_instance.save()
                    
                    check_EnableProductBatchWise = False
                    if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
                        check_EnableProductBatchWise = GeneralSettings.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").SettingsValue
                    
                    if product_is_Service == False:
                        MultiFactor = PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=PriceListID).MultiFactor
                        def_pricelists = PriceList.objects.get(
                            CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)

                        PriceListID_DefUnit = def_pricelists.PriceListID
                        PurchasePrice = def_pricelists.PurchasePrice
                        SalesPrice = def_pricelists.SalesPrice

                        Stock_Qty = converted_float(MultiFactor) * converted_float(Qty)
                        Stock_Excess_or_Shortage = converted_float(MultiFactor) * converted_float(Excess_or_Shortage)
                        Cost = converted_float(Rate) / converted_float(MultiFactor)
                        # if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WarehouseID, VoucherMasterID=StockMasterID, VoucherDetailID=StockDetailsID, BranchID=BranchID, VoucherType=BatchType, ProductID=ProductID).exists():
                        #     stock_instance = StockPosting.objects.filter(
                        #         CompanyID=CompanyID, WareHouseID=WarehouseID, VoucherMasterID=StockMasterID, VoucherDetailID=StockDetailsID, BranchID=BranchID, VoucherType=BatchType, ProductID=ProductID).first()
                            
                        #     if converted_float(Stock_Excess_or_Shortage) > 0:
                        #         stock_instance.QtyIn = converted_float(
                        #             stock_instance.QtyIn) + converted_float(Stock_Excess_or_Shortage)
                        #         BatchType = "ES"
                        #         BatchQty = Stock_Excess_or_Shortage
                        #         print(BatchQty)
                        #     elif converted_float(Stock_Excess_or_Shortage) < 0:
                        #         stock_instance.QtyOut = converted_float(stock_instance.QtyOut) + converted_float(Stock_Excess_or_Shortage)
                        #         BatchType = "SS"
                        #         BatchQty = Stock_Excess_or_Shortage
                                
                        #     stock_instance.Date = Date
                        #     stock_instance.Action = Action
                        #     stock_instance.save()
                        # else:
                        QtyIn = 0
                        QtyOut = 0
                        BatchQty = ""
                        BatchType = "ES"
                        BatchQty = 0
                        
                        if converted_float(Excess_or_Shortage) > 0:
                            QtyIn = Excess_or_Shortage
                            BatchType = "ES"
                            BatchQty = QtyIn
                        elif converted_float(Excess_or_Shortage) < 0:
                            QtyOut = abs(Excess_or_Shortage)
                            BatchType = "SS"
                            BatchQty = QtyOut
                        StockPostingID = get_auto_stockPostid(
                            StockPosting, BranchID, CompanyID)
                        pricelist, warehouse = get_ModelInstance(
                            CompanyID, BranchID, PriceListID_DefUnit, WarehouseID)

                        StockPosting.objects.create(
                            StockPostingID=StockPostingID,
                            BranchID=BranchID,
                            Action=Action,
                            Date=Date,
                            VoucherMasterID=StockMasterID,
                            VoucherDetailID=StockDetailsID,
                            VoucherType=BatchType,
                            ProductID=ProductID,
                            BatchID=BatchCode,
                            WareHouseID=WarehouseID,
                            QtyIn=QtyIn,
                            QtyOut=QtyOut,
                            Rate=Cost,
                            PriceListID=PriceListID_DefUnit,
                            IsActive=True,
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
                            Date=Date,
                            VoucherMasterID=StockMasterID,
                            VoucherDetailID=StockDetailsID,
                            VoucherType=BatchType,
                            ProductID=ProductID,
                            BatchID=BatchCode,
                            WareHouseID=WarehouseID,
                            QtyIn=QtyIn,
                            QtyOut=QtyOut,
                            Rate=Cost,
                            PriceListID=PriceListID_DefUnit,
                            IsActive=True,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )

                    update_stock(CompanyID, BranchID, ProductID)
                        
                if detailID == 1:
                    Action = "A"
                    if check_EnableProductBatchWise == True or check_EnableProductBatchWise == "True":
                        BatchCode = SetBatchInStockManagement(CompanyID, BranchID, Cost,SalesPrice,ProductID,PriceListID, BatchQty,WarehouseID, BatchCode,CreatedUserID,today, BatchType,check_BatchCriteria)
                    StockDetailsID = get_auto_StockDetailsID(
                        StockManagementDetails, BranchID, CompanyID)
                    log_instances = StockManagementDetails_Log.objects.create(
                        TransactionID=StockDetailsID,
                        BranchID=BranchID,
                        Action=Action,
                        StockMasterID=StockMasterID,
                        ProductID=ProductID,
                        PriceListID=PriceListID,
                        BatchCode=BatchCode,
                        Qty=Qty,
                        Excess_or_Shortage=Excess_or_Shortage,
                        CreatedDate=today,
                        LastUPDDate=today,
                        CreatedUserID=CreatedUserID,
                        LastUPDUserID=CreatedUserID,
                        CostPerItem=Rate,
                        Stock=Stock,
                        CompanyID=CompanyID
                    )
                    StockManagementDetails.objects.create(
                        CompanyID=CompanyID,
                        StockDetailsID=StockDetailsID,
                        BranchID=BranchID,
                        Action=Action,
                        StockMasterID=StockMasterID,
                        ProductID=ProductID,
                        PriceListID=PriceListID,
                        BatchCode=BatchCode,
                        Qty=Qty,
                        Excess_or_Shortage=Excess_or_Shortage,
                        CreatedDate=today,
                        LastUPDDate=today,
                        CreatedUserID=CreatedUserID,
                        LastUPDUserID=CreatedUserID,
                        CostPerItem=Rate,
                        Stock=Stock,
                        LogID=log_instances.ID
                    )


                    StockPostingID = get_auto_stockPostid(
                        StockPosting, BranchID, CompanyID)

                    pricelist, warehouse = get_ModelInstance(
                        CompanyID, BranchID, PriceListID, WarehouseID)
                    
                    QtyIn = 0
                    QtyOut = 0
                    BatchType = ""
                    BatchQty = ""
                    if converted_float(Excess_or_Shortage) > 0:
                        QtyIn = Excess_or_Shortage
                        BatchType = "ES"
                        BatchQty = QtyIn
                    elif converted_float(Excess_or_Shortage) < 0:
                        QtyOut = abs(Excess_or_Shortage)
                        BatchType = "SS"
                        BatchQty = QtyOut
                    
                    if converted_float(QtyIn) > 0 or converted_float(QtyOut) > 0:
                        StockPosting.objects.create(
                            StockPostingID=StockPostingID,
                            BranchID=BranchID,
                            Action=Action,
                            Date=Date,
                            VoucherMasterID=StockMasterID,
                            VoucherDetailID=StockDetailsID,
                            VoucherType=BatchType,
                            ProductID=ProductID,
                            WareHouseID=WarehouseID,
                            QtyIn=QtyIn,
                            QtyOut=QtyOut,
                            Rate=Cost,
                            BatchID=BatchCode,
                            PriceListID=PriceListID,
                            IsActive=True,
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
                            Date=Date,
                            VoucherMasterID=StockMasterID,
                            VoucherDetailID=StockDetailsID,
                            VoucherType=BatchType,
                            ProductID=ProductID,
                            WareHouseID=WarehouseID,
                            QtyIn=QtyIn,
                            QtyOut=QtyOut,
                            Rate=Cost,
                            BatchID=BatchCode,
                            PriceListID=PriceListID,
                            IsActive=True,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )

                        update_stock(CompanyID, BranchID, ProductID)
                        
            response_data = {
                "StatusCode": 6000,
                "message": "Stock Management Updated Successfully!!!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again",
            "err_descrb": err_descrb
        }

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Stock Management',
                     'Edit', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)
    
    
    
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def stockManagement_pagination(request):
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
            stockManagement_object = StockManagementMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID).order_by('-StockMasterID')

            sale_sort_pagination = list_pagination(
                stockManagement_object,
                items_per_page,
                page_number
            )
            sale_serializer = StockManagementSerializer(
                sale_sort_pagination,
                many=True,
                context={"request": request, "CompanyID": CompanyID,
                         "PriceRounding": PriceRounding}
            )
            data = sale_serializer.data
            if not data == None:
                response_data = {
                    "StatusCode": 6000,
                    "data": data,
                    "count": len(stockManagement_object)
                }
            else:
                response_data = {
                    "StatusCode": 6001
                }

            return Response(response_data, status=status.HTTP_200_OK)
    
    
    
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_stockManagement(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    try:
        selecte_ids = data['selecte_ids']
    except:
        selecte_ids = []

    today = datetime.datetime.now()
    instances = None
    if selecte_ids:
        if StockManagementMaster.objects.filter(CompanyID=CompanyID, pk__in=selecte_ids).exists():
            instances = StockManagementMaster.objects.filter(pk__in=selecte_ids)
    else:
        if StockManagementMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
            instances = StockManagementMaster.objects.filter(pk=pk)

    if instances:
        for instance in instances:
            StockMasterID = instance.StockMasterID
            BranchID = instance.BranchID
            # StockType = instance.StockType
            VoucherNo = instance.VoucherNo
            Date = instance.Date
            Notes = instance.Notes
            WarehouseID = instance.WarehouseID
            TotalQty = instance.TotalQty
            GrandTotal = instance.GrandTotal
            TotalExcessOrShortage = instance.TotalExcessOrShortage
            TotalExcessAmount = instance.TotalExcessAmount
            TotalShortageAmount = instance.TotalShortageAmount

            Action = "D"

            StockManagementMaster_Log.objects.create(
                TransactionID=StockMasterID,
                BranchID=BranchID,
                VoucherNo=VoucherNo,
                Date=Date,
                Action=Action,
                # StockType=StockType,
                Notes=Notes,
                WarehouseID=WarehouseID,
                TotalQty=TotalQty,
                GrandTotal=GrandTotal,
                TotalExcessOrShortage=TotalExcessOrShortage,
                TotalExcessAmount=TotalExcessAmount,
                TotalShortageAmount=TotalShortageAmount,
                CreatedDate=today,
                LastUPDDate=today,
                CreatedUserID=CreatedUserID,
                LastUPDUserID=CreatedUserID,
            )
            
            VoucherType = ""
            # if StockType == "0":
            #     VoucherType = "ES"
            # elif StockType == "1":
            #     VoucherType = "SS"
            # elif StockType == "2":
            VoucherType = "SA"
            if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=StockMasterID, BranchID=BranchID, VoucherType=VoucherType).exists():
                stockPostingInstances = StockPosting.objects.filter(
                    CompanyID=CompanyID, VoucherMasterID=StockMasterID, BranchID=BranchID, VoucherType=VoucherType)
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

            detail_instances = StockManagementDetails.objects.filter(
                CompanyID=CompanyID, StockMasterID=StockMasterID, BranchID=BranchID)

            for detail_instance in detail_instances:
                StockDetailsID = detail_instance.StockDetailsID
                BranchID = detail_instance.BranchID
                StockMasterID = detail_instance.StockMasterID
                ProductID = detail_instance.ProductID
                PriceListID = detail_instance.PriceListID
                Qty = detail_instance.Qty
                BatchCode = detail_instance.BatchCode
                Excess_or_Shortage = detail_instance.Excess_or_Shortage
                CostPerItem = detail_instance.CostPerItem

                update_stock(CompanyID, BranchID, ProductID)

                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
                    batch_ins = Batch.objects.get(
                        CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode)
                    MultiFactor = PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=PriceListID).MultiFactor

                    qty_batch = converted_float(Qty)
                    Qty_batch = converted_float(MultiFactor) * converted_float(qty_batch)
                    qty_Excess_or_Shortage = converted_float(MultiFactor) * converted_float(Excess_or_Shortage)
                    # if StockType == "0":
                    #     StockIn = batch_ins.StockIn
                    #     batch_ins.StockIn = converted_float(StockIn) - converted_float(Qty_batch)
                    # elif StockType == "1":
                    #     StockOut = batch_ins.StockOut
                    #     batch_ins.StockOut = converted_float(StockOut) - converted_float(Qty_batch)
                    # elif StockType == "2":
                    if converted_float(Excess_or_Shortage) > 0:
                        StockIn = batch_ins.StockIn
                        batch_ins.StockIn = converted_float(StockIn) - converted_float(qty_Excess_or_Shortage)
                    elif converted_float(Excess_or_Shortage) < 0:
                        StockOut = batch_ins.StockOut
                        batch_ins.StockOut = converted_float(StockOut) - converted_float(qty_Excess_or_Shortage)
                    batch_ins.save()

            

                StockManagementDetails_Log.objects.create(
                    TransactionID=StockDetailsID,
                    BranchID=BranchID,
                    Action=Action,
                    StockMasterID=StockMasterID,
                    ProductID=ProductID,
                    PriceListID=PriceListID,
                    Qty=Qty,
                    Excess_or_Shortage=Excess_or_Shortage,
                    CostPerItem=CostPerItem,
                    CreatedDate=today,
                    LastUPDDate=today,
                )

                detail_instance.delete()
            instance.delete()

        # request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Stock Management',
                     'Deleted', 'Stock Management Deleted successfully.', 'Stock Management Deleted successfully')

        response_data = {
            "StatusCode": 6000,
            "title": "Success",
            "message": "Stock Management Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "title": "Failed",
            "message": "Stock Management Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def view_stockManagement(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    instance = None
    if StockManagementMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = StockManagementMaster.objects.get(CompanyID=CompanyID, pk=pk)
        serialized = StockManagementSerializer(
            instance, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding, })

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Stock Management Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)