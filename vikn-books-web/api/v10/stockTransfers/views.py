import datetime
import os
import re
import sys

from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, renderer_classes,authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from sqlalchemy import false

from api.v10.brands.serializers import ListSerializer
from api.v10.products.functions import update_stock
from api.v10.purchases.functions import get_auto_StockRateID, get_auto_StockTransID
from api.v10.reportQuerys.functions import stock_transfer_report_data
from api.v10.sales.functions import get_auto_stockPostid, get_auto_VoucherNo
from api.v10.stockTransfers.functions import (
    generate_serializer_errors,
    get_auto_id,
    get_auto_idMaster,
)
from api.v10.stockTransfers.serializers import (
    StockTransferDetailsRestSerializer,
    StockTransferDetailsSerializer,
    StockTransferMaster1_IDRestSerializer,
    StockTransferMaster_IDRestSerializer,
    StockTransferMaster_IDSerializer,
    StockTransferRegisterReportSerializer,
)
from brands.models import (
    Activity_Log,
    PriceList,
    Product,
    StockPosting,
    StockPosting_Log,
    StockRate,
    StockTrans,
    StockTransferDetails,
    StockTransferDetails_Log,
    StockTransferDetailsDummy,
    StockTransferMaster_ID,
    StockTransferMasterID_Log,
    UserTable,
    VoucherNoTable,
)
from main.functions import (
    activity_log,
    converted_float,
    get_GeneralSettings,
    get_company,
    get_ModelInstance,
    list_pagination,
    update_voucher_table,
)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def create_stockTransfer(request):
    try:
        with transaction.atomic():
            today = datetime.datetime.now()
            data = request.data
            CompanyID = data["CompanyID"]
            CompanyID = get_company(CompanyID)
            BranchID = data["BranchID"]
            CreatedUserID = data["CreatedUserID"]
            Date = data["Date"]
            VoucherNo = data["VoucherNo"]
            Notes = data["Notes"]
            TransferredByID = data["TransferredByID"]
            WarehouseFromID = data["WarehouseFromID"]
            WarehouseToID = data["WarehouseToID"]
            TotalQty = data["TotalQty"]
            GrandTotal = data["GrandTotal"]
            IsActive = data["IsActive"]
            BatchID = data["BatchID"]
            MaxGrandTotal = data["MaxGrandTotal"]

            Action = "A"
            VoucherType = "ST"
            # VoucherNo Updated
            try:
                PreFix = data["PreFix"]
            except:
                PreFix = "ST"

            try:
                Seperator = data["Seperator"]
            except:
                Seperator = ""

            try:
                InvoiceNo = data["InvoiceNo"]
            except:
                InvoiceNo = 1

            try:
                BranchFromID = data["BranchFromID"]
            except:
                BranchFromID = 1

            try:
                BranchToID = data["BranchToID"]
            except:
                BranchToID = 1
                
            try:
                StockOrderNo = data["StockOrderNo"]
            except:
                StockOrderNo = ""
            
            is_transferOK = True
            if StockTransferMaster_ID.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherNo=VoucherNo).exists():
                check_VoucherNoAutoGenerate = get_GeneralSettings(
                    CompanyID, BranchID, "VoucherNoAutoGenerate")
                if check_VoucherNoAutoGenerate == False:
                    is_transferOK = False
            
            if is_transferOK:
            
                if StockTransferMaster_ID.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherNo=StockOrderNo).exists():
                    stock_order = StockTransferMaster_ID.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, VoucherNo=StockOrderNo).first()
                    stock_order.IsTaken = True
                    stock_order.save()

                update_voucher_table(
                    CompanyID, CreatedUserID, VoucherType, PreFix, Seperator, InvoiceNo
                )
                StockTransferMasterID = get_auto_idMaster(
                    StockTransferMaster_ID, BranchID, CompanyID
                )
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
                    MaxGrandTotal=MaxGrandTotal,
                    BranchFromID=BranchFromID,
                    BranchToID=BranchToID,
                    VoucherType=VoucherType,
                    StockOrderNo=StockOrderNo,
                )

                stock_transfer_create = StockTransferMaster_ID.objects.create(
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
                    MaxGrandTotal=MaxGrandTotal,
                    BranchFromID=BranchFromID,
                    BranchToID=BranchToID,
                    VoucherType=VoucherType,
                    StockOrderNo=StockOrderNo,
                )

                stockTransferDetails = data["StockTransferDetails"]
                for i in stockTransferDetails:
                    ProductID = i["ProductID"]
                    Qty = i["Qty"]
                    PriceListID = i["PriceListID"]
                    Rate = i["Rate"]
                    MaxRate = i["MaXRate"]
                    Amount = i["Amount"]
                    MaxAmount = i["MaxAmount"]

                    StockTransferDetailsID = get_auto_id(
                        StockTransferDetails, BranchID, CompanyID
                    )

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
                        LogID=log_instance.ID,
                    )

                    # priceList = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,DefaultUnit=True,BranchID=BranchID)

                    # PriceListID = priceList.PriceListID
                    # MultiFactor = priceList.MultiFactor

                    MultiFactor = PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=PriceListID
                    ).MultiFactor
                    PriceListID = PriceList.objects.get(
                        CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True
                    ).PriceListID

                    # PurchasePrice = priceList.PurchasePrice
                    # SalesPrice = priceList.SalesPrice
                    princeList_instance = PriceList.objects.get(
                        CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID
                    )
                    PurchasePrice = princeList_instance.PurchasePrice
                    SalesPrice = princeList_instance.SalesPrice

                    Qty = converted_float(MultiFactor) * converted_float(Qty)
                    Cost = converted_float(Rate) / converted_float(MultiFactor)

                    # Qy = round(Qty, 4)
                    # Qty = str(Qy)

                    # Ct = round(Cost, 4)
                    # Cost = str(Ct)

                    princeList_instance = PriceList.objects.get(
                        CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID
                    )
                    PurchasePrice = princeList_instance.PurchasePrice
                    SalesPrice = princeList_instance.SalesPrice

                    # transfer from warehouse stock post

                    StockPostingID = get_auto_stockPostid(
                        StockPosting, BranchFromID, CompanyID
                    )

                    pricelist, warehouse = get_ModelInstance(
                        CompanyID, BranchID, PriceListID, WarehouseFromID
                    )

                    StockPosting.objects.create(
                        StockPostingID=StockPostingID,
                        BranchID=BranchFromID,
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
                        CompanyID=CompanyID,
                        pricelist=pricelist,
                        warehouse=warehouse,
                    )

                    StockPosting_Log.objects.create(
                        TransactionID=StockPostingID,
                        BranchID=BranchFromID,
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
                        CompanyID=CompanyID,
                    )

                    update_stock(CompanyID, BranchFromID, ProductID)

                    # transfer to warehouse stock post
                    StockPostingID = get_auto_stockPostid(
                        StockPosting, BranchToID, CompanyID
                    )

                    pricelist, warehouse = get_ModelInstance(
                        CompanyID, BranchID, PriceListID, WarehouseToID
                    )

                    StockPosting.objects.create(
                        StockPostingID=StockPostingID,
                        BranchID=BranchToID,
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
                        CompanyID=CompanyID,
                        pricelist=pricelist,
                        warehouse=warehouse,
                    )

                    StockPosting_Log.objects.create(
                        TransactionID=StockPostingID,
                        BranchID=BranchToID,
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
                        CompanyID=CompanyID,
                    )

                    update_stock(CompanyID, BranchToID, ProductID)

                response_data = {
                    "id": stock_transfer_create.id,
                    "StatusCode": 6000,
                    "message": "Stock Transfer created Successfully!!!",
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "VoucherNo already exist",
                }

                return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again",
        }

        activity_id = activity_log(
            request._request,
            CompanyID,
            "Error",
            CreatedUserID,
            "Stock Transfer",
            "Create",
            str(e),
            err_descrb,
        )
        body_params = str(request.data)
        Activity_Log.objects.filter(id=activity_id).update(body_params=body_params)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def edit_stockTransfer(request, pk):
    try:
        with transaction.atomic():
            today = datetime.datetime.now()
            data = request.data
            CompanyID = data["CompanyID"]
            CompanyID = get_company(CompanyID)
            Date = data["Date"]
            Notes = data["Notes"]
            TransferredByID = data["TransferredByID"]
            WarehouseFromID = data["WarehouseFromID"]
            WarehouseToID = data["WarehouseToID"]
            TotalQty = data["TotalQty"]
            GrandTotal = data["GrandTotal"]
            IsActive = data["IsActive"]
            BatchID = data["BatchID"]
            MaxGrandTotal = data["MaxGrandTotal"]

            try:
                BranchFromID = data["BranchFromID"]
            except:
                BranchFromID = 1

            try:
                BranchToID = data["BranchToID"]
            except:
                BranchToID = 1

            stockTransferMaster_instance = StockTransferMaster_ID.objects.get(
                CompanyID=CompanyID, pk=pk
            )

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
                BranchFromID=BranchFromID,
                BranchToID=BranchToID,
                VoucherType=VoucherType,
            )

            # if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=StockTransferMasterID, BranchID=BranchID, VoucherType=VoucherType).exists():
            #     stockPostingInstances = StockPosting.objects.filter(
            #         CompanyID=CompanyID, VoucherMasterID=StockTransferMasterID, BranchID=BranchID, VoucherType=VoucherType)
            #     for stockPostingInstance in stockPostingInstances:
            #         stockPostingInstance.delete()

            # if StockTransferDetails.objects.filter(
            #     CompanyID=CompanyID,BranchID=BranchID, StockTransferMasterID=StockTransferMasterID
            # ).exists():
            #     stockTransferInstances = StockTransferDetails.objects.filter(
            #         CompanyID=CompanyID, BranchID=BranchID, StockTransferMasterID=StockTransferMasterID
            #     )
            #     for i in stockTransferInstances:
            #         if not StockPosting.objects.filter(
            #             CompanyID=CompanyID,
            #             VoucherMasterID=StockTransferMasterID,
            #             VoucherDetailID=i.StockTransferDetailsID,
            #             VoucherType="ST",
            #         ).exists():
            #             StockPosting.objects.filter(
            #                 CompanyID=CompanyID,
            #                 VoucherMasterID=StockTransferMasterID,
            #                 VoucherDetailID=i.StockTransferDetailsID,
            #                 VoucherType="ST",
            #             ).delete()

            #         instance_MultiFactor = PriceList.objects.get(
            #             CompanyID=CompanyID, PriceListID=i.PriceListID
            #         ).MultiFactor

            #         instance_qty_sum = converted_float(i.Qty)
            #         instance_Qty = converted_float(
            #             instance_MultiFactor
            #         ) * converted_float(instance_qty_sum)
            #         if StockPosting.objects.filter(
            #             CompanyID=CompanyID,
            #             WareHouseID=instance_to_warehouse,
            #             VoucherMasterID=StockTransferMasterID,
            #             VoucherDetailID=i.StockTransferDetailsID,
            #             ProductID=i.ProductID,
            #             VoucherType="ST",
            #         ).exists():
            #             stock_inst = StockPosting.objects.filter(
            #                 CompanyID=CompanyID,
            #                 WareHouseID=instance_to_warehouse,
            #                 VoucherMasterID=StockTransferMasterID,
            #                 VoucherDetailID=i.StockTransferDetailsID,
            #                 ProductID=i.ProductID,
            #                 VoucherType="ST",
            #             ).first()
            #             stock_inst.QtyIn = converted_float(
            #                 stock_inst.QtyIn
            #             ) - converted_float(instance_Qty)
            #             stock_inst.save()
            #             update_stock(CompanyID, BranchID, i.ProductID)

            #         if StockPosting.objects.filter(
            #             CompanyID=CompanyID,
            #             WareHouseID=instance_from_warehouse,
            #             VoucherMasterID=StockTransferMasterID,
            #             VoucherDetailID=i.StockTransferDetailsID,
            #             ProductID=i.ProductID,
            #             VoucherType="ST",
            #         ).exists():
            #             stock_inst = StockPosting.objects.filter(
            #                 CompanyID=CompanyID,
            #                 WareHouseID=instance_from_warehouse,
            #                 VoucherMasterID=StockTransferMasterID,
            #                 VoucherDetailID=i.StockTransferDetailsID,
            #                 ProductID=i.ProductID,
            #                 VoucherType="ST",
            #             ).first()
            #             stock_inst.QtyOut = converted_float(
            #                 stock_inst.QtyOut
            #             ) - converted_float(instance_Qty)
            #             stock_inst.save()
            #             update_stock(CompanyID, BranchID, i.ProductID)

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
            stockTransferMaster_instance.BranchFromID = BranchFromID
            stockTransferMaster_instance.BranchToID = BranchToID
            stockTransferMaster_instance.save()

            deleted_datas = data["deleted_data"]
            if deleted_datas:
                for deleted_Data in deleted_datas:
                    deleted_pk = deleted_Data["unq_id"]
                    StockTransferDetailsID_Deleted = deleted_Data[
                        "StockTransferDetailsID"
                    ]
                    ProductID_Deleted = deleted_Data["ProductID"]
                    # PriceListID_Deleted = deleted_Data['PriceListID']
                    Rate_Deleted = deleted_Data["Rate"]
                    StockTransferMasterID_Deleted = deleted_Data[
                        "StockTransferMasterID"
                    ]
                    BranchFromID_deleted = deleted_Data["BranchFromID"]
                    BranchToID_deleted = deleted_Data["BranchToID"]
                    # WarehouseFromID_Deleted = deleted_Data['WarehouseFromID']
                    # WarehouseToID_Deleted = deleted_Data['WarehouseToID']

                    if PriceList.objects.filter(
                        CompanyID=CompanyID,
                        ProductID=ProductID_Deleted,
                        DefaultUnit=True,
                    ).exists():
                        priceList = PriceList.objects.get(
                            CompanyID=CompanyID,
                            ProductID=ProductID_Deleted,
                            DefaultUnit=True,
                        )
                        MultiFactor = priceList.MultiFactor
                        Cost = converted_float(Rate_Deleted) / converted_float(
                            MultiFactor
                        )
                        Ct = round(Cost, 4)
                        # Cost_Deleted = str(Ct)

                        if not deleted_pk == "" or not deleted_pk == 0:
                            if StockTransferDetails.objects.filter(
                                CompanyID=CompanyID, pk=deleted_pk
                            ).exists():
                                deleted_detail = StockTransferDetails.objects.filter(
                                    CompanyID=CompanyID, pk=deleted_pk
                                )
                                deleted_detail.delete()

                                if StockPosting.objects.filter(
                                    CompanyID=CompanyID,
                                    VoucherMasterID=StockTransferMasterID_Deleted,
                                    VoucherDetailID=StockTransferDetailsID_Deleted,
                                    ProductID=ProductID_Deleted,
                                    VoucherType="ST",
                                ).exists():
                                    stock_instances_delete = StockPosting.objects.filter(
                                        CompanyID=CompanyID,
                                        VoucherMasterID=StockTransferMasterID_Deleted,
                                        VoucherDetailID=StockTransferDetailsID_Deleted,
                                        ProductID=ProductID_Deleted,
                                        VoucherType="ST",
                                    )
                                    stock_instances_delete.delete()
                                    update_stock(
                                        CompanyID,
                                        BranchFromID_deleted,
                                        ProductID_Deleted,
                                    )
                                    update_stock(
                                        CompanyID, BranchToID_deleted, ProductID_Deleted
                                    )

                                # if StockRate.objects.filter(CompanyID=CompanyID, ProductID=ProductID_Deleted, PriceListID=PriceListID_Deleted, Cost=Cost_Deleted, WareHouseID=WarehouseFromID_Deleted).exists():
                                #     stockRate_instance = StockRate.objects.get(
                                #         CompanyID=CompanyID, ProductID=ProductID_Deleted, PriceListID=PriceListID_Deleted, Cost=Cost_Deleted, WareHouseID=WarehouseFromID_Deleted)
                                #     StockRateID = stockRate_instance.StockRateID
                                #     if StockTrans.objects.filter(CompanyID=CompanyID, DetailID=StockTransferDetailsID_Deleted, MasterID=StockTransferMasterID_Deleted, BranchID=BranchID,
                                #                                  VoucherType=VoucherType, IsActive=True, StockRateID=StockRateID).exists():
                                #         stockTrans_instance = StockTrans.objects.get(CompanyID=CompanyID, DetailID=StockTransferDetailsID_Deleted, MasterID=StockTransferMasterID_Deleted, BranchID=BranchID,
                                #                                                      VoucherType=VoucherType, IsActive=True, StockRateID=StockRateID)
                                #         qty_in_stockTrans = stockTrans_instance.Qty
                                #         stockRate_instance.Qty = converted_float(
                                #             stockRate_instance.Qty) + converted_float(qty_in_stockTrans)
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
                                #         stockRate_instance.Qty = converted_float(
                                #             stockRate_instance.Qty) - converted_float(qty_in_stockTrans)
                                #         stockRate_instance.save()
                                #         stockTrans_instance.IsActive = False
                                #         stockTrans_instance.save()

            stockTransferDetails = data["StockTransferDetails"]
            StockPosting.objects.filter(
                CompanyID=CompanyID,
                VoucherMasterID=StockTransferMasterID,
                VoucherType="ST",
            ).delete()
            for stockTransferDetail in stockTransferDetails:
                pk = stockTransferDetail["unq_id"]
                detailID = stockTransferDetail["detailID"]
                ProductID = stockTransferDetail["ProductID"]
                Qty_detail = stockTransferDetail["Qty"]
                PriceListID = stockTransferDetail["PriceListID"]
                Rate = stockTransferDetail["Rate"]
                MaxRate = stockTransferDetail["MaXRate"]
                Amount = stockTransferDetail["Amount"]
                MaxAmount = stockTransferDetail["MaxAmount"]

                

                # priceList = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,DefaultUnit=True)

                # PriceListID_DefUnit = priceList.PriceListID
                # MultiFactor = priceList.MultiFactor

                MultiFactor = PriceList.objects.get(
                    CompanyID=CompanyID, PriceListID=PriceListID
                ).MultiFactor
                PriceListID_DefUnit = PriceList.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True
                ).PriceListID

                # PurchasePrice = priceList.PurchasePrice
                # SalesPrice = priceList.SalesPrice

                # qty = converted_float(FreeQty) + converted_float(Qty)

                Qty = converted_float(MultiFactor) * converted_float(Qty_detail)
                Cost = converted_float(Rate) / converted_float(MultiFactor)

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
                #         stockRate_instance.Qty = converted_float(stockRate_instance.Qty) + converted_float(qty_in_stockTrans)
                #         stockRate_instance.save()
                #     if StockRate.objects.filter(StockRateID=StockRateID,BranchID=BranchID,WareHouseID=WarehouseToID).exists():
                #         stockRate_instance = StockRate.objects.get(StockRateID=StockRateID,BranchID=BranchID,WareHouseID=WarehouseToID)
                #         stockRate_instance.Qty = converted_float(stockRate_instance.Qty) - converted_float(qty_in_stockTrans)
                #         stockRate_instance.save()

                princeList_instance = PriceList.objects.get(
                    CompanyID=CompanyID,
                    ProductID=ProductID,
                    PriceListID=PriceListID_DefUnit,
                )
                PurchasePrice = princeList_instance.PurchasePrice
                SalesPrice = princeList_instance.SalesPrice

                product_is_Service = Product.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID
                ).is_Service

                StockTransferDetailsID = get_auto_id(
                    StockTransferDetails, BranchID, CompanyID
                )

                if detailID == 0:
                    stockTransferDetail_instance = StockTransferDetails.objects.get(
                        pk=pk
                    )
                    StockTransferDetailsID = (
                        stockTransferDetail_instance.StockTransferDetailsID
                    )

                    

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
                        pricelist, warehouse = get_ModelInstance(
                            CompanyID, BranchID, PriceListID, WarehouseToID
                        )

                        

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
                        LogID=log_instance.ID,
                    )
                    pricelist, warehouse = get_ModelInstance(
                        CompanyID, BranchToID, PriceListID, WarehouseToID
                    )

                # transfer from warehouse stock post

                StockPostingID = get_auto_stockPostid(
                    StockPosting, BranchFromID, CompanyID
                )

                pricelist, warehouse = get_ModelInstance(
                    CompanyID, BranchID, PriceListID, WarehouseFromID
                )

                StockPosting.objects.create(
                    StockPostingID=StockPostingID,
                    BranchID=BranchFromID,
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
                    CompanyID=CompanyID,
                    pricelist=pricelist,
                    warehouse=warehouse,
                )

                StockPosting_Log.objects.create(
                    TransactionID=StockPostingID,
                    BranchID=BranchFromID,
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
                    CompanyID=CompanyID,
                )

                update_stock(CompanyID, BranchFromID, ProductID)

                # transfer to warehouse stock post
                StockPostingID = get_auto_stockPostid(
                    StockPosting, BranchToID, CompanyID
                )

                pricelist, warehouse = get_ModelInstance(
                    CompanyID, BranchID, PriceListID, WarehouseToID
                )

                StockPosting.objects.create(
                    StockPostingID=StockPostingID,
                    BranchID=BranchToID,
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
                    CompanyID=CompanyID,
                    pricelist=pricelist,
                    warehouse=warehouse,
                )

                StockPosting_Log.objects.create(
                    TransactionID=StockPostingID,
                    BranchID=BranchToID,
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
                    CompanyID=CompanyID,
                )

                update_stock(CompanyID, BranchToID, ProductID)
                    
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
            "message": "some error occured..please try again",
            "err_descrb": err_descrb
        }

        activity_id = activity_log(
            request._request,
            CompanyID,
            "Error",
            CreatedUserID,
            "Stock Transfer",
            "Edit",
            str(e),
            err_descrb,
        )
        body_params = str(request.data)
        Activity_Log.objects.filter(id=activity_id).update(body_params=body_params)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def list_stockTransferMasterID(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]
    serialized1 = ListSerializer(data=request.data)
    try:
        VoucherType = data["VoucherType"]
    except:
        VoucherType = "ST"

    if serialized1.is_valid():
        BranchID = serialized1.data["BranchID"]
        if StockTransferMaster_ID.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType
        ).exists():
            instances = StockTransferMaster_ID.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType
            )
            import time

            first = time.time()
            serialized = StockTransferMaster_IDRestSerializer(
                instances,
                many=True,
                context={"CompanyID": CompanyID, "PriceRounding": PriceRounding},
            )

            # request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Stock Transfer', 'List',
            #              'Stock Transfer List Viewed successfully.', 'Stock Transfer List Viewed successfully')

            response_data = {"StatusCode": 6000, "data": serialized.data}

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Stock Transfer not found in this branch.",
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch you enterd is not valid.",
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def stock_transfer_pagination(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]

    page_number = data["page_no"]
    items_per_page = data["items_per_page"]
    try:
        VoucherType = data["VoucherType"]
    except:
        VoucherType = "ST"

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data["BranchID"]

        if page_number and items_per_page:
            stock_transfer_object = StockTransferMaster_ID.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType
            )

            stock_transfer_sort_pagination = list_pagination(
                stock_transfer_object, items_per_page, page_number
            )
            stock_transfer_serializer = StockTransferMaster1_IDRestSerializer(
                stock_transfer_sort_pagination,
                many=True,
                context={
                    "request": request,
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                },
            )
            data = stock_transfer_serializer.data
            if not data == None:
                response_data = {
                    "StatusCode": 6000,
                    "data": data,
                    "count": len(stock_transfer_object),
                }
            else:
                response_data = {"StatusCode": 6001}

            return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def stockTransferMasterID(request, pk):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]
    if StockTransferMaster_ID.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = StockTransferMaster_ID.objects.get(CompanyID=CompanyID, pk=pk)

        serialized = StockTransferMaster_IDRestSerializer(
            instance, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding}
        )

        # request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Stock Transfer', 'View',
        #              'Stock Transfer Single Viewed successfully.', 'Stock Transfer Single Viewed successfully.')
        response_data = {"StatusCode": 6000, "data": serialized.data}
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Stock Transfer Master ID Not Found!",
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def delete_stockTransferDetails(request, pk):
    data = request.data
    CompanyID = data["CompanyID"]
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
            "message": "Stock Transfer Details Deleted Successfully!",
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Stock Transfer Details Not Found!",
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def delete_stockTransferMasterID(request, pk):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    today = datetime.datetime.now()
    try:
        selecte_ids = data["selecte_ids"]
    except:
        selecte_ids = []

    instances = None
    if selecte_ids:
        if StockTransferMaster_ID.objects.filter(
            CompanyID=CompanyID, pk__in=selecte_ids
        ).exists():
            instances = StockTransferMaster_ID.objects.filter(pk__in=selecte_ids)
    else:
        if StockTransferMaster_ID.objects.filter(CompanyID=CompanyID, pk=pk).exists():
            instances = StockTransferMaster_ID.objects.filter(pk=pk)

    if instances:
        for instance in instances:
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
            BranchFromID = instance.BranchFromID
            BranchToID = instance.BranchToID
            CreatedUserID = instance.CreatedUserID
            Action = "D"

            if StockPosting.objects.filter(
                CompanyID=CompanyID,
                VoucherType="ST",
                VoucherMasterID=StockTransferMasterID,
            ).exists():
                StockPosting.objects.filter(
                    CompanyID=CompanyID,
                    VoucherType="ST",
                    VoucherMasterID=StockTransferMasterID,
                ).delete()

            detail_instances = StockTransferDetails.objects.filter(
                CompanyID=CompanyID,
                StockTransferMasterID=StockTransferMasterID,
                BranchID=BranchID,
            )

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
                update_stock(CompanyID, BranchID, ProductID)

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
                BranchFromID=BranchFromID,
                BranchToID=BranchToID,
            )

        # request , company, log_type, user, source, action, message, description
        activity_log(
            request._request,
            CompanyID,
            "Information",
            CreatedUserID,
            "Stock Transfer",
            "Delete",
            "Stock Transfer Deleted successfully.",
            "Stock Transfer Deleted successfully.",
        )
        response_data = {
            "StatusCode": 6000,
            "title": "Success",
            "message": "Stock Transfer Deleted Successfully!",
        }
    else:
        # request , company, log_type, user, source, action, message, description
        activity_log(
            request._request,
            CompanyID,
            "Warning",
            CreatedUserID,
            "Stock Transfer",
            "Delete",
            "Stock Transfer Deleted Failed.",
            "Stock Transfer Not Found",
        )
        response_data = {
            "StatusCode": 6001,
            "title": "Failed",
            "message": "Stock Transfer Not Found!",
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def report_stockTransfer_register(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    BranchID = data["BranchID"]
    PriceRounding = data["PriceRounding"]
    FromDate = data["FromDate"]
    ToDate = data["ToDate"]
    UserID = data["UserID"]
    WareHouseFrom = data["WareHouseFrom"]
    WareHouseTo = data["WareHouseTo"]

    if StockTransferMaster_ID.objects.filter(
        CompanyID=CompanyID,
        BranchID=BranchID,
        Date__gte=FromDate,
        Date__lte=ToDate,
        VoucherType="ST",
    ).exists():
        # instance = StockTransferMaster_ID.objects.filter(
        #     CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate
        # )

        # if not UserID == "0":
        #     UserID = UserTable.objects.get(pk=UserID).customer.user.id
        #     if instance.filter(CreatedUserID=UserID).exists():
        #         instance = instance.filter(CreatedUserID=UserID)

        # if WareHouseFrom == 0 and WareHouseTo == 0:
        #     report_instance = instance
        # elif WareHouseFrom == 0 and WareHouseTo > 0:
        #     report_instance = instance.filter(WarehouseToID=WareHouseTo)
        # elif WareHouseFrom > 0 and WareHouseTo == 0:
        #     report_instance = instance.filter(WarehouseFromID=WareHouseFrom)
        # else:
        #     report_instance = instance.filter(
        #         WarehouseFromID=WareHouseFrom, WarehouseToID=WareHouseTo
        #     )

        # serialized = StockTransferRegisterReportSerializer(
        #     report_instance,
        #     many=True,
        #     context={
        #         "CompanyID": CompanyID,
        #         "PriceRounding": PriceRounding,
        #     },
        # )

        df, details = stock_transfer_report_data(
            data["CompanyID"],
            BranchID,
            FromDate,
            ToDate,
            PriceRounding,
            int(UserID),
            int(WareHouseFrom),
            int(WareHouseTo),
            "ST",
        )
        response_data = {"StatusCode": 6000, "data": details}
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Datas Not Found During this time!",
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def get_stock_order(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    StockOrderNo = data["StockOrderNo"]
    PriceRounding = data["PriceRounding"]
    if StockTransferMaster_ID.objects.filter(CompanyID=CompanyID, VoucherNo=StockOrderNo).exists():
        instance = StockTransferMaster_ID.objects.filter(
            CompanyID=CompanyID, VoucherNo=StockOrderNo, IsTaken=False).first()
        if instance:
            serialized = StockTransferMaster_IDRestSerializer(
                instance, context={"CompanyID": CompanyID,
                                "PriceRounding": PriceRounding}
            )
            response_data = {"StatusCode": 6000, "data": serialized.data}
        else:
            response_data = {"StatusCode": 6001,
                             "message": "Stock Order Already Transfered" }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Stock Order Not Found!",
        }

    return Response(response_data, status=status.HTTP_200_OK)
