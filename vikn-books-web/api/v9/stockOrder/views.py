import datetime
import os
import re
import sys

from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from api.v9.brands.serializers import ListSerializer
from api.v9.products.functions import update_stock
from api.v9.purchases.functions import get_auto_StockRateID, get_auto_StockTransID
from api.v9.sales.functions import get_auto_stockPostid, get_auto_VoucherNo
from api.v9.stockTransfers.functions import (
    generate_serializer_errors,
    get_auto_id,
    get_auto_idMaster,
)
from api.v9.stockTransfers.serializers import (
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
    get_company,
    get_ModelInstance,
    list_pagination,
    update_voucher_table,
)
from api.v9.reportQuerys.functions import stock_transfer_report_data

@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def create_stockOrder(request):
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
            VoucherType = "STO"
            # VoucherNo Updated
            try:
                PreFix = data["PreFix"]
            except:
                PreFix = "STO"

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
                VoucherType=VoucherType
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
                VoucherType=VoucherType
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


            response_data = {
                "id":stock_transfer_create.id,
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
            "message": "some error occured..please try again",
        }

        activity_id = activity_log(
            request._request,
            CompanyID,
            "Error",
            CreatedUserID,
            "Stock Order",
            "Create",
            str(e),
            err_descrb,
        )
        body_params = str(request.data)
        Activity_Log.objects.filter(id=activity_id).update(body_params=body_params)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def edit_stockOrder(request, pk):
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
            VoucherType = "STO"

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
                VoucherType=VoucherType
            )


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
                    if not deleted_pk == "" or not deleted_pk == 0:
                        if StockTransferDetails.objects.filter(
                            CompanyID=CompanyID, pk=deleted_pk
                        ).exists():
                            deleted_detail = StockTransferDetails.objects.filter(
                                CompanyID=CompanyID, pk=deleted_pk
                            )
                            deleted_detail.delete()



            stockTransferDetails = data["StockTransferDetails"]
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

                if detailID == 1:
                    Action = "A"

                    log_instance = StockTransferDetails_Log.objects.create(
                        TransactionID=StockTransferDetailsID,
                        BranchID=BranchID,
                        StockTransferMasterID=StockTransferMasterID,
                        ProductID=ProductID,
                        Qty=Qty_detail,
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
                        Qty=Qty_detail,
                        PriceListID=PriceListID,
                        Rate=Rate,
                        MaxRate=MaxRate,
                        Amount=Amount,
                        MaxAmount=MaxAmount,
                        Action=Action,
                        CompanyID=CompanyID,
                        LogID=log_instance.ID,
                    )

            # request , company, log_type, user, source, action, message, description
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
            "message": "some error occured..please try again",
        }

        activity_log(
            request._request,
            CompanyID,
            "Error",
            CreatedUserID,
            "Stock Order",
            "Edit",
            str(e),
            err_descrb,
        )
        return Response(response_data, status=status.HTTP_200_OK)



@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def stock_order_pagination(request):
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
        VoucherType = "STO"

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
@renderer_classes((JSONRenderer,))
def stockOrderMasterID(request, pk):
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
@renderer_classes((JSONRenderer,))
def delete_stockOrderMasterID(request, pk):
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
            "Stock Order Deleted successfully.",
            "Stock Order Deleted successfully.",
        )
        response_data = {
            "StatusCode": 6000,
            "title": "Success",
            "message": "Stock Order Deleted Successfully!",
        }
    else:
        # request , company, log_type, user, source, action, message, description
        activity_log(
            request._request,
            CompanyID,
            "Warning",
            CreatedUserID,
            "Stock Order",
            "Delete",
            "Stock Order Deleted Failed.",
            "Stock Order Not Found",
        )
        response_data = {
            "StatusCode": 6001,
            "title": "Failed",
            "message": "Stock Order Not Found!",
        }

    return Response(response_data, status=status.HTTP_200_OK)

