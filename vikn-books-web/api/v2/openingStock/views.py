from brands.models import OpeningStockMaster, OpeningStockMaster_Log, OpeningStockDetails, OpeningStockDetails_Log, OpeningStockDetailsDummy, StockPosting, StockPosting_Log,\
PriceList, StockRate, StockTrans
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v2.openingStock.serializers import OpeningStockMasterSerializer, OpeningStockMasterRestSerializer, OpeningStockDetailsSerializer, OpeningStockDetailsRestSerializer
from api.v2.brands.serializers import ListSerializer
from api.v2.openingStock.functions import generate_serializer_errors
from rest_framework import status
from api.v2.openingStock.functions import get_auto_id, get_auto_idMaster
from api.v2.sales.functions import get_auto_stockPostid 
from api.v2.purchases.functions import get_auto_StockRateID, get_auto_StockTransID
import datetime
from django.shortcuts import get_object_or_404
from main.functions import get_company, activity_log, list_pagination



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_openingStock(request):
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

    #checking voucher number already exist
    VoucherNoLow = VoucherNo.lower()
    is_voucherExist = False
    insts = OpeningStockMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
    if insts:
        for i in insts:
            voucher_no = i.VoucherNo
            voucherNo = voucher_no.lower()
            if VoucherNoLow == voucherNo:
                is_voucherExist = True

    if not is_voucherExist:
        OpeningStockMasterID = get_auto_idMaster(OpeningStockMaster,BranchID,CompanyID)
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
            
        openingStockDetails = data["OpeningStockDetails"]
        for openingStockDetail in openingStockDetails:

            ProductID = openingStockDetail["ProductID"]
            Qty = openingStockDetail["Qty"]
            PriceListID = openingStockDetail["PriceListID"]
            Rate = openingStockDetail["Rate"]
            Amount = openingStockDetail["Amount"]

            OpeningStockDetailsID = get_auto_id(OpeningStockDetails,BranchID,CompanyID)

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
                )

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

            

            # priceList = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,DefaultUnit=True,BranchID=BranchID)

            # PriceListID = priceList.PriceListID
            # MultiFactor = priceList.MultiFactor

            MultiFactor = PriceList.objects.get(CompanyID=CompanyID,PriceListID=PriceListID,BranchID=BranchID).MultiFactor
            PriceListID = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,DefaultUnit=True,BranchID=BranchID).PriceListID

            princeList_instance = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,PriceListID=PriceListID,BranchID=BranchID)
            PurchasePrice = princeList_instance.PurchasePrice
            SalesPrice = princeList_instance.SalesPrice

            # qty = float(FreeQty) + float(Qty)

            Qty = float(MultiFactor) * float(Qty)
            Cost = float(Rate) /  float(MultiFactor)

            Qy = round(Qty,4)
            Qty = str(Qy)

            Ct = round(Cost,4)
            Cost = str(Ct)

            VoucherType = "OS"
            StockPostingID = get_auto_stockPostid(StockPosting,BranchID,CompanyID)
            StockPosting.objects.create(
                StockPostingID=StockPostingID,
                BranchID=BranchID,
                Action=Action,
                Date=Date,
                VoucherMasterID=OpeningStockMasterID,
                VoucherType=VoucherType,
                ProductID=ProductID,
                BatchID=BatchID,
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

            StockPosting_Log.objects.create(
                TransactionID=StockPostingID,
                BranchID=BranchID,
                Action=Action,
                Date=Date,
                VoucherMasterID=OpeningStockMasterID,
                VoucherType=VoucherType,
                ProductID=ProductID,
                BatchID=BatchID,
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


            if StockRate.objects.filter(CompanyID=CompanyID,BranchID=BranchID,Cost=Cost,ProductID=ProductID,WareHouseID=WarehouseID,PriceListID=PriceListID).exists():
                stockRateInstance = StockRate.objects.get(CompanyID=CompanyID,BranchID=BranchID,Cost=Cost,ProductID=ProductID,WareHouseID=WarehouseID,PriceListID=PriceListID)
                
                StockRateID = stockRateInstance.StockRateID
                stockRateInstance.Qty = float(stockRateInstance.Qty) + float(Qty)
                stockRateInstance.save()

                StockTransID = get_auto_StockTransID(StockTrans,BranchID,CompanyID)
                StockTrans.objects.create(
                    StockTransID=StockTransID,
                    BranchID=BranchID,
                    VoucherType=VoucherType,
                    StockRateID=StockRateID,
                    DetailID=OpeningStockDetailsID,
                    MasterID=OpeningStockMasterID,
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
                    WareHouseID=WarehouseID,
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
                    DetailID=OpeningStockDetailsID,
                    MasterID=OpeningStockMasterID,
                    Qty=Qty,
                    IsActive=IsActive,
                    CompanyID=CompanyID,
                    )
            

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'OpeningStocK', 'Create', 'OpeningStocK created successfully.', 'OpeningStocK saved successfully.')
        response_data = {
            "StatusCode" : 6000,
            "message" : "Open Stock created Successfully!!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'OpeningStocK', 'Create', 'OpeningStocK created Failed.', 'VoucherNo already exist')
        response_data = {
        "StatusCode" : 6001,
        "message" : "VoucherNo already exist!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def edit_openingStock(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()

    openStockMaster_instance = None
    openingStockDetails = None
    openingStockDetails_instances = None
    openStockMaster_instance = OpeningStockMaster.objects.get(CompanyID=CompanyID,pk=pk)
    OpeningStockMasterID = openStockMaster_instance.OpeningStockMasterID
    BranchID = openStockMaster_instance.BranchID
    VoucherNo = openStockMaster_instance.VoucherNo


    Date = data["Date"]
    WarehouseID = data["WarehouseID"]
    Notes = data["Notes"]
    TotalQty = data["TotalQty"]
    GrandTotal = data["GrandTotal"]
    IsActive = data["IsActive"]
    BatchID = data["BatchID"]

    Action = 'M'

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

    if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=OpeningStockMasterID,BranchID=BranchID,VoucherType="OS").exists():
        stockPostingInstances = StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=OpeningStockMasterID,BranchID=BranchID,VoucherType="OS")
        for stockPostingInstance in stockPostingInstances: 
            stockPostingInstance.delete()


    if OpeningStockDetails.objects.filter(CompanyID=CompanyID,BranchID=BranchID,OpeningStockMasterID=OpeningStockMasterID).exists():
        openingStockInstances = OpeningStockDetails.objects.filter(CompanyID=CompanyID, OpeningStockMasterID=OpeningStockMasterID,BranchID=BranchID)
        for openingStockInstance in openingStockInstances: 
            openingStockInstance.delete()

    if StockTrans.objects.filter(CompanyID=CompanyID,BranchID=BranchID,MasterID=OpeningStockMasterID,VoucherType="OS",IsActive=True).exists():
        stocktransIns = StockTrans.objects.filter(CompanyID=CompanyID,BranchID=BranchID,MasterID=OpeningStockMasterID,VoucherType="OS",IsActive=True)
        for stocktran in stocktransIns:
            StockRateID = stocktran.StockRateID
            Qty = stocktran.Qty
            stockRateIns = StockRate.objects.get(BranchID=BranchID,StockRateID=StockRateID,CompanyID=CompanyID)
            stockRateIns.Qty = float(stockRateIns.Qty) - float(Qty)
            stockRateIns.save()
            stocktran.IsActive = False
            stocktran.save()

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

    VoucherType = "OS"


    # deleted_datas = data["deleted_data"]
    # if deleted_datas:
    #     for deleted_Data in deleted_datas:
    #         deleted_pk = deleted_Data['unq_id']
    #         OpeningStockDetailsID_Deleted = deleted_Data['OpeningStockDetailsID']
    #         ProductID_Deleted = deleted_Data['ProductID']
    #         PriceListID_Deleted = deleted_Data['PriceListID']
    #         Rate_Deleted = deleted_Data['Rate']
    #         OpeningStockMasterID_Deleted = deleted_Data['OpeningStockMasterID']
    #         WarehouseID_Deleted = deleted_Data['WarehouseID']

    #         if PriceList.objects.filter(CompanyID=CompanyID,ProductID=ProductID_Deleted,DefaultUnit=True).exists():
    #             priceList = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID_Deleted,DefaultUnit=True)
    #             MultiFactor = priceList.MultiFactor
    #             Cost = float(Rate_Deleted) /  float(MultiFactor)
    #             Ct = round(Cost,4)
    #             Cost_Deleted = str(Ct)

    #             if not deleted_pk == '' or not deleted_pk == 0:
    #                 if OpeningStockDetails.objects.filter(CompanyID=CompanyID,pk=deleted_pk).exists():
    #                     deleted_detail = OpeningStockDetails.objects.filter(CompanyID=CompanyID,pk=deleted_pk)
    #                     deleted_detail.delete()

    #                     if StockRate.objects.filter(CompanyID=CompanyID,ProductID=ProductID_Deleted,PriceListID=PriceListID_Deleted,Cost=Cost_Deleted,WareHouseID=WarehouseID_Deleted).exists():
    #                         stockRate_instance = StockRate.objects.get(CompanyID=CompanyID,ProductID=ProductID_Deleted,PriceListID=PriceListID_Deleted,Cost=Cost_Deleted,WareHouseID=WarehouseID_Deleted)
    #                         StockRateID = stockRate_instance.StockRateID
    #                         if StockTrans.objects.filter(CompanyID=CompanyID,DetailID=OpeningStockDetailsID_Deleted,MasterID=OpeningStockMasterID_Deleted,BranchID=BranchID,
    #                             VoucherType=VoucherType,IsActive=True,StockRateID=StockRateID).exists():
    #                             stockTrans_instance = StockTrans.objects.get(CompanyID=CompanyID,DetailID=OpeningStockDetailsID_Deleted,MasterID=OpeningStockMasterID_Deleted,BranchID=BranchID,
    #                                 VoucherType=VoucherType,IsActive=True,StockRateID=StockRateID)
    #                             qty_in_stockTrans = stockTrans_instance.Qty
    #                             stockRate_instance.Qty = float(stockRate_instance.Qty) - float(qty_in_stockTrans)
    #                             stockRate_instance.save()
    #                             stockTrans_instance.IsActive = False
    #                             stockTrans_instance.save()

    
    openingStockDetails = data["OpeningStockDetails"]

    for openingStockDetail in openingStockDetails:

        pk = openingStockDetail["unq_id"]
        detailID = openingStockDetail["detailID"]
        ProductID = openingStockDetail["ProductID"]
        Qty = openingStockDetail["Qty"]
        PriceListID = openingStockDetail["PriceListID"]
        Rate = openingStockDetail["Rate"]
        Amount = openingStockDetail["Amount"]

        # priceList = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,DefaultUnit=True)

        # PriceListID_DefUnit = priceList.PriceListID
        # MultiFactor = priceList.MultiFactor

        # # PurchasePrice = priceList.PurchasePrice
        # # SalesPrice = priceList.SalesPrice

        # # qty = float(FreeQty) + float(Qty)

        # Qty = float(MultiFactor) * float(Qty)
        # Cost = float(Rate) /  float(MultiFactor)

        # Qy = round(Qty,4)
        # Qty = str(Qy)


        # Ct = round(Cost,4)
        # Cost = str(Ct)

        # princeList_instance = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,PriceListID=PriceListID_DefUnit,BranchID=BranchID)
        # PurchasePrice = princeList_instance.PurchasePrice
        # SalesPrice = princeList_instance.SalesPrice

        OpeningStockDetailsID = get_auto_id(OpeningStockDetails,BranchID,CompanyID)

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
            )

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

        

        # priceList = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,DefaultUnit=True,BranchID=BranchID)

        # PriceListID = priceList.PriceListID
        # MultiFactor = priceList.MultiFactor

        MultiFactor = PriceList.objects.get(CompanyID=CompanyID,PriceListID=PriceListID,BranchID=BranchID).MultiFactor
        PriceListID = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,DefaultUnit=True,BranchID=BranchID).PriceListID

        princeList_instance = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,PriceListID=PriceListID,BranchID=BranchID)
        PurchasePrice = princeList_instance.PurchasePrice
        SalesPrice = princeList_instance.SalesPrice

        # qty = float(FreeQty) + float(Qty)

        Qty = float(MultiFactor) * float(Qty)
        Cost = float(Rate) /  float(MultiFactor)

        Qy = round(Qty,4)
        Qty = str(Qy)

        Ct = round(Cost,4)
        Cost = str(Ct)

        VoucherType = "OS"
        StockPostingID = get_auto_stockPostid(StockPosting,BranchID,CompanyID)
        StockPosting.objects.create(
            StockPostingID=StockPostingID,
            BranchID=BranchID,
            Action=Action,
            Date=Date,
            VoucherMasterID=OpeningStockMasterID,
            VoucherType=VoucherType,
            ProductID=ProductID,
            BatchID=BatchID,
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

        StockPosting_Log.objects.create(
            TransactionID=StockPostingID,
            BranchID=BranchID,
            Action=Action,
            Date=Date,
            VoucherMasterID=OpeningStockMasterID,
            VoucherType=VoucherType,
            ProductID=ProductID,
            BatchID=BatchID,
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

        if StockRate.objects.filter(CompanyID=CompanyID,BranchID=BranchID,Cost=Cost,ProductID=ProductID,WareHouseID=WarehouseID,PriceListID=PriceListID).exists():
            stockRateInstance = StockRate.objects.filter(CompanyID=CompanyID,BranchID=BranchID,Cost=Cost,ProductID=ProductID,WareHouseID=WarehouseID,PriceListID=PriceListID).first()
            
            StockRateID = stockRateInstance.StockRateID
            stockRateInstance.Qty = float(stockRateInstance.Qty) + float(Qty)
            stockRateInstance.save()

            StockTransID = get_auto_StockTransID(StockTrans,BranchID,CompanyID)
            StockTrans.objects.create(
                StockTransID=StockTransID,
                BranchID=BranchID,
                VoucherType=VoucherType,
                StockRateID=StockRateID,
                DetailID=OpeningStockDetailsID,
                MasterID=OpeningStockMasterID,
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
                WareHouseID=WarehouseID,
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
                DetailID=OpeningStockDetailsID,
                MasterID=OpeningStockMasterID,
                Qty=Qty,
                IsActive=IsActive,
                CompanyID=CompanyID,
                )

    #request , company, log_type, user, source, action, message, description
    activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'OpeningStocK', 'Edit', 'OpeningStocK Updated successfully.', 'OpeningStocK Updated successfully.')
    response_data = {
        "StatusCode" : 6000,
        "message" : "Open Stock Updated Successfully!!!",
    }

    return Response(response_data, status=status.HTTP_200_OK)




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

        if OpeningStockMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():

            instances = OpeningStockMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID)

            serialized = OpeningStockMasterRestSerializer(instances,many=True,context = {"CompanyID": CompanyID,
                "PriceRounding" : PriceRounding})

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'OpeningStocK', 'List View', 'OpeningStocK List Viewed successfully.', 'OpeningStocK List Viewed successfully.')
            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'OpeningStocK', 'List View', 'OpeningStocK List Viewed Failed.', 'OpeningStocK List Not Found Under this Branch.')
            response_data = {
            "StatusCode" : 6001,
            "message" : "Opening Stock Master not found in this branch."
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Branch you enterd is not valid."
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
            opening_stock_object = OpeningStockMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID)

            opening_stock_sort_pagination = list_pagination(
                opening_stock_object,
                items_per_page,
                page_number
            )
            purchase_return_serializer = OpeningStockMasterRestSerializer(
                opening_stock_sort_pagination,
                many=True,
                context={"request":request,"CompanyID":CompanyID,"PriceRounding" : PriceRounding}
            )
            data = purchase_return_serializer.data
            if not data==None:
                response_data = {
                    "StatusCode" : 6000,
                    "data" : data,
                    "count": len(opening_stock_object)
                }
            else:
                response_data = {
                    "StatusCode" : 6001
                }

            return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def openingStock(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    instance = None

    if OpeningStockMaster.objects.filter(CompanyID=CompanyID,pk=pk).exists():
        instance = OpeningStockMaster.objects.get(CompanyID=CompanyID,pk=pk)
        serialized = OpeningStockMasterRestSerializer(instance,context = {"CompanyID": CompanyID,
         "PriceRounding" : PriceRounding})

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'OpeningStocK', 'View', 'OpeningStocK Single Page Viewed successfully.', 'OpeningStocK Single Page Viewed successfully.')
        response_data = {
            "StatusCode" : 6000,
            "data" : serialized.data
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'OpeningStocK', 'View', 'OpeningStocK Single Page Failed.', 'OpeningStocK List Not Found Under this Branch.')
        response_data = {
            "StatusCode" : 6001,
            "message" : "Opening Stock Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)




@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_openingStockDetails(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    instance = None
    if OpeningStockDetails.objects.filter(CompanyID=CompanyID,pk=pk).exists():
        instance = OpeningStockDetails.objects.get(CompanyID=CompanyID,pk=pk)
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

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'OpeningStocK', 'Delete', 'OpeningStocK Deleted successfully.', 'OpeningStocK Deleted successfully..')
        response_data = {
            "StatusCode" : 6000,
            "message" : "Opening Stock Details Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Opening Stock Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_openingStockMaster(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    instance = None
    if OpeningStockMaster.objects.filter(CompanyID=CompanyID,pk=pk).exists():
        instance = OpeningStockMaster.objects.get(CompanyID=CompanyID,pk=pk)

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

        if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=OpeningStockMasterID,BranchID=BranchID,VoucherType="OS").exists():

            stockPostingInstances = StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=OpeningStockMasterID,BranchID=BranchID,VoucherType="OS")
            
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
                    VoucherMasterID=OpeningStockMasterID,
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

        detail_instances = OpeningStockDetails.objects.filter(CompanyID=CompanyID,OpeningStockMasterID=OpeningStockMasterID)

        for detail_instance in detail_instances:

            OpeningStockDetailsID = detail_instance.OpeningStockDetailsID
            BranchID = detail_instance.BranchID
            OpeningStockMasterID = detail_instance.OpeningStockMasterID
            ProductID = detail_instance.ProductID
            Qty = detail_instance.Qty
            PriceListID = detail_instance.PriceListID
            Rate = detail_instance.Rate
            Amount = detail_instance.Amount

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


            if StockTrans.objects.filter(CompanyID=CompanyID, DetailID=OpeningStockDetailsID, MasterID=OpeningStockMasterID, BranchID=BranchID, VoucherType="OS",IsActive = True).exists():
                stockTrans_instances = StockTrans.objects.filter(
                    CompanyID=CompanyID, DetailID=OpeningStockDetailsID, MasterID=OpeningStockMasterID, BranchID=BranchID, VoucherType="OS",IsActive = True)

                for i in stockTrans_instances:
                    stockRateID = i.StockRateID
                    i.IsActive = False
                    i.save()

                    stockRate_instance = StockRate.objects.get(
                        CompanyID=CompanyID, StockRateID=stockRateID, BranchID=BranchID)
                    stockRate_instance.Qty = float(stockRate_instance.Qty) - float(i.Qty)
                    stockRate_instance.save()

        
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'OpeningStocK', 'Delete', 'OpeningStocK Deleted successfully.', 'OpeningStocK Deleted successfully..')
        response_data = {
            "StatusCode" : 6000,
            "title" : "Success",
            "message" : "Opening Stock Master Deleted Successfully!"
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'OpeningStocK', 'Delete', 'OpeningStocK Deleted Failed.', 'OpeningStocK Not Found Under this Branch.')
        response_data = {
            "StatusCode" : 6001,
            "title" : "Failed",
            "message" : "Opening Stock Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)

