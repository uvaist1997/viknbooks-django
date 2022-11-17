from brands.models import PurchaseMaster, PurchaseMaster_Log, PurchaseDetails, PurchaseDetails_Log, StockPosting, LedgerPosting, StockPosting_Log,\
LedgerPosting_Log, PurchaseDetailsDummy, StockRate, PriceList, StockTrans,ProductGroup,Brand,Unit,Warehouse,PurchaseReturnMaster,OpeningStockMaster,GeneralSettings,Product,WorkOrderMaster,WorkOrderMaster_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v2.purchases.serializers import PurchaseMasterSerializer, PurchaseMasterRestSerializer, PurchaseDetailsSerializer,\
PurchaseDetailsRestSerializer, PurchaseMasterReportSerializer, PurchaseMasterForReturnSerializer
from api.v2.brands.serializers import ListSerializer
from api.v2.purchases.functions import generate_serializer_errors
from api.v2.products.functions import get_auto_AutoBatchCode
from rest_framework import status
from api.v2.sales.serializers import ListSerializerforReport
from api.v2.workOrder.functions import get_auto_id, get_auto_idMaster, get_auto_StockRateID, get_auto_StockTransID
from api.v2.sales.functions import get_auto_stockPostid 
from api.v2.accountLedgers.functions import get_auto_LedgerPostid
import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from main.functions import get_company, activity_log
from api.v2.purchaseReturns.serializers import PurchaseReturnMasterRestSerializer
import re



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_workOrder(request):
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
    PriceList = data['PriceList']
    Amount = data['Amount']
    TotalQty = data['TotalQty']
    GrandTotal = data['GrandTotal']
    IsActive = data['IsActive']
    ManufactureDate = data['ManufactureDate']
    ExpiryDate = data['ExpiryDate']
    

    Action = "A"

    VoucherType = "WO"
    BatchID = 1

    #checking voucher number already exist
    VoucherNoLow = VoucherNo.lower()
    is_voucherExist = False
    insts = WorkOrderMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
    if insts:
        for i in insts:
            voucher_no = i.VoucherNo
            voucherNo = voucher_no.lower()
            if VoucherNoLow == voucherNo:
                is_voucherExist = True

    if not is_voucherExist:

        WorkOrderMasterID = get_auto_idMaster(WorkOrderMaster,BranchID,CompanyID)

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
            ProductQty=ProductQty,
            CostPerPrice=CostPerPrice,
            PriceListID=PriceListID,
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
            ProductQty=ProductQty,
            CostPerPrice=CostPerPrice,
            PriceListID=PriceListID,
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


        MultiFactor = PriceList.objects.get(CompanyID=CompanyID,PriceListID=PriceListID,BranchID=BranchID).MultiFactor
        PriceListID = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,DefaultUnit=True,BranchID=BranchID).PriceListID

        # PurchasePrice = priceList.PurchasePrice
        # SalesPrice = priceList.SalesPrice


        Qty = float(MultiFactor) * float(Qty)
        Cost = float(CostPerPrice) /  float(MultiFactor)

        Qy = round(Qty,4)
        Qty = str(Qy)

        Ct = round(Cost,4)
        Cost = str(Ct)

        princeList_instance = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,PriceListID=PriceListID,BranchID=BranchID)
        PurchasePrice = princeList_instance.PurchasePrice
        SalesPrice = princeList_instance.SalesPrice

        StockPostingID = get_auto_stockPostid(StockPosting,BranchID,CompanyID)

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

        if StockRate.objects.filter(CompanyID=CompanyID,BranchID=BranchID,Cost=Cost,ProductID=ProductID,WareHouseID=WareHouseID,PriceListID=PriceListID).exists():
            stockRateInstance = StockRate.objects.get(CompanyID=CompanyID,BranchID=BranchID,Cost=Cost,ProductID=ProductID,WareHouseID=WareHouseID,PriceListID=PriceListID)
            
            StockRateID = stockRateInstance.StockRateID
            stockRateInstance.Qty = float(stockRateInstance.Qty) + float(Qty)
            stockRateInstance.save()

            if StockTrans.objects.filter(StockRateID=StockRateID,MasterID=WorkOrderMasterID,VoucherType=VoucherType,BranchID=BranchID).exists():
                stockTra_in = StockTrans.objects.filter(StockRateID=StockRateID,MasterID=WorkOrderMasterID,VoucherType=VoucherType,BranchID=BranchID).first()
                stockTra_in.Qty = float(stockTra_in.Qty) + float(Qty)
                stockTra_in.save()
            else:
                StockTransID = get_auto_StockTransID(StockTrans,BranchID,CompanyID)
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
            StockRateID = get_auto_StockRateID(StockRate,BranchID,CompanyID)
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

            StockTransID = get_auto_StockTransID(StockTrans,BranchID,CompanyID)
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


        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
            check_EnableProductBatchWise = GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
            if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                if Batch.objects.filter(CompanyID=CompanyID,BranchID=BranchID,ProductID=ProductID,PriceListID=PriceListID,WareHouseID=WareHouseID,PurchasePrice=PurchasePrice).exists():
                    batch_ins = Batch.objects.filter(CompanyID=CompanyID,BranchID=BranchID,ProductID=ProductID,PriceListID=PriceListID,WareHouseID=WareHouseID,PurchasePrice=PurchasePrice).first()
                    StockIn = batch_ins.StockIn
                    NewStock = float(StockIn) + float(TotalQty)
                    batch_ins.update(ManufactureDate=ManufactureDate,ExpiryDate=ExpiryDate,StockIn=NewStock)
                else:
                    BatchCode = get_auto_AutoBatchCode(Batch, BranchID, CompanyID)
                    Batch.objects.create(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        ManufactureDate=ManufactureDate,
                        ExpiryDate=ExpiryDate,
                        BatchCode=BatchCode,
                        StockIn=TotalQty,
                        PurchasePrice=PurchasePrice,
                        SalesPrice=SalesPrice,
                        PriceListID=PriceListID,
                        ProductID=ProductID,
                        WareHouseID=WareHouseID,
                        Description=Notes,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CreatedUserID=CreatedUserID,
                        )
            else:
                if Batch.objects.filter(CompanyID=CompanyID,BranchID=BranchID,ProductID=ProductID,PriceListID=PriceListID,WareHouseID=WareHouseID,PurchasePrice=PurchasePrice).exists():
                    batch_ins = Batch.objects.filter(CompanyID=CompanyID,BranchID=BranchID,ProductID=ProductID,PriceListID=PriceListID,WareHouseID=WareHouseID,PurchasePrice=PurchasePrice).first()
                    StockIn = batch_ins.StockIn
                    NewStock = float(StockIn) + float(TotalQty)
                    batch_ins.update(ManufactureDate=ManufactureDate,ExpiryDate=ExpiryDate,StockIn=NewStock)



        WorkOrderDetails = data["WorkOrderDetails"]

        for WorkOrderDetail in WorkOrderDetails:  

            # PurchaseMasterID = serialized.data['PurchaseMasterID']
            WorkOrderMasterID = purchaseDetail['WorkOrderMasterID']
            ProductID = purchaseDetail['ProductID']
            Qty = float(purchaseDetail['Qty'])
            PriceListID = purchaseDetail['PriceListID']
            CostPerPrice = float(purchaseDetail['CostPerPrice'])
            Amount = float(purchaseDetail['Amount'])
            
            Qty = round(Qty,PriceRounding)
            CostPerPrice = round(CostPerPrice,PriceRounding)
            Amount = round(Amount,PriceRounding)
            
            WorkOrderDetailsID = get_auto_id(WorkOrderDetails,BranchID,CompanyID)

            WorkOrderDetails.objects.create(
                CompanyID=CompanyID,
                WorkOrderDetailsID=WorkOrderDetailsID,
                BranchID=BranchID,
                Action=Action,
                WorkOrderMasterID=WorkOrderMasterID,
                ProductID=ProductID,
                Qty=Qty,
                PriceListID=PriceListID,
                CostPerPrice=CostPerPrice,
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
                Qty=Qty,
                PriceListID=PriceListID,
                CostPerPrice=CostPerPrice,
                Amount=Amount,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                )





            MultiFactor = PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).MultiFactor
            PriceListID_DefUnit = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True, BranchID=BranchID).PriceListID

            # PriceListID_DefUnit = priceList.PriceListID
            # MultiFactor = priceList.MultiFactor

            # PurchasePrice = priceList.PurchasePrice
            # SalesPrice = priceList.SalesPrice
            DetailQty = Qty

            Qty = float(MultiFactor) * float(Qty)
            Cost = float(CostPerPrice) / float(MultiFactor)

            Qy = round(Qty, 4)
            Qty = str(Qy)

            Ct = round(Cost, 4)
            Cost = str(Ct)

            princeList_instance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID_DefUnit, BranchID=BranchID)
            PurchasePrice = princeList_instance.PurchasePrice
            SalesPrice = princeList_instance.SalesPrice


            if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
                check_EnableProductBatchWise = GeneralSettings.objects.get(
                    CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
                if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                    if Batch.objects.filter(CompanyID=CompanyID,BranchID=BranchID,ProductID=ProductID,PriceListID=PriceListID,WareHouseID=WareHouseID,PurchasePrice=PurchasePrice).exists():
                        batch_ins = Batch.objects.filter(CompanyID=CompanyID,BranchID=BranchID,ProductID=ProductID,PriceListID=PriceListID,WareHouseID=WareHouseID,PurchasePrice=PurchasePrice).first()
                        StockIn = batch_ins.StockIn
                        NewStock = float(StockIn) - float(DetailQty)
                        batch_ins.update(StockOut=NewStock)
                    else:
                        BatchCode = get_auto_AutoBatchCode(Batch, BranchID, CompanyID)
                        Batch.objects.create(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            BatchCode=BatchCode,
                            StockOut=DetailQty,
                            PurchasePrice=PurchasePrice,
                            SalesPrice=SalesPrice,
                            PriceListID=PriceListID,
                            ProductID=ProductID,
                            WareHouseID=WareHouseID,
                            Description=Notes,
                            CreatedDate=CreatedDate,
                            UpdatedDate=UpdatedDate,
                            CreatedUserID=CreatedUserID,
                            )
                else:
                    if Batch.objects.filter(CompanyID=CompanyID,BranchID=BranchID,ProductID=ProductID,PriceListID=PriceListID,WareHouseID=WareHouseID,PurchasePrice=PurchasePrice).exists():
                        batch_ins = Batch.objects.filter(CompanyID=CompanyID,BranchID=BranchID,ProductID=ProductID,PriceListID=PriceListID,WareHouseID=WareHouseID,PurchasePrice=PurchasePrice).first()
                        StockIn = batch_ins.StockIn
                        NewStock = float(StockIn) - float(DetailQty)
                        batch_ins.update(StockOut=NewStock)
                        

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
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Work Order', 'Create', 'Work Order created successfully.', 'Work Order saved successfully.')

        response_data = {
            "StatusCode" : 6000,
            "id": instance.id,
            "message" : "Work Order created Successfully!!!",
            }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Work Order', 'Create', 'Work Order created Failed.', 'VoucherNo already exist')
        response_data = {
        "StatusCode" : 6001,
        "message" : "VoucherNo already exist!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


