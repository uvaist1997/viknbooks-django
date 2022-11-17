from brands.models import Product,VoucherNoTable,StockTransferMaster_ID, StockTransferMasterID_Log, StockTransferDetails, StockTransferDetails_Log,\
    StockTransferDetailsDummy, StockRate, StockTrans, StockPosting, StockPosting_Log, PriceList, UserTable
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v6.stockTransfers.serializers import StockTransferMaster_IDSerializer, StockTransferMaster_IDRestSerializer,\
    StockTransferDetailsSerializer, StockTransferDetailsRestSerializer, StockTransferRegisterReportSerializer,StockTransferMaster1_IDRestSerializer
from api.v6.brands.serializers import ListSerializer
from api.v6.stockTransfers.functions import generate_serializer_errors
from rest_framework import status
from api.v6.stockTransfers.functions import get_auto_id, get_auto_idMaster
from api.v6.purchases.functions import get_auto_StockRateID, get_auto_StockTransID
from api.v6.sales.functions import get_auto_stockPostid, get_auto_VoucherNo
import datetime
from django.shortcuts import get_object_or_404
from main.functions import get_company, activity_log, list_pagination
from django.db import transaction,IntegrityError
import re,sys, os
from main.functions import update_voucher_table
from api.v6.products.functions import update_stock


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def create_stockTransfer(request):
    try:
        with transaction.atomic():
            today = datetime.datetime.now()
            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            BranchID = data['BranchID']
            CreatedUserID = data['CreatedUserID']
            Date = data['Date']
            VoucherNo = data['VoucherNo']
            Notes = data['Notes']
            TransferredByID = data['TransferredByID']
            WarehouseFromID = data['WarehouseFromID']
            WarehouseToID = data['WarehouseToID']
            TotalQty = data['TotalQty']
            GrandTotal = data['GrandTotal']
            IsActive = data['IsActive']
            BatchID = data['BatchID']
            MaxGrandTotal = data['MaxGrandTotal']

            Action = "A"
            VoucherType = "ST"
            # VoucherNo Updated
            try:
                PreFix = data['PreFix']
            except:
                PreFix = "ST"

            try:
                Seperator = data['Seperator']
            except:
                Seperator = ""

            try:
                InvoiceNo = data['InvoiceNo']
            except:
                InvoiceNo = 1

            update_voucher_table(CompanyID,CreatedUserID,VoucherType,PreFix,Seperator, InvoiceNo)
            StockTransferMasterID = get_auto_idMaster(
                StockTransferMaster_ID, BranchID, CompanyID)
            # VoucherNo = get_auto_VoucherNo(StockTransferMaster_ID,BranchID)
            StockTransferMasterID_Log.objects.create(
                TransactionID=StockTransferMasterID,
                BranchID=BranchID,
                VoucherNo=VoucherNo,
                Date=Date,
                Notes=Notes,
                TransferredByID=TransferredByID,
                WarehouseFromID=WarehouseFromID,
                WarehouseToID=WarehouseToID,
                TotalQty=TotalQty,
                GrandTotal=GrandTotal,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                CompanyID=CompanyID,
                MaxGrandTotal=MaxGrandTotal
            )

            StockTransferMaster_ID.objects.create(
                StockTransferMasterID=StockTransferMasterID,
                BranchID=BranchID,
                VoucherNo=VoucherNo,
                Date=Date,
                Notes=Notes,
                TransferredByID=TransferredByID,
                WarehouseFromID=WarehouseFromID,
                WarehouseToID=WarehouseToID,
                TotalQty=TotalQty,
                GrandTotal=GrandTotal,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                CompanyID=CompanyID,
                MaxGrandTotal=MaxGrandTotal
            )

            stockTransferDetails = data["StockTransferDetails"]

            for stockTransferDetail in stockTransferDetails:
                # StockTransferMasterID = stockTransferDetail['StockTransferMasterID']
                ProductID = stockTransferDetail['ProductID']
                Qty = stockTransferDetail['Qty']
                PriceListID = stockTransferDetail['PriceListID']
                Rate = stockTransferDetail['Rate']
                MaxRate = stockTransferDetail['MaxRate']
                Amount = stockTransferDetail['Amount']
                MaxAmount = stockTransferDetail['MaxAmount']

                StockTransferDetailsID = get_auto_id(
                    StockTransferDetails, BranchID, CompanyID)

                log_instance = StockTransferDetails_Log.objects.create(
                    TransactionID=StockTransferDetailsID,
                    BranchID=BranchID,
                    StockTransferMasterID=StockTransferMasterID,
                    ProductID=ProductID,
                    Qty=Qty,
                    PriceListID=PriceListID,
                    Rate=Rate,
                    MaxRate=MaxRate,
                    Amount=Amount,
                    MaxAmount=MaxAmount,
                    Action=Action,
                    CompanyID=CompanyID
                )
                StockTransferDetails.objects.create(
                    StockTransferDetailsID=StockTransferDetailsID,
                    BranchID=BranchID,
                    StockTransferMasterID=StockTransferMasterID,
                    ProductID=ProductID,
                    Qty=Qty,
                    PriceListID=PriceListID,
                    Rate=Rate,
                    MaxRate=MaxRate,
                    Amount=Amount,
                    MaxAmount=MaxAmount,
                    Action=Action,
                    CompanyID=CompanyID,
                    LogID=log_instance.ID
                )

                

                # priceList = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,DefaultUnit=True,BranchID=BranchID)

                # PriceListID = priceList.PriceListID
                # MultiFactor = priceList.MultiFactor

                MultiFactor = PriceList.objects.get(
                    CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).MultiFactor
                PriceListID = PriceList.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True, BranchID=BranchID).PriceListID

                # PurchasePrice = priceList.PurchasePrice
                # SalesPrice = priceList.SalesPrice
                princeList_instance = PriceList.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID, BranchID=BranchID)
                PurchasePrice = princeList_instance.PurchasePrice
                SalesPrice = princeList_instance.SalesPrice

                Qty = float(MultiFactor) * float(Qty)
                Cost = float(Rate) / float(MultiFactor)

                # Qy = round(Qty, 4)
                # Qty = str(Qy)

                # Ct = round(Cost, 4)
                # Cost = str(Ct)

                princeList_instance = PriceList.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID, BranchID=BranchID)
                PurchasePrice = princeList_instance.PurchasePrice
                SalesPrice = princeList_instance.SalesPrice

                # transfer from warehouse stock post

                StockPostingID = get_auto_stockPostid(
                    StockPosting, BranchID, CompanyID)

                StockPosting.objects.create(
                    StockPostingID=StockPostingID,
                    BranchID=BranchID,
                    Action=Action,
                    Date=Date,
                    VoucherMasterID=StockTransferMasterID,
                    VoucherDetailID=StockTransferDetailsID,
                    VoucherType=VoucherType,
                    ProductID=ProductID,
                    BatchID=BatchID,
                    WareHouseID=WarehouseFromID,
                    QtyOut=Qty,
                    Rate=Cost,
                    PriceListID=PriceListID,
                    IsActive=IsActive,
                    CreatedDate=today,
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID
                )

                StockPosting_Log.objects.create(
                    TransactionID=StockPostingID,
                    BranchID=BranchID,
                    Action=Action,
                    Date=Date,
                    VoucherMasterID=StockTransferMasterID,
                    VoucherDetailID=StockTransferDetailsID,
                    VoucherType=VoucherType,
                    ProductID=ProductID,
                    BatchID=BatchID,
                    WareHouseID=WarehouseFromID,
                    QtyOut=Qty,
                    Rate=Cost,
                    PriceListID=PriceListID,
                    IsActive=IsActive,
                    CreatedDate=today,
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID
                )

                update_stock(CompanyID,BranchID,ProductID)

                # transfer to warehouse stock post
                StockPostingID = get_auto_stockPostid(
                    StockPosting, BranchID, CompanyID)

                StockPosting.objects.create(
                    StockPostingID=StockPostingID,
                    BranchID=BranchID,
                    Action=Action,
                    Date=Date,
                    VoucherMasterID=StockTransferMasterID,
                    VoucherDetailID=StockTransferDetailsID,
                    VoucherType=VoucherType,
                    ProductID=ProductID,
                    BatchID=BatchID,
                    WareHouseID=WarehouseToID,
                    QtyIn=Qty,
                    Rate=Cost,
                    PriceListID=PriceListID,
                    IsActive=IsActive,
                    CreatedDate=today,
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID
                )

                StockPosting_Log.objects.create(
                    TransactionID=StockPostingID,
                    BranchID=BranchID,
                    Action=Action,
                    Date=Date,
                    VoucherMasterID=StockTransferMasterID,
                    VoucherDetailID=StockTransferDetailsID,
                    VoucherType=VoucherType,
                    ProductID=ProductID,
                    BatchID=BatchID,
                    WareHouseID=WarehouseToID,
                    QtyIn=Qty,
                    Rate=Cost,
                    PriceListID=PriceListID,
                    IsActive=IsActive,
                    CreatedDate=today,
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID
                )

                update_stock(CompanyID,BranchID,ProductID)

                # stockRateInstance = None

                # stock rate for from warehouse

                # if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WarehouseFromID, PriceListID=PriceListID).exists():
                #     stockRateInstance = StockRate.objects.get(
                #         CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WarehouseFromID, PriceListID=PriceListID)

                #     StockRateID = stockRateInstance.StockRateID
                #     stockRateInstance.Qty = float(stockRateInstance.Qty) - float(Qty)
                #     stockRateInstance.save()

                #     StockTransID = get_auto_StockTransID(
                #         StockTrans, BranchID, CompanyID)
                #     StockTrans.objects.create(
                #         StockTransID=StockTransID,
                #         BranchID=BranchID,
                #         VoucherType=VoucherType,
                #         StockRateID=StockRateID,
                #         DetailID=StockTransferDetailsID,
                #         MasterID=StockTransferMasterID,
                #         Qty=Qty,
                #         IsActive=IsActive,
                #         CompanyID=CompanyID,
                #     )
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
                #         WareHouseID=WarehouseFromID,
                #         Date=Date,
                #         PriceListID=PriceListID,
                #         CreatedUserID=CreatedUserID,
                #         CreatedDate=today,
                #         CompanyID=CompanyID,
                #     )

                #     StockTransID = get_auto_StockTransID(
                #         StockTrans, BranchID, CompanyID)
                #     StockTrans.objects.create(
                #         StockTransID=StockTransID,
                #         BranchID=BranchID,
                #         VoucherType=VoucherType,
                #         StockRateID=StockRateID,
                #         DetailID=StockTransferDetailsID,
                #         MasterID=StockTransferMasterID,
                #         Qty=Qty,
                #         IsActive=IsActive,
                #         CompanyID=CompanyID,
                #     )

                # # stock rate for To warehouse

                # if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WarehouseToID, PriceListID=PriceListID).exists():
                #     stockRateInstance = StockRate.objects.get(
                #         CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WarehouseToID, PriceListID=PriceListID)

                #     StockRateID = stockRateInstance.StockRateID
                #     stockRateInstance.Qty = float(stockRateInstance.Qty) + float(Qty)
                #     stockRateInstance.save()

                #     StockTransID = get_auto_StockTransID(
                #         StockTrans, BranchID, CompanyID)
                #     StockTrans.objects.create(
                #         StockTransID=StockTransID,
                #         BranchID=BranchID,
                #         VoucherType=VoucherType,
                #         StockRateID=StockRateID,
                #         DetailID=StockTransferDetailsID,
                #         MasterID=StockTransferMasterID,
                #         Qty=Qty,
                #         IsActive=IsActive,
                #         CompanyID=CompanyID,
                #     )
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
                #         WareHouseID=WarehouseToID,
                #         Date=Date,
                #         PriceListID=PriceListID,
                #         CreatedUserID=CreatedUserID,
                #         CreatedDate=today,
                #         CompanyID=CompanyID,
                #     )

                #     StockTransID = get_auto_StockTransID(
                #         StockTrans, BranchID, CompanyID)
                #     StockTrans.objects.create(
                #         StockTransID=StockTransID,
                #         BranchID=BranchID,
                #         VoucherType=VoucherType,
                #         StockRateID=StockRateID,
                #         DetailID=StockTransferDetailsID,
                #         MasterID=StockTransferMasterID,
                #         Qty=Qty,
                #         IsActive=IsActive,
                #         CompanyID=CompanyID,
                #     )

            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Stock Transfer',
            #              'Create', 'Stock Transfer created successfully.', 'Stock Transfer saved successfully.')

            response_data = {
                "StatusCode": 6000,
                "message": "Stock Transfer created Successfully!!!",
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

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Stock Transfer',
                         'Create', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def edit_stockTransfer(request, pk):
    try:
        with transaction.atomic():
            today = datetime.datetime.now()
            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            Date = data['Date']
            Notes = data['Notes']
            TransferredByID = data['TransferredByID']
            WarehouseFromID = data['WarehouseFromID']
            WarehouseToID = data['WarehouseToID']
            TotalQty = data['TotalQty']
            GrandTotal = data['GrandTotal']
            IsActive = data['IsActive']
            BatchID = data['BatchID']
            MaxGrandTotal = data['MaxGrandTotal']

            stockTransferMaster_instance = StockTransferMaster_ID.objects.get(
                CompanyID=CompanyID, pk=pk)

            StockTransferMasterID = stockTransferMaster_instance.StockTransferMasterID
            BranchID = stockTransferMaster_instance.BranchID
            CreatedUserID = stockTransferMaster_instance.CreatedUserID
            VoucherNo = stockTransferMaster_instance.VoucherNo
            instance_from_warehouse = stockTransferMaster_instance.WarehouseFromID
            instance_to_warehouse = stockTransferMaster_instance.WarehouseToID

            Action = "M"
            VoucherType = "ST"

            StockTransferMasterID_Log.objects.create(
                TransactionID=StockTransferMasterID,
                BranchID=BranchID,
                VoucherNo=VoucherNo,
                Date=Date,
                Notes=Notes,
                TransferredByID=TransferredByID,
                WarehouseFromID=WarehouseFromID,
                WarehouseToID=WarehouseToID,
                TotalQty=TotalQty,
                GrandTotal=GrandTotal,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                CompanyID=CompanyID,
                MaxGrandTotal=MaxGrandTotal,
            )

            # if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=StockTransferMasterID, BranchID=BranchID, VoucherType=VoucherType).exists():
            #     stockPostingInstances = StockPosting.objects.filter(
            #         CompanyID=CompanyID, VoucherMasterID=StockTransferMasterID, BranchID=BranchID, VoucherType=VoucherType)
            #     for stockPostingInstance in stockPostingInstances:
            #         stockPostingInstance.delete()

            if StockTransferDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, StockTransferMasterID=StockTransferMasterID).exists():
                stockTransferInstances = StockTransferDetails.objects.filter(
                    CompanyID=CompanyID, StockTransferMasterID=StockTransferMasterID, BranchID=BranchID)
                for i in stockTransferInstances:
                    if not StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=StockTransferMasterID,VoucherDetailID=i.StockTransferDetailsID,BranchID=BranchID, VoucherType="ST").exists():
                        StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=StockTransferMasterID,BranchID=BranchID, VoucherType="ST").delete()

                    instance_MultiFactor = PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=i.PriceListID, BranchID=BranchID).MultiFactor

                    instance_qty_sum = float(i.Qty)
                    instance_Qty = float(instance_MultiFactor) * float(instance_qty_sum)
                    if StockPosting.objects.filter(CompanyID=CompanyID,WareHouseID=instance_to_warehouse, VoucherMasterID=StockTransferMasterID,VoucherDetailID=i.StockTransferDetailsID,ProductID=i.ProductID,BranchID=BranchID, VoucherType="ST").exists():
                        stock_inst = StockPosting.objects.filter(CompanyID=CompanyID,WareHouseID=instance_to_warehouse, VoucherMasterID=StockTransferMasterID,VoucherDetailID=i.StockTransferDetailsID,ProductID=i.ProductID,BranchID=BranchID, VoucherType="ST").first()
                        stock_inst.QtyIn = float(stock_inst.QtyIn) - float(instance_Qty)
                        stock_inst.save()
                        update_stock(CompanyID,BranchID,i.ProductID)

                    if StockPosting.objects.filter(CompanyID=CompanyID,WareHouseID=WarehouseFromID, VoucherMasterID=StockTransferMasterID,VoucherDetailID=i.StockTransferDetailsID,ProductID=i.ProductID,BranchID=BranchID, VoucherType="ST").exists():
                        stock_inst = StockPosting.objects.filter(CompanyID=CompanyID,WareHouseID=WarehouseFromID, VoucherMasterID=StockTransferMasterID,VoucherDetailID=i.StockTransferDetailsID,ProductID=i.ProductID,BranchID=BranchID, VoucherType="ST").first()
                        stock_inst.QtyOut = float(stock_inst.QtyIn) - float(instance_Qty)
                        stock_inst.save()
                        update_stock(CompanyID,BranchID,i.ProductID)

            stockTransferMaster_instance.Date = Date
            stockTransferMaster_instance.Notes = Notes
            stockTransferMaster_instance.TransferredByID = TransferredByID
            stockTransferMaster_instance.WarehouseFromID = WarehouseFromID
            stockTransferMaster_instance.WarehouseToID = WarehouseToID
            stockTransferMaster_instance.TotalQty = TotalQty
            stockTransferMaster_instance.GrandTotal = GrandTotal
            stockTransferMaster_instance.MaxGrandTotal = MaxGrandTotal
            stockTransferMaster_instance.IsActive = IsActive
            stockTransferMaster_instance.Action = Action
            stockTransferMaster_instance.save()

            deleted_datas = data["deleted_data"]
            if deleted_datas:
                for deleted_Data in deleted_datas:
                    deleted_pk = deleted_Data['unq_id']
                    StockTransferDetailsID_Deleted = deleted_Data['StockTransferDetailsID']
                    ProductID_Deleted = deleted_Data['ProductID']
                    PriceListID_Deleted = deleted_Data['PriceListID']
                    Rate_Deleted = deleted_Data['Rate']
                    StockTransferMasterID_Deleted = deleted_Data['StockTransferMasterID']
                    WarehouseFromID_Deleted = deleted_Data['WarehouseFromID']
                    WarehouseToID_Deleted = deleted_Data['WarehouseToID']

                    if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID_Deleted, DefaultUnit=True).exists():
                        priceList = PriceList.objects.get(
                            CompanyID=CompanyID, ProductID=ProductID_Deleted, DefaultUnit=True)
                        MultiFactor = priceList.MultiFactor
                        Cost = float(Rate_Deleted) / float(MultiFactor)
                        Ct = round(Cost, 4)
                        Cost_Deleted = str(Ct)

                        if not deleted_pk == '' or not deleted_pk == 0:
                            if StockTransferDetails.objects.filter(CompanyID=CompanyID, pk=deleted_pk).exists():
                                deleted_detail = StockTransferDetails.objects.filter(
                                    CompanyID=CompanyID, pk=deleted_pk)
                                deleted_detail.delete()

                                if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=StockTransferMasterID_Deleted,VoucherDetailID=StockTransferDetailsID_Deleted,ProductID=ProductID_Deleted,BranchID=BranchID, VoucherType="ST").exists():
                                    stock_instances_delete = StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=StockTransferMasterID_Deleted,VoucherDetailID=StockTransferDetailsID_Deleted,ProductID=ProductID_Deleted,BranchID=BranchID, VoucherType="ST")
                                    stock_instances_delete.delete()
                                    update_stock(CompanyID,BranchID,ProductID_Deleted)

                                # if StockRate.objects.filter(CompanyID=CompanyID, ProductID=ProductID_Deleted, PriceListID=PriceListID_Deleted, Cost=Cost_Deleted, WareHouseID=WarehouseFromID_Deleted).exists():
                                #     stockRate_instance = StockRate.objects.get(
                                #         CompanyID=CompanyID, ProductID=ProductID_Deleted, PriceListID=PriceListID_Deleted, Cost=Cost_Deleted, WareHouseID=WarehouseFromID_Deleted)
                                #     StockRateID = stockRate_instance.StockRateID
                                #     if StockTrans.objects.filter(CompanyID=CompanyID, DetailID=StockTransferDetailsID_Deleted, MasterID=StockTransferMasterID_Deleted, BranchID=BranchID,
                                #                                  VoucherType=VoucherType, IsActive=True, StockRateID=StockRateID).exists():
                                #         stockTrans_instance = StockTrans.objects.get(CompanyID=CompanyID, DetailID=StockTransferDetailsID_Deleted, MasterID=StockTransferMasterID_Deleted, BranchID=BranchID,
                                #                                                      VoucherType=VoucherType, IsActive=True, StockRateID=StockRateID)
                                #         qty_in_stockTrans = stockTrans_instance.Qty
                                #         stockRate_instance.Qty = float(
                                #             stockRate_instance.Qty) + float(qty_in_stockTrans)
                                #         stockRate_instance.save()
                                #         stockTrans_instance.IsActive = False
                                #         stockTrans_instance.save()

                                # if StockRate.objects.filter(CompanyID=CompanyID, ProductID=ProductID_Deleted, PriceListID=PriceListID_Deleted, Cost=Cost_Deleted, WareHouseID=WarehouseToID_Deleted).exists():
                                #     stockRate_instance = StockRate.objects.get(
                                #         CompanyID=CompanyID, ProductID=ProductID_Deleted, PriceListID=PriceListID_Deleted, Cost=Cost_Deleted, WareHouseID=WarehouseToID_Deleted)
                                #     StockRateID = stockRate_instance.StockRateID
                                #     if StockTrans.objects.filter(CompanyID=CompanyID, DetailID=StockTransferDetailsID_Deleted, MasterID=StockTransferMasterID_Deleted, BranchID=BranchID,
                                #                                  VoucherType=VoucherType, IsActive=True, StockRateID=StockRateID).exists():
                                #         stockTrans_instance = StockTrans.objects.get(CompanyID=CompanyID, DetailID=StockTransferDetailsID_Deleted, MasterID=StockTransferMasterID_Deleted, BranchID=BranchID,
                                #                                                      VoucherType=VoucherType, IsActive=True, StockRateID=StockRateID)
                                #         qty_in_stockTrans = stockTrans_instance.Qty
                                #         stockRate_instance.Qty = float(
                                #             stockRate_instance.Qty) - float(qty_in_stockTrans)
                                #         stockRate_instance.save()
                                #         stockTrans_instance.IsActive = False
                                #         stockTrans_instance.save()

            stockTransferDetails = data["StockTransferDetails"]
            for stockTransferDetail in stockTransferDetails:
                pk = stockTransferDetail['unq_id']
                detailID = stockTransferDetail["detailID"]
                ProductID = stockTransferDetail['ProductID']
                Qty_detail = stockTransferDetail['Qty']
                PriceListID = stockTransferDetail['PriceListID']
                Rate = stockTransferDetail['Rate']
                MaxRate = stockTransferDetail['MaxRate']
                Amount = stockTransferDetail['Amount']
                MaxAmount = stockTransferDetail['MaxAmount']

                # priceList = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,DefaultUnit=True)

                # PriceListID_DefUnit = priceList.PriceListID
                # MultiFactor = priceList.MultiFactor

                MultiFactor = PriceList.objects.get(
                    CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).MultiFactor
                PriceListID_DefUnit = PriceList.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True, BranchID=BranchID).PriceListID

                # PurchasePrice = priceList.PurchasePrice
                # SalesPrice = priceList.SalesPrice

                # qty = float(FreeQty) + float(Qty)

                Qty = float(MultiFactor) * float(Qty_detail)
                Cost = float(Rate) / float(MultiFactor)

                # Qy = round(Qty, 4)
                # Qty = str(Qy)

                # Ct = round(Cost, 4)
                # Cost = str(Ct)

                # if StockTrans.objects.filter(DetailID=StockTransferDetailsID,MasterID=StockTransferMasterID,BranchID=BranchID,VoucherType=VoucherType,IsActive=True).exists():
                #     stockTrans_instance = StockTrans.objects.filter(DetailID=StockTransferDetailsID,MasterID=StockTransferMasterID,BranchID=BranchID,VoucherType=VoucherType,IsActive=True).first()
                #     qty_in_stockTrans = stockTrans_instance.Qty
                #     StockRateID = stockTrans_instance.StockRateID
                #     stockTrans_instance.IsActive = False
                #     stockTrans_instance.save()

                #     if StockRate.objects.filter(StockRateID=StockRateID,BranchID=BranchID,WareHouseID=WarehouseFromID).exists():
                #         stockRate_instance = StockRate.objects.get(StockRateID=StockRateID,BranchID=BranchID,WareHouseID=WarehouseFromID)
                #         stockRate_instance.Qty = float(stockRate_instance.Qty) + float(qty_in_stockTrans)
                #         stockRate_instance.save()
                #     if StockRate.objects.filter(StockRateID=StockRateID,BranchID=BranchID,WareHouseID=WarehouseToID).exists():
                #         stockRate_instance = StockRate.objects.get(StockRateID=StockRateID,BranchID=BranchID,WareHouseID=WarehouseToID)
                #         stockRate_instance.Qty = float(stockRate_instance.Qty) - float(qty_in_stockTrans)
                #         stockRate_instance.save()

                princeList_instance = PriceList.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID_DefUnit, BranchID=BranchID)
                PurchasePrice = princeList_instance.PurchasePrice
                SalesPrice = princeList_instance.SalesPrice

                product_is_Service = Product.objects.get(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).is_Service

                StockTransferDetailsID = get_auto_id(
                    StockTransferDetails, BranchID, CompanyID)

                if detailID == 0:
                    stockTransferDetail_instance = StockTransferDetails.objects.get(
                        pk=pk)
                    StockTransferDetailsID = stockTransferDetail_instance.StockTransferDetailsID

                    log_instance = StockTransferDetails_Log.objects.create(
                        TransactionID=StockTransferDetailsID,
                        BranchID=BranchID,
                        StockTransferMasterID=StockTransferMasterID,
                        ProductID=ProductID,
                        Qty=Qty_detail,
                        PriceListID=PriceListID,
                        Rate=Rate,
                        Amount=Amount,
                        Action=Action,
                        CompanyID=CompanyID,
                    )

                    stockTransferDetail_instance.ProductID = ProductID
                    stockTransferDetail_instance.Qty = Qty_detail
                    stockTransferDetail_instance.PriceListID = PriceListID
                    stockTransferDetail_instance.Rate = Rate
                    stockTransferDetail_instance.MaxRate = MaxRate
                    stockTransferDetail_instance.Amount = Amount
                    stockTransferDetail_instance.MaxAmount = MaxAmount
                    stockTransferDetail_instance.Action = Action
                    stockTransferDetail_instance.LogID = log_instance.ID

                    stockTransferDetail_instance.save()
                    if product_is_Service == False:
                        if StockPosting.objects.filter(CompanyID=CompanyID,WareHouseID=WarehouseToID, VoucherMasterID=StockTransferMasterID,VoucherDetailID=StockTransferDetailsID,BranchID=BranchID, VoucherType="ST",ProductID=ProductID).exists():
                            stock_instance = StockPosting.objects.filter(CompanyID=CompanyID,WareHouseID=WarehouseToID, VoucherMasterID=StockTransferMasterID,VoucherDetailID=StockTransferDetailsID,BranchID=BranchID, VoucherType="ST",ProductID=ProductID).first()
                            stock_instance.QtyIn = Qty
                            stock_instance.Action = Action
                            stock_instance.save()
                        else:
                            StockPostingID = get_auto_stockPostid(
                                StockPosting, BranchID, CompanyID)
                            StockPosting.objects.create(
                                StockPostingID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=Date,
                                VoucherMasterID=StockTransferMasterID,
                                VoucherDetailID=StockTransferDetailsID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                BatchID=BatchID,
                                WareHouseID=WarehouseToID,
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
                                VoucherMasterID=StockTransferMasterID,
                                VoucherDetailID=StockTransferDetailsID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                BatchID=BatchID,
                                WareHouseID=WarehouseToID,
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

                        if StockPosting.objects.filter(CompanyID=CompanyID,WareHouseID=WarehouseFromID, VoucherMasterID=StockTransferMasterID,VoucherDetailID=StockTransferDetailsID,BranchID=BranchID, VoucherType="ST",ProductID=ProductID).exists():
                            stock_instance = StockPosting.objects.filter(CompanyID=CompanyID,WareHouseID=WarehouseFromID, VoucherMasterID=StockTransferMasterID,VoucherDetailID=StockTransferDetailsID,BranchID=BranchID, VoucherType="ST",ProductID=ProductID).first()
                            stock_instance.QtyOut = Qty
                            stock_instance.Action = Action
                            stock_instance.save()
                        else:
                            StockPostingID = get_auto_stockPostid(
                                StockPosting, BranchID, CompanyID)
                            StockPosting.objects.create(
                                StockPostingID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=Date,
                                VoucherMasterID=StockTransferMasterID,
                                VoucherDetailID=StockTransferDetailsID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                BatchID=BatchID,
                                WareHouseID=WarehouseFromID,
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
                                VoucherMasterID=StockTransferMasterID,
                                VoucherDetailID=StockTransferDetailsID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                BatchID=BatchID,
                                WareHouseID=WarehouseFromID,
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

                    # transfer from warehouse stock post

                    # StockPostingID = get_auto_stockPostid(
                    #     StockPosting, BranchID, CompanyID)

                    # StockPosting.objects.create(
                    #     StockPostingID=StockPostingID,
                    #     BranchID=BranchID,
                    #     Action=Action,
                    #     Date=Date,
                    #     VoucherMasterID=StockTransferMasterID,
                    #     VoucherType=VoucherType,
                    #     ProductID=ProductID,
                    #     BatchID=BatchID,
                    #     WareHouseID=WarehouseFromID,
                    #     QtyOut=Qty,
                    #     Rate=Rate,
                    #     PriceListID=PriceListID_DefUnit,
                    #     IsActive=IsActive,
                    #     CreatedDate=today,
                    #     CreatedUserID=CreatedUserID,
                    #     CompanyID=CompanyID,
                    # )

                    # StockPosting_Log.objects.create(
                    #     TransactionID=StockPostingID,
                    #     BranchID=BranchID,
                    #     Action=Action,
                    #     Date=Date,
                    #     VoucherMasterID=StockTransferMasterID,
                    #     VoucherType=VoucherType,
                    #     ProductID=ProductID,
                    #     BatchID=BatchID,
                    #     WareHouseID=WarehouseFromID,
                    #     QtyOut=Qty,
                    #     Rate=Rate,
                    #     PriceListID=PriceListID_DefUnit,
                    #     IsActive=IsActive,
                    #     CreatedDate=today,
                    #     CreatedUserID=CreatedUserID,
                    #     CompanyID=CompanyID,
                    # )

                    # transfer to warehouse stock post
                    # StockPostingID = get_auto_stockPostid(
                    #     StockPosting, BranchID, CompanyID)

                    # StockPosting.objects.create(
                    #     StockPostingID=StockPostingID,
                    #     BranchID=BranchID,
                    #     Action=Action,
                    #     Date=Date,
                    #     VoucherMasterID=StockTransferMasterID,
                    #     VoucherType=VoucherType,
                    #     ProductID=ProductID,
                    #     BatchID=BatchID,
                    #     WareHouseID=WarehouseToID,
                    #     QtyIn=Qty,
                    #     Rate=Rate,
                    #     PriceListID=PriceListID_DefUnit,
                    #     IsActive=IsActive,
                    #     CreatedDate=today,
                    #     CreatedUserID=CreatedUserID,
                    #     CompanyID=CompanyID,
                    # )

                    # StockPosting_Log.objects.create(
                    #     TransactionID=StockPostingID,
                    #     BranchID=BranchID,
                    #     Action=Action,
                    #     Date=Date,
                    #     VoucherMasterID=StockTransferMasterID,
                    #     VoucherType=VoucherType,
                    #     ProductID=ProductID,
                    #     BatchID=BatchID,
                    #     WareHouseID=WarehouseToID,
                    #     QtyIn=Qty,
                    #     Rate=Rate,
                    #     PriceListID=PriceListID_DefUnit,
                    #     IsActive=IsActive,
                    #     CreatedDate=today,
                    #     CreatedUserID=CreatedUserID,
                    #     CompanyID=CompanyID,
                    # )

                if detailID == 1:
                    Action = "A"

                    log_instance = StockTransferDetails_Log.objects.create(
                        TransactionID=StockTransferDetailsID,
                        BranchID=BranchID,
                        StockTransferMasterID=StockTransferMasterID,
                        ProductID=ProductID,
                        Qty=Qty,
                        PriceListID=PriceListID,
                        Rate=Rate,
                        MaxRate=MaxRate,
                        Amount=Amount,
                        MaxAmount=MaxAmount,
                        Action=Action,
                        CompanyID=CompanyID,
                    )
                    StockTransferDetails.objects.create(
                        StockTransferDetailsID=StockTransferDetailsID,
                        BranchID=BranchID,
                        StockTransferMasterID=StockTransferMasterID,
                        ProductID=ProductID,
                        Qty=Qty,
                        PriceListID=PriceListID,
                        Rate=Rate,
                        MaxRate=MaxRate,
                        Amount=Amount,
                        MaxAmount=MaxAmount,
                        Action=Action,
                        CompanyID=CompanyID,
                        LogID=log_instance.ID
                    )

                    StockPostingID = get_auto_stockPostid(
                        StockPosting, BranchID, CompanyID)
                    StockPosting.objects.create(
                        StockPostingID=StockPostingID,
                        BranchID=BranchID,
                        Action=Action,
                        Date=Date,
                        VoucherMasterID=StockTransferMasterID,
                        VoucherDetailID=StockTransferDetailsID,
                        VoucherType=VoucherType,
                        ProductID=ProductID,
                        BatchID=BatchID,
                        WareHouseID=WarehouseToID,
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
                        VoucherMasterID=StockTransferMasterID,
                        VoucherDetailID=StockTransferDetailsID,
                        VoucherType=VoucherType,
                        ProductID=ProductID,
                        BatchID=BatchID,
                        WareHouseID=WarehouseToID,
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

                    StockPostingID = get_auto_stockPostid(
                        StockPosting, BranchID, CompanyID)
                    StockPosting.objects.create(
                        StockPostingID=StockPostingID,
                        BranchID=BranchID,
                        Action=Action,
                        Date=Date,
                        VoucherMasterID=StockTransferMasterID,
                        VoucherDetailID=StockTransferDetailsID,
                        VoucherType=VoucherType,
                        ProductID=ProductID,
                        BatchID=BatchID,
                        WareHouseID=WarehouseFromID,
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
                        VoucherMasterID=StockTransferMasterID,
                        VoucherDetailID=StockTransferDetailsID,
                        VoucherType=VoucherType,
                        ProductID=ProductID,
                        BatchID=BatchID,
                        WareHouseID=WarehouseFromID,
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

                # transfer from warehouse stock post

                # StockPostingID = get_auto_stockPostid(
                #     StockPosting, BranchID, CompanyID)

                # StockPosting.objects.create(
                #     StockPostingID=StockPostingID,
                #     BranchID=BranchID,
                #     Action=Action,
                #     Date=Date,
                #     VoucherMasterID=StockTransferMasterID,
                #     VoucherType=VoucherType,
                #     ProductID=ProductID,
                #     BatchID=BatchID,
                #     WareHouseID=WarehouseFromID,
                #     QtyOut=Qty,
                #     Rate=Rate,
                #     PriceListID=PriceListID_DefUnit,
                #     IsActive=IsActive,
                #     CreatedDate=today,
                #     CreatedUserID=CreatedUserID,
                #     CompanyID=CompanyID,
                # )

                # StockPosting_Log.objects.create(
                #     TransactionID=StockPostingID,
                #     BranchID=BranchID,
                #     Action=Action,
                #     Date=Date,
                #     VoucherMasterID=StockTransferMasterID,
                #     VoucherType=VoucherType,
                #     ProductID=ProductID,
                #     BatchID=BatchID,
                #     WareHouseID=WarehouseFromID,
                #     QtyOut=Qty,
                #     Rate=Rate,
                #     PriceListID=PriceListID_DefUnit,
                #     IsActive=IsActive,
                #     CreatedDate=today,
                #     CreatedUserID=CreatedUserID,
                #     CompanyID=CompanyID,
                # )

                # # transfer to warehouse stock post
                # StockPostingID = get_auto_stockPostid(
                #     StockPosting, BranchID, CompanyID)

                # StockPosting.objects.create(
                #     StockPostingID=StockPostingID,
                #     BranchID=BranchID,
                #     Action=Action,
                #     Date=Date,
                #     VoucherMasterID=StockTransferMasterID,
                #     VoucherType=VoucherType,
                #     ProductID=ProductID,
                #     BatchID=BatchID,
                #     WareHouseID=WarehouseToID,
                #     QtyIn=Qty,
                #     Rate=Rate,
                #     PriceListID=PriceListID_DefUnit,
                #     IsActive=IsActive,
                #     CreatedDate=today,
                #     CreatedUserID=CreatedUserID,
                #     CompanyID=CompanyID,
                # )

                # StockPosting_Log.objects.create(
                #     TransactionID=StockPostingID,
                #     BranchID=BranchID,
                #     Action=Action,
                #     Date=Date,
                #     VoucherMasterID=StockTransferMasterID,
                #     VoucherType=VoucherType,
                #     ProductID=ProductID,
                #     BatchID=BatchID,
                #     WareHouseID=WarehouseToID,
                #     QtyIn=Qty,
                #     Rate=Rate,
                #     PriceListID=PriceListID_DefUnit,
                #     IsActive=IsActive,
                #     CreatedDate=today,
                #     CreatedUserID=CreatedUserID,
                #     CompanyID=CompanyID,
                # )

                # if detailID == 1:
                #     # stock rate updation for from warehouse
                #     if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WarehouseFromID, PriceListID=PriceListID).exists():
                #         stockRateInstance = StockRate.objects.get(
                #             CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WarehouseFromID, PriceListID=PriceListID)

                #         StockRateID = stockRateInstance.StockRateID
                #         stockRateInstance.Qty = float(
                #             stockRateInstance.Qty) - float(Qty)
                #         stockRateInstance.save()

                #         StockTransID = get_auto_StockTransID(
                #             StockTrans, BranchID, CompanyID)
                #         StockTrans.objects.create(
                #             StockTransID=StockTransID,
                #             BranchID=BranchID,
                #             VoucherType=VoucherType,
                #             StockRateID=StockRateID,
                #             DetailID=StockTransferDetailsID,
                #             MasterID=StockTransferMasterID,
                #             Qty=Qty,
                #             IsActive=IsActive,
                #             CompanyID=CompanyID,
                #         )
                #     else:
                #         StockRateID = get_auto_StockRateID(
                #             StockRate, BranchID, CompanyID)
                #         StockRate.objects.create(
                #             StockRateID=StockRateID,
                #             BranchID=BranchID,
                #             BatchID=BatchID,
                #             PurchasePrice=PurchasePrice,
                #             SalesPrice=SalesPrice,
                #             Qty=Qty,
                #             Cost=Cost,
                #             ProductID=ProductID,
                #             WareHouseID=WarehouseFromID,
                #             Date=Date,
                #             PriceListID=PriceListID_DefUnit,
                #             CreatedUserID=CreatedUserID,
                #             CreatedDate=today,
                #             CompanyID=CompanyID,
                #         )

                #         StockTransID = get_auto_StockTransID(
                #             StockTrans, BranchID, CompanyID)
                #         StockTrans.objects.create(
                #             StockTransID=StockTransID,
                #             BranchID=BranchID,
                #             VoucherType=VoucherType,
                #             StockRateID=StockRateID,
                #             DetailID=StockTransferDetailsID,
                #             MasterID=StockTransferMasterID,
                #             Qty=Qty,
                #             IsActive=IsActive,
                #             CompanyID=CompanyID,
                #         )
                #     # stock rate updation for to warehouse
                #     if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WarehouseToID, PriceListID=PriceListID).exists():
                #         stockRateInstance = StockRate.objects.get(
                #             CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WarehouseToID, PriceListID=PriceListID)

                #         StockRateID = stockRateInstance.StockRateID
                #         stockRateInstance.Qty = float(
                #             stockRateInstance.Qty) + float(Qty)
                #         stockRateInstance.save()

                #         StockTransID = get_auto_StockTransID(
                #             StockTrans, BranchID, CompanyID)
                #         StockTrans.objects.create(
                #             StockTransID=StockTransID,
                #             BranchID=BranchID,
                #             VoucherType=VoucherType,
                #             StockRateID=StockRateID,
                #             DetailID=StockTransferDetailsID,
                #             MasterID=StockTransferMasterID,
                #             Qty=Qty,
                #             IsActive=IsActive,
                #             CompanyID=CompanyID,
                #         )
                #     else:
                #         StockRateID = get_auto_StockRateID(
                #             StockRate, BranchID, CompanyID)
                #         StockRate.objects.create(
                #             StockRateID=StockRateID,
                #             BranchID=BranchID,
                #             BatchID=BatchID,
                #             PurchasePrice=PurchasePrice,
                #             SalesPrice=SalesPrice,
                #             Qty=Qty,
                #             Cost=Cost,
                #             ProductID=ProductID,
                #             WareHouseID=WarehouseToID,
                #             Date=Date,
                #             PriceListID=PriceListID_DefUnit,
                #             CreatedUserID=CreatedUserID,
                #             CreatedDate=today,
                #             CompanyID=CompanyID,
                #         )

                #         StockTransID = get_auto_StockTransID(
                #             StockTrans, BranchID, CompanyID)
                #         StockTrans.objects.create(
                #             StockTransID=StockTransID,
                #             BranchID=BranchID,
                #             VoucherType=VoucherType,
                #             StockRateID=StockRateID,
                #             DetailID=StockTransferDetailsID,
                #             MasterID=StockTransferMasterID,
                #             Qty=Qty,
                #             IsActive=IsActive,
                #             CompanyID=CompanyID,
                #         )
                # else:
                #     stockTrans_instances = StockTrans.objects.filter(
                #         CompanyID=CompanyID, DetailID=StockTransferDetailsID, BranchID=BranchID, VoucherType=VoucherType, IsActive=True)
                #     for stockTrans_instance in stockTrans_instances:

                #         stockRateID = stockTrans_instance.StockRateID
                #         # stock rate updation for from warehose
                #         if StockRate.objects.filter(CompanyID=CompanyID, StockRateID=stockRateID, BranchID=BranchID, WareHouseID=WarehouseFromID).exists():
                #             stockRate_instances = StockRate.objects.filter(
                #                 CompanyID=CompanyID, StockRateID=stockRateID, BranchID=BranchID, WareHouseID=WarehouseFromID)
                #             for stockRate_instance in stockRate_instances:
                #                 if float(stockTrans_instance.Qty) < float(Qty):
                #                     deff = float(Qty) - float(stockTrans_instance.Qty)
                #                     stockTrans_instance.Qty = float(
                #                         stockTrans_instance.Qty) + float(deff)
                #                     stockTrans_instance.save()

                #                     stockRate_instance.Qty = float(
                #                         stockRate_instance.Qty) - float(deff)
                #                     stockRate_instance.save()

                #                 elif float(stockTrans_instance.Qty) > float(Qty):
                #                     deff = float(stockTrans_instance.Qty) - float(Qty)
                #                     stockTrans_instance.Qty = float(
                #                         stockTrans_instance.Qty) - float(deff)
                #                     stockTrans_instance.save()

                #                     stockRate_instance.Qty = float(
                #                         stockRate_instance.Qty) + float(deff)
                #                     stockRate_instance.save()

                #         # stock rate updation for to warehose
                #         if StockRate.objects.filter(CompanyID=CompanyID, StockRateID=stockRateID, BranchID=BranchID, WareHouseID=WarehouseToID).exists():
                #             stockRate_instances = StockRate.objects.filter(
                #                 CompanyID=CompanyID, StockRateID=stockRateID, BranchID=BranchID, WareHouseID=WarehouseToID)

                #             for stockRate_instance in stockRate_instances:
                #                 if float(stockTrans_instance.Qty) < float(Qty):
                #                     deff = float(Qty) - float(stockTrans_instance.Qty)
                #                     stockTrans_instance.Qty = float(
                #                         stockTrans_instance.Qty) + float(deff)
                #                     stockTrans_instance.save()

                #                     stockRate_instance.Qty = float(
                #                         stockRate_instance.Qty) + float(deff)
                #                     stockRate_instance.save()

                #                 elif float(stockTrans_instance.Qty) > float(Qty):
                #                     deff = float(stockTrans_instance.Qty) - float(Qty)
                #                     stockTrans_instance.Qty = float(
                #                         stockTrans_instance.Qty) - float(deff)
                #                     stockTrans_instance.save()

                #                     stockRate_instance.Qty = float(
                #                         stockRate_instance.Qty) - float(deff)
                #                     stockRate_instance.save()

            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Stock Transfer',
            #              'Edit', 'Stock Transfer Updated successfully.', 'Stock Transfer Updated successfully.')

            response_data = {
                "StatusCode": 6000,
                "message": "Stock Transfer Updated Successfully!!!",
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

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Stock Transfer',
                         'Edit', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def list_stockTransferMasterID(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if StockTransferMaster_ID.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instances = StockTransferMaster_ID.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
            serialized = StockTransferMaster_IDRestSerializer(instances, many=True, context={"CompanyID": CompanyID,
                                                                                             "PriceRounding": PriceRounding})

            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Stock Transfer', 'List',
            #              'Stock Transfer List Viewed successfully.', 'Stock Transfer List Viewed successfully')

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Stock Transfer not found in this branch."
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
def stock_transfer_pagination(request):
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
            stock_transfer_object = StockTransferMaster_ID.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)

            stock_transfer_sort_pagination = list_pagination(
                stock_transfer_object,
                items_per_page,
                page_number
            )
            stock_transfer_serializer = StockTransferMaster1_IDRestSerializer(
                stock_transfer_sort_pagination,
                many=True,
                context={"request": request, "CompanyID": CompanyID,
                         "PriceRounding": PriceRounding}
            )
            data = stock_transfer_serializer.data
            if not data == None:
                response_data = {
                    "StatusCode": 6000,
                    "data": data,
                    "count": len(stock_transfer_object)
                }
            else:
                response_data = {
                    "StatusCode": 6001
                }

            return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def stockTransferMasterID(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    if StockTransferMaster_ID.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = StockTransferMaster_ID.objects.get(
            CompanyID=CompanyID, pk=pk)

        serialized = StockTransferMaster_IDRestSerializer(instance, context={"CompanyID": CompanyID,
                                                                             "PriceRounding": PriceRounding})

        #request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Stock Transfer', 'View',
        #              'Stock Transfer Single Viewed successfully.', 'Stock Transfer Single Viewed successfully.')
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Stock Transfer Master ID Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_stockTransferDetails(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    if StockTransferDetails.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = StockTransferDetails.objects.get(CompanyID=CompanyID, pk=pk)
    if instance:
        StockTransferDetailsID = instance.StockTransferDetailsID
        BranchID = instance.BranchID
        StockTransferMasterID = instance.StockTransferMasterID
        ProductID = instance.ProductID
        Qty = instance.Qty
        PriceListID = instance.PriceListID
        Rate = instance.Rate
        Amount = instance.Amount
        Action = "D"

        instance.delete()

        StockTransferDetails_Log.objects.create(
            TransactionID=StockTransferDetailsID,
            BranchID=BranchID,
            StockTransferMasterID=StockTransferMasterID,
            ProductID=ProductID,
            Qty=Qty,
            PriceListID=PriceListID,
            Rate=Rate,
            Amount=Amount,
            Action=Action,
            CompanyID=CompanyID,
        )

        response_data = {
            "StatusCode": 6000,
            "message": "Stock Transfer Details Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Stock Transfer Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_stockTransferMasterID(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    instance = None
    if StockTransferMaster_ID.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = StockTransferMaster_ID.objects.get(
            CompanyID=CompanyID, pk=pk)

        StockTransferMasterID = instance.StockTransferMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        Date = instance.Date
        Notes = instance.Notes
        TransferredByID = instance.TransferredByID
        WarehouseFromID = instance.WarehouseFromID
        WarehouseToID = instance.WarehouseToID
        TotalQty = instance.TotalQty
        GrandTotal = instance.GrandTotal
        MaxGrandTotal = instance.MaxGrandTotal
        IsActive = instance.IsActive
        CreatedUserID = instance.CreatedUserID
        Action = "D"

        if StockPosting.objects.filter(CompanyID=CompanyID,BranchID=BranchID,VoucherType="ST",VoucherMasterID=StockTransferMasterID).exists():
            StockPosting.objects.filter(CompanyID=CompanyID,BranchID=BranchID,VoucherType="ST",VoucherMasterID=StockTransferMasterID).delete()
            update_stock(CompanyID,BranchID,ProductID)

        detail_instances = StockTransferDetails.objects.filter(
            CompanyID=CompanyID, StockTransferMasterID=StockTransferMasterID, BranchID=BranchID)

        for detail_instance in detail_instances:

            StockTransferDetailsID = detail_instance.StockTransferDetailsID
            BranchID = detail_instance.BranchID
            StockTransferMasterID = detail_instance.StockTransferMasterID
            ProductID = detail_instance.ProductID
            Qty = detail_instance.Qty
            PriceListID = detail_instance.PriceListID
            Rate = detail_instance.Rate
            MaxRate = detail_instance.MaxRate
            Amount = detail_instance.Amount
            MaxAmount = detail_instance.MaxAmount

            detail_instance.delete()

            StockTransferDetails_Log.objects.create(
                TransactionID=StockTransferDetailsID,
                BranchID=BranchID,
                StockTransferMasterID=StockTransferMasterID,
                ProductID=ProductID,
                Qty=Qty,
                PriceListID=PriceListID,
                Rate=Rate,
                MaxRate=MaxRate,
                Amount=Amount,
                MaxAmount=MaxAmount,
                Action=Action,
                CompanyID=CompanyID,
            )

        instance.delete()

        StockTransferMasterID_Log.objects.create(
            TransactionID=StockTransferMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            Date=Date,
            Notes=Notes,
            TransferredByID=TransferredByID,
            WarehouseFromID=WarehouseFromID,
            WarehouseToID=WarehouseToID,
            TotalQty=TotalQty,
            GrandTotal=GrandTotal,
            MaxGrandTotal=MaxGrandTotal,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            CompanyID=CompanyID,
        )

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Stock Transfer',
                     'Delete', 'Stock Transfer Deleted successfully.', 'Stock Transfer Deleted successfully.')
        response_data = {
            "StatusCode": 6000,
            "title": "Success",
            "message": "Stock Transfer Deleted Successfully!"
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Stock Transfer',
                     'Delete', 'Stock Transfer Deleted Failed.', 'Stock Transfer Not Found')
        response_data = {
            "StatusCode": 6001,
            "title": "Failed",
            "message": "Stock Transfer Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def report_stockTransfer_register(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    PriceRounding = data['PriceRounding']
    FromDate = data['FromDate']
    ToDate = data['ToDate']
    UserID = data['UserID']
    WareHouseFrom = data['WareHouseFrom']
    WareHouseTo = data['WareHouseTo']

    if StockTransferMaster_ID.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
        instance = StockTransferMaster_ID.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)

        if not UserID == "0":
            UserID = UserTable.objects.get(pk=UserID).customer.user.id
            if instance.filter(CreatedUserID=UserID).exists():
                instance = instance.filter(
                    CreatedUserID=UserID)

        if WareHouseFrom == 0 and WareHouseTo == 0:
            report_instance = instance
        elif WareHouseFrom == 0 and WareHouseTo > 0:
            report_instance = instance.filter(WarehouseToID=WareHouseTo)
        elif WareHouseFrom > 0 and WareHouseTo == 0:
            report_instance = instance.filter(WarehouseFromID=WareHouseFrom)
        else:
            report_instance = instance.filter(
                WarehouseFromID=WareHouseFrom, WarehouseToID=WareHouseTo)

        serialized = StockTransferRegisterReportSerializer(report_instance, many=True, context={"CompanyID": CompanyID,
                                                                                                "PriceRounding": PriceRounding, })
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Datas Not Found During this time!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
