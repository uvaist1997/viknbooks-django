from brands.models import StockAdjustmentMaster, StockAdjustmentMaster_Log, StockAdjustmentDetails, StockAdjustmentDetails_Log, ExcessStockMaster, ExcessStockMaster_Log, ExcessStockDetails,\
    ExcessStockDetails_Log, PriceList, StockPosting, StockPosting_Log, StockRate, StockTrans, ShortageStockMaster, ShortageStockMaster_Log, ShortageStockDetails, ShortageStockDetails_Log,Batch,GeneralSettings
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v3.stockAdjustments.serializers import StockAdjustmentMasterSerializer, StockAdjustmentMasterRestSerializer, StockAdjustmentDetailsSerializer, StockAdjustmentDetailsRestSerializer
from api.v3.brands.serializers import ListSerializer
from api.v3.stockAdjustments.functions import generate_serializer_errors, get_VoucherNo
from rest_framework import status
from api.v3.stockAdjustments.functions import get_auto_id, get_auto_idMaster
import datetime
from main.functions import get_company
from api.v3.stockPostings.functions import get_auto_excessMasterID, get_auto_excessDetailsID, get_auto_shortageMasterID, get_auto_shortageDetailsID
from api.v3.purchases.functions import get_auto_StockRateID, get_auto_StockTransID
from api.v3.sales.functions import get_auto_stockPostid
from api.v3.products.functions import get_auto_AutoBatchCode


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_stockAdjustment(request):
    today = datetime.datetime.now()

    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)

    CreatedUserID = data['CreatedUserID']
    BranchID = data['BranchID']
    Date = data['Date']
    Notes = data['Notes']
    WarehouseID = data['WarehouseID']
    TotalQty = data['TotalQty']
    GrandTotal = data['GrandTotal']

    Action = "A"

    ExcessDetails = []
    ShortageDetails = []

    Details = data["Details"]

    for d in Details:
        ProductID = d['ProductID']
        Stock = d['Stock']
        PriceListID = d['PriceListID']
        ExcessOrShortage = d['ExcessOrShortage']
        StockAdjustment = d['StockAdjustment']
        CostPerItem = d['CostPerItem']
        BatchCode = d['BatchCode']
        Batch_purchasePrice = d['Batch_purchasePrice']
        Batch_salesPrice = d['Batch_salesPrice']

        if(float(ExcessOrShortage) > 0):
            ExcessDetails.append({
                "ProductID": ProductID,
                "Stock": Stock,
                "PriceListID": PriceListID,
                "ExcessStock": ExcessOrShortage,
                "StockAdjustment": StockAdjustment,
                "CostPerItem": CostPerItem,
                "BatchCode": BatchCode,
                "Batch_purchasePrice": Batch_purchasePrice,
                "Batch_salesPrice": Batch_salesPrice,
            })
        if(float(ExcessOrShortage) < 0):
            ShortageDetails.append({
                "ProductID": ProductID,
                "Stock": Stock,
                "PriceListID": PriceListID,
                "ShortageStock": ExcessOrShortage,
                "StockAdjustment": StockAdjustment,
                "CostPerItem": CostPerItem,
                "BatchCode": BatchCode,
                "Batch_purchasePrice": Batch_purchasePrice,
                "Batch_salesPrice": Batch_salesPrice,
            })

    if len(ExcessDetails) > 0:
        VoucherType = "ES"
        VoucherNo = get_VoucherNo(VoucherType, BranchID, CompanyID)

        ExcessStockMasterID = get_auto_excessMasterID(
            ExcessStockMaster, BranchID, CompanyID)

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

        for e in ExcessDetails:
            ProductID = e['ProductID']
            Stock = e['Stock']
            PriceListID = e['PriceListID']
            ExcessStock = e['ExcessStock']
            CostPerItem = e['CostPerItem']
            BatchCode = e['BatchCode']
            Batch_purchasePrice = e['Batch_purchasePrice']
            Batch_salesPrice = e['Batch_salesPrice']

            ExcessStock = float(ExcessStock)

            ExcessStockDetailsID = get_auto_excessDetailsID(
                ExcessStockDetails, BranchID, CompanyID)

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
            )

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

            pricelist_ins = PriceList.objects.get(
                PriceListID=PriceListID, CompanyID=CompanyID, BranchID=BranchID)
            SalesPrice = pricelist_ins.SalesPrice
            PurchasePrice = pricelist_ins.PurchasePrice

            StockPostingID = get_auto_stockPostid(
                StockPosting, BranchID, CompanyID)

            StockPosting.objects.create(
                StockPostingID=StockPostingID,
                BranchID=BranchID,
                Action=Action,
                Date=Date,
                VoucherMasterID=ExcessStockMasterID,
                VoucherType=VoucherType,
                ProductID=ProductID,
                WareHouseID=WarehouseID,
                QtyIn=ExcessStock,
                Rate=CostPerItem,
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
                VoucherType=VoucherType,
                ProductID=ProductID,
                WareHouseID=WarehouseID,
                QtyIn=ExcessStock,
                Rate=CostPerItem,
                PriceListID=PriceListID,
                IsActive=True,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
                check_EnableProductBatchWise = GeneralSettings.objects.get(
                    CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
                if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                    if Batch.objects.filter(CompanyID=CompanyID,BranchID=BranchID,BatchCode=BatchCode).exists():
                        batch_insts = Batch.objects.get(CompanyID=CompanyID,BranchID=BranchID,BatchCode=BatchCode)

                        StockIn = batch_insts.StockIn
                        batch_insts.StockIn = float(StockIn) + float(ExcessStock)
                        batch_insts.save()
                    else:
                        BatchCode = get_auto_AutoBatchCode(
                            Batch, BranchID, CompanyID)
                        Batch.objects.create(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            BatchCode=BatchCode,
                            StockIn=ExcessStock,
                            PurchasePrice=Batch_purchasePrice,
                            SalesPrice=Batch_salesPrice,
                            PriceListID=PriceListID,
                            ProductID=ProductID,
                            WareHouseID=WarehouseID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                        )

            if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Cost=CostPerItem, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID).exists():
                stockRateInstance = StockRate.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, Cost=CostPerItem, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID)

                StockRateID = stockRateInstance.StockRateID
                stockRateInstance.Qty = float(
                    stockRateInstance.Qty) + float(ExcessStock)
                stockRateInstance.save()

                if StockTrans.objects.filter(StockRateID=StockRateID, DetailID=ExcessStockDetailsID, MasterID=ExcessStockMasterID, VoucherType=VoucherType, BranchID=BranchID, IsActive=True).exists():
                    stockTra_in = StockTrans.objects.filter(StockRateID=StockRateID, DetailID=ExcessStockDetailsID,
                                                            MasterID=ExcessStockMasterID, VoucherType=VoucherType, BranchID=BranchID, IsActive=True).first()
                    stockTra_in.Qty = float(
                        stockTra_in.Qty) + float(ExcessStock)
                    stockTra_in.save()
                else:
                    StockTransID = get_auto_StockTransID(
                        StockTrans, BranchID, CompanyID)
                    StockTrans.objects.create(
                        StockTransID=StockTransID,
                        BranchID=BranchID,
                        VoucherType=VoucherType,
                        StockRateID=StockRateID,
                        DetailID=ExcessStockDetailsID,
                        MasterID=ExcessStockMasterID,
                        Qty=ExcessStock,
                        IsActive=True,
                        CompanyID=CompanyID,
                    )

            else:
                StockRateID = get_auto_StockRateID(
                    StockRate, BranchID, CompanyID)
                StockRate.objects.create(
                    StockRateID=StockRateID,
                    BranchID=BranchID,
                    PurchasePrice=PurchasePrice,
                    SalesPrice=SalesPrice,
                    Qty=ExcessStock,
                    Cost=CostPerItem,
                    ProductID=ProductID,
                    WareHouseID=WarehouseID,
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
                    DetailID=ExcessStockDetailsID,
                    MasterID=ExcessStockMasterID,
                    Qty=ExcessStock,
                    IsActive=True,
                    CompanyID=CompanyID,
                )

    if len(ShortageDetails) > 0:
        VoucherType = "SS"
        VoucherNo = get_VoucherNo(VoucherType, BranchID, CompanyID)

        ShortageStockMasterID = get_auto_shortageMasterID(
            ShortageStockMaster, BranchID, CompanyID)

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

        for e in ShortageDetails:
            ProductID = e['ProductID']
            Stock = e['Stock']
            PriceListID = e['PriceListID']
            ShortageStock = e['ShortageStock']
            CostPerItem = e['CostPerItem']
            BatchCode = e['BatchCode']
            Batch_purchasePrice = e['Batch_purchasePrice']
            Batch_salesPrice = e['Batch_salesPrice']

            ShortageStock = float(ShortageStock)

            ShortageStockDetailsID = get_auto_shortageDetailsID(
                ShortageStockDetails, BranchID, CompanyID)

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
            )

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

            pricelist_ins = PriceList.objects.get(
                PriceListID=PriceListID, CompanyID=CompanyID, BranchID=BranchID)
            SalesPrice = pricelist_ins.SalesPrice
            PurchasePrice = pricelist_ins.PurchasePrice

            StockPostingID = get_auto_stockPostid(
                StockPosting, BranchID, CompanyID)

            StockPosting.objects.create(
                StockPostingID=StockPostingID,
                BranchID=BranchID,
                Action=Action,
                Date=Date,
                VoucherMasterID=ShortageStockMasterID,
                VoucherType=VoucherType,
                ProductID=ProductID,
                WareHouseID=WarehouseID,
                QtyOut=ShortageStock,
                Rate=CostPerItem,
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
                VoucherType=VoucherType,
                ProductID=ProductID,
                WareHouseID=WarehouseID,
                QtyOut=ShortageStock,
                Rate=CostPerItem,
                PriceListID=PriceListID,
                IsActive=True,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
                check_EnableProductBatchWise = GeneralSettings.objects.get(
                    CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
                if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                    if Batch.objects.filter(CompanyID=CompanyID,BranchID=BranchID,BatchCode=BatchCode).exists():
                        batch_insts = Batch.objects.get(CompanyID=CompanyID,BranchID=BranchID,BatchCode=BatchCode)
                        abs_ShortageStock = abs(ShortageStock)
                        StockOut = batch_insts.StockOut
                        batch_insts.StockOut = float(StockOut) + float(abs_ShortageStock)
                        batch_insts.save()
                    else:
                        BatchCode = get_auto_AutoBatchCode(
                            Batch, BranchID, CompanyID)
                        Batch.objects.create(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            BatchCode=BatchCode,
                            StockOut=abs_ShortageStock,
                            PurchasePrice=Batch_purchasePrice,
                            SalesPrice=Batch_salesPrice,
                            PriceListID=PriceListID,
                            ProductID=ProductID,
                            WareHouseID=WarehouseID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                        )

            if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Cost=CostPerItem, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID).exists():
                stockRateInstance = StockRate.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, Cost=CostPerItem, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID)

                StockRateID = stockRateInstance.StockRateID
                stockRateInstance.Qty = float(
                    stockRateInstance.Qty) - float(ShortageStock)
                stockRateInstance.save()

                if StockTrans.objects.filter(StockRateID=StockRateID, DetailID=ShortageStockDetailsID, MasterID=ShortageStockMasterID, VoucherType=VoucherType, BranchID=BranchID, IsActive=True).exists():
                    stockTra_in = StockTrans.objects.filter(StockRateID=StockRateID, DetailID=ShortageStockDetailsID,
                                                            MasterID=ShortageStockMasterID, VoucherType=VoucherType, BranchID=BranchID, IsActive=True).first()
                    stockTra_in.Qty = float(
                        stockTra_in.Qty) - float(ShortageStock)
                    stockTra_in.save()
                else:
                    StockTransID = get_auto_StockTransID(
                        StockTrans, BranchID, CompanyID)
                    StockTrans.objects.create(
                        StockTransID=StockTransID,
                        BranchID=BranchID,
                        VoucherType=VoucherType,
                        StockRateID=StockRateID,
                        DetailID=ShortageStockDetailsID,
                        MasterID=ShortageStockMasterID,
                        Qty=ShortageStock,
                        IsActive=True,
                        CompanyID=CompanyID,
                    )

            else:
                StockRateID = get_auto_StockRateID(
                    StockRate, BranchID, CompanyID)
                StockRate.objects.create(
                    StockRateID=StockRateID,
                    BranchID=BranchID,
                    PurchasePrice=PurchasePrice,
                    SalesPrice=SalesPrice,
                    Qty=ShortageStock,
                    Cost=CostPerItem,
                    ProductID=ProductID,
                    WareHouseID=WarehouseID,
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
                    DetailID=ShortageStockDetailsID,
                    MasterID=ShortageStockMasterID,
                    Qty=ShortageStock,
                    IsActive=True,
                    CompanyID=CompanyID,
                )

    response_data = {
        "StatusCode": 6000,
        "message": "Stock Adjustments created Successfully!!!",
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def edit_stockAdjustment(request, pk):
    today = datetime.datetime.now()

    stockAdjustmentMaster_instance = None

    stockAdjustmentDetails = None

    stockAdjustmentMaster_instance = StockAdjustmentMaster.objects.get(pk=pk)

    StockAdjustmentMasterID = stockAdjustmentMaster_instance.StockAdjustmentMasterID
    BranchID = stockAdjustmentMaster_instance.BranchID
    CreatedUserID = stockAdjustmentMaster_instance.CreatedUserID

    data = request.data

    VoucherNo = data['VoucherNo']
    InvoiceNo = data['InvoiceNo']
    Date = data['Date']
    WarehouseID = data['WarehouseID']
    Notes = data['Notes']
    GroupWise = data['GroupWise']
    ProductGroupID = data['ProductGroupID']
    IsActive = data['IsActive']

    Action = "M"

    stockAdjustmentMaster_instance.VoucherNo = VoucherNo
    stockAdjustmentMaster_instance.InvoiceNo = InvoiceNo
    stockAdjustmentMaster_instance.Date = Date
    stockAdjustmentMaster_instance.WarehouseID = WarehouseID
    stockAdjustmentMaster_instance.Notes = Notes
    stockAdjustmentMaster_instance.GroupWise = GroupWise
    stockAdjustmentMaster_instance.ProductGroupID = ProductGroupID
    stockAdjustmentMaster_instance.IsActive = IsActive
    stockAdjustmentMaster_instance.Action = Action
    stockAdjustmentMaster_instance.save()

    StockAdjustmentMaster_Log.objects.create(
        TransactionID=StockAdjustmentMasterID,
        BranchID=BranchID,
        VoucherNo=VoucherNo,
        InvoiceNo=InvoiceNo,
        Date=Date,
        WarehouseID=WarehouseID,
        Notes=Notes,
        GroupWise=GroupWise,
        ProductGroupID=ProductGroupID,
        IsActive=IsActive,
        Action=Action,
        CreatedUserID=CreatedUserID,
        CreatedDate=today,
    )

    stockAdjustmentDetails = data["StockAdjustmentDetails"]

    for stockAdjustmentDetail in stockAdjustmentDetails:
        pk = stockAdjustmentDetail["id"]
        ProductID = stockAdjustmentDetail['ProductID']
        PriceListID = stockAdjustmentDetail['PriceListID']
        ActualStock = stockAdjustmentDetail['ActualStock']
        PhysicalStock = stockAdjustmentDetail['PhysicalStock']
        Difference = stockAdjustmentDetail['Difference']

        stockAdjustmentDetails_instance = StockAdjustmentDetails.objects.get(
            pk=pk)

        StockAdjustmentDetailsID = stockAdjustmentDetails_instance.StockAdjustmentDetailsID

        stockAdjustmentDetails_instance.ProductID = ProductID
        stockAdjustmentDetails_instance.PriceListID = PriceListID
        stockAdjustmentDetails_instance.ActualStock = ActualStock
        stockAdjustmentDetails_instance.PhysicalStock = PhysicalStock
        stockAdjustmentDetails_instance.Difference = Difference
        stockAdjustmentDetails_instance.Action = Action

        stockAdjustmentDetails_instance.save()

        StockAdjustmentDetails_Log.objects.create(
            TransactionID=StockAdjustmentDetailsID,
            BranchID=BranchID,
            StockAdjustmentMasterID=StockAdjustmentMasterID,
            ProductID=ProductID,
            PriceListID=PriceListID,
            ActualStock=ActualStock,
            PhysicalStock=PhysicalStock,
            Difference=Difference,
            Action=Action,
        )

    response_data = {
        "StatusCode": 6000,
        "message": "Stock Adjustment Updated Successfully!!!",
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_stockAdjustmentMaster(request):
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        dummies = StockAdjustmentDetailsDummy.objects.filter(BranchID=BranchID)

        for dummy in dummies:
            dummy.delete()

        if StockAdjustmentMaster.objects.filter(BranchID=BranchID).exists():

            instances = StockAdjustmentMaster.objects.filter(BranchID=BranchID)

            serialized = StockAdjustmentMasterRestSerializer(
                instances, many=True)

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Stock Adjustment Master Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def stockAdjustmentMaster(request, pk):
    instance = None
    if StockAdjustmentMaster.objects.filter(pk=pk).exists():
        instance = StockAdjustmentMaster.objects.get(pk=pk)
    if instance:
        serialized = StockAdjustmentMasterRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Stock Adjustment Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_stockAdjustmentDetails(request, pk):
    instance = None
    if StockAdjustmentDetails.objects.filter(pk=pk).exists():
        instance = StockAdjustmentDetails.objects.get(pk=pk)
    if instance:
        StockAdjustmentDetailsID = instance.StockAdjustmentDetailsID
        BranchID = instance.BranchID
        StockAdjustmentMasterID = instance.StockAdjustmentMasterID
        ProductID = instance.ProductID
        PriceListID = instance.PriceListID
        ActualStock = instance.ActualStock
        PhysicalStock = instance.PhysicalStock
        Difference = instance.Difference
        Action = "D"

        instance.delete()

        StockAdjustmentDetails_Log.objects.create(
            TransactionID=StockAdjustmentDetailsID,
            BranchID=BranchID,
            StockAdjustmentMasterID=StockAdjustmentMasterID,
            ProductID=ProductID,
            PriceListID=PriceListID,
            ActualStock=ActualStock,
            PhysicalStock=PhysicalStock,
            Difference=Difference,
            Action=Action,
        )
        response_data = {
            "StatusCode": 6000,
            "message": "Stock Adjustment Details Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Stock Adjustment Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_stockAdjustmentMaster(request, pk):
    today = datetime.datetime.now()
    instance = None
    if StockAdjustmentMaster.objects.filter(pk=pk).exists():
        instance = StockAdjustmentMaster.objects.get(pk=pk)
    if instance:
        StockAdjustmentMasterID = instance.StockAdjustmentMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        InvoiceNo = instance.InvoiceNo
        Date = instance.Date
        WarehouseID = instance.WarehouseID
        Notes = instance.Notes
        GroupWise = instance.GroupWise
        ProductGroupID = instance.ProductGroupID
        IsActive = instance.IsActive
        CreatedUserID = instance.CreatedUserID
        Action = "D"

        instance.delete()

        detail_instances = StockAdjustmentDetails.objects.filter(
            StockAdjustmentMasterID=StockAdjustmentMasterID)

        for detail_instance in detail_instances:

            StockAdjustmentDetailsID = detail_instance.StockAdjustmentDetailsID
            BranchID = detail_instance.BranchID
            StockAdjustmentMasterID = detail_instance.StockAdjustmentMasterID
            ProductID = detail_instance.ProductID
            PriceListID = detail_instance.PriceListID
            ActualStock = detail_instance.ActualStock
            PhysicalStock = detail_instance.PhysicalStock
            Difference = detail_instance.Difference

            detail_instance.delete()

            StockAdjustmentDetails_Log.objects.create(
                TransactionID=StockAdjustmentDetailsID,
                BranchID=BranchID,
                StockAdjustmentMasterID=StockAdjustmentMasterID,
                ProductID=ProductID,
                PriceListID=PriceListID,
                ActualStock=ActualStock,
                PhysicalStock=PhysicalStock,
                Difference=Difference,
                Action=Action,
            )

        StockAdjustmentMaster_Log.objects.create(
            TransactionID=StockAdjustmentMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            InvoiceNo=InvoiceNo,
            Date=Date,
            WarehouseID=WarehouseID,
            Notes=Notes,
            GroupWise=GroupWise,
            ProductGroupID=ProductGroupID,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
        )
        response_data = {
            "StatusCode": 6000,
            "message": "Stock Adjustment Master Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Stock Adjustment Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
