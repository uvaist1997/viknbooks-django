from brands.models import Kitchen,Kitchen_Log,CancelReasons,StockPosting_Log,StockPosting,SalesDetails,PriceList,LedgerPosting_Log,LedgerPosting,AccountLedger,QrCode,Parties,UserTable,SalesMaster_Log,SalesDetails_Log,Batch,SalesMaster,SalesOrderDetails,SalesOrderDetails_Log,SalesOrderMaster_Log,GeneralSettings,POS_Settings,Warehouse,SalesOrderMaster,ProductGroup,Product,POS_Table_log,PriceCategory,POS_Table,POS_User_log,POS_User,Employee,POS_Role_Log,POS_Role,POSHoldMaster, POSHoldMaster_Log, POSHoldDetails, POSHoldDetails_Log, POSHoldDetailsDummy
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v6.posholds.serializers import Kitchen_Serializer,POS_LedgerSerializer,POS_SalesOrder_PrintSerializer,POS_Sales_PrintSerializer,OrderReason_Serializer,POS_Order_Serializer,POS_ProductGroup_Serializer,POS_Product_Serializer,POS_Table_Serializer,POS_User_Serializer,POS_Role_Serializer,POSHoldMasterSerializer, POSHoldMasterRestSerializer, POSHoldDetailsSerializer, POSHoldDetailsRestSerializer
from api.v6.brands.serializers import ListSerializer
from api.v6.posholds.functions import generate_serializer_errors,get_pin_no,get_TokenNo,get_KitchenID
from rest_framework import status
from api.v6.posholds.functions import get_auto_id, get_auto_idMaster,get_VoucherNoForPOS,get_InvoiceNo
import datetime
from main.functions import get_company,activity_log
from random import randint
from django.db import transaction,IntegrityError
from main.functions import update_voucher_table
from api.v6.salesOrders.functions import get_auto_id as order_id, get_auto_idMaster as order_master_id
from api.v6.sales.functions import get_auto_id as invoice_id, get_auto_idMaster as invoice_master_id,get_auto_stockPostid
import re,sys, os
from api.v6.salesOrders.serializers import  SalesOrderMasterRestSerializer
from api.v6.sales.serializers import SalesMasterRestSerializer
from api.v6.accountLedgers.functions import get_auto_LedgerPostid
from api.v6.products.functions import get_auto_AutoBatchCode,update_stock
from api.v6.ledgerPosting.functions import convertOrderdDict
from api.v6.users.serializers import MyCompaniesSerializer, CompaniesSerializer
from brands import models as models
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from datetime import date
from api.v6.sales.functions import get_Genrate_VoucherNo


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_poshold(request):
    today = datetime.datetime.now()

    data = request.data

    BranchID = data['BranchID']
    VoucherNo = data['VoucherNo']
    InvoiceNo = data['InvoiceNo']
    Date = data['Date']
    LedgerID = data['LedgerID']
    PriceCategoryID = data['PriceCategoryID']
    EmployeeID = data['EmployeeID']
    SalesAccount = data['SalesAccount']
    HoldStatus = data['HoldStatus']
    CustomerName = data['CustomerName']
    Address1 = data['Address1']
    Address2 = data['Address2']
    Address3 = data['Address3']
    Notes = data['Notes']
    FinacialYearID = data['FinacialYearID']
    TotalTax = data['TotalTax']
    NetTotal = data['NetTotal']
    BillDiscount = data['BillDiscount']
    GrandTotal = data['GrandTotal']
    RoundOff = data['RoundOff']
    CashReceived = data['CashReceived']
    CashAmount = data['CashAmount']
    BankAmount = data['BankAmount']
    WarehouseID = data['WarehouseID']
    TableID = data['TableID']
    SeatNumber = data['SeatNumber']
    NoOfGuests = data['NoOfGuests']
    INOUT = data['INOUT']
    TokenNumber = data['TokenNumber']
    IsActive = data['IsActive']
    CreatedUserID = data['CreatedUserID']

    Action = "A"

    POSHoldMasterID = get_auto_idMaster(POSHoldMaster, BranchID)

    POSHoldMaster.objects.create(
        POSHoldMasterID=POSHoldMasterID,
        BranchID=BranchID,
        VoucherNo=VoucherNo,
        InvoiceNo=InvoiceNo,
        Date=Date,
        LedgerID=LedgerID,
        PriceCategoryID=PriceCategoryID,
        EmployeeID=EmployeeID,
        SalesAccount=SalesAccount,
        HoldStatus=HoldStatus,
        CustomerName=CustomerName,
        Address1=Address1,
        Address2=Address2,
        Address3=Address3,
        Notes=Notes,
        FinacialYearID=FinacialYearID,
        TotalTax=TotalTax,
        NetTotal=NetTotal,
        BillDiscount=BillDiscount,
        GrandTotal=GrandTotal,
        RoundOff=RoundOff,
        CashReceived=CashReceived,
        CashAmount=CashAmount,
        BankAmount=BankAmount,
        WarehouseID=WarehouseID,
        TableID=TableID,
        SeatNumber=SeatNumber,
        NoOfGuests=NoOfGuests,
        INOUT=INOUT,
        TokenNumber=TokenNumber,
        IsActive=IsActive,
        Action=Action,
        CreatedUserID=CreatedUserID,
        CreatedDate=today
    )

    POSHoldMaster_Log.objects.create(
        TransactionID=POSHoldMasterID,
        BranchID=BranchID,
        VoucherNo=VoucherNo,
        InvoiceNo=InvoiceNo,
        Date=Date,
        LedgerID=LedgerID,
        PriceCategoryID=PriceCategoryID,
        EmployeeID=EmployeeID,
        SalesAccount=SalesAccount,
        HoldStatus=HoldStatus,
        CustomerName=CustomerName,
        Address1=Address1,
        Address2=Address2,
        Address3=Address3,
        Notes=Notes,
        FinacialYearID=FinacialYearID,
        TotalTax=TotalTax,
        NetTotal=NetTotal,
        BillDiscount=BillDiscount,
        GrandTotal=GrandTotal,
        RoundOff=RoundOff,
        CashReceived=CashReceived,
        CashAmount=CashAmount,
        BankAmount=BankAmount,
        WarehouseID=WarehouseID,
        TableID=TableID,
        SeatNumber=SeatNumber,
        NoOfGuests=NoOfGuests,
        INOUT=INOUT,
        TokenNumber=TokenNumber,
        IsActive=IsActive,
        Action=Action,
        CreatedUserID=CreatedUserID,
        CreatedDate=today
    )

    posholdDetails = data["POSHoldDetails"]

    for posholdDetail in posholdDetails:

        ProductID = posholdDetail['ProductID']
        Qty = posholdDetail['Qty']
        FreeQty = posholdDetail['FreeQty']
        UnitPrice = posholdDetail['UnitPrice']
        RateWithTax = posholdDetail['RateWithTax']
        CostPerPrice = posholdDetail['CostPerPrice']
        PriceListID = posholdDetail['PriceListID']
        TaxID = posholdDetail['TaxID']
        TaxType = posholdDetail['TaxType']
        DiscountPerc = posholdDetail['DiscountPerc']
        DiscountAmount = posholdDetail['DiscountAmount']
        GrossAmount = posholdDetail['GrossAmount']
        TaxableAmount = posholdDetail['TaxableAmount']
        VATPerc = posholdDetail['VATPerc']
        VATAmount = posholdDetail['VATAmount']
        SGSTPerc = posholdDetail['SGSTPerc']
        SGSTAmount = posholdDetail['SGSTAmount']
        CGSTPerc = posholdDetail['CGSTPerc']
        CGSTAmount = posholdDetail['CGSTAmount']
        IGSTPerc = posholdDetail['IGSTPerc']
        IGSTAmount = posholdDetail['IGSTAmount']
        NetAmount = posholdDetail['NetAmount']
        Flavour = posholdDetail['Flavour']

        POSHoldDetailsID = get_auto_id(POSHoldDetails, BranchID)

        POSHoldDetails.objects.create(
            POSHoldDetailsID=POSHoldDetailsID,
            BranchID=BranchID,
            POSHoldMasterID=POSHoldMasterID,
            ProductID=ProductID,
            Qty=Qty,
            FreeQty=FreeQty,
            UnitPrice=UnitPrice,
            RateWithTax=RateWithTax,
            CostPerPrice=CostPerPrice,
            PriceListID=PriceListID,
            TaxID=TaxID,
            TaxType=TaxType,
            DiscountPerc=DiscountPerc,
            DiscountAmount=DiscountAmount,
            GrossAmount=GrossAmount,
            TaxableAmount=TaxableAmount,
            VATPerc=VATPerc,
            VATAmount=VATAmount,
            SGSTPerc=SGSTPerc,
            SGSTAmount=SGSTAmount,
            CGSTPerc=CGSTPerc,
            CGSTAmount=CGSTAmount,
            IGSTPerc=IGSTPerc,
            IGSTAmount=IGSTAmount,
            NetAmount=NetAmount,
            Flavour=Flavour,
            Action=Action,
        )

        POSHoldDetails_Log.objects.create(
            TransactionID=POSHoldDetailsID,
            BranchID=BranchID,
            POSHoldMasterID=POSHoldMasterID,
            ProductID=ProductID,
            Qty=Qty,
            FreeQty=FreeQty,
            UnitPrice=UnitPrice,
            RateWithTax=RateWithTax,
            CostPerPrice=CostPerPrice,
            PriceListID=PriceListID,
            TaxID=TaxID,
            TaxType=TaxType,
            DiscountPerc=DiscountPerc,
            DiscountAmount=DiscountAmount,
            GrossAmount=GrossAmount,
            TaxableAmount=TaxableAmount,
            VATPerc=VATPerc,
            VATAmount=VATAmount,
            SGSTPerc=SGSTPerc,
            SGSTAmount=SGSTAmount,
            CGSTPerc=CGSTPerc,
            CGSTAmount=CGSTAmount,
            IGSTPerc=IGSTPerc,
            IGSTAmount=IGSTAmount,
            NetAmount=NetAmount,
            Flavour=Flavour,
            Action=Action,
        )

    dummies = POSHoldDetailsDummy.objects.filter(BranchID=BranchID)

    for dummy in dummies:
        dummy.delete()

    response_data = {
        "StatusCode": 6000,
        "message": "POSHold created Successfully!!!",
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def edit_poshold(request, pk):
    today = datetime.datetime.now()

    posholdMaster_instance = None
    posHoldDetails = None

    posholdMaster_instance = POSHoldMaster.objects.get(pk=pk)

    POSHoldMasterID = posholdMaster_instance.POSHoldMasterID
    BranchID = posholdMaster_instance.BranchID
    CreatedUserID = posholdMaster_instance.CreatedUserID

    data = request.data

    VoucherNo = data['VoucherNo']
    InvoiceNo = data['InvoiceNo']
    Date = data['Date']
    LedgerID = data['LedgerID']
    PriceCategoryID = data['PriceCategoryID']
    EmployeeID = data['EmployeeID']
    SalesAccount = data['SalesAccount']
    HoldStatus = data['HoldStatus']
    CustomerName = data['CustomerName']
    Address1 = data['Address1']
    Address2 = data['Address2']
    Address3 = data['Address3']
    Notes = data['Notes']
    FinacialYearID = data['FinacialYearID']
    TotalTax = data['TotalTax']
    NetTotal = data['NetTotal']
    BillDiscount = data['BillDiscount']
    GrandTotal = data['GrandTotal']
    RoundOff = data['RoundOff']
    CashReceived = data['CashReceived']
    CashAmount = data['CashAmount']
    BankAmount = data['BankAmount']
    WarehouseID = data['WarehouseID']
    TableID = data['TableID']
    SeatNumber = data['SeatNumber']
    NoOfGuests = data['NoOfGuests']
    INOUT = data['INOUT']
    TokenNumber = data['TokenNumber']
    IsActive = data['IsActive']

    Action = "M"

    posholdMaster_instance.VoucherNo = VoucherNo
    posholdMaster_instance.InvoiceNo = InvoiceNo
    posholdMaster_instance.Date = Date
    posholdMaster_instance.LedgerID = LedgerID
    posholdMaster_instance.PriceCategoryID = PriceCategoryID
    posholdMaster_instance.EmployeeID = EmployeeID
    posholdMaster_instance.SalesAccount = SalesAccount
    posholdMaster_instance.HoldStatus = HoldStatus
    posholdMaster_instance.CustomerName = CustomerName
    posholdMaster_instance.Address1 = Address1
    posholdMaster_instance.Address2 = Address2
    posholdMaster_instance.Address3 = Address3
    posholdMaster_instance.Notes = Notes
    posholdMaster_instance.FinacialYearID = FinacialYearID
    posholdMaster_instance.TotalTax = TotalTax
    posholdMaster_instance.NetTotal = NetTotal
    posholdMaster_instance.BillDiscount = BillDiscount
    posholdMaster_instance.GrandTotal = GrandTotal
    posholdMaster_instance.RoundOff = RoundOff
    posholdMaster_instance.CashReceived = CashReceived
    posholdMaster_instance.CashAmount = CashAmount
    posholdMaster_instance.BankAmount = BankAmount
    posholdMaster_instance.WarehouseID = WarehouseID
    posholdMaster_instance.TableID = TableID
    posholdMaster_instance.SeatNumber = SeatNumber
    posholdMaster_instance.NoOfGuests = NoOfGuests
    posholdMaster_instance.INOUT = INOUT
    posholdMaster_instance.TokenNumber = TokenNumber
    posholdMaster_instance.IsActive = IsActive
    posholdMaster_instance.Action = Action

    posholdMaster_instance.save()

    POSHoldMaster_Log.objects.create(
        TransactionID=POSHoldMasterID,
        BranchID=BranchID,
        VoucherNo=VoucherNo,
        InvoiceNo=InvoiceNo,
        Date=Date,
        LedgerID=LedgerID,
        PriceCategoryID=PriceCategoryID,
        EmployeeID=EmployeeID,
        SalesAccount=SalesAccount,
        HoldStatus=HoldStatus,
        CustomerName=CustomerName,
        Address1=Address1,
        Address2=Address2,
        Address3=Address3,
        Notes=Notes,
        FinacialYearID=FinacialYearID,
        TotalTax=TotalTax,
        NetTotal=NetTotal,
        BillDiscount=BillDiscount,
        GrandTotal=GrandTotal,
        RoundOff=RoundOff,
        CashReceived=CashReceived,
        CashAmount=CashAmount,
        BankAmount=BankAmount,
        WarehouseID=WarehouseID,
        TableID=TableID,
        SeatNumber=SeatNumber,
        NoOfGuests=NoOfGuests,
        INOUT=INOUT,
        TokenNumber=TokenNumber,
        IsActive=IsActive,
        Action=Action,
        CreatedUserID=CreatedUserID,
        CreatedDate=today
    )

    posholdDetails = data["POSHoldDetails"]

    for posholdDetail in posholdDetails:

        pk = posholdDetail["id"]
        ProductID = posholdDetail['ProductID']
        Qty = posholdDetail['Qty']
        FreeQty = posholdDetail['FreeQty']
        UnitPrice = posholdDetail['UnitPrice']
        RateWithTax = posholdDetail['RateWithTax']
        CostPerPrice = posholdDetail['CostPerPrice']
        PriceListID = posholdDetail['PriceListID']
        TaxID = posholdDetail['TaxID']
        TaxType = posholdDetail['TaxType']
        DiscountPerc = posholdDetail['DiscountPerc']
        DiscountAmount = posholdDetail['DiscountAmount']
        GrossAmount = posholdDetail['GrossAmount']
        TaxableAmount = posholdDetail['TaxableAmount']
        VATPerc = posholdDetail['VATPerc']
        VATAmount = posholdDetail['VATAmount']
        SGSTPerc = posholdDetail['SGSTPerc']
        SGSTAmount = posholdDetail['SGSTAmount']
        CGSTPerc = posholdDetail['CGSTPerc']
        CGSTAmount = posholdDetail['CGSTAmount']
        IGSTPerc = posholdDetail['IGSTPerc']
        IGSTAmount = posholdDetail['IGSTAmount']
        NetAmount = posholdDetail['NetAmount']
        Flavour = posholdDetail['Flavour']

        posholdDetails_instance = POSHoldDetails.objects.get(pk=pk)

        POSHoldDetailsID = posholdDetails_instance.POSHoldDetailsID

        posholdDetails_instance.ProductID = ProductID
        posholdDetails_instance.Qty = Qty
        posholdDetails_instance.FreeQty = FreeQty
        posholdDetails_instance.UnitPrice = UnitPrice
        posholdDetails_instance.RateWithTax = RateWithTax
        posholdDetails_instance.CostPerPrice = CostPerPrice
        posholdDetails_instance.PriceListID = PriceListID
        posholdDetails_instance.TaxID = TaxID
        posholdDetails_instance.TaxType = TaxType
        posholdDetails_instance.DiscountPerc = DiscountPerc
        posholdDetails_instance.GrossAmount = GrossAmount
        posholdDetails_instance.TaxableAmount = TaxableAmount
        posholdDetails_instance.VATPerc = VATPerc
        posholdDetails_instance.VATAmount = VATAmount
        posholdDetails_instance.SGSTPerc = SGSTPerc
        posholdDetails_instance.SGSTAmount = SGSTAmount
        posholdDetails_instance.CGSTPerc = CGSTPerc
        posholdDetails_instance.CGSTAmount = CGSTAmount
        posholdDetails_instance.IGSTPerc = IGSTPerc
        posholdDetails_instance.IGSTAmount = IGSTAmount
        posholdDetails_instance.NetAmount = NetAmount
        posholdDetails_instance.Flavour = Flavour
        posholdDetails_instance.Action = Action

        posholdDetails_instance.save()

        POSHoldDetails_Log.objects.create(
            TransactionID=POSHoldDetailsID,
            BranchID=BranchID,
            POSHoldMasterID=POSHoldMasterID,
            ProductID=ProductID,
            Qty=Qty,
            FreeQty=FreeQty,
            UnitPrice=UnitPrice,
            RateWithTax=RateWithTax,
            CostPerPrice=CostPerPrice,
            PriceListID=PriceListID,
            TaxID=TaxID,
            TaxType=TaxType,
            DiscountPerc=DiscountPerc,
            DiscountAmount=DiscountAmount,
            GrossAmount=GrossAmount,
            TaxableAmount=TaxableAmount,
            VATPerc=VATPerc,
            VATAmount=VATAmount,
            SGSTPerc=SGSTPerc,
            SGSTAmount=SGSTAmount,
            CGSTPerc=CGSTPerc,
            CGSTAmount=CGSTAmount,
            IGSTPerc=IGSTPerc,
            IGSTAmount=IGSTAmount,
            NetAmount=NetAmount,
            Flavour=Flavour,
            Action=Action,
        )

    response_data = {
        "StatusCode": 6000,
        "message": "POSHold Updated Successfully!!!",
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_posholdMaster(request):
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        dummies = POSHoldDetailsDummy.objects.filter(BranchID=BranchID)

        for dummy in dummies:
            dummy.delete()

        if POSHoldMaster.objects.filter(BranchID=BranchID).exists():

            instances = POSHoldMaster.objects.filter(BranchID=BranchID)

            serialized = POSHoldMasterRestSerializer(instances, many=True)

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "POSHold Master Not Found in this BranchID!"
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
def posholdMaster(request, pk):
    instance = None
    if POSHoldMaster.objects.filter(pk=pk).exists():
        instance = POSHoldMaster.objects.get(pk=pk)
    if instance:
        serialized = POSHoldMasterRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "POSHold Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_posholdDetails(request, pk):
    instance = None
    if POSHoldDetails.objects.filter(pk=pk).exists():
        instance = POSHoldDetails.objects.get(pk=pk)
    if instance:

        POSHoldDetailsID = instance.POSHoldDetailsID
        BranchID = instance.BranchID
        POSHoldMasterID = instance.POSHoldMasterID
        ProductID = instance.ProductID
        Qty = instance.Qty
        FreeQty = instance.FreeQty
        UnitPrice = instance.UnitPrice
        RateWithTax = instance.RateWithTax
        CostPerPrice = instance.CostPerPrice
        PriceListID = instance.PriceListID
        TaxID = instance.TaxID
        TaxType = instance.TaxType
        DiscountPerc = instance.DiscountPerc
        DiscountAmount = instance.DiscountAmount
        GrossAmount = instance.GrossAmount
        TaxableAmount = instance.TaxableAmount
        VATPerc = instance.VATPerc
        VATAmount = instance.VATAmount
        SGSTPerc = instance.SGSTPerc
        SGSTAmount = instance.SGSTAmount
        CGSTPerc = instance.CGSTPerc
        CGSTAmount = instance.CGSTAmount
        IGSTPerc = instance.IGSTPerc
        IGSTAmount = instance.IGSTAmount
        NetAmount = instance.NetAmount
        Flavour = instance.Flavour
        Action = "D"

        instance.delete()

        POSHoldDetails_Log.objects.create(
            TransactionID=POSHoldDetailsID,
            BranchID=BranchID,
            POSHoldMasterID=POSHoldMasterID,
            ProductID=ProductID,
            Qty=Qty,
            FreeQty=FreeQty,
            UnitPrice=UnitPrice,
            RateWithTax=RateWithTax,
            CostPerPrice=CostPerPrice,
            PriceListID=PriceListID,
            TaxID=TaxID,
            TaxType=TaxType,
            DiscountPerc=DiscountPerc,
            DiscountAmount=DiscountAmount,
            GrossAmount=GrossAmount,
            TaxableAmount=TaxableAmount,
            VATPerc=VATPerc,
            VATAmount=VATAmount,
            SGSTPerc=SGSTPerc,
            SGSTAmount=SGSTAmount,
            CGSTPerc=CGSTPerc,
            CGSTAmount=CGSTAmount,
            IGSTPerc=IGSTPerc,
            IGSTAmount=IGSTAmount,
            NetAmount=NetAmount,
            Flavour=Flavour,
            Action=Action,
        )
        response_data = {
            "StatusCode": 6000,
            "message": "POSHold Details Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "POSHold Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_posholdMaster(request, pk):
    today = datetime.datetime.now()
    instance = None
    if POSHoldMaster.objects.filter(pk=pk).exists():
        instance = POSHoldMaster.objects.get(pk=pk)
    if instance:

        POSHoldMasterID = instance.POSHoldMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        InvoiceNo = instance.InvoiceNo
        Date = instance.Date
        LedgerID = instance.LedgerID
        PriceCategoryID = instance.PriceCategoryID
        EmployeeID = instance.EmployeeID
        SalesAccount = instance.SalesAccount
        HoldStatus = instance.HoldStatus
        CustomerName = instance.CustomerName
        Address1 = instance.Address1
        Address2 = instance.Address2
        Address3 = instance.Address3
        Notes = instance.Notes
        FinacialYearID = instance.FinacialYearID
        TotalTax = instance.TotalTax
        NetTotal = instance.NetTotal
        BillDiscount = instance.BillDiscount
        GrandTotal = instance.GrandTotal
        RoundOff = instance.RoundOff
        CashReceived = instance.CashReceived
        CashAmount = instance.CashAmount
        BankAmount = instance.BankAmount
        WarehouseID = instance.WarehouseID
        TableID = instance.TableID
        SeatNumber = instance.SeatNumber
        NoOfGuests = instance.NoOfGuests
        INOUT = instance.INOUT
        TokenNumber = instance.TokenNumber
        IsActive = instance.IsActive
        CreatedUserID = instance.CreatedUserID
        Action = "D"

        instance.delete()

        detail_instances = POSHoldDetails.objects.filter(
            POSHoldMasterID=POSHoldMasterID)

        for detail_instance in detail_instances:

            POSHoldDetailsID = detail_instance.POSHoldDetailsID
            BranchID = detail_instance.BranchID
            POSHoldMasterID = detail_instance.POSHoldMasterID
            ProductID = detail_instance.ProductID
            Qty = detail_instance.Qty
            FreeQty = detail_instance.FreeQty
            UnitPrice = detail_instance.UnitPrice
            RateWithTax = detail_instance.RateWithTax
            CostPerPrice = detail_instance.CostPerPrice
            PriceListID = detail_instance.PriceListID
            TaxID = detail_instance.TaxID
            TaxType = detail_instance.TaxType
            DiscountPerc = detail_instance.DiscountPerc
            DiscountAmount = detail_instance.DiscountAmount
            GrossAmount = detail_instance.GrossAmount
            TaxableAmount = detail_instance.TaxableAmount
            VATPerc = detail_instance.VATPerc
            VATAmount = detail_instance.VATAmount
            SGSTPerc = detail_instance.SGSTPerc
            SGSTAmount = detail_instance.SGSTAmount
            CGSTPerc = detail_instance.CGSTPerc
            CGSTAmount = detail_instance.CGSTAmount
            IGSTPerc = detail_instance.IGSTPerc
            IGSTAmount = detail_instance.IGSTAmount
            NetAmount = detail_instance.NetAmount
            Flavour = detail_instance.Flavour

            detail_instance.delete()

            POSHoldDetails_Log.objects.create(
                TransactionID=POSHoldDetailsID,
                BranchID=BranchID,
                POSHoldMasterID=POSHoldMasterID,
                ProductID=ProductID,
                Qty=Qty,
                FreeQty=FreeQty,
                UnitPrice=UnitPrice,
                RateWithTax=RateWithTax,
                CostPerPrice=CostPerPrice,
                PriceListID=PriceListID,
                TaxID=TaxID,
                TaxType=TaxType,
                DiscountPerc=DiscountPerc,
                DiscountAmount=DiscountAmount,
                GrossAmount=GrossAmount,
                TaxableAmount=TaxableAmount,
                VATPerc=VATPerc,
                VATAmount=VATAmount,
                SGSTPerc=SGSTPerc,
                SGSTAmount=SGSTAmount,
                CGSTPerc=CGSTPerc,
                CGSTAmount=CGSTAmount,
                IGSTPerc=IGSTPerc,
                IGSTAmount=IGSTAmount,
                NetAmount=NetAmount,
                Flavour=Flavour,
                Action=Action,
            )

        POSHoldMaster_Log.objects.create(
            TransactionID=POSHoldMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            InvoiceNo=InvoiceNo,
            Date=Date,
            LedgerID=LedgerID,
            PriceCategoryID=PriceCategoryID,
            EmployeeID=EmployeeID,
            SalesAccount=SalesAccount,
            HoldStatus=HoldStatus,
            CustomerName=CustomerName,
            Address1=Address1,
            Address2=Address2,
            Address3=Address3,
            Notes=Notes,
            FinacialYearID=FinacialYearID,
            TotalTax=TotalTax,
            NetTotal=NetTotal,
            BillDiscount=BillDiscount,
            GrandTotal=GrandTotal,
            RoundOff=RoundOff,
            CashReceived=CashReceived,
            CashAmount=CashAmount,
            BankAmount=BankAmount,
            WarehouseID=WarehouseID,
            TableID=TableID,
            SeatNumber=SeatNumber,
            NoOfGuests=NoOfGuests,
            INOUT=INOUT,
            TokenNumber=TokenNumber,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today
        )
        response_data = {
            "StatusCode": 6000,
            "message": "POSHold Master Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "POSHold Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)




@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_pos_role(request):
    today = datetime.datetime.now()
    data = request.data

    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    RoleName = data['RoleName']
    show_dining = data['show_dining']
    show_take_away = data['show_take_away']
    show_online = data['show_online']
    show_car = data['show_car']
    show_kitchen = data['show_kitchen']

    pos = POS_Role.objects.create(
        CompanyID=CompanyID,
        BranchID=BranchID,
        RoleName=RoleName,
        show_dining=show_dining,
        show_take_away=show_take_away,
        show_online=show_online,
        show_car=show_car,
        show_kitchen=show_kitchen,
    )

    POS_Role_Log.objects.create(
        MasterID=pos.id,
        CompanyID=CompanyID,
        BranchID=BranchID,
        RoleName=RoleName,
        show_dining=show_dining,
        show_take_away=show_take_away,
        show_online=show_online,
        show_car=show_car,
        show_kitchen=show_kitchen,
    )
    

    response_data = {
        "StatusCode": 6000,
        "message": "POS Role created Successfully!!!",
    }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_pos_user(request):
    today = datetime.datetime.now()
    data = request.data

    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    User = data['User']
    Role = data['Role']
    PinNo = data['PinNo']

    user = None
    role = None
    if Employee.objects.filter(id=User).exists():
        user = Employee.objects.get(id=User)
    if POS_Role.objects.filter(id=Role).exists():
        role = POS_Role.objects.get(id=Role)

    pos = POS_User.objects.create(
        CompanyID=CompanyID,
        BranchID=BranchID,
        User=user,
        Role=role,
        PinNo=PinNo
    )

    POS_User_log.objects.create(
        MasterID=pos.id,
        CompanyID=CompanyID,
        BranchID=BranchID,
        User=user,
        Role=role,
        PinNo=PinNo
    )
    

    response_data = {
        "StatusCode": 6000,
        "message": "POS User created Successfully!!!",
    }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def generate_pos_pin(request):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    
    PinNo = get_pin_no(CompanyID,BranchID)
    

    response_data = {
        "StatusCode": 6000,
        "PinNo": PinNo,
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def list_pos_role(request):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    
    if POS_Role.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        role_instances = POS_Role.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
        serialized = POS_Role_Serializer(role_instances,many=True)
    
        response_data = {
            "StatusCode": 6000,
            "data" : serialized.data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "no data",
        }

        return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def list_pos_users(request):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    
    if POS_User.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        user_instances = POS_User.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
        serialized = POS_User_Serializer(user_instances,many=True)
    
        response_data = {
            "StatusCode": 6000,
            "data" : serialized.data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "no data",
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def single_pos_user(request, pk):
    today = datetime.datetime.now()
    instance = None
    if POS_User.objects.filter(pk=pk).exists():
        instance = POS_User.objects.get(pk=pk)
        serialized = POS_User_Serializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Role Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def single_pos_role(request, pk):
    today = datetime.datetime.now()
    instance = None
    if POS_Role.objects.filter(pk=pk).exists():
        instance = POS_Role.objects.get(pk=pk)
        serialized = POS_Role_Serializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Role Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_pos_user(request, pk):
    today = datetime.datetime.now()
    instance = None
    if POS_User.objects.filter(pk=pk).exists():
        instance = POS_User.objects.get(pk=pk)
        CompanyID = instance.CompanyID
        BranchID = instance.BranchID
        user = instance.User
        role = instance.Role
        PinNo = instance.PinNo
        
        POS_User_log.objects.create(
            MasterID=instance.id,
            CompanyID=CompanyID,
            BranchID=BranchID,
            User=user,
            Role=role,
            PinNo=PinNo
        )
        instance.delete()
        response_data = {
            "StatusCode": 6000,
            "message": "User Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "User Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_pos_role(request, pk):
    today = datetime.datetime.now()
    instance = None
    if POS_Role.objects.filter(pk=pk).exists():
        instance = POS_Role.objects.get(pk=pk)
        CompanyID = instance.CompanyID
        BranchID = instance.BranchID
        RoleName = instance.RoleName
        show_dining = instance.show_dining
        show_take_away = instance.show_take_away
        show_online = instance.show_online
        show_car = instance.show_car
        show_kitchen = instance.show_kitchen

        if not POS_User.objects.filter(CompanyID=CompanyID,BranchID=BranchID,Role=instance).exists():

            POS_Role_Log.objects.create(
                MasterID=pk,
                CompanyID=CompanyID,
                BranchID=BranchID,
                RoleName=RoleName,
                show_dining=show_dining,
                show_take_away=show_take_away,
                show_online=show_online,
                show_car=show_car,
                show_kitchen=show_kitchen,
            )
            instance.delete()
            response_data = {
                "StatusCode": 6000,
                "message": "Role Deleted Successfully!"
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Role cant't be deleted ,User already exist with this role!"
            }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Role Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_pos_role(request,pk):
    today = datetime.datetime.now()
    data = request.data

    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    RoleName = data['RoleName']
    show_dining = data['show_dining']
    show_take_away = data['show_take_away']
    show_online = data['show_online']
    show_car = data['show_car']
    show_kitchen = data['show_kitchen']

    if POS_Role.objects.filter(pk=pk).exists():
        instance = POS_Role.objects.get(pk=pk)
        instance.RoleName = RoleName
        instance.show_dining = show_dining
        instance.show_take_away = show_take_away
        instance.show_online = show_online
        instance.show_car = show_car
        instance.show_kitchen = show_kitchen
        instance.save()
        POS_Role_Log.objects.create(
            MasterID=instance.id,
            CompanyID=CompanyID,
            BranchID=BranchID,
            RoleName=RoleName,
            show_dining=show_dining,
            show_take_away=show_take_away,
            show_online=show_online,
            show_car=show_car,
            show_kitchen=show_kitchen,
        )
    

        response_data = {
            "StatusCode": 6000,
            "message": "POS Role Updated Successfully!!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "No Data",
        }

        return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_pos_user(request,pk):
    today = datetime.datetime.now()
    data = request.data

    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    User = data['User']
    Role = data['Role']
    PinNo = data['PinNo']

    user = None
    role = None
    if Employee.objects.filter(id=User).exists():
        user = Employee.objects.get(id=User)
    if POS_Role.objects.filter(id=Role).exists():
        role = POS_Role.objects.get(id=Role)

    if POS_User.objects.filter(pk=pk).exists():
        instance = POS_User.objects.get(pk=pk)
        instance.User = user
        instance.Role = role
        instance.PinNo = PinNo
        instance.save()
        POS_User_log.objects.create(
            MasterID=instance.id,
            CompanyID=CompanyID,
            BranchID=BranchID,
            User=user,
            Role=role,
            PinNo=PinNo
        )
    
        response_data = {
            "StatusCode": 6000,
            "message": "POS User Updated Successfully!!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "No Data",
        }

        return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def validate_user_pin(request):
    today = datetime.datetime.now()
    data = request.data

    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    PinNo = data['PinNo']

    if POS_User.objects.filter(CompanyID=CompanyID,BranchID=BranchID,PinNo=PinNo).exists():
        instance = POS_User.objects.filter(CompanyID=CompanyID,BranchID=BranchID,PinNo=PinNo).first()
        user = instance.User
        role = instance.Role 
        
        response_data = {
            "StatusCode": 6000,
            "user_id":user.id,
            "user_name":user.FirstName,
            "role":role.id,
            "role_name": role.RoleName,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "No Data",
        }

        return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def pos_table_create(request):
    today = datetime.datetime.now()
    data = request.data

    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    tables = data['tables']
    Deleted_cards = data['Deleted_cards']

    is_createOK = False
    if Deleted_cards:
        is_createOK = True
        if POS_Table.objects.filter(CompanyID=CompanyID,BranchID=BranchID,id__in=Deleted_cards).exists():
            POS_Table.objects.filter(CompanyID=CompanyID,BranchID=BranchID,id__in=Deleted_cards).delete()
            response_data = {
                "StatusCode": 6000,
            }

    if tables:
        is_createOK = True
        position = 1
        for i in tables:
            count = 0
            if not POS_Table.objects.filter(CompanyID=CompanyID,BranchID=BranchID,id=i['id']).exists():
                if not POS_Table.objects.filter(CompanyID=CompanyID,BranchID=BranchID,TableName=i['title']).exists():
                    priceCategory = None
                    if(i['priceid']):
                        if PriceCategory.objects.filter(id=i['priceid']).exists():
                            priceCategory = PriceCategory.objects.get(id=i['priceid'])

                    pos = POS_Table.objects.create(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        TableName=i['title'],
                        IsActive=i['IsActive'],
                        PriceCategory=priceCategory,
                        Position=position,
                    )

                    POS_Table_log.objects.create(
                        MasterID=pos.id,
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        TableName=i['title'],
                        IsActive=i['IsActive'],
                        PriceCategory=priceCategory,
                        Position=position,
                    )

                    response_data = {
                        "StatusCode": 6000,
                    }

                else:
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Table Name already exist",
                        "name": i['title']
                    }

            else:
                table_instances = POS_Table.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exclude(id=i['id'])
                if not table_instances.filter(TableName=i['title']).exclude(id=i['id']):
                    priceCategory = None
                    if(i['priceid']):
                        if PriceCategory.objects.filter(id=i['priceid']).exists():
                            priceCategory = PriceCategory.objects.get(id=i['priceid'])
                    table_instances = POS_Table.objects.get(CompanyID=CompanyID,BranchID=BranchID,id=i['id'])
                    table_instances.TableName=i['title']
                    table_instances.IsActive=i['IsActive']
                    table_instances.PriceCategory=priceCategory
                    table_instances.Position=position
                    table_instances.save()

                    response_data = {
                        "StatusCode": 6000,
                    }

                else:
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Table Name already exist",
                        "name": i['title']
                    }
            position += 1

    if is_createOK:
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "No Data",
        }

        return Response(response_data, status=status.HTTP_200_OK)   


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def pos_table_list(request):
    today = datetime.datetime.now()
    data = request.data

    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    try:
        pos_type = data['type']
    except:
        pos_type = "admin"

    is_ok = False
    Dining = []
    Online = []
    TakeAway = []
    Car = []
    reason_data = []
    if POS_Table.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        if pos_type == "admin":
            pos_instances = POS_Table.objects.filter(CompanyID=CompanyID,BranchID=BranchID).order_by('Position')
        else:
            pos_instances = POS_Table.objects.filter(CompanyID=CompanyID,BranchID=BranchID,IsActive=True).order_by('Position')
        serialized = POS_Table_Serializer(pos_instances,many=True)
        Dining = serialized.data
        is_ok = True
    if SalesOrderMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        pos_order_instances = SalesOrderMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
        Orderserialized = POS_Order_Serializer(pos_order_instances,many=True)
        orderdDict = Orderserialized.data
        jsnDatas = convertOrderdDict(orderdDict)
        
        for i in jsnDatas:
            Type = i['Type']
            statuses = ["Delivered","Cancelled"]
            if Type == "Online" and i['Status'] not in statuses:
                online_datas = {
                    "SalesOrderID": i['SalesOrderID'],
                    "CustomerName": i['CustomerName'],
                    "TokenNumber": i['TokenNumber'],
                    "Phone": i['Phone'],
                    "Status": i['Status'],
                    "SalesOrderGrandTotal": i['SalesOrderGrandTotal'],
                    "OrderTime": i['OrderTime'],
                }
                Online.append(online_datas)
            elif Type == "TakeAway" and i['Status'] not in statuses:
                take_away_datas = {
                    "SalesOrderID": i['SalesOrderID'],
                    "SalesID": i['SalesID'],
                    "CustomerName": i['CustomerName'],
                    "TokenNumber": i['TokenNumber'],
                    "Phone": i['Phone'],
                    "Status": i['Status'],
                    "SalesOrderGrandTotal": i['SalesOrderGrandTotal'],
                    "OrderTime": i['OrderTime'],
                }
                TakeAway.append(take_away_datas)
            elif Type == "Car" and i['Status'] not in statuses:
                car_datas = {
                    "SalesOrderID": i['SalesOrderID'],
                    "CustomerName": i['CustomerName'],
                    "TokenNumber": i['TokenNumber'],
                    "Phone": i['Phone'],
                    "Status": i['Status'],
                    "SalesOrderGrandTotal": i['SalesOrderGrandTotal'],
                    "OrderTime": i['OrderTime'],
                }
                Car.append(car_datas)
            is_ok = True

        if CancelReasons.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
            instance = CancelReasons.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
            reason_serialized = OrderReason_Serializer(
                instance,many=True, context={"CompanyID": CompanyID})
            reason_data = reason_serialized.data

        
    if is_ok:
        DiningStatusCode = 6000
        OnlineStatusCode = 6000
        TakeAwayStatusCode = 6000
        CarStatusCode = 6000
        if not Dining:
            DiningStatusCode = 6001
        if not Online:
            OnlineStatusCode = 6001
        if not TakeAway:
            TakeAwayStatusCode = 6001
        if not Car:
            CarStatusCode = 6001
        response_data = {
            "StatusCode": 6000,
            "data" : Dining,
            "Online" : Online,
            "TakeAway" : TakeAway,
            "Car" : Car,
            "DiningStatusCode":DiningStatusCode,
            "OnlineStatusCode":OnlineStatusCode,
            "TakeAwayStatusCode":TakeAwayStatusCode,
            "CarStatusCode":CarStatusCode,
            "Reasons": reason_data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "No data",
            "data" : []
        }

        return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def pos_product_group_list(request):
    today = datetime.datetime.now()
    data = request.data

    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']

    if ProductGroup.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        instances = ProductGroup.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
        serialized = POS_ProductGroup_Serializer(instances,many=True)

        response_data = {
            "StatusCode": 6000,
            "data" : serialized.data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "No data",
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def pos_product_list(request):
    today = datetime.datetime.now()
    data = request.data

    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    PriceRounding = data['PriceRounding']

    GroupID = data['GroupID']

    if Product.objects.filter(CompanyID=CompanyID,BranchID=BranchID,ProductGroupID=GroupID).exists():
        instances = Product.objects.filter(CompanyID=CompanyID,BranchID=BranchID,ProductGroupID=GroupID)
        serialized = POS_Product_Serializer(instances,many=True,context={
                                                       "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding})

        response_data = {
            "StatusCode": 6000,
            "data" : serialized.data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "No data",
        }

        return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def create_pos_salesOrder(request):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            CreatedUserID = data['CreatedUserID']

            today = datetime.datetime.now()
            BranchID = data['BranchID']
            # VoucherNo = data['VoucherNo']
            Date = data['Date']
            DeliveryDate = data['DeliveryDate']
            LedgerID = data['LedgerID']
            PriceCategoryID = data['PriceCategoryID']
            CustomerName = data['CustomerName']
            Address1 = data['Address1']
            Address2 = data['Address2']
            Notes = data['Notes']
            FinacialYearID = data['FinacialYearID']
            TotalTax = data['TotalTax']
            NetTotal = data['NetTotal']
            BillDiscAmt = data['BillDiscAmt']
            BillDiscPercent = data['BillDiscPercent']
            GrandTotal = data['GrandTotal']
            RoundOff = data['RoundOff']
            IsActive = data['IsActive']
            IsInvoiced = data['IsInvoiced']
            TaxID = data['TaxID']
            TaxType = data['TaxType']
            VATAmount = data['VATAmount']
            SGSTAmount = data['SGSTAmount']
            CGSTAmount = data['CGSTAmount']
            IGSTAmount = data['IGSTAmount']
            TAX1Amount = data['TAX1Amount']
            TAX2Amount = data['TAX2Amount']
            TAX3Amount = data['TAX3Amount']
            TotalGrossAmt = data['TotalGrossAmt']

            Action = "A"

            try:
                ShippingCharge = data['ShippingCharge']
            except:
                ShippingCharge = 0

            try:
                shipping_tax_amount = data['shipping_tax_amount']
            except:
                shipping_tax_amount = 0

            try:
                TaxTypeID = data['TaxTypeID']
            except:
                TaxTypeID = ""

            try:
                SAC = data['SAC']
            except:
                SAC = ""

            try:
                SalesTax = data['SalesTax']
            except:
                SalesTax = 0

            try:
                Country_of_Supply = data['Country_of_Supply']
            except:
                Country_of_Supply = ""

            try:
                State_of_Supply = data['State_of_Supply']
            except:
                State_of_Supply = ""

            try:
                GST_Treatment = data['GST_Treatment']
            except:
                GST_Treatment = ""

            try:
                OrderTime = data['OrderTime']
            except:
                OrderTime = ""

            VoucherType="SO"

            # VoucherNo Updated
            VoucherNo = get_VoucherNoForPOS(CompanyID,BranchID,CreatedUserID,"SO")

            try:
                PreFix = data['PreFix']
            except:
                PreFix = "SO"

            try:
                Seperator = data['Seperator']
            except:
                Seperator = ""

            # try:
            #     InvoiceNo = data['InvoiceNo']
            # except:
            #     InvoiceNo = 1

            InvoiceNo = get_InvoiceNo(VoucherNo)

            try:
                Type = data['Type']
            except:
                Type = ""

            try:
                TokenNumber = data['TokenNumber']
            except:
                TokenNumber = ""

            try:
                DeliveryTime = data['DeliveryTime']
            except:
                DeliveryTime = ""

            try:
                Phone = data['Phone']
            except:
                Phone = ""

            try:
                Table = data['Table']
            except:
                Table = None

            table_ins = None
            if Type == "Dining" and Table:
                if POS_Table.objects.filter(CompanyID=CompanyID,BranchID=BranchID,id=Table).exists():
                    table_ins = POS_Table.objects.get(CompanyID=CompanyID,BranchID=BranchID,id=Table)
                    table_ins.Status = "Ordered"
                    table_ins.save()

            # checking voucher number already exist
            VoucherNoLow = VoucherNo.lower()
            is_voucherExist = False
            insts = SalesOrderMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
            if insts:
                for i in insts:
                    voucher_no = i.VoucherNo
                    voucherNo = voucher_no.lower()
                    if VoucherNoLow == voucherNo:
                        is_voucherExist = True

            check_VoucherNoAutoGenerate = False
            is_SaleOrderOK = True

            if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="VoucherNoAutoGenerate").exists():
                check_VoucherNoAutoGenerate = GeneralSettings.objects.get(
                    CompanyID=CompanyID, SettingsType="VoucherNoAutoGenerate").SettingsValue

            if is_voucherExist == True and check_VoucherNoAutoGenerate == "True":
                VoucherNo = get_Genrate_VoucherNo(
                    SalesOrderMaster, BranchID, CompanyID, "SO")
                is_SaleOrderOK = True
            elif is_voucherExist == False:
                is_SaleOrderOK = True
            else:
                is_SaleOrderOK = False

            if is_SaleOrderOK:
                update_voucher_table(CompanyID,CreatedUserID,VoucherType,PreFix,Seperator, InvoiceNo)
                SalesOrderMasterID = order_master_id(
                    SalesOrderMaster, BranchID, CompanyID)

                SalesOrderMaster_Log.objects.create(
                    CompanyID=CompanyID,
                    TransactionID=SalesOrderMasterID,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    Date=Date,
                    DeliveryDate=DeliveryDate,
                    LedgerID=LedgerID,
                    PriceCategoryID=PriceCategoryID,
                    CustomerName=CustomerName,
                    Address1=Address1,
                    Address2=Address2,
                    Notes=Notes,
                    FinacialYearID=FinacialYearID,
                    TotalTax=TotalTax,
                    TotalGrossAmt=TotalGrossAmt,
                    NetTotal=NetTotal,
                    BillDiscAmt=BillDiscAmt,
                    BillDiscPercent=BillDiscPercent,
                    GrandTotal=GrandTotal,
                    RoundOff=RoundOff,
                    TaxID=TaxID,
                    TaxType=TaxType,
                    IsActive=IsActive,
                    IsInvoiced=IsInvoiced,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    VATAmount=VATAmount,
                    SGSTAmount=SGSTAmount,
                    CGSTAmount=CGSTAmount,
                    IGSTAmount=IGSTAmount,
                    TAX1Amount=TAX1Amount,
                    TAX2Amount=TAX2Amount,
                    TAX3Amount=TAX3Amount,
                    ShippingCharge=ShippingCharge,
                    shipping_tax_amount=shipping_tax_amount,
                    TaxTypeID=TaxTypeID,
                    SAC=SAC,
                    SalesTax=SalesTax,
                    Country_of_Supply=Country_of_Supply,
                    State_of_Supply=State_of_Supply,
                    GST_Treatment=GST_Treatment,
                    Table=table_ins,
                    Type=Type,
                    TokenNumber=TokenNumber,
                    DeliveryTime=DeliveryTime,
                    Status="Ordered",
                    Phone=Phone,
                    OrderTime=OrderTime,
                )

                instance = SalesOrderMaster.objects.create(
                    CompanyID=CompanyID,
                    SalesOrderMasterID=SalesOrderMasterID,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    Date=Date,
                    DeliveryDate=DeliveryDate,
                    LedgerID=LedgerID,
                    PriceCategoryID=PriceCategoryID,
                    CustomerName=CustomerName,
                    Address1=Address1,
                    Address2=Address2,
                    Notes=Notes,
                    FinacialYearID=FinacialYearID,
                    TotalGrossAmt=TotalGrossAmt,
                    TotalTax=TotalTax,
                    NetTotal=NetTotal,
                    BillDiscAmt=BillDiscAmt,
                    BillDiscPercent=BillDiscPercent,
                    GrandTotal=GrandTotal,
                    RoundOff=RoundOff,
                    TaxID=TaxID,
                    TaxType=TaxType,
                    IsActive=IsActive,
                    IsInvoiced=IsInvoiced,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    VATAmount=VATAmount,
                    SGSTAmount=SGSTAmount,
                    CGSTAmount=CGSTAmount,
                    IGSTAmount=IGSTAmount,
                    TAX1Amount=TAX1Amount,
                    TAX2Amount=TAX2Amount,
                    TAX3Amount=TAX3Amount,
                    ShippingCharge=ShippingCharge,
                    shipping_tax_amount=shipping_tax_amount,
                    TaxTypeID=TaxTypeID,
                    SAC=SAC,
                    SalesTax=SalesTax,
                    Country_of_Supply=Country_of_Supply,
                    State_of_Supply=State_of_Supply,
                    GST_Treatment=GST_Treatment,
                    Table=table_ins,
                    Type=Type,
                    TokenNumber=TokenNumber,
                    DeliveryTime=DeliveryTime,
                    Status="Ordered",
                    Phone=Phone,
                    OrderTime=OrderTime
                )

                saleOrdersDetails = data["saleOrdersDetails"]

                for saleOrdersDetail in saleOrdersDetails:

                    ProductID = saleOrdersDetail['ProductID']
                    if ProductID:
                        Qty = saleOrdersDetail['Qty']
                        FreeQty = 0
                        UnitPrice = saleOrdersDetail['UnitPrice']
                        RateWithTax = saleOrdersDetail['RateWithTax']
                        PriceListID = saleOrdersDetail['PriceListID']
                        DiscountPerc = 0
                        DiscountAmount = 0
                        GrossAmount = saleOrdersDetail['GrossAmount']
                        TaxableAmount = saleOrdersDetail['TaxableAmount']
                        VATPerc = saleOrdersDetail['VATPerc']
                        VATAmount = saleOrdersDetail['VATAmount']
                        SGSTPerc = saleOrdersDetail['SGSTPerc']
                        SGSTAmount = saleOrdersDetail['SGSTAmount']
                        CGSTPerc = saleOrdersDetail['CGSTPerc']
                        CGSTAmount = saleOrdersDetail['CGSTAmount']
                        IGSTPerc = saleOrdersDetail['IGSTPerc']
                        IGSTAmount = saleOrdersDetail['IGSTAmount']
                        TAX1Perc = 0
                        TAX1Amount = 0
                        TAX2Perc = 0
                        TAX2Amount = 0
                        TAX3Perc = 0
                        TAX3Amount = 0
                        KFCAmount = 0
                        NetAmount = saleOrdersDetail['NetAmount']
                        InclusivePrice = saleOrdersDetail['InclusivePrice']
                        BatchCode = 0

                        try:
                            SerialNos = saleOrdersDetail['SerialNos']
                        except:
                            SerialNos = []

                        try:
                            Description = saleOrdersDetail['Description']
                        except:
                            Description = ""

                        try:
                            ProductTaxID = saleOrdersDetail['ProductTaxID']
                        except:
                            ProductTaxID = ""

                        SalesOrderDetailsID = order_id(
                            SalesOrderDetails, BranchID, CompanyID)

                        if SerialNos:
                            for sn in SerialNos:
                                try:
                                    SerialNo = sn['SerialNo']
                                except:
                                    SerialNo = ""
                                try:
                                    ItemCode = sn['ItemCode']
                                except:
                                    ItemCode = ""
                                SerialNumbers.objects.create(
                                    VoucherType="SO",
                                    CompanyID=CompanyID,
                                    SerialNo=SerialNo,
                                    ItemCode=ItemCode,
                                    SalesMasterID=SalesOrderMasterID,
                                    SalesDetailsID=SalesOrderDetailsID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CreatedUserID=CreatedUserID,
                                )

                        log_instance = SalesOrderDetails_Log.objects.create(
                            CompanyID=CompanyID,
                            TransactionID=SalesOrderDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            SalesOrderMasterID=SalesOrderMasterID,
                            ProductID=ProductID,
                            Qty=Qty,
                            FreeQty=FreeQty,
                            UnitPrice=UnitPrice,
                            RateWithTax=RateWithTax,
                            PriceListID=PriceListID,
                            DiscountPerc=DiscountPerc,
                            DiscountAmount=DiscountAmount,
                            GrossAmount=GrossAmount,
                            TaxableAmount=TaxableAmount,
                            VATPerc=VATPerc,
                            VATAmount=VATAmount,
                            SGSTPerc=SGSTPerc,
                            SGSTAmount=SGSTAmount,
                            CGSTPerc=CGSTPerc,
                            CGSTAmount=CGSTAmount,
                            IGSTPerc=IGSTPerc,
                            IGSTAmount=IGSTAmount,
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            KFCAmount=KFCAmount,
                            NetAmount=NetAmount,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            InclusivePrice=InclusivePrice,
                            BatchCode=BatchCode,
                            ProductTaxID=ProductTaxID
                        )

                        SalesOrderDetails.objects.create(
                            CompanyID=CompanyID,
                            SalesOrderDetailsID=SalesOrderDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            SalesOrderMasterID=SalesOrderMasterID,
                            ProductID=ProductID,
                            Qty=Qty,
                            FreeQty=FreeQty,
                            UnitPrice=UnitPrice,
                            RateWithTax=RateWithTax,
                            PriceListID=PriceListID,
                            DiscountPerc=DiscountPerc,
                            DiscountAmount=DiscountAmount,
                            GrossAmount=GrossAmount,
                            TaxableAmount=TaxableAmount,
                            VATPerc=VATPerc,
                            VATAmount=VATAmount,
                            SGSTPerc=SGSTPerc,
                            SGSTAmount=SGSTAmount,
                            CGSTPerc=CGSTPerc,
                            CGSTAmount=CGSTAmount,
                            IGSTPerc=IGSTPerc,
                            IGSTAmount=IGSTAmount,
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            KFCAmount=KFCAmount,
                            NetAmount=NetAmount,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            InclusivePrice=InclusivePrice,
                            BatchCode=BatchCode,
                            LogID=log_instance.ID,
                            ProductTaxID=ProductTaxID
                        )

                #request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sale Orders',
                #              'Create', 'Sale Orders created successfully.', 'Sale Orders saved successfully.')

                response_data = {
                    "StatusCode": 6000,
                    "message": "Sale Orders created Successfully!!!",
                    "OrderID" : instance.id
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Sale Orders',
                             'Create', 'Sale Orders created Failed.', 'VoucherNo already exist!')
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

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Sales Order',
                         'Create', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def edit_pos_sales_order(request, pk):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            CreatedUserID = data['CreatedUserID']

            today = datetime.datetime.now()
            BranchID = data['BranchID']
            # VoucherNo = data['VoucherNo']
            Date = data['Date']
            DeliveryDate = data['DeliveryDate']
            LedgerID = data['LedgerID']
            PriceCategoryID = data['PriceCategoryID']
            CustomerName = data['CustomerName']
            Address1 = data['Address1']
            Address2 = data['Address2']
            Notes = data['Notes']
            FinacialYearID = data['FinacialYearID']
            TotalTax = data['TotalTax']
            NetTotal = data['NetTotal']
            BillDiscAmt = data['BillDiscAmt']
            BillDiscPercent = data['BillDiscPercent']
            GrandTotal = data['GrandTotal']
            RoundOff = data['RoundOff']
            IsActive = data['IsActive']
            IsInvoiced = data['IsInvoiced']
            TaxID = data['TaxID']
            TaxType = data['TaxType']
            VATAmount = data['VATAmount']
            SGSTAmount = data['SGSTAmount']
            CGSTAmount = data['CGSTAmount']
            IGSTAmount = data['IGSTAmount']
            TAX1Amount = data['TAX1Amount']
            TAX2Amount = data['TAX2Amount']
            TAX3Amount = data['TAX3Amount']

            salesOrderMaster_instance = SalesOrderMaster.objects.get(
                CompanyID=CompanyID, pk=pk)

            SalesOrderMasterID = salesOrderMaster_instance.SalesOrderMasterID
            BranchID = salesOrderMaster_instance.BranchID
            VoucherNo = salesOrderMaster_instance.VoucherNo

            Action = "A"

            try:
                ShippingCharge = data['ShippingCharge']
            except:
                ShippingCharge = 0

            try:
                shipping_tax_amount = data['shipping_tax_amount']
            except:
                shipping_tax_amount = 0

            try:
                TaxTypeID = data['TaxTypeID']
            except:
                TaxTypeID = ""

            try:
                SAC = data['SAC']
            except:
                SAC = ""

            try:
                SalesTax = data['SalesTax']
            except:
                SalesTax = 0

            try:
                Country_of_Supply = data['Country_of_Supply']
            except:
                Country_of_Supply = ""

            try:
                State_of_Supply = data['State_of_Supply']
            except:
                State_of_Supply = ""

            try:
                GST_Treatment = data['GST_Treatment']
            except:
                GST_Treatment = ""

            try:
                Phone = data['Phone']
            except:
                Phone = ""

            VoucherType="SO"

            SalesOrderMaster_Log.objects.create(
                CompanyID=CompanyID,
                TransactionID=SalesOrderMasterID,
                BranchID=BranchID,
                Action=Action,
                VoucherNo=VoucherNo,
                DeliveryDate=DeliveryDate,
                Date=Date,
                LedgerID=LedgerID,
                PriceCategoryID=PriceCategoryID,
                CustomerName=CustomerName,
                Address1=Address1,
                Address2=Address2,
                Notes=Notes,
                FinacialYearID=FinacialYearID,
                TotalTax=TotalTax,
                NetTotal=NetTotal,
                BillDiscAmt=BillDiscAmt,
                BillDiscPercent=BillDiscPercent,
                GrandTotal=GrandTotal,
                RoundOff=RoundOff,
                IsActive=IsActive,
                IsInvoiced=IsInvoiced,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                TaxID=TaxID,
                TaxType=TaxType,
                VATAmount=VATAmount,
                SGSTAmount=SGSTAmount,
                CGSTAmount=CGSTAmount,
                IGSTAmount=IGSTAmount,
                TAX1Amount=TAX1Amount,
                TAX2Amount=TAX2Amount,
                TAX3Amount=TAX3Amount,
                ShippingCharge=ShippingCharge,
                shipping_tax_amount=shipping_tax_amount,
                TaxTypeID=TaxTypeID,
                SAC=SAC,
                SalesTax=SalesTax,
                Country_of_Supply=Country_of_Supply,
                State_of_Supply=State_of_Supply,
                GST_Treatment=GST_Treatment,
                Phone=Phone
            )

            salesOrderMaster_instance.Date = Date
            salesOrderMaster_instance.DeliveryDate = DeliveryDate
            salesOrderMaster_instance.LedgerID = LedgerID
            salesOrderMaster_instance.PriceCategoryID = PriceCategoryID
            salesOrderMaster_instance.CustomerName = CustomerName
            salesOrderMaster_instance.Address1 = Address1
            salesOrderMaster_instance.Address2 = Address2
            salesOrderMaster_instance.Notes = Notes
            salesOrderMaster_instance.FinacialYearID = FinacialYearID
            salesOrderMaster_instance.TotalTax = TotalTax
            salesOrderMaster_instance.NetTotal = NetTotal
            salesOrderMaster_instance.BillDiscAmt = BillDiscAmt
            salesOrderMaster_instance.BillDiscPercent = BillDiscPercent
            salesOrderMaster_instance.GrandTotal = GrandTotal
            salesOrderMaster_instance.RoundOff = RoundOff
            salesOrderMaster_instance.IsActive = IsActive
            salesOrderMaster_instance.IsInvoiced = IsInvoiced
            salesOrderMaster_instance.Action = Action
            salesOrderMaster_instance.UpdatedDate = today
            salesOrderMaster_instance.CreatedUserID = CreatedUserID
            salesOrderMaster_instance.TaxID = TaxID
            salesOrderMaster_instance.TaxType = TaxType
            salesOrderMaster_instance.CompanyID = CompanyID
            salesOrderMaster_instance.VATAmount = VATAmount
            salesOrderMaster_instance.SGSTAmount = SGSTAmount
            salesOrderMaster_instance.CGSTAmount = CGSTAmount
            salesOrderMaster_instance.IGSTAmount = IGSTAmount
            salesOrderMaster_instance.TAX1Amount = TAX1Amount
            salesOrderMaster_instance.TAX2Amount = TAX2Amount
            salesOrderMaster_instance.TAX3Amount = TAX3Amount
            salesOrderMaster_instance.ShippingCharge = ShippingCharge
            salesOrderMaster_instance.shipping_tax_amount = shipping_tax_amount
            salesOrderMaster_instance.TaxTypeID = TaxTypeID
            salesOrderMaster_instance.SAC = SAC
            salesOrderMaster_instance.SalesTax = SalesTax
            salesOrderMaster_instance.Country_of_Supply = Country_of_Supply
            salesOrderMaster_instance.State_of_Supply = State_of_Supply
            salesOrderMaster_instance.GST_Treatment = GST_Treatment
            salesOrderMaster_instance.Phone = Phone
            salesOrderMaster_instance.save()

            deleted_datas = data["deleted_data"]
            if deleted_datas:
                for deleted_Data in deleted_datas:
                    deleted_pk = deleted_Data['unq_id']

                    if not deleted_pk == '' or not deleted_pk == 0:
                        if SalesOrderDetails.objects.filter(CompanyID=CompanyID, pk=deleted_pk).exists():
                            deleted_detail = SalesOrderDetails.objects.filter(
                                CompanyID=CompanyID, pk=deleted_pk)
                            deleted_detail.delete()

            salesOrderDetails = data["saleOrdersDetails"]
            for salesOrderDetail in salesOrderDetails:
                unq_id = salesOrderDetail['unq_id']
                ProductID = salesOrderDetail['ProductID']
                if ProductID:
                    Qty = salesOrderDetail['Qty']
                    FreeQty = salesOrderDetail['FreeQty']
                    UnitPrice = salesOrderDetail['UnitPrice']
                    RateWithTax = salesOrderDetail['RateWithTax']
                    PriceListID = salesOrderDetail['PriceListID']
                    DiscountPerc = salesOrderDetail['DiscountPerc']
                    DiscountAmount = salesOrderDetail['DiscountAmount']
                    GrossAmount = salesOrderDetail['GrossAmount']
                    TaxableAmount = salesOrderDetail['TaxableAmount']
                    VATPerc = salesOrderDetail['VATPerc']
                    VATAmount = salesOrderDetail['VATAmount']
                    SGSTPerc = salesOrderDetail['SGSTPerc']
                    SGSTAmount = salesOrderDetail['SGSTAmount']
                    CGSTPerc = salesOrderDetail['CGSTPerc']
                    CGSTAmount = salesOrderDetail['CGSTAmount']
                    IGSTPerc = salesOrderDetail['IGSTPerc']
                    IGSTAmount = salesOrderDetail['IGSTAmount']
                    TAX1Perc = salesOrderDetail['TAX1Perc']
                    TAX1Amount = salesOrderDetail['TAX1Amount']
                    TAX2Perc = salesOrderDetail['TAX2Perc']
                    TAX2Amount = salesOrderDetail['TAX2Amount']
                    TAX3Perc = salesOrderDetail['TAX3Perc']
                    TAX3Amount = salesOrderDetail['TAX3Amount']
                    KFCAmount = salesOrderDetail['KFCAmount']
                    NetAmount = salesOrderDetail['NetAmount']
                    BatchCode = salesOrderDetail['BatchCode']
                    InclusivePrice = salesOrderDetail['InclusivePrice']
                    detailID = salesOrderDetail['detailID']

                    try:
                        SerialNos = salesOrderDetail['SerialNos']
                    except:
                        SerialNos = []

                    try:
                        Description = salesOrderDetail['Description']
                    except:
                        Description = ""

                    try:
                        ProductTaxID = salesOrderDetail['ProductTaxID']
                    except:
                        ProductTaxID = ""


                    if detailID == 0:
                        Action = "M"
                        salesDetail_instance = SalesOrderDetails.objects.get(
                            CompanyID=CompanyID, pk=unq_id)
                        SalesOrderDetailsID = salesDetail_instance.SalesOrderDetailsID

                        log_instance = SalesOrderDetails_Log.objects.create(
                            CompanyID=CompanyID,
                            TransactionID=SalesOrderDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            SalesOrderMasterID=SalesOrderMasterID,
                            ProductID=ProductID,
                            Qty=Qty,
                            FreeQty=FreeQty,
                            UnitPrice=UnitPrice,
                            InclusivePrice=InclusivePrice,
                            BatchCode=BatchCode,
                            RateWithTax=RateWithTax,
                            PriceListID=PriceListID,
                            # TaxID=TaxID,
                            # TaxType=TaxType,
                            DiscountPerc=DiscountPerc,
                            DiscountAmount=DiscountAmount,
                            GrossAmount=GrossAmount,
                            TaxableAmount=TaxableAmount,
                            VATPerc=VATPerc,
                            VATAmount=VATAmount,
                            SGSTPerc=SGSTPerc,
                            SGSTAmount=SGSTAmount,
                            CGSTPerc=CGSTPerc,
                            CGSTAmount=CGSTAmount,
                            IGSTPerc=IGSTPerc,
                            IGSTAmount=IGSTAmount,
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            KFCAmount=KFCAmount,
                            NetAmount=NetAmount,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            ProductTaxID=ProductTaxID
                        )

                        salesDetail_instance.ProductID = ProductID
                        salesDetail_instance.Qty = Qty
                        salesDetail_instance.FreeQty = FreeQty
                        salesDetail_instance.UnitPrice = UnitPrice
                        salesDetail_instance.InclusivePrice = InclusivePrice
                        salesDetail_instance.RateWithTax = RateWithTax
                        salesDetail_instance.PriceListID = PriceListID
                        salesDetail_instance.DiscountPerc = DiscountPerc
                        salesDetail_instance.DiscountAmount = DiscountAmount
                        # salesDetail_instance.AddlDiscPerc = AddlDiscPerc
                        # salesDetail_instance.AddlDiscAmt = AddlDiscAmt
                        salesDetail_instance.GrossAmount = GrossAmount
                        salesDetail_instance.TaxableAmount = TaxableAmount
                        salesDetail_instance.VATPerc = VATPerc
                        salesDetail_instance.VATAmount = VATAmount
                        salesDetail_instance.SGSTPerc = SGSTPerc
                        salesDetail_instance.SGSTAmount = SGSTAmount
                        salesDetail_instance.CGSTPerc = CGSTPerc
                        salesDetail_instance.CGSTAmount = CGSTAmount
                        salesDetail_instance.IGSTPerc = IGSTPerc
                        salesDetail_instance.IGSTAmount = IGSTAmount
                        salesDetail_instance.NetAmount = NetAmount
                        salesDetail_instance.CreatedUserID = CreatedUserID
                        salesDetail_instance.UpdatedDate = today
                        salesDetail_instance.Action = Action
                        salesDetail_instance.CreatedDate = today
                        salesDetail_instance.TAX1Perc = TAX1Perc
                        salesDetail_instance.TAX1Amount = TAX1Amount
                        salesDetail_instance.TAX2Perc = TAX2Perc
                        salesDetail_instance.TAX2Amount = TAX2Amount
                        salesDetail_instance.TAX3Perc = TAX3Perc
                        salesDetail_instance.TAX3Amount = TAX3Amount
                        salesDetail_instance.KFCAmount = KFCAmount
                        salesDetail_instance.BatchCode = BatchCode
                        salesDetail_instance.CompanyID = CompanyID
                        salesDetail_instance.LogID = log_instance.ID
                        salesDetail_instance.ProductTaxID = log_instance.ProductTaxID

                        salesDetail_instance.save()

                    if detailID == 1:
                        SalesOrderDetailsID = order_id(
                            SalesOrderDetails, BranchID, CompanyID)
                        Action = "A"

                        log_instance = SalesOrderDetails_Log.objects.create(
                            CompanyID=CompanyID,
                            TransactionID=SalesOrderDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            SalesOrderMasterID=SalesOrderMasterID,
                            ProductID=ProductID,
                            Qty=Qty,
                            FreeQty=FreeQty,
                            UnitPrice=UnitPrice,
                            InclusivePrice=InclusivePrice,
                            RateWithTax=RateWithTax,
                            PriceListID=PriceListID,
                            DiscountPerc=DiscountPerc,
                            DiscountAmount=DiscountAmount,
                            GrossAmount=GrossAmount,
                            TaxableAmount=TaxableAmount,
                            VATPerc=VATPerc,
                            VATAmount=VATAmount,
                            SGSTPerc=SGSTPerc,
                            SGSTAmount=SGSTAmount,
                            CGSTPerc=CGSTPerc,
                            CGSTAmount=CGSTAmount,
                            IGSTPerc=IGSTPerc,
                            IGSTAmount=IGSTAmount,
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            KFCAmount=KFCAmount,
                            NetAmount=NetAmount,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            BatchCode=BatchCode,
                            ProductTaxID=ProductTaxID
                        )

                        SalesOrderDetails.objects.create(
                            CompanyID=CompanyID,
                            SalesOrderDetailsID=SalesOrderDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            SalesOrderMasterID=SalesOrderMasterID,
                            ProductID=ProductID,
                            Qty=Qty,
                            FreeQty=FreeQty,
                            UnitPrice=UnitPrice,
                            InclusivePrice=InclusivePrice,
                            RateWithTax=RateWithTax,
                            PriceListID=PriceListID,
                            DiscountPerc=DiscountPerc,
                            DiscountAmount=DiscountAmount,
                            GrossAmount=GrossAmount,
                            TaxableAmount=TaxableAmount,
                            VATPerc=VATPerc,
                            VATAmount=VATAmount,
                            SGSTPerc=SGSTPerc,
                            SGSTAmount=SGSTAmount,
                            CGSTPerc=CGSTPerc,
                            CGSTAmount=CGSTAmount,
                            IGSTPerc=IGSTPerc,
                            IGSTAmount=IGSTAmount,
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            KFCAmount=KFCAmount,
                            NetAmount=NetAmount,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            BatchCode=BatchCode,
                            LogID=log_instance.ID,
                            ProductTaxID=ProductTaxID
                        )


            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sale Orders',
            #              'Edit', 'Sale Orders Updated successfully.', 'Sale Orders Updated successfully.')

            response_data = {
                "StatusCode": 6000,
                "message": "SalesOrder Updated Successfully!!!",
                "OrderID" : salesOrderMaster_instance.id
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

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Sales Order',
                         'Create', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def check_pos_table_delete(request):
    today = datetime.datetime.now()
    data = request.data

    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    table_id = data['table_id']

    is_exist = False
    if POS_Table.objects.filter(id=table_id).exists():
        instance = POS_Table.objects.get(id=table_id)
        if SalesOrderMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,Table=instance).exists():
            is_exist = True

        response_data = {
            "StatusCode": 6000,
            "is_exist":is_exist,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "is_exist": is_exist,
        }

        return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def update_pos_settings(request):
    today = datetime.datetime.now()
    data = request.data

    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    warehouse_id = data['warehouse_id']

    warehouse_instance = Warehouse.objects.get(id=warehouse_id)
    if POS_Settings.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        instance = POS_Settings.objects.filter(CompanyID=CompanyID,BranchID=BranchID).first()
        instance.Warehouse = warehouse_instance
        instance.save()
    else:
        POS_Settings.objects.create(
                CompanyID=CompanyID,
                BranchID=BranchID,
                Warehouse=warehouse_instance,
            )
    response_data = {
        "StatusCode": 6000,
        "message" : "success"
    }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def view_pos_salesOrder(request,pk):
    today = datetime.datetime.now()
    data = request.data

    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    PriceRounding = data['PriceRounding']

    if SalesOrderMaster.objects.filter(pk=pk).exists():
        instance = SalesOrderMaster.objects.get(CompanyID=CompanyID, pk=pk)
        serialized = SalesOrderMasterRestSerializer(
            instance, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding})

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Sales Order Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)




@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def create_pos_salesInvoice(request):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            CreatedUserID = data['CreatedUserID']
            today = datetime.datetime.now()
            BranchID = data['BranchID']

            GrandTotal = data['GrandTotal']
            BillDiscPercent = data['BillDiscPercent']
            BillDiscAmt = data['BidillDiscAmt']
            CashReceived = data['CashReceived']
            BankAmount = data['BankAmount']
            CardTypeID = data['CardTypeID']
            CardNumber = data['CardNumber']
            SalesOrderID = data['SalesOrderID']
            TotalDiscount = data['TotalDiscount']
            Date = data['Date']
            RoundOff = data['RoundOff']
            Balance = data['Balance']
            AllowCashReceiptMoreSaleAmt = data['AllowCashReceiptMoreSaleAmt']
            LedgerID = data['LedgerID']

            Cash_Account = None
            Bank_Account = None

            if UserTable.objects.filter(CompanyID=CompanyID, customer__user__pk=CreatedUserID).exists():
                Cash_Account = UserTable.objects.get(
                    CompanyID=CompanyID, customer__user__pk=CreatedUserID).Cash_Account
                Bank_Account = UserTable.objects.get(
                    CompanyID=CompanyID, customer__user__pk=CreatedUserID).Bank_Account

            Action = "A"
            VoucherType="SI"

            CashID = Cash_Account
            BankID = Bank_Account

            sales_order_instance = SalesOrderMaster.objects.get(id=SalesOrderID,CompanyID=CompanyID)
            sales_order_instance.Status =  "Paid"
            sales_order_instance.IsInvoiced =  "I"
            sales_order_instance.save()
            SalesOrderMasterID = sales_order_instance.SalesOrderMasterID

            CreditPeriod = 0
            # LedgerID = sales_order_instance.LedgerID
            PriceCategoryID = sales_order_instance.PriceCategoryID
            EmployeeID = 0
            SalesAccount = 85
            CustomerName = sales_order_instance.CustomerName
            Address1 = sales_order_instance.Address1
            Address2 = sales_order_instance.Address2
            Notes = sales_order_instance.Notes
            TransactionTypeID = 1
            WarehouseID = 1
            WarehouseID = 1
            IsActive =  sales_order_instance.IsActive
            TaxID =  sales_order_instance.TaxID
            TaxType =  sales_order_instance.TaxType
            FinacialYearID =  sales_order_instance.FinacialYearID
            TotalGrossAmt =  sales_order_instance.TotalGrossAmt
            TotalTax =  sales_order_instance.TotalTax
            NetTotal =  sales_order_instance.NetTotal
            AddlDiscAmt = 0
            AdditionalCost = 0
            AddlDiscPercent = 0
            VATAmount = sales_order_instance.VATAmount
            SGSTAmount = sales_order_instance.SGSTAmount
            CGSTAmount = sales_order_instance.CGSTAmount
            IGSTAmount = sales_order_instance.IGSTAmount
            TAX1Amount = sales_order_instance.TAX1Amount
            TAX2Amount = sales_order_instance.TAX2Amount
            TAX3Amount = sales_order_instance.TAX3Amount
            KFCAmount = 0
            OldLedgerBalance = 0
            BatchID = 0
            SeatNumber = ""
            NoOfGuests = 0
            INOUT = True
            TokenNumber = 0
            SalesType = ""

            order_details = SalesOrderDetails.objects.filter(CompanyID=CompanyID,BranchID=BranchID,SalesOrderMasterID=SalesOrderMasterID)
            TotalTaxableAmount = 0
            for i in order_details:
                TotalTaxableAmount+= i.TaxableAmount

            # VoucherNo Updated
            VoucherNo = get_VoucherNoForPOS(CompanyID,BranchID,CreatedUserID,"SI")
            InvoiceNo = get_InvoiceNo(VoucherNo)
            PreFix = "SI"
            Seperator = ""
            ShippingCharge = 0
            shipping_tax_amount = 0
            TaxTypeID = ""
            SAC = ""
            SalesTax = 0
            Country_of_Supply = ""
            State_of_Supply = ""
            GST_Treatment = ""

            Table = None
            if sales_order_instance.Table:
                Table = sales_order_instance.Table.id
            Type = sales_order_instance.Type
            table_ins = None
            if Type == "Dining" and Table:
                if POS_Table.objects.filter(CompanyID=CompanyID,BranchID=BranchID,id=Table).exists():
                    table_ins = POS_Table.objects.get(CompanyID=CompanyID,BranchID=BranchID,id=Table)
                    table_ins.Status = "Paid"
                    table_ins.save()

            # checking voucher number already exist
            VoucherNoLow = VoucherNo.lower()
            is_voucherExist = False
            insts = SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID)
            if insts:
                for i in insts:
                    voucher_no = i.VoucherNo
                    voucherNo = voucher_no.lower()
                    if VoucherNoLow == voucherNo:
                        is_voucherExist = True

            check_VoucherNoAutoGenerate = False
            is_SaleOK = True
            if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="VoucherNoAutoGenerate").exists():
                check_VoucherNoAutoGenerate = GeneralSettings.objects.get(
                    CompanyID=CompanyID, SettingsType="VoucherNoAutoGenerate").SettingsValue

            if is_voucherExist == True and check_VoucherNoAutoGenerate == "True":
                VoucherNo = get_Genrate_VoucherNo(
                    SalesMaster, BranchID, CompanyID, "SI")
                is_SaleOK = True
            elif is_voucherExist == False:
                is_SaleOK = True
            else:
                is_SaleOK = False

            if is_SaleOK:

                SalesMasterID = invoice_master_id(SalesMaster, BranchID, CompanyID)
                sales_order_instance.InvoiceID = SalesMasterID
                sales_order_instance.save()
                if Parties.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID).exists():

                    party_instances = Parties.objects.filter(
                        CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID)

                    for party_instance in party_instances:

                        party_instance.PartyName = CustomerName

                        party_instance.save()

                if AllowCashReceiptMoreSaleAmt == True or AllowCashReceiptMoreSaleAmt == "true":
                    CashAmount = CashReceived
                elif float(Balance) < 0:
                    CashAmount = float(GrandTotal) - float(BankAmount)
                else:
                    CashAmount = CashReceived

                update_voucher_table(CompanyID,CreatedUserID,VoucherType,PreFix,Seperator, InvoiceNo)
                loyalty_customer = None
                Address3 = ""
                IsPosted = True
                SalesMaster_Log.objects.create(
                    LoyaltyCustomerID=loyalty_customer,
                    TotalTaxableAmount=TotalTaxableAmount,
                    TransactionID=SalesMasterID,
                    BranchID=BranchID,
                    VoucherNo=VoucherNo,
                    Date=Date,
                    CreditPeriod=CreditPeriod,
                    LedgerID=LedgerID,
                    PriceCategoryID=PriceCategoryID,
                    EmployeeID=EmployeeID,
                    SalesAccount=SalesAccount,
                    CustomerName=CustomerName,
                    Address1=Address1,
                    Address2=Address2,
                    Address3=Address3,
                    Notes=Notes,
                    FinacialYearID=FinacialYearID,
                    TotalGrossAmt=TotalGrossAmt,
                    AddlDiscPercent=AddlDiscPercent,
                    AddlDiscAmt=AddlDiscAmt,
                    TotalDiscount=TotalDiscount,
                    TotalTax=TotalTax,
                    NetTotal=NetTotal,
                    AdditionalCost=AdditionalCost,
                    GrandTotal=GrandTotal,
                    RoundOff=RoundOff,
                    CashReceived=CashReceived,
                    CashAmount=CashAmount,
                    BankAmount=BankAmount,
                    WarehouseID=WarehouseID,
                    TableID=1,
                    SeatNumber=SeatNumber,
                    NoOfGuests=NoOfGuests,
                    INOUT=INOUT,
                    TokenNumber=TokenNumber,
                    CardTypeID=CardTypeID,
                    CardNumber=CardNumber,
                    IsActive=IsActive,
                    IsPosted=IsPosted,
                    SalesType=SalesType,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    # TaxID=TaxID,
                    # TaxType=TaxType,
                    BillDiscPercent=BillDiscPercent,
                    BillDiscAmt=BillDiscAmt,
                    VATAmount=VATAmount,
                    SGSTAmount=SGSTAmount,
                    CGSTAmount=CGSTAmount,
                    IGSTAmount=IGSTAmount,
                    TAX1Amount=TAX1Amount,
                    TAX2Amount=TAX2Amount,
                    TAX3Amount=TAX3Amount,
                    KFCAmount=KFCAmount,
                    Balance=Balance,
                    TransactionTypeID=TransactionTypeID,
                    CompanyID=CompanyID,
                    OldLedgerBalance=OldLedgerBalance,
                    BankID=BankID,
                    CashID=CashID,
                    ShippingCharge=ShippingCharge,
                    shipping_tax_amount=shipping_tax_amount,
                    TaxTypeID=TaxTypeID,
                    SAC=SAC,
                    SalesTax=SalesTax,
                    Country_of_Supply=Country_of_Supply,
                    State_of_Supply=State_of_Supply,
                    GST_Treatment=GST_Treatment,
                    Table=table_ins,
                )

                sales_instance = SalesMaster.objects.create(
                    LoyaltyCustomerID=loyalty_customer,
                    TotalTaxableAmount=TotalTaxableAmount,
                    SalesMasterID=SalesMasterID,
                    BranchID=BranchID,
                    VoucherNo=VoucherNo,
                    Date=Date,
                    CreditPeriod=CreditPeriod,
                    LedgerID=LedgerID,
                    PriceCategoryID=PriceCategoryID,
                    EmployeeID=EmployeeID,
                    SalesAccount=SalesAccount,
                    CustomerName=CustomerName,
                    Address1=Address1,
                    Address2=Address2,
                    Address3=Address3,
                    Notes=Notes,
                    FinacialYearID=FinacialYearID,
                    TotalGrossAmt=TotalGrossAmt,
                    AddlDiscPercent=AddlDiscPercent,
                    AddlDiscAmt=AddlDiscAmt,
                    TotalDiscount=TotalDiscount,
                    TotalTax=TotalTax,
                    NetTotal=NetTotal,
                    AdditionalCost=AdditionalCost,
                    GrandTotal=GrandTotal,
                    RoundOff=RoundOff,
                    CashReceived=CashReceived,
                    CashAmount=CashAmount,
                    BankAmount=BankAmount,
                    WarehouseID=WarehouseID,
                    TableID=1,
                    SeatNumber=SeatNumber,
                    NoOfGuests=NoOfGuests,
                    INOUT=INOUT,
                    TokenNumber=TokenNumber,
                    CardTypeID=CardTypeID,
                    CardNumber=CardNumber,
                    IsActive=IsActive,
                    IsPosted=IsPosted,
                    SalesType=SalesType,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    TaxID=TaxID,
                    TaxType=TaxType,
                    BillDiscPercent=BillDiscPercent,
                    BillDiscAmt=BillDiscAmt,
                    VATAmount=VATAmount,
                    SGSTAmount=SGSTAmount,
                    CGSTAmount=CGSTAmount,
                    IGSTAmount=IGSTAmount,
                    TAX1Amount=TAX1Amount,
                    TAX2Amount=TAX2Amount,
                    TAX3Amount=TAX3Amount,
                    KFCAmount=KFCAmount,
                    Balance=Balance,
                    TransactionTypeID=TransactionTypeID,
                    CompanyID=CompanyID,
                    OldLedgerBalance=OldLedgerBalance,
                    BankID=BankID,
                    CashID=CashID,
                    ShippingCharge=ShippingCharge,
                    shipping_tax_amount=shipping_tax_amount,
                    TaxTypeID=TaxTypeID,
                    SAC=SAC,
                    SalesTax=SalesTax,
                    Country_of_Supply=Country_of_Supply,
                    State_of_Supply=State_of_Supply,
                    GST_Treatment=GST_Treatment,
                    Table=table_ins,
                )
                # ======QRCODE==========
                url = str("https://viknbooks.vikncodes.com/invoice/") + str(sales_instance.pk)+str('/')+ str('SI')
                # url = str("https://viknbooks.com/invoice/") + str(sales_instance.pk)+str('/')+ str('SI')
                # url = str("http://localhost:3000/invoice/") + str(sales_instance.pk)+str('/')+ str('SI')
                print(url)
                qr_instance = QrCode.objects.create(
                    voucher_type= "SI",
                    master_id = sales_instance.pk,
                    url=url,                
                )

                account_group = AccountLedger.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).AccountGroupUnder

                if TaxType == 'VAT':
                    if float(VATAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=55,
                            RelatedLedgerID=SalesAccount,
                            Credit=VATAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=55,
                            RelatedLedgerID=SalesAccount,
                            Credit=VATAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=55,
                            Debit=VATAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=55,
                            Debit=VATAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )


                elif TaxType == 'GST Intra-state B2B' or TaxType == 'GST Intra-state B2C':
                    if float(CGSTAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=3,
                            RelatedLedgerID=SalesAccount,
                            Credit=CGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )
                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=3,
                            RelatedLedgerID=SalesAccount,
                            Credit=CGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=3,
                            Debit=CGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=3,
                            Debit=CGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                    if float(SGSTAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=10,
                            RelatedLedgerID=SalesAccount,
                            Credit=SGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )
                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=10,
                            RelatedLedgerID=SalesAccount,
                            Credit=SGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=10,
                            Debit=SGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=10,
                            Debit=SGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )


                    if float(KFCAmount) > 0:

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=93,
                            RelatedLedgerID=SalesAccount,
                            Credit=KFCAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )
                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=93,
                            RelatedLedgerID=SalesAccount,
                            Credit=KFCAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=93,
                            Debit=KFCAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=93,
                            Debit=KFCAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )


                elif TaxType == 'GST Inter-state B2B' or TaxType == 'GST Inter-state B2C':
                    if float(IGSTAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=7,
                            RelatedLedgerID=SalesAccount,
                            Credit=IGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=7,
                            RelatedLedgerID=SalesAccount,
                            Credit=IGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=7,
                            Debit=IGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=7,
                            Debit=IGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                if not TaxType == 'Export':
                    if float(TAX1Amount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=16,
                            RelatedLedgerID=SalesAccount,
                            Credit=TAX1Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=16,
                            RelatedLedgerID=SalesAccount,
                            Credit=TAX1Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=16,
                            Debit=TAX1Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=16,
                            Debit=TAX1Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                    if float(TAX2Amount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=19,
                            RelatedLedgerID=SalesAccount,
                            Credit=TAX2Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=19,
                            RelatedLedgerID=SalesAccount,
                            Credit=TAX2Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=19,
                            Debit=TAX2Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=19,
                            Debit=TAX2Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                    if float(TAX3Amount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=22,
                            RelatedLedgerID=SalesAccount,
                            Credit=TAX3Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=22,
                            RelatedLedgerID=SalesAccount,
                            Credit=TAX3Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=22,
                            Debit=TAX3Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=22,
                            Debit=TAX3Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )


                if float(RoundOff) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=78,
                        RelatedLedgerID=SalesAccount,
                        Credit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=78,
                        RelatedLedgerID=SalesAccount,
                        Credit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=78,
                        Debit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=78,
                        Debit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                if float(RoundOff) < 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    RoundOff = abs(float(RoundOff))

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=78,
                        RelatedLedgerID=SalesAccount,
                        Debit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=78,
                        RelatedLedgerID=SalesAccount,
                        Debit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )


                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=78,
                        Credit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=78,
                        Credit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )


                if float(TotalDiscount) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=74,
                        RelatedLedgerID=SalesAccount,
                        Debit=TotalDiscount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=74,
                        RelatedLedgerID=SalesAccount,
                        Debit=TotalDiscount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=74,
                        Credit=TotalDiscount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=74,
                        Credit=TotalDiscount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                
                # credit sales start here
                if float(CashReceived) == 0 and float(BankAmount) == 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
                        Credit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
                        Credit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                # credit sales end here 

                # customer with cash and customer with partial cash start here
                elif (account_group == 10 or account_group == 29 or account_group== 32) and float(CashReceived) > 0 and float(BankAmount) == 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
                        Credit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
                        Credit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=CashID,
                        RelatedLedgerID=LedgerID,
                        Debit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=CashID,
                        RelatedLedgerID=LedgerID,
                        Debit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=CashID,
                        Credit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=CashID,
                        Credit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                # customer with cash and customer with partial cash end here

                # customer with bank and customer with partial bank start here
                elif (account_group == 10 or account_group == 29 or account_group== 32) and float(CashReceived) == 0 and float(BankAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
                        Credit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
                        Credit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=BankID,
                        RelatedLedgerID=LedgerID,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=BankID,
                        RelatedLedgerID=LedgerID,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=BankID,
                        Credit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=BankID,
                        Credit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                # customer with bank and customer with partial bank end here

                # bank with cash and cash with cash start here
                elif (account_group == 8 or account_group == 9) and float(CashReceived) > 0 and float(BankAmount) == 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=CashID,
                        Credit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=CashID,
                        Credit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=CashID,
                        RelatedLedgerID=SalesAccount,
                        Debit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=CashID,
                        RelatedLedgerID=SalesAccount,
                        Debit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    csh_value = float(GrandTotal) - float(CashReceived)
                    if float(csh_value) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                                LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=LedgerID,
                            RelatedLedgerID=SalesAccount,
                            Debit=csh_value,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=LedgerID,
                            RelatedLedgerID=SalesAccount,
                            Debit=csh_value,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                                LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=LedgerID,
                            Credit=csh_value,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=LedgerID,
                            Credit=csh_value,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )
                # bank with cash and cash with cash end here

                # bank with bank and cash with bank start here
                elif (account_group == 8 or account_group == 9) and float(CashReceived) == 0 and float(BankAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=BankID,
                        Credit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=BankID,
                        Credit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=BankID,
                        RelatedLedgerID=SalesAccount,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=BankID,
                        RelatedLedgerID=SalesAccount,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    bnk_value = float(GrandTotal) - float(BankAmount)
                    if not float(bnk_value) == 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                                LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=LedgerID,
                            RelatedLedgerID=SalesAccount,
                            Debit=bnk_value,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=LedgerID,
                            RelatedLedgerID=SalesAccount,
                            Debit=bnk_value,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                                LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=LedgerID,
                            Credit=bnk_value,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=LedgerID,
                            Credit=bnk_value,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )


                # bank with bank and cash with bank end here

                # customer with partial cash /bank and customer with cash/bank
                elif (account_group == 10 or account_group == 29 or account_group== 32) and float(CashReceived) > 0 and float(BankAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
                        Credit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
                        Credit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=CashID,
                        RelatedLedgerID=LedgerID,
                        Debit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=CashID,
                        RelatedLedgerID=LedgerID,
                        Debit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=CashID,
                        Credit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=CashID,
                        Credit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=BankID,
                        RelatedLedgerID=LedgerID,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=BankID,
                        RelatedLedgerID=LedgerID,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=BankID,
                        Credit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=BankID,
                        RelatedLedgerID=LedgerID,
                        Credit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )
                # customer with partial cash /bank and customer with cash/bank

                # cash with cash/bank start here
                elif (account_group == 9 or account_group == 8) and float(CashReceived) > 0 and float(BankAmount) > 0:
                    if float(Balance) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                                LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=CashID,
                            Credit=Balance,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=CashID,
                            Credit=Balance,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                                LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=CashID,
                            RelatedLedgerID=SalesAccount,
                            Debit=Balance,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=CashID,
                            RelatedLedgerID=SalesAccount,
                            Debit=Balance,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                    LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=BankID,
                        RelatedLedgerID=SalesAccount,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=BankID,
                        RelatedLedgerID=SalesAccount,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=BankID,
                        Credit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=BankID,
                        Credit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=CashID,
                        Credit=CashReceived,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=CashID,
                        Credit=CashReceived,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=CashID,
                        RelatedLedgerID=SalesAccount,
                        Debit=CashReceived,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=CashID,
                        RelatedLedgerID=SalesAccount,
                        Debit=CashReceived,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                # cash with cash/bank end here
                # new posting ending here


                for order in order_details:

                    ProductID = order.ProductID
                    if ProductID:
                        Qty = order.Qty
                        FreeQty = order.FreeQty
                        Flavour = ""
                        PriceListID = order.PriceListID
                        BatchCode = order.BatchCode
                        is_inclusive = order.is_inclusive

                        UnitPrice = float(order.UnitPrice)
                        InclusivePrice = float(order.InclusivePrice)
                        RateWithTax = float(order.RateWithTax)
                        # CostPerPrice = float(order.CostPerPrice)
                        AddlDiscPerc = 0
                        AddlDiscAmt = 0
                        DiscountPerc = order.DiscountPerc
                        DiscountAmount = order.DiscountAmount
                        GrossAmount = float(order.GrossAmount)
                        TaxableAmount = float(order.TaxableAmount)
                        VATPerc = float(order.VATPerc)
                        VATAmount = float(order.VATAmount)
                        SGSTPerc = float(order.SGSTPerc)
                        SGSTAmount = float(order.SGSTAmount)
                        CGSTPerc = float(order.CGSTPerc)
                        CGSTAmount = float(order.CGSTAmount)
                        IGSTPerc = float(order.IGSTPerc)
                        IGSTAmount = float(order.IGSTAmount)
                        NetAmount = float(order.NetAmount)
                        KFCAmount = float(order.KFCAmount)
                        TAX1Perc = float(order.TAX1Perc)
                        TAX1Amount = float(order.TAX1Amount)
                        TAX2Perc = float(order.TAX2Perc)
                        TAX2Amount = float(order.TAX2Amount)
                        TAX3Perc = float(order.TAX3Perc)
                        TAX3Amount = float(order.TAX3Amount)
                        ProductTaxID = order.ProductTaxID

                        CostPerPrice = PriceList.objects.get(CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).PurchasePrice

                        SerialNos = []
                        Description = ""
                        KFCPerc = 0

                        if is_inclusive == True:
                            Batch_salesPrice = InclusivePrice
                        else:
                            Batch_salesPrice = UnitPrice

                        product_is_Service = Product.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).is_Service
                        
                        product_purchasePrice = PriceList.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, PriceListID=PriceListID).PurchasePrice
                        MultiFactor = PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).MultiFactor

                        qty_batch = float(FreeQty) + float(Qty)
                        Qty_batch = float(MultiFactor) * float(qty_batch)

                        check_AllowUpdateBatchPriceInSales = False

                        if product_is_Service == False:
                            if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="AllowUpdateBatchPriceInSales").exists():
                                check_AllowUpdateBatchPriceInSales = GeneralSettings.objects.get(
                                    CompanyID=CompanyID, SettingsType="AllowUpdateBatchPriceInSales").SettingsValue

                            if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
                                check_EnableProductBatchWise = GeneralSettings.objects.get(
                                    CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
                                # check_BatchCriteria = "PurchasePriceAndSalesPrice"

                                if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                                    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
                                        if check_AllowUpdateBatchPriceInSales == "True" or check_AllowUpdateBatchPriceInSales == True:
                                            batch_ins = Batch.objects.get(
                                                CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode)
                                            StockOut = batch_ins.StockOut
                                            BatchCode = batch_ins.BatchCode
                                            NewStock = float(
                                                StockOut) + float(Qty_batch)
                                            batch_ins.StockOut = NewStock
                                            batch_ins.SalesPrice = Batch_salesPrice
                                            batch_ins.save()
                                        else:
                                            batch_ins = Batch.objects.get(
                                                CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode)
                                            StockOut = batch_ins.StockOut
                                            BatchCode = batch_ins.BatchCode
                                            NewStock = float(
                                                StockOut) + float(Qty_batch)
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
                                            PurchasePrice=product_purchasePrice,
                                            SalesPrice=Batch_salesPrice,
                                            PriceListID=PriceListID,
                                            ProductID=ProductID,
                                            WareHouseID=WarehouseID,
                                            CreatedDate=today,
                                            UpdatedDate=today,
                                            CreatedUserID=CreatedUserID,
                                        )

                                else:
                                    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PriceListID=PriceListID).exists():
                                        batch_ins = Batch.objects.get(
                                            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PriceListID=PriceListID)
                                        StockOut = batch_ins.StockOut
                                        BatchCode = batch_ins.BatchCode
                                        NewStock = float(
                                            StockOut) + float(Qty_batch)
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
                                            PurchasePrice=product_purchasePrice,
                                            SalesPrice=Batch_salesPrice,
                                            PriceListID=PriceListID,
                                            ProductID=ProductID,
                                            WareHouseID=WarehouseID,
                                            CreatedDate=today,
                                            UpdatedDate=today,
                                            CreatedUserID=CreatedUserID,
                                        )

                        SalesDetailsID = invoice_id(
                            SalesDetails, BranchID, CompanyID)

                        if SerialNos:
                            for sn in SerialNos:
                                try:
                                    SerialNo = sn["SerialNo"]
                                except:
                                    SerialNo = ""

                                try:
                                    ItemCode = sn["ItemCode"]
                                except:
                                    ItemCode = ""

                                SerialNumbers.objects.create(
                                    VoucherType="SI",
                                    CompanyID=CompanyID,
                                    SerialNo=SerialNo,
                                    ItemCode=ItemCode,
                                    SalesMasterID=SalesMasterID,
                                    SalesDetailsID=SalesDetailsID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CreatedUserID=CreatedUserID,
                                )

                        log_instance = SalesDetails_Log.objects.create(
                            TransactionID=SalesDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            SalesMasterID=SalesMasterID,
                            ProductID=ProductID,
                            Qty=Qty,
                            ReturnQty=Qty,
                            FreeQty=FreeQty,
                            UnitPrice=UnitPrice,
                            InclusivePrice=InclusivePrice,
                            RateWithTax=RateWithTax,
                            CostPerPrice=CostPerPrice,
                            PriceListID=PriceListID,
                            AddlDiscPerc=AddlDiscPerc,
                            AddlDiscAmt=AddlDiscAmt,
                            DiscountPerc=DiscountPerc,
                            DiscountAmount=DiscountAmount,
                            GrossAmount=GrossAmount,
                            TaxableAmount=TaxableAmount,
                            VATPerc=VATPerc,
                            VATAmount=VATAmount,
                            SGSTPerc=SGSTPerc,
                            SGSTAmount=SGSTAmount,
                            CGSTPerc=CGSTPerc,
                            CGSTAmount=CGSTAmount,
                            IGSTPerc=IGSTPerc,
                            IGSTAmount=IGSTAmount,
                            NetAmount=NetAmount,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            Flavour=Flavour,
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            KFCAmount=KFCAmount,
                            CompanyID=CompanyID,
                            BatchCode=BatchCode,
                            Description=Description,
                            KFCPerc=KFCPerc,
                            ProductTaxID=ProductTaxID
                        )

                        SalesDetails.objects.create(
                            SalesDetailsID=SalesDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            SalesMasterID=SalesMasterID,
                            ProductID=ProductID,
                            Qty=Qty,
                            ReturnQty=Qty,
                            FreeQty=FreeQty,
                            UnitPrice=UnitPrice,
                            InclusivePrice=InclusivePrice,
                            RateWithTax=RateWithTax,
                            CostPerPrice=CostPerPrice,
                            PriceListID=PriceListID,
                            AddlDiscPerc=AddlDiscPerc,
                            AddlDiscAmt=AddlDiscAmt,
                            DiscountPerc=DiscountPerc,
                            DiscountAmount=DiscountAmount,
                            GrossAmount=GrossAmount,
                            TaxableAmount=TaxableAmount,
                            VATPerc=VATPerc,
                            VATAmount=VATAmount,
                            SGSTPerc=SGSTPerc,
                            SGSTAmount=SGSTAmount,
                            CGSTPerc=CGSTPerc,
                            CGSTAmount=CGSTAmount,
                            IGSTPerc=IGSTPerc,
                            IGSTAmount=IGSTAmount,
                            NetAmount=NetAmount,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            Flavour=Flavour,
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            KFCAmount=KFCAmount,
                            CompanyID=CompanyID,
                            BatchCode=BatchCode,
                            LogID=log_instance.ID,
                            Description=Description,
                            KFCPerc=KFCPerc,
                            ProductTaxID=ProductTaxID
                        )

                        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="SalesPriceUpdate").exists():
                            check_SalesPriceUpdate = GeneralSettings.objects.get(
                                CompanyID=CompanyID, SettingsType="SalesPriceUpdate", BranchID=BranchID).SettingsValue
                            if check_SalesPriceUpdate == "True" or check_SalesPriceUpdate == True:
                                pri_ins = PriceList.objects.get(
                                    CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID)
                                pri_ins.SalesPrice = Batch_salesPrice
                                pri_ins.save()


                        if product_is_Service == False:

                            # priceList = PriceList.objects.get(CompanyID=CompanyID,PriceListID=PriceListID,BranchID=BranchID)

                            # MultiFactor = PriceList.objects.get(
                            #     CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).MultiFactor
                            PriceListID_DefUnit = PriceList.objects.get(
                                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True, BranchID=BranchID).PriceListID

                            # PriceListID_DefUnit = priceList.PriceListID
                            # MultiFactor = priceList.MultiFactor

                            # PurchasePrice = priceList.PurchasePrice
                            # SalesPrice = priceList.SalesPrice

                            qty = float(FreeQty) + float(Qty)

                            Qty = float(MultiFactor) * float(qty)
                            Cost = float(CostPerPrice) / float(MultiFactor)

                            # Qy = round(Qty, 4)
                            # Qty = str(Qy)

                            # Ct = round(Cost, 4)
                            # Cost = str(Ct)

                            princeList_instance = PriceList.objects.get(
                                CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID_DefUnit, BranchID=BranchID)
                            PurchasePrice = princeList_instance.PurchasePrice
                            SalesPrice = princeList_instance.SalesPrice

                            StockPostingID = get_auto_stockPostid(
                                StockPosting, BranchID, CompanyID)
                            StockPosting.objects.create(
                                StockPostingID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=Date,
                                VoucherMasterID=SalesMasterID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                BatchID=BatchID,
                                WareHouseID=WarehouseID,
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
                                VoucherMasterID=SalesMasterID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                BatchID=BatchID,
                                WareHouseID=WarehouseID,
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





                #request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sale Orders',
                #              'Create', 'Sale Orders created successfully.', 'Sale Orders saved successfully.')

                response_data = {
                    "StatusCode": 6000,
                    "message": "Sale Invoice created Successfully!!!",
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Sale Invoice',
                             'Create', 'Sale Invoice created Failed.', 'VoucherNo already exist!')
                response_data = {
                    "StatusCode": 6001,
                    "message": "VoucherNo already exist.Please Change Your Prefix!"
                    }
                return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        data = request.data
        CreatedUserID = data['CreatedUserID']
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again"
        }

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Sales invoice pos',
                         'Create', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)




@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def generate_pos_order_token_no(request):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    
    TokenNumber = get_TokenNo(CompanyID,BranchID)

    response_data = {
        "StatusCode": 6000,
        "TokenNumber": TokenNumber,
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def reset_status(request):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    Type = data['Type']
    unqid = data['unqid']
    reason_id = data['reason_id']
    
    is_success = False
    if Type == "Dining":
        if POS_Table.objects.filter(CompanyID=CompanyID,BranchID=BranchID,id=unqid).exists():
            instance = POS_Table.objects.get(CompanyID=CompanyID,BranchID=BranchID,id=unqid)
            instance.Status = "Vacant"
            instance.save()
            is_success = True
    elif Type == "Dining&Cancel":
        if POS_Table.objects.filter(CompanyID=CompanyID,BranchID=BranchID,id=unqid).exists():
            instance = POS_Table.objects.get(CompanyID=CompanyID,BranchID=BranchID,id=unqid)
            if SalesOrderMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,Table__Status="Ordered").exists():
                order_instance = SalesOrderMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,Table__Status="Ordered").first()
                order_instance.Status = "Cancelled"
                if CancelReasons.objects.filter(id=reason_id).exists():
                    reason_instance = CancelReasons.objects.get(id=reason_id)
                    order_instance.CancelReason = reason_instance
                order_instance.save()
            instance.Status = "Vacant"
            instance.save()
            is_success = True
    else:
        if SalesOrderMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,id=unqid).exists():
            instance = SalesOrderMaster.objects.get(CompanyID=CompanyID,BranchID=BranchID,id=unqid)
            Status = "Delivered"
            if Type == "Cancel":
                Status = "Cancelled"
            instance.Status = Status
            if Status == "Cancelled":
                if CancelReasons.objects.filter(id=reason_id).exists():
                    reason_instance = CancelReasons.objects.get(id=reason_id)
                    instance.CancelReason = reason_instance
            instance.save()
            is_success = True

    StatusCode = 6000
    message = "Success"
    if is_success == False:
        StatusCode = 6001
        message = "Data Not Updated"
    response_data = {
        "StatusCode": StatusCode,
        "message": message
    }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def list_order_reason(request):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']

    if CancelReasons.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        instance = CancelReasons.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
        serialized = OrderReason_Serializer(
            instance,many=True, context={"CompanyID": CompanyID})

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Reasons Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def order_reason(request):
    today = datetime.datetime.now()
    data = request.data

    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    Reason = data['Reason']
    Type = data['Type']
    unqid = data['unqid']

    StatusCode = 6001
    message = ""
    if Type == "create":
        CancelReasons.objects.create(
            CompanyID=CompanyID,
            BranchID=BranchID,
            Reason=Reason,
        )
        StatusCode = 6000
        message = "Reason created Successfully!"
    elif Type == "update":
        if CancelReasons.objects.filter(id=unqid).exists():
            reason_instance = CancelReasons.objects.get(id=unqid)
            reason_instance.Reason = Reason
            reason_instance.save()
            StatusCode = 6000
            message = "Reason updated Successfully!"
        else:
            StatusCode = 6001
            message = "Reason not updated!"
    elif Type == "delete":
        if not SalesOrderMaster.objects.filter(CancelReason__id=unqid).exists():
            if CancelReasons.objects.filter(id=unqid).exists():
                reason_instance = CancelReasons.objects.get(id=unqid)
                reason_instance.delete()
                StatusCode = 6000
                message = "Reason deleted Successfully!"
            else:
                StatusCode = 6001
                message = "Reason not deleted!"
        else:
            StatusCode == 6001
            message = "Reason can't deleted, Sales Order already Cancelled with this Reason!"
    else:
        StatusCode == 6001
        message = "Error!"

    response_data = {
        "StatusCode": StatusCode,
        "message": message
    }

    return Response(response_data, status=status.HTTP_200_OK)




@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def products_search_pos(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    product_name = data['product_name']
    length = data['length']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']

        if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Active=True, IsSales=True).exists():
            if length < 3:
                instances = Product.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, Active=True, ProductName__icontains=product_name, IsSales=True)[:10]
            else:
                instances = Product.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, Active=True, ProductName__icontains=product_name, IsSales=True)

            serialized = POS_Product_Serializer(instances,many=True,context={
                                                       "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding})
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Product',
                         'List', 'Product List Viewed Failed.', 'Product Not Found in this Branch!')
            response_data = {
                "StatusCode": 6001,
                "message": "Product Not Found in this Branch!!"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Something went wrong"
        }

        return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def pos_companies(request):
    userId = request.data['userId']
    userId = get_object_or_404(User.objects.filter(id=userId))
    my_company_instances = models.CompanySettings.objects.filter(
        owner=userId, is_deleted=False,business_type__Name="Restaurant")
    my_company_serialized = MyCompaniesSerializer(
        my_company_instances, many=True)
    my_company_json = convertOrderdDict(my_company_serialized.data)

    member_company_instances = models.UserTable.objects.filter(
        customer__user=userId,CompanyID__business_type__Name="Restaurant")
    member_company_serialized = CompaniesSerializer(
        member_company_instances, many=True)
    member_company_json = convertOrderdDict(member_company_serialized.data)

    data = []
    for i in my_company_json:
        id = i['id']
        CompanyImage = ""
        if my_company_instances.get(id=id).CompanyLogo:
            CompanyImage =  my_company_instances.get(id=id).CompanyLogo.url
        CompanyName = i['CompanyName']
        company_type = i['company_type']
        ExpiryDate = i['ExpiryDate']
        Permission = i['Permission']
        print("CompanyImage")
        print(CompanyImage)
        print(type(CompanyImage))
        ExpiryDate = date.today().strftime("%Y-%m-%d")
        if i['ExpiryDate'] != None:
            ExpiryDate = i['ExpiryDate']
        dic = {
            'id': id,
            'CompanyName': CompanyName,
            'company_type': company_type,
            'ExpiryDate': ExpiryDate,
            'Permission': Permission,
            'CompanyImage':CompanyImage
        }
        data.append(dic)

    for i in member_company_json:
        id = i['id']
        CompanyImage = ""
        if models.CompanySettings.objects.get(id=id).CompanyLogo:
            CompanyImage =  models.CompanySettings.objects.get(id=id).CompanyLogo.url
        CompanyName = i['CompanyName']
        company_type = i['company_type']
        Permission = i['Permission']
        ExpiryDate = date.today().strftime("%Y-%m-%d")
        if i['ExpiryDate'] != None:
            ExpiryDate = i['ExpiryDate']
        dic = {
            'id': id,
            'CompanyName': CompanyName,
            'company_type': company_type,
            'ExpiryDate': ExpiryDate,
            'Permission': Permission,
            'CompanyImage':CompanyImage
        }
        data.append(dic)

    tes_arry = []
    final_array = []
    for i in data:
        if not i['id'] in tes_arry:
            tes_arry.append(i['id'])
            final_array.append(i)

    CurrentVersion = 0
    MinimumVersion = 0
    if models.SoftwareVersion.objects.exists():
        CurrentVersion = models.SoftwareVersion.objects.get().CurrentVersion
        MinimumVersion = models.SoftwareVersion.objects.get().MinimumVersion

    software_version_dic = {
        "CurrentVersion": CurrentVersion,
        "MinimumVersion": MinimumVersion,
    }
    response_data = {
        "StatusCode": 6000,
        "data": final_array,
        "SoftwareVersion": software_version_dic
    }

    return Response(response_data, status=status.HTTP_200_OK)




@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def pos_sale_invoice(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    Type = data['Type']
    if Type == "SI":
        if models.SalesMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
            instance = models.SalesMaster.objects.get(CompanyID=CompanyID, pk=pk)
            serialized = POS_Sales_PrintSerializer(
                instance, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding,"request": request, })

            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sales Invoice', 'View',
            #              'Sales Invoice Single Viewed successfully.', 'Sales Invoice Single Viewed successfully.')
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Sales Not Found!"
            }
    else:
        if models.SalesOrderMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
            instance = models.SalesOrderMaster.objects.get(CompanyID=CompanyID, pk=pk)
            serialized = POS_SalesOrder_PrintSerializer(
                instance, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding,"request": request, })

            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sales Invoice', 'View',
            #              'Sales Invoice Single Viewed successfully.', 'Sales Invoice Single Viewed successfully.')
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Sales Not Found!"
            }

    return Response(response_data, status=status.HTTP_200_OK)




@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def pos_ledgerListByID(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    try:
        type_invoice = data['type_invoice']
    except:
        type_invoice = "None"

    try:
        ledger_name = data['ledger_name']
    except:
        ledger_name = ""

    try:
        length = data['length']
    except:
        length = ""

    try:
        load_data = data['load_data']
    except:
        load_data = False

    final_array = []
    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if models.AccountLedger.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
            AccountGroupUnder_list = [10, 29]

            if ledger_name:
                if float(length) < 3:
                    instances = models.AccountLedger.objects.filter(
                        BranchID=BranchID, CompanyID=CompanyID, LedgerName__icontains=ledger_name, AccountGroupUnder__in=AccountGroupUnder_list)[:10]
                else:
                    instances = models.AccountLedger.objects.filter(
                        BranchID=BranchID, CompanyID=CompanyID, LedgerName__icontains=ledger_name, AccountGroupUnder__in=AccountGroupUnder_list)
            elif load_data:
                instances = models.AccountLedger.objects.filter(
                    BranchID=BranchID, CompanyID=CompanyID, AccountGroupUnder__in=AccountGroupUnder_list)[:10]
            else:
                instances = models.AccountLedger.objects.filter(
                    BranchID=BranchID, CompanyID=CompanyID, AccountGroupUnder__in=AccountGroupUnder_list)

            serialized = POS_LedgerSerializer(instances, many=True, context={"CompanyID": CompanyID,
                                                                                    "PriceRounding": PriceRounding})
            jsnDatas = convertOrderdDict(serialized.data)
            for i in jsnDatas:
                LedgerID = i['LedgerID']
                LedgerName = i['LedgerName']
                OpeningBalance = i['OpeningBalance']
                CustomerLedgerBalance = i['CustomerLedgerBalance']
                AccountGroupUnder = i['AccountGroupUnder']

                final_array.append({
                        "LedgerID" : LedgerID,
                        "LedgerName" : LedgerName,
                        "OpeningBalance" : OpeningBalance,
                        "CustomerLedgerBalance" : CustomerLedgerBalance,
                        "AccountGroupUnder" : AccountGroupUnder,
                    })

            walkincustomer = {
                "LedgerID" : 1,
                "LedgerName" : "walk in customer",
                "OpeningBalance" : 0,
                "CustomerLedgerBalance" : 0,
                "AccountGroupUnder" : 10,
            }

            final_array.append(walkincustomer)

            response_data = {
                "StatusCode": 6000,
                "data": final_array
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Account Ledger Not Found in this Branch!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch  not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)




@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def pos_kitchen(request):
    today = datetime.datetime.now()
    data = request.data

    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    KitchenName = data['KitchenName']
    IPAddress = data['IPAddress']
    Notes = data['Notes']
    Type = data['Type']
    unqid = data['unqid']

    StatusCode = 6001
    message = ""
    if Type == "create":
        KitchenID = get_KitchenID(Kitchen, BranchID)
        Kitchen.objects.create(
            CompanyID=CompanyID,
            BranchID=BranchID,
            KitchenID=KitchenID,
            KitchenName=KitchenName,
            IPAddress=IPAddress,
            Notes=Notes,
        )
        Kitchen_Log.objects.create(
            CompanyID=CompanyID,
            BranchID=BranchID,
            TransactionID=KitchenID,
            KitchenName=KitchenName,
            IPAddress=IPAddress,
            Notes=Notes,
        )
        StatusCode = 6000
        message = "Kitchen created Successfully!"
    elif Type == "update":
        if Kitchen.objects.filter(id=unqid).exists():
            kitchen_instance = Kitchen.objects.get(id=unqid)
            kitchen_instance.KitchenName = KitchenName
            kitchen_instance.IPAddress = IPAddress
            kitchen_instance.Notes = Notes
            kitchen_instance.save()

            Kitchen_Log.objects.create(
                CompanyID=CompanyID,
                BranchID=BranchID,
                TransactionID=kitchen_instance.KitchenID,
                KitchenName=KitchenName,
                IPAddress=IPAddress,
                Notes=Notes,
            )
            StatusCode = 6000
            message = "Kitchen updated Successfully!"
        else:
            StatusCode = 6001
            message = "Kitchen not updated!"
    elif Type == "delete":
        if not ProductGroup.objects.filter(kitchen__id=unqid).exists():
            if Kitchen.objects.filter(id=unqid).exists():
                kitchen_instance = Kitchen.objects.get(id=unqid)
                kitchen_instance.delete()
                Kitchen_Log.objects.create(
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    TransactionID=kitchen_instance.KitchenID,
                    KitchenName=kitchen_instance.KitchenName,
                    IPAddress=kitchen_instance.IPAddress,
                    Notes=kitchen_instance.Notes,
                )
                StatusCode = 6000
                message = "Kitchen deleted Successfully!"
            else:
                StatusCode = 6001
                message = "Kitchen not deleted!"
        else:
            StatusCode == 6001
            message = "Kitchen can't deleted, ProductGroup already exist with this Kitchen!"
    else:
        StatusCode == 6001
        message = "Error!"

    response_data = {
        "StatusCode": StatusCode,
        "message": message
    }

    return Response(response_data, status=status.HTTP_200_OK)




@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def list_pos_kitchen(request):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']

    if Kitchen.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        instance = Kitchen.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
        serialized = Kitchen_Serializer(
            instance,many=True, context={"CompanyID": CompanyID})

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Kitchen Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def kitchen_print(request):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    OrderID = data['OrderID']
    final_data = []
    if Kitchen.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        kitchens = Kitchen.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
        for k in kitchens:
            if ProductGroup.objects.filter(CompanyID=CompanyID,BranchID=BranchID,kitchen=k).exists():
                kitchen_groups = ProductGroup.objects.filter(CompanyID=CompanyID,BranchID=BranchID,kitchen=k)
                group_ids = kitchen_groups.values_list('ProductGroupID',flat=True)
                products = Product.objects.filter(CompanyID=CompanyID,BranchID=BranchID,ProductGroupID__in=group_ids)
                group_productids = products.values_list('ProductID',flat=True)

                if SalesOrderMaster.objects.filter(id=OrderID).exists():
                    instance = SalesOrderMaster.objects.get(id=OrderID)
                    SalesOrderMasterID = instance.SalesOrderMasterID
                    detail_instances = SalesOrderDetails.objects.filter(CompanyID=CompanyID,BranchID=BranchID,SalesOrderMasterID=SalesOrderMasterID,KitchenPrint=False)
                    # productids = detail_instances.values_list('ProductID',flat=True)
                    # details_products = Product.objects.filter(CompanyID=CompanyID,BranchID=BranchID,ProductID__in=productids)
                    Items = []
                    TotalQty = 0
                    for p in detail_instances:
                        if p.ProductID in group_productids:
                            ProductName = products.filter(ProductID=p.ProductID).first().ProductName
                            ProductDescription = products.filter(ProductID=p.ProductID).first().Description
                            TableName = ""
                            Type = ""
                            TokenNumber = ""
                            if instance.Table:
                                TableName = instance.Table.TableName
                            items = {
                                "ProductName" : ProductName,
                                "ProductDescription" : ProductDescription,
                                "Qty" : p.Qty,
                                "TableName" : TableName,
                                "OrderType" : instance.Type,
                                "TokenNumber" : instance.TokenNumber,
                                "VoucherNo" : instance.VoucherNo,
                            }
                            TotalQty += float(p.Qty)
                            Items.append(items)
                            # p.KitchenPrint = True
                            p.save()
                    if Items:
                        final_data.append({
                                "kitchen_name" : k.KitchenName,
                                "IPAddress" : k.IPAddress,
                                "Items" : Items,
                                "TotalQty" : TotalQty
                            })



        response_data = {
            "StatusCode": 6000,
            "final_data": final_data,
            "message": "Success"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Kitchen Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)