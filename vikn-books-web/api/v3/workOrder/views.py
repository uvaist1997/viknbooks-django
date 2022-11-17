from brands.models import PurchaseMaster, PurchaseMaster_Log, PurchaseDetails, PurchaseDetails_Log, StockPosting, LedgerPosting, StockPosting_Log,\
    LedgerPosting_Log, PurchaseDetailsDummy, StockRate, PriceList, StockTrans, ProductGroup, Brand, Unit, Warehouse, PurchaseReturnMaster, OpeningStockMaster, GeneralSettings, Product, WorkOrderMaster, WorkOrderMaster_Log, Batch, WorkOrderDetails, WorkOrderDetails_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v3.purchases.serializers import PurchaseMasterSerializer, PurchaseMasterRestSerializer, PurchaseDetailsSerializer,\
    PurchaseDetailsRestSerializer, PurchaseMasterReportSerializer, PurchaseMasterForReturnSerializer
from api.v3.workOrder import serializers
from api.v3.brands.serializers import ListSerializer
from api.v3.purchases.functions import generate_serializer_errors
from api.v3.products.functions import get_auto_AutoBatchCode
from rest_framework import status
from api.v3.sales.serializers import ListSerializerforReport
from api.v3.workOrder.functions import get_auto_id, get_auto_idMaster, get_auto_StockRateID, get_auto_StockTransID
from api.v3.sales.functions import get_auto_stockPostid
from api.v3.accountLedgers.functions import get_auto_LedgerPostid
import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from main.functions import get_company, activity_log
from api.v3.purchaseReturns.serializers import PurchaseReturnMasterRestSerializer
import re
from django.db.models import Max
from django.db.models import Q, Prefetch


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_workorder(request):
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
                BranchID=1, GroupName="Inventory",
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action
            )
        else:
            GeneralSettings.objects.filter(
                CompanyID=CompanyID,
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

    if not is_voucherExist:
        WorkOrderMasterID = get_auto_idMaster(WorkOrderMaster, BranchID, CompanyID)

        check_CreateBatchForWorkOrder = False
        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="CreateBatchForWorkOrder").exists():
            check_CreateBatchForWorkOrder = GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="CreateBatchForWorkOrder").SettingsValue

        if check_CreateBatchForWorkOrder == True or check_CreateBatchForWorkOrder == "True":
            BatchCode = get_auto_AutoBatchCode(Batch, BranchID, CompanyID)
            Batch.objects.create(
                CompanyID=CompanyID,
                BranchID=BranchID,
                ManufactureDate=ManufactureDate,
                ExpiryDate=ExpiryDate,
                BatchCode=BatchCode,
                StockIn=ProductQty,
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
                    CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
                check_BatchCriteria = "PurchasePriceAndSalesPrice"
                if GeneralSettings.objects.filter(
                        CompanyID=CompanyID, SettingsType="BatchCriteria").exists():
                    check_BatchCriteria = GeneralSettings.objects.get(
                        CompanyID=CompanyID, SettingsType="BatchCriteria").SettingsValue
                if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                    
                    if check_BatchCriteria == "PurchasePrice":
                        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode,PurchasePrice=BatchPurchasePrice).exists():
                            batch_ins = Batch.objects.get(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode,PurchasePrice=BatchPurchasePrice)
                            StockIn = batch_ins.StockIn
                            NewStock = float(StockIn) + float(ProductQty)
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
                                StockIn=ProductQty,
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
                        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode,SalesPrice=BatchSalesPrice).exists():
                            batch_ins = Batch.objects.get(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode,SalesPrice=BatchSalesPrice)
                            StockIn = batch_ins.StockIn
                            NewStock = float(StockIn) + float(ProductQty)
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
                                StockIn=ProductQty,
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
                        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode,PurchasePrice=BatchPurchasePrice,SalesPrice=BatchSalesPrice).exists():
                            batch_ins = Batch.objects.get(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode,PurchasePrice=BatchPurchasePrice,SalesPrice=BatchSalesPrice)
                            StockIn = batch_ins.StockIn
                            NewStock = float(StockIn) + float(ProductQty)
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
                                StockIn=ProductQty,
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
                    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode,PriceListID=BatchPriceListID).exists():
                        batch_ins = Batch.objects.get(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode,PriceListID=BatchPriceListID)
                        StockIn = batch_ins.StockIn
                        NewStock = float(StockIn) + float(ProductQty)
                        batch_ins.StockIn = NewStock
                        batch_ins.save()
                    else:
                        BatchCode = get_auto_AutoBatchCode(
                            Batch, BranchID, CompanyID)
                        Batch.objects.create(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            BatchCode=BatchCode,
                            StockIn=ProductQty,
                            PurchasePrice=BatchPurchasePrice,
                            SalesPrice=BatchSalesPrice,
                            PriceListID=BatchPriceListID,
                            ProductID=ProductID,
                            WareHouseID=WareHouseID,
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

        Product.objects.filter(ProductID=ProductID, CompanyID=CompanyID,
                               BranchID=BranchID).update(IsFinishedProduct=True)

        MultiFactor = PriceList.objects.get(
            CompanyID=CompanyID, PriceListID=BatchPriceListID, BranchID=BranchID).MultiFactor
        PriceListID = PriceList.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True, BranchID=BranchID).PriceListID

        # PurchasePrice = priceList.PurchasePrice
        # SalesPrice = priceList.SalesPrice

        Qty = float(MultiFactor) * float(ProductQty)
        Cost = float(CostPerPrice) / float(MultiFactor)

        Qy = round(Qty, 4)
        Qty = str(Qy)

        Ct = round(Cost, 4)
        Cost = str(Ct)

        priceList_instance = PriceList.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID, BranchID=BranchID)
        PurchasePrice = priceList_instance.PurchasePrice
        SalesPrice = priceList_instance.SalesPrice

        StockPostingID = get_auto_stockPostid(
            StockPosting, BranchID, CompanyID)

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

        stockRateInstance = None

        if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WareHouseID, PriceListID=PriceListID).exists():
            stockRateInstance = StockRate.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WareHouseID, PriceListID=PriceListID)

            StockRateID = stockRateInstance.StockRateID
            stockRateInstance.Qty = float(stockRateInstance.Qty) + float(Qty)
            stockRateInstance.save()

            if StockTrans.objects.filter(StockRateID=StockRateID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                stockTra_in = StockTrans.objects.filter(
                    StockRateID=StockRateID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                stockTra_in.Qty = float(stockTra_in.Qty) + float(Qty)
                stockTra_in.save()
            else:
                StockTransID = get_auto_StockTransID(
                    StockTrans, BranchID, CompanyID)
                StockTrans.objects.create(
                    StockTransID=StockTransID,
                    BranchID=BranchID,
                    VoucherType=VoucherType,
                    StockRateID=StockRateID,
                    MasterID=WorkOrderMasterID,
                    Qty=Qty,
                    IsActive=IsActive,
                    CompanyID=CompanyID,
                )

        else:
            StockRateID = get_auto_StockRateID(StockRate, BranchID, CompanyID)
            StockRate.objects.create(
                StockRateID=StockRateID,
                BranchID=BranchID,
                BatchID=BatchID,
                PurchasePrice=PurchasePrice,
                SalesPrice=SalesPrice,
                Qty=Qty,
                Cost=Cost,
                ProductID=ProductID,
                WareHouseID=WareHouseID,
                Date=Date,
                PriceListID=PriceListID,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )

            StockTransID = get_auto_StockTransID(
                StockTrans, BranchID, CompanyID)
            StockTrans.objects.create(
                StockTransID=StockTransID,
                BranchID=BranchID,
                VoucherType=VoucherType,
                StockRateID=StockRateID,
                MasterID=WorkOrderMasterID,
                Qty=Qty,
                IsActive=IsActive,
                CompanyID=CompanyID,
            )

        
                

        WorkOrderDetailses = data["WorkOrderDetails"]

        for WorkOrderDetail in WorkOrderDetailses:

            # PurchaseMasterID = serialized.data['PurchaseMasterID']
            # WorkOrderMasterID = purchaseDetail['WorkOrderMasterID']
            ProductID = WorkOrderDetail['ProductID']
            if ProductID:
                Qty = float(WorkOrderDetail['Qty'])
                DetailPriceListID = WorkOrderDetail['PriceListID']
                CostPerPrice = float(WorkOrderDetail['CostPerItem'])
                UnitPrice = float(WorkOrderDetail['UnitPrice'])
                Amount = float(WorkOrderDetail['NetAmount'])
                DetailPurchasePrice = float(WorkOrderDetail['PurchasePrice'])
                DetailSalesPrice = float(WorkOrderDetail['UnitPrice'])
                BatchCode = int(WorkOrderDetail['BatchCode'])
                InclusivePrice = float(WorkOrderDetail['InclusivePrice'])
                is_inclusive = WorkOrderDetail['is_inclusive']

                DetailQty = round(Qty, PriceRounding)
                CostPerPrice = round(CostPerPrice, PriceRounding)
                UnitPrice = round(UnitPrice, PriceRounding)
                DetailPurchasePrice = round(DetailPurchasePrice, PriceRounding)
                DetailSalesPrice = round(DetailSalesPrice, PriceRounding)
                Amount = round(Amount, PriceRounding)

                if is_inclusive == True:
                    DetailSalesPrice = str(InclusivePrice)
                else:
                    DetailSalesPrice = str(UnitPrice)

                DetailPurchasePrice = str(DetailPurchasePrice)


                WorkOrderDetailsID = get_auto_id(
                    WorkOrderDetails, BranchID, CompanyID)

                if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
                    check_EnableProductBatchWise = GeneralSettings.objects.get(
                        CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue

                    check_BatchCriteria = "PurchasePriceAndSalesPrice"
                    # if GeneralSettings.objects.filter(
                    #         CompanyID=CompanyID, SettingsType="BatchCriteria").exists():
                    #     check_BatchCriteria = GeneralSettings.objects.get(
                    #         CompanyID=CompanyID, SettingsType="BatchCriteria").SettingsValue

                    if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                        if check_BatchCriteria == "PurchasePrice":
                            if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode,PurchasePrice=DetailPurchasePrice).exists():
                                batch_ins = Batch.objects.get(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=DetailPurchasePrice)
                                StockOut = batch_ins.StockOut
                                NewStock = float(StockOut) + float(DetailQty)
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
                                    StockOut=DetailQty,
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
                                batch_ins = Batch.objects.get(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, SalesPrice=DetailSalesPrice)
                                StockOut = batch_ins.StockOut
                                NewStock = float(StockOut) + float(DetailQty)
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
                                    StockOut=DetailQty,
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
                                batch_ins = Batch.objects.get(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=DetailPurchasePrice, SalesPrice=DetailSalesPrice)
                                StockOut = batch_ins.StockOut
                                NewStock = float(StockOut) + float(DetailQty)
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
                                    StockOut=DetailQty,
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
                        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode,PriceListID=PriceListID).exists():
                            batch_ins = Batch.objects.get(CompanyID=CompanyID, BranchID=BranchID,BatchCode=BatchCode,PriceListID=PriceListID)
                            StockOut = batch_ins.StockOut
                            NewStock = float(StockOut) + float(Qty)
                            batch_ins.StockOut = NewStock
                            batch_ins.save()
                        else:
                            BatchCode = get_auto_AutoBatchCode(Batch, BranchID, CompanyID)
                            Batch.objects.create(
                                CompanyID=CompanyID,
                                BranchID=BranchID,
                                BatchCode=BatchCode,
                                StockOut=Qty,
                                PurchasePrice=PurchasePrice,
                                SalesPrice=SalesPrice,
                                PriceListID=PriceListID,
                                ProductID=ProductID,
                                WareHouseID=WareHouseID,
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
                )

                WorkOrderDetails_Log.objects.create(
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

                MultiFactor = PriceList.objects.get(
                    CompanyID=CompanyID, PriceListID=DetailPriceListID, BranchID=BranchID).MultiFactor
                PriceListID_DefUnit = PriceList.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True, BranchID=BranchID).PriceListID

                # PriceListID_DefUnit = priceList.PriceListID
                # MultiFactor = priceList.MultiFactor

                # PurchasePrice = priceList.PurchasePrice
                # SalesPrice = priceList.SalesPrice
                DetailQty = Qty

                Qty = float(MultiFactor) * float(DetailQty)
                Cost = float(CostPerPrice) / float(MultiFactor)

                Qy = round(Qty, 4)
                Qty = str(Qy)

                Ct = round(Cost, 4)
                Cost = str(Ct)

                priceList_instance = PriceList.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID_DefUnit, BranchID=BranchID)
                PurchasePrice = priceList_instance.PurchasePrice
                SalesPrice = priceList_instance.SalesPrice

                
                       

                changQty = Qty
                if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WareHouseID, Qty__gt=0, PriceListID=PriceListID_DefUnit).exists():
                    stockRate_instances = StockRate.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WareHouseID, Qty__gt=0, PriceListID=PriceListID_DefUnit)
                    count = stockRate_instances.count()
                    last = 0
                    for stockRate_instance in stockRate_instances:
                        last = float(last) + float(1)
                        StockRateID = stockRate_instance.StockRateID
                        stock_post_cost = stockRate_instance.Cost
                        if float(stockRate_instance.Qty) > float(Qty):
                            stockRate_instance.Qty = float(
                                stockRate_instance.Qty) - float(Qty)
                            changQty = 0
                            stockRate_instance.save()

                            if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                                                           VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit).exists():
                                stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                                                                              VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit)
                                QtyOut = stockPost_instance.QtyOut
                                newQty = float(QtyOut) + float(Qty)

                                stockPost_instance.QtyOut = newQty
                                stockPost_instance.save()
                            else:
                                StockPostingID = get_auto_stockPostid(
                                    StockPosting, BranchID, CompanyID)
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
                                    QtyOut=Qty,
                                    Rate=stock_post_cost,
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
                                    VoucherMasterID=WorkOrderMasterID,
                                    VoucherType=VoucherType,
                                    ProductID=ProductID,
                                    BatchID=BatchID,
                                    WareHouseID=WareHouseID,
                                    QtyOut=Qty,
                                    Rate=stock_post_cost,
                                    PriceListID=PriceListID_DefUnit,
                                    IsActive=IsActive,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CreatedUserID=CreatedUserID,
                                    CompanyID=CompanyID,
                                )

                            if StockTrans.objects.filter(StockRateID=StockRateID, DetailID=WorkOrderDetailsID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                                stockTra_in = StockTrans.objects.filter(
                                    StockRateID=StockRateID, DetailID=WorkOrderDetailsID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                                stockTra_in.Qty = float(
                                    stockTra_in.Qty) + float(Qty)
                                stockTra_in.save()
                            else:
                                StockTransID = get_auto_StockTransID(
                                    StockTrans, BranchID, CompanyID)
                                StockTrans.objects.create(
                                    StockTransID=StockTransID,
                                    BranchID=BranchID,
                                    VoucherType=VoucherType,
                                    StockRateID=StockRateID,
                                    DetailID=WorkOrderDetailsID,
                                    MasterID=WorkOrderMasterID,
                                    Qty=Qty,
                                    IsActive=IsActive,
                                    CompanyID=CompanyID,
                                )
                        elif float(stockRate_instance.Qty) < float(Qty):

                            if float(changQty) > float(stockRate_instance.Qty):
                                changQty = float(changQty) - \
                                    float(stockRate_instance.Qty)
                                stckQty = stockRate_instance.Qty
                                stockRate_instance.Qty = 0
                                stockRate_instance.save()

                                if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                                                               VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit).exists():
                                    stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                                                                                  VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit)
                                    QtyOut = stockPost_instance.QtyOut
                                    newQty = float(QtyOut) + \
                                        float(stockRate_instance.Qty)
                                    stockPost_instance.QtyOut = newQty
                                    stockPost_instance.save()
                                else:
                                    StockPostingID = get_auto_stockPostid(
                                        StockPosting, BranchID, CompanyID)
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
                                        QtyOut=stckQty,
                                        Rate=stock_post_cost,
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
                                        VoucherMasterID=WorkOrderMasterID,
                                        VoucherType=VoucherType,
                                        ProductID=ProductID,
                                        BatchID=BatchID,
                                        WareHouseID=WareHouseID,
                                        QtyOut=stckQty,
                                        Rate=stock_post_cost,
                                        PriceListID=PriceListID_DefUnit,
                                        IsActive=IsActive,
                                        CreatedDate=today,
                                        UpdatedDate=today,
                                        CreatedUserID=CreatedUserID,
                                        CompanyID=CompanyID,
                                    )
                                if StockTrans.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, DetailID=WorkOrderDetailsID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                                    stockTra_in = StockTrans.objects.filter(
                                        CompanyID=CompanyID, StockRateID=StockRateID, DetailID=WorkOrderDetailsID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                                    stockTra_in.Qty = float(
                                        stockTra_in.Qty) + float(stockRate_instance.Qty)
                                    stockTra_in.save()
                                else:
                                    StockTransID = get_auto_StockTransID(
                                        StockTrans, BranchID, CompanyID)
                                    StockTrans.objects.create(
                                        StockTransID=StockTransID,
                                        BranchID=BranchID,
                                        VoucherType=VoucherType,
                                        StockRateID=StockRateID,
                                        DetailID=WorkOrderDetailsID,
                                        MasterID=WorkOrderMasterID,
                                        Qty=stockRate_instance.Qty,
                                        IsActive=IsActive,
                                        CompanyID=CompanyID,
                                    )
                            else:
                                if changQty < 0:
                                    changQty = 0
                                chqty = changQty
                                changQty = float(
                                    stockRate_instance.Qty) - float(changQty)
                                stockRate_instance.Qty = changQty
                                changQty = 0
                                stockRate_instance.save()

                                if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                                                               VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit).exists():
                                    stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                                                                                  VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit)
                                    QtyOut = stockPost_instance.QtyOut
                                    newQty = float(QtyOut) + float(chqty)
                                    stockPost_instance.QtyOut = newQty
                                    stockPost_instance.save()
                                else:
                                    StockPostingID = get_auto_stockPostid(
                                        StockPosting, BranchID, CompanyID)
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
                                        QtyOut=chqty,
                                        Rate=stock_post_cost,
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
                                        VoucherMasterID=WorkOrderMasterID,
                                        VoucherType=VoucherType,
                                        ProductID=ProductID,
                                        BatchID=BatchID,
                                        WareHouseID=WareHouseID,
                                        QtyOut=chqty,
                                        Rate=stock_post_cost,
                                        PriceListID=PriceListID_DefUnit,
                                        IsActive=IsActive,
                                        CreatedDate=today,
                                        UpdatedDate=today,
                                        CreatedUserID=CreatedUserID,
                                        CompanyID=CompanyID,
                                    )

                                if StockTrans.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, DetailID=WorkOrderDetailsID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                                    stockTra_in = StockTrans.objects.filter(
                                        CompanyID=CompanyID, StockRateID=StockRateID, DetailID=WorkOrderDetailsID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                                    stockTra_in.Qty = float(
                                        stockTra_in.Qty) + float(chqty)
                                    stockTra_in.save()
                                else:
                                    StockTransID = get_auto_StockTransID(
                                        StockTrans, BranchID, CompanyID)
                                    StockTrans.objects.create(
                                        StockTransID=StockTransID,
                                        BranchID=BranchID,
                                        VoucherType=VoucherType,
                                        StockRateID=StockRateID,
                                        DetailID=WorkOrderDetailsID,
                                        MasterID=WorkOrderMasterID,
                                        Qty=chqty,
                                        IsActive=IsActive,
                                        CompanyID=CompanyID,
                                    )

                        elif float(stockRate_instance.Qty) == float(Qty):
                            stockRate_instance.Qty = 0
                            changQty = 0
                            stockRate_instance.save()

                            if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                                                           VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit).exists():
                                stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                                                                              VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit)
                                QtyOut = stockPost_instance.QtyOut
                                newQty = float(QtyOut) + \
                                    float(Qty)
                                stockPost_instance.QtyOut = newQty
                                stockPost_instance.save()
                            else:
                                StockPostingID = get_auto_stockPostid(
                                    StockPosting, BranchID, CompanyID)
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
                                    QtyOut=Qty,
                                    Rate=stock_post_cost,
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
                                    VoucherMasterID=WorkOrderMasterID,
                                    VoucherType=VoucherType,
                                    ProductID=ProductID,
                                    BatchID=BatchID,
                                    WareHouseID=WareHouseID,
                                    QtyOut=Qty,
                                    Rate=stock_post_cost,
                                    PriceListID=PriceListID_DefUnit,
                                    IsActive=IsActive,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CreatedUserID=CreatedUserID,
                                    CompanyID=CompanyID,
                                )

                            if StockTrans.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, DetailID=WorkOrderDetailsID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                                stockTra_in = StockTrans.objects.filter(
                                    CompanyID=CompanyID, StockRateID=StockRateID, DetailID=WorkOrderDetailsID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                                stockTra_in.Qty = float(
                                    stockTra_in.Qty) + float(Qty)
                                stockTra_in.save()
                            else:
                                StockTransID = get_auto_StockTransID(
                                    StockTrans, BranchID, CompanyID)
                                StockTrans.objects.create(
                                    StockTransID=StockTransID,
                                    BranchID=BranchID,
                                    VoucherType=VoucherType,
                                    StockRateID=StockRateID,
                                    DetailID=WorkOrderDetailsID,
                                    MasterID=WorkOrderMasterID,
                                    Qty=Qty,
                                    IsActive=IsActive,
                                    CompanyID=CompanyID,
                                )

                if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, Cost=Cost, WareHouseID=WareHouseID, Qty__lte=0, PriceListID=PriceListID_DefUnit).exists():
                    stockRate_instance = StockRate.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, Cost=Cost, WareHouseID=WareHouseID, Qty__lte=0, PriceListID=PriceListID_DefUnit).first()
                    stock_post_cost = stockRate_instance.Cost
                    if float(changQty) > 0:
                        stockRate_instance.Qty = float(
                            stockRate_instance.Qty) - float(changQty)
                        stockRate_instance.save()

                        if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                                                       VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit).exists():
                            stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                                                                          VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit)
                            QtyOut = stockPost_instance.QtyOut
                            newQty = float(QtyOut) + float(changQty)
                            stockPost_instance.QtyOut = newQty
                            stockPost_instance.save()
                        else:
                            StockPostingID = get_auto_stockPostid(
                                StockPosting, BranchID, CompanyID)
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
                                QtyOut=changQty,
                                Rate=stock_post_cost,
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
                                VoucherMasterID=WorkOrderMasterID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                BatchID=BatchID,
                                WareHouseID=WareHouseID,
                                QtyOut=changQty,
                                Rate=stock_post_cost,
                                PriceListID=PriceListID_DefUnit,
                                IsActive=IsActive,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                            )

                        if not StockTrans.objects.filter(CompanyID=CompanyID,
                                                         StockRateID=stockRate_instance.StockRateID,
                                                         DetailID=WorkOrderDetailsID,
                                                         MasterID=WorkOrderMasterID,
                                                         VoucherType=VoucherType,
                                                         BranchID=BranchID).exists():

                            StockTransID = get_auto_StockTransID(
                                StockTrans, BranchID, CompanyID)
                            StockTrans.objects.create(
                                CompanyID=CompanyID,
                                StockTransID=StockTransID,
                                BranchID=BranchID,
                                VoucherType=VoucherType,
                                StockRateID=stockRate_instance.StockRateID,
                                DetailID=WorkOrderDetailsID,
                                MasterID=WorkOrderMasterID,
                                Qty=changQty,
                                IsActive=IsActive
                            )
                else:
                    if float(changQty) > 0:
                        qty = float(Qty) * -1
                        StockRateID = get_auto_StockRateID(
                            StockRate, BranchID, CompanyID)
                        StockRate.objects.create(
                            StockRateID=StockRateID,
                            BranchID=BranchID,
                            BatchID=BatchID,
                            PurchasePrice=PurchasePrice,
                            SalesPrice=SalesPrice,
                            Qty=qty,
                            Cost=Cost,
                            ProductID=ProductID,
                            WareHouseID=WareHouseID,
                            Date=Date,
                            PriceListID=PriceListID_DefUnit,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        StockPostingID = get_auto_stockPostid(
                            StockPosting, BranchID, CompanyID)
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
                            VoucherMasterID=WorkOrderMasterID,
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
                        StockTransID = get_auto_StockTransID(
                            StockTrans, BranchID, CompanyID)
                        StockTrans.objects.create(
                            StockTransID=StockTransID,
                            BranchID=BranchID,
                            VoucherType=VoucherType,
                            StockRateID=StockRateID,
                            DetailID=WorkOrderDetailsID,
                            MasterID=WorkOrderMasterID,
                            Qty=Qty,
                            IsActive=IsActive,
                            CompanyID=CompanyID,
                        )

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Work Order',
                     'Create', 'Work Order created successfully.', 'Work Order saved successfully.')

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


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_workorder(request, pk):
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
        if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=instance.WorkOrderMasterID, BranchID=instance.BranchID, VoucherType=VoucherType).exists():
            StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=instance.WorkOrderMasterID,
                                        BranchID=instance.BranchID, VoucherType=VoucherType).delete()

        if WorkOrderDetails.objects.filter(CompanyID=CompanyID,BranchID=BranchID,WorkOrderMasterID=instance.WorkOrderMasterID).exists():
            Work_ins = WorkOrderDetails.objects.filter(CompanyID=CompanyID,BranchID=BranchID,WorkOrderMasterID=instance.WorkOrderMasterID)
            for i in Work_ins:
                DetailBatchCode = i.BatchCode
                Qty = i.Qty
                if Batch.objects.filter(CompanyID=CompanyID,BranchID=BranchID,BatchCode=DetailBatchCode).exists():
                    batch_ins = Batch.objects.get(CompanyID=CompanyID,BranchID=BranchID,BatchCode=DetailBatchCode)
                    StockOut = batch_ins.StockOut
                    batch_ins.StockOut = float(StockOut) - float(Qty)
                    batch_ins.save()


        if StockTrans.objects.filter(CompanyID=CompanyID, DetailID=None, MasterID=instance.WorkOrderMasterID, BranchID=BranchID, VoucherType=VoucherType, IsActive=True).exists():
            stockTrans_instance = StockTrans.objects.filter(
                CompanyID=CompanyID, DetailID=None, MasterID=instance.WorkOrderMasterID, BranchID=BranchID, VoucherType=VoucherType, IsActive=True)
            for stck in stockTrans_instance:
                StockRateID = stck.StockRateID
                stck.IsActive = False
                qty_in_stockTrans = stck.Qty
                if StockRate.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, BranchID=BranchID).exists():
                    stockRateInstance = StockRate.objects.get(
                        CompanyID=CompanyID, StockRateID=StockRateID, BranchID=BranchID)
                    stockRateInstance.Qty = float(
                        stockRateInstance.Qty) - float(qty_in_stockTrans)
                    stockRateInstance.save()
                stck.save()


        MasterBatchCode = instance.BatchCode
        MasterProductQty = instance.ProductQty
        if Batch.objects.filter(CompanyID=CompanyID,BranchID=BranchID,BatchCode=MasterBatchCode).exists():
            batch_ins = Batch.objects.get(CompanyID=CompanyID,BranchID=BranchID,BatchCode=MasterBatchCode)
            StockIn = batch_ins.StockIn
            batch_ins.StockIn = float(StockIn) - float(MasterProductQty)
            batch_ins.save()


        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
            check_EnableProductBatchWise = GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
            check_BatchCriteria = "PurchasePriceAndSalesPrice"
            if GeneralSettings.objects.filter(
                    CompanyID=CompanyID, SettingsType="BatchCriteria").exists():
                check_BatchCriteria = GeneralSettings.objects.get(
                    CompanyID=CompanyID, SettingsType="BatchCriteria").SettingsValue
            if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                
                if check_BatchCriteria == "PurchasePrice":
                    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode,PurchasePrice=BatchPurchasePrice).exists():
                        batch_ins = Batch.objects.get(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode,PurchasePrice=BatchPurchasePrice)
                        StockIn = batch_ins.StockIn
                        NewStock = float(StockIn) + float(ProductQty)
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
                            StockIn=ProductQty,
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
                    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode,SalesPrice=BatchSalesPrice).exists():
                        batch_ins = Batch.objects.get(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode,SalesPrice=BatchSalesPrice)
                        StockIn = batch_ins.StockIn
                        NewStock = float(StockIn) + float(ProductQty)
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
                            StockIn=ProductQty,
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
                    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode,PurchasePrice=BatchPurchasePrice,SalesPrice=BatchSalesPrice).exists():
                        batch_ins = Batch.objects.get(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode,PurchasePrice=BatchPurchasePrice,SalesPrice=BatchSalesPrice)
                        StockIn = batch_ins.StockIn
                        NewStock = float(StockIn) + float(ProductQty)
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
                            StockIn=ProductQty,
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
                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode,PriceListID=BatchPriceListID).exists():
                    batch_ins = Batch.objects.get(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode,PriceListID=BatchPriceListID)
                    StockIn = batch_ins.StockIn
                    NewStock = float(StockIn) + float(ProductQty)
                    batch_ins.StockIn = NewStock
                    batch_ins.save()
                else:
                    BatchCode = get_auto_AutoBatchCode(
                        Batch, BranchID, CompanyID)
                    Batch.objects.create(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        BatchCode=BatchCode,
                        StockIn=ProductQty,
                        PurchasePrice=PurchasePrice,
                        SalesPrice=SalesPrice,
                        PriceListID=BatchPriceListID,
                        ProductID=ProductID,
                        WareHouseID=WareHouseID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
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

        MultiFactor = PriceList.objects.get(
            CompanyID=CompanyID, PriceListID=BatchPriceListID, BranchID=BranchID).MultiFactor
        PriceListID = PriceList.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True, BranchID=BranchID).PriceListID

        # PurchasePrice = priceList.PurchasePrice
        # SalesPrice = priceList.SalesPrice

        Qty = float(MultiFactor) * float(ProductQty)
        Cost = float(CostPerPrice) / float(MultiFactor)

        Qy = round(Qty, 4)
        Qty = str(Qy)

        Ct = round(Cost, 4)
        Cost = str(Ct)

        priceList_instance = PriceList.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID, BranchID=BranchID)
        PurchasePrice = priceList_instance.PurchasePrice
        SalesPrice = priceList_instance.SalesPrice

        StockPostingID = get_auto_stockPostid(
            StockPosting, BranchID, CompanyID)

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

        stockRateInstance = None

        if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WareHouseID, PriceListID=PriceListID).exists():
            stockRateInstance = StockRate.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WareHouseID, PriceListID=PriceListID)

            StockRateID = stockRateInstance.StockRateID
            stockRateInstance.Qty = float(stockRateInstance.Qty) + float(Qty)
            stockRateInstance.save()

            if StockTrans.objects.filter(StockRateID=StockRateID, MasterID=instance.WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                stockTra_in = StockTrans.objects.filter(
                    StockRateID=StockRateID, MasterID=instance.WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                stockTra_in.Qty = float(stockTra_in.Qty) + float(Qty)
                stockTra_in.save()
            else:
                StockTransID = get_auto_StockTransID(
                    StockTrans, BranchID, CompanyID)
                StockTrans.objects.create(
                    StockTransID=StockTransID,
                    BranchID=BranchID,
                    VoucherType=VoucherType,
                    StockRateID=StockRateID,
                    MasterID=instance.WorkOrderMasterID,
                    Qty=Qty,
                    IsActive=IsActive,
                    CompanyID=CompanyID,
                )

        else:
            StockRateID = get_auto_StockRateID(StockRate, BranchID, CompanyID)
            StockRate.objects.create(
                StockRateID=StockRateID,
                BranchID=BranchID,
                BatchID=BatchID,
                PurchasePrice=PurchasePrice,
                SalesPrice=SalesPrice,
                Qty=Qty,
                Cost=Cost,
                ProductID=ProductID,
                WareHouseID=WareHouseID,
                Date=Date,
                PriceListID=PriceListID,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )

            StockTransID = get_auto_StockTransID(
                StockTrans, BranchID, CompanyID)
            StockTrans.objects.create(
                StockTransID=StockTransID,
                BranchID=BranchID,
                VoucherType=VoucherType,
                StockRateID=StockRateID,
                MasterID=instance.WorkOrderMasterID,
                Qty=Qty,
                IsActive=IsActive,
                CompanyID=CompanyID,
            )


        deleted_datas = data["deleted_data"]
        if deleted_datas:
            for deleted_Data in deleted_datas:
                deleted_pk = deleted_Data['unq_id']
                WorkOrderMasterID_Deleted = deleted_Data['WorkOrderMasterID']
                WorkOrderDetailsID_Deleted = deleted_Data['WorkOrderDetailsID']
                ProductID_Deleted = deleted_Data['ProductID']
                PriceListID_Deleted = deleted_Data['PriceListID']
                Rate_Deleted = deleted_Data['Rate']
                WarehouseID_Deleted = deleted_Data['WarehouseID']

                if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID_Deleted, DefaultUnit=True).exists():
                    priceList = PriceList.objects.get(
                        CompanyID=CompanyID, ProductID=ProductID_Deleted, DefaultUnit=True)
                    MultiFactor = priceList.MultiFactor
                    Cost = float(Rate_Deleted) / float(MultiFactor)
                    Ct = round(Cost, 4)
                    Cost_Deleted = str(Ct)

                    if not deleted_pk == '' or not deleted_pk == 0:
                        if WorkOrderDetails.objects.filter(CompanyID=CompanyID, pk=deleted_pk).exists():
                            deleted_detail = WorkOrderDetails.objects.filter(
                                CompanyID=CompanyID, pk=deleted_pk)
                            deleted_detail.delete()


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
                                        stockRateInstance.Qty = float(
                                            stockRateInstance.Qty) + float(qty_in_stockTrans)
                                        stockRateInstance.save()
                                    stck.save()

        

        WorkOrderDetails_ins = data["WorkOrderDetails"]

        for WorkOrderDetail in WorkOrderDetails_ins:
            pk = WorkOrderDetail['id']
            ProductID = WorkOrderDetail['ProductID']
            if ProductID:
                Qty = float(WorkOrderDetail['Qty'])
                DetailPriceListID = WorkOrderDetail['PriceListID']
                CostPerPrice = float(WorkOrderDetail['CostPerItem'])
                UnitPrice = float(WorkOrderDetail['UnitPrice'])
                DetailPurchasePrice = float(WorkOrderDetail['PurchasePrice'])
                DetailSalesPrice = float(WorkOrderDetail['UnitPrice'])
                Amount = float(WorkOrderDetail['NetAmount'])
                BatchCode = float(WorkOrderDetail['BatchCode'])
                InclusivePrice = float(WorkOrderDetail['InclusivePrice'])
                is_inclusive = WorkOrderDetail['is_inclusive']

                DetailQty = round(Qty, PriceRounding)
                UnitPrice = round(UnitPrice, PriceRounding)
                CostPerPrice = round(CostPerPrice, PriceRounding)
                DetailPurchasePrice = round(DetailPurchasePrice, PriceRounding)
                DetailSalesPrice = round(DetailSalesPrice, PriceRounding)
                Amount = round(Amount, PriceRounding)

                # WorkOrderDetailsID = get_auto_id(
                    # WorkOrderDetails, BranchID, CompanyID)
                if is_inclusive == True:
                    DetailSalesPrice = str(InclusivePrice)
                else:
                    DetailSalesPrice = str(UnitPrice)

                DetailPurchasePrice = str(DetailPurchasePrice)

                workorder_details_instance = WorkOrderDetails.objects.get(
                    CompanyID=CompanyID, pk=pk)

                WorkOrderDetailsID = workorder_details_instance.WorkOrderDetailsID

                if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
                    check_EnableProductBatchWise = GeneralSettings.objects.get(
                        CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue

                    check_BatchCriteria = "PurchasePriceAndSalesPrice"
                    # if GeneralSettings.objects.filter(
                    #         CompanyID=CompanyID, SettingsType="BatchCriteria").exists():
                    #     check_BatchCriteria = GeneralSettings.objects.get(
                    #         CompanyID=CompanyID, SettingsType="BatchCriteria").SettingsValue

                    if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                        if check_BatchCriteria == "PurchasePrice":
                            if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode,PurchasePrice=DetailPurchasePrice).exists():
                                batch_ins = Batch.objects.get(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=DetailPurchasePrice)
                                StockOut = batch_ins.StockOut
                                NewStock = float(StockOut) + float(DetailQty)
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
                                    StockOut=DetailQty,
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
                                batch_ins = Batch.objects.get(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, SalesPrice=DetailSalesPrice)
                                StockOut = batch_ins.StockOut
                                NewStock = float(StockOut) + float(DetailQty)
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
                                    StockOut=DetailQty,
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
                                batch_ins = Batch.objects.get(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=DetailPurchasePrice, SalesPrice=DetailSalesPrice)
                                StockOut = batch_ins.StockOut
                                NewStock = float(StockOut) + float(DetailQty)
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
                                    StockOut=DetailQty,
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
                        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode,PriceListID=PriceListID).exists():
                            batch_ins = Batch.objects.get(CompanyID=CompanyID, BranchID=BranchID,BatchCode=BatchCode,PriceListID=PriceListID)
                            StockOut = batch_ins.StockOut
                            NewStock = float(StockOut) + float(Qty)
                            batch_ins.StockOut = NewStock
                            batch_ins.save()
                        else:
                            BatchCode = get_auto_AutoBatchCode(Batch, BranchID, CompanyID)
                            Batch.objects.create(
                                CompanyID=CompanyID,
                                BranchID=BranchID,
                                BatchCode=BatchCode,
                                StockOut=Qty,
                                PurchasePrice=PurchasePrice,
                                SalesPrice=SalesPrice,
                                PriceListID=PriceListID,
                                ProductID=ProductID,
                                WareHouseID=WareHouseID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
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
                # workorder_details_instance.CreatedUserID = CreatedUserID
                workorder_details_instance.save()

                WorkOrderDetails_Log.objects.create(
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

                Qty = float(MultiFactor) * float(DetailQty)
                Cost = float(CostPerPrice) / float(MultiFactor)

                Qy = round(Qty, 4)
                Qty = str(Qy)

                Ct = round(Cost, 4)
                Cost = str(Ct)

                priceList_instance = PriceList.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID_DefUnit, BranchID=BranchID)
                PurchasePrice = priceList_instance.PurchasePrice
                SalesPrice = priceList_instance.SalesPrice


                changQty = Qty
                if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WareHouseID, Qty__gt=0, PriceListID=PriceListID_DefUnit).exists():
                    stockRate_instances = StockRate.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WareHouseID, Qty__gt=0, PriceListID=PriceListID_DefUnit)
                    count = stockRate_instances.count()
                    last = 0
                    for stockRate_instance in stockRate_instances:
                        last = float(last) + float(1)
                        StockRateID = stockRate_instance.StockRateID
                        stock_post_cost = stockRate_instance.Cost
                        if float(stockRate_instance.Qty) > float(Qty):
                            stockRate_instance.Qty = float(
                                stockRate_instance.Qty) - float(Qty)
                            changQty = 0
                            stockRate_instance.save()

                            if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                                                           VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit).exists():
                                stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                                                                              VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit)
                                QtyOut = stockPost_instance.QtyOut
                                newQty = float(QtyOut) + float(Qty)

                                stockPost_instance.QtyOut = newQty
                                stockPost_instance.save()
                            else:
                                StockPostingID = get_auto_stockPostid(
                                    StockPosting, BranchID, CompanyID)
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
                                    QtyOut=Qty,
                                    Rate=stock_post_cost,
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
                                    VoucherMasterID=WorkOrderMasterID,
                                    VoucherType=VoucherType,
                                    ProductID=ProductID,
                                    BatchID=BatchID,
                                    WareHouseID=WareHouseID,
                                    QtyOut=Qty,
                                    Rate=stock_post_cost,
                                    PriceListID=PriceListID_DefUnit,
                                    IsActive=IsActive,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CreatedUserID=CreatedUserID,
                                    CompanyID=CompanyID,
                                )

                            if StockTrans.objects.filter(StockRateID=StockRateID, DetailID=WorkOrderDetailsID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                                stockTra_in = StockTrans.objects.filter(
                                    StockRateID=StockRateID, DetailID=WorkOrderDetailsID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                                stockTra_in.Qty = float(
                                    stockTra_in.Qty) + float(Qty)
                                stockTra_in.save()
                            else:
                                StockTransID = get_auto_StockTransID(
                                    StockTrans, BranchID, CompanyID)
                                StockTrans.objects.create(
                                    StockTransID=StockTransID,
                                    BranchID=BranchID,
                                    VoucherType=VoucherType,
                                    StockRateID=StockRateID,
                                    DetailID=WorkOrderDetailsID,
                                    MasterID=WorkOrderMasterID,
                                    Qty=Qty,
                                    IsActive=IsActive,
                                    CompanyID=CompanyID,
                                )
                        elif float(stockRate_instance.Qty) < float(Qty):

                            if float(changQty) > float(stockRate_instance.Qty):
                                changQty = float(changQty) - \
                                    float(stockRate_instance.Qty)
                                stckQty = stockRate_instance.Qty
                                stockRate_instance.Qty = 0
                                stockRate_instance.save()

                                if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                                                               VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit).exists():
                                    stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                                                                                  VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit)
                                    QtyOut = stockPost_instance.QtyOut
                                    newQty = float(QtyOut) + \
                                        float(stockRate_instance.Qty)
                                    stockPost_instance.QtyOut = newQty
                                    stockPost_instance.save()
                                else:
                                    StockPostingID = get_auto_stockPostid(
                                        StockPosting, BranchID, CompanyID)
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
                                        QtyOut=stckQty,
                                        Rate=stock_post_cost,
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
                                        VoucherMasterID=WorkOrderMasterID,
                                        VoucherType=VoucherType,
                                        ProductID=ProductID,
                                        BatchID=BatchID,
                                        WareHouseID=WareHouseID,
                                        QtyOut=stckQty,
                                        Rate=stock_post_cost,
                                        PriceListID=PriceListID_DefUnit,
                                        IsActive=IsActive,
                                        CreatedDate=today,
                                        UpdatedDate=today,
                                        CreatedUserID=CreatedUserID,
                                        CompanyID=CompanyID,
                                    )
                                if StockTrans.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, DetailID=WorkOrderDetailsID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                                    stockTra_in = StockTrans.objects.filter(
                                        CompanyID=CompanyID, StockRateID=StockRateID, DetailID=WorkOrderDetailsID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                                    stockTra_in.Qty = float(
                                        stockTra_in.Qty) + float(stockRate_instance.Qty)
                                    stockTra_in.save()
                                else:
                                    StockTransID = get_auto_StockTransID(
                                        StockTrans, BranchID, CompanyID)
                                    StockTrans.objects.create(
                                        StockTransID=StockTransID,
                                        BranchID=BranchID,
                                        VoucherType=VoucherType,
                                        StockRateID=StockRateID,
                                        DetailID=WorkOrderDetailsID,
                                        MasterID=WorkOrderMasterID,
                                        Qty=stockRate_instance.Qty,
                                        IsActive=IsActive,
                                        CompanyID=CompanyID,
                                    )
                            else:
                                if changQty < 0:
                                    changQty = 0
                                chqty = changQty
                                changQty = float(
                                    stockRate_instance.Qty) - float(changQty)
                                stockRate_instance.Qty = changQty
                                changQty = 0
                                stockRate_instance.save()

                                if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                                                               VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit).exists():
                                    stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                                                                                  VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit)
                                    QtyOut = stockPost_instance.QtyOut
                                    newQty = float(QtyOut) + float(chqty)
                                    stockPost_instance.QtyOut = newQty
                                    stockPost_instance.save()
                                else:
                                    StockPostingID = get_auto_stockPostid(
                                        StockPosting, BranchID, CompanyID)
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
                                        QtyOut=chqty,
                                        Rate=stock_post_cost,
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
                                        VoucherMasterID=WorkOrderMasterID,
                                        VoucherType=VoucherType,
                                        ProductID=ProductID,
                                        BatchID=BatchID,
                                        WareHouseID=WareHouseID,
                                        QtyOut=chqty,
                                        Rate=stock_post_cost,
                                        PriceListID=PriceListID_DefUnit,
                                        IsActive=IsActive,
                                        CreatedDate=today,
                                        UpdatedDate=today,
                                        CreatedUserID=CreatedUserID,
                                        CompanyID=CompanyID,
                                    )

                                if StockTrans.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, DetailID=WorkOrderDetailsID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                                    stockTra_in = StockTrans.objects.filter(
                                        CompanyID=CompanyID, StockRateID=StockRateID, DetailID=WorkOrderDetailsID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                                    stockTra_in.Qty = float(
                                        stockTra_in.Qty) + float(chqty)
                                    stockTra_in.save()
                                else:
                                    StockTransID = get_auto_StockTransID(
                                        StockTrans, BranchID, CompanyID)
                                    StockTrans.objects.create(
                                        StockTransID=StockTransID,
                                        BranchID=BranchID,
                                        VoucherType=VoucherType,
                                        StockRateID=StockRateID,
                                        DetailID=WorkOrderDetailsID,
                                        MasterID=WorkOrderMasterID,
                                        Qty=chqty,
                                        IsActive=IsActive,
                                        CompanyID=CompanyID,
                                    )

                        elif float(stockRate_instance.Qty) == float(Qty):
                            stockRate_instance.Qty = 0
                            changQty = 0
                            stockRate_instance.save()

                            if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                                                           VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit).exists():
                                stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                                                                              VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit)
                                QtyOut = stockPost_instance.QtyOut
                                newQty = float(QtyOut) + \
                                    float(Qty)
                                stockPost_instance.QtyOut = newQty
                                stockPost_instance.save()
                            else:
                                StockPostingID = get_auto_stockPostid(
                                    StockPosting, BranchID, CompanyID)
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
                                    QtyOut=Qty,
                                    Rate=stock_post_cost,
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
                                    VoucherMasterID=WorkOrderMasterID,
                                    VoucherType=VoucherType,
                                    ProductID=ProductID,
                                    BatchID=BatchID,
                                    WareHouseID=WareHouseID,
                                    QtyOut=Qty,
                                    Rate=stock_post_cost,
                                    PriceListID=PriceListID_DefUnit,
                                    IsActive=IsActive,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CreatedUserID=CreatedUserID,
                                    CompanyID=CompanyID,
                                )

                            if StockTrans.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, DetailID=WorkOrderDetailsID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                                stockTra_in = StockTrans.objects.filter(
                                    CompanyID=CompanyID, StockRateID=StockRateID, DetailID=WorkOrderDetailsID, MasterID=WorkOrderMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                                stockTra_in.Qty = float(
                                    stockTra_in.Qty) + float(Qty)
                                stockTra_in.save()
                            else:
                                StockTransID = get_auto_StockTransID(
                                    StockTrans, BranchID, CompanyID)
                                StockTrans.objects.create(
                                    StockTransID=StockTransID,
                                    BranchID=BranchID,
                                    VoucherType=VoucherType,
                                    StockRateID=StockRateID,
                                    DetailID=WorkOrderDetailsID,
                                    MasterID=WorkOrderMasterID,
                                    Qty=Qty,
                                    IsActive=IsActive,
                                    CompanyID=CompanyID,
                                )

                if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, Cost=Cost, WareHouseID=WareHouseID, Qty__lte=0, PriceListID=PriceListID_DefUnit).exists():
                    stockRate_instance = StockRate.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, Cost=Cost, WareHouseID=WareHouseID, Qty__lte=0, PriceListID=PriceListID_DefUnit).first()
                    stock_post_cost = stockRate_instance.Cost
                    if float(changQty) > 0:
                        stockRate_instance.Qty = float(
                            stockRate_instance.Qty) - float(changQty)
                        stockRate_instance.save()

                        if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                                                       VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit).exists():
                            stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WareHouseID, ProductID=ProductID, BranchID=BranchID,
                                                                          VoucherMasterID=WorkOrderMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit)
                            QtyOut = stockPost_instance.QtyOut
                            newQty = float(QtyOut) + float(changQty)
                            stockPost_instance.QtyOut = newQty
                            stockPost_instance.save()
                        else:
                            StockPostingID = get_auto_stockPostid(
                                StockPosting, BranchID, CompanyID)
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
                                QtyOut=changQty,
                                Rate=stock_post_cost,
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
                                VoucherMasterID=WorkOrderMasterID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                BatchID=BatchID,
                                WareHouseID=WareHouseID,
                                QtyOut=changQty,
                                Rate=stock_post_cost,
                                PriceListID=PriceListID_DefUnit,
                                IsActive=IsActive,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                            )

                        if not StockTrans.objects.filter(CompanyID=CompanyID,
                                                         StockRateID=stockRate_instance.StockRateID,
                                                         DetailID=WorkOrderDetailsID,
                                                         MasterID=WorkOrderMasterID,
                                                         VoucherType=VoucherType,
                                                         BranchID=BranchID).exists():

                            StockTransID = get_auto_StockTransID(
                                StockTrans, BranchID, CompanyID)
                            StockTrans.objects.create(
                                CompanyID=CompanyID,
                                StockTransID=StockTransID,
                                BranchID=BranchID,
                                VoucherType=VoucherType,
                                StockRateID=stockRate_instance.StockRateID,
                                DetailID=WorkOrderDetailsID,
                                MasterID=WorkOrderMasterID,
                                Qty=changQty,
                                IsActive=IsActive
                            )
                else:
                    if float(changQty) > 0:
                        qty = float(Qty) * -1
                        StockRateID = get_auto_StockRateID(
                            StockRate, BranchID, CompanyID)
                        StockRate.objects.create(
                            StockRateID=StockRateID,
                            BranchID=BranchID,
                            BatchID=BatchID,
                            PurchasePrice=PurchasePrice,
                            SalesPrice=SalesPrice,
                            Qty=qty,
                            Cost=Cost,
                            ProductID=ProductID,
                            WareHouseID=WareHouseID,
                            Date=Date,
                            PriceListID=PriceListID_DefUnit,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        StockPostingID = get_auto_stockPostid(
                            StockPosting, BranchID, CompanyID)
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
                            VoucherMasterID=WorkOrderMasterID,
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
                        StockTransID = get_auto_StockTransID(
                            StockTrans, BranchID, CompanyID)
                        StockTrans.objects.create(
                            StockTransID=StockTransID,
                            BranchID=BranchID,
                            VoucherType=VoucherType,
                            StockRateID=StockRateID,
                            DetailID=WorkOrderDetailsID,
                            MasterID=WorkOrderMasterID,
                            Qty=Qty,
                            IsActive=IsActive,
                            CompanyID=CompanyID,
                        )

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Work Order',
                     'Create', 'Work Order created successfully.', 'Work Order saved successfully.')

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
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Workorder',
                         'List', 'Workorder List Viewed successfully.', 'Workorder List Viewed successfully.')
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
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Workorder',
                     'View', 'Workorder Single Viewed successfully.', 'Workorder Single Viewed successfully.')
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
            product_serializer = serializers.WorkOrderSerializer(
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
                                                             "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding,})
                
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