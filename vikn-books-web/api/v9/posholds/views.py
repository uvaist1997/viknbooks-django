from api.v9.loyaltyCustomer.serializers import LoyaltyCustomerRestSerializer, LoyaltyCustomerSerializer
from api.v9.parties.functions import get_PartyCode, get_auto_idLedger, get_auto_id as party_id
from brands.models import AccountLedger_Log, Activity_Log, Kitchen, Kitchen_Log, CancelReasons, LoyaltyCustomer, LoyaltyCustomer_Log, MasterType, POS_Printer, Parties_Log, PriceList_Log, Product_Log, ProductVariants, PurchaseDetails, PurchaseOrderDetails, SerialNumbers, SoftwareVersion, StockPosting_Log, StockPosting, SalesDetails, PriceList, LedgerPosting_Log, LedgerPosting, AccountLedger, QrCode, Parties, TransactionTypes, UserTable, SalesMaster_Log, SalesDetails_Log, Batch, SalesMaster, SalesOrderDetails, SalesOrderDetails_Log, SalesOrderMaster_Log, GeneralSettings, POS_Settings, Warehouse, SalesOrderMaster, ProductGroup, Product, POS_Table_log, PriceCategory, POS_Table, POS_User_log, POS_User, Employee, POS_Role_Log, POS_Role, POSHoldMaster, POSHoldMaster_Log, POSHoldDetails, POSHoldDetails_Log, POSHoldDetailsDummy
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v9.posholds.serializers import POS_Table_Serializer1, Kitchen_Serializer, POS_LedgerSerializer, POS_SalesOrder_PrintSerializer, POS_Sales_PrintSerializer, OrderReason_Serializer, POS_Order_Serializer, POS_ProductGroup_Serializer, POS_Product_Serializer, POS_Table_Serializer, POS_User_Serializer, POS_Role_Serializer, POS_partySerializer, POSHoldMasterSerializer, POSHoldMasterRestSerializer, POSHoldDetailsSerializer, POSHoldDetailsRestSerializer, PrintSerializer, ProductVariantSerializer
from api.v9.brands.serializers import ListSerializer
from api.v9.posholds.functions import generate_serializer_errors, get_auto_PrinterID, get_auto_VariantID, get_pin_no, get_TokenNo, get_KitchenID, query_dining_report_rassassy_data, query_product_report_rassassy_data, query_sales_report_rassassy_data, query_table_wise_report_rassassy_data, query_take_away_report_rassassy_data
from rest_framework import status
from api.v9.posholds.functions import get_auto_id, get_auto_idMaster, get_VoucherNoForPOS, get_InvoiceNo
import datetime
from main.functions import converted_float, get_BranchLedgerId_for_LedgerPosting, get_GeneralSettings, get_ModelInstance, get_company, activity_log
from random import randint
from django.db import transaction, IntegrityError
from main.functions import update_voucher_table
from api.v9.salesOrders.functions import get_auto_id as order_id, get_auto_idMaster as order_master_id
from api.v9.sales.functions import get_auto_id as invoice_id, get_auto_idMaster as invoice_master_id, get_auto_stockPostid
import re
import sys
import os
from api.v9.salesOrders.serializers import SalesOrderMasterRestSerializer
from api.v9.sales.serializers import SalesMasterRestSerializer
from api.v9.accountLedgers.functions import get_LedgerCode, get_auto_id as generated_ledgerID,get_auto_LedgerPostid
from api.v9.products.functions import get_ProductCode, get_auto_AutoBarcode, get_auto_AutoBatchCode, get_auto_priceListid, update_stock,get_auto_id as get_auto_ProductID
from api.v9.ledgerPosting.functions import convertOrderdDict
from api.v9.users.serializers import MyCompaniesSerializer, CompaniesSerializer
from brands import models as models
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from datetime import date
from api.v9.sales.functions import get_Genrate_VoucherNo
from brands import models as administrations_models
from api.v9.users.functions import get_general_settings
from fatoora import Fatoora
from api.v9.loyaltyCustomer.functions import get_auto_id as get_auto_loyaltyID
from api.v9.transactionTypes.functions import get_auto_id as trans_type_get_auto_id


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

    PinNo = get_pin_no(CompanyID, BranchID)

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

    if POS_Role.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        role_instances = POS_Role.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID)
        serialized = POS_Role_Serializer(role_instances, many=True)

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
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

    if POS_User.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        user_instances = POS_User.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID)
        serialized = POS_User_Serializer(user_instances, many=True)

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
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

        if not POS_User.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Role=instance).exists():

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
def edit_pos_role(request, pk):
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
def edit_pos_user(request, pk):
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

    if POS_User.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PinNo=PinNo).exists():
        instance = POS_User.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, PinNo=PinNo).first()
        user = instance.User
        role = instance.Role

        response_data = {
            "StatusCode": 6000,
            "user_id": user.id,
            "user_name": user.FirstName,
            "role": role.id,
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
        if POS_Table.objects.filter(CompanyID=CompanyID, BranchID=BranchID, id__in=Deleted_cards).exists():
            POS_Table.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, id__in=Deleted_cards).delete()
            response_data = {
                "StatusCode": 6000,
            }

    if tables:
        is_createOK = True
        position = 1
        for i in tables:
            count = 0
            if not POS_Table.objects.filter(CompanyID=CompanyID, BranchID=BranchID, id=i['id']).exists():
                if not POS_Table.objects.filter(CompanyID=CompanyID, BranchID=BranchID, TableName=i['title']).exists():
                    priceCategory = None
                    if(i['priceid']):
                        if PriceCategory.objects.filter(id=i['priceid']).exists():
                            priceCategory = PriceCategory.objects.get(
                                id=i['priceid'])

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
                table_instances = POS_Table.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID).exclude(id=i['id'])
                if not table_instances.filter(TableName=i['title']).exclude(id=i['id']):
                    priceCategory = None
                    if(i['priceid']):
                        if PriceCategory.objects.filter(id=i['priceid']).exists():
                            priceCategory = PriceCategory.objects.get(
                                id=i['priceid'])
                    table_instances = POS_Table.objects.get(
                        CompanyID=CompanyID, BranchID=BranchID, id=i['id'])
                    table_instances.TableName = i['title']
                    table_instances.IsActive = i['IsActive']
                    table_instances.PriceCategory = priceCategory
                    table_instances.Position = position
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
    from datetime import date
    from datetime import timedelta
    today = datetime.datetime.now()
    data = request.data

    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    try:
        pos_type = data['type']
    except:
        pos_type = "admin"

    try:
        paid = data['paid']
    except:
        paid = True

    is_ok = False
    Dining = []
    Online = []
    TakeAway = []
    Car = []
    reason_data = []
    if POS_Table.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        if pos_type == "admin":
            pos_instances = POS_Table.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID).order_by('Position')
        else:
            pos_instances = POS_Table.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, IsActive=True).order_by('Position')
        serialized = POS_Table_Serializer(pos_instances, many=True)
        serialized_Dining = serialized.data
        if not pos_type == "admin":
            Dining_datas = convertOrderdDict(serialized_Dining)
            for i in Dining_datas:
                statuses = ["Delivered", "Cancelled"]
                # if paid == False:
                #     statuses = ["Delivered","Cancelled","Paid"]
                if i['Status'] not in statuses:
                    dining_dict = {
                        "id": i['id'],
                        "title": i['title'],
                        "description": i['description'],
                        "PriceCategory": i['PriceCategory'],
                        "Status": i['Status'],
                        "priceid": i['priceid'],
                        "SalesOrderID": i['SalesOrderID'],
                        "SalesMasterID": i['SalesMasterID'],
                        "SalesOrderGrandTotal": i['SalesOrderGrandTotal'],
                        "SalesGrandTotal": i['SalesGrandTotal'],
                        "OrderTime": i['OrderTime'],
                        "IsActive": i['IsActive'],
                    }
                    Dining.append(dining_dict)
        else:
            Dining = serialized.data
        is_ok = True
    # filter with date
    yesterday = today - timedelta(days=1)
    if SalesOrderMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=yesterday).exists():
        pos_order_instances = SalesOrderMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Date__gte=yesterday)
        Orderserialized = POS_Order_Serializer(pos_order_instances, many=True)
        orderdDict = Orderserialized.data
        jsnDatas = convertOrderdDict(orderdDict)

        for i in jsnDatas:
            Type = i['Type']
            statuses = ["Delivered", "Cancelled"]
            if paid == False:
                statuses = ["Delivered", "Cancelled", "Paid"]
            if Type == "Online" and i['Status'] not in statuses:
                online_datas = {
                    "SalesOrderID": i['SalesOrderID'],
                    "SalesID": i['SalesID'],
                    "CustomerName": i['CustomerName'],
                    "TokenNumber": i['TokenNumber'],
                    "Phone": i['Phone'],
                    "Status": i['Status'],
                    "SalesOrderGrandTotal": i['SalesOrderGrandTotal'],
                    "SalesGrandTotal": i['SalesGrandTotal'],
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
                    "SalesGrandTotal": i['SalesGrandTotal'],
                    "OrderTime": i['OrderTime'],
                }
                TakeAway.append(take_away_datas)
            elif Type == "Car" and i['Status'] not in statuses:
                car_datas = {
                    "SalesOrderID": i['SalesOrderID'],
                    "SalesID": i['SalesID'],
                    "CustomerName": i['CustomerName'],
                    "TokenNumber": i['TokenNumber'],
                    "Phone": i['Phone'],
                    "Status": i['Status'],
                    "SalesOrderGrandTotal": i['SalesOrderGrandTotal'],
                    "SalesGrandTotal": i['SalesGrandTotal'],
                    "OrderTime": i['OrderTime'],
                }
                Car.append(car_datas)
            is_ok = True

        if CancelReasons.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instance = CancelReasons.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
            reason_serialized = OrderReason_Serializer(
                instance, many=True, context={"CompanyID": CompanyID})
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
            "data": Dining,
            "Online": Online,
            "TakeAway": TakeAway,
            "Car": Car,
            "DiningStatusCode": DiningStatusCode,
            "OnlineStatusCode": OnlineStatusCode,
            "TakeAwayStatusCode": TakeAwayStatusCode,
            "CarStatusCode": CarStatusCode,
            "Reasons": reason_data,
            "Edition": CompanyID.Edition,
            "ExpiryDate": CompanyID.ExpiryDate,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "No data",
            "data": [],
            "Edition": CompanyID.Edition,
            "ExpiryDate": CompanyID.ExpiryDate,
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

    TokenNumber = get_TokenNo(CompanyID, BranchID)

    if ProductGroup.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        instances = ProductGroup.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID)
        serialized = POS_ProductGroup_Serializer(instances, many=True)

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data,
            "TokenNumber": TokenNumber,

        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "No data",
            "TokenNumber": TokenNumber,
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
    instances = None
    if GroupID:
        if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductGroupID=GroupID).exists():
            instances = Product.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, ProductGroupID=GroupID)
    else:
        if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instances = Product.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID)
    if instances:
        serialized = POS_Product_Serializer(instances, many=True, context={
            "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding})

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
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

            VoucherType = "SO"

            # VoucherNo Updated
            VoucherNo = get_VoucherNoForPOS(
                CompanyID, BranchID, CreatedUserID, "SO")

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
                if POS_Table.objects.filter(CompanyID=CompanyID, BranchID=BranchID, id=Table).exists():
                    table_ins = POS_Table.objects.get(
                        CompanyID=CompanyID, BranchID=BranchID, id=Table)
                    table_ins.Status = "Ordered"
                    table_ins.save()

            # checking voucher number already exist
            VoucherNoLow = VoucherNo.lower()
            is_voucherExist = False
            insts = SalesOrderMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
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
                    BranchID=BranchID, CompanyID=CompanyID, SettingsType="VoucherNoAutoGenerate").SettingsValue

            if is_voucherExist == True and check_VoucherNoAutoGenerate == "True":
                VoucherNo = get_Genrate_VoucherNo(
                    SalesOrderMaster, BranchID, CompanyID, "SO")
                is_SaleOrderOK = True
            elif is_voucherExist == False:
                is_SaleOrderOK = True
            else:
                is_SaleOrderOK = False

            if is_SaleOrderOK:
                update_voucher_table(
                    CompanyID, CreatedUserID, VoucherType, PreFix, Seperator, InvoiceNo)
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
                        try:
                            Flavour = saleOrdersDetail['Flavour']
                        except:
                            Flavour = ""

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
                            ProductTaxID=ProductTaxID,
                            Flavour=Flavour
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
                            ProductTaxID=ProductTaxID,
                            Flavour=Flavour
                        )

                #request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sale Orders',
                #              'Create', 'Sale Orders created successfully.', 'Sale Orders saved successfully.')

                response_data = {
                    "StatusCode": 6000,
                    "message": "Sale Orders created Successfully!!!",
                    "OrderID": instance.id
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
            TotalGrossAmt = data['TotalGrossAmt']
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

            Action = "M"

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

            VoucherType = "SO"

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
                TotalGrossAmt=TotalGrossAmt,
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
            salesOrderMaster_instance.TotalGrossAmt = TotalGrossAmt
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
                        
                    try:
                        Flavour = saleOrdersDetail['Flavour']
                    except:
                        Flavour = ""

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
                            ProductTaxID=ProductTaxID,
                            Flavour=Flavour
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
                        salesDetail_instance.Flavour = Flavour
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
                            ProductTaxID=ProductTaxID,
                            Flavour=Flavour,
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
                            ProductTaxID=ProductTaxID,
                            Flavour=Flavour,
                        )

            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sale Orders',
            #              'Edit', 'Sale Orders Updated successfully.', 'Sale Orders Updated successfully.')

            response_data = {
                "StatusCode": 6000,
                "message": "SalesOrder Updated Successfully!!!",
                "OrderID": salesOrderMaster_instance.id
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
        if SalesOrderMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Table=instance).exists():
            is_exist = True

        response_data = {
            "StatusCode": 6000,
            "is_exist": is_exist,
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
    try:
        IsPosUser = data['IsPosUser']
    except:
        IsPosUser = False
    CompanyID.IsPosUser = IsPosUser
    CompanyID.save()
    warehouse_instance = Warehouse.objects.get(id=warehouse_id)
    if POS_Settings.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        instance = POS_Settings.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID).first()
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
        "message": "success"
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def view_pos_salesOrder(request, pk):
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

            try:
                paid = data['paid']
            except:
                paid = True

            try:
                table_vacant = data['table_vacant']
            except:
                table_vacant = False
            
            try:
                TotalTax = data['TotalTax']
            except:
                TotalTax = sales_order_instance.TotalTax

            Cash_Account = None
            Bank_Account = None

            if UserTable.objects.filter(CompanyID=CompanyID, customer__user__pk=CreatedUserID).exists():
                Cash_Account = UserTable.objects.get(
                    CompanyID=CompanyID, customer__user__pk=CreatedUserID).Cash_Account
                Bank_Account = UserTable.objects.get(
                    CompanyID=CompanyID, customer__user__pk=CreatedUserID).Bank_Account

            Action = "A"
            VoucherType = "SI"

            CashID = Cash_Account
            BankID = Bank_Account

            sales_order_instance = SalesOrderMaster.objects.get(
                id=SalesOrderID, CompanyID=CompanyID)
            sales_order_instance.Status = "Paid"
            sales_order_instance.IsInvoiced = "I"
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
            IsActive = sales_order_instance.IsActive
            TaxID = sales_order_instance.TaxID
            TaxType = sales_order_instance.TaxType
            FinacialYearID = sales_order_instance.FinacialYearID
            TotalGrossAmt = sales_order_instance.TotalGrossAmt
            TotalTax = TotalTax
            NetTotal = sales_order_instance.NetTotal
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
            OrderNo = sales_order_instance.VoucherNo

            order_details = SalesOrderDetails.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, SalesOrderMasterID=SalesOrderMasterID)
            TotalTaxableAmount = 0
            for i in order_details:
                TotalTaxableAmount += i.TaxableAmount

            # VoucherNo Updated
            VoucherNo = get_VoucherNoForPOS(
                CompanyID, BranchID, CreatedUserID, "SI")
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
                if POS_Table.objects.filter(CompanyID=CompanyID, BranchID=BranchID, id=Table).exists():
                    table_ins = POS_Table.objects.get(
                        CompanyID=CompanyID, BranchID=BranchID, id=Table)
                    table_ins.Status = "Paid"
                    if table_vacant == True:
                        table_ins.Status = "Vacant"
                    table_ins.save()

            # checking voucher number already exist
            VoucherNoLow = VoucherNo.lower()
            is_voucherExist = False
            insts = SalesMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
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
                    BranchID=BranchID, CompanyID=CompanyID, SettingsType="VoucherNoAutoGenerate").SettingsValue

            if is_voucherExist == True and check_VoucherNoAutoGenerate == "True":
                VoucherNo = get_Genrate_VoucherNo(
                    SalesMaster, BranchID, CompanyID, "SI")
                is_SaleOK = True
            elif is_voucherExist == False:
                is_SaleOK = True
            else:
                is_SaleOK = False

            if is_SaleOK:

                SalesMasterID = invoice_master_id(
                    SalesMaster, BranchID, CompanyID)
                sales_order_instance.InvoiceID = SalesMasterID
                TokenNumber = sales_order_instance.TokenNumber
                sales_order_instance.save()
                # if Parties.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID).exists():
                #     party_instances = Parties.objects.filter(
                #         CompanyID=CompanyID, LedgerID=LedgerID)
                #     for party_instance in party_instances:
                #         party_instance.PartyName = CustomerName
                #         party_instance.save()

                if AllowCashReceiptMoreSaleAmt == True or AllowCashReceiptMoreSaleAmt == "true":
                    CashAmount = CashReceived
                elif converted_float(Balance) < 0:
                    CashAmount = converted_float(GrandTotal) - converted_float(BankAmount)
                else:
                    CashAmount = CashReceived
                    
                Country_of_Supply = CompanyID.Country.id
                State_of_Supply = CompanyID.State.id
                GST_Treatment = "2"
                VAT_Treatment = "1"

                update_voucher_table(
                    CompanyID, CreatedUserID, VoucherType, PreFix, Seperator, InvoiceNo)
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
                    Table=table_ins,
                    Country_of_Supply=Country_of_Supply,
                    State_of_Supply=State_of_Supply,
                    GST_Treatment=GST_Treatment,
                    VAT_Treatment=VAT_Treatment,
                    OrderNo=OrderNo,
                    Type=Type
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
                    Table=table_ins,
                    Country_of_Supply=Country_of_Supply,
                    State_of_Supply=State_of_Supply,
                    GST_Treatment=GST_Treatment,
                    VAT_Treatment=VAT_Treatment,
                    OrderNo=OrderNo,
                    Type=Type
                )
                # ======QRCODE==========
                if CompanyID.is_vat and CompanyID.VATNumber:
                    tax_number = CompanyID.VATNumber
                elif CompanyID.is_gst and CompanyID.GSTNumber:
                    tax_number = CompanyID.GSTNumber
                else:
                    tax_number = ""
                # url = str("https://viknbooks.vikncodes.com/invoice/") + \
                #     str(sales_instance.pk)+str('/') + str('SI')
                # url = str("https://viknbooks.com/invoice/") + str(sales_instance.pk)+str('/')+ str('SI')
                # url = str("http://localhost:3000/invoice/") + str(sales_instance.pk)+str('/')+ str('SI')
                fatoora_obj = Fatoora(
                    seller_name=CompanyID.CompanyName,
                    tax_number=tax_number,  # or "1234567891"
                    invoice_date=str(sales_instance.CreatedDate),  # Timestamp
                    total_amount=GrandTotal,  # or 100.0, 100.00, "100.0", "100.00"
                    tax_amount=TotalTax,  # or 15.0, 15.00, "15.0", "15.00"
                )
                url = fatoora_obj.base64
                qr_instance = QrCode.objects.create(
                    voucher_type="SI",
                    master_id=sales_instance.pk,
                    url=url,
                )

                account_group = AccountLedger.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).AccountGroupUnder

                if TaxType == 'VAT':
                    if converted_float(VATAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        # VAT on Sales
                        vat_on_sales = get_BranchLedgerId_for_LedgerPosting(
                            BranchID, CompanyID, 'vat_on_sales')

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=vat_on_sales,
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
                            LedgerID=vat_on_sales,
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
                            RelatedLedgerID=vat_on_sales,
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
                            RelatedLedgerID=vat_on_sales,
                            Debit=VATAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                elif TaxType == 'GST Intra-state B2B' or TaxType == 'GST Intra-state B2C':
                    if converted_float(CGSTAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        # Central GST on Sales
                        central_gst_on_sales = get_BranchLedgerId_for_LedgerPosting(
                            BranchID, CompanyID, 'central_gst_on_sales')

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=central_gst_on_sales,
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
                            LedgerID=central_gst_on_sales,
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
                            RelatedLedgerID=central_gst_on_sales,
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
                            RelatedLedgerID=central_gst_on_sales,
                            Debit=CGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                    if converted_float(SGSTAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        # State GST on Sales
                        state_gst_on_sales = get_BranchLedgerId_for_LedgerPosting(
                            BranchID, CompanyID, 'state_gst_on_sales')

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=state_gst_on_sales,
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
                            LedgerID=state_gst_on_sales,
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
                            RelatedLedgerID=state_gst_on_sales,
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
                            RelatedLedgerID=state_gst_on_sales,
                            Debit=SGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                    if converted_float(KFCAmount) > 0:

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
                    if converted_float(IGSTAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        # Integrated GST on Sales
                        integrated_gst_on_sales = get_BranchLedgerId_for_LedgerPosting(
                            BranchID, CompanyID, 'integrated_gst_on_sales')

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=integrated_gst_on_sales,
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
                            LedgerID=integrated_gst_on_sales,
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
                            RelatedLedgerID=integrated_gst_on_sales,
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
                            RelatedLedgerID=integrated_gst_on_sales,
                            Debit=IGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                if not TaxType == 'Export':
                    if converted_float(TAX1Amount) > 0:
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

                    if converted_float(TAX2Amount) > 0:
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

                    if converted_float(TAX3Amount) > 0:
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

                if converted_float(RoundOff) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    # Round off Sales
                    round_off_sales = get_BranchLedgerId_for_LedgerPosting(
                        BranchID, CompanyID, 'round_off_sales')

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=round_off_sales,
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
                        LedgerID=round_off_sales,
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
                        RelatedLedgerID=round_off_sales,
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
                        RelatedLedgerID=round_off_sales,
                        Debit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                if converted_float(RoundOff) < 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    RoundOff = abs(converted_float(RoundOff))
                    # Round off Sales
                    round_off_sales = get_BranchLedgerId_for_LedgerPosting(
                        BranchID, CompanyID, 'round_off_sales')

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=round_off_sales,
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
                        LedgerID=round_off_sales,
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
                        RelatedLedgerID=round_off_sales,
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
                        RelatedLedgerID=round_off_sales,
                        Credit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                if converted_float(TotalDiscount) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    # Discount on Sales
                    discount_on_sales = get_BranchLedgerId_for_LedgerPosting(
                        BranchID, CompanyID, 'discount_on_sales')

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=discount_on_sales,
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
                        LedgerID=discount_on_sales,
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
                        RelatedLedgerID=discount_on_sales,
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
                        RelatedLedgerID=discount_on_sales,
                        Credit=TotalDiscount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                # credit sales start here
                if converted_float(CashReceived) == 0 and converted_float(BankAmount) == 0:
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
                elif (account_group == 10 or account_group == 29 or account_group == 32) and converted_float(CashReceived) > 0 and converted_float(BankAmount) == 0:
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
                elif (account_group == 10 or account_group == 29 or account_group == 32) and converted_float(CashReceived) == 0 and converted_float(BankAmount) > 0:
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
                elif (account_group == 8 or account_group == 9) and converted_float(CashReceived) > 0 and converted_float(BankAmount) == 0:
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

                    csh_value = converted_float(GrandTotal) - converted_float(CashReceived)
                    if converted_float(csh_value) > 0:
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
                elif (account_group == 8 or account_group == 9) and converted_float(CashReceived) == 0 and converted_float(BankAmount) > 0:
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

                    bnk_value = converted_float(GrandTotal) - converted_float(BankAmount)
                    if not converted_float(bnk_value) == 0:
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
                elif (account_group == 10 or account_group == 29 or account_group == 32) and converted_float(CashReceived) > 0 and converted_float(BankAmount) > 0:
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
                elif (account_group == 9 or account_group == 8) and converted_float(CashReceived) > 0 and converted_float(BankAmount) > 0:
                    if converted_float(Balance) > 0:
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

                        UnitPrice = converted_float(order.UnitPrice)
                        InclusivePrice = converted_float(order.InclusivePrice)
                        RateWithTax = converted_float(order.RateWithTax)
                        # CostPerPrice = converted_float(order.CostPerPrice)
                        AddlDiscPerc = 0
                        AddlDiscAmt = 0
                        DiscountPerc = order.DiscountPerc
                        DiscountAmount = order.DiscountAmount
                        GrossAmount = converted_float(order.GrossAmount)
                        TaxableAmount = converted_float(order.TaxableAmount)
                        VATPerc = converted_float(order.VATPerc)
                        VATAmount = converted_float(order.VATAmount)
                        SGSTPerc = converted_float(order.SGSTPerc)
                        SGSTAmount = converted_float(order.SGSTAmount)
                        CGSTPerc = converted_float(order.CGSTPerc)
                        CGSTAmount = converted_float(order.CGSTAmount)
                        IGSTPerc = converted_float(order.IGSTPerc)
                        IGSTAmount = converted_float(order.IGSTAmount)
                        NetAmount = converted_float(order.NetAmount)
                        KFCAmount = converted_float(order.KFCAmount)
                        TAX1Perc = converted_float(order.TAX1Perc)
                        TAX1Amount = converted_float(order.TAX1Amount)
                        TAX2Perc = converted_float(order.TAX2Perc)
                        TAX2Amount = converted_float(order.TAX2Amount)
                        TAX3Perc = converted_float(order.TAX3Perc)
                        TAX3Amount = converted_float(order.TAX3Amount)
                        ProductTaxID = order.ProductTaxID

                        CostPerPrice = PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=PriceListID).PurchasePrice

                        SerialNos = []
                        Description = ""
                        KFCPerc = 0

                        if is_inclusive == True:
                            Batch_salesPrice = InclusivePrice
                        else:
                            Batch_salesPrice = UnitPrice

                        product_is_Service = Product.objects.get(
                            CompanyID=CompanyID, ProductID=ProductID).is_Service

                        product_purchasePrice = PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=PriceListID).PurchasePrice
                        MultiFactor = PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=PriceListID).MultiFactor

                        qty_batch = converted_float(FreeQty) + converted_float(Qty)
                        Qty_batch = converted_float(MultiFactor) * converted_float(qty_batch)

                        check_AllowUpdateBatchPriceInSales = False

                        if product_is_Service == False:
                            if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="AllowUpdateBatchPriceInSales").exists():
                                check_AllowUpdateBatchPriceInSales = GeneralSettings.objects.get(
                                    BranchID=BranchID, CompanyID=CompanyID, SettingsType="AllowUpdateBatchPriceInSales").SettingsValue

                            if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
                                check_EnableProductBatchWise = GeneralSettings.objects.get(
                                    BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
                                # check_BatchCriteria = "PurchasePriceAndSalesPrice"

                                if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                                    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
                                        if check_AllowUpdateBatchPriceInSales == "True" or check_AllowUpdateBatchPriceInSales == True:
                                            batch_ins = Batch.objects.get(
                                                CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode)
                                            StockOut = batch_ins.StockOut
                                            BatchCode = batch_ins.BatchCode
                                            NewStock = converted_float(
                                                StockOut) + converted_float(Qty_batch)
                                            batch_ins.StockOut = NewStock
                                            batch_ins.SalesPrice = Batch_salesPrice
                                            batch_ins.save()
                                        else:
                                            batch_ins = Batch.objects.get(
                                                CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode)
                                            StockOut = batch_ins.StockOut
                                            BatchCode = batch_ins.BatchCode
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
                                    CompanyID=CompanyID, PriceListID=PriceListID)
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

                            qty = converted_float(FreeQty) + converted_float(Qty)

                            Qty = converted_float(MultiFactor) * converted_float(qty)
                            Cost = converted_float(CostPerPrice) / converted_float(MultiFactor)

                            # Qy = round(Qty, 4)
                            # Qty = str(Qy)

                            # Ct = round(Cost, 4)
                            # Cost = str(Ct)

                            princeList_instance = PriceList.objects.get(
                                CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID_DefUnit, BranchID=BranchID)
                            PurchasePrice = princeList_instance.PurchasePrice
                            SalesPrice = princeList_instance.SalesPrice

                            pricelist, warehouse = get_ModelInstance(
                                CompanyID, BranchID, PriceListID, WarehouseID)
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
                                pricelist=pricelist,
                                warehouse=warehouse
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

                            update_stock(CompanyID, BranchID, ProductID)

                #request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sale Orders',
                #              'Create', 'Sale Orders created successfully.', 'Sale Orders saved successfully.')

                response_data = {
                    "StatusCode": 6000,
                    "message": "Sale Invoice created Successfully!!!",
                    "invoice_id": sales_instance.id
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

        activity_id = activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Sales invoice pos',
                     'Create', str(e), err_descrb)
        body_params = str(request.data)
        Activity_Log.objects.filter(
            id=activity_id).update(body_params=body_params)
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

    TokenNumber = get_TokenNo(CompanyID, BranchID)

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
        if POS_Table.objects.filter(CompanyID=CompanyID, BranchID=BranchID, id=unqid).exists():
            instance = POS_Table.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, id=unqid)
            instance.Status = "Vacant"
            instance.save()
            is_success = True
    elif Type == "Dining&Cancel":
        if POS_Table.objects.filter(CompanyID=CompanyID, BranchID=BranchID, id=unqid).exists():
            instance = POS_Table.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, id=unqid)
            if SalesOrderMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Table__Status="Ordered").exists():
                order_instance = SalesOrderMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, Table__Status="Ordered").first()
                order_instance.Status = "Cancelled"
                if CancelReasons.objects.filter(id=reason_id).exists():
                    reason_instance = CancelReasons.objects.get(id=reason_id)
                    order_instance.CancelReason = reason_instance
                order_instance.save()
            instance.Status = "Vacant"
            instance.save()
            is_success = True
    else:
        if SalesOrderMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, id=unqid).exists():
            instance = SalesOrderMaster.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, id=unqid)
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

    if CancelReasons.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        instance = CancelReasons.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID)
        serialized = OrderReason_Serializer(
            instance, many=True, context={"CompanyID": CompanyID})

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

            serialized = POS_Product_Serializer(instances, many=True, context={
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
        owner=userId, is_deleted=False, business_type__Name="Restaurant")
    my_company_serialized = MyCompaniesSerializer(
        my_company_instances, many=True)
    my_company_json = convertOrderdDict(my_company_serialized.data)

    member_company_instances = models.UserTable.objects.filter(
        customer__user=userId, CompanyID__business_type__Name="Restaurant")
    member_company_serialized = CompaniesSerializer(
        member_company_instances, many=True)
    member_company_json = convertOrderdDict(member_company_serialized.data)

    data = []
    for i in my_company_json:
        id = i['id']
        CompanyImage = ""
        if my_company_instances.get(id=id).CompanyLogo:
            CompanyImage = my_company_instances.get(id=id).CompanyLogo.url
        CompanyName = i['CompanyName']
        company_type = i['company_type']
        ExpiryDate = i['ExpiryDate']
        Permission = i['Permission']
        Edition = i['Edition']
        IsPosUser = i['IsPosUser']
        ExpiryDate = date.today().strftime("%Y-%m-%d")
        if i['ExpiryDate'] != None:
            ExpiryDate = i['ExpiryDate']
        dic = {
            'id': id,
            'CompanyName': CompanyName,
            'company_type': company_type,
            'ExpiryDate': ExpiryDate,
            'Permission': Permission,
            'Edition': Edition,
            'IsPosUser': IsPosUser,
            'CompanyImage': CompanyImage
        }
        data.append(dic)

    for i in member_company_json:
        id = i['id']
        CompanyImage = ""
        if models.CompanySettings.objects.get(id=id).CompanyLogo:
            CompanyImage = models.CompanySettings.objects.get(
                id=id).CompanyLogo.url
        CompanyName = i['CompanyName']
        company_type = i['company_type']
        Permission = i['Permission']
        Edition = i['Edition']
        IsPosUser = i['IsPosUser']
        ExpiryDate = date.today().strftime("%Y-%m-%d")
        if i['ExpiryDate'] != None:
            ExpiryDate = i['ExpiryDate']
        dic = {
            'id': id,
            'CompanyName': CompanyName,
            'company_type': company_type,
            'ExpiryDate': ExpiryDate,
            'Permission': Permission,
            'Edition': Edition,
            'IsPosUser': IsPosUser,
            'CompanyImage': CompanyImage
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
            instance = models.SalesMaster.objects.get(
                CompanyID=CompanyID, pk=pk)
            serialized = POS_Sales_PrintSerializer(
                instance, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding, "request": request, })

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
            instance = models.SalesOrderMaster.objects.get(
                CompanyID=CompanyID, pk=pk)
            serialized = POS_SalesOrder_PrintSerializer(
                instance, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding, "request": request, })

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
        if models.AccountLedger.objects.filter(CompanyID=CompanyID).exists():
            AccountGroupUnder_list = [10, 29]

            if ledger_name:
                if converted_float(length) < 3:
                    instances = models.AccountLedger.objects.filter(
                        CompanyID=CompanyID, LedgerName__icontains=ledger_name, AccountGroupUnder__in=AccountGroupUnder_list)[:10]
                else:
                    instances = models.AccountLedger.objects.filter(
                        CompanyID=CompanyID, LedgerName__icontains=ledger_name, AccountGroupUnder__in=AccountGroupUnder_list)
            elif load_data:
                instances = models.AccountLedger.objects.filter(
                    CompanyID=CompanyID, AccountGroupUnder__in=AccountGroupUnder_list)[:10]
            else:
                instances = models.AccountLedger.objects.filter(
                    CompanyID=CompanyID, AccountGroupUnder__in=AccountGroupUnder_list)

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
                    "LedgerID": LedgerID,
                    "LedgerName": LedgerName,
                    "OpeningBalance": OpeningBalance,
                    "CustomerLedgerBalance": CustomerLedgerBalance,
                    "AccountGroupUnder": AccountGroupUnder,
                })

            walkincustomer = {
                "LedgerID": 1,
                "LedgerName": "walk in customer",
                "OpeningBalance": 0,
                "CustomerLedgerBalance": 0,
                "AccountGroupUnder": 10,
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
        if Kitchen.objects.filter(CompanyID=CompanyID,BranchID=BranchID,KitchenName=KitchenName).exists():
            StatusCode = 6002
            message = "Kitchen name already exist!"
        else:
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

    if Kitchen.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        instance = Kitchen.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID)
        serialized = Kitchen_Serializer(
            instance, many=True, context={"CompanyID": CompanyID})

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
def view_pos_kitchen(request,pk):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']

    if Kitchen.objects.filter(pk=pk).exists():
        instance = Kitchen.objects.get(pk=pk)
        serialized = Kitchen_Serializer(
            instance, context={"CompanyID": CompanyID})

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
    try:
        is_test = data['is_test']
    except:
        is_test = False
        
    final_data = []
    if Kitchen.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        kitchens = Kitchen.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID)
        for k in kitchens:
            if ProductGroup.objects.filter(CompanyID=CompanyID, BranchID=BranchID, kitchen=k).exists():
                kitchen_groups = ProductGroup.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, kitchen=k)
                group_ids = kitchen_groups.values_list(
                    'ProductGroupID', flat=True)
                products = Product.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductGroupID__in=group_ids)
                group_productids = products.values_list('ProductID', flat=True)

                if SalesOrderMaster.objects.filter(id=OrderID).exists():
                    instance = SalesOrderMaster.objects.get(id=OrderID)
                    SalesOrderMasterID = instance.SalesOrderMasterID
                    detail_instances = SalesOrderDetails.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, SalesOrderMasterID=SalesOrderMasterID, KitchenPrint=False)
                    # productids = detail_instances.values_list('ProductID',flat=True)
                    # details_products = Product.objects.filter(CompanyID=CompanyID,BranchID=BranchID,ProductID__in=productids)
                    Items = []
                    TotalQty = 0
                    for p in detail_instances:
                        if p.ProductID in group_productids:
                            ProductName = products.filter(
                                ProductID=p.ProductID).first().ProductName
                            ProductDescription = products.filter(
                                ProductID=p.ProductID).first().Description
                            TableName = ""
                            Type = ""
                            TokenNumber = ""
                            if instance.Table:
                                TableName = instance.Table.TableName
                            items = {
                                "ProductName": ProductName,
                                "ProductDescription": ProductDescription,
                                "Qty": p.Qty,
                                "TableName": TableName,
                                "OrderType": instance.Type,
                                "TokenNumber": instance.TokenNumber,
                                "VoucherNo": instance.VoucherNo,
                            }
                            TotalQty += converted_float(p.Qty)
                            Items.append(items)
                            if is_test == False:
                                p.KitchenPrint = True
                            p.save()
                    if Items:
                        final_data.append({
                            "kitchen_name": k.KitchenName,
                            "IPAddress": k.IPAddress,
                            "Items": Items,
                            "TotalQty": TotalQty
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


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def table_create(request):
    today = datetime.datetime.now()
    data = request.data

    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    TableName = data['TableName']
    IsActive = data['IsActive']
    PriceCategoryID = data['PriceCategoryID']

    position = POS_Table.objects.filter(
        CompanyID=CompanyID, BranchID=BranchID).count()

    priceCategory = None
    if PriceCategoryID:
        if PriceCategory.objects.filter(id=PriceCategoryID).exists():
            priceCategory = PriceCategory.objects.get(id=PriceCategoryID)

    if not POS_Table.objects.filter(CompanyID=CompanyID, BranchID=BranchID, TableName=TableName).exists():
        pos = POS_Table.objects.create(
            CompanyID=CompanyID,
            BranchID=BranchID,
            TableName=TableName,
            IsActive=IsActive,
            PriceCategory=priceCategory,
            Position=position + 1,
        )

        POS_Table_log.objects.create(
            MasterID=pos.id,
            CompanyID=CompanyID,
            BranchID=BranchID,
            TableName=TableName,
            IsActive=IsActive,
            PriceCategory=priceCategory,
            Position=position + 1,
        )

        response_data = {
            "StatusCode": 6000,
            "message": "Table Name created successfully",
            "name": TableName
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Table already exists with name " + TableName,
            "name": TableName
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def table_list(request):
    today = datetime.datetime.now()
    data = request.data

    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']

    if POS_Table.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        table_instances = POS_Table.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID)
        serialized = POS_Table_Serializer1(table_instances, many=True)

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Tables not Found",
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def table_delete(request):
    today = datetime.datetime.now()
    data = request.data

    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    TableName = data['TableName']

    if POS_Table.objects.filter(CompanyID=CompanyID, BranchID=BranchID, TableName=TableName).exists():
        table_instances = POS_Table.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, TableName=TableName).first()

        POS_Table_log.objects.create(
            MasterID=table_instances.id,
            CompanyID=CompanyID,
            BranchID=BranchID,
            TableName=table_instances.TableName,
            IsActive=table_instances.IsActive,
            PriceCategory=table_instances.PriceCategory,
            Position=table_instances.Position,
        )
        table_instances.delete()
        response_data = {
            "StatusCode": 6000,
            "message": "Table Deleted Successfully"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Tables not Found",
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def get_defaults(request):
    data = request.data
    CompanyID = data['CompanyID']
    BranchID = data['BranchID']
    userId = data['userId']
    Sales_Account_name = ""
    Sales_Return_Account_name = ""
    Purchase_Account_name = ""
    Purchase_Return_Account_name = ""
    Cash_Account_name = ""
    Bank_Account_name = ""
    Warehouse_name = ""
    VAT_Type_name = ""
    Sales_GST_Type_name = ""
    Purchase_GST_Type_name = ""
    Sales_VAT_Type_name = ""
    Purchase_VAT_Type_name = ""
    CompanyName = get_company(CompanyID).CompanyName
    CRNumber = get_company(CompanyID).CRNumber
    CINNumber = get_company(CompanyID).CINNumber
    Description = get_company(CompanyID).Description
    IsTrialVersion = get_company(CompanyID).IsTrialVersion
    Edition = get_company(CompanyID).Edition
    # usertable exceed delete
    NoOfUsers = int(get_company(CompanyID).NoOfUsers)
    VATNumber = get_company(CompanyID).VATNumber
    GSTNumber = get_company(CompanyID).GSTNumber
    Phone = get_company(CompanyID).Phone
    usertable_count = administrations_models.UserTable.objects.filter(
        CompanyID=CompanyID).count()
    if usertable_count > NoOfUsers:
        corrent_user = usertable_count - NoOfUsers
        last_user_table_instance = administrations_models.UserTable.objects.filter(CompanyID=CompanyID)[
            corrent_user:]
        administrations_models.UserTable.objects.exclude(
            CompanyID=CompanyID, pk__in=last_user_table_instance).delete()
    # # usertable exceed delete ends here
    today = str(datetime.date.today())
    ExpiryDate = administrations_models.CompanySettings.objects.get(
        pk=CompanyID).ExpiryDate
    DefaultAccountForUser = False
    Sales_Account = 85
    Sales_Return_Account = 86
    Purchase_Account = 69
    Purchase_Return_Account = 70
    Cash_Account = 1
    Bank_Account = 92
    WarehouseID = 1
    company_expire_date = ExpiryDate
    is_owner = True
    user_type = ""
    # =============Uvais================
    # ===========VAT======
    vat = False
    gst = False
    if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="VAT").exists():
        vat = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="VAT").SettingsValue
    if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="GST").exists():
        gst = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="GST").SettingsValue
    comapny_instance = get_company(CompanyID)
    if vat == "true" or vat == "True" or vat == True:
        vat = True
    else:
        vat = False
    if gst == "true" or gst == "True" or gst == True:
        gst = True
    else:
        gst = False
    comapny_instance.is_gst = gst
    comapny_instance.is_vat = vat
    comapny_instance.save()

    if not administrations_models.MasterType.objects.filter(CompanyID__pk=CompanyID, BranchID=BranchID, Name="Loyalty Card Type").exists():
        MasterTypeID = get_master_auto_id(MasterType, BranchID, CompanyID)
        # if CompanySettings.objects.filter(pk=CompanyID).exists():
        comp_instance = administrations_models.CompanySettings.objects.get(
            pk=CompanyID)
        administrations_models.MasterType.objects.create(
            BranchID=BranchID,
            MasterTypeID=MasterTypeID,
            Name="Loyalty Card Type",
            Action="A",

            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=userId,
            CompanyID=comp_instance,
        )
        administrations_models.MasterType_Log.objects.create(
            BranchID=BranchID,
            TransactionID=MasterTypeID,
            Name="Loyalty Card Type",
            Action="A",

            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=userId,
            CompanyID=comp_instance,
        )
    if not administrations_models.MasterType.objects.filter(CompanyID__pk=CompanyID, BranchID=BranchID, Name="Loyalty Card Status").exists():
        MasterTypeID = get_master_auto_id(
            administrations_models.MasterType, BranchID, CompanyID)
        comp_instance = administrations_models.CompanySettings.objects.get(
            pk=CompanyID)
        administrations_models.MasterType.objects.create(
            BranchID=BranchID,
            MasterTypeID=MasterTypeID,
            Name="Loyalty Card Status",
            Action="A",

            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=userId,
            CompanyID=comp_instance,
        )
        administrations_models.MasterType_Log.objects.create(
            BranchID=BranchID,
            TransactionID=MasterTypeID,
            Name="Loyalty Card Status",
            Action="A",

            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=userId,
            CompanyID=comp_instance,
        )
    # =============End================

    if administrations_models.UserTable.objects.filter(CompanyID__pk=CompanyID, customer__user=userId).exists():
        user_table_instance = administrations_models.UserTable.objects.get(
            CompanyID__pk=CompanyID, customer__user=userId)
        DefaultAccountForUser = administrations_models.UserTable.objects.get(
            CompanyID=CompanyID, customer__user__pk=userId).DefaultAccountForUser
        Cash_Account = user_table_instance.Cash_Account
        Bank_Account = user_table_instance.Bank_Account
        Sales_Account = user_table_instance.Sales_Account
        Sales_Return_Account = user_table_instance.Sales_Return_Account
        Purchase_Account = user_table_instance.Purchase_Account
        Purchase_Return_Account = user_table_instance.Purchase_Return_Account
        ExpiryDate = user_table_instance.ExpiryDate
        is_owner = user_table_instance.is_owner
        user_type = user_table_instance.UserType.ID

        if administrations_models.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Sales_Account).exists():
            Sales_Account_name = get_object_or_404(administrations_models.AccountLedger.objects.filter(
                CompanyID=CompanyID, LedgerID=Sales_Account)).LedgerName

        if administrations_models.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Sales_Return_Account).exists():
            Sales_Return_Account_name = get_object_or_404(administrations_models.AccountLedger.objects.filter(
                CompanyID=CompanyID, LedgerID=Sales_Return_Account)).LedgerName

        if administrations_models.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Purchase_Account).exists():
            Purchase_Account_name = get_object_or_404(administrations_models.AccountLedger.objects.filter(
                CompanyID=CompanyID, LedgerID=Purchase_Account)).LedgerName

        if administrations_models.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Purchase_Return_Account).exists():
            Purchase_Return_Account_name = get_object_or_404(administrations_models.AccountLedger.objects.filter(
                CompanyID=CompanyID, LedgerID=Purchase_Return_Account)).LedgerName

        if administrations_models.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Cash_Account).exists():
            Cash_Account_name = get_object_or_404(administrations_models.AccountLedger.objects.filter(
                CompanyID=CompanyID, LedgerID=Cash_Account)).LedgerName

        if administrations_models.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Bank_Account).exists():
            Bank_Account_name = get_object_or_404(administrations_models.AccountLedger.objects.filter(
                CompanyID=CompanyID, LedgerID=Bank_Account)).LedgerName

        if administrations_models.Warehouse.objects.filter(CompanyID=CompanyID, WarehouseID=WarehouseID, BranchID=BranchID).exists():
            Warehouse_name = get_object_or_404(administrations_models.Warehouse.objects.filter(
                CompanyID=CompanyID, WarehouseID=WarehouseID, BranchID=BranchID)).WarehouseName

    Country = ''
    CountryName = ''
    State = ''
    StateName = ''
    State_Code = ''
    CompanyLogo = ''
    Address1 = ''
    Address2 = ''
    Address3 = ''
    City = ''
    BussinesType = ''
    if administrations_models.CompanySettings.objects.filter(id=CompanyID).exists():
        com_ins = administrations_models.CompanySettings.objects.get(
            id=CompanyID)
        BussinesType = com_ins.business_type.Name
        Country = administrations_models.CompanySettings.objects.get(
            id=CompanyID).Country.id
        CountryName = administrations_models.CompanySettings.objects.get(
            id=CompanyID).Country.Country_Name
        CurrencySymbol = administrations_models.CompanySettings.objects.get(
            id=CompanyID).Country.Symbol
        State = administrations_models.CompanySettings.objects.get(
            id=CompanyID).State.id
        StateName = administrations_models.CompanySettings.objects.get(
            id=CompanyID).State.Name
        State_Code = administrations_models.CompanySettings.objects.get(
            id=CompanyID).State.State_Code
        if administrations_models.CompanySettings.objects.get(id=CompanyID).CompanyLogo:
            CompanyLogo = administrations_models.CompanySettings.objects.get(
                id=CompanyID).CompanyLogo.url
        if administrations_models.CompanySettings.objects.get(id=CompanyID).City:
            City = administrations_models.CompanySettings.objects.get(
                id=CompanyID).City

        if administrations_models.CompanySettings.objects.get(id=CompanyID).Address1:
            Address1 = administrations_models.CompanySettings.objects.get(
                id=CompanyID).Address1
        if administrations_models.CompanySettings.objects.get(id=CompanyID).Address2:
            Address2 = administrations_models.CompanySettings.objects.get(
                id=CompanyID).Address2
        if administrations_models.CompanySettings.objects.get(id=CompanyID).Address3:
            Address3 = administrations_models.CompanySettings.objects.get(
                id=CompanyID).Address3

    if administrations_models.FinancialYear.objects.filter(CompanyID=CompanyID, IsClosed=False).exists():
        financialyear = administrations_models.FinancialYear.objects.filter(
            CompanyID=CompanyID, IsClosed=False).first()
        financial_FromDate = financialyear.FromDate
        financial_ToDate = financialyear.ToDate
    else:
        try:
            financialyear = administrations_models.FinancialYear.objects.filter(
                CompanyID=CompanyID).first()
            financial_FromDate = financialyear.FromDate
            financial_ToDate = financialyear.ToDate
        except:
            financial_FromDate = ""
            financial_ToDate = ""

    if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():

        QtyDecimalPoint = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="QtyDecimalPoint").SettingsValue
        PriceDecimalPoint = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="PriceDecimalPoint").SettingsValue
        Show_Sales_Type = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Show_Sales_Type").SettingsValue
        Show_Purchase_Type = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Show_Purchase_Type").SettingsValue
        Sales_VAT_Type = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Sales_VAT_Type").SettingsValue
        Purchase_VAT_Type = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Purchase_VAT_Type").SettingsValue
        Sales_GST_Type = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Sales_GST_Type").SettingsValue
        Purchase_GST_Type = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Purchase_GST_Type").SettingsValue

        RoundingFigure = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="RoundingFigure").SettingsValue
        RoundOffPurchase = 5
        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="RoundOffPurchase").exists():
            RoundOffPurchase = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="RoundOffPurchase").SettingsValue

        RoundOffSales = 5
        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="RoundOffSales").exists():
            RoundOffSales = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="RoundOffSales").SettingsValue

        Sales_VAT_Type = int(Sales_VAT_Type)
        Purchase_VAT_Type = int(Purchase_VAT_Type)
        Sales_GST_Type = int(Sales_GST_Type)
        Purchase_GST_Type = int(Purchase_GST_Type)

        PreDateTransaction = 30
        PostDateTransaction = 30
        EnableVoucherNoUserWise = True
        ShowSettingsinSales = False
        EnableProductBatchWise = False
        ShowYearMonthCalanderInWorkOrder = False
        BatchCriteria = ""
        loyalty_PointValue = ""

        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="loyalty_point_value").exists():
            loyalty_PointValue = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="loyalty_point_value").SettingsValue

        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="PreDateTransaction").exists():
            PreDateTransaction = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="PreDateTransaction").SettingsValue
        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="PostDateTransaction").exists():
            PostDateTransaction = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="PostDateTransaction").SettingsValue

        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="BatchCriteria").exists():
            BatchCriteria = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="BatchCriteria").SettingsValue

        # CompanyID, SettingsType
        EnableLoyaltySettings = get_general_settings(
            CompanyID, "EnableLoyaltySettings")
        CustomerBasedPrint = get_general_settings(
            CompanyID, "CustomerBasedPrint")
        Loyalty_Point_Expire = get_general_settings(
            CompanyID, "Loyalty_Point_Expire")
        is_Loyalty_SalesReturn_MinimumSalePrice = get_general_settings(
            CompanyID, "is_Loyalty_SalesReturn_MinimumSalePrice")
        MultiUnit = get_general_settings(CompanyID, "MultiUnit")
        AllowNegativeStockSales = get_general_settings(
            CompanyID, "AllowNegativeStockSales")
        PriceCategory = get_general_settings(CompanyID, "PriceCategory")
        BlockSalesPrice = get_general_settings(CompanyID, "BlockSalesPrice")
        VoucherNoAutoGenerate = get_general_settings(
            CompanyID, "VoucherNoAutoGenerate")
        EnableVoucherNoUserWise = get_general_settings(
            CompanyID, "EnableVoucherNoUserWise")
        ShowSalesPriceInPurchase = get_general_settings(
            CompanyID, "ShowSalesPriceInPurchase")
        ShowSettingsinSales = get_general_settings(
            CompanyID, "ShowSettingsinSales")
        ShowSettingsinPurchase = get_general_settings(
            CompanyID, "ShowSettingsinPurchase")
        EnableProductBatchWise = get_general_settings(
            CompanyID, "EnableProductBatchWise")
        AllowUpdateBatchPriceInSales = get_general_settings(
            CompanyID, "AllowUpdateBatchPriceInSales")
        SalesPriceUpdate = get_general_settings(CompanyID, "SalesPriceUpdate")
        PurchasePriceUpdate = get_general_settings(
            CompanyID, "PurchasePriceUpdate")
        EnableTransilationInProduct = get_general_settings(
            CompanyID, "EnableTransilationInProduct")
        ShowPositiveStockInSales = get_general_settings(
            CompanyID, "ShowPositiveStockInSales")
        ShowNegativeBatchInSales = get_general_settings(
            CompanyID, "ShowNegativeBatchInSales")
        CreateBatchForWorkOrder = get_general_settings(
            CompanyID, "CreateBatchForWorkOrder")
        KFC = get_general_settings(CompanyID, "KFC")
        blockSaleByBillDisct = get_general_settings(
            CompanyID, "blockSaleByBillDisct")
        AllowCashReceiptMoreSaleAmt = get_general_settings(
            CompanyID, "AllowCashReceiptMoreSaleAmt")
        AllowCashReceiptMorePurchaseAmt = get_general_settings(
            CompanyID, "AllowCashReceiptMorePurchaseAmt")
        AllowAdvanceReceiptinSales = get_general_settings(
            CompanyID, "AllowAdvanceReceiptinSales")
        AllowAdvanceReceiptinPurchase = get_general_settings(
            CompanyID, "AllowAdvanceReceiptinPurchase")
        AllowQtyDividerinSales = get_general_settings(
            CompanyID, "AllowQtyDividerinSales")
        InclusiveRatePurchase = get_general_settings(
            CompanyID, "InclusiveRatePurchase")
        InclusiveRateSales = get_general_settings(
            CompanyID, "InclusiveRateSales")
        InclusiveRateWorkOrder = get_general_settings(
            CompanyID, "InclusiveRateWorkOrder")
        ShowDiscountInSales = get_general_settings(
            CompanyID, "ShowDiscountInSales")
        ShowSupplierInSales = get_general_settings(
            CompanyID, "ShowSupplierInSales")
        EnableShippingCharge = get_general_settings(
            CompanyID, "EnableShippingCharge")
        ShowDueBalanceInSales = get_general_settings(
            CompanyID, "ShowDueBalanceInSales")
        ShowDueBalanceInPurchase = get_general_settings(
            CompanyID, "ShowDueBalanceInPurchase")
        ShowEmployeesInSales = get_general_settings(
            CompanyID, "ShowEmployeesInSales")
        EnableSerialNoInSales = get_general_settings(
            CompanyID, "EnableSerialNoInSales")
        EnableItemCodeNoInSales = get_general_settings(
            CompanyID, "EnableItemCodeNoInSales")
        EnableSalesManInSales = get_general_settings(
            CompanyID, "EnableSalesManInSales")
        ShowWarrantyPeriodInProduct = get_general_settings(
            CompanyID, "ShowWarrantyPeriodInProduct")
        ShowDescriptionInSales = get_general_settings(
            CompanyID, "ShowDescriptionInSales")
        AllowExtraSerielNos = get_general_settings(
            CompanyID, "AllowExtraSerielNos")
        Free_Quantity_In_Sales = get_general_settings(
            CompanyID, "Free_Quantity_In_Sales")
        Free_Quantity_In_Purchase = get_general_settings(
            CompanyID, "Free_Quantity_In_Purchase")
        ShowCustomerInPurchase = get_general_settings(
            CompanyID, "ShowCustomerInPurchase")
        ShowManDateAndExpDatePurchase = get_general_settings(
            CompanyID, "ShowManDateAndExpDatePurchase")
        ShowDiscountInPurchase = get_general_settings(
            CompanyID, "ShowDiscountInPurchase")
        ShowDiscountInPayments = get_general_settings(
            CompanyID, "ShowDiscountInPayments")
        ShowDiscountInReceipts = get_general_settings(
            CompanyID, "ShowDiscountInReceipts")
        EnableCardNetWork = get_general_settings(
            CompanyID, "EnableCardNetWork")
        BlockTransactionsByDate = get_general_settings(
            CompanyID, "BlockTransactionsByDate")
        EnableCardDetails = get_general_settings(
            CompanyID, "EnableCardDetails")

        Show_Sales_Type = get_general_settings(CompanyID, "Show_Sales_Type")
        Show_Purchase_Type = get_general_settings(
            CompanyID, "Show_Purchase_Type")
        TAX1 = get_general_settings(CompanyID, "TAX1")
        TAX2 = get_general_settings(CompanyID, "TAX2")
        TAX3 = get_general_settings(CompanyID, "TAX3")
        Additional_Discount = get_general_settings(
            CompanyID, "Additional_Discount")
        Bill_Discount = get_general_settings(CompanyID, "Bill_Discount")
        Negatine_Stock = get_general_settings(CompanyID, "Negatine_Stock")
        Increment_Qty_In_POS = get_general_settings(
            CompanyID, "Increment_Qty_In_POS")
        Kitchen_Print = get_general_settings(CompanyID, "Kitchen_Print")
        Order_Print = get_general_settings(CompanyID, "Order_Print")
        Print_After_Save_Active = get_general_settings(
            CompanyID, "Print_After_Save_Active")
        VAT = get_general_settings(CompanyID, "VAT")
        GST = get_general_settings(CompanyID, "GST")

        if TransactionTypes.objects.filter(CompanyID=CompanyID, TransactionTypesID=Sales_VAT_Type, BranchID=BranchID).exists():
            Sales_VAT_Type_name = get_object_or_404(TransactionTypes.objects.filter(
                CompanyID=CompanyID, TransactionTypesID=Sales_VAT_Type, BranchID=BranchID)).Name

        if TransactionTypes.objects.filter(CompanyID=CompanyID, TransactionTypesID=Purchase_VAT_Type, BranchID=BranchID).exists():
            Purchase_VAT_Type_name = get_object_or_404(TransactionTypes.objects.filter(
                CompanyID=CompanyID, TransactionTypesID=Purchase_VAT_Type, BranchID=BranchID)).Name

        if TransactionTypes.objects.filter(CompanyID=CompanyID, TransactionTypesID=Sales_GST_Type, BranchID=BranchID).exists():
            Sales_GST_Type_name = get_object_or_404(TransactionTypes.objects.filter(
                CompanyID=CompanyID, TransactionTypesID=Sales_GST_Type, BranchID=BranchID)).Name

        if TransactionTypes.objects.filter(CompanyID=CompanyID, TransactionTypesID=Purchase_GST_Type, BranchID=BranchID).exists():
            Purchase_GST_Type_name = get_object_or_404(TransactionTypes.objects.filter(
                CompanyID=CompanyID, TransactionTypesID=Purchase_GST_Type, BranchID=BranchID)).Name

        template = "template1"
        IsDefaultThermalPrinter = True
        PageSize = "3.14"
        IsCompanyLogo = True
        IsCompanyName = True
        IsDescription = True
        IsAddress = True
        IsMobile = True
        IsEmail = True
        IsTaxNo = True
        IsCRNo = True
        IsCurrentBalance = True
        SalesInvoiceTrName = "Sales Invoice"
        SalesOrderTrName = "Sales Order"
        SalesReturnTrName = "Sales Return"
        PurchaseInvoiceTrName = "Purchase Invoice"
        PurchaseOrderTrName = "Purchase Order"
        PurchaseReturnTrName = "Purchase Return"
        CashRecieptTrName = "Cash Reciept"
        BankRecieptTrName = "Bank Reciept"
        CashPaymentTrName = "Cash Payment"
        BankPaymentTrName = "Bank Payment"
        IsInclusiveTaxUnitPrice = True
        IsInclusiveTaxNetAmount = True
        IsFlavour = True
        IsShowDescription = True
        IsTotalQuantity = True
        IsTaxDetails = True
        IsHSNCode = True
        IsProductCode = True
        IsReceivedAmount = True
        # print bank details===START
        IsBankDetails = False
        BankNameFooter = ""
        AccountNumberFooter = ""
        BranchIFCFooter = ""
        # print bank details===END
        SalesInvoiceFooter = ""
        SalesReturnFooter = ""
        SalesOrderFooter = ""
        PurchaseInvoiceFooter = ""
        PurchaseOrderFooter = ""
        PurchaseReturnFooter = ""
        CashRecieptFooter = ""
        BankRecieptFooter = ""
        CashPaymentFooter = ""
        BankPaymentFooter = ""
        TermsAndConditionsSales = ""
        TermsAndConditionsPurchase = ""
        TermsAndConditionsSaleEstimate = ""
        HeadFontSize = ""
        BodyFontSize = ""
        ContentFontSize = ""
        FooterFontSize = ""
        if administrations_models.PrintSettings.objects.filter(CompanyID=CompanyID).exists():
            template = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).template
            IsDefaultThermalPrinter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsDefaultThermalPrinter
            PageSize = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).PageSize
            IsCompanyLogo = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsCompanyLogo
            IsCompanyName = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsCompanyName
            IsDescription = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsDescription
            IsAddress = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsAddress
            IsMobile = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsMobile
            IsEmail = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsEmail
            IsTaxNo = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsTaxNo
            IsCRNo = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsCRNo
            IsCurrentBalance = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsCurrentBalance
            SalesInvoiceTrName = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).SalesInvoiceTrName
            SalesOrderTrName = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).SalesOrderTrName
            SalesReturnTrName = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).SalesReturnTrName
            PurchaseInvoiceTrName = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).PurchaseInvoiceTrName
            PurchaseOrderTrName = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).PurchaseOrderTrName
            PurchaseReturnTrName = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).PurchaseReturnTrName
            CashRecieptTrName = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).CashRecieptTrName
            BankRecieptTrName = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).BankRecieptTrName
            CashPaymentTrName = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).CashPaymentTrName
            BankPaymentTrName = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).BankPaymentTrName
            IsInclusiveTaxUnitPrice = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsInclusiveTaxUnitPrice
            IsInclusiveTaxNetAmount = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsInclusiveTaxNetAmount
            IsFlavour = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsFlavour
            IsShowDescription = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsShowDescription
            IsTotalQuantity = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsTotalQuantity
            IsTaxDetails = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsTaxDetails
            IsHSNCode = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsHSNCode
            IsProductCode = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsProductCode

            IsReceivedAmount = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsReceivedAmount
            # print Bank details ====START
            IsBankDetails = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsBankDetails
            BankNameFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).BankNameFooter
            AccountNumberFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).AccountNumberFooter
            BranchIFCFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).BranchIFCFooter
            # print Bank details ====END

            SalesInvoiceFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).SalesInvoiceFooter
            SalesReturnFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).SalesReturnFooter
            SalesOrderFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).SalesOrderFooter
            PurchaseInvoiceFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).PurchaseInvoiceFooter
            PurchaseOrderFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).PurchaseOrderFooter
            PurchaseReturnFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).PurchaseReturnFooter
            CashRecieptFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).CashRecieptFooter
            BankRecieptFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).BankRecieptFooter
            CashPaymentFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).CashPaymentFooter
            BankPaymentFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).BankPaymentFooter
            TermsAndConditionsSales = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).TermsAndConditionsSales
            TermsAndConditionsPurchase = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).TermsAndConditionsPurchase
            TermsAndConditionsSaleEstimate = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).TermsAndConditionsSaleEstimate

            HeadFontSize = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).HeadFontSize
            BodyFontSize = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).BodyFontSize
            ContentFontSize = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).ContentFontSize
            FooterFontSize = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).FooterFontSize

        today = newDatetime.strptime(today, '%Y-%m-%d')
        remaining_days = company_expire_date - today.date()
        if administrations_models.GeneralSettings.objects.filter(
                CompanyID=CompanyID, SettingsType="Bill_Discount").exists():
            Bill_Discount = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="Bill_Discount").SettingsValue
            if Bill_Discount == "true":
                Bill_Discount = True
            else:
                Bill_Discount = False

        dic = {
            # "Free_Quantity_In_Sales": Free_Quantity_In_Sales,
            "loyalty_PointValue": loyalty_PointValue,
            "EnableLoyaltySettings": EnableLoyaltySettings,
            "CustomerBasedPrint": CustomerBasedPrint,
            "Loyalty_Point_Expire": Loyalty_Point_Expire,
            "is_Loyalty_SalesReturn_MinimumSalePrice": is_Loyalty_SalesReturn_MinimumSalePrice,
            # "Free_Quantity_In_Purchase": Free_Quantity_In_Purchase,
            "Bill_Discount": Bill_Discount,
            "MultiUnit": MultiUnit,
            "AllowNegativeStockSales": AllowNegativeStockSales,
            "PriceCategory": PriceCategory,
            "BlockSalesPrice": BlockSalesPrice,
            "VoucherNoAutoGenerate": VoucherNoAutoGenerate,
            "EnableVoucherNoUserWise": EnableVoucherNoUserWise,
            "ShowSalesPriceInPurchase": ShowSalesPriceInPurchase,
            "ShowSettingsinSales": ShowSettingsinSales,
            "ShowSettingsinPurchase": ShowSettingsinPurchase,
            "EnableProductBatchWise": EnableProductBatchWise,
            "AllowUpdateBatchPriceInSales": AllowUpdateBatchPriceInSales,
            "SalesPriceUpdate": SalesPriceUpdate,
            "PurchasePriceUpdate": PurchasePriceUpdate,
            "EnableTransilationInProduct": EnableTransilationInProduct,
            "ShowPositiveStockInSales": ShowPositiveStockInSales,
            "ShowNegativeBatchInSales": ShowNegativeBatchInSales,
            "CreateBatchForWorkOrder": CreateBatchForWorkOrder,
            "ShowYearMonthCalanderInWorkOrder": ShowYearMonthCalanderInWorkOrder,
            "KFC": KFC,
            "BatchCriteria": BatchCriteria,
            "blockSaleByBillDisct": blockSaleByBillDisct,
            "AllowCashReceiptMoreSaleAmt": AllowCashReceiptMoreSaleAmt,
            "AllowCashReceiptMorePurchaseAmt": AllowCashReceiptMorePurchaseAmt,
            "AllowAdvanceReceiptinSales": AllowAdvanceReceiptinSales,
            "AllowAdvanceReceiptinPurchase": AllowAdvanceReceiptinPurchase,
            "AllowQtyDividerinSales": AllowQtyDividerinSales,
            "InclusiveRatePurchase": InclusiveRatePurchase,
            "InclusiveRateSales": InclusiveRateSales,
            "InclusiveRateWorkOrder": InclusiveRateWorkOrder,
            "ShowDiscountInSales": ShowDiscountInSales,
            "ShowSupplierInSales": ShowSupplierInSales,
            "EnableShippingCharge": EnableShippingCharge,
            "ShowDueBalanceInSales": ShowDueBalanceInSales,
            "ShowDueBalanceInPurchase": ShowDueBalanceInPurchase,
            "ShowEmployeesInSales": ShowEmployeesInSales,
            "EnableSerialNoInSales": EnableSerialNoInSales,
            "EnableItemCodeNoInSales": EnableItemCodeNoInSales,
            "EnableSalesManInSales": EnableSalesManInSales,
            "ShowWarrantyPeriodInProduct": ShowWarrantyPeriodInProduct,
            "ShowDescriptionInSales": ShowDescriptionInSales,
            "AllowExtraSerielNos": AllowExtraSerielNos,
            "Free_Quantity_In_Sales": Free_Quantity_In_Sales,
            "Free_Quantity_In_Purchase": Free_Quantity_In_Purchase,
            "ShowCustomerInPurchase": ShowCustomerInPurchase,
            "ShowManDateAndExpDatePurchase": ShowManDateAndExpDatePurchase,
            "ShowDiscountInPurchase": ShowDiscountInPurchase,
            "ShowDiscountInPayments": ShowDiscountInPayments,
            "ShowDiscountInReceipts": ShowDiscountInReceipts,
            "EnableCardNetWork": EnableCardNetWork,
            "BlockTransactionsByDate": BlockTransactionsByDate,
            "EnableCardDetails": EnableCardDetails,
            "PreDateTransaction": PreDateTransaction,
            "PostDateTransaction": PostDateTransaction,
            "VAT": VAT,
            "GST": GST,
            "TAX1": TAX1,
            "TAX2": TAX2,
            "TAX3": TAX3,
            "QtyDecimalPoint": QtyDecimalPoint,
            "PriceDecimalPoint": PriceDecimalPoint,
            "Additional_Discount": Additional_Discount,
            "Bill_Discount": Bill_Discount,
            "Negatine_Stock": Negatine_Stock,
            "Increment_Qty_In_POS": Increment_Qty_In_POS,
            "Kitchen_Print": Kitchen_Print,
            "Order_Print": Order_Print,
            "Print_After_Save_Active": Print_After_Save_Active,
            "QtyDecimalPoint": QtyDecimalPoint,
            "PriceDecimalPoint": PriceDecimalPoint,
            "RoundingFigure": RoundingFigure,
            "RoundOffPurchase": RoundOffPurchase,
            "RoundOffSales": RoundOffSales,
            "Business_Type": BussinesType,
            "today": today,
            "ExpiryDate": ExpiryDate,
            "VAT_Type_name": VAT_Type_name,
            "Sales_VAT_Type_name": Sales_VAT_Type_name,
            "Purchase_VAT_Type_name": Purchase_VAT_Type_name,
            "Sales_GST_Type_name": Sales_GST_Type_name,
            "Purchase_GST_Type_name": Purchase_GST_Type_name,
            "Sales_GST_Type": Sales_GST_Type,
            "Purchase_GST_Type": Purchase_GST_Type,
            "Sales_VAT_Type": Sales_VAT_Type,
            "Purchase_VAT_Type": Purchase_VAT_Type,
            "Show_Sales_Type": Show_Sales_Type,
            "Show_Purchase_Type": Show_Purchase_Type,
        }
        CurrentVersion = 0
        MinimumVersion = 0
        if SoftwareVersion.objects.exists():
            CurrentVersion = SoftwareVersion.objects.get().CurrentVersion
            MinimumVersion = SoftwareVersion.objects.get().MinimumVersion

        software_version_dic = {
            "CurrentVersion": CurrentVersion,
            "MinimumVersion": MinimumVersion,
        }
        success = 6000
        message = "success!"

        # if administrations_models.UserTable.objects.filter(CompanyID=CompanyID)

        return Response(
            {
                'success': success,
                'StatusCode': success,
                'message': message,
                'error': None,
                "DefaultAccountForUser": DefaultAccountForUser,
                "Cash_Account": Cash_Account,
                "Bank_Account": Bank_Account,
                "Warehouse": WarehouseID,
                "Sales_Account": Sales_Account,
                "Sales_Return_Account": Sales_Return_Account,
                "Purchase_Account": Purchase_Account,
                "Purchase_Return_Account": Purchase_Return_Account,
                "Sales_GST_Type": Sales_GST_Type,
                "Purchase_GST_Type": Purchase_GST_Type,
                # "VAT_Type" : VAT_Type,
                "settingsData": dic,
                "Sales_Account_name": Sales_Account_name,
                "Sales_Return_Account_name": Sales_Return_Account_name,
                "Purchase_Account_name": Purchase_Account_name,
                "Purchase_Return_Account_name": Purchase_Return_Account_name,
                "Cash_Account_name": Cash_Account_name,
                "Bank_Account_name": Bank_Account_name,
                # "VAT_Type_name" : VAT_Type_name,
                "Sales_GST_Type_name": Sales_GST_Type_name,
                "Purchase_GST_Type_name": Purchase_GST_Type_name,
                "Warehouse_name": Warehouse_name,
                "Country": Country,
                "CountryName": CountryName,
                "CurrencySymbol": CurrencySymbol,
                "CompanyLogo": CompanyLogo,
                "State": State,
                "StateName": StateName,
                "State_Code": State_Code,
                "Address1": Address1,
                "Address2": Address2,
                "Address3": Address3,
                "City": City,
                "CompanyName": CompanyName,
                "CRNumber": CRNumber,
                "CINNumber": CINNumber,
                "Description": Description,
                "financial_FromDate": financial_FromDate,
                "financial_ToDate": financial_ToDate,
                "SoftwareVersion": software_version_dic,
                "IsTrialVersion": IsTrialVersion,
                "Edition": Edition,
                "remaining_days": remaining_days.days,
                "is_owner": is_owner,
                "user_type": user_type,
                "VATNumber": VATNumber,
                "GSTNumber": GSTNumber,
                "Phone": Phone,
            },
            status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Not Found"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def customer_create(request):
    try:
        with transaction.atomic():
            today = datetime.datetime.now()
            data = request.data

            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            BranchID = data['BranchID']
            CreatedUserID = data['CreatedUserID']
            
            PartyImage = data['PartyImage']
            CustomerName = data['CustomerName']
            DisplayName = data['DisplayName']
            OpeningBalance = data['OpeningBalance']
            CrOrDr = data['CrOrDr']
            if data['as_on_date'] and converted_float(OpeningBalance) > 0:
                as_on_date = data['as_on_date']
            else:
                as_on_date = today
            Email = data['Email']
            WorkPhone = data['WorkPhone']
            WebURL = data['WebURL']
            Address = data['Address']
            CreditPeriod = data['CreditPeriod']
            PriceCategoryID = data['PriceCategoryID']
            PanNumber = data['PanNumber']
            CreditLimit = data['CreditLimit']
            RouteID = data['RouteID']
            CRNo = data['CRNo']
            BankName1 = data['BankName']
            AccountName1 = data['AccountName']
            AccountNo1 = data['AccountNo']
            IBANOrIFSCCode1 = data['IBANOrIFSCCode1']
            PartyType = "customer"
            Action = "A"
            IsActive = True
            
            try:
                PartyCode = data["PartyCode"]
            except:
                PartyCode = get_PartyCode(
                    Parties, BranchID, CompanyID, PartyType)
            is_nameExist = False
            if Parties.objects.filter(CompanyID=CompanyID,BranchID=BranchID,PartyName__iexact=CustomerName, PartyType=PartyType).exists():
                is_nameExist = True
            if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerName__iexact=CustomerName).exists():
                is_nameExist = True
            LedgerID = get_auto_idLedger(
                AccountLedger, BranchID, CompanyID)
            if not is_nameExist:
                Balance = 0
                if converted_float(OpeningBalance) > 0:
                    if CrOrDr == "Cr":
                        Balance = converted_float(OpeningBalance) * -1
                    elif CrOrDr == "Dr":
                        Balance = OpeningBalance
                AccountLedger.objects.create(
                    LedgerID=LedgerID,
                    BranchID=BranchID,
                    LedgerName=CustomerName,
                    LedgerCode=PartyCode,
                    AccountGroupUnder=10,
                    OpeningBalance=OpeningBalance,
                    CrOrDr=CrOrDr,
                    IsActive=True,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action="A",
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                    as_on_date=as_on_date,
                    Balance=Balance,
                )

                AccountLedger_Log.objects.create(
                    BranchID=BranchID,
                    TransactionID=LedgerID,
                    LedgerName=CustomerName,
                    LedgerCode=PartyCode,
                    AccountGroupUnder=10,
                    OpeningBalance=OpeningBalance,
                    CrOrDr=CrOrDr,
                    IsActive=True,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action="A",
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                    as_on_date=as_on_date,
                    Balance=Balance,
                )
                if converted_float(OpeningBalance) > 0:
                    Credit = 0
                    Debit = 0
                    if CrOrDr == "Cr":
                        Credit = OpeningBalance
                    elif CrOrDr == "Dr":
                        Debit = OpeningBalance
                    VoucherType = "LOB"

                    if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerName="Suspense Account").exists():
                        RelativeLedgerID = AccountLedger.objects.get(
                            CompanyID=CompanyID, LedgerName="Suspense Account").LedgerID
                    else:
                        RelativeLedgerID = generated_ledgerID(
                            AccountLedger, BranchID, CompanyID)
                        SuspenseLedgerCode = get_LedgerCode(
                            AccountLedger, BranchID, CompanyID)

                        AccountLedger.objects.create(
                            LedgerID=RelativeLedgerID,
                            BranchID=BranchID,
                            LedgerName="Suspense Account",
                            LedgerCode=SuspenseLedgerCode,
                            AccountGroupUnder=26,
                            OpeningBalance=0,
                            CrOrDr="Dr",
                            Notes="",
                            IsActive=True,
                            IsDefault=True,
                            CreatedDate=today,
                            UpdatedDate=today,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )

                        AccountLedger_Log.objects.create(
                            BranchID=BranchID,
                            TransactionID=RelativeLedgerID,
                            LedgerName="Suspense Account",
                            LedgerCode=SuspenseLedgerCode,
                            AccountGroupUnder=26,
                            OpeningBalance=0,
                            CrOrDr="Dr",
                            Notes="",
                            IsActive=True,
                            IsDefault=True,
                            CreatedDate=today,
                            UpdatedDate=today,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=as_on_date,
                        VoucherMasterID=LedgerID,
                        VoucherType=VoucherType,
                        VoucherNo=PartyCode,
                        LedgerID=LedgerID,
                        RelatedLedgerID=RelativeLedgerID,
                        Debit=Debit,
                        Credit=Credit,
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
                        Date=as_on_date,
                        VoucherMasterID=LedgerID,
                        VoucherNo=PartyCode,
                        VoucherType=VoucherType,
                        LedgerID=LedgerID,
                        RelatedLedgerID=RelativeLedgerID,
                        Debit=Debit,
                        Credit=Credit,
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
                        Date=today,
                        VoucherMasterID=LedgerID,
                        VoucherType=VoucherType,
                        VoucherNo=PartyCode,
                        LedgerID=RelativeLedgerID,
                        RelatedLedgerID=LedgerID,
                        Debit=Credit,
                        Credit=Debit,
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
                        Date=today,
                        VoucherMasterID=LedgerID,
                        VoucherNo=PartyCode,
                        VoucherType=VoucherType,
                        LedgerID=RelativeLedgerID,
                        RelatedLedgerID=LedgerID,
                        Debit=Credit,
                        Credit=Debit,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )
                
                PartyID = party_id(Parties, BranchID, CompanyID)
                party_instance = Parties.objects.create(
                    PartyID=PartyID,
                    BranchID=BranchID,
                    PartyType=PartyType,
                    LedgerID=LedgerID,
                    PartyCode=PartyCode,
                    PartyName=CustomerName,
                    DisplayName=DisplayName,
                    FirstName=CustomerName,
                    Address1=Address,
                    WorkPhone=WorkPhone,
                    Email=Email,
                    CurrencyID=0,
                    Action="A",
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    PartyImage=PartyImage,
                    CompanyID=CompanyID,
                    WebURL=WebURL,
                    CreditPeriod=CreditPeriod,
                    PriceCategoryID=PriceCategoryID,
                    PanNumber=PanNumber,
                    CreditLimit=CreditLimit,
                    RouteID=RouteID,
                    CRNo=CRNo,
                    BankName1=BankName1,
                    AccountName1=AccountName1,
                    AccountNo1=AccountNo1,
                    IBANOrIFSCCode1=IBANOrIFSCCode1,
                    OpeningBalance=OpeningBalance
                )

                Parties_Log.objects.create(
                    TransactionID=PartyID,
                    BranchID=BranchID,
                    PartyType=PartyType,
                    LedgerID=LedgerID,
                    PartyCode=PartyCode,
                    PartyName=CustomerName,
                    DisplayName=DisplayName,
                    FirstName=CustomerName,
                    Address1=Address,
                    WorkPhone=WorkPhone,
                    Email=Email,
                    CurrencyID=0,
                    Action="A",
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    PartyImage=PartyImage,
                    CompanyID=CompanyID,
                    WebURL=WebURL,
                    CreditPeriod=CreditPeriod,
                    PriceCategoryID=PriceCategoryID,
                    PanNumber=PanNumber,
                    CreditLimit=CreditLimit,
                    RouteID=RouteID,
                    CRNo=CRNo,
                    BankName1=BankName1,
                    AccountName1=AccountName1,
                    AccountNo1=AccountNo1,
                    IBANOrIFSCCode1=IBANOrIFSCCode1,
                    OpeningBalance=OpeningBalance
                )

                response_data = {
                    "StatusCode": 6000,
                    "message": "Customer created successfully",
                }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "Customer Name Already Exist",
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

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Cusomer Rassasy',
                     'Create', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)
    
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def customer_list(request):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)

    if Parties.objects.filter(CompanyID=CompanyID,PartyType="customer").exists():
        instance = Parties.objects.filter(CompanyID=CompanyID,PartyType="customer")
        serialized = POS_partySerializer(
            instance, many=True, context={"CompanyID": CompanyID})

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Customers Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def single_customer(request, pk):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)

    if Parties.objects.filter(pk=pk).exists():
        instance = Parties.objects.get(pk=pk)
        serialized = POS_partySerializer(
            instance, context={"CompanyID": CompanyID})

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Customer Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def edit_customer(request,pk):
    try:
        with transaction.atomic():
            today = datetime.datetime.now()
            data = request.data

            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            BranchID = data['BranchID']
            CreatedUserID = data['CreatedUserID']

            PartyImage = data['PartyImage']
            CustomerName = data['CustomerName']
            DisplayName = data['DisplayName']
            OpeningBalance = data['OpeningBalance']
            CrOrDr = data['CrOrDr']
            if data['as_on_date'] and converted_float(OpeningBalance) > 0:
                as_on_date = data['as_on_date']
            else:
                as_on_date = today
            Email = data['Email']
            WorkPhone = data['WorkPhone']
            WebURL = data['WebURL']
            Address = data['Address']
            CreditPeriod = data['CreditPeriod']
            PriceCategoryID = data['PriceCategoryID']
            PanNumber = data['PanNumber']
            CreditLimit = data['CreditLimit']
            RouteID = data['RouteID']
            CRNo = data['CRNo']
            BankName1 = data['BankName']
            AccountName1 = data['AccountName']
            AccountNo1 = data['AccountNo']
            IBANOrIFSCCode1 = data['IBANOrIFSCCode1']
            PartyType = "customer"
            Action = "M"
            IsActive = True
            
            instance = Parties.objects.get(pk=pk)
            PartyCode = instance.PartyCode

            is_nameExist = False
            if Parties.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PartyName__iexact=CustomerName, PartyType=PartyType).exclude(id=pk).exists():
                is_nameExist = True
            if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerName__iexact=CustomerName).exclude(CompanyID=CompanyID,LedgerID=instance.LedgerID).exists():
                is_nameExist = True
                
            LedgerID = instance.LedgerID
            if LedgerPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=LedgerID, BranchID=BranchID, VoucherType="LOB").exists():
                ledgerPostInstances = LedgerPosting.objects.filter(
                    CompanyID=CompanyID, VoucherMasterID=LedgerID, BranchID=BranchID, VoucherType="LOB").delete()
            if not is_nameExist:
                Balance = 0
                if converted_float(OpeningBalance) > 0:
                    if CrOrDr == "Cr":
                        Balance = converted_float(OpeningBalance) * -1
                    elif CrOrDr == "Dr":
                        Balance = OpeningBalance
                account_ledger = AccountLedger.objects.get(
                    CompanyID=CompanyID, LedgerID=LedgerID)
                account_ledger.LedgerName = CustomerName
                account_ledger.save()
                AccountLedger_Log.objects.create(
                    BranchID=BranchID,
                    TransactionID=LedgerID,
                    LedgerName=CustomerName,
                    LedgerCode=PartyCode,
                    AccountGroupUnder=10,
                    OpeningBalance=OpeningBalance,
                    CrOrDr=CrOrDr,
                    IsActive=True,
                    UpdatedDate=today,
                    Action="M",
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                    as_on_date=as_on_date,
                    Balance=Balance,
                )
                if converted_float(OpeningBalance) > 0:
                    Credit = 0
                    Debit = 0
                    if CrOrDr == "Cr":
                        Credit = OpeningBalance
                    elif CrOrDr == "Dr":
                        Debit = OpeningBalance
                    VoucherType = "LOB"

                    if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerName="Suspense Account").exists():
                        RelativeLedgerID = AccountLedger.objects.get(
                            CompanyID=CompanyID, LedgerName="Suspense Account").LedgerID
                    else:
                        RelativeLedgerID = generated_ledgerID(
                            AccountLedger, BranchID, CompanyID)
                        SuspenseLedgerCode = get_LedgerCode(
                            AccountLedger, BranchID, CompanyID)

                        AccountLedger.objects.create(
                            LedgerID=RelativeLedgerID,
                            BranchID=BranchID,
                            LedgerName="Suspense Account",
                            LedgerCode=SuspenseLedgerCode,
                            AccountGroupUnder=26,
                            OpeningBalance=0,
                            CrOrDr="Dr",
                            Notes="Suspense Account",
                            IsActive=True,
                            IsDefault=True,
                            CreatedDate=today,
                            UpdatedDate=today,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )

                        AccountLedger_Log.objects.create(
                            BranchID=BranchID,
                            TransactionID=RelativeLedgerID,
                            LedgerName="Suspense Account",
                            LedgerCode=SuspenseLedgerCode,
                            AccountGroupUnder=26,
                            OpeningBalance=0,
                            CrOrDr="Dr",
                            Notes="Suspense Account",
                            IsActive=True,
                            IsDefault=True,
                            CreatedDate=today,
                            UpdatedDate=today,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=as_on_date,
                        VoucherMasterID=LedgerID,
                        VoucherType=VoucherType,
                        VoucherNo=PartyCode,
                        LedgerID=LedgerID,
                        RelatedLedgerID=RelativeLedgerID,
                        Debit=Debit,
                        Credit=Credit,
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
                        Date=as_on_date,
                        VoucherMasterID=LedgerID,
                        VoucherNo=PartyCode,
                        VoucherType=VoucherType,
                        LedgerID=LedgerID,
                        RelatedLedgerID=RelativeLedgerID,
                        Debit=Debit,
                        Credit=Credit,
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
                        Date=today,
                        VoucherMasterID=LedgerID,
                        VoucherType=VoucherType,
                        VoucherNo=PartyCode,
                        LedgerID=RelativeLedgerID,
                        RelatedLedgerID=LedgerID,
                        Debit=Credit,
                        Credit=Debit,
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
                        Date=today,
                        VoucherMasterID=LedgerID,
                        VoucherNo=PartyCode,
                        VoucherType=VoucherType,
                        LedgerID=RelativeLedgerID,
                        RelatedLedgerID=LedgerID,
                        Debit=Credit,
                        Credit=Debit,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )
                instance.PartyName = CustomerName
                instance.FirstName = CustomerName
                instance.DisplayName = DisplayName
                instance.Address = Address
                instance.WorkPhone = WorkPhone
                instance.Email = Email
                instance.WebURL = WebURL
                instance.CreditPeriod = CreditPeriod
                instance.PriceCategoryID = PriceCategoryID
                instance.PanNumber = PanNumber
                instance.CreditLimit = CreditLimit
                instance.RouteID = RouteID
                instance.CRNo = CRNo
                instance.BankName1 = BankName1
                instance.AccountName1 = AccountName1
                instance.AccountNo1 = AccountNo1
                instance.IBANOrIFSCCode1 = IBANOrIFSCCode1
                instance.OpeningBalance = OpeningBalance
                PartyID = instance.PartyID
                instance.save()

                Parties_Log.objects.create(
                    TransactionID=PartyID,
                    BranchID=BranchID,
                    PartyType=PartyType,
                    LedgerID=LedgerID,
                    PartyCode=PartyCode,
                    PartyName=CustomerName,
                    DisplayName=DisplayName,
                    FirstName=CustomerName,
                    Address1=Address,
                    WorkPhone=WorkPhone,
                    Email=Email,
                    CurrencyID=0,
                    Action="M",
                    CreatedUserID=CreatedUserID,
                    UpdatedDate=today,
                    PartyImage=PartyImage,
                    CompanyID=CompanyID,
                    WebURL=WebURL,
                    CreditPeriod=CreditPeriod,
                    PriceCategoryID=PriceCategoryID,
                    PanNumber=PanNumber,
                    CreditLimit=CreditLimit,
                    RouteID=RouteID,
                    CRNo=CRNo,
                    BankName1=BankName1,
                    AccountName1=AccountName1,
                    AccountNo1=AccountNo1,
                    IBANOrIFSCCode1=IBANOrIFSCCode1,
                    OpeningBalance=OpeningBalance
                )

                response_data = {
                    "StatusCode": 6000,
                    "message": "Customer updated successfully",
                }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "Customer Name Already Exist",
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

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Cusomer Rassasy',
                     'Create', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_customer(request, pk):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    if Parties.objects.filter(pk=pk).exists():
        instance = Parties.objects.get(pk=pk)
        if not LedgerPosting.objects.filter(CompanyID=CompanyID, LedgerID=instance.LedgerID).exclude(VoucherType="LOB").exists():
            Action = "D"
            BranchID = instance.BranchID
            PartyID = instance.PartyID
            PartyType = instance.PartyType
            LedgerID = instance.LedgerID
            PartyCode = instance.PartyCode
            PartyName = instance.PartyName
            DisplayName = instance.DisplayName
            FirstName = instance.FirstName
            LastName = instance.LastName
            Attention = instance.Attention
            Address1 = instance.Address1
            Address2 = instance.Address2
            City = instance.City
            State = instance.State
            Country = instance.Country
            PostalCode = instance.PostalCode
            OfficePhone = instance.OfficePhone
            WorkPhone = instance.WorkPhone
            Mobile = instance.Mobile
            WebURL = instance.WebURL
            Email = instance.Email
            IsBillwiseApplicable = instance.IsBillwiseApplicable
            CreditPeriod = instance.CreditPeriod
            CreditLimit = instance.CreditLimit
            PriceCategoryID = instance.PriceCategoryID
            CurrencyID = instance.CurrencyID
            InterestOrNot = instance.InterestOrNot
            RouteID = instance.RouteID
            VATNumber = instance.VATNumber
            GSTNumber = instance.GSTNumber
            Tax1Number = instance.Tax1Number
            Tax2Number = instance.Tax2Number
            Tax3Number = instance.Tax3Number
            PanNumber = instance.PanNumber
            CRNo = instance.CRNo
            BankName1 = instance.BankName1
            AccountName1 = instance.AccountName1
            AccountNo1 = instance.AccountNo1
            IBANOrIFSCCode1 = instance.IBANOrIFSCCode1
            BankName2 = instance.BankName2
            AccountName2 = instance.AccountName2
            AccountNo2 = instance.AccountNo2
            IBANOrIFSCCode2 = instance.IBANOrIFSCCode2
            IsActive = instance.IsActive
            OpeningBalance = instance.OpeningBalance
            PartyImage = instance.PartyImage
            Attention_Shipping = instance.Attention_Shipping
            Address1_Shipping = instance.Address1_Shipping
            Address2_Shipping = instance.Address2_Shipping
            State_Shipping = instance.State_Shipping
            Country_Shipping = instance.Country_Shipping
            City_Shipping = instance.City_Shipping
            PostalCode_Shipping = instance.PostalCode_Shipping
            Phone_Shipping = instance.Phone_Shipping
            GST_Treatment = instance.GST_Treatment
            VAT_Treatment = instance.VAT_Treatment
            State_Code = instance.State_Code
            PlaceOfSupply = instance.PlaceOfSupply
            District = instance.District
            AdditionalNo = instance.AdditionalNo
            District_shipping = instance.District_shipping
            AdditionalNo_shipping = instance.AdditionalNo_shipping

            Parties_Log.objects.create(
                TransactionID=PartyID,
                BranchID=BranchID,
                PartyType=PartyType,
                LedgerID=LedgerID,
                PartyCode=PartyCode,
                PartyName=PartyName,
                DisplayName=DisplayName,
                FirstName=FirstName,
                LastName=LastName,
                Attention=Attention,
                Address1=Address1,
                Address2=Address2,
                City=City,
                State=State,
                Country=Country,
                PostalCode=PostalCode,
                OfficePhone=OfficePhone,
                WorkPhone=WorkPhone,
                Mobile=Mobile,
                WebURL=WebURL,
                Email=Email,
                IsBillwiseApplicable=IsBillwiseApplicable,
                CreditPeriod=CreditPeriod,
                CreditLimit=CreditLimit,
                PriceCategoryID=PriceCategoryID,
                CurrencyID=CurrencyID,
                InterestOrNot=InterestOrNot,
                RouteID=RouteID,
                VATNumber=VATNumber,
                GSTNumber=GSTNumber,
                Tax1Number=Tax1Number,
                Tax2Number=Tax2Number,
                Tax3Number=Tax3Number,
                PanNumber=PanNumber,
                CRNo=CRNo,
                BankName1=BankName1,
                AccountName1=AccountName1,
                AccountNo1=AccountNo1,
                IBANOrIFSCCode1=IBANOrIFSCCode1,
                BankName2=BankName2,
                AccountName2=AccountName2,
                AccountNo2=AccountNo2,
                IBANOrIFSCCode2=IBANOrIFSCCode2,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                OpeningBalance=OpeningBalance,
                PartyImage=PartyImage,
                CompanyID=CompanyID,
                Attention_Shipping=Attention_Shipping,
                Address1_Shipping=Address1_Shipping,
                Address2_Shipping=Address2_Shipping,
                State_Shipping=State_Shipping,
                Country_Shipping=Country_Shipping,
                City_Shipping=City_Shipping,
                PostalCode_Shipping=PostalCode_Shipping,
                Phone_Shipping=Phone_Shipping,
                GST_Treatment=GST_Treatment,
                VAT_Treatment=VAT_Treatment,
                State_Code=State_Code,
                PlaceOfSupply=PlaceOfSupply,
                District=District,
                AdditionalNo=AdditionalNo,
                District_shipping=District_shipping,
                AdditionalNo_shipping=AdditionalNo_shipping,
            )
            
            if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID).exists():
                accountLedgerInstance = AccountLedger.objects.get(
                    CompanyID=CompanyID, LedgerID=LedgerID)

                LedgerName = accountLedgerInstance.LedgerName
                LedgerCode = accountLedgerInstance.LedgerCode
                AccountGroupUnder = accountLedgerInstance.AccountGroupUnder
                OpeningBalance = accountLedgerInstance.OpeningBalance
                CrOrDr = accountLedgerInstance.CrOrDr
                Notes = accountLedgerInstance.Notes
                IsActive = accountLedgerInstance.IsActive
                IsDefault = accountLedgerInstance.IsDefault
                CreatedUserID = accountLedgerInstance.CreatedUserID

                accountLedgerInstance.delete()

                AccountLedger_Log.objects.create(
                    BranchID=BranchID,
                    TransactionID=LedgerID,
                    LedgerName=LedgerName,
                    LedgerCode=LedgerCode,
                    AccountGroupUnder=AccountGroupUnder,
                    OpeningBalance=OpeningBalance,
                    CrOrDr=CrOrDr,
                    Notes=Notes,
                    IsActive=IsActive,
                    IsDefault=IsDefault,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=Action,
                    CompanyID=CompanyID,
                )

            if LedgerPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=LedgerID, VoucherType="LOB", BranchID=BranchID).exists():
                ledgerPostInstances = LedgerPosting.objects.filter(
                    CompanyID=CompanyID, VoucherMasterID=LedgerID, VoucherType="LOB", BranchID=BranchID)
                for ledgerPostInstance in ledgerPostInstances:
                    LedgerPostingID = ledgerPostInstance.LedgerPostingID
                    VoucherType = ledgerPostInstance.VoucherType
                    LedgerID = ledgerPostInstance.LedgerID
                    RelatedLedgerID = ledgerPostInstance.RelatedLedgerID
                    Debit = ledgerPostInstance.Debit
                    Credit = ledgerPostInstance.Credit
                    IsActive = ledgerPostInstance.IsActive
                    CreatedUserID = ledgerPostInstance.CreatedUserID

                    ledgerPostInstance.delete()

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=today,
                        VoucherMasterID=LedgerID,
                        VoucherType=VoucherType,
                        LedgerID=LedgerID,
                        RelatedLedgerID=RelatedLedgerID,
                        Debit=Debit,
                        Credit=Credit,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

            instance.delete()
            response_data = {
                "StatusCode": 6000,
                "message": "Party Deleted Successfully!",
                "title": "Success",
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Can't delete this party!"
            }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Customer Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def printer_create(request):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    CreatedUserID = data['CreatedUserID']
    PrinterName = data['PrinterName']
    IPAddress = data['IPAddress']
    Type = data['Type']
    
    PrinterID = get_auto_PrinterID(CompanyID, BranchID)

    pos = POS_Printer.objects.create(
        CompanyID=CompanyID,
        BranchID=BranchID,
        PrinterID=PrinterID,
        PrinterName=PrinterName,
        IPAddress=IPAddress,
        CreatedUserID=CreatedUserID,
        CreatedDate=today,
        UpdatedDate=today,
        Type=Type
    )

    response_data = {
        "StatusCode": 6000,
        "message": "POS Printer created Successfully!!!",
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def printer_list(request):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']

    if POS_Printer.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        instances = POS_Printer.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID)
        serialized = PrintSerializer(
            instances,many=True, context={"CompanyID": CompanyID})

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "not found"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_printer(request,pk):
    today = datetime.datetime.now()

    if POS_Printer.objects.filter(pk=pk).exists():
        instances = POS_Printer.objects.filter(pk=pk).delete()
        
        response_data = {
            "StatusCode": 6000,
            "message" : "deleted successfully"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "not found"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def variant_create(request):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    CreatedUserID = data['CreatedUserID']
    VariantName = data['VariantName']
    Amount = data['Amount']
    
    VariantID = get_auto_VariantID(CompanyID, BranchID)

    pos = ProductVariants.objects.create(
        CompanyID=CompanyID,
        BranchID=BranchID,
        VariantID=VariantID,
        VariantName=VariantName,
        Amount=Amount,
        CreatedUserID=CreatedUserID,
        CreatedDate=today,
        UpdatedDate=today,
    )

    response_data = {
        "StatusCode": 6000,
        "message": "POS Product Variant created Successfully!!!",
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def variant_list(request):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']

    if ProductVariants.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        instances = ProductVariants.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID)
        
        serialized = ProductVariantSerializer(
            instances, many=True, context={"CompanyID": CompanyID})

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data,
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Variants Not Found",
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def product_create(request):
    try:
        with transaction.atomic():
            today = datetime.datetime.now()
            data = request.data

            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            BranchID = data['BranchID']
            CreatedUserID = data['CreatedUserID']

            productImage1 = data['productImage1']
            productImage2 = data['productImage2']
            productImage3 = data['productImage3']
            VegOrNonVeg = data['VegOrNonVeg']
            ProductName = data['ProductName']
            ProductGroupID = data['ProductGroupID']
            Description = data['Description']
            SalesPrice = data['SalesPrice']
            PurchasePrice = data['PurchasePrice']
            TaxID = data['TaxID']
            Variant = data['Variant']

            variant_ins = None
            if ProductVariants.objects.filter(id=Variant).exists():
                variant_ins = ProductVariants.objects.get(id=Variant)
            is_nameExist = False
            if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductName__iexact=ProductName).exists():
                is_nameExist = True
                
            ProductID = get_auto_ProductID(Product, BranchID, CompanyID)
            ProductCode = get_ProductCode(
                Product, BranchID, CompanyID)
            GST = 1
            VatID = 1
            if get_GeneralSettings(CompanyID, BranchID, "GST"):
                GST = TaxID
            if get_GeneralSettings(CompanyID, BranchID, "VAT"):
                VatID = TaxID
            if not is_nameExist:
                instance = Product.objects.create(
                    ProductID=ProductID,
                    BranchID=BranchID,
                    ProductCode=ProductCode,
                    ProductName=ProductName,
                    DisplayName=ProductName,
                    Description=Description,
                    ProductGroupID=ProductGroupID,
                    BrandID=1,
                    InventoryType="StockItem",
                    VatID=VatID,
                    ProductImage=productImage1,
                    ProductImage2=productImage2,
                    ProductImage3=productImage3,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    GST=GST,
                    Tax1=1,
                    Tax2=1,
                    Tax3=1,
                    CompanyID=CompanyID,
                    Variant=variant_ins,
                    VegOrNonVeg=VegOrNonVeg
                )

                Product_Log.objects.create(
                    TransactionID=ProductID,
                    BranchID=BranchID,
                    ProductCode=ProductCode,
                    ProductName=ProductName,
                    DisplayName=ProductName,
                    Description=Description,
                    ProductGroupID=ProductGroupID,
                    BrandID=1,
                    InventoryType="StockItem",
                    VatID=VatID,
                    ProductImage=productImage1,
                    ProductImage2=productImage2,
                    ProductImage3=productImage3,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    GST=GST,
                    Tax1=1,
                    Tax2=1,
                    Tax3=1,
                    CompanyID=CompanyID,
                    Variant=variant_ins,
                    VegOrNonVeg=VegOrNonVeg
                )
                
                PriceListID = get_auto_priceListid(
                    PriceList, BranchID, CompanyID
                )
                AutoBarcode = get_auto_AutoBarcode(
                    PriceList, BranchID, CompanyID
                )

                PriceList.objects.create(
                    PriceListID=PriceListID,
                    BranchID=BranchID,
                    ProductID=ProductID,
                    product=instance,
                    UnitID=1,
                    SalesPrice=SalesPrice,
                    PurchasePrice=PurchasePrice,
                    MultiFactor=1,
                    Barcode="",
                    AutoBarcode=AutoBarcode,
                    CreatedDate=today,
                    UpdatedDate=today,
                    MRP=SalesPrice,
                    DefaultUnit=1,
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                )

                PriceList_Log.objects.create(
                    TransactionID=PriceListID,
                    BranchID=BranchID,
                    ProductID=ProductID,
                    UnitID=1,
                    SalesPrice=SalesPrice,
                    PurchasePrice=PurchasePrice,
                    MultiFactor=1,
                    Barcode="",
                    AutoBarcode=AutoBarcode,
                    CreatedDate=today,
                    UpdatedDate=today,
                    MRP=SalesPrice,
                    DefaultUnit=1,
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                )

                response_data = {
                    "StatusCode": 6000,
                    "message": "Product created successfully",
                }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Name Already Exist",
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
        CompanyID = get_company(request.data['CompanyID'])

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Product Rassasy',
                     'Create', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def single_product(request, pk):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)

    if Product.objects.filter(pk=pk).exists():
        instance = Product.objects.get(pk=pk)
        serialized = POS_Product_Serializer(instance, context={
            "request": request, "CompanyID": CompanyID, "PriceRounding": 2})

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Customer Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_product(request, pk):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]

    today = datetime.datetime.now()
    product_instance = None
    priceLists_instance = None
    purchaseDetails_exist = None
    purchaseOrderDetails_exist = None
    salesDetails_exist = None
    salesOrderDetails_exist = None
    stockPostings_exist = None


    if Product.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        product_instance = Product.objects.get(CompanyID=CompanyID, pk=pk)
        ProductID = product_instance.ProductID
        BranchID = product_instance.BranchID

        ProductCode = product_instance.ProductCode
        ProductName = product_instance.ProductName
        DisplayName = product_instance.DisplayName
        Description = product_instance.Description
        ProductGroupID = product_instance.ProductGroupID
        BrandID = product_instance.BrandID
        InventoryType = product_instance.InventoryType
        VatID = product_instance.VatID
        StockMinimum = product_instance.StockMinimum
        StockReOrder = product_instance.StockReOrder
        StockMaximum = product_instance.StockMaximum
        MarginPercent = product_instance.MarginPercent
        ProductImage = product_instance.ProductImage
        Active = product_instance.Active
        IsRawMaterial = product_instance.IsRawMaterial
        IsFinishedProduct = product_instance.IsFinishedProduct
        IsSales = product_instance.IsSales
        IsPurchase = product_instance.IsPurchase
        IsWeighingScale = product_instance.IsWeighingScale
        WeighingCalcType = product_instance.WeighingCalcType
        PLUNo = product_instance.PLUNo
        GST = product_instance.GST
        Tax1 = product_instance.Tax1
        Tax2 = product_instance.Tax2
        Tax3 = product_instance.Tax3
        IsFavourite = product_instance.IsFavourite
        IsKFC = product_instance.IsKFC
        HSNCode = product_instance.HSNCode
        WarrantyType = product_instance.WarrantyType
        Warranty = product_instance.Warranty
        is_Service = product_instance.is_Service
        is_inclusive = product_instance.is_inclusive

        Action = "D"

        purchaseDetails_exist = PurchaseDetails.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID
        ).exists()
        purchaseOrderDetails_exist = PurchaseOrderDetails.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID
        ).exists()
        salesDetails_exist = SalesDetails.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID
        ).exists()
        salesOrderDetails_exist = SalesOrderDetails.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID
        ).exists()
        stockPostings_exist = StockPosting.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID
        ).exists()

        if (
            not purchaseDetails_exist
            and not purchaseOrderDetails_exist
            and not salesDetails_exist
            and not salesOrderDetails_exist
            and not stockPostings_exist
        ):

            product_instance.delete()

            Product_Log.objects.create(
                TransactionID=ProductID,
                BranchID=BranchID,
                ProductCode=ProductCode,
                ProductName=ProductName,
                DisplayName=DisplayName,
                Description=Description,
                ProductGroupID=ProductGroupID,
                BrandID=BrandID,
                InventoryType=InventoryType,
                VatID=VatID,
                StockMinimum=StockMinimum,
                StockReOrder=StockReOrder,
                StockMaximum=StockMaximum,
                MarginPercent=MarginPercent,
                ProductImage=ProductImage,
                Active=Active,
                IsWeighingScale=IsWeighingScale,
                IsRawMaterial=IsRawMaterial,
                IsFinishedProduct=IsFinishedProduct,
                IsSales=IsSales,
                IsPurchase=IsPurchase,
                WeighingCalcType=WeighingCalcType,
                PLUNo=PLUNo,
                IsFavourite=IsFavourite,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                GST=GST,
                Tax1=Tax1,
                Tax2=Tax2,
                Tax3=Tax3,
                Action=Action,
                CompanyID=CompanyID,
                IsKFC=IsKFC,
                HSNCode=HSNCode,
                WarrantyType=WarrantyType,
                Warranty=Warranty,
                is_Service=is_Service,
                is_inclusive=is_inclusive,
            )

            priceLists_instances = PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
            )

            for priceLists_instance in priceLists_instances:

                PriceListID = priceLists_instance.PriceListID
                BranchID = priceLists_instance.BranchID
                ProductID = priceLists_instance.ProductID
                UnitName = priceLists_instance.UnitName
                SalesPrice = priceLists_instance.SalesPrice
                PurchasePrice = priceLists_instance.PurchasePrice
                MultiFactor = priceLists_instance.MultiFactor
                Barcode = priceLists_instance.Barcode
                AutoBarcode = priceLists_instance.AutoBarcode
                SalesPrice1 = priceLists_instance.SalesPrice1
                SalesPrice2 = priceLists_instance.SalesPrice2
                SalesPrice3 = priceLists_instance.SalesPrice3
                DefaultUnit = priceLists_instance.DefaultUnit
                UnitInSales = priceLists_instance.UnitInSales
                UnitInPurchase = priceLists_instance.UnitInPurchase
                UnitInReports = priceLists_instance.UnitInReports

                priceLists_instance.delete()

                PriceList_Log.objects.create(
                    TransactionID=PriceListID,
                    BranchID=BranchID,
                    ProductID=ProductID,
                    UnitName=UnitName,
                    SalesPrice=SalesPrice,
                    PurchasePrice=PurchasePrice,
                    MultiFactor=MultiFactor,
                    Barcode=Barcode,
                    AutoBarcode=AutoBarcode,
                    SalesPrice1=SalesPrice1,
                    SalesPrice2=SalesPrice2,
                    SalesPrice3=SalesPrice3,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=Action,
                    DefaultUnit=DefaultUnit,
                    UnitInSales=UnitInSales,
                    UnitInPurchase=UnitInPurchase,
                    UnitInReports=UnitInReports,
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                )

            if Batch.objects.filter(ProductID=ProductID).exists():
                batch_ins = Batch.objects.filter(ProductID=ProductID)
                for i in batch_ins:
                    i.delete()
            # request , company, log_type, user, source, action, message, description
            activity_log(
                request._request,
                CompanyID,
                "Information",
                CreatedUserID,
                "Product",
                "Deleted",
                "Product Deleted successfully.",
                "Product Deleted successfully.",
            )

            response_data = {
                "StatusCode": 6000,
                "title": "Success",
                "message": "Product Deleted Successfully!",
            }

        else:
            # request , company, log_type, user, source, action, message, description
            activity_log(
                request._request,
                CompanyID,
                "Warning",
                CreatedUserID,
                "Product",
                "Deleted",
                "Product Deleted Failed.",
                "You Cant Delete this Product,this ProductID is using somewhere",
            )
            response_data = {
                "StatusCode": 6001,
                "title": "Failed",
                "message": "You Cant Delete this Product,this ProductID is using somewhere!!",
            }
    else:
        response_data = {
            "StatusCode": 6001,
            "title": "Failed",
            "message": "Product Not Fount!",
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def edit_product(request,pk):
    try:
        with transaction.atomic():
            today = datetime.datetime.now()
            data = request.data

            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            BranchID = data['BranchID']
            CreatedUserID = data['CreatedUserID']

            productImage1 = data['productImage1']
            productImage2 = data['productImage2']
            productImage3 = data['productImage3']
            VegOrNonVeg = data['VegOrNonVeg']
            ProductName = data['ProductName']
            ProductGroupID = data['ProductGroupID']
            Description = data['Description']
            SalesPrice = data['SalesPrice']
            PurchasePrice = data['PurchasePrice']
            TaxID = data['TaxID']
            Variant = data['Variant']
            
            instance = Product.objects.get(pk=pk)

            variant_ins = None
            if ProductVariants.objects.filter(id=Variant).exists():
                variant_ins = ProductVariants.objects.get(id=Variant)
            is_nameExist = False
            if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductName__iexact=ProductName).exclude(pk=pk).exists():
                is_nameExist = True

            ProductID = instance.ProductID
            ProductCode = instance.ProductCode
            GST = 1
            VatID = 1
            if get_GeneralSettings(CompanyID, BranchID, "GST"):
                GST = TaxID
            if get_GeneralSettings(CompanyID, BranchID, "VAT"):
                VatID = TaxID
            if not is_nameExist:
                instance.ProductName = ProductName
                instance.DisplayName = ProductName
                instance.Description = Description
                instance.ProductGroupID = ProductGroupID
                instance.VatID = VatID
                instance.productImage1 = productImage1
                instance.productImage2 = productImage2
                instance.productImage3 = productImage3
                instance.Variant = variant_ins
                instance.GST = GST
                instance.VegOrNonVeg = VegOrNonVeg
                instance.save()
                Product_Log.objects.create(
                    TransactionID=ProductID,
                    BranchID=BranchID,
                    ProductCode=ProductCode,
                    ProductName=ProductName,
                    DisplayName=ProductName,
                    Description=Description,
                    ProductGroupID=ProductGroupID,
                    BrandID=1,
                    InventoryType="StockItem",
                    VatID=VatID,
                    ProductImage=productImage1,
                    ProductImage2=productImage2,
                    ProductImage3=productImage3,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    GST=GST,
                    Tax1=1,
                    Tax2=1,
                    Tax3=1,
                    CompanyID=CompanyID,
                    Variant=variant_ins,
                    VegOrNonVeg=VegOrNonVeg
                )
                pricelist = PriceList.objects.get(
                    ProductID=ProductID, CompanyID=CompanyID)
                PriceListID = pricelist.PriceListID
                AutoBarcode = pricelist.AutoBarcode

                pricelist.SalesPrice = SalesPrice
                pricelist.PurchasePrice = PurchasePrice
                pricelist.MRP = SalesPrice
                pricelist.save()
                PriceList_Log.objects.create(
                    TransactionID=PriceListID,
                    BranchID=BranchID,
                    ProductID=ProductID,
                    UnitID=1,
                    SalesPrice=SalesPrice,
                    PurchasePrice=PurchasePrice,
                    MultiFactor=1,
                    Barcode="",
                    AutoBarcode=AutoBarcode,
                    CreatedDate=today,
                    UpdatedDate=today,
                    MRP=SalesPrice,
                    DefaultUnit=1,
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                )

                response_data = {
                    "StatusCode": 6000,
                    "message": "Product updated successfully",
                }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Name Already Exist",
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

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Product Rassasy',
                     'Create', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_pos_user_role(request):
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
    User = data['User']
    Role = data['Role']
    PinNo = data['PinNo']

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
def rassassy_reports(request):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    BranchID = data['BranchID']
    ReportType = data['ReportType']
    filterVal = data['filterVal']
    FromDate = data['FromDate']
    ToDate = data['ToDate']
    details = []
    if ReportType == "SalesReport":
        df, details = query_sales_report_rassassy_data(
            data["CompanyID"], BranchID, FromDate, ToDate, filterVal, PriceRounding, ReportType)
    elif ReportType == "DiningReport":
        df, details = query_dining_report_rassassy_data(
            data["CompanyID"], BranchID, FromDate, ToDate, filterVal, PriceRounding, ReportType)
    elif ReportType == "TakeAwayReport" or ReportType == "OnlineReport" or ReportType == "CarReport":
        if ReportType == "TakeAwayReport":
            ReportType = "TakeAway"
        if ReportType == "OnlineReport":
            ReportType = "Online"
        if ReportType == "CarReport":
            ReportType = "Car"
        df, details = query_take_away_report_rassassy_data(
            data["CompanyID"], BranchID, FromDate, ToDate, filterVal, PriceRounding, ReportType)
    elif ReportType == "TableWiseReport":
        df, details = query_table_wise_report_rassassy_data(
            data["CompanyID"], BranchID, FromDate, ToDate, filterVal, PriceRounding, ReportType)
    elif ReportType == "ProductReport":
        df, details = query_product_report_rassassy_data(
            data["CompanyID"], BranchID, FromDate, ToDate, filterVal, PriceRounding, ReportType)

    response_data = {
        "StatusCode": 6000,
        "data": details,
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def rassassy_create_loyality_customer(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    BranchID = data['BranchID']
    MobileNo = data['Phone']
    FirstName = data['Name']
    Address1 = data['Location']
    CardTypeID = data['CardTypeID']
    CardTypeName = data['CardTypeName']
    CardNumber = data['CardNumber']
    CardStatusID = data['CardStatusID']
    CardStatusName = data['CardStatusName']
    
    Action = 'A'
    MobileNo_ok = False
    CardNumber_ok = False
    LoyaltyCustomerID = get_auto_loyaltyID(LoyaltyCustomer, BranchID, CompanyID)
    loyalty_instances = LoyaltyCustomer.objects.filter(
        BranchID=BranchID, CompanyID=CompanyID)
    if loyalty_instances.filter(MobileNo=MobileNo).exists():
        MobileNo_ok = True
    if loyalty_instances.filter(CardNumber=CardNumber).exists():
        CardNumber_ok = True
    is_firstnameExist = False

    sundry_debtor_instance = None
    try:
        AccountLedgerID = data['AccountLedgerID']
    except:
        AccountLedgerID = None
    if AccountLedger.objects.filter(pk=AccountLedgerID).exists():
        sundry_debtor_instance = AccountLedger.objects.get(
            pk=AccountLedgerID)

    if not MobileNo_ok:
        if not loyalty_instances.filter(AccountLedgerID=sundry_debtor_instance, MobileNo=MobileNo, CardNumber=CardNumber):
            card_status_instance = None
            card_type_instance = None
            # if TransactionTypes.objects.filter(pk=CardStatusID).exists():
            #     card_status_instance = TransactionTypes.objects.get(
            #         pk=CardStatusID)
            # if TransactionTypes.objects.filter(pk=CardTypeID).exists():
            #     card_type_instance = TransactionTypes.objects.get(
            #         pk=CardTypeID)
            card_status = MasterType.objects.get(
                Name="Loyalty Card Status", CompanyID=CompanyID, BranchID=BranchID).MasterTypeID
            card_type = MasterType.objects.get(
                Name="Loyalty Card Type", CompanyID=CompanyID, BranchID=BranchID).MasterTypeID
            try:
                card_status_instance = TransactionTypes.objects.get(
                    id=CardStatusID)
            except:
                if TransactionTypes.objects.filter(Name__iexact=CardStatusName, MasterTypeID=card_status, CompanyID=CompanyID).exists():
                    card_status_instance = TransactionTypes.objects.get(
                        Name__iexact=CardStatusName, MasterTypeID=card_status, CompanyID=CompanyID)
                else:
                    TransactionTypesID = trans_type_get_auto_id(
                        TransactionTypes, BranchID, CompanyID)
                    card_status_instance = TransactionTypes.objects.create(
                        MasterTypeID=card_status,
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        CreatedUserID=request.user.id,
                        Action="A",
                        CreatedDate=today,
                        Name=CardStatusName.title(),
                        TransactionTypesID=TransactionTypesID
                    )

            try:
                card_type_instance = TransactionTypes.objects.get(
                    id=CardTypeID)
            except:
                if TransactionTypes.objects.filter(Name__iexact=CardTypeName, MasterTypeID=card_type, CompanyID=CompanyID).exists():
                    card_type_instance = TransactionTypes.objects.get(
                        Name__iexact=CardTypeName, MasterTypeID=card_type, CompanyID=CompanyID)
                else:
                    TransactionTypesID = trans_type_get_auto_id(
                        TransactionTypes, BranchID, CompanyID)
                    card_type_instance = TransactionTypes.objects.create(
                        MasterTypeID=card_type,
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        CreatedUserID=request.user.id, Action="A",
                        CreatedDate=today,
                        Name=CardTypeName.title(),
                        TransactionTypesID=TransactionTypesID

                    )

            if not is_firstnameExist:
                # serialized.save(BrandID=BrandID,CreatedDate=today,ModifiedDate=today)
                loyaltyinstance = LoyaltyCustomer.objects.create(
                    LoyaltyCustomerID=LoyaltyCustomerID,
                    BranchID=BranchID,

                    MobileNo=MobileNo,
                    FirstName=FirstName,
                    Address1=Address1,
                    CardNumber=CardNumber,
                    CardStatusID=card_status_instance,
                    CardTypeID=card_type_instance,
                    AccountLedgerID=sundry_debtor_instance,

                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                )

                LoyaltyCustomer_Log.objects.create(
                    BranchID=BranchID,
                    LoyaltyCustomerID=LoyaltyCustomerID,
                    MobileNo=MobileNo,
                    FirstName=FirstName,
                    Address1=Address1,
                    CardNumber=CardNumber,
                    CardStatusID=card_status_instance,
                    CardTypeID=card_type_instance,
                    AccountLedgerID=sundry_debtor_instance,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                )

                response_data = {
                    "StatusCode": 6000,
                    "LoyaltyCustomerID": loyaltyinstance.LoyaltyCustomerID,
                    "message": "successfully created"
                }

                return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Loyalty Customer Already Exist!!!"
            }
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Mobile Number exists"
        }
        return Response(response_data, status=status.HTTP_200_OK)
    
   
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def rassassy_list_loyality_customer(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    print(CompanyID)

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if LoyaltyCustomer.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
            instances = LoyaltyCustomer.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID)
            serialized = LoyaltyCustomerRestSerializer(instances, many=True)
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Loyalty Customer Not Found in this BranchID!"
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
def rassassy_search_loyality_customer(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    SearchVal = data['SearchVal']
    valLength = len(SearchVal)

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if LoyaltyCustomer.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
            instances = LoyaltyCustomer.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID, FirstName__icontains=SearchVal)
            if not instances:
                instances = LoyaltyCustomer.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID, MobileNo__icontains=SearchVal)
            if valLength < 3 and instances:
                instances = instances.filter()[:10]
            if instances:
                serialized = LoyaltyCustomerRestSerializer(instances, many=True)
                response_data = {
                    "StatusCode": 6000,
                    "data": serialized.data
                }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "Loyalty Customer Not Found"
                }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Loyalty Customer Not Found"
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
def rassassy_loyaltyCustomer(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instance = None
    if LoyaltyCustomer.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = LoyaltyCustomer.objects.get(pk=pk, CompanyID=CompanyID)
        serialized = LoyaltyCustomerRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Loyalty Customer Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def rassassy_edit_loyaltyCustomer(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = LoyaltyCustomer.objects.get(pk=pk, CompanyID=CompanyID)
    BranchID = instance.BranchID
    LoyaltyCustomerID = instance.LoyaltyCustomerID
    MobileNo = data['Phone']
    FirstName = data['Name']
    Address1 = data['Location']
    CardNumber = data['CardNumber']
    CardTypeID = data['CardTypeID']
    CardStatusID = data['CardStatusID']
    CardStatusName = data['CardStatusName']
    CardTypeName = data['CardTypeName']

    Action = 'M'
    is_nameExist = False
    LoyaltyCustomer_ok = False
    if LoyaltyCustomer.objects.filter(BranchID=BranchID, CompanyID=CompanyID, MobileNo=MobileNo).exclude(id=pk).exists():
        LoyaltyCustomer_ok = True

    if not LoyaltyCustomer_ok:
        card_status_instance = None
        card_type_instance = None
        
        card_status = MasterType.objects.get(Name="Loyalty Card Status",CompanyID=CompanyID, BranchID=BranchID).MasterTypeID
        card_type = MasterType.objects.get(Name="Loyalty Card Type",CompanyID=CompanyID, BranchID=BranchID).MasterTypeID
        try:
            card_status_instance = TransactionTypes.objects.get(id=CardStatusID)
        except:
            if TransactionTypes.objects.filter(Name__iexact=CardStatusName,MasterTypeID=card_status,CompanyID=CompanyID).exists():
                card_status_instance = TransactionTypes.objects.get(Name__iexact=CardStatusName,MasterTypeID=card_status,CompanyID=CompanyID)
            else:
                TransactionTypesID = trans_type_get_auto_id(TransactionTypes, BranchID, CompanyID)                          
                card_status_instance = TransactionTypes.objects.create(
                    MasterTypeID=card_status,
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    CreatedUserID=request.user.id,
                    Action="A",
                    CreatedDate=today,
                    Name=CardStatusName.title(),
                    TransactionTypesID=TransactionTypesID
                    )

        try:
            card_type_instance = TransactionTypes.objects.get(id=CardTypeID)
        except:
            if TransactionTypes.objects.filter(Name__iexact=CardTypeName,MasterTypeID=card_type,CompanyID=CompanyID).exists():
                card_type_instance = TransactionTypes.objects.get(Name__iexact=CardTypeName,MasterTypeID=card_type,CompanyID=CompanyID)
            else:
                TransactionTypesID = trans_type_get_auto_id(TransactionTypes, BranchID, CompanyID)                          
                card_type_instance = TransactionTypes.objects.create(
                    MasterTypeID=card_type,
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    CreatedUserID=request.user.id
                    ,Action="A",
                    CreatedDate=today,
                    Name=CardTypeName.title(),
                    TransactionTypesID=TransactionTypesID

                    )

        sundry_debtor_instance = None

        instance.MobileNo = MobileNo
        instance.FirstName = FirstName
        instance.Address1 = Address1
        instance.CardNumber = CardNumber
        instance.CardStatusID = card_status_instance
        instance.CardTypeID = card_type_instance

        instance.Action = Action
        instance.UpdatedDate = today
        instance.CreatedUserID = CreatedUserID
        instance.save()

        LoyaltyCustomer_Log.objects.create(
            BranchID=BranchID,

            LoyaltyCustomerID=LoyaltyCustomerID,

            MobileNo=MobileNo,
            FirstName=FirstName,
            Address1=Address1,
            AccountLedgerID=sundry_debtor_instance,
            CardNumber=CardNumber,
            CardStatusID=card_status_instance,
            CardTypeID=card_type_instance,

            CreatedDate=today,
            UpdatedDate=today,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CompanyID=CompanyID,
        )

        response_data = {
            "StatusCode": 6000,
            "data": data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Mobile Num Exists"
        }

        return Response(response_data, status=status.HTTP_200_OK)

    
    
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def rassassy_delete_loyaltyCustomer(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if LoyaltyCustomer.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = LoyaltyCustomer.objects.get(pk=pk, CompanyID=CompanyID)
        BranchID = instance.BranchID
        LoyaltyCustomerID = instance.LoyaltyCustomerID

        Action = "D"

        instance.delete()

        LoyaltyCustomer_Log.objects.create(
            BranchID=BranchID,

            LoyaltyCustomerID=LoyaltyCustomerID,
            MobileNo=instance.MobileNo,
            FirstName=instance.FirstName,
            LastName=instance.LastName,
            Address1=instance.Address1,
            Address2=instance.Address2,
            AccountLedgerID=instance.AccountLedgerID,
            CardNumber=instance.CardNumber,
            CardTypeID=instance.CardTypeID,
            CardStatusID=instance.CardStatusID,


            CreatedDate=today,
            UpdatedDate=today,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CompanyID=CompanyID,
        )

        response_data = {
            "StatusCode": 6000,
            "message": "Loyalty Customer Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Loyalty Customer Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
