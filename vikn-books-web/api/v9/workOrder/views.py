from brands.models import VoucherNoTable, PurchaseMaster, PurchaseMaster_Log, PurchaseDetails, PurchaseDetails_Log, StockPosting, LedgerPosting, StockPosting_Log,\
    LedgerPosting_Log, PurchaseDetailsDummy, StockRate, PriceList, StockTrans, ProductGroup, Brand, Unit, Warehouse, PurchaseReturnMaster, OpeningStockMaster, GeneralSettings, Product, WorkOrderMaster, WorkOrderMaster_Log, Batch, WorkOrderDetails, WorkOrderDetails_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v9.purchases.serializers import PurchaseMasterSerializer, PurchaseMasterRestSerializer, PurchaseDetailsSerializer,\
    PurchaseDetailsRestSerializer, PurchaseMasterReportSerializer, PurchaseMasterForReturnSerializer
from api.v9.workOrder import serializers
from api.v9.brands.serializers import ListSerializer
from api.v9.purchases.functions import generate_serializer_errors
from api.v9.products.functions import get_auto_AutoBatchCode
from rest_framework import status
from api.v9.sales.serializers import ListSerializerforReport
from api.v9.workOrder.functions import get_auto_id, get_auto_idMaster, get_auto_StockRateID, get_auto_StockTransID
from api.v9.sales.functions import get_auto_stockPostid
from api.v9.accountLedgers.functions import get_auto_LedgerPostid
import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from main.functions import converted_float, get_ModelInstance, get_company, activity_log
from api.v9.purchaseReturns.serializers import PurchaseReturnMasterRestSerializer
import re
import sys
import os
from django.db.models import Max
from django.db.models import Q, Prefetch
from api.v9.sales.functions import get_Genrate_VoucherNo
from django.db import transaction, IntegrityError
from main.functions import update_voucher_table
from api.v9.products.functions import get_auto_AutoBatchCode, update_stock


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def create_workorder(request):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data['CompanyID']
            CreatedUserID = data['CreatedUserID']
            PriceRounding = data['PriceRounding']
            CompanyID = get_company(CompanyID)

            today = datetime.datetime.now()
            BranchID = data['BranchID']
            VoucherNo = data['VoucherNo']
            Date = data['Date']
            WareHouseID = data['WareHouseID']
            Notes = data['Notes']
            ProductID = data['ProductID']
            ProductQty = data['ProductQty']
            CostPerPrice = data['CostPerPrice']
            UnitPrice = data['BatchSalesPrice']
            BatchPriceListID = data['PriceListID']
            Amount = data['Amount']
            TotalQty = data['TotalQty']
            GrandTotal = data['GrandTotal']
            IsActive = data['IsActive']
            ManufactureDate = data['ManufactureDate']
            ExpiryDate = data['ExpiryDate']
            BatchPurchasePrice = data['BatchPurchasePrice']
            BatchSalesPrice = data['BatchSalesPrice']
            BatchCode = data['BatchCode']
            is_inclusive = data['is_inclusive']
            InclusivePriceBatch = data['InclusivePriceBatch']

            Action = "A"

            VoucherType = "WO"

            # VoucherNo Updated
            try:
                PreFix = data['PreFix']
            except:
                PreFix = "WO"

            try:
                Seperator = data['Seperator']
            except:
                Seperator = ""

            try:
                InvoiceNo = data['InvoiceNo']
            except:
                InvoiceNo = 1

            def max_id():
                general_settings_id = GeneralSettings.objects.filter(
                    CompanyID=CompanyID).aggregate(Max('GeneralSettingsID'))
                general_settings_id = general_settings_id.get(
                    'GeneralSettingsID__max', 0)
                general_settings_id += 1
                return general_settings_id

            try:
                ExpiryDays = data['ExpiryDays']
                is_except = False
            except:
                ExpiryDays = False
                is_except = True

            if is_except == False:
                if not GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ExpiryDays").exists():
                    GeneralSettings.objects.create(
                        CompanyID=CompanyID,
                        GeneralSettingsID=max_id(),
                        SettingsType="ExpiryDays",
                        SettingsValue=ExpiryDays,
                        BranchID=BranchID, GroupName="Inventory",
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        Action=Action
                    )
                else:
                    GeneralSettings.objects.filter(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        SettingsType="ExpiryDays"
                    ).update(
                        SettingsValue=ExpiryDays,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        Action=Action
                    )

            VoucherType = "WO"
            BatchID = 1

            if is_inclusive == True:
                BatchSalesPrice = str(InclusivePriceBatch)
            else:
                BatchSalesPrice = str(UnitPrice)

            BatchPurchasePrice = str(BatchPurchasePrice)

            MultiFactor = PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=BatchPriceListID, BranchID=BranchID).MultiFactor

            # qty_batch = converted_float(FreeQty) + converted_float(ProductQty)
            Qty_batch = converted_float(MultiFactor) * converted_float(ProductQty)

            # checking voucher number already exist
            VoucherNoLow = VoucherNo.lower()
            is_voucherExist = False
            insts = WorkOrderMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
            if insts:
                for i in insts:
                    voucher_no = i.VoucherNo
                    voucherNo = voucher_no.lower()
                    if VoucherNoLow == voucherNo:
                        is_voucherExist = True

            check_VoucherNoAutoGenerate = False
            is_WorkOrderOK = True

            if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="VoucherNoAutoGenerate").exists():
                check_VoucherNoAutoGenerate = GeneralSettings.objects.get(
                    BranchID=BranchID, CompanyID=CompanyID, SettingsType="VoucherNoAutoGenerate").SettingsValue

            if is_voucherExist == True and check_VoucherNoAutoGenerate == "True":
                VoucherNo = get_Genrate_VoucherNo(
                    WorkOrderMaster, BranchID, CompanyID, "WO")
                is_WorkOrderOK = True
            elif is_voucherExist == False:
                is_WorkOrderOK = True
            else:
                is_WorkOrderOK = False

            if is_WorkOrderOK:
                WorkOrderMasterID = get_auto_idMaster(
                    WorkOrderMaster, BranchID, CompanyID)

                check_CreateBatchForWorkOrder = False
                if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="CreateBatchForWorkOrder").exists():
                    check_CreateBatchForWorkOrder = GeneralSettings.objects.get(
                        BranchID=BranchID, CompanyID=CompanyID, SettingsType="CreateBatchForWorkOrder").SettingsValue

                if check_CreateBatchForWorkOrder == True or check_CreateBatchForWorkOrder == "True":
                    BatchCode = get_auto_AutoBatchCode(
                        Batch, BranchID, CompanyID)
                    Batch.objects.create(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        ManufactureDate=ManufactureDate,
                        ExpiryDate=ExpiryDate,
                        BatchCode=BatchCode,
                        StockIn=Qty_batch,
                        PurchasePrice=BatchPurchasePrice,
                        SalesPrice=BatchSalesPrice,
                        PriceListID=BatchPriceListID,
                        ProductID=ProductID,
                        WareHouseID=WareHouseID,
                        Description=Notes,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        ConnectID=WorkOrderMasterID
                    )
                else:
                    if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
                        check_EnableProductBatchWise = GeneralSettings.objects.get(
                            BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
                        check_BatchCriteria = "PurchasePriceAndSalesPrice"
                        if GeneralSettings.objects.filter(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="BatchCriteria").exists():
                            check_BatchCriteria = GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="BatchCriteria").SettingsValue
                        if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:

                            if check_BatchCriteria == "PurchasePrice":
                                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=BatchPurchasePrice).exists():
                                    batch_ins = Batch.objects.get(
                                        CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=BatchPurchasePrice)
                                    StockIn = batch_ins.StockIn
                                    NewStock = converted_float(
                                        StockIn) + converted_float(Qty_batch)
                                    batch_ins.StockIn = NewStock
                                    batch_ins.ManufactureDate = ManufactureDate
                                    batch_ins.ExpiryDate = ExpiryDate
                                    batch_ins.ConnectID = WorkOrderMasterID
                                    batch_ins.save()
                                else:
                                    BatchCode = get_auto_AutoBatchCode(
                                        Batch, BranchID, CompanyID)
                                    Batch.objects.create(
                                        CompanyID=CompanyID,
                                        BranchID=BranchID,
                                        ManufactureDate=ManufactureDate,
                                        ExpiryDate=ExpiryDate,
                                        BatchCode=BatchCode,
                                        StockIn=Qty_batch,
                                        PurchasePrice=BatchPurchasePrice,
                                        SalesPrice=BatchSalesPrice,
                                        PriceListID=BatchPriceListID,
                                        ProductID=ProductID,
                                        WareHouseID=WareHouseID,
                                        Description=Notes,
                                        CreatedDate=today,
                                        UpdatedDate=today,
                                        CreatedUserID=CreatedUserID,
                                        ConnectID=WorkOrderMasterID
                                    )
                            elif check_BatchCriteria == "SalesPrice":
                                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, SalesPrice=BatchSalesPrice).exists():
                                    batch_ins = Batch.objects.get(
                                        CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, SalesPrice=BatchSalesPrice)
                                    StockIn = batch_ins.StockIn
                                    NewStock = converted_float(
                                        StockIn) + converted_float(Qty_batch)
                                    batch_ins.StockIn = NewStock
                                    batch_ins.ManufactureDate = ManufactureDate
                                    batch_ins.ExpiryDate = ExpiryDate
                                    batch_ins.ConnectID = WorkOrderMasterID
                                    batch_ins.save()
                                else:
                                    BatchCode = get_auto_AutoBatchCode(
                                        Batch, BranchID, CompanyID)
                                    Batch.objects.create(
                                        CompanyID=CompanyID,
                                        BranchID=BranchID,
                                        ManufactureDate=ManufactureDate,
                                        ExpiryDate=ExpiryDate,
                                        BatchCode=BatchCode,
                                        StockIn=Qty_batch,
                                        PurchasePrice=BatchPurchasePrice,
                                        SalesPrice=BatchSalesPrice,
                                        PriceListID=BatchPriceListID,
                                        ProductID=ProductID,
                                        WareHouseID=WareHouseID,
                                        Description=Notes,
                                        CreatedDate=today,
                                        UpdatedDate=today,
                                        CreatedUserID=CreatedUserID,
                                        ConnectID=WorkOrderMasterID
                                    )
                            else:
                                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=BatchPurchasePrice, SalesPrice=BatchSalesPrice).exists():
                                    batch_ins = Batch.objects.get(
                                        CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=BatchPurchasePrice, SalesPrice=BatchSalesPrice)
                                    StockIn = batch_ins.StockIn
                                    NewStock = converted_float(
                                        StockIn) + converted_float(Qty_batch)
                                    batch_ins.StockIn = NewStock
                                    batch_ins.ManufactureDate = ManufactureDate
                                    batch_ins.ExpiryDate = ExpiryDate
                                    batch_ins.ConnectID = WorkOrderMasterID
                                    batch_ins.save()
                                else:
                                    BatchCode = get_auto_AutoBatchCode(
                                        Batch, BranchID, CompanyID)
                                    Batch.objects.create(
                                        CompanyID=CompanyID,
                                        BranchID=BranchID,
                                        ManufactureDate=ManufactureDate,
                                        ExpiryDate=ExpiryDate,
                                        BatchCode=BatchCode,
                                        StockIn=Qty_batch,
                                        PurchasePrice=BatchPurchasePrice,
                                        SalesPrice=BatchSalesPrice,
                                        PriceListID=BatchPriceListID,
                                        ProductID=ProductID,
                                        WareHouseID=WareHouseID,
                                        Description=Notes,
                                        CreatedDate=today,
                                        UpdatedDate=today,
                                        CreatedUserID=CreatedUserID,
                                        ConnectID=WorkOrderMasterID
                                    )
                        else:
                            if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PriceListID=BatchPriceListID).exists():
                                batch_ins = Batch.objects.get(
                                    CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PriceListID=BatchPriceListID)
                                StockIn = batch_ins.StockIn
                                NewStock = converted_float(StockIn) + converted_float(Qty_batch)
                                batch_ins.StockIn = NewStock
                                batch_ins.save()
                            else:
                                BatchCode = get_auto_AutoBatchCode(
                                    Batch, BranchID, CompanyID)
                                Batch.objects.create(
                                    CompanyID=CompanyID,
                                    BranchID=BranchID,
                                    BatchCode=BatchCode,
                                    StockIn=Qty_batch,
                                    PurchasePrice=BatchPurchasePrice,
                                    SalesPrice=BatchSalesPrice,
                                    PriceListID=BatchPriceListID,
                                    ProductID=ProductID,
                                    WareHouseID=WareHouseID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CreatedUserID=CreatedUserID,
                                )

                update_voucher_table(
                    CompanyID, CreatedUserID, VoucherType, PreFix, Seperator, InvoiceNo)

                WorkOrderMaster_Log.objects.create(
                    CompanyID=CompanyID,
                    TransactionID=WorkOrderMasterID,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    Date=Date,
                    WareHouseID=WareHouseID,
                    Notes=Notes,
                    ProductID=ProductID,
                    BatchCode=BatchCode,
                    ProductQty=ProductQty,
                    CostPerPrice=CostPerPrice,
                    UnitPrice=UnitPrice,
                    PriceListID=BatchPriceListID,
                    Amount=Amount,
                    TotalQty=TotalQty,
                    ManufactureDate=ManufactureDate,
                    ExpiryDate=ExpiryDate,
                    GrandTotal=GrandTotal,
                    IsActive=IsActive,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                )

                instance = WorkOrderMaster.objects.create(
                    CompanyID=CompanyID,
                    WorkOrderMasterID=WorkOrderMasterID,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    Date=Date,
                    WareHouseID=WareHouseID,
                    Notes=Notes,
                    ProductID=ProductID,
                    BatchCode=BatchCode,
                    ProductQty=ProductQty,
                    CostPerPrice=CostPerPrice,
                    UnitPrice=UnitPrice,
                    PriceListID=BatchPriceListID,
                    Amount=Amount,
                    TotalQty=TotalQty,
                    GrandTotal=GrandTotal,
                    IsActive=IsActive,
                    ManufactureDate=ManufactureDate,
                    ExpiryDate=ExpiryDate,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                )

                Product.objects.filter(ProductID=ProductID, CompanyID=CompanyID,
                                       BranchID=BranchID).update(IsFinishedProduct=True)

                # MultiFactor = PriceList.objects.get(
                #     CompanyID=CompanyID, PriceListID=BatchPriceListID, BranchID=BranchID).MultiFactor
                PriceListID = PriceList.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True, BranchID=BranchID).PriceListID

                # PurchasePrice = priceList.PurchasePrice
                # SalesPrice = priceList.SalesPrice

                Qty = converted_float(MultiFactor) * converted_float(ProductQty)
                Cost = converted_float(CostPerPrice) / converted_float(MultiFactor)

                # Qy = round(Qty, 4)
                # Qty = str(Qy)

                # Ct = round(Cost, 4)
                # Cost = str(Ct)

                priceList_instance = PriceList.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID, BranchID=BranchID)
                PurchasePrice = priceList_instance.PurchasePrice
                SalesPrice = priceList_instance.SalesPrice

                StockPostingID = get_auto_stockPostid(
                    StockPosting, BranchID, CompanyID)

                pricelist, warehouse = get_ModelInstance(
                    CompanyID, BranchID, PriceListID, WareHouseID)

                StockPosting.objects.create(
                    StockPostingID=StockPostingID,
                    BranchID=BranchID,
                    Action=Action,
                    Date=Date,
                    VoucherMasterID=WorkOrderMasterID,
                    VoucherType=VoucherType,
                    ProductID=ProductID,
                    BatchID=BatchID,
                    WareHouseID=WareHouseID,
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
                    Date=Date,
                    VoucherMasterID=WorkOrderMasterID,
                    VoucherType=VoucherType,
                    ProductID=ProductID,
                    BatchID=BatchID,
                    WareHouseID=WareHouseID,
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
                stockRateInstance = None

                # if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WareHouseID, PriceListID=PriceListID).exists():
                #     stockRateInstance = StockRate.objects.get(
                #         CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WareHouseID, PriceListID=PriceListID)

                #     StockRateID = stockRateInstance.StockRateID
                #     stockRateInstance.Qty = converted_float(stockRateInstance.Qty) + converted_float(Qty)
                #     stockRateInstance.save()

                #     if StockTrans.objects.filter(StockRateID=StockRateID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                #         stockTra_in = StockTrans.objects.filter(
                #             StockRateID=StockRateID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                #         stockTra_in.Qty = converted_float(stockTra_in.Qty) + converted_float(Qty)
                #         stockTra_in.save()
                #     else:
                #         StockTransID = get_auto_StockTransID(
                #             StockTrans, BranchID, CompanyID)
                #         StockTrans.objects.create(
                #             StockTransID=StockTransID,
                #             BranchID=BranchID,
                #             VoucherType=VoucherType,
                #             StockRateID=StockRateID,
                #             MasterID=WorkOrderMasterID,
                #             Qty=Qty,
                #             IsActive=IsActive,
                #             CompanyID=CompanyID,
                #         )

                # else:
                #     StockRateID = get_auto_StockRateID(StockRate, BranchID, CompanyID)
                #     StockRate.objects.create(
                #         StockRateID=StockRateID,
                #         BranchID=BranchID,
                #         BatchID=BatchID,
                #         PurchasePrice=PurchasePrice,
                #         SalesPrice=SalesPrice,
                #         Qty=Qty,
                #         Cost=Cost,
                #         ProductID=ProductID,
                #         WareHouseID=WareHouseID,
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
                #         MasterID=WorkOrderMasterID,
                #         Qty=Qty,
                #         IsActive=IsActive,
                #         CompanyID=CompanyID,
                #     )

                WorkOrderDetailses = data["WorkOrderDetails"]

                for WorkOrderDetail in WorkOrderDetailses:

                    # PurchaseMasterID = serialized.data['PurchaseMasterID']
                    # WorkOrderMasterID = purchaseDetail['WorkOrderMasterID']
                    ProductID = WorkOrderDetail['ProductID']
                    if ProductID:
                        Qty = converted_float(WorkOrderDetail['Qty'])
                        DetailPriceListID = WorkOrderDetail['PriceListID']
                        CostPerPrice = converted_float(WorkOrderDetail['CostPerItem'])
                        UnitPrice = converted_float(WorkOrderDetail['UnitPrice'])
                        Amount = converted_float(WorkOrderDetail['NetAmount'])
                        DetailPurchasePrice = converted_float(
                            WorkOrderDetail['PurchasePrice'])
                        DetailSalesPrice = converted_float(WorkOrderDetail['UnitPrice'])
                        BatchCode = int(WorkOrderDetail['BatchCode'])
                        InclusivePrice = converted_float(
                            WorkOrderDetail['InclusivePrice'])
                        is_inclusive = WorkOrderDetail['is_inclusive']

                        DetailQty = Qty
                        # CostPerPrice = round(CostPerPrice, PriceRounding)
                        # UnitPrice = round(UnitPrice, PriceRounding)
                        # DetailPurchasePrice = round(DetailPurchasePrice, PriceRounding)
                        # DetailSalesPrice = round(DetailSalesPrice, PriceRounding)
                        # Amount = round(Amount, PriceRounding)

                        if is_inclusive == True:
                            DetailSalesPrice = str(InclusivePrice)
                        else:
                            DetailSalesPrice = str(UnitPrice)

                        DetailPurchasePrice = str(DetailPurchasePrice)

                        MultiFactor = PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=DetailPriceListID, BranchID=BranchID).MultiFactor

                        # qty_batch = converted_float(FreeQty) + converted_float(Qty)
                        Qty_batch = converted_float(MultiFactor) * converted_float(DetailQty)

                        WorkOrderDetailsID = get_auto_id(
                            WorkOrderDetails, BranchID, CompanyID)

                        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
                            check_EnableProductBatchWise = GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue

                            check_BatchCriteria = "PurchasePriceAndSalesPrice"
                            # if GeneralSettings.objects.filter(
                            #         CompanyID=CompanyID, SettingsType="BatchCriteria").exists():
                            #     check_BatchCriteria = GeneralSettings.objects.get(
                            #         CompanyID=CompanyID, SettingsType="BatchCriteria").SettingsValue

                            if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                                if check_BatchCriteria == "PurchasePrice":
                                    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=DetailPurchasePrice).exists():
                                        batch_ins = Batch.objects.get(
                                            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=DetailPurchasePrice)
                                        StockOut = batch_ins.StockOut
                                        NewStock = converted_float(
                                            StockOut) + converted_float(Qty_batch)
                                        batch_ins.StockOut = NewStock
                                        # batch_ins.ManufactureDate = ManufactureDate
                                        # batch_ins.ExpiryDate = ExpiryDate
                                        batch_ins.ConnectID = WorkOrderMasterID
                                        batch_ins.save()
                                    else:
                                        BatchCode = get_auto_AutoBatchCode(
                                            Batch, BranchID, CompanyID)
                                        Batch.objects.create(
                                            CompanyID=CompanyID,
                                            BranchID=BranchID,
                                            BatchCode=BatchCode,
                                            StockOut=Qty_batch,
                                            PurchasePrice=DetailPurchasePrice,
                                            SalesPrice=DetailSalesPrice,
                                            PriceListID=DetailPriceListID,
                                            ProductID=ProductID,
                                            WareHouseID=WareHouseID,
                                            Description=Notes,
                                            CreatedDate=today,
                                            UpdatedDate=today,
                                            CreatedUserID=CreatedUserID,
                                            ConnectID=WorkOrderMasterID
                                        )
                                elif check_BatchCriteria == "SalesPrice":
                                    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, SalesPrice=DetailSalesPrice).exists():
                                        batch_ins = Batch.objects.get(
                                            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, SalesPrice=DetailSalesPrice)
                                        StockOut = batch_ins.StockOut
                                        NewStock = converted_float(
                                            StockOut) + converted_float(Qty_batch)
                                        batch_ins.StockOut = NewStock
                                        # batch_ins.ManufactureDate = ManufactureDate
                                        # batch_ins.ExpiryDate = ExpiryDate
                                        batch_ins.ConnectID = WorkOrderMasterID
                                        batch_ins.save()
                                    else:
                                        BatchCode = get_auto_AutoBatchCode(
                                            Batch, BranchID, CompanyID)
                                        Batch.objects.create(
                                            CompanyID=CompanyID,
                                            BranchID=BranchID,
                                            BatchCode=BatchCode,
                                            StockOut=Qty_batch,
                                            PurchasePrice=DetailPurchasePrice,
                                            SalesPrice=DetailSalesPrice,
                                            PriceListID=DetailPriceListID,
                                            ProductID=ProductID,
                                            WareHouseID=WareHouseID,
                                            Description=Notes,
                                            CreatedDate=today,
                                            UpdatedDate=today,
                                            CreatedUserID=CreatedUserID,
                                            ConnectID=WorkOrderMasterID

                                        )
                                else:
                                    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=DetailPurchasePrice, SalesPrice=DetailSalesPrice).exists():
                                        batch_ins = Batch.objects.get(
                                            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=DetailPurchasePrice, SalesPrice=DetailSalesPrice)
                                        StockOut = batch_ins.StockOut
                                        NewStock = converted_float(
                                            StockOut) + converted_float(Qty_batch)
                                        batch_ins.StockOut = NewStock
                                        # batch_ins.ManufactureDate = ManufactureDate
                                        # batch_ins.ExpiryDate = ExpiryDate
                                        batch_ins.ConnectID = WorkOrderMasterID
                                        batch_ins.save()
                                    else:
                                        BatchCode = get_auto_AutoBatchCode(
                                            Batch, BranchID, CompanyID)
                                        Batch.objects.create(
                                            CompanyID=CompanyID,
                                            BranchID=BranchID,
                                            BatchCode=BatchCode,
                                            StockOut=Qty_batch,
                                            PurchasePrice=DetailPurchasePrice,
                                            SalesPrice=DetailSalesPrice,
                                            PriceListID=DetailPriceListID,
                                            ProductID=ProductID,
                                            WareHouseID=WareHouseID,
                                            Description=Notes,
                                            CreatedDate=today,
                                            UpdatedDate=today,
                                            CreatedUserID=CreatedUserID,
                                            ConnectID=WorkOrderMasterID
                                        )
                            else:
                                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PriceListID=PriceListID).exists():
                                    batch_ins = Batch.objects.get(
                                        CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PriceListID=PriceListID)
                                    StockOut = batch_ins.StockOut
                                    NewStock = converted_float(
                                        StockOut) + converted_float(Qty_batch)
                                    batch_ins.StockOut = NewStock
                                    batch_ins.save()
                                else:
                                    BatchCode = get_auto_AutoBatchCode(
                                        Batch, BranchID, CompanyID)
                                    Batch.objects.create(
                                        CompanyID=CompanyID,
                                        BranchID=BranchID,
                                        BatchCode=BatchCode,
                                        StockOut=Qty_batch,
                                        PurchasePrice=PurchasePrice,
                                        SalesPrice=SalesPrice,
                                        PriceListID=PriceListID,
                                        ProductID=ProductID,
                                        WareHouseID=WareHouseID,
                                        CreatedDate=today,
                                        UpdatedDate=today,
                                        CreatedUserID=CreatedUserID,
                                    )

                        log_instance = WorkOrderDetails_Log.objects.create(
                            CompanyID=CompanyID,
                            TransactionID=WorkOrderDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            WorkOrderMasterID=WorkOrderMasterID,
                            ProductID=ProductID,
                            BatchCode=BatchCode,
                            Qty=DetailQty,
                            PriceListID=DetailPriceListID,
                            CostPerPrice=CostPerPrice,
                            UnitPrice=UnitPrice,
                            Amount=Amount,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                        )

                        WorkOrderDetails.objects.create(
                            CompanyID=CompanyID,
                            WorkOrderDetailsID=WorkOrderDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            WorkOrderMasterID=WorkOrderMasterID,
                            ProductID=ProductID,
                            BatchCode=BatchCode,
                            Qty=DetailQty,
                            PriceListID=DetailPriceListID,
                            CostPerPrice=CostPerPrice,
                            UnitPrice=UnitPrice,
                            Amount=Amount,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            LogID=log_instance.ID
                        )

                        # MultiFactor = PriceList.objects.get(
                        #     CompanyID=CompanyID, PriceListID=DetailPriceListID, BranchID=BranchID).MultiFactor
                        PriceListID_DefUnit = PriceList.objects.get(
                            CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).PriceListID

                        # PriceListID_DefUnit = priceList.PriceListID
                        # MultiFactor = priceList.MultiFactor

                        # PurchasePrice = priceList.PurchasePrice
                        # SalesPrice = priceList.SalesPrice
                        DetailQty = Qty

                        Qty = converted_float(MultiFactor) * converted_float(DetailQty)
                        Cost = converted_float(CostPerPrice) / converted_float(MultiFactor)

                        # Qy = round(Qty, 4)
                        # Qty = str(Qy)

                        # Ct = round(Cost, 4)
                        # Cost = str(Ct)

                        priceList_instance = PriceList.objects.get(
                            CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID_DefUnit, BranchID=BranchID)
                        PurchasePrice = priceList_instance.PurchasePrice
                        SalesPrice = priceList_instance.SalesPrice

                        StockPostingID = get_auto_stockPostid(
                            StockPosting, BranchID, CompanyID)

                        pricelist, warehouse = get_ModelInstance(
                            CompanyID, BranchID, PriceListID_DefUnit, WareHouseID)

                        StockPosting.objects.create(
                            StockPostingID=StockPostingID,
                            BranchID=BranchID,
                            Action=Action,
                            Date=Date,
                            VoucherMasterID=WorkOrderMasterID,
                            VoucherDetailID=WorkOrderDetailsID,
                            VoucherType=VoucherType,
                            ProductID=ProductID,
                            BatchID=BatchID,
                            WareHouseID=WareHouseID,
                            QtyOut=Qty,
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
                            Date=Date,
                            VoucherMasterID=WorkOrderMasterID,
                            VoucherDetailID=WorkOrderDetailsID,
                            VoucherType=VoucherType,
                            ProductID=ProductID,
                            BatchID=BatchID,
                            WareHouseID=WareHouseID,
                            QtyOut=Qty,
                            Rate=Cost,
                            PriceListID=PriceListID_DefUnit,
                            IsActive=IsActive,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )

                        update_stock(CompanyID, BranchID, ProductID)

                        # changQty = Qty
                        # if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WareHouseID, PriceListID=PriceListID_DefUnit).exists():
                        #     if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WareHouseID, Qty__gt=0, PriceListID=PriceListID_DefUnit).exists():
                        #         stockRate_instances = StockRate.objects.filter(
                        #             CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WareHouseID, Qty__gt=0, PriceListID=PriceListID_DefUnit)
                        #         count = stockRate_instances.count()
                        #         last = 0
                        #         for stockRate_instance in stockRate_instances:
                        #             last = converted_float(last) + converted_float(1)
                        #             StockRateID = stockRate_instance.StockRateID
                        #             stock_post_cost = stockRate_instance.Cost
                        #             if converted_float(stockRate_instance.Qty) > converted_float(changQty):
                        #                 # stockRate_instance.Qty = converted_float(
                        #                 #     stockRate_instance.Qty) - converted_float(changQty)
                        #                 # changQty = converted_float(stockRate_instance.Qty) - converted_float(changQty)
                        #                 lastQty = converted_float(
                        #                     stockRate_instance.Qty) - converted_float(changQty)
                        #                 chqy = changQty
                        #                 changQty = 0
                        #                 stockRate_instance.Qty = lastQty
                        #                 stockRate_instance.save()

                        #                 if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                        #                                                VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit).exists():
                        #                     stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                        #                                                                   VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit)
                        #                     QtyOut = stockPost_instance.QtyOut
                        #                     newQty = converted_float(QtyOut) + converted_float(chqy)

                        #                     stockPost_instance.QtyOut = newQty
                        #                     stockPost_instance.save()
                        #                 else:
                        #                     StockPostingID = get_auto_stockPostid(
                        #                         StockPosting, BranchID, CompanyID)
                        #                     StockPosting.objects.create(
                        #                         StockPostingID=StockPostingID,
                        #                         BranchID=BranchID,
                        #                         Action=Action,
                        #                         Date=Date,
                        #                         VoucherMasterID=WorkOrderMasterID,
                        #                         VoucherType=VoucherType,
                        #                         ProductID=ProductID,
                        #                         BatchID=BatchID,
                        #                         WareHouseID=WareHouseID,
                        #                         QtyOut=chqy,
                        #                         Rate=stock_post_cost,
                        #                         PriceListID=PriceListID_DefUnit,
                        #                         IsActive=IsActive,
                        #                         CreatedDate=today,
                        #                         UpdatedDate=today,
                        #                         CreatedUserID=CreatedUserID,
                        #                         CompanyID=CompanyID,
                        #                     )

                        #                     StockPosting_Log.objects.create(
                        #                         TransactionID=StockPostingID,
                        #                         BranchID=BranchID,
                        #                         Action=Action,
                        #                         Date=Date,
                        #                         VoucherMasterID=WorkOrderMasterID,
                        #                         VoucherType=VoucherType,
                        #                         ProductID=ProductID,
                        #                         BatchID=BatchID,
                        #                         WareHouseID=WareHouseID,
                        #                         QtyOut=chqy,
                        #                         Rate=stock_post_cost,
                        #                         PriceListID=PriceListID_DefUnit,
                        #                         IsActive=IsActive,
                        #                         CreatedDate=today,
                        #                         UpdatedDate=today,
                        #                         CreatedUserID=CreatedUserID,
                        #                         CompanyID=CompanyID,
                        #                     )

                        #                 if StockTrans.objects.filter(StockRateID=StockRateID, DetailID=WorkOrderDetailsID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                        #                     stockTra_in = StockTrans.objects.filter(
                        #                         StockRateID=StockRateID, DetailID=WorkOrderDetailsID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                        #                     stockTra_in.Qty = converted_float(
                        #                         stockTra_in.Qty) + converted_float(chqy)
                        #                     stockTra_in.save()
                        #                 else:
                        #                     StockTransID = get_auto_StockTransID(
                        #                         StockTrans, BranchID, CompanyID)
                        #                     StockTrans.objects.create(
                        #                         StockTransID=StockTransID,
                        #                         BranchID=BranchID,
                        #                         VoucherType=VoucherType,
                        #                         StockRateID=StockRateID,
                        #                         DetailID=WorkOrderDetailsID,
                        #                         MasterID=WorkOrderMasterID,
                        #                         Qty=chqy,
                        #                         IsActive=IsActive,
                        #                         CompanyID=CompanyID,
                        #                     )
                        #                 break
                        #             elif converted_float(stockRate_instance.Qty) < converted_float(changQty):
                        #                 if converted_float(changQty) > converted_float(stockRate_instance.Qty):
                        #                     changQty = converted_float(changQty) - \
                        #                         converted_float(stockRate_instance.Qty)
                        #                     stckQty = stockRate_instance.Qty
                        #                     stockRate_instance.Qty = 0
                        #                     stockRate_instance.save()

                        #                     if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                        #                                                    VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit).exists():
                        #                         stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                        #                                                                       VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit)
                        #                         QtyOut = stockPost_instance.QtyOut
                        #                         newQty = converted_float(QtyOut) + \
                        #                             converted_float(stckQty)
                        #                         stockPost_instance.QtyOut = newQty
                        #                         stockPost_instance.save()
                        #                     else:
                        #                         StockPostingID = get_auto_stockPostid(
                        #                             StockPosting, BranchID, CompanyID)
                        #                         StockPosting.objects.create(
                        #                             StockPostingID=StockPostingID,
                        #                             BranchID=BranchID,
                        #                             Action=Action,
                        #                             Date=Date,
                        #                             VoucherMasterID=WorkOrderMasterID,
                        #                             VoucherType=VoucherType,
                        #                             ProductID=ProductID,
                        #                             BatchID=BatchID,
                        #                             WareHouseID=WareHouseID,
                        #                             QtyOut=stckQty,
                        #                             Rate=stock_post_cost,
                        #                             PriceListID=PriceListID_DefUnit,
                        #                             IsActive=IsActive,
                        #                             CreatedDate=today,
                        #                             UpdatedDate=today,
                        #                             CreatedUserID=CreatedUserID,
                        #                             CompanyID=CompanyID,
                        #                         )

                        #                         StockPosting_Log.objects.create(
                        #                             TransactionID=StockPostingID,
                        #                             BranchID=BranchID,
                        #                             Action=Action,
                        #                             Date=Date,
                        #                             VoucherMasterID=WorkOrderMasterID,
                        #                             VoucherType=VoucherType,
                        #                             ProductID=ProductID,
                        #                             BatchID=BatchID,
                        #                             WareHouseID=WareHouseID,
                        #                             QtyOut=stckQty,
                        #                             Rate=stock_post_cost,
                        #                             PriceListID=PriceListID_DefUnit,
                        #                             IsActive=IsActive,
                        #                             CreatedDate=today,
                        #                             UpdatedDate=today,
                        #                             CreatedUserID=CreatedUserID,
                        #                             CompanyID=CompanyID,
                        #                         )
                        #                     if StockTrans.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, DetailID=WorkOrderDetailsID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                        #                         stockTra_in = StockTrans.objects.filter(
                        #                             CompanyID=CompanyID, StockRateID=StockRateID, DetailID=WorkOrderDetailsID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                        #                         stockTra_in.Qty = converted_float(
                        #                             stockTra_in.Qty) + converted_float(stckQty)
                        #                         stockTra_in.save()
                        #                     else:
                        #                         StockTransID = get_auto_StockTransID(
                        #                             StockTrans, BranchID, CompanyID)
                        #                         StockTrans.objects.create(
                        #                             StockTransID=StockTransID,
                        #                             BranchID=BranchID,
                        #                             VoucherType=VoucherType,
                        #                             StockRateID=StockRateID,
                        #                             DetailID=WorkOrderDetailsID,
                        #                             MasterID=WorkOrderMasterID,
                        #                             Qty=stckQty,
                        #                             IsActive=IsActive,
                        #                             CompanyID=CompanyID,
                        #                         )
                        #                 else:
                        #                     if changQty < 0:
                        #                         changQty = 0
                        #                     # chqty = changQty
                        #                     changQty = converted_float(
                        #                         stockRate_instance.Qty) - converted_float(changQty)
                        #                     chqty = changQty
                        #                     stockRate_instance.Qty = changQty
                        #                     changQty = 0
                        #                     stockRate_instance.save()

                        #                     if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                        #                                                    VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit).exists():
                        #                         stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                        #                                                                       VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit)
                        #                         QtyOut = stockPost_instance.QtyOut
                        #                         newQty = converted_float(QtyOut) + converted_float(chqty)
                        #                         stockPost_instance.QtyOut = newQty
                        #                         stockPost_instance.save()
                        #                     else:
                        #                         StockPostingID = get_auto_stockPostid(
                        #                             StockPosting, BranchID, CompanyID)
                        #                         StockPosting.objects.create(
                        #                             StockPostingID=StockPostingID,
                        #                             BranchID=BranchID,
                        #                             Action=Action,
                        #                             Date=Date,
                        #                             VoucherMasterID=WorkOrderMasterID,
                        #                             VoucherType=VoucherType,
                        #                             ProductID=ProductID,
                        #                             BatchID=BatchID,
                        #                             WareHouseID=WareHouseID,
                        #                             QtyOut=chqty,
                        #                             Rate=stock_post_cost,
                        #                             PriceListID=PriceListID_DefUnit,
                        #                             IsActive=IsActive,
                        #                             CreatedDate=today,
                        #                             UpdatedDate=today,
                        #                             CreatedUserID=CreatedUserID,
                        #                             CompanyID=CompanyID,
                        #                         )

                        #                         StockPosting_Log.objects.create(
                        #                             TransactionID=StockPostingID,
                        #                             BranchID=BranchID,
                        #                             Action=Action,
                        #                             Date=Date,
                        #                             VoucherMasterID=WorkOrderMasterID,
                        #                             VoucherType=VoucherType,
                        #                             ProductID=ProductID,
                        #                             BatchID=BatchID,
                        #                             WareHouseID=WareHouseID,
                        #                             QtyOut=chqty,
                        #                             Rate=stock_post_cost,
                        #                             PriceListID=PriceListID_DefUnit,
                        #                             IsActive=IsActive,
                        #                             CreatedDate=today,
                        #                             UpdatedDate=today,
                        #                             CreatedUserID=CreatedUserID,
                        #                             CompanyID=CompanyID,
                        #                         )

                        #                     if StockTrans.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, DetailID=WorkOrderDetailsID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                        #                         stockTra_in = StockTrans.objects.filter(
                        #                             CompanyID=CompanyID, StockRateID=StockRateID, DetailID=WorkOrderDetailsID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                        #                         stockTra_in.Qty = converted_float(
                        #                             stockTra_in.Qty) + converted_float(chqty)
                        #                         stockTra_in.save()
                        #                     else:
                        #                         StockTransID = get_auto_StockTransID(
                        #                             StockTrans, BranchID, CompanyID)
                        #                         StockTrans.objects.create(
                        #                             StockTransID=StockTransID,
                        #                             BranchID=BranchID,
                        #                             VoucherType=VoucherType,
                        #                             StockRateID=StockRateID,
                        #                             DetailID=WorkOrderDetailsID,
                        #                             MasterID=WorkOrderMasterID,
                        #                             Qty=chqty,
                        #                             IsActive=IsActive,
                        #                             CompanyID=CompanyID,
                        #                         )

                        #             elif converted_float(stockRate_instance.Qty) == converted_float(changQty):
                        #                 chty = stockRate_instance.Qty
                        #                 stockRate_instance.Qty = 0
                        #                 changQty = 0
                        #                 stockRate_instance.save()

                        #                 if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                        #                                                VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit).exists():
                        #                     stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                        #                                                                   VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit)
                        #                     QtyOut = stockPost_instance.QtyOut
                        #                     newQty = converted_float(QtyOut) + \
                        #                         converted_float(chty)
                        #                     stockPost_instance.QtyOut = newQty
                        #                     stockPost_instance.save()
                        #                 else:
                        #                     StockPostingID = get_auto_stockPostid(
                        #                         StockPosting, BranchID, CompanyID)
                        #                     StockPosting.objects.create(
                        #                         StockPostingID=StockPostingID,
                        #                         BranchID=BranchID,
                        #                         Action=Action,
                        #                         Date=Date,
                        #                         VoucherMasterID=WorkOrderMasterID,
                        #                         VoucherType=VoucherType,
                        #                         ProductID=ProductID,
                        #                         BatchID=BatchID,
                        #                         WareHouseID=WareHouseID,
                        #                         QtyOut=chty,
                        #                         Rate=stock_post_cost,
                        #                         PriceListID=PriceListID_DefUnit,
                        #                         IsActive=IsActive,
                        #                         CreatedDate=today,
                        #                         UpdatedDate=today,
                        #                         CreatedUserID=CreatedUserID,
                        #                         CompanyID=CompanyID,
                        #                     )

                        #                     StockPosting_Log.objects.create(
                        #                         TransactionID=StockPostingID,
                        #                         BranchID=BranchID,
                        #                         Action=Action,
                        #                         Date=Date,
                        #                         VoucherMasterID=WorkOrderMasterID,
                        #                         VoucherType=VoucherType,
                        #                         ProductID=ProductID,
                        #                         BatchID=BatchID,
                        #                         WareHouseID=WareHouseID,
                        #                         QtyOut=chty,
                        #                         Rate=stock_post_cost,
                        #                         PriceListID=PriceListID_DefUnit,
                        #                         IsActive=IsActive,
                        #                         CreatedDate=today,
                        #                         UpdatedDate=today,
                        #                         CreatedUserID=CreatedUserID,
                        #                         CompanyID=CompanyID,
                        #                     )

                        #                 if StockTrans.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, DetailID=WorkOrderDetailsID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                        #                     stockTra_in = StockTrans.objects.filter(
                        #                         CompanyID=CompanyID, StockRateID=StockRateID, DetailID=WorkOrderDetailsID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                        #                     stockTra_in.Qty = converted_float(
                        #                         stockTra_in.Qty) + converted_float(chty)
                        #                     stockTra_in.save()
                        #                 else:
                        #                     StockTransID = get_auto_StockTransID(
                        #                         StockTrans, BranchID, CompanyID)
                        #                     StockTrans.objects.create(
                        #                         StockTransID=StockTransID,
                        #                         BranchID=BranchID,
                        #                         VoucherType=VoucherType,
                        #                         StockRateID=StockRateID,
                        #                         DetailID=WorkOrderDetailsID,
                        #                         MasterID=WorkOrderMasterID,
                        #                         Qty=chty,
                        #                         IsActive=IsActive,
                        #                         CompanyID=CompanyID,
                        #                     )
                        #                 break

                        #     if converted_float(changQty) > 0:
                        #         if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WareHouseID, Qty__lte=0, PriceListID=PriceListID_DefUnit).exists():
                        #             stockRate_instance = StockRate.objects.filter(
                        #                 CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WareHouseID, Qty__lte=0, PriceListID=PriceListID_DefUnit).first()
                        #             stock_post_cost = stockRate_instance.Cost
                        #             if converted_float(changQty) > 0:
                        #                 stockRate_instance.Qty = converted_float(
                        #                     stockRate_instance.Qty) - converted_float(changQty)
                        #                 stockRate_instance.save()

                        #                 if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                        #                                                VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit).exists():
                        #                     stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                        #                                                                   VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit)
                        #                     QtyOut = stockPost_instance.QtyOut
                        #                     newQty = converted_float(QtyOut) + converted_float(changQty)
                        #                     stockPost_instance.QtyOut = newQty
                        #                     stockPost_instance.save()
                        #                 else:
                        #                     StockPostingID = get_auto_stockPostid(
                        #                         StockPosting, BranchID, CompanyID)
                        #                     StockPosting.objects.create(
                        #                         StockPostingID=StockPostingID,
                        #                         BranchID=BranchID,
                        #                         Action=Action,
                        #                         Date=Date,
                        #                         VoucherMasterID=WorkOrderMasterID,
                        #                         VoucherType=VoucherType,
                        #                         ProductID=ProductID,
                        #                         BatchID=BatchID,
                        #                         WareHouseID=WareHouseID,
                        #                         QtyOut=changQty,
                        #                         Rate=stock_post_cost,
                        #                         PriceListID=PriceListID_DefUnit,
                        #                         IsActive=IsActive,
                        #                         CreatedDate=today,
                        #                         UpdatedDate=today,
                        #                         CreatedUserID=CreatedUserID,
                        #                         CompanyID=CompanyID,
                        #                     )

                        #                     StockPosting_Log.objects.create(
                        #                         TransactionID=StockPostingID,
                        #                         BranchID=BranchID,
                        #                         Action=Action,
                        #                         Date=Date,
                        #                         VoucherMasterID=WorkOrderMasterID,
                        #                         VoucherType=VoucherType,
                        #                         ProductID=ProductID,
                        #                         BatchID=BatchID,
                        #                         WareHouseID=WareHouseID,
                        #                         QtyOut=changQty,
                        #                         Rate=stock_post_cost,
                        #                         PriceListID=PriceListID_DefUnit,
                        #                         IsActive=IsActive,
                        #                         CreatedDate=today,
                        #                         UpdatedDate=today,
                        #                         CreatedUserID=CreatedUserID,
                        #                         CompanyID=CompanyID,
                        #                     )

                        #                 if not StockTrans.objects.filter(CompanyID=CompanyID,
                        #                                                  StockRateID=stockRate_instance.StockRateID,
                        #                                                  DetailID=WorkOrderDetailsID,
                        #                                                  MasterID=WorkOrderMasterID,
                        #                                                  VoucherType=VoucherType,
                        #                                                  BranchID=BranchID).exists():

                        #                     StockTransID = get_auto_StockTransID(
                        #                         StockTrans, BranchID, CompanyID)
                        #                     StockTrans.objects.create(
                        #                         CompanyID=CompanyID,
                        #                         StockTransID=StockTransID,
                        #                         BranchID=BranchID,
                        #                         VoucherType=VoucherType,
                        #                         StockRateID=stockRate_instance.StockRateID,
                        #                         DetailID=WorkOrderDetailsID,
                        #                         MasterID=WorkOrderMasterID,
                        #                         Qty=changQty,
                        #                         IsActive=IsActive
                        #                     )
                        # else:
                        #     if converted_float(Qty) > 0:
                        #         qty = converted_float(Qty) * -1
                        #     StockRateID = get_auto_StockRateID(
                        #         StockRate, BranchID, CompanyID)
                        #     StockRate.objects.create(
                        #         StockRateID=StockRateID,
                        #         BranchID=BranchID,
                        #         BatchID=BatchID,
                        #         PurchasePrice=PurchasePrice,
                        #         SalesPrice=SalesPrice,
                        #         Qty=qty,
                        #         Cost=Cost,
                        #         ProductID=ProductID,
                        #         WareHouseID=WareHouseID,
                        #         Date=Date,
                        #         PriceListID=PriceListID_DefUnit,
                        #         CreatedUserID=CreatedUserID,
                        #         CreatedDate=today,
                        #         UpdatedDate=today,
                        #         CompanyID=CompanyID,
                        #     )

                        #     StockPostingID = get_auto_stockPostid(
                        #         StockPosting, BranchID, CompanyID)
                        #     StockPosting.objects.create(
                        #         StockPostingID=StockPostingID,
                        #         BranchID=BranchID,
                        #         Action=Action,
                        #         Date=Date,
                        #         VoucherMasterID=WorkOrderMasterID,
                        #         VoucherType=VoucherType,
                        #         ProductID=ProductID,
                        #         BatchID=BatchID,
                        #         WareHouseID=WareHouseID,
                        #         QtyOut=Qty,
                        #         Rate=Cost,
                        #         PriceListID=PriceListID_DefUnit,
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
                        #         VoucherMasterID=WorkOrderMasterID,
                        #         VoucherType=VoucherType,
                        #         ProductID=ProductID,
                        #         BatchID=BatchID,
                        #         WareHouseID=WareHouseID,
                        #         QtyOut=Qty,
                        #         Rate=Cost,
                        #         PriceListID=PriceListID_DefUnit,
                        #         IsActive=IsActive,
                        #         CreatedDate=today,
                        #         UpdatedDate=today,
                        #         CreatedUserID=CreatedUserID,
                        #         CompanyID=CompanyID,
                        #     )
                        #     StockTransID = get_auto_StockTransID(
                        #         StockTrans, BranchID, CompanyID)
                        #     StockTrans.objects.create(
                        #         StockTransID=StockTransID,
                        #         BranchID=BranchID,
                        #         VoucherType=VoucherType,
                        #         StockRateID=StockRateID,
                        #         DetailID=WorkOrderDetailsID,
                        #         MasterID=WorkOrderMasterID,
                        #         Qty=qty,
                        #         IsActive=IsActive,
                        #         CompanyID=CompanyID,
                        #     )

                #request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Work Order',
                #              'Create', 'Work Order created successfully.', 'Work Order saved successfully.')

                response_data = {
                    "StatusCode": 6000,
                    "id": instance.id,
                    "message": "Work Order created Successfully!!!",
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Work Order',
                             'Create', 'Work Order created Failed.', 'VoucherNo already exist')
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

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Work Order',
                     'Create', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def edit_workorder(request, pk):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data['CompanyID']
            CreatedUserID = data['CreatedUserID']
            PriceRounding = data['PriceRounding']
            CompanyID = get_company(CompanyID)

            today = datetime.datetime.now()
            BranchID = data['BranchID']
            VoucherNo = data['VoucherNo']
            Date = data['Date']
            WareHouseID = data['WareHouseID']
            Notes = data['Notes']
            ProductID = data['ProductID']
            ProductQty = data['ProductQty']
            CostPerPrice = data['CostPerPrice']
            UnitPrice = data['BatchSalesPrice']
            BatchPriceListID = data['PriceListID']
            Amount = data['Amount']
            TotalQty = data['TotalQty']
            GrandTotal = data['GrandTotal']
            IsActive = data['IsActive']
            ManufactureDate = data['ManufactureDate']
            ExpiryDate = data['ExpiryDate']
            BatchPurchasePrice = data['BatchPurchasePrice']
            BatchSalesPrice = data['BatchSalesPrice']
            BatchCode = data['BatchCode']
            is_inclusive = data['is_inclusive']
            InclusivePriceBatch = data['InclusivePriceBatch']

            Action = "M"
            VoucherType = "WO"
            BatchID = 1

            if is_inclusive == True:
                BatchSalesPrice = str(InclusivePriceBatch)
            else:
                BatchSalesPrice = str(UnitPrice)

            instance = WorkOrderMaster.objects.get(
                pk=pk, CompanyID=CompanyID, BranchID=BranchID)
            instanceVoucherNo = instance.VoucherNo
            WorkOrderMasterID = instance.WorkOrderMasterID

            if not WorkOrderMaster.objects.filter(BranchID=BranchID, CompanyID=CompanyID, VoucherNo__iexact=VoucherNo).exclude(VoucherNo=instanceVoucherNo):
                # if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=instance.WorkOrderMasterID, BranchID=instance.BranchID, VoucherType=VoucherType).exists():
                #     StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=instance.WorkOrderMasterID,
                #                                 BranchID=instance.BranchID, VoucherType=VoucherType).delete()

                if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=instance.WorkOrderMasterID, BranchID=BranchID, VoucherType="WO").exists():
                    stk_ins = StockPosting.objects.filter(
                        CompanyID=CompanyID, VoucherMasterID=instance.WorkOrderMasterID, BranchID=BranchID, VoucherType="WO")
                    total_count_stock = stk_ins.count()
                    null_count = stk_ins.filter(
                        VoucherDetailID__isnull=True).count()

                    if total_count_stock == null_count:
                        stk_ins.delete()
                    else:
                        instance_qty_sum = converted_float(instance.ProductQty)
                        instance_MultiFactor = PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=instance.PriceListID, BranchID=BranchID).MultiFactor
                        instance_Qty = converted_float(
                            instance_MultiFactor) * converted_float(instance_qty_sum)
                        stk_ins_master = stk_ins.filter(QtyIn__gt=0).first()
                        stk_ins_master.QtyIn = converted_float(
                            stk_ins_master.QtyIn) - converted_float(instance_Qty)

                if WorkOrderDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, WorkOrderMasterID=instance.WorkOrderMasterID).exists():
                    Work_ins = WorkOrderDetails.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, WorkOrderMasterID=instance.WorkOrderMasterID)
                    for i in Work_ins:
                        DetailBatchCode = i.BatchCode
                        Qty = i.Qty
                        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=DetailBatchCode).exists():
                            batch_ins = Batch.objects.get(
                                CompanyID=CompanyID, BranchID=BranchID, BatchCode=DetailBatchCode)
                            StockOut = batch_ins.StockOut
                            batch_ins.StockOut = converted_float(StockOut) - converted_float(Qty)
                            batch_ins.save()

                        # if not StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=instance.WorkOrderMasterID,VoucherDetailID=i.WorkOrderDetailsID,BranchID=BranchID, VoucherType="WO").exists():
                        #     StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=instance.WorkOrderMasterID,BranchID=BranchID, VoucherType="WO").delete()

                        instance_MultiFactor = PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=i.PriceListID, BranchID=BranchID).MultiFactor

                        instance_qty_sum = converted_float(i.Qty)
                        instance_Qty = converted_float(
                            instance_MultiFactor) * converted_float(instance_qty_sum)
                        if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=instance.WorkOrderMasterID, VoucherDetailID=i.WorkOrderDetailsID, ProductID=i.ProductID, BranchID=BranchID, VoucherType="WO").exists():
                            stock_inst = StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=instance.WorkOrderMasterID,
                                                                     VoucherDetailID=i.WorkOrderDetailsID, ProductID=i.ProductID, BranchID=BranchID, VoucherType="WO").first()
                            print("instance_Qty//////////")
                            print(instance_Qty)
                            print(stock_inst.QtyOut)
                            stock_inst.QtyOut = converted_float(
                                stock_inst.QtyOut) - converted_float(instance_Qty)
                            stock_inst.save()

                # if StockTrans.objects.filter(CompanyID=CompanyID, DetailID=None, MasterID=instance.WorkOrderMasterID, BranchID=BranchID, VoucherType=VoucherType, IsActive=True).exists():
                #     stockTrans_instance = StockTrans.objects.filter(
                #         CompanyID=CompanyID, DetailID=None, MasterID=instance.WorkOrderMasterID, BranchID=BranchID, VoucherType=VoucherType, IsActive=True)
                #     for stck in stockTrans_instance:
                #         StockRateID = stck.StockRateID
                #         stck.IsActive = False
                #         qty_in_stockTrans = stck.Qty
                #         if StockRate.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, BranchID=BranchID).exists():
                #             stockRateInstance = StockRate.objects.get(
                #                 CompanyID=CompanyID, StockRateID=StockRateID, BranchID=BranchID)
                #             stockRateInstance.Qty = converted_float(
                #                 stockRateInstance.Qty) - converted_float(qty_in_stockTrans)
                #             stockRateInstance.save()
                #         stck.save()

                MasterBatchCode = instance.BatchCode
                MasterProductQty = instance.ProductQty
                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=MasterBatchCode).exists():
                    batch_ins = Batch.objects.get(
                        CompanyID=CompanyID, BranchID=BranchID, BatchCode=MasterBatchCode)
                    StockIn = batch_ins.StockIn
                    batch_ins.StockIn = converted_float(
                        StockIn) - converted_float(MasterProductQty)
                    batch_ins.save()

                MultiFactor = PriceList.objects.get(
                    CompanyID=CompanyID, PriceListID=BatchPriceListID, BranchID=BranchID).MultiFactor

                # qty_batch = converted_float(FreeQty) + converted_float(Qty_detail)
                Qty_batch = converted_float(MultiFactor) * converted_float(ProductQty)

                if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
                    check_EnableProductBatchWise = GeneralSettings.objects.get(
                        BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
                    check_BatchCriteria = "PurchasePriceAndSalesPrice"
                    if GeneralSettings.objects.filter(
                            CompanyID=CompanyID, SettingsType="BatchCriteria").exists():
                        check_BatchCriteria = GeneralSettings.objects.get(
                            BranchID=BranchID, CompanyID=CompanyID, SettingsType="BatchCriteria").SettingsValue
                    if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:

                        if check_BatchCriteria == "PurchasePrice":
                            if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=BatchPurchasePrice).exists():
                                batch_ins = Batch.objects.get(
                                    CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=BatchPurchasePrice)
                                StockIn = batch_ins.StockIn
                                NewStock = converted_float(StockIn) + converted_float(Qty_batch)
                                batch_ins.StockIn = NewStock
                                batch_ins.ManufactureDate = ManufactureDate
                                batch_ins.ExpiryDate = ExpiryDate
                                batch_ins.ConnectID = instance.WorkOrderMasterID
                                batch_ins.save()
                            else:
                                BatchCode = get_auto_AutoBatchCode(
                                    Batch, BranchID, CompanyID)
                                Batch.objects.create(
                                    CompanyID=CompanyID,
                                    BranchID=BranchID,
                                    ManufactureDate=ManufactureDate,
                                    ExpiryDate=ExpiryDate,
                                    BatchCode=BatchCode,
                                    StockIn=Qty_batch,
                                    PurchasePrice=BatchPurchasePrice,
                                    SalesPrice=BatchSalesPrice,
                                    PriceListID=BatchPriceListID,
                                    ProductID=ProductID,
                                    WareHouseID=WareHouseID,
                                    Description=Notes,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CreatedUserID=CreatedUserID,
                                    ConnectID=instance.WorkOrderMasterID
                                )
                        elif check_BatchCriteria == "SalesPrice":
                            if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, SalesPrice=BatchSalesPrice).exists():
                                batch_ins = Batch.objects.get(
                                    CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, SalesPrice=BatchSalesPrice)
                                StockIn = batch_ins.StockIn
                                NewStock = converted_float(StockIn) + converted_float(Qty_batch)
                                batch_ins.StockIn = NewStock
                                batch_ins.ManufactureDate = ManufactureDate
                                batch_ins.ExpiryDate = ExpiryDate
                                batch_ins.ConnectID = instance.WorkOrderMasterID
                                batch_ins.save()
                            else:
                                BatchCode = get_auto_AutoBatchCode(
                                    Batch, BranchID, CompanyID)
                                Batch.objects.create(
                                    CompanyID=CompanyID,
                                    BranchID=BranchID,
                                    ManufactureDate=ManufactureDate,
                                    ExpiryDate=ExpiryDate,
                                    BatchCode=BatchCode,
                                    StockIn=Qty_batch,
                                    PurchasePrice=BatchPurchasePrice,
                                    SalesPrice=BatchSalesPrice,
                                    PriceListID=BatchPriceListID,
                                    ProductID=ProductID,
                                    WareHouseID=WareHouseID,
                                    Description=Notes,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CreatedUserID=CreatedUserID,
                                    ConnectID=instance.WorkOrderMasterID
                                )
                        else:
                            if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=BatchPurchasePrice, SalesPrice=BatchSalesPrice).exists():
                                batch_ins = Batch.objects.get(
                                    CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=BatchPurchasePrice, SalesPrice=BatchSalesPrice)
                                StockIn = batch_ins.StockIn
                                NewStock = converted_float(StockIn) + converted_float(Qty_batch)
                                batch_ins.StockIn = NewStock
                                batch_ins.ManufactureDate = ManufactureDate
                                batch_ins.ExpiryDate = ExpiryDate
                                batch_ins.ConnectID = instance.WorkOrderMasterID
                                batch_ins.save()
                            else:
                                BatchCode = get_auto_AutoBatchCode(
                                    Batch, BranchID, CompanyID)
                                Batch.objects.create(
                                    CompanyID=CompanyID,
                                    BranchID=BranchID,
                                    ManufactureDate=ManufactureDate,
                                    ExpiryDate=ExpiryDate,
                                    BatchCode=BatchCode,
                                    StockIn=Qty_batch,
                                    PurchasePrice=BatchPurchasePrice,
                                    SalesPrice=BatchSalesPrice,
                                    PriceListID=BatchPriceListID,
                                    ProductID=ProductID,
                                    WareHouseID=WareHouseID,
                                    Description=Notes,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CreatedUserID=CreatedUserID,
                                    ConnectID=instance.WorkOrderMasterID
                                )
                    else:
                        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PriceListID=BatchPriceListID).exists():
                            batch_ins = Batch.objects.get(
                                CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PriceListID=BatchPriceListID)
                            StockIn = batch_ins.StockIn
                            NewStock = converted_float(StockIn) + converted_float(Qty_batch)
                            batch_ins.StockIn = NewStock
                            batch_ins.save()
                        else:
                            BatchCode = get_auto_AutoBatchCode(
                                Batch, BranchID, CompanyID)
                            Batch.objects.create(
                                CompanyID=CompanyID,
                                BranchID=BranchID,
                                BatchCode=BatchCode,
                                StockIn=Qty_batch,
                                PurchasePrice=PurchasePrice,
                                SalesPrice=SalesPrice,
                                PriceListID=BatchPriceListID,
                                ProductID=ProductID,
                                WareHouseID=WareHouseID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                            )

                WorkOrderMaster_Log.objects.create(
                    CompanyID=instance.CompanyID,
                    TransactionID=instance.WorkOrderMasterID,
                    BranchID=instance.BranchID,
                    Action=Action,
                    VoucherNo=instance.VoucherNo,
                    Date=Date,
                    WareHouseID=WareHouseID,
                    Notes=Notes,
                    ProductID=ProductID,
                    ProductQty=ProductQty,
                    CostPerPrice=CostPerPrice,
                    PriceListID=BatchPriceListID,
                    Amount=Amount,
                    BatchCode=BatchCode,
                    TotalQty=TotalQty,
                    ManufactureDate=ManufactureDate,
                    ExpiryDate=ExpiryDate,
                    GrandTotal=GrandTotal,
                    IsActive=IsActive,
                    CreatedDate=instance.CreatedDate,
                    UpdatedDate=today,
                    CreatedUserID=instance.CreatedUserID,
                )

                # WorkOrderMasterID = get_auto_idMaster(
                #     WorkOrderMaster, BranchID, CompanyID)
                # instance.CompanyID = CompanyID
                # instance.WorkOrderMasterID = WorkOrderMasterID
                # instance.BranchID = BranchID
                # instance.VoucherNo = VoucherNo
                instance.Action = Action
                instance.Date = Date
                instance.WareHouseID = WareHouseID
                instance.Notes = Notes
                instance.ProductID = ProductID
                instance.ProductQty = ProductQty
                instance.CostPerPrice = CostPerPrice
                instance.UnitPrice = UnitPrice
                instance.PriceListID = BatchPriceListID
                instance.Amount = Amount
                instance.TotalQty = TotalQty
                instance.GrandTotal = GrandTotal
                instance.IsActive = IsActive
                instance.ManufactureDate = ManufactureDate
                instance.ExpiryDate = ExpiryDate
                instance.UpdatedDate = today
                instance.CreatedUserID = CreatedUserID
                instance.BatchCode = BatchCode
                instance.save()

                # MultiFactor = PriceList.objects.get(
                #     CompanyID=CompanyID, PriceListID=BatchPriceListID, BranchID=BranchID).MultiFactor
                PriceListID = PriceList.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True, BranchID=BranchID).PriceListID

                # PurchasePrice = priceList.PurchasePrice
                # SalesPrice = priceList.SalesPrice

                Qty = converted_float(MultiFactor) * converted_float(ProductQty)
                Cost = converted_float(CostPerPrice) / converted_float(MultiFactor)

                # Qy = round(Qty, 4)
                # Qty = str(Qy)

                # Ct = round(Cost, 4)
                # Cost = str(Ct)

                priceList_instance = PriceList.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID, BranchID=BranchID)
                PurchasePrice = priceList_instance.PurchasePrice
                SalesPrice = priceList_instance.SalesPrice

                if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherType="WO", VoucherMasterID=instance.WorkOrderMasterID, QtyIn__gt=0).exists():
                    stock_master_ins = StockPosting.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, VoucherType="WO", VoucherMasterID=instance.WorkOrderMasterID, QtyIn__gt=0).first()
                    stock_master_ins.QtyIn = Qty
                    stock_master_ins.Action = Action
                    stock_master_ins.save()
                    update_stock(CompanyID, BranchID, ProductID)
                else:
                    StockPostingID = get_auto_stockPostid(
                        StockPosting, BranchID, CompanyID)

                    pricelist, warehouse = get_ModelInstance(
                        CompanyID, BranchID, PriceListID, WareHouseID)

                    StockPosting.objects.create(
                        StockPostingID=StockPostingID,
                        BranchID=BranchID,
                        Action=Action,
                        Date=Date,
                        VoucherMasterID=instance.WorkOrderMasterID,
                        VoucherType=VoucherType,
                        ProductID=ProductID,
                        BatchID=BatchID,
                        WareHouseID=WareHouseID,
                        QtyIn=Qty,
                        Rate=Cost,
                        PriceListID=PriceListID,
                        IsActive=IsActive,
                        CreatedDate=instance.CreatedDate,
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
                        VoucherMasterID=instance.WorkOrderMasterID,
                        VoucherType=VoucherType,
                        ProductID=ProductID,
                        BatchID=BatchID,
                        WareHouseID=WareHouseID,
                        QtyIn=Qty,
                        Rate=Cost,
                        PriceListID=PriceListID,
                        IsActive=IsActive,
                        CreatedDate=instance.CreatedDate,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                    )
                    update_stock(CompanyID, BranchID, ProductID)
                # stockRateInstance = None

                # if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WareHouseID, PriceListID=PriceListID).exists():
                #     stockRateInstance = StockRate.objects.get(
                #         CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WareHouseID, PriceListID=PriceListID)

                #     StockRateID = stockRateInstance.StockRateID
                #     stockRateInstance.Qty = converted_float(stockRateInstance.Qty) + converted_float(Qty)
                #     stockRateInstance.save()

                #     if StockTrans.objects.filter(StockRateID=StockRateID, MasterID=instance.WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                #         stockTra_in = StockTrans.objects.filter(
                #             StockRateID=StockRateID, MasterID=instance.WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                #         stockTra_in.Qty = converted_float(stockTra_in.Qty) + converted_float(Qty)
                #         stockTra_in.save()
                #     else:
                #         StockTransID = get_auto_StockTransID(
                #             StockTrans, BranchID, CompanyID)
                #         StockTrans.objects.create(
                #             StockTransID=StockTransID,
                #             BranchID=BranchID,
                #             VoucherType=VoucherType,
                #             StockRateID=StockRateID,
                #             MasterID=instance.WorkOrderMasterID,
                #             Qty=Qty,
                #             IsActive=IsActive,
                #             CompanyID=CompanyID,
                #         )

                # else:
                #     StockRateID = get_auto_StockRateID(StockRate, BranchID, CompanyID)
                #     StockRate.objects.create(
                #         StockRateID=StockRateID,
                #         BranchID=BranchID,
                #         BatchID=BatchID,
                #         PurchasePrice=PurchasePrice,
                #         SalesPrice=SalesPrice,
                #         Qty=Qty,
                #         Cost=Cost,
                #         ProductID=ProductID,
                #         WareHouseID=WareHouseID,
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
                #         MasterID=instance.WorkOrderMasterID,
                #         Qty=Qty,
                #         IsActive=IsActive,
                #         CompanyID=CompanyID,
                #     )

                deleted_datas = data["deleted_data"]
                if deleted_datas:
                    for deleted_Data in deleted_datas:
                        deleted_pk = deleted_Data['unq_id']
                        WorkOrderMasterID_Deleted = deleted_Data['WorkOrderMasterID']
                        WorkOrderDetailsID_Deleted = deleted_Data['WorkOrderDetailsID']
                        ProductID_Deleted = deleted_Data['ProductID']
                        PriceListID_Deleted = deleted_Data['PriceListID']
                        Rate_Deleted = deleted_Data['Rate']
                        WareHouseID_Deleted = deleted_Data['WarehouseID']

                        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID_Deleted, DefaultUnit=True).exists():
                            priceList = PriceList.objects.get(
                                CompanyID=CompanyID, ProductID=ProductID_Deleted, DefaultUnit=True)
                            MultiFactor = priceList.MultiFactor
                            Cost = converted_float(Rate_Deleted) / converted_float(MultiFactor)
                            Ct = round(Cost, 4)
                            Cost_Deleted = str(Ct)

                            if not deleted_pk == '' or not deleted_pk == 0:
                                if WorkOrderDetails.objects.filter(CompanyID=CompanyID, pk=deleted_pk).exists():
                                    deleted_detail = WorkOrderDetails.objects.filter(
                                        CompanyID=CompanyID, pk=deleted_pk)
                                    deleted_detail.delete()

                                    if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=WorkOrderMasterID_Deleted, VoucherDetailID=WorkOrderDetailsID_Deleted, ProductID=ProductID_Deleted, BranchID=BranchID, VoucherType="WO").exists():
                                        stock_instances_delete = StockPosting.objects.filter(
                                            CompanyID=CompanyID, VoucherMasterID=WorkOrderMasterID_Deleted, VoucherDetailID=WorkOrderDetailsID_Deleted, ProductID=ProductID_Deleted, BranchID=BranchID, VoucherType="WO")
                                        stock_instances_delete.delete()
                                        update_stock(
                                            CompanyID, BranchID, ProductID)
                                    if StockTrans.objects.filter(CompanyID=CompanyID, DetailID=WorkOrderDetailsID_Deleted, MasterID=WorkOrderMasterID_Deleted, BranchID=BranchID, VoucherType=VoucherType, IsActive=True).exists():
                                        stockTrans_instance = StockTrans.objects.filter(
                                            CompanyID=CompanyID, DetailID=WorkOrderDetailsID_Deleted, MasterID=WorkOrderMasterID_Deleted, BranchID=BranchID, VoucherType=VoucherType, IsActive=True)
                                        for stck in stockTrans_instance:
                                            StockRateID = stck.StockRateID
                                            stck.IsActive = False
                                            qty_in_stockTrans = stck.Qty
                                            if StockRate.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, BranchID=BranchID).exists():
                                                stockRateInstance = StockRate.objects.get(
                                                    CompanyID=CompanyID, StockRateID=StockRateID, BranchID=BranchID)
                                                stockRateInstance.Qty = converted_float(
                                                    stockRateInstance.Qty) + converted_float(qty_in_stockTrans)
                                                stockRateInstance.save()
                                            stck.save()

                WorkOrderDetails_ins = data["WorkOrderDetails"]

                for WorkOrderDetail in WorkOrderDetails_ins:
                    pk = WorkOrderDetail['id']
                    ProductID = WorkOrderDetail['ProductID']
                    if ProductID:
                        Qty = converted_float(WorkOrderDetail['Qty'])
                        DetailPriceListID = WorkOrderDetail['PriceListID']
                        CostPerPrice = converted_float(WorkOrderDetail['CostPerItem'])
                        UnitPrice = converted_float(WorkOrderDetail['UnitPrice'])
                        DetailPurchasePrice = converted_float(
                            WorkOrderDetail['PurchasePrice'])
                        DetailSalesPrice = converted_float(WorkOrderDetail['UnitPrice'])
                        Amount = converted_float(WorkOrderDetail['NetAmount'])
                        BatchCode = converted_float(WorkOrderDetail['BatchCode'])
                        InclusivePrice = converted_float(
                            WorkOrderDetail['InclusivePrice'])
                        is_inclusive = WorkOrderDetail['is_inclusive']
                        detailID = WorkOrderDetail['detailID']

                        DetailQty = Qty
                        # UnitPrice = round(UnitPrice, PriceRounding)
                        # CostPerPrice = round(CostPerPrice, PriceRounding)
                        # DetailPurchasePrice = round(DetailPurchasePrice, PriceRounding)
                        # DetailSalesPrice = round(DetailSalesPrice, PriceRounding)
                        # Amount = round(Amount, PriceRounding)

                        # WorkOrderDetailsID = get_auto_id(
                        # WorkOrderDetails, BranchID, CompanyID)
                        if is_inclusive == True:
                            DetailSalesPrice = str(InclusivePrice)
                        else:
                            DetailSalesPrice = str(UnitPrice)

                        DetailPurchasePrice = str(DetailPurchasePrice)

                        PriceListID_DefUnit = PriceList.objects.get(
                            CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).PriceListID

                        MultiFactor = PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=DetailPriceListID, BranchID=BranchID).MultiFactor
                        Cost = converted_float(CostPerPrice) / converted_float(MultiFactor)

                        # qty_batch = converted_float(FreeQty) + converted_float(Qty)
                        Qty_batch = converted_float(MultiFactor) * converted_float(DetailQty)

                        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
                            check_EnableProductBatchWise = GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue

                            check_BatchCriteria = "PurchasePriceAndSalesPrice"
                            # if GeneralSettings.objects.filter(
                            #         CompanyID=CompanyID, SettingsType="BatchCriteria").exists():
                            #     check_BatchCriteria = GeneralSettings.objects.get(
                            #         CompanyID=CompanyID, SettingsType="BatchCriteria").SettingsValue

                            if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                                if check_BatchCriteria == "PurchasePrice":
                                    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=DetailPurchasePrice).exists():
                                        batch_ins = Batch.objects.get(
                                            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=DetailPurchasePrice)
                                        StockOut = batch_ins.StockOut
                                        NewStock = converted_float(
                                            StockOut) + converted_float(Qty_batch)
                                        batch_ins.StockOut = NewStock
                                        # batch_ins.ManufactureDate = ManufactureDate
                                        # batch_ins.ExpiryDate = ExpiryDate
                                        batch_ins.ConnectID = WorkOrderMasterID
                                        batch_ins.save()
                                    else:
                                        BatchCode = get_auto_AutoBatchCode(
                                            Batch, BranchID, CompanyID)
                                        Batch.objects.create(
                                            CompanyID=CompanyID,
                                            BranchID=BranchID,
                                            BatchCode=BatchCode,
                                            StockOut=Qty_batch,
                                            PurchasePrice=DetailPurchasePrice,
                                            SalesPrice=DetailSalesPrice,
                                            PriceListID=DetailPriceListID,
                                            ProductID=ProductID,
                                            WareHouseID=WareHouseID,
                                            Description=Notes,
                                            CreatedDate=today,
                                            UpdatedDate=today,
                                            CreatedUserID=CreatedUserID,
                                            ConnectID=WorkOrderMasterID
                                        )
                                elif check_BatchCriteria == "SalesPrice":
                                    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, SalesPrice=DetailSalesPrice).exists():
                                        batch_ins = Batch.objects.get(
                                            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, SalesPrice=DetailSalesPrice)
                                        StockOut = batch_ins.StockOut
                                        NewStock = converted_float(
                                            StockOut) + converted_float(Qty_batch)
                                        batch_ins.StockOut = NewStock
                                        # batch_ins.ManufactureDate = ManufactureDate
                                        # batch_ins.ExpiryDate = ExpiryDate
                                        batch_ins.ConnectID = WorkOrderMasterID
                                        batch_ins.save()
                                    else:
                                        BatchCode = get_auto_AutoBatchCode(
                                            Batch, BranchID, CompanyID)
                                        Batch.objects.create(
                                            CompanyID=CompanyID,
                                            BranchID=BranchID,
                                            BatchCode=BatchCode,
                                            StockOut=Qty_batch,
                                            PurchasePrice=DetailPurchasePrice,
                                            SalesPrice=DetailSalesPrice,
                                            PriceListID=DetailPriceListID,
                                            ProductID=ProductID,
                                            WareHouseID=WareHouseID,
                                            Description=Notes,
                                            CreatedDate=today,
                                            UpdatedDate=today,
                                            CreatedUserID=CreatedUserID,
                                            ConnectID=WorkOrderMasterID

                                        )
                                else:
                                    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=DetailPurchasePrice, SalesPrice=DetailSalesPrice).exists():
                                        batch_ins = Batch.objects.get(
                                            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=DetailPurchasePrice, SalesPrice=DetailSalesPrice)
                                        StockOut = batch_ins.StockOut
                                        NewStock = converted_float(
                                            StockOut) + converted_float(Qty_batch)
                                        batch_ins.StockOut = NewStock
                                        # batch_ins.ManufactureDate = ManufactureDate
                                        # batch_ins.ExpiryDate = ExpiryDate
                                        batch_ins.ConnectID = WorkOrderMasterID
                                        batch_ins.save()
                                    else:
                                        BatchCode = get_auto_AutoBatchCode(
                                            Batch, BranchID, CompanyID)
                                        Batch.objects.create(
                                            CompanyID=CompanyID,
                                            BranchID=BranchID,
                                            BatchCode=BatchCode,
                                            StockOut=Qty_batch,
                                            PurchasePrice=DetailPurchasePrice,
                                            SalesPrice=DetailSalesPrice,
                                            PriceListID=DetailPriceListID,
                                            ProductID=ProductID,
                                            WareHouseID=WareHouseID,
                                            Description=Notes,
                                            CreatedDate=today,
                                            UpdatedDate=today,
                                            CreatedUserID=CreatedUserID,
                                            ConnectID=WorkOrderMasterID
                                        )
                            else:
                                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PriceListID=PriceListID).exists():
                                    batch_ins = Batch.objects.get(
                                        CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PriceListID=PriceListID)
                                    StockOut = batch_ins.StockOut
                                    NewStock = converted_float(
                                        StockOut) + converted_float(Qty_batch)
                                    batch_ins.StockOut = NewStock
                                    batch_ins.save()
                                else:
                                    BatchCode = get_auto_AutoBatchCode(
                                        Batch, BranchID, CompanyID)
                                    Batch.objects.create(
                                        CompanyID=CompanyID,
                                        BranchID=BranchID,
                                        BatchCode=BatchCode,
                                        StockOut=Qty_batch,
                                        PurchasePrice=PurchasePrice,
                                        SalesPrice=SalesPrice,
                                        PriceListID=PriceListID,
                                        ProductID=ProductID,
                                        WareHouseID=WareHouseID,
                                        CreatedDate=today,
                                        UpdatedDate=today,
                                        CreatedUserID=CreatedUserID,
                                    )

                        if detailID == 0:
                            workorder_details_instance = WorkOrderDetails.objects.get(
                                CompanyID=CompanyID, pk=pk)
                            WorkOrderDetailsID = workorder_details_instance.WorkOrderDetailsID

                            log_instance = WorkOrderDetails_Log.objects.create(
                                CompanyID=CompanyID,
                                TransactionID=WorkOrderDetailsID,
                                BranchID=BranchID,
                                Action=Action,
                                WorkOrderMasterID=WorkOrderMasterID,
                                ProductID=ProductID,
                                Qty=DetailQty,
                                PriceListID=DetailPriceListID,
                                CostPerPrice=CostPerPrice,
                                Amount=Amount,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                BatchCode=BatchCode
                            )

                            # workorder_details_instance.CompanyID = CompanyID
                            # workorder_details_instance.WorkOrderDetailsID = WorkOrderDetailsID
                            # workorder_details_instance.BranchID = BranchID
                            workorder_details_instance.Action = Action
                            workorder_details_instance.WorkOrderMasterID = WorkOrderMasterID
                            workorder_details_instance.ProductID = ProductID
                            workorder_details_instance.Qty = DetailQty
                            workorder_details_instance.PriceListID = DetailPriceListID
                            workorder_details_instance.CostPerPrice = CostPerPrice
                            workorder_details_instance.UnitPrice = UnitPrice
                            workorder_details_instance.Amount = Amount
                            workorder_details_instance.CreatedDate = workorder_details_instance.CreatedDate
                            workorder_details_instance.UpdatedDate = today
                            workorder_details_instance.BatchCode = BatchCode
                            workorder_details_instance.LogID = log_instance.ID
                            # workorder_details_instance.CreatedUserID = CreatedUserID
                            workorder_details_instance.save()

                            pricelist, warehouse = get_ModelInstance(
                                CompanyID, BranchID, PriceListID_DefUnit, WareHouseID)

                            if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WareHouseID, VoucherMasterID=WorkOrderMasterID, VoucherDetailID=WorkOrderDetailsID, BranchID=BranchID, VoucherType="WO", ProductID=ProductID).exists():
                                stock_instance = StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WareHouseID, VoucherMasterID=WorkOrderMasterID,
                                                                             VoucherDetailID=WorkOrderDetailsID, BranchID=BranchID, VoucherType="WO", ProductID=ProductID).first()
                                stock_instance.QtyOut = Qty_batch
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
                                    Date=Date,
                                    VoucherMasterID=WorkOrderMasterID,
                                    VoucherDetailID=WorkOrderDetailsID,
                                    VoucherType=VoucherType,
                                    ProductID=ProductID,
                                    BatchID=BatchID,
                                    WareHouseID=WareHouseID,
                                    QtyOut=Qty_batch,
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
                                    Date=Date,
                                    VoucherMasterID=WorkOrderMasterID,
                                    VoucherDetailID=WorkOrderDetailsID,
                                    VoucherType=VoucherType,
                                    ProductID=ProductID,
                                    BatchID=BatchID,
                                    WareHouseID=WareHouseID,
                                    QtyOut=Qty_batch,
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
                            WorkOrderDetailsID = get_auto_id(
                                WorkOrderDetails, BranchID, CompanyID)
                            log_instance = WorkOrderDetails_Log.objects.create(
                                CompanyID=CompanyID,
                                TransactionID=WorkOrderDetailsID,
                                BranchID=BranchID,
                                Action=Action,
                                WorkOrderMasterID=WorkOrderMasterID,
                                ProductID=ProductID,
                                BatchCode=BatchCode,
                                Qty=DetailQty,
                                PriceListID=DetailPriceListID,
                                CostPerPrice=CostPerPrice,
                                UnitPrice=UnitPrice,
                                Amount=Amount,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                            )

                            WorkOrderDetails.objects.create(
                                CompanyID=CompanyID,
                                WorkOrderDetailsID=WorkOrderDetailsID,
                                BranchID=BranchID,
                                Action=Action,
                                WorkOrderMasterID=WorkOrderMasterID,
                                ProductID=ProductID,
                                BatchCode=BatchCode,
                                Qty=DetailQty,
                                PriceListID=DetailPriceListID,
                                CostPerPrice=CostPerPrice,
                                UnitPrice=UnitPrice,
                                Amount=Amount,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                LogID=log_instance.ID
                            )

                            MultiFactor = PriceList.objects.get(
                                CompanyID=CompanyID, PriceListID=DetailPriceListID, BranchID=BranchID).MultiFactor
                            PriceListID_DefUnit = PriceList.objects.get(
                                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True, BranchID=BranchID).PriceListID

                            # PriceListID_DefUnit = priceList.PriceListID
                            # MultiFactor = priceList.MultiFactor

                            # PurchasePrice = priceList.PurchasePrice
                            # SalesPrice = priceList.SalesPrice
                            DetailQty = DetailQty

                            Qty = converted_float(MultiFactor) * converted_float(DetailQty)
                            Cost = converted_float(CostPerPrice) / converted_float(MultiFactor)

                            # Qy = round(Qty, 4)
                            # Qty = str(Qy)

                            # Ct = round(Cost, 4)
                            # Cost = str(Ct)

                            priceList_instance = PriceList.objects.get(
                                CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID_DefUnit, BranchID=BranchID)
                            PurchasePrice = priceList_instance.PurchasePrice
                            SalesPrice = priceList_instance.SalesPrice

                            StockPostingID = get_auto_stockPostid(
                                StockPosting, BranchID, CompanyID)
                            pricelist, warehouse = get_ModelInstance(
                                CompanyID, BranchID, PriceListID_DefUnit, PriceListID_DefUnit)

                            StockPosting.objects.create(
                                StockPostingID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=Date,
                                VoucherMasterID=WorkOrderMasterID,
                                VoucherDetailID=WorkOrderDetailsID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                BatchID=BatchID,
                                WareHouseID=WareHouseID,
                                QtyOut=Qty,
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
                                Date=Date,
                                VoucherMasterID=WorkOrderMasterID,
                                VoucherDetailID=WorkOrderDetailsID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                BatchID=BatchID,
                                WareHouseID=WareHouseID,
                                QtyOut=Qty,
                                Rate=Cost,
                                PriceListID=PriceListID_DefUnit,
                                IsActive=IsActive,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                            )

                            update_stock(CompanyID, BranchID, ProductID)

                        # changQty = Qty
                        # if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WareHouseID, Qty__gt=0, PriceListID=PriceListID_DefUnit).exists():
                        #     stockRate_instances = StockRate.objects.filter(
                        #         CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WareHouseID, Qty__gt=0, PriceListID=PriceListID_DefUnit)
                        #     count = stockRate_instances.count()
                        #     last = 0
                        #     for stockRate_instance in stockRate_instances:
                        #         last = converted_float(last) + converted_float(1)
                        #         StockRateID = stockRate_instance.StockRateID
                        #         stock_post_cost = stockRate_instance.Cost
                        #         if converted_float(stockRate_instance.Qty) > converted_float(Qty):
                        #             stockRate_instance.Qty = converted_float(
                        #                 stockRate_instance.Qty) - converted_float(Qty)
                        #             changQty = 0
                        #             stockRate_instance.save()

                        #             if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                        #                                            VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit).exists():
                        #                 stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                        #                                                               VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit)
                        #                 QtyOut = stockPost_instance.QtyOut
                        #                 newQty = converted_float(QtyOut) + converted_float(Qty)

                        #                 stockPost_instance.QtyOut = newQty
                        #                 stockPost_instance.save()
                        #             else:
                        #                 StockPostingID = get_auto_stockPostid(
                        #                     StockPosting, BranchID, CompanyID)
                        #                 StockPosting.objects.create(
                        #                     StockPostingID=StockPostingID,
                        #                     BranchID=BranchID,
                        #                     Action=Action,
                        #                     Date=Date,
                        #                     VoucherMasterID=WorkOrderMasterID,
                        #                     VoucherType=VoucherType,
                        #                     ProductID=ProductID,
                        #                     BatchID=BatchID,
                        #                     WareHouseID=WareHouseID,
                        #                     QtyOut=Qty,
                        #                     Rate=stock_post_cost,
                        #                     PriceListID=PriceListID_DefUnit,
                        #                     IsActive=IsActive,
                        #                     CreatedDate=today,
                        #                     UpdatedDate=today,
                        #                     CreatedUserID=CreatedUserID,
                        #                     CompanyID=CompanyID,
                        #                 )

                        #                 StockPosting_Log.objects.create(
                        #                     TransactionID=StockPostingID,
                        #                     BranchID=BranchID,
                        #                     Action=Action,
                        #                     Date=Date,
                        #                     VoucherMasterID=WorkOrderMasterID,
                        #                     VoucherType=VoucherType,
                        #                     ProductID=ProductID,
                        #                     BatchID=BatchID,
                        #                     WareHouseID=WareHouseID,
                        #                     QtyOut=Qty,
                        #                     Rate=stock_post_cost,
                        #                     PriceListID=PriceListID_DefUnit,
                        #                     IsActive=IsActive,
                        #                     CreatedDate=today,
                        #                     UpdatedDate=today,
                        #                     CreatedUserID=CreatedUserID,
                        #                     CompanyID=CompanyID,
                        #                 )

                        #             if StockTrans.objects.filter(StockRateID=StockRateID, DetailID=WorkOrderDetailsID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                        #                 stockTra_in = StockTrans.objects.filter(
                        #                     StockRateID=StockRateID, DetailID=WorkOrderDetailsID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                        #                 stockTra_in.Qty = converted_float(
                        #                     stockTra_in.Qty) + converted_float(Qty)
                        #                 stockTra_in.save()
                        #             else:
                        #                 StockTransID = get_auto_StockTransID(
                        #                     StockTrans, BranchID, CompanyID)
                        #                 StockTrans.objects.create(
                        #                     StockTransID=StockTransID,
                        #                     BranchID=BranchID,
                        #                     VoucherType=VoucherType,
                        #                     StockRateID=StockRateID,
                        #                     DetailID=WorkOrderDetailsID,
                        #                     MasterID=WorkOrderMasterID,
                        #                     Qty=Qty,
                        #                     IsActive=IsActive,
                        #                     CompanyID=CompanyID,
                        #                 )
                        #         elif converted_float(stockRate_instance.Qty) < converted_float(Qty):

                        #             if converted_float(changQty) > converted_float(stockRate_instance.Qty):
                        #                 changQty = converted_float(changQty) - \
                        #                     converted_float(stockRate_instance.Qty)
                        #                 stckQty = stockRate_instance.Qty
                        #                 stockRate_instance.Qty = 0
                        #                 stockRate_instance.save()

                        #                 if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                        #                                                VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit).exists():
                        #                     stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                        #                                                                   VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit)
                        #                     QtyOut = stockPost_instance.QtyOut
                        #                     newQty = converted_float(QtyOut) + \
                        #                         converted_float(stockRate_instance.Qty)
                        #                     stockPost_instance.QtyOut = newQty
                        #                     stockPost_instance.save()
                        #                 else:
                        #                     StockPostingID = get_auto_stockPostid(
                        #                         StockPosting, BranchID, CompanyID)
                        #                     StockPosting.objects.create(
                        #                         StockPostingID=StockPostingID,
                        #                         BranchID=BranchID,
                        #                         Action=Action,
                        #                         Date=Date,
                        #                         VoucherMasterID=WorkOrderMasterID,
                        #                         VoucherType=VoucherType,
                        #                         ProductID=ProductID,
                        #                         BatchID=BatchID,
                        #                         WareHouseID=WareHouseID,
                        #                         QtyOut=stckQty,
                        #                         Rate=stock_post_cost,
                        #                         PriceListID=PriceListID_DefUnit,
                        #                         IsActive=IsActive,
                        #                         CreatedDate=today,
                        #                         UpdatedDate=today,
                        #                         CreatedUserID=CreatedUserID,
                        #                         CompanyID=CompanyID,
                        #                     )

                        #                     StockPosting_Log.objects.create(
                        #                         TransactionID=StockPostingID,
                        #                         BranchID=BranchID,
                        #                         Action=Action,
                        #                         Date=Date,
                        #                         VoucherMasterID=WorkOrderMasterID,
                        #                         VoucherType=VoucherType,
                        #                         ProductID=ProductID,
                        #                         BatchID=BatchID,
                        #                         WareHouseID=WareHouseID,
                        #                         QtyOut=stckQty,
                        #                         Rate=stock_post_cost,
                        #                         PriceListID=PriceListID_DefUnit,
                        #                         IsActive=IsActive,
                        #                         CreatedDate=today,
                        #                         UpdatedDate=today,
                        #                         CreatedUserID=CreatedUserID,
                        #                         CompanyID=CompanyID,
                        #                     )
                        #                 if StockTrans.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, DetailID=WorkOrderDetailsID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                        #                     stockTra_in = StockTrans.objects.filter(
                        #                         CompanyID=CompanyID, StockRateID=StockRateID, DetailID=WorkOrderDetailsID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                        #                     stockTra_in.Qty = converted_float(
                        #                         stockTra_in.Qty) + converted_float(stockRate_instance.Qty)
                        #                     stockTra_in.save()
                        #                 else:
                        #                     StockTransID = get_auto_StockTransID(
                        #                         StockTrans, BranchID, CompanyID)
                        #                     StockTrans.objects.create(
                        #                         StockTransID=StockTransID,
                        #                         BranchID=BranchID,
                        #                         VoucherType=VoucherType,
                        #                         StockRateID=StockRateID,
                        #                         DetailID=WorkOrderDetailsID,
                        #                         MasterID=WorkOrderMasterID,
                        #                         Qty=stockRate_instance.Qty,
                        #                         IsActive=IsActive,
                        #                         CompanyID=CompanyID,
                        #                     )
                        #             else:
                        #                 if changQty < 0:
                        #                     changQty = 0
                        #                 chqty = changQty
                        #                 changQty = converted_float(
                        #                     stockRate_instance.Qty) - converted_float(changQty)
                        #                 stockRate_instance.Qty = changQty
                        #                 changQty = 0
                        #                 stockRate_instance.save()

                        #                 if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                        #                                                VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit).exists():
                        #                     stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                        #                                                                   VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit)
                        #                     QtyOut = stockPost_instance.QtyOut
                        #                     newQty = converted_float(QtyOut) + converted_float(chqty)
                        #                     stockPost_instance.QtyOut = newQty
                        #                     stockPost_instance.save()
                        #                 else:
                        #                     StockPostingID = get_auto_stockPostid(
                        #                         StockPosting, BranchID, CompanyID)
                        #                     StockPosting.objects.create(
                        #                         StockPostingID=StockPostingID,
                        #                         BranchID=BranchID,
                        #                         Action=Action,
                        #                         Date=Date,
                        #                         VoucherMasterID=WorkOrderMasterID,
                        #                         VoucherType=VoucherType,
                        #                         ProductID=ProductID,
                        #                         BatchID=BatchID,
                        #                         WareHouseID=WareHouseID,
                        #                         QtyOut=chqty,
                        #                         Rate=stock_post_cost,
                        #                         PriceListID=PriceListID_DefUnit,
                        #                         IsActive=IsActive,
                        #                         CreatedDate=today,
                        #                         UpdatedDate=today,
                        #                         CreatedUserID=CreatedUserID,
                        #                         CompanyID=CompanyID,
                        #                     )

                        #                     StockPosting_Log.objects.create(
                        #                         TransactionID=StockPostingID,
                        #                         BranchID=BranchID,
                        #                         Action=Action,
                        #                         Date=Date,
                        #                         VoucherMasterID=WorkOrderMasterID,
                        #                         VoucherType=VoucherType,
                        #                         ProductID=ProductID,
                        #                         BatchID=BatchID,
                        #                         WareHouseID=WareHouseID,
                        #                         QtyOut=chqty,
                        #                         Rate=stock_post_cost,
                        #                         PriceListID=PriceListID_DefUnit,
                        #                         IsActive=IsActive,
                        #                         CreatedDate=today,
                        #                         UpdatedDate=today,
                        #                         CreatedUserID=CreatedUserID,
                        #                         CompanyID=CompanyID,
                        #                     )

                        #                 if StockTrans.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, DetailID=WorkOrderDetailsID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                        #                     stockTra_in = StockTrans.objects.filter(
                        #                         CompanyID=CompanyID, StockRateID=StockRateID, DetailID=WorkOrderDetailsID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                        #                     stockTra_in.Qty = converted_float(
                        #                         stockTra_in.Qty) + converted_float(chqty)
                        #                     stockTra_in.save()
                        #                 else:
                        #                     StockTransID = get_auto_StockTransID(
                        #                         StockTrans, BranchID, CompanyID)
                        #                     StockTrans.objects.create(
                        #                         StockTransID=StockTransID,
                        #                         BranchID=BranchID,
                        #                         VoucherType=VoucherType,
                        #                         StockRateID=StockRateID,
                        #                         DetailID=WorkOrderDetailsID,
                        #                         MasterID=WorkOrderMasterID,
                        #                         Qty=chqty,
                        #                         IsActive=IsActive,
                        #                         CompanyID=CompanyID,
                        #                     )

                        #         elif converted_float(stockRate_instance.Qty) == converted_float(Qty):
                        #             stockRate_instance.Qty = 0
                        #             changQty = 0
                        #             stockRate_instance.save()

                        #             if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                        #                                            VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit).exists():
                        #                 stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                        #                                                               VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit)
                        #                 QtyOut = stockPost_instance.QtyOut
                        #                 newQty = converted_float(QtyOut) + \
                        #                     converted_float(Qty)
                        #                 stockPost_instance.QtyOut = newQty
                        #                 stockPost_instance.save()
                        #             else:
                        #                 StockPostingID = get_auto_stockPostid(
                        #                     StockPosting, BranchID, CompanyID)
                        #                 StockPosting.objects.create(
                        #                     StockPostingID=StockPostingID,
                        #                     BranchID=BranchID,
                        #                     Action=Action,
                        #                     Date=Date,
                        #                     VoucherMasterID=WorkOrderMasterID,
                        #                     VoucherType=VoucherType,
                        #                     ProductID=ProductID,
                        #                     BatchID=BatchID,
                        #                     WareHouseID=WareHouseID,
                        #                     QtyOut=Qty,
                        #                     Rate=stock_post_cost,
                        #                     PriceListID=PriceListID_DefUnit,
                        #                     IsActive=IsActive,
                        #                     CreatedDate=today,
                        #                     UpdatedDate=today,
                        #                     CreatedUserID=CreatedUserID,
                        #                     CompanyID=CompanyID,
                        #                 )

                        #                 StockPosting_Log.objects.create(
                        #                     TransactionID=StockPostingID,
                        #                     BranchID=BranchID,
                        #                     Action=Action,
                        #                     Date=Date,
                        #                     VoucherMasterID=WorkOrderMasterID,
                        #                     VoucherType=VoucherType,
                        #                     ProductID=ProductID,
                        #                     BatchID=BatchID,
                        #                     WareHouseID=WareHouseID,
                        #                     QtyOut=Qty,
                        #                     Rate=stock_post_cost,
                        #                     PriceListID=PriceListID_DefUnit,
                        #                     IsActive=IsActive,
                        #                     CreatedDate=today,
                        #                     UpdatedDate=today,
                        #                     CreatedUserID=CreatedUserID,
                        #                     CompanyID=CompanyID,
                        #                 )

                        #             if StockTrans.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, DetailID=WorkOrderDetailsID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                        #                 stockTra_in = StockTrans.objects.filter(
                        #                     CompanyID=CompanyID, StockRateID=StockRateID, DetailID=WorkOrderDetailsID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                        #                 stockTra_in.Qty = converted_float(
                        #                     stockTra_in.Qty) + converted_float(Qty)
                        #                 stockTra_in.save()
                        #             else:
                        #                 StockTransID = get_auto_StockTransID(
                        #                     StockTrans, BranchID, CompanyID)
                        #                 StockTrans.objects.create(
                        #                     StockTransID=StockTransID,
                        #                     BranchID=BranchID,
                        #                     VoucherType=VoucherType,
                        #                     StockRateID=StockRateID,
                        #                     DetailID=WorkOrderDetailsID,
                        #                     MasterID=WorkOrderMasterID,
                        #                     Qty=Qty,
                        #                     IsActive=IsActive,
                        #                     CompanyID=CompanyID,
                        #                 )

                        # if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, Cost=Cost, WareHouseID=WareHouseID, Qty__lte=0, PriceListID=PriceListID_DefUnit).exists():
                        #     stockRate_instance = StockRate.objects.filter(
                        #         CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, Cost=Cost, WareHouseID=WareHouseID, Qty__lte=0, PriceListID=PriceListID_DefUnit).first()
                        #     stock_post_cost = stockRate_instance.Cost
                        #     if converted_float(changQty) > 0:
                        #         stockRate_instance.Qty = converted_float(
                        #             stockRate_instance.Qty) - converted_float(changQty)
                        #         stockRate_instance.save()

                        #         if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                        #                                        VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit).exists():
                        #             stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                        #                                                           VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit)
                        #             QtyOut = stockPost_instance.QtyOut
                        #             newQty = converted_float(QtyOut) + converted_float(changQty)
                        #             stockPost_instance.QtyOut = newQty
                        #             stockPost_instance.save()
                        #         else:
                        #             StockPostingID = get_auto_stockPostid(
                        #                 StockPosting, BranchID, CompanyID)
                        #             StockPosting.objects.create(
                        #                 StockPostingID=StockPostingID,
                        #                 BranchID=BranchID,
                        #                 Action=Action,
                        #                 Date=Date,
                        #                 VoucherMasterID=WorkOrderMasterID,
                        #                 VoucherType=VoucherType,
                        #                 ProductID=ProductID,
                        #                 BatchID=BatchID,
                        #                 WareHouseID=WareHouseID,
                        #                 QtyOut=changQty,
                        #                 Rate=stock_post_cost,
                        #                 PriceListID=PriceListID_DefUnit,
                        #                 IsActive=IsActive,
                        #                 CreatedDate=today,
                        #                 UpdatedDate=today,
                        #                 CreatedUserID=CreatedUserID,
                        #                 CompanyID=CompanyID,
                        #             )

                        #             StockPosting_Log.objects.create(
                        #                 TransactionID=StockPostingID,
                        #                 BranchID=BranchID,
                        #                 Action=Action,
                        #                 Date=Date,
                        #                 VoucherMasterID=WorkOrderMasterID,
                        #                 VoucherType=VoucherType,
                        #                 ProductID=ProductID,
                        #                 BatchID=BatchID,
                        #                 WareHouseID=WareHouseID,
                        #                 QtyOut=changQty,
                        #                 Rate=stock_post_cost,
                        #                 PriceListID=PriceListID_DefUnit,
                        #                 IsActive=IsActive,
                        #                 CreatedDate=today,
                        #                 UpdatedDate=today,
                        #                 CreatedUserID=CreatedUserID,
                        #                 CompanyID=CompanyID,
                        #             )

                        #         if not StockTrans.objects.filter(CompanyID=CompanyID,
                        #                                          StockRateID=stockRate_instance.StockRateID,
                        #                                          DetailID=WorkOrderDetailsID,
                        #                                          MasterID=WorkOrderMasterID,
                        #                                          VoucherType=VoucherType,
                        #                                          BranchID=BranchID).exists():

                        #             StockTransID = get_auto_StockTransID(
                        #                 StockTrans, BranchID, CompanyID)
                        #             StockTrans.objects.create(
                        #                 CompanyID=CompanyID,
                        #                 StockTransID=StockTransID,
                        #                 BranchID=BranchID,
                        #                 VoucherType=VoucherType,
                        #                 StockRateID=stockRate_instance.StockRateID,
                        #                 DetailID=WorkOrderDetailsID,
                        #                 MasterID=WorkOrderMasterID,
                        #                 Qty=changQty,
                        #                 IsActive=IsActive
                        #             )
                        # else:
                        #     if converted_float(changQty) > 0:
                        #         qty = converted_float(Qty) * -1
                        #         StockRateID = get_auto_StockRateID(
                        #             StockRate, BranchID, CompanyID)
                        #         StockRate.objects.create(
                        #             StockRateID=StockRateID,
                        #             BranchID=BranchID,
                        #             BatchID=BatchID,
                        #             PurchasePrice=PurchasePrice,
                        #             SalesPrice=SalesPrice,
                        #             Qty=qty,
                        #             Cost=Cost,
                        #             ProductID=ProductID,
                        #             WareHouseID=WareHouseID,
                        #             Date=Date,
                        #             PriceListID=PriceListID_DefUnit,
                        #             CreatedUserID=CreatedUserID,
                        #             CreatedDate=today,
                        #             UpdatedDate=today,
                        #             CompanyID=CompanyID,
                        #         )

                        #         StockPostingID = get_auto_stockPostid(
                        #             StockPosting, BranchID, CompanyID)
                        #         StockPosting.objects.create(
                        #             StockPostingID=StockPostingID,
                        #             BranchID=BranchID,
                        #             Action=Action,
                        #             Date=Date,
                        #             VoucherMasterID=WorkOrderMasterID,
                        #             VoucherType=VoucherType,
                        #             ProductID=ProductID,
                        #             BatchID=BatchID,
                        #             WareHouseID=WareHouseID,
                        #             QtyOut=Qty,
                        #             Rate=Cost,
                        #             PriceListID=PriceListID_DefUnit,
                        #             IsActive=IsActive,
                        #             CreatedDate=today,
                        #             UpdatedDate=today,
                        #             CreatedUserID=CreatedUserID,
                        #             CompanyID=CompanyID,
                        #         )

                        #         StockPosting_Log.objects.create(
                        #             TransactionID=StockPostingID,
                        #             BranchID=BranchID,
                        #             Action=Action,
                        #             Date=Date,
                        #             VoucherMasterID=WorkOrderMasterID,
                        #             VoucherType=VoucherType,
                        #             ProductID=ProductID,
                        #             BatchID=BatchID,
                        #             WareHouseID=WareHouseID,
                        #             QtyOut=Qty,
                        #             Rate=Cost,
                        #             PriceListID=PriceListID_DefUnit,
                        #             IsActive=IsActive,
                        #             CreatedDate=today,
                        #             UpdatedDate=today,
                        #             CreatedUserID=CreatedUserID,
                        #             CompanyID=CompanyID,
                        #         )
                        #         StockTransID = get_auto_StockTransID(
                        #             StockTrans, BranchID, CompanyID)
                        #         StockTrans.objects.create(
                        #             StockTransID=StockTransID,
                        #             BranchID=BranchID,
                        #             VoucherType=VoucherType,
                        #             StockRateID=StockRateID,
                        #             DetailID=WorkOrderDetailsID,
                        #             MasterID=WorkOrderMasterID,
                        #             Qty=Qty,
                        #             IsActive=IsActive,
                        #             CompanyID=CompanyID,
                        #         )

                #request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Work Order',
                #              'Create', 'Work Order created successfully.', 'Work Order saved successfully.')

                response_data = {
                    "StatusCode": 6000,
                    "id": instance.id,
                    "message": "Work Order created Successfully!!!",
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Work Order',
                             'Create', 'Work Order created Failed.', 'VoucherNo already exist')
                response_data = {
                    "StatusCode": 6001,
                    "message": "VoucherNo already exist!"
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

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Work Order',
                     'Edit', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def workorders(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if WorkOrderMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instances = WorkOrderMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
            serialized = serializers.WorkOrderSerializer(instances, many=True, context={
                "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding})

            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Workorder',
            #              'List', 'Workorder List Viewed successfully.', 'Workorder List Viewed successfully.')
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Workorder',
                         'List', 'Workorder List Viewed Failed.', 'Workorder Not Found in this Branch!')
            response_data = {
                "StatusCode": 6001,
                "message": "Workorder Not Found in this Branch!!"
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
def workorder(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    if WorkOrderMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = WorkOrderMaster.objects.get(CompanyID=CompanyID, pk=pk)
        serialized = serializers.WorkOrderSerializer(instance, context={
            "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding})

        #request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Workorder',
        #              'View', 'Workorder Single Viewed successfully.', 'Workorder Single Viewed successfully.')
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID,
                     'Workorder', 'View', 'Workorder Single Viewed Failed.', 'Workorder Not Found.')
        response_data = {
            "StatusCode": 6001,
            "message": "Workorder Not Found!"
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


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def workorders_scroll(request):
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
            product_object = WorkOrderMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)

            product_sort_pagination = list_pagination(
                product_object,
                items_per_page,
                page_number
            )
            product_serializer = serializers.WorkOrder1Serializer(
                product_sort_pagination,
                many=True,
                context={
                    "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding}
            )
            data = product_serializer.data
            if not data == None:
                response_data = {
                    "StatusCode": 6000,
                    "data": data,
                    "count": len(product_object)
                }
    else:
        response_data = {
            "StatusCode": 6001
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def workorders_search(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    selectedkey = data['selectedkey']
    length = data['length']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if WorkOrderMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            if length < 3:
                instances = WorkOrderMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)
                instances = instances.filter((Q(VoucherNo__icontains=selectedkey)) | (
                    Q(WorkOrderMasterID__icontains=selectedkey)))[:10]
            else:
                instances = WorkOrderMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)
                instances = instances.filter((Q(VoucherNo__icontains=selectedkey)) | (
                    Q(WorkOrderMasterID__icontains=selectedkey)))
            serialized = serializers.WorkOrderSerializer(instances, many=True, context={
                "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding, })

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
def delete_workorder(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    try:
        selecte_ids = data['selecte_ids']
    except:
        selecte_ids = []

    today = datetime.datetime.now()
    instance = None
    if selecte_ids:
        if WorkOrderMaster.objects.filter(CompanyID=CompanyID, pk__in=selecte_ids).exists():
            instances = WorkOrderMaster.objects.filter(pk__in=selecte_ids)
    else:
        if WorkOrderMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
            instances = WorkOrderMaster.objects.filter(pk=pk)

    if instances:
        for instance in instances:
            # instance = WorkOrderMaster.objects.get(pk=pk)
            WorkOrderMasterID = instance.WorkOrderMasterID
            BranchID = instance.BranchID
            VoucherNo = instance.VoucherNo
            Date = instance.Date
            WareHouseID = instance.WareHouseID
            Notes = instance.Notes
            ProductID = instance.ProductID
            ManufactureDate = instance.ManufactureDate
            ExpiryDate = instance.ExpiryDate
            ProductQty = instance.ProductQty
            CostPerPrice = instance.CostPerPrice
            UnitPrice = instance.UnitPrice
            PriceListID = instance.PriceListID
            CostSum = instance.CostSum
            Amount = instance.Amount
            Weight = instance.Weight
            TotalQty = instance.TotalQty
            GrandTotal = instance.GrandTotal
            GrandCostSum = instance.GrandCostSum
            IsActive = instance.IsActive
            BatchCode = instance.BatchCode

            Action = "D"

            MultiFactor = PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=PriceListID).MultiFactor

            Qty_batch = converted_float(MultiFactor) * converted_float(ProductQty)

            if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
                batch_ins = Batch.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode)
                StockIn = batch_ins.StockIn
                batch_ins.StockIn = converted_float(StockIn) - converted_float(Qty_batch)
                batch_ins.save()

            WorkOrderMaster_Log.objects.create(
                TransactionID=WorkOrderMasterID,
                BranchID=BranchID,
                VoucherNo=VoucherNo,
                Date=Date,
                WareHouseID=WareHouseID,
                Notes=Notes,
                ProductID=ProductID,
                ManufactureDate=ManufactureDate,
                ExpiryDate=ExpiryDate,
                ProductQty=ProductQty,
                CostPerPrice=CostPerPrice,
                UnitPrice=UnitPrice,
                PriceListID=PriceListID,
                CostSum=CostSum,
                Amount=Amount,
                Weight=Weight,
                TotalQty=TotalQty,
                GrandTotal=GrandTotal,
                GrandCostSum=GrandCostSum,
                IsActive=IsActive,
                CompanyID=CompanyID,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                BatchCode=BatchCode,
            )

            detail_instances = WorkOrderDetails.objects.filter(
                CompanyID=CompanyID, WorkOrderMasterID=WorkOrderMasterID, BranchID=BranchID)

            for detail_instance in detail_instances:

                WorkOrderDetailsID = detail_instance.WorkOrderDetailsID
                BranchID = detail_instance.BranchID
                BatchCode = detail_instance.BatchCode
                ProductID = detail_instance.ProductID
                Qty = detail_instance.Qty
                PriceListID = detail_instance.PriceListID
                CostPerPrice = detail_instance.CostPerPrice
                UnitPrice = detail_instance.UnitPrice
                Amount = detail_instance.Amount
                CostSum = detail_instance.CostSum

                MultiFactor = PriceList.objects.get(
                    CompanyID=CompanyID, PriceListID=PriceListID).MultiFactor

                Qty_batch = converted_float(MultiFactor) * converted_float(Qty)

                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
                    batch_ins = Batch.objects.get(
                        CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode)
                    StockOut = batch_ins.StockOut
                    batch_ins.StockOut = converted_float(StockOut) - converted_float(Qty_batch)
                    batch_ins.save()

                WorkOrderDetails_Log.objects.create(
                    CompanyID=CompanyID,
                    TransactionID=WorkOrderDetailsID,
                    BranchID=BranchID,
                    BatchCode=BatchCode,
                    Action=Action,
                    WorkOrderMasterID=WorkOrderMasterID,
                    ProductID=ProductID,
                    Qty=Qty,
                    PriceListID=PriceListID,
                    CostPerPrice=CostPerPrice,
                    UnitPrice=UnitPrice,
                    CostSum=CostSum,
                    Amount=Amount,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                )

                detail_instance.delete()

            if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=WorkOrderMasterID, BranchID=BranchID, VoucherType="WO").exists():
                stockPostingInstances = StockPosting.objects.filter(
                    CompanyID=CompanyID, VoucherMasterID=WorkOrderMasterID, BranchID=BranchID, VoucherType="WO")

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
            instance.delete()

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Work Order',
                     'Deleted', 'Work Order Deleted successfully.', 'Work Order Deleted successfully')

        response_data = {
            "StatusCode": 6000,
            "title": "Success",
            "message": "Work Order Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "title": "Failed",
            "message": "Work Order  Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)




@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def create_workorder_new(request):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data['CompanyID']
            CreatedUserID = data['CreatedUserID']
            PriceRounding = data['PriceRounding']
            CompanyID = get_company(CompanyID)

            today = datetime.datetime.now()
            BranchID = data['BranchID']
            VoucherNo = data['VoucherNo']
            Date = data['Date']
            WareHouseID = data['WareHouseID']
            Notes = data['Notes']
            ProductIDMaster = data['ProductIDMaster']
            QtyMaster = data['QtyMaster']
            CostMaster = data['CostMaster']
            SalesPriceMaster = data['SalesPriceMaster']
            PriceListIDMaster = data['PriceListIDMaster']
            SumCostMaster = data['SumCostMaster']
            SumSalesPriceMaster = data['SumSalesPriceMaster']
            TotalQty = data['TotalQty']
            GrandTotalSalesPrice = data['GrandTotalSalesPrice']
            GrandTotalCost = data['GrandTotalCost']
            IsActive = data['IsActive']
            ManufactureDate = data['ManufactureDate']
            ExpiryDate = data['ExpiryDate']
            BatchCode = data['BatchCode']
            PriceCategoryID = data['PriceCategoryID']

            Action = "A"

            VoucherType = "WO"
            # VoucherNo Updated
            try:
                PreFix = data['PreFix']
            except:
                PreFix = "WO"

            try:
                Seperator = data['Seperator']
            except:
                Seperator = ""

            try:
                InvoiceNo = data['InvoiceNo']
            except:
                InvoiceNo = 1

            BatchID = 1

            MultiFactorMaster = PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=PriceListIDMaster).MultiFactor

            QtyMasterUnit = converted_float(MultiFactorMaster) * converted_float(QtyMaster)

            # checking voucher number already exist
            VoucherNoLow = VoucherNo.lower()
            is_voucherExist = False
            insts = WorkOrderMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
            if insts:
                for i in insts:
                    voucher_no = i.VoucherNo
                    voucherNo = voucher_no.lower()
                    if VoucherNoLow == voucherNo:
                        is_voucherExist = True

            check_VoucherNoAutoGenerate = False
            is_WorkOrderOK = True

            if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="VoucherNoAutoGenerate").exists():
                check_VoucherNoAutoGenerate = GeneralSettings.objects.get(
                    BranchID=BranchID, CompanyID=CompanyID, SettingsType="VoucherNoAutoGenerate").SettingsValue

            if is_voucherExist == True and check_VoucherNoAutoGenerate == "True":
                VoucherNo = get_Genrate_VoucherNo(
                    WorkOrderMaster, BranchID, CompanyID, "WO")
                is_WorkOrderOK = True
            elif is_voucherExist == False:
                is_WorkOrderOK = True
            else:
                is_WorkOrderOK = False

            if is_WorkOrderOK:
                WorkOrderMasterID = get_auto_idMaster(
                    WorkOrderMaster, BranchID, CompanyID)

                check_CreateBatchForWorkOrder = False
                if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="CreateBatchForWorkOrder").exists():
                    check_CreateBatchForWorkOrder = GeneralSettings.objects.get(
                        BranchID=BranchID, CompanyID=CompanyID, SettingsType="CreateBatchForWorkOrder").SettingsValue

                if check_CreateBatchForWorkOrder == True or check_CreateBatchForWorkOrder == "True":
                    BatchCode = get_auto_AutoBatchCode(
                        Batch, BranchID, CompanyID)
                    Batch.objects.create(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        ManufactureDate=ManufactureDate,
                        ExpiryDate=ExpiryDate,
                        BatchCode=BatchCode,
                        StockIn=QtyMasterUnit,
                        PurchasePrice=CostMaster,
                        SalesPrice=SalesPriceMaster,
                        PriceListID=PriceListIDMaster,
                        ProductID=ProductIDMaster,
                        WareHouseID=WareHouseID,
                        Description=Notes,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        ConnectID=WorkOrderMasterID
                    )
                else:
                    if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
                        check_EnableProductBatchWise = GeneralSettings.objects.get(
                            BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
                        check_BatchCriteria = "PurchasePriceAndSalesPrice"
                        if GeneralSettings.objects.filter(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="BatchCriteria").exists():
                            check_BatchCriteria = GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="BatchCriteria").SettingsValue
                        if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                            if check_BatchCriteria == "PurchasePrice":
                                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=CostMaster).exists():
                                    batch_ins = Batch.objects.get(
                                        CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=CostMaster)
                                    StockIn = batch_ins.StockIn
                                    NewStock = converted_float(
                                        StockIn) + converted_float(QtyMasterUnit)
                                    batch_ins.StockIn = NewStock
                                    batch_ins.ManufactureDate = ManufactureDate
                                    batch_ins.ExpiryDate = ExpiryDate
                                    batch_ins.ConnectID = WorkOrderMasterID
                                    batch_ins.save()
                                else:
                                    BatchCode = get_auto_AutoBatchCode(
                                        Batch, BranchID, CompanyID)
                                    Batch.objects.create(
                                        CompanyID=CompanyID,
                                        BranchID=BranchID,
                                        ManufactureDate=ManufactureDate,
                                        ExpiryDate=ExpiryDate,
                                        BatchCode=BatchCode,
                                        StockIn=QtyMasterUnit,
                                        PurchasePrice=CostMaster,
                                        SalesPrice=SalesPriceMaster,
                                        PriceListID=PriceListIDMaster,
                                        ProductID=ProductIDMaster,
                                        WareHouseID=WareHouseID,
                                        Description=Notes,
                                        CreatedDate=today,
                                        UpdatedDate=today,
                                        CreatedUserID=CreatedUserID,
                                        ConnectID=WorkOrderMasterID
                                    )
                            elif check_BatchCriteria == "SalesPrice":
                                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, SalesPrice=SalesPriceMaster).exists():
                                    batch_ins = Batch.objects.get(
                                        CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, SalesPrice=SalesPriceMaster)
                                    StockIn = batch_ins.StockIn
                                    NewStock = converted_float(
                                        StockIn) + converted_float(QtyMasterUnit)
                                    batch_ins.StockIn = NewStock
                                    batch_ins.ManufactureDate = ManufactureDate
                                    batch_ins.ExpiryDate = ExpiryDate
                                    batch_ins.ConnectID = WorkOrderMasterID
                                    batch_ins.save()
                                else:
                                    BatchCode = get_auto_AutoBatchCode(
                                        Batch, BranchID, CompanyID)
                                    Batch.objects.create(
                                        CompanyID=CompanyID,
                                        BranchID=BranchID,
                                        ManufactureDate=ManufactureDate,
                                        ExpiryDate=ExpiryDate,
                                        BatchCode=BatchCode,
                                        StockIn=QtyMasterUnit,
                                        PurchasePrice=CostMaster,
                                        SalesPrice=SalesPriceMaster,
                                        PriceListID=PriceListIDMaster,
                                        ProductID=ProductIDMaster,
                                        WareHouseID=WareHouseID,
                                        Description=Notes,
                                        CreatedDate=today,
                                        UpdatedDate=today,
                                        CreatedUserID=CreatedUserID,
                                        ConnectID=WorkOrderMasterID
                                    )
                            else:
                                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=CostMaster, SalesPrice=SalesPriceMaster).exists():
                                    batch_ins = Batch.objects.get(
                                        CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=CostMaster, SalesPrice=SalesPriceMaster)
                                    StockIn = batch_ins.StockIn
                                    NewStock = converted_float(
                                        StockIn) + converted_float(Qty_batch)
                                    batch_ins.StockIn = NewStock
                                    batch_ins.ManufactureDate = ManufactureDate
                                    batch_ins.ExpiryDate = ExpiryDate
                                    batch_ins.ConnectID = WorkOrderMasterID
                                    batch_ins.save()
                                else:
                                    BatchCode = get_auto_AutoBatchCode(
                                        Batch, BranchID, CompanyID)
                                    Batch.objects.create(
                                        CompanyID=CompanyID,
                                        BranchID=BranchID,
                                        ManufactureDate=ManufactureDate,
                                        ExpiryDate=ExpiryDate,
                                        BatchCode=BatchCode,
                                        StockIn=Qty_batch,
                                        PurchasePrice=CostMaster,
                                        SalesPrice=SalesPriceMaster,
                                        PriceListID=PriceListIDMaster,
                                        ProductID=ProductIDMaster,
                                        WareHouseID=WareHouseID,
                                        Description=Notes,
                                        CreatedDate=today,
                                        UpdatedDate=today,
                                        CreatedUserID=CreatedUserID,
                                        ConnectID=WorkOrderMasterID
                                    )
                        

                update_voucher_table(
                    CompanyID, CreatedUserID, VoucherType, PreFix, Seperator, InvoiceNo)

                WorkOrderMaster_Log.objects.create(
                    CompanyID=CompanyID,
                    TransactionID=WorkOrderMasterID,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    Date=Date,
                    WareHouseID=WareHouseID,
                    Notes=Notes,
                    ProductID=ProductIDMaster,
                    BatchCode=BatchCode,
                    ProductQty=QtyMaster,
                    CostPerPrice=CostMaster,
                    UnitPrice=SalesPriceMaster,
                    PriceListID=PriceListIDMaster,
                    Amount=SumSalesPriceMaster,
                    CostSum=SumCostMaster,
                    TotalQty=TotalQty,
                    ManufactureDate=ManufactureDate,
                    ExpiryDate=ExpiryDate,
                    GrandTotal=GrandTotalSalesPrice,
                    GrandCostSum=GrandTotalCost,
                    IsActive=IsActive,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    PriceCategoryID=PriceCategoryID
                )

                instance = WorkOrderMaster.objects.create(
                    CompanyID=CompanyID,
                    WorkOrderMasterID=WorkOrderMasterID,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    Date=Date,
                    WareHouseID=WareHouseID,
                    Notes=Notes,
                    ProductID=ProductIDMaster,
                    BatchCode=BatchCode,
                    ProductQty=QtyMaster,
                    CostPerPrice=CostMaster,
                    UnitPrice=SalesPriceMaster,
                    PriceListID=PriceListIDMaster,
                    Amount=SumSalesPriceMaster,
                    CostSum=SumCostMaster,
                    TotalQty=TotalQty,
                    ManufactureDate=ManufactureDate,
                    ExpiryDate=ExpiryDate,
                    GrandTotal=GrandTotalSalesPrice,
                    GrandCostSum=GrandTotalCost,
                    IsActive=IsActive,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    PriceCategoryID=PriceCategoryID
                )

                Product.objects.filter(ProductID=ProductIDMaster, CompanyID=CompanyID,
                                       BranchID=BranchID).update(IsFinishedProduct=True)

                PriceListID = PriceList.objects.get(
                    CompanyID=CompanyID, ProductID=ProductIDMaster, DefaultUnit=True).PriceListID

                # Qty = converted_float(MultiFactorMaster) * converted_float(QtyMaster)
                Cost = converted_float(CostMaster) / converted_float(MultiFactorMaster)

                priceList_instance = PriceList.objects.get(
                    CompanyID=CompanyID, ProductID=ProductIDMaster, PriceListID=PriceListID)
                PurchasePrice = priceList_instance.PurchasePrice
                SalesPrice = priceList_instance.SalesPrice

                StockPostingID = get_auto_stockPostid(
                    StockPosting, BranchID, CompanyID)

                pricelist, warehouse = get_ModelInstance(
                    CompanyID, BranchID, PriceListID, WareHouseID)

                StockPosting.objects.create(
                    StockPostingID=StockPostingID,
                    BranchID=BranchID,
                    Action=Action,
                    Date=Date,
                    VoucherMasterID=WorkOrderMasterID,
                    VoucherType=VoucherType,
                    ProductID=ProductIDMaster,
                    BatchID=BatchCode,
                    WareHouseID=WareHouseID,
                    QtyIn=QtyMasterUnit,
                    Rate=Cost,
                    PriceListID=PriceListIDMaster,
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
                    Date=Date,
                    VoucherMasterID=WorkOrderMasterID,
                    VoucherType=VoucherType,
                    ProductID=ProductIDMaster,
                    BatchID=BatchCode,
                    WareHouseID=WareHouseID,
                    QtyIn=QtyMasterUnit,
                    Rate=Cost,
                    PriceListID=PriceListIDMaster,
                    IsActive=IsActive,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                )

                WorkOrderDetailses = data["WorkOrderDetails"]
                for WorkOrderDetail in WorkOrderDetailses:
                    ProductID = WorkOrderDetail['ProductID']
                    if ProductID:
                        Qty = converted_float(WorkOrderDetail['Qty'])
                        DetailPriceListID = WorkOrderDetail['PriceListID']
                        # CostPerPrice = converted_float(WorkOrderDetail['CostPerItem'])
                        UnitPrice = converted_float(WorkOrderDetail['UnitPrice'])
                        SalesPrice = converted_float(WorkOrderDetail['SalesPrice'])
                        total_cost = converted_float(WorkOrderDetail['total_cost'])
                        total_sales = converted_float(WorkOrderDetail['total_sales'])
                        BatchCode = WorkOrderDetail['BatchCode']
                        DetailQty = Qty
                        MultiFactor = PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=DetailPriceListID).MultiFactor
                        # qty_batch = converted_float(FreeQty) + converted_float(Qty)
                        Qty_batch = converted_float(MultiFactor) * converted_float(DetailQty)

                        WorkOrderDetailsID = get_auto_id(
                            WorkOrderDetails, BranchID, CompanyID)

                        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
                            check_EnableProductBatchWise = GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue

                            check_BatchCriteria = "PurchasePriceAndSalesPrice"
                            if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                                if check_BatchCriteria == "PurchasePrice":
                                    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=UnitPrice).exists():
                                        batch_ins = Batch.objects.get(
                                            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=UnitPrice)
                                        StockOut = batch_ins.StockOut
                                        NewStock = converted_float(
                                            StockOut) + converted_float(Qty_batch)
                                        batch_ins.StockOut = NewStock
                                        # batch_ins.ManufactureDate = ManufactureDate
                                        # batch_ins.ExpiryDate = ExpiryDate
                                        batch_ins.ConnectID = WorkOrderMasterID
                                        batch_ins.save()
                                    else:
                                        BatchCode = get_auto_AutoBatchCode(
                                            Batch, BranchID, CompanyID)
                                        Batch.objects.create(
                                            CompanyID=CompanyID,
                                            BranchID=BranchID,
                                            BatchCode=BatchCode,
                                            StockOut=Qty_batch,
                                            PurchasePrice=UnitPrice,
                                            SalesPrice=SalesPrice,
                                            PriceListID=DetailPriceListID,
                                            ProductID=ProductID,
                                            WareHouseID=WareHouseID,
                                            Description=Notes,
                                            CreatedDate=today,
                                            UpdatedDate=today,
                                            CreatedUserID=CreatedUserID,
                                            ConnectID=WorkOrderMasterID
                                        )
                                elif check_BatchCriteria == "SalesPrice":
                                    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, SalesPrice=SalesPrice).exists():
                                        batch_ins = Batch.objects.get(
                                            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, SalesPrice=SalesPrice)
                                        StockOut = batch_ins.StockOut
                                        NewStock = converted_float(
                                            StockOut) + converted_float(Qty_batch)
                                        batch_ins.StockOut = NewStock
                                        # batch_ins.ManufactureDate = ManufactureDate
                                        # batch_ins.ExpiryDate = ExpiryDate
                                        batch_ins.ConnectID = WorkOrderMasterID
                                        batch_ins.save()
                                    else:
                                        BatchCode = get_auto_AutoBatchCode(
                                            Batch, BranchID, CompanyID)
                                        Batch.objects.create(
                                            CompanyID=CompanyID,
                                            BranchID=BranchID,
                                            BatchCode=BatchCode,
                                            StockOut=Qty_batch,
                                            PurchasePrice=UnitPrice,
                                            SalesPrice=SalesPrice,
                                            PriceListID=DetailPriceListID,
                                            ProductID=ProductID,
                                            WareHouseID=WareHouseID,
                                            Description=Notes,
                                            CreatedDate=today,
                                            UpdatedDate=today,
                                            CreatedUserID=CreatedUserID,
                                            ConnectID=WorkOrderMasterID

                                        )
                                else:
                                    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=UnitPrice, SalesPrice=SalesPrice).exists():
                                        batch_ins = Batch.objects.get(
                                            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=UnitPrice, SalesPrice=SalesPrice)
                                        StockOut = batch_ins.StockOut
                                        NewStock = converted_float(
                                            StockOut) + converted_float(Qty_batch)
                                        batch_ins.StockOut = NewStock
                                        # batch_ins.ManufactureDate = ManufactureDate
                                        # batch_ins.ExpiryDate = ExpiryDate
                                        batch_ins.ConnectID = WorkOrderMasterID
                                        batch_ins.save()
                                    else:
                                        BatchCode = get_auto_AutoBatchCode(
                                            Batch, BranchID, CompanyID)
                                        Batch.objects.create(
                                            CompanyID=CompanyID,
                                            BranchID=BranchID,
                                            BatchCode=BatchCode,
                                            StockOut=Qty_batch,
                                            PurchasePrice=UnitPrice,
                                            SalesPrice=SalesPrice,
                                            PriceListID=DetailPriceListID,
                                            ProductID=ProductID,
                                            WareHouseID=WareHouseID,
                                            Description=Notes,
                                            CreatedDate=today,
                                            UpdatedDate=today,
                                            CreatedUserID=CreatedUserID,
                                            ConnectID=WorkOrderMasterID
                                        )
                            
                        log_instance = WorkOrderDetails_Log.objects.create(
                            CompanyID=CompanyID,
                            TransactionID=WorkOrderDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            WorkOrderMasterID=WorkOrderMasterID,
                            ProductID=ProductID,
                            BatchCode=BatchCode,
                            Qty=DetailQty,
                            PriceListID=DetailPriceListID,
                            CostPerPrice=UnitPrice,
                            UnitPrice=SalesPrice,
                            CostSum=total_cost,
                            Amount=total_sales,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                        )

                        WorkOrderDetails.objects.create(
                            CompanyID=CompanyID,
                            WorkOrderDetailsID=WorkOrderDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            WorkOrderMasterID=WorkOrderMasterID,
                            ProductID=ProductID,
                            BatchCode=BatchCode,
                            Qty=DetailQty,
                            PriceListID=DetailPriceListID,
                            CostPerPrice=UnitPrice,
                            UnitPrice=SalesPrice,
                            CostSum=total_cost,
                            Amount=total_sales,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            LogID=log_instance.ID
                        )

                        PriceListID_DefUnit = PriceList.objects.get(
                            CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).PriceListID

                        DetailQty = Qty

                        Qty = converted_float(MultiFactor) * converted_float(DetailQty)
                        Cost = converted_float(UnitPrice) / converted_float(MultiFactor)

                        priceList_instance = PriceList.objects.get(
                            CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID_DefUnit)
                        PurchasePrice = priceList_instance.PurchasePrice
                        SalesPrice = priceList_instance.SalesPrice

                        StockPostingID = get_auto_stockPostid(
                            StockPosting, BranchID, CompanyID)

                        pricelist, warehouse = get_ModelInstance(
                            CompanyID, BranchID, PriceListID_DefUnit, WareHouseID)

                        StockPosting.objects.create(
                            StockPostingID=StockPostingID,
                            BranchID=BranchID,
                            Action=Action,
                            Date=Date,
                            VoucherMasterID=WorkOrderMasterID,
                            VoucherDetailID=WorkOrderDetailsID,
                            VoucherType=VoucherType,
                            ProductID=ProductID,
                            BatchID=BatchCode,
                            WareHouseID=WareHouseID,
                            QtyOut=Qty,
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
                            Date=Date,
                            VoucherMasterID=WorkOrderMasterID,
                            VoucherDetailID=WorkOrderDetailsID,
                            VoucherType=VoucherType,
                            ProductID=ProductID,
                            BatchID=BatchCode,
                            WareHouseID=WareHouseID,
                            QtyOut=Qty,
                            Rate=Cost,
                            PriceListID=PriceListID_DefUnit,
                            IsActive=IsActive,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )

                        update_stock(CompanyID, BranchID, ProductID)

              
                response_data = {
                    "StatusCode": 6000,
                    "id": instance.id,
                    "message": "Work Order created Successfully!!!",
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Work Order',
                             'Create', 'Work Order created Failed.', 'VoucherNo already exist')
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

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Work Order',
                     'Create', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def edit_workorder_new(request,pk):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data['CompanyID']
            CreatedUserID = data['CreatedUserID']
            PriceRounding = data['PriceRounding']
            CompanyID = get_company(CompanyID)

            today = datetime.datetime.now()
            BranchID = data['BranchID']
            VoucherNo = data['VoucherNo']
            Date = data['Date']
            WareHouseID = data['WareHouseID']
            Notes = data['Notes']
            ProductIDMaster = data['ProductIDMaster']
            QtyMaster = data['QtyMaster']
            CostMaster = data['CostMaster']
            SalesPriceMaster = data['SalesPriceMaster']
            PriceListIDMaster = data['PriceListIDMaster']
            SumCostMaster = data['SumCostMaster']
            SumSalesPriceMaster = data['SumSalesPriceMaster']
            TotalQty = data['TotalQty']
            GrandTotalSalesPrice = data['GrandTotalSalesPrice']
            GrandTotalCost = data['GrandTotalCost']
            IsActive = data['IsActive']
            ManufactureDate = data['ManufactureDate']
            ExpiryDate = data['ExpiryDate']
            BatchCode = data['BatchCode']
            PriceCategoryID = data['PriceCategoryID']

            Action = "M"

            VoucherType = "WO"
            # VoucherNo Updated
            try:
                PreFix = data['PreFix']
            except:
                PreFix = "WO"

            try:
                Seperator = data['Seperator']
            except:
                Seperator = ""

            try:
                InvoiceNo = data['InvoiceNo']
            except:
                InvoiceNo = 1

            instance = WorkOrderMaster.objects.get(
                pk=pk, CompanyID=CompanyID, BranchID=BranchID)

            instanceVoucherNo = instance.VoucherNo
            WorkOrderMasterID = instance.WorkOrderMasterID
# --------------------------------------------------------------------------
            if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=instance.WorkOrderMasterID, BranchID=BranchID, VoucherType="WO").exists():
                stk_ins = StockPosting.objects.filter(
                    CompanyID=CompanyID, VoucherMasterID=instance.WorkOrderMasterID, BranchID=BranchID, VoucherType="WO")
                total_count_stock = stk_ins.count()
                null_count = stk_ins.filter(
                    VoucherDetailID__isnull=True).count()

                if total_count_stock == null_count:
                    stk_ins.delete()
                else:
                    instance_qty_sum = converted_float(instance.ProductQty)
                    instance_MultiFactor = PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=instance.PriceListID).MultiFactor
                    instance_Qty = converted_float(
                        instance_MultiFactor) * converted_float(instance_qty_sum)
                    stk_ins_master = stk_ins.filter(QtyIn__gt=0).first()
                    stk_ins_master.QtyIn = converted_float(
                        stk_ins_master.QtyIn) - converted_float(instance_Qty)

            if WorkOrderDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, WorkOrderMasterID=instance.WorkOrderMasterID).exists():
                Work_ins = WorkOrderDetails.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, WorkOrderMasterID=instance.WorkOrderMasterID)
                for i in Work_ins:
                    DetailBatchCode = i.BatchCode
                    Qty = i.Qty
                    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=DetailBatchCode).exists():
                        batch_ins = Batch.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, BatchCode=DetailBatchCode)
                        StockOut = batch_ins.StockOut
                        batch_ins.StockOut = converted_float(StockOut) - converted_float(Qty)
                        batch_ins.save()

                    # if not StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=instance.WorkOrderMasterID,VoucherDetailID=i.WorkOrderDetailsID,BranchID=BranchID, VoucherType="WO").exists():
                    #     StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=instance.WorkOrderMasterID,BranchID=BranchID, VoucherType="WO").delete()

                    instance_MultiFactor = PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=i.PriceListID).MultiFactor

                    instance_qty_sum = converted_float(i.Qty)
                    instance_Qty = converted_float(
                        instance_MultiFactor) * converted_float(instance_qty_sum)
                    if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=instance.WorkOrderMasterID, VoucherDetailID=i.WorkOrderDetailsID, ProductID=i.ProductID, BranchID=BranchID, VoucherType="WO").exists():
                        stock_inst = StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=instance.WorkOrderMasterID,
                                                                    VoucherDetailID=i.WorkOrderDetailsID, ProductID=i.ProductID, BranchID=BranchID, VoucherType="WO").first()
                        stock_inst.QtyOut = converted_float(
                            stock_inst.QtyOut) - converted_float(instance_Qty)
                        stock_inst.save()
            MasterBatchCode = instance.BatchCode
            MasterProductQty = instance.ProductQty
            if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=MasterBatchCode).exists():
                batch_ins = Batch.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, BatchCode=MasterBatchCode)
                StockIn = batch_ins.StockIn
                batch_ins.StockIn = converted_float(
                    StockIn) - converted_float(MasterProductQty)
                batch_ins.save()

# ------------------------------------------------------------------------------------
            MultiFactorMaster = PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=PriceListIDMaster).MultiFactor

            QtyMasterUnit = converted_float(MultiFactorMaster) * converted_float(QtyMaster)

            # checking voucher number already exist
            is_WorkOrderOK = True

            if is_WorkOrderOK:
                check_CreateBatchForWorkOrder = False
                if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="CreateBatchForWorkOrder").exists():
                    check_CreateBatchForWorkOrder = GeneralSettings.objects.get(
                        BranchID=BranchID, CompanyID=CompanyID, SettingsType="CreateBatchForWorkOrder").SettingsValue

                if check_CreateBatchForWorkOrder == True or check_CreateBatchForWorkOrder == "True":
                    BatchCode = get_auto_AutoBatchCode(
                        Batch, BranchID, CompanyID)
                    Batch.objects.create(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        ManufactureDate=ManufactureDate,
                        ExpiryDate=ExpiryDate,
                        BatchCode=BatchCode,
                        StockIn=QtyMasterUnit,
                        PurchasePrice=CostMaster,
                        SalesPrice=SalesPriceMaster,
                        PriceListID=PriceListIDMaster,
                        ProductID=ProductIDMaster,
                        WareHouseID=WareHouseID,
                        Description=Notes,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        ConnectID=WorkOrderMasterID
                    )
                else:
                    if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
                        check_EnableProductBatchWise = GeneralSettings.objects.get(
                            BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
                        check_BatchCriteria = "PurchasePriceAndSalesPrice"
                        if GeneralSettings.objects.filter(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="BatchCriteria").exists():
                            check_BatchCriteria = GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="BatchCriteria").SettingsValue
                        if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                            if check_BatchCriteria == "PurchasePrice":
                                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=CostMaster).exists():
                                    batch_ins = Batch.objects.get(
                                        CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=CostMaster)
                                    StockIn = batch_ins.StockIn
                                    NewStock = converted_float(
                                        StockIn) + converted_float(QtyMasterUnit)
                                    batch_ins.StockIn = NewStock
                                    batch_ins.ManufactureDate = ManufactureDate
                                    batch_ins.ExpiryDate = ExpiryDate
                                    batch_ins.ConnectID = WorkOrderMasterID
                                    batch_ins.save()
                                else:
                                    BatchCode = get_auto_AutoBatchCode(
                                        Batch, BranchID, CompanyID)
                                    Batch.objects.create(
                                        CompanyID=CompanyID,
                                        BranchID=BranchID,
                                        ManufactureDate=ManufactureDate,
                                        ExpiryDate=ExpiryDate,
                                        BatchCode=BatchCode,
                                        StockIn=QtyMasterUnit,
                                        PurchasePrice=CostMaster,
                                        SalesPrice=SalesPriceMaster,
                                        PriceListID=PriceListIDMaster,
                                        ProductID=ProductIDMaster,
                                        WareHouseID=WareHouseID,
                                        Description=Notes,
                                        CreatedDate=today,
                                        UpdatedDate=today,
                                        CreatedUserID=CreatedUserID,
                                        ConnectID=WorkOrderMasterID
                                    )
                            elif check_BatchCriteria == "SalesPrice":
                                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, SalesPrice=SalesPriceMaster).exists():
                                    batch_ins = Batch.objects.get(
                                        CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, SalesPrice=SalesPriceMaster)
                                    StockIn = batch_ins.StockIn
                                    NewStock = converted_float(
                                        StockIn) + converted_float(QtyMasterUnit)
                                    batch_ins.StockIn = NewStock
                                    batch_ins.ManufactureDate = ManufactureDate
                                    batch_ins.ExpiryDate = ExpiryDate
                                    batch_ins.ConnectID = WorkOrderMasterID
                                    batch_ins.save()
                                else:
                                    BatchCode = get_auto_AutoBatchCode(
                                        Batch, BranchID, CompanyID)
                                    Batch.objects.create(
                                        CompanyID=CompanyID,
                                        BranchID=BranchID,
                                        ManufactureDate=ManufactureDate,
                                        ExpiryDate=ExpiryDate,
                                        BatchCode=BatchCode,
                                        StockIn=QtyMasterUnit,
                                        PurchasePrice=CostMaster,
                                        SalesPrice=SalesPriceMaster,
                                        PriceListID=PriceListIDMaster,
                                        ProductID=ProductIDMaster,
                                        WareHouseID=WareHouseID,
                                        Description=Notes,
                                        CreatedDate=today,
                                        UpdatedDate=today,
                                        CreatedUserID=CreatedUserID,
                                        ConnectID=WorkOrderMasterID
                                    )
                            else:
                                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=CostMaster, SalesPrice=SalesPriceMaster).exists():
                                    batch_ins = Batch.objects.get(
                                        CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=CostMaster, SalesPrice=SalesPriceMaster)
                                    StockIn = batch_ins.StockIn
                                    NewStock = converted_float(
                                        StockIn) + converted_float(QtyMasterUnit)
                                    batch_ins.StockIn = NewStock
                                    batch_ins.ManufactureDate = ManufactureDate
                                    batch_ins.ExpiryDate = ExpiryDate
                                    batch_ins.ConnectID = WorkOrderMasterID
                                    batch_ins.save()
                                else:
                                    BatchCode = get_auto_AutoBatchCode(
                                        Batch, BranchID, CompanyID)
                                    Batch.objects.create(
                                        CompanyID=CompanyID,
                                        BranchID=BranchID,
                                        ManufactureDate=ManufactureDate,
                                        ExpiryDate=ExpiryDate,
                                        BatchCode=BatchCode,
                                        StockIn=QtyMasterUnit,
                                        PurchasePrice=CostMaster,
                                        SalesPrice=SalesPriceMaster,
                                        PriceListID=PriceListIDMaster,
                                        ProductID=ProductIDMaster,
                                        WareHouseID=WareHouseID,
                                        Description=Notes,
                                        CreatedDate=today,
                                        UpdatedDate=today,
                                        CreatedUserID=CreatedUserID,
                                        ConnectID=WorkOrderMasterID
                                    )

                WorkOrderMaster_Log.objects.create(
                    CompanyID=CompanyID,
                    TransactionID=WorkOrderMasterID,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    Date=Date,
                    WareHouseID=WareHouseID,
                    Notes=Notes,
                    ProductID=ProductIDMaster,
                    BatchCode=BatchCode,
                    ProductQty=QtyMaster,
                    CostPerPrice=CostMaster,
                    UnitPrice=SalesPriceMaster,
                    PriceListID=PriceListIDMaster,
                    Amount=SumSalesPriceMaster,
                    CostSum=SumCostMaster,
                    TotalQty=TotalQty,
                    ManufactureDate=ManufactureDate,
                    ExpiryDate=ExpiryDate,
                    GrandTotal=GrandTotalSalesPrice,
                    GrandCostSum=GrandTotalCost,
                    IsActive=IsActive,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    PriceCategoryID=PriceCategoryID
                )

                instance.Action = Action
                instance.Date = Date
                instance.WareHouseID = WareHouseID
                instance.Notes = Notes
                instance.ProductID = ProductIDMaster
                instance.ProductQty = QtyMaster
                instance.CostPerPrice = CostMaster
                instance.UnitPrice = SalesPriceMaster
                instance.PriceListID = PriceListIDMaster
                instance.Amount = SumSalesPriceMaster
                instance.TotalQty = TotalQty
                instance.GrandTotal = GrandTotalSalesPrice
                instance.IsActive = IsActive
                instance.ManufactureDate = ManufactureDate
                instance.ExpiryDate = ExpiryDate
                instance.UpdatedDate = today
                instance.CreatedUserID = CreatedUserID
                instance.BatchCode = BatchCode
                instance.CostSum = SumCostMaster
                instance.GrandCostSum = GrandTotalCost
                instance.PriceCategoryID = PriceCategoryID
                instance.save()

                Product.objects.filter(ProductID=ProductIDMaster, CompanyID=CompanyID,
                                       BranchID=BranchID).update(IsFinishedProduct=True)

                PriceListID = PriceList.objects.get(
                    CompanyID=CompanyID, ProductID=ProductIDMaster, DefaultUnit=True).PriceListID

                # Qty = converted_float(MultiFactorMaster) * converted_float(QtyMaster)
                Cost = converted_float(CostMaster) / converted_float(MultiFactorMaster)

                priceList_instance = PriceList.objects.get(
                    CompanyID=CompanyID, ProductID=ProductIDMaster, PriceListID=PriceListID)
                SalesPrice = priceList_instance.SalesPrice
                if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherType="WO", VoucherMasterID=instance.WorkOrderMasterID, QtyIn__gt=0).exists():
                    stock_master_ins = StockPosting.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, VoucherType="WO", VoucherMasterID=instance.WorkOrderMasterID, QtyIn__gt=0).first()
                    stock_master_ins.QtyIn = QtyMasterUnit
                    stock_master_ins.Action = Action
                    stock_master_ins.save()

                else:
                    StockPostingID = get_auto_stockPostid(
                        StockPosting, BranchID, CompanyID)

                    pricelist, warehouse = get_ModelInstance(
                        CompanyID, BranchID, PriceListID, WareHouseID)

                    StockPosting.objects.create(
                        StockPostingID=StockPostingID,
                        BranchID=BranchID,
                        Action=Action,
                        Date=Date,
                        VoucherMasterID=WorkOrderMasterID,
                        VoucherType=VoucherType,
                        ProductID=ProductIDMaster,
                        BatchID=BatchCode,
                        WareHouseID=WareHouseID,
                        QtyIn=QtyMasterUnit,
                        Rate=Cost,
                        PriceListID=PriceListIDMaster,
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
                        Date=Date,
                        VoucherMasterID=WorkOrderMasterID,
                        VoucherType=VoucherType,
                        ProductID=ProductIDMaster,
                        BatchID=BatchCode,
                        WareHouseID=WareHouseID,
                        QtyIn=QtyMasterUnit,
                        Rate=Cost,
                        PriceListID=PriceListIDMaster,
                        IsActive=IsActive,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                    )

                deleted_datas = data["deleted_data"]
                if deleted_datas:
                    for deleted_Data in deleted_datas:
                        deleted_pk = deleted_Data['unq_id']
                        WorkOrderMasterID_Deleted = deleted_Data['WorkOrderMasterID']
                        WorkOrderDetailsID_Deleted = deleted_Data['WorkOrderDetailsID']
                        ProductID_Deleted = deleted_Data['ProductID']
                        Rate_Deleted = deleted_Data['Rate']

                        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID_Deleted, DefaultUnit=True).exists():
                            priceList = PriceList.objects.get(
                                CompanyID=CompanyID, ProductID=ProductID_Deleted, DefaultUnit=True)
                            MultiFactor = priceList.MultiFactor
                            Cost = converted_float(Rate_Deleted) / converted_float(MultiFactor)
                            Ct = round(Cost, 4)

                            if not deleted_pk == '' or not deleted_pk == 0:
                                if WorkOrderDetails.objects.filter(CompanyID=CompanyID, pk=deleted_pk).exists():
                                    deleted_detail = WorkOrderDetails.objects.filter(
                                        CompanyID=CompanyID, pk=deleted_pk)
                                    deleted_detail.delete()

                                    if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=WorkOrderMasterID_Deleted, VoucherDetailID=WorkOrderDetailsID_Deleted, ProductID=ProductID_Deleted, BranchID=BranchID, VoucherType="WO").exists():
                                        stock_instances_delete = StockPosting.objects.filter(
                                            CompanyID=CompanyID, VoucherMasterID=WorkOrderMasterID_Deleted, VoucherDetailID=WorkOrderDetailsID_Deleted, ProductID=ProductID_Deleted, BranchID=BranchID, VoucherType="WO")
                                        stock_instances_delete.delete()


                WorkOrderDetailses = data["WorkOrderDetails"]
                for WorkOrderDetail in WorkOrderDetailses:
                    pk = WorkOrderDetail['unq_id']
                    ProductID = WorkOrderDetail['ProductID']
                    if ProductID:
                        Qty = converted_float(WorkOrderDetail['Qty'])
                        DetailPriceListID = WorkOrderDetail['PriceListID']
                        # CostPerPrice = converted_float(WorkOrderDetail['CostPerItem'])
                        UnitPrice = converted_float(WorkOrderDetail['UnitPrice'])
                        SalesPrice = converted_float(WorkOrderDetail['SalesPrice'])
                        total_cost = converted_float(WorkOrderDetail['total_cost'])
                        total_sales = converted_float(WorkOrderDetail['total_sales'])
                        BatchCode = WorkOrderDetail['BatchCode']
                        detailID = int(WorkOrderDetail['detailID'])
                        DetailQty = Qty
                        MultiFactor = PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=DetailPriceListID).MultiFactor
                        # qty_batch = converted_float(FreeQty) + converted_float(Qty)
                        Qty_batch = converted_float(MultiFactor) * converted_float(DetailQty)

                        WorkOrderDetailsID = get_auto_id(
                            WorkOrderDetails, BranchID, CompanyID)

                        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
                            check_EnableProductBatchWise = GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue

                            check_BatchCriteria = "PurchasePriceAndSalesPrice"
                            if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                                if check_BatchCriteria == "PurchasePrice":
                                    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=UnitPrice).exists():
                                        batch_ins = Batch.objects.get(
                                            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=UnitPrice)
                                        StockOut = batch_ins.StockOut
                                        NewStock = converted_float(
                                            StockOut) + converted_float(Qty_batch)
                                        batch_ins.StockOut = NewStock
                                        # batch_ins.ManufactureDate = ManufactureDate
                                        # batch_ins.ExpiryDate = ExpiryDate
                                        batch_ins.ConnectID = WorkOrderMasterID
                                        batch_ins.save()
                                    else:
                                        BatchCode = get_auto_AutoBatchCode(
                                            Batch, BranchID, CompanyID)
                                        Batch.objects.create(
                                            CompanyID=CompanyID,
                                            BranchID=BranchID,
                                            BatchCode=BatchCode,
                                            StockOut=Qty_batch,
                                            PurchasePrice=UnitPrice,
                                            SalesPrice=SalesPrice,
                                            PriceListID=DetailPriceListID,
                                            ProductID=ProductID,
                                            WareHouseID=WareHouseID,
                                            Description=Notes,
                                            CreatedDate=today,
                                            UpdatedDate=today,
                                            CreatedUserID=CreatedUserID,
                                            ConnectID=WorkOrderMasterID
                                        )
                                elif check_BatchCriteria == "SalesPrice":
                                    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, SalesPrice=SalesPrice).exists():
                                        batch_ins = Batch.objects.get(
                                            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, SalesPrice=SalesPrice)
                                        StockOut = batch_ins.StockOut
                                        NewStock = converted_float(
                                            StockOut) + converted_float(Qty_batch)
                                        batch_ins.StockOut = NewStock
                                        # batch_ins.ManufactureDate = ManufactureDate
                                        # batch_ins.ExpiryDate = ExpiryDate
                                        batch_ins.ConnectID = WorkOrderMasterID
                                        batch_ins.save()
                                    else:
                                        BatchCode = get_auto_AutoBatchCode(
                                            Batch, BranchID, CompanyID)
                                        Batch.objects.create(
                                            CompanyID=CompanyID,
                                            BranchID=BranchID,
                                            BatchCode=BatchCode,
                                            StockOut=Qty_batch,
                                            PurchasePrice=UnitPrice,
                                            SalesPrice=SalesPrice,
                                            PriceListID=DetailPriceListID,
                                            ProductID=ProductID,
                                            WareHouseID=WareHouseID,
                                            Description=Notes,
                                            CreatedDate=today,
                                            UpdatedDate=today,
                                            CreatedUserID=CreatedUserID,
                                            ConnectID=WorkOrderMasterID

                                        )
                                else:
                                    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=UnitPrice, SalesPrice=SalesPrice).exists():
                                        batch_ins = Batch.objects.get(
                                            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=UnitPrice, SalesPrice=SalesPrice)
                                        StockOut = batch_ins.StockOut
                                        NewStock = converted_float(
                                            StockOut) + converted_float(Qty_batch)
                                        batch_ins.StockOut = NewStock
                                        # batch_ins.ManufactureDate = ManufactureDate
                                        # batch_ins.ExpiryDate = ExpiryDate
                                        batch_ins.ConnectID = WorkOrderMasterID
                                        batch_ins.save()
                                    else:
                                        BatchCode = get_auto_AutoBatchCode(
                                            Batch, BranchID, CompanyID)
                                        Batch.objects.create(
                                            CompanyID=CompanyID,
                                            BranchID=BranchID,
                                            BatchCode=BatchCode,
                                            StockOut=Qty_batch,
                                            PurchasePrice=UnitPrice,
                                            SalesPrice=SalesPrice,
                                            PriceListID=DetailPriceListID,
                                            ProductID=ProductID,
                                            WareHouseID=WareHouseID,
                                            Description=Notes,
                                            CreatedDate=today,
                                            UpdatedDate=today,
                                            CreatedUserID=CreatedUserID,
                                            ConnectID=WorkOrderMasterID
                                        )

                        if detailID == 0:
                            workorder_details_instance = WorkOrderDetails.objects.get(
                                CompanyID=CompanyID, pk=pk)
                            WorkOrderDetailsID = workorder_details_instance.WorkOrderDetailsID
                            WorkOrderMasterID = workorder_details_instance.WorkOrderMasterID
                            log_instance = WorkOrderDetails_Log.objects.create(
                                CompanyID=CompanyID,
                                TransactionID=WorkOrderDetailsID,
                                BranchID=BranchID,
                                Action=Action,
                                WorkOrderMasterID=WorkOrderMasterID,
                                ProductID=ProductID,
                                BatchCode=BatchCode,
                                Qty=DetailQty,
                                PriceListID=DetailPriceListID,
                                CostPerPrice=UnitPrice,
                                UnitPrice=SalesPrice,
                                CostSum=total_cost,
                                Amount=total_sales,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                            )

                            workorder_details_instance.Action = Action
                            workorder_details_instance.ProductID = ProductID
                            workorder_details_instance.Qty = DetailQty
                            workorder_details_instance.PriceListID = DetailPriceListID
                            workorder_details_instance.CostPerPrice = UnitPrice
                            workorder_details_instance.UnitPrice = SalesPrice
                            workorder_details_instance.CostSum = total_cost
                            workorder_details_instance.Amount = total_sales
                            workorder_details_instance.CreatedDate = workorder_details_instance.CreatedDate
                            workorder_details_instance.UpdatedDate = today
                            workorder_details_instance.BatchCode = BatchCode
                            workorder_details_instance.LogID = log_instance.ID
                            workorder_details_instance.save()

                            if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WareHouseID, VoucherMasterID=WorkOrderMasterID, VoucherDetailID=WorkOrderDetailsID, BranchID=BranchID, VoucherType="WO", ProductID=ProductID).exists():
                                stock_instance = StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WareHouseID, VoucherMasterID=WorkOrderMasterID, VoucherDetailID=WorkOrderDetailsID, BranchID=BranchID, VoucherType="WO", ProductID=ProductID).first()
                                stock_instance.QtyOut = Qty_batch
                                stock_instance.Action = Action
                                stock_instance.save()
                            else:
                                PriceListID_DefUnit = PriceList.objects.get(
                                    CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).PriceListID

                                DetailQty = Qty

                                Qty = converted_float(MultiFactor) * converted_float(DetailQty)
                                Cost = converted_float(UnitPrice) / converted_float(MultiFactor)

                                priceList_instance = PriceList.objects.get(
                                    CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID_DefUnit)
                                SalesPrice = priceList_instance.SalesPrice

                                StockPostingID = get_auto_stockPostid(
                                    StockPosting, BranchID, CompanyID)

                                pricelist, warehouse = get_ModelInstance(
                                    CompanyID, BranchID, PriceListID_DefUnit, WareHouseID)

                                StockPosting.objects.create(
                                    StockPostingID=StockPostingID,
                                    BranchID=BranchID,
                                    Action=Action,
                                    Date=Date,
                                    VoucherMasterID=WorkOrderMasterID,
                                    VoucherDetailID=WorkOrderDetailsID,
                                    VoucherType=VoucherType,
                                    ProductID=ProductID,
                                    BatchID=BatchCode,
                                    WareHouseID=WareHouseID,
                                    QtyOut=Qty,
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
                                    Date=Date,
                                    VoucherMasterID=WorkOrderMasterID,
                                    VoucherDetailID=WorkOrderDetailsID,
                                    VoucherType=VoucherType,
                                    ProductID=ProductID,
                                    BatchID=BatchCode,
                                    WareHouseID=WareHouseID,
                                    QtyOut=Qty,
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
                            WorkOrderDetailsID = get_auto_id(
                                WorkOrderDetails, BranchID, CompanyID)

                            log_instance = WorkOrderDetails_Log.objects.create(
                                CompanyID=CompanyID,
                                TransactionID=WorkOrderDetailsID,
                                BranchID=BranchID,
                                Action=Action,
                                WorkOrderMasterID=WorkOrderMasterID,
                                ProductID=ProductID,
                                BatchCode=BatchCode,
                                Qty=DetailQty,
                                PriceListID=DetailPriceListID,
                                CostPerPrice=UnitPrice,
                                UnitPrice=SalesPrice,
                                CostSum=total_cost,
                                Amount=total_sales,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                            )

                            WorkOrderDetails.objects.create(
                                CompanyID=CompanyID,
                                WorkOrderDetailsID=WorkOrderDetailsID,
                                BranchID=BranchID,
                                Action=Action,
                                WorkOrderMasterID=WorkOrderMasterID,
                                ProductID=ProductID,
                                BatchCode=BatchCode,
                                Qty=DetailQty,
                                PriceListID=DetailPriceListID,
                                CostPerPrice=UnitPrice,
                                UnitPrice=SalesPrice,
                                CostSum=total_cost,
                                Amount=total_sales,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                LogID=log_instance.ID
                            )

                            PriceListID_DefUnit = PriceList.objects.get(
                                    CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).PriceListID

                            DetailQty = Qty

                            Qty = converted_float(MultiFactor) * converted_float(DetailQty)
                            Cost = converted_float(UnitPrice) / converted_float(MultiFactor)

                            priceList_instance = PriceList.objects.get(
                                CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID_DefUnit)
                            SalesPrice = priceList_instance.SalesPrice

                            StockPostingID = get_auto_stockPostid(
                                StockPosting, BranchID, CompanyID)

                            pricelist, warehouse = get_ModelInstance(
                                CompanyID, BranchID, PriceListID_DefUnit, WareHouseID)

                            StockPosting.objects.create(
                                StockPostingID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=Date,
                                VoucherMasterID=WorkOrderMasterID,
                                VoucherDetailID=WorkOrderDetailsID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                BatchID=BatchCode,
                                WareHouseID=WareHouseID,
                                QtyOut=Qty,
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
                                Date=Date,
                                VoucherMasterID=WorkOrderMasterID,
                                VoucherDetailID=WorkOrderDetailsID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                BatchID=BatchCode,
                                WareHouseID=WareHouseID,
                                QtyOut=Qty,
                                Rate=Cost,
                                PriceListID=PriceListID_DefUnit,
                                IsActive=IsActive,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                            )

                            update_stock(CompanyID, BranchID, ProductID)

                                

              
                response_data = {
                    "StatusCode": 6000,
                    "id": instance.id,
                    "message": "Work Order updated Successfully!!!",
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Work Order',
                             'Create', 'Work Order created Failed.', 'VoucherNo already exist')
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
            "message": "some error occured..please try again",
            "err_descrb": err_descrb
        }

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Work Order',
                     'Create', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)