from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v8.pos_apis.serializers import POS_ProductList_Serializer, POS_Sales_Serializer, POS_BranchList_Serializer
from api.v8.brands.serializers import ListSerializer
from api.v8.pos_apis.functions import generate_serializer_errors, get_pin_no, get_TokenNo, get_KitchenID
from rest_framework import status
import datetime
from main.functions import get_company, activity_log
from random import randint
from django.db import transaction, IntegrityError
from main.functions import update_voucher_table
import re
import sys
import os
from api.v8.products.functions import get_auto_AutoBatchCode, update_stock
from api.v8.ledgerPosting.functions import convertOrderdDict
from api.v8.users.serializers import MyCompaniesSerializer, CompaniesSerializer
from brands import models as table
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from datetime import date
from api.v8.parties.serializers import PartiesRestSerializer, PartyListSerializer
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Max, Q, Prefetch, Sum
from api.v8.sales.functions import set_LoyaltyCalculation, get_Genrate_VoucherNo, get_auto_id, get_auto_idMaster, get_auto_stockPostid
from api.v8.accountLedgers.functions import get_auto_LedgerPostid, get_LedgerCode, get_auto_id as generated_ledgerID, UpdateLedgerBalance
from api.v8.salesReturns.functions import get_auto_idMaster as get_returnMasterID, get_auto_id as get_returnDetailID


def call_paginator_all(model_object, page_number, items_per_page):
    paginator = Paginator(model_object, items_per_page)
    content = paginator.page(page_number)
    return content


def list_pagination(list_value, items_per_page, page_no):
    paginator_object = Paginator(list_value, items_per_page)
    get_value = paginator_object.page(page_no).object_list
    return get_value


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def pos_companies(request):
    userId = request.data['userId']
    userId = get_object_or_404(User.objects.filter(id=userId))
    my_company_instances = table.CompanySettings.objects.filter(
        owner=userId, is_deleted=False, business_type__Name="Restaurant")
    my_company_serialized = MyCompaniesSerializer(
        my_company_instances, many=True)
    my_company_json = convertOrderdDict(my_company_serialized.data)

    member_company_instances = table.UserTable.objects.filter(
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
        StateName = i['StateName']
        Email = i['Email']
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
            'StateName': StateName,
            'Email': Email,
            'CompanyImage': CompanyImage
        }
        data.append(dic)

    for i in member_company_json:
        id = i['id']
        CompanyImage = ""
        if table.CompanySettings.objects.get(id=id).CompanyLogo:
            CompanyImage = table.CompanySettings.objects.get(
                id=id).CompanyLogo.url
        CompanyName = i['CompanyName']
        company_type = i['company_type']
        Permission = i['Permission']
        Edition = i['Edition']
        IsPosUser = i['IsPosUser']
        StateName = i['StateName']
        Email = i['Email']
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
            'StateName': StateName,
            'Email': Email,
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
    if table.SoftwareVersion.objects.exists():
        CurrentVersion = table.SoftwareVersion.objects.get().CurrentVersion
        MinimumVersion = table.SoftwareVersion.objects.get().MinimumVersion

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
def pos_product_list(request):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    PriceRounding = data['PriceRounding']
    product_name = data['product_name']
    length = data['length']

    if table.Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        if length < 3:
            instances = table.Product.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
            instances = instances.filter((Q(ProductName__icontains=product_name)) | (
                Q(ProductCode__icontains=product_name)))[:10]
        else:
            instances = table.Product.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
            instances = instances.filter((Q(ProductName__icontains=product_name)) | (
                Q(ProductCode__icontains=product_name)))

        serialized = POS_ProductList_Serializer(instances, many=True, context={
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
def pos_parties(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    CreatedUserID = data['CreatedUserID']

    try:
        page_number = data['page_no']
    except:
        page_number = ""

    try:
        items_per_page = data['items_per_page']
    except:
        items_per_page = ""

    serialized1 = PartyListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        PartyType = serialized1.data['PartyType']

        if PartyType == "1":
            PartyType = "customer"

        elif PartyType == "2":
            PartyType = "supplier"

        if PartyType == "0":

            if table.Parties.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
                if page_number and items_per_page:
                    instances = table.Parties.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID)
                    count = len(instances)
                    ledger_sort_pagination = list_pagination(
                        instances,
                        items_per_page,
                        page_number
                    )
                else:
                    ledger_sort_pagination = table.Parties.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID)
                    count = len(ledger_sort_pagination)
                serialized = PartiesRestSerializer(ledger_sort_pagination, many=True, context={
                                                   "CompanyID": CompanyID, "PriceRounding": PriceRounding})

                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Party',
                             'List Viewed', 'Party List Viewed Successfully.', 'Party List Viewed Successfully.')
                response_data = {
                    "StatusCode": 6000,
                    "data": serialized.data,
                    "count": count,
                }

                return Response(response_data, status=status.HTTP_200_OK)

            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Party',
                             'List Viewed', 'Party List Viewed Failed.', "Parties not found in this branch.")
                response_data = {
                    "StatusCode": 6001,
                    "message": "Parties not found in this branch."
                }

                return Response(response_data, status=status.HTTP_200_OK)

        elif table.Parties.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PartyType=PartyType).exists():

            if page_number and items_per_page:
                instances = table.Parties.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, PartyType=PartyType)
                count = len(instances)
                ledger_sort_pagination = list_pagination(
                    instances,
                    items_per_page,
                    page_number
                )
            else:
                ledger_sort_pagination = table.Parties.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, PartyType=PartyType)
                count = len(ledger_sort_pagination)

            serialized = PartiesRestSerializer(ledger_sort_pagination, many=True, context={
                                               "CompanyID": CompanyID, "PriceRounding": PriceRounding})

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Party',
                         'List Viewed', 'Party List Viewed Successfully.', 'Party List Viewed Successfully.')
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "count": count,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Party',
                         'List Viewed', 'Party List Viewed Failed.', "Parties not found in this branch.")
            response_data = {
                "StatusCode": 6001,
                "message": "Parties not found in this branch."
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch you enterd is not Valid."
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def pos_device_registration(request):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    DeviceName = data['DeviceName']
    DeviceMachineID = data['DeviceMachineID']
    UserID = data['UserID']

    if not table.POS_Devices.objects.filter(IsActive=True, DeviceMachineID=DeviceMachineID).exists():
        warehouse = None
        if table.Warehouse.objects.filter(CompanyID=CompanyID).exists():
            warehouse = table.Warehouse.objects.filter(
                CompanyID=CompanyID).last()
        table.POS_Devices.objects.create(
            DeviceName=DeviceName,
            DeviceMachineID=DeviceMachineID,
            CompanyID=CompanyID,
            WareHouseID=warehouse,
            AutoIncrimentQty=False,
            IsActive=True,
        )

        BranchID = 1
        user_role = ""
        if table.UserTable.objects.filter(CompanyID=CompanyID, customer__user__id=UserID).exists():
            user_table = table.UserTable.objects.filter(
                CompanyID=CompanyID, customer__user__id=UserID).first()
            BranchID = user_table.BranchID
            user_role = user_table.UserType.ID

        response_data = {
            "StatusCode": 6000,
            "CompanyID": CompanyID.id,
            "ExpiryDate": CompanyID.ExpiryDate,
            "DeviceMachineID": DeviceMachineID,
            "warehouse_id": warehouse.id,
            "CompanyState": CompanyID.State.id,
            "CompanyStateName": CompanyID.State.Name,
            "warehouse_name": warehouse.WarehouseName,
            "AutoIncrimentQty": False,
            "IsActive": True,
            "BranchID": BranchID,
            "user_role": user_role
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "this Device has been already Registered with Some Other Company,please Deactivate that Registration to Register with this Company",
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def pos_device_data(request):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    DeviceMachineID = data['DeviceMachineID']
    UserID = data['UserID']

    if table.POS_Devices.objects.filter(IsActive=True, DeviceMachineID=DeviceMachineID, CompanyID=CompanyID).exists():
        device_instance = table.POS_Devices.objects.filter(
            IsActive=True, DeviceMachineID=DeviceMachineID, CompanyID=CompanyID).first()

        BranchID = 1
        user_role = ""
        if table.UserTable.objects.filter(CompanyID=CompanyID, customer__user__id=UserID).exists():
            user_table = table.UserTable.objects.filter(
                CompanyID=CompanyID, customer__user__id=UserID).first()
            BranchID = user_table.BranchID
            user_role = user_table.UserType.ID

        response_data = {
            "StatusCode": 6000,
            "CompanyID": CompanyID.id,
            "ExpiryDate": CompanyID.ExpiryDate,
            "DeviceMachineID": DeviceMachineID,
            "warehouse_id": device_instance.WareHouseID.id,
            "warehouse_name": device_instance.WareHouseID.WarehouseName,
            "AutoIncrimentQty": device_instance.AutoIncrimentQty,
            "IsActive": device_instance.IsActive,
            "CompanyState": CompanyID.State.id,
            "CompanyStateName": CompanyID.State.Name,
            "BranchID": BranchID,
            "user_role": user_role
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "No Activated Device has Registered with Device MachineID under this Company",
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def pos_get_sales(request):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    VoucherNo = data['VoucherNo']
    BranchID = data['BranchID']
    PriceRounding = data['PriceRounding']

    if table.SalesMaster.objects.filter(CompanyID=CompanyID, VoucherNo=VoucherNo, BranchID=BranchID).exists():
        instance = table.SalesMaster.objects.filter(
            CompanyID=CompanyID, VoucherNo=VoucherNo, BranchID=BranchID).first()
        serialized = POS_Sales_Serializer(instance, context={
            "CompanyID": CompanyID, "PriceRounding": PriceRounding})
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Sales not exist with this voucher",
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def pos_get_product_barcode(request):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    Barcode = data['Barcode']
    PriceRounding = data['PriceRounding']

    ProductID = None
    if table.PriceList.objects.filter(CompanyID=CompanyID, Barcode=Barcode, BranchID=BranchID).exists():
        ProductID = table.PriceList.objects.filter(
            CompanyID=CompanyID, Barcode=Barcode, BranchID=BranchID).first().ProductID
    elif table.PriceList.objects.filter(CompanyID=CompanyID, AutoBarcode=Barcode, BranchID=BranchID).exists():
        ProductID = table.PriceList.objects.filter(
            CompanyID=CompanyID, AutoBarcode=Barcode, BranchID=BranchID).first().ProductID
    data = []
    if ProductID:
        if table.Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).exists():
            instance = table.Product.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)
            serialized = POS_ProductList_Serializer(instance, context={
                                                    "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding})
            data = serialized.data
        response_data = {
            "StatusCode": 6000,
            "data": data,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Product not found!",
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def pos_create_sale(request):
    try:
        with transaction.atomic():
            data = request.data

            PriceRounding = data['PriceRounding']

            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            CreatedUserID = data['CreatedUserID']

            today = datetime.datetime.now()
            BranchID = data['BranchID']

            VoucherNo = data['VoucherNo']
            Date = data['Date']
            CreditPeriod = data['CreditPeriod']
            LedgerID = data['LedgerID']
            PriceCategoryID = data['PriceCategoryID']
            EmployeeID = data['EmployeeID']
            SalesAccount = data['SalesAccount']
            CustomerName = data['CustomerName']
            Address1 = data['Address1']
            Address2 = data['Address2']
            Address3 = data['Address3']
            Notes = data['Notes']
            TransactionTypeID = data['TransactionTypeID']
            WarehouseID = data['WarehouseID']
            IsActive = data['IsActive']
            TaxID = data['TaxID']
            TaxType = data['TaxType']
            FinacialYearID = data['FinacialYearID']

            TotalGrossAmt = float(data['TotalGrossAmt'])
            TotalTax = float(data['TotalTax'])
            NetTotal = float(data['NetTotal'])
            AddlDiscAmt = float(data['AddlDiscAmt'])
            AdditionalCost = float(data['AdditionalCost'])
            TotalDiscount = float(data['TotalDiscount'])
            RoundOff = float(data['RoundOff'])
            AddlDiscPercent = float(data['AddlDiscPercent'])
            GrandTotal = float(data['GrandTotal'])

            VATAmount = float(data['VATAmount'])
            SGSTAmount = float(data['SGSTAmount'])
            CGSTAmount = float(data['CGSTAmount'])
            IGSTAmount = float(data['IGSTAmount'])
            TAX1Amount = float(data['TAX1Amount'])
            TAX2Amount = float(data['TAX2Amount'])
            TAX3Amount = float(data['TAX3Amount'])
            KFCAmount = float(data['KFCAmount'])
            BillDiscPercent = float(data['BillDiscPercent'])
            BankAmount = float(data['BankAmount'])
            BillDiscAmt = float(data['BillDiscAmt'])
            Balance = float(data['Balance'])
            OldLedgerBalance = float(data['OldLedgerBalance'])

            BatchID = data['BatchID']
            CashReceived = data['CashReceived']
            # CashAmount = data['CashAmount']
            TableID = data['TableID']
            SeatNumber = data['SeatNumber']
            NoOfGuests = data['NoOfGuests']
            INOUT = data['INOUT']
            TokenNumber = data['TokenNumber']
            CardTypeID = data['CardTypeID']
            CardNumber = data['CardNumber']
            IsPosted = data['IsPosted']
            SalesType = data['SalesType']

            try:
                OrderNo = data['OrderNo']
            except:
                OrderNo = "SO0"

            try:
                order_vouchers = data['order_vouchers']
            except:
                order_vouchers = []
            # =========
            details = data["SalesDetails"]
            TotalTaxableAmount = 0
            for i in details:
                TotalTaxableAmount += float(i['TaxableAmount'])
            # =========

            VoucherType = "SI"
            # VoucherNo Updated
            try:
                PreFix = data['PreFix']
            except:
                PreFix = "SI"

            try:
                Seperator = data['Seperator']
            except:
                Seperator = ""

            try:
                InvoiceNo = data['InvoiceNo']
            except:
                InvoiceNo = 1

            Cash_Account = None
            Bank_Account = None

            if table.UserTable.objects.filter(CompanyID=CompanyID, customer__user__pk=CreatedUserID).exists():
                Cash_Account = table.UserTable.objects.get(
                    CompanyID=CompanyID, customer__user__pk=CreatedUserID).Cash_Account
                Bank_Account = table.UserTable.objects.get(
                    CompanyID=CompanyID, customer__user__pk=CreatedUserID).Bank_Account

            try:
                CashID = data['CashID']
            except:
                CashID = Cash_Account

            try:
                BankID = data['BankID']
            except:
                BankID = Bank_Account

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
                VAT_Treatment = data['VAT_Treatment']
            except:
                VAT_Treatment = ""

            try:
                ShippingAddress = data['ShippingAddress']
            except:
                ShippingAddress = None

            if ShippingAddress:
                if table.UserAdrress.objects.filter(id=ShippingAddress).exists():
                    ShippingAddress = table.UserAdrress.objects.get(
                        id=ShippingAddress)

            if table.SalesOrderMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherNo=OrderNo, IsInvoiced="N").exists():
                order_instance = table.SalesOrderMaster.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, VoucherNo=OrderNo, IsInvoiced="N")
                order_instance.IsInvoiced = "I"
                order_instance.save()
            else:
                if order_vouchers:
                    order_instances = table.SalesOrderMaster.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, VoucherNo__in=order_vouchers, IsInvoiced="N")
                    for b in order_instances:
                        b.IsInvoiced = "I"
                        b.save()

            Action = "A"
            AllowCashReceiptMoreSaleAmt = data['AllowCashReceiptMoreSaleAmt']
            # checking voucher number already exist
            VoucherNoLow = VoucherNo.lower()
            is_voucherExist = False
            insts = table.SalesMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
            if insts:
                for i in insts:
                    voucher_no = i.VoucherNo
                    voucherNo = voucher_no.lower()
                    if VoucherNoLow == voucherNo:
                        is_voucherExist = True

            check_VoucherNoAutoGenerate = False
            is_SaleOK = True

            if table.GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="VoucherNoAutoGenerate").exists():
                check_VoucherNoAutoGenerate = table.GeneralSettings.objects.get(
                    CompanyID=CompanyID, SettingsType="VoucherNoAutoGenerate").SettingsValue

            if is_voucherExist == True and check_VoucherNoAutoGenerate == "True":
                VoucherNo = get_Genrate_VoucherNo(
                    table.SalesMaster, BranchID, CompanyID, "SI")
                is_SaleOK = True
            elif is_voucherExist == False:
                is_SaleOK = True
            else:
                is_SaleOK = False

            if is_SaleOK:

                SalesMasterID = get_auto_idMaster(
                    table.SalesMaster, BranchID, CompanyID)

                if table.Parties.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID).exists():

                    party_instances = table.Parties.objects.filter(
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

                # Loyalty Customer instance
                LoyaltyCustomerID = data['LoyaltyCustomerID']

                loyalty_customer = None
                is_LoyaltyCustomer = False
                if LoyaltyCustomerID:
                    if table.LoyaltyCustomer.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LoyaltyCustomerID=LoyaltyCustomerID).exists():
                        loyalty_customer = table.LoyaltyCustomer.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, LoyaltyCustomerID=LoyaltyCustomerID)
                        is_LoyaltyCustomer = True

                update_voucher_table(
                    CompanyID, CreatedUserID, VoucherType, PreFix, Seperator, InvoiceNo)

                table.SalesMaster_Log.objects.create(
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
                    TableID=TableID,
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
                    VAT_Treatment=VAT_Treatment,
                    ShippingAddress=ShippingAddress,
                )

                sales_instance = table.SalesMaster.objects.create(
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
                    TableID=TableID,
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
                    VAT_Treatment=VAT_Treatment,
                    ShippingAddress=ShippingAddress,
                )
                # ======QRCODE==========
                # url = str("https://viknbooks.vikncodes.com/invoice/") + str(sales_instance.pk)+str('/')+ str('SI')
                url = str("https://viknbooks.com/invoice/") + \
                    str(sales_instance.pk)+str('/') + str('SI')
                # url = request.META['HTTP_ORIGIN'] + "/invoice/" + str(sales_instance.pk)+str('/') + str('SI')
                qr_instance = table.QrCode.objects.create(
                    voucher_type="SI",
                    master_id=sales_instance.pk,
                    url=url,
                )

                # ======END============
                details = data["SalesDetails"]

                if is_LoyaltyCustomer:
                    Loyalty_Point_Expire = data['Loyalty_Point_Expire']
                    try:
                        RadeemPoint = data['RadeemPoint']
                    except:
                        RadeemPoint = None
                    # set_LoyaltyCalculation(sales_instance, loyalty_customer,
                    #                        details, Loyalty_Point_Expire, Action, RadeemPoint)
                    set_LoyaltyCalculation(
                        sales_instance, loyalty_customer, details, Loyalty_Point_Expire, Action, RadeemPoint)
                    # ===========================

                account_group = table.AccountLedger.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).AccountGroupUnder

                # new posting starting from here

                if TaxType == 'VAT':
                    if float(VATAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)

                        table.LedgerPosting.objects.create(
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

                        table.LedgerPosting_Log.objects.create(
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

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, 55, SalesMasterID, VoucherType, VATAmount, "Cr", "create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)

                        table.LedgerPosting.objects.create(
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

                        table.LedgerPosting_Log.objects.create(
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

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, SalesAccount, SalesMasterID, VoucherType, VATAmount, "Dr", "create")

                elif TaxType == 'GST Intra-state B2B' or TaxType == 'GST Intra-state B2C':
                    if float(CGSTAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)

                        table.LedgerPosting.objects.create(
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
                        table.LedgerPosting_Log.objects.create(
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

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, 3, SalesMasterID, VoucherType, CGSTAmount, "Cr", "create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)

                        table.LedgerPosting.objects.create(
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

                        table.LedgerPosting_Log.objects.create(
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

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, SalesAccount, SalesMasterID, VoucherType, CGSTAmount, "Dr", "create")

                    if float(SGSTAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)

                        table.LedgerPosting.objects.create(
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
                        table.LedgerPosting_Log.objects.create(
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

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, 10, SalesMasterID, VoucherType, SGSTAmount, "Cr", "create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)

                        table.LedgerPosting.objects.create(
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

                        table.LedgerPosting_Log.objects.create(
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

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, SalesAccount, SalesMasterID, VoucherType, SGSTAmount, "Dr", "create")

                    if float(KFCAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)

                        table.LedgerPosting.objects.create(
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
                        table.LedgerPosting_Log.objects.create(
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

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, 93, SalesMasterID, VoucherType, KFCAmount, "Cr", "create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)

                        table.LedgerPosting.objects.create(
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

                        table.LedgerPosting_Log.objects.create(
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

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, SalesAccount, SalesMasterID, VoucherType, KFCAmount, "Dr", "create")

                elif TaxType == 'GST Inter-state B2B' or TaxType == 'GST Inter-state B2C':
                    if float(IGSTAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)

                        table.LedgerPosting.objects.create(
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

                        table.LedgerPosting_Log.objects.create(
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

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, 7, SalesMasterID, VoucherType, IGSTAmount, "Cr", "create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)

                        table.LedgerPosting.objects.create(
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

                        table.LedgerPosting_Log.objects.create(
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

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, SalesAccount, SalesMasterID, VoucherType, IGSTAmount, "Dr", "create")

                if not TaxType == 'Export':
                    if float(TAX1Amount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)
                        table.LedgerPosting.objects.create(
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

                        table.LedgerPosting_Log.objects.create(
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

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, 16, SalesMasterID, VoucherType, TAX1Amount, "Cr", "create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)
                        table.LedgerPosting.objects.create(
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

                        table.LedgerPosting_Log.objects.create(
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

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, SalesAccount, SalesMasterID, VoucherType, TAX1Amount, "Dr", "create")

                    if float(TAX2Amount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)
                        table.LedgerPosting.objects.create(
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

                        table.LedgerPosting_Log.objects.create(
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

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, 19, SalesMasterID, VoucherType, TAX2Amount, "Cr", "create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)
                        table.LedgerPosting.objects.create(
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

                        table.LedgerPosting_Log.objects.create(
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

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, SalesAccount, SalesMasterID, VoucherType, TAX2Amount, "Dr", "create")

                    if float(TAX3Amount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)
                        table.LedgerPosting.objects.create(
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

                        table.LedgerPosting_Log.objects.create(
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

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, 22, SalesMasterID, VoucherType, TAX3Amount, "Cr", "create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)
                        table.LedgerPosting.objects.create(
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

                        table.LedgerPosting_Log.objects.create(
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

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, SalesAccount, SalesMasterID, VoucherType, TAX3Amount, "Dr", "create")

                if float(RoundOff) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, 78, SalesMasterID, VoucherType, RoundOff, "Cr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, SalesAccount, SalesMasterID, VoucherType, RoundOff, "Dr", "create")

                if float(RoundOff) < 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    RoundOff = abs(float(RoundOff))

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, 78, SalesMasterID, VoucherType, RoundOff, "Dr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, SalesAccount, SalesMasterID, VoucherType, RoundOff, "Cr", "create")

                if float(TotalDiscount) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, 74, SalesMasterID, VoucherType, TotalDiscount, "Dr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, SalesAccount, SalesMasterID, VoucherType, TotalDiscount, "Cr", "create")

                # credit sales start here
                if float(CashReceived) == 0 and float(BankAmount) == 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, SalesAccount, SalesMasterID, VoucherType, GrandTotal, "Cr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, LedgerID, SalesMasterID, VoucherType, GrandTotal, "Dr", "create")

                # credit sales end here

                # customer with cash and customer with partial cash start here
                elif (account_group == 10 or account_group == 29 or account_group == 32) and float(CashReceived) > 0 and float(BankAmount) == 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, SalesAccount, SalesMasterID, VoucherType, GrandTotal, "Cr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, LedgerID, SalesMasterID, VoucherType, GrandTotal, "Dr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, CashID, SalesMasterID, VoucherType, CashAmount, "Dr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, LedgerID, SalesMasterID, VoucherType, CashAmount, "Cr", "create")

                # customer with cash and customer with partial cash end here

                # customer with bank and customer with partial bank start here
                elif (account_group == 10 or account_group == 29 or account_group == 32) and float(CashReceived) == 0 and float(BankAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, SalesAccount, SalesMasterID, VoucherType, GrandTotal, "Cr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, LedgerID, SalesMasterID, VoucherType, GrandTotal, "Dr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, BankID, SalesMasterID, VoucherType, BankAmount, "Dr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, LedgerID, SalesMasterID, VoucherType, BankAmount, "Cr", "create")

                # customer with bank and customer with partial bank end here

                # bank with cash and cash with cash start here
                elif (account_group == 8 or account_group == 9) and float(CashReceived) > 0 and float(BankAmount) == 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, SalesAccount, SalesMasterID, VoucherType, CashAmount, "Cr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, CashID, SalesMasterID, VoucherType, CashAmount, "Dr", "create")

                    csh_value = float(GrandTotal) - float(CashReceived)
                    if float(csh_value) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        table.LedgerPosting.objects.create(
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

                        table.LedgerPosting_Log.objects.create(
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

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, LedgerID, SalesMasterID, VoucherType, csh_value, "Dr", "create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)

                        table.LedgerPosting.objects.create(
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

                        table.LedgerPosting_Log.objects.create(
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

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, SalesAccount, SalesMasterID, VoucherType, csh_value, "Cr", "create")
                # bank with cash and cash with cash end here

                # bank with bank and cash with bank start here
                elif (account_group == 8 or account_group == 9) and float(CashReceived) == 0 and float(BankAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, SalesAccount, SalesMasterID, VoucherType, BankAmount, "Cr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, BankID, SalesMasterID, VoucherType, BankAmount, "Dr", "create")

                    bnk_value = float(GrandTotal) - float(BankAmount)
                    if not float(bnk_value) == 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)

                        table.LedgerPosting.objects.create(
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

                        table.LedgerPosting_Log.objects.create(
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

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, LedgerID, SalesMasterID, VoucherType, bnk_value, "Dr", "create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)

                        table.LedgerPosting.objects.create(
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

                        table.LedgerPosting_Log.objects.create(
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

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, SalesAccount, SalesMasterID, VoucherType, bnk_value, "Cr", "create")

                # bank with bank and cash with bank end here

                # customer with partial cash /bank and customer with cash/bank
                elif (account_group == 10 or account_group == 29 or account_group == 32) and float(CashReceived) > 0 and float(BankAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, SalesAccount, SalesMasterID, VoucherType, GrandTotal, "Cr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, LedgerID, SalesMasterID, VoucherType, GrandTotal, "Dr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, CashID, SalesMasterID, VoucherType, CashAmount, "Dr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, LedgerID, SalesMasterID, VoucherType, CashAmount, "Cr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, BankID, SalesMasterID, VoucherType, BankAmount, "Dr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, LedgerID, SalesMasterID, VoucherType, BankAmount, "Cr", "create")
                # customer with partial cash /bank and customer with cash/bank

                # cash with cash/bank start here
                elif (account_group == 9 or account_group == 8) and float(CashReceived) > 0 and float(BankAmount) > 0:
                    if float(Balance) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)

                        table.LedgerPosting.objects.create(
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

                        table.LedgerPosting_Log.objects.create(
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

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, SalesAccount, SalesMasterID, VoucherType, Balance, "Cr", "create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)

                        table.LedgerPosting.objects.create(
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

                        table.LedgerPosting_Log.objects.create(
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

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, CashID, SalesMasterID, VoucherType, Balance, "Dr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, BankID, SalesMasterID, VoucherType, BankAmount, "Dr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, SalesAccount, SalesMasterID, VoucherType, BankAmount, "Cr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, SalesAccount, SalesMasterID, VoucherType, CashReceived, "Cr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, CashID, SalesMasterID, VoucherType, CashReceived, "Dr", "create")

                # cash with cash/bank end here
                # new posting ending here

                salesdetails = data["SalesDetails"]
                if salesdetails:
                    for salesdetail in salesdetails:
                        ProductID = salesdetail['ProductID']
                        if ProductID:
                            Qty = salesdetail['Qty']
                            FreeQty = salesdetail['FreeQty']
                            Flavour = salesdetail['Flavour']
                            PriceListID = salesdetail['PriceListID']
                            BatchCode = salesdetail['BatchCode']
                            is_inclusive = salesdetail['is_inclusive']

                            UnitPrice = float(salesdetail['UnitPrice'])
                            InclusivePrice = float(
                                salesdetail['InclusivePrice'])
                            RateWithTax = float(salesdetail['RateWithTax'])
                            CostPerPrice = float(salesdetail['CostPerPrice'])
                            AddlDiscPerc = float(salesdetail['AddlDiscPerc'])
                            AddlDiscAmt = float(salesdetail['AddlDiscAmt'])
                            DiscountPerc = salesdetail['DiscountPerc']
                            DiscountAmount = salesdetail['DiscountAmount']
                            GrossAmount = float(salesdetail['GrossAmount'])
                            TaxableAmount = float(salesdetail['TaxableAmount'])
                            VATPerc = float(salesdetail['VATPerc'])
                            VATAmount = float(salesdetail['VATAmount'])
                            SGSTPerc = float(salesdetail['SGSTPerc'])
                            SGSTAmount = float(salesdetail['SGSTAmount'])
                            CGSTPerc = float(salesdetail['CGSTPerc'])
                            CGSTAmount = float(salesdetail['CGSTAmount'])
                            IGSTPerc = float(salesdetail['IGSTPerc'])
                            IGSTAmount = float(salesdetail['IGSTAmount'])
                            NetAmount = float(salesdetail['NetAmount'])
                            KFCAmount = float(salesdetail['KFCAmount'])
                            TAX1Perc = float(salesdetail['TAX1Perc'])
                            TAX1Amount = float(salesdetail['TAX1Amount'])
                            TAX2Perc = float(salesdetail['TAX2Perc'])
                            TAX2Amount = float(salesdetail['TAX2Amount'])
                            TAX3Perc = float(salesdetail['TAX3Perc'])
                            TAX3Amount = float(salesdetail['TAX3Amount'])

                            # UnitPrice = round(UnitPrice, PriceRounding)
                            # InclusivePrice = round(InclusivePrice, PriceRounding)
                            # RateWithTax = round(RateWithTax, PriceRounding)

                            CostPerPrice = table.PriceList.objects.get(
                                CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).PurchasePrice

                            # CostPerPrice = round(CostPerPrice, PriceRounding)
                            # AddlDiscPerc = round(AddlDiscPerc, PriceRounding)

                            # AddlDiscAmt = round(AddlDiscAmt, PriceRounding)
                            # DiscountPerc = round(DiscountPerc, PriceRounding)
                            # DiscountAmount = round(DiscountAmount, PriceRounding)
                            # GrossAmount = round(GrossAmount, PriceRounding)
                            # TaxableAmount = round(TaxableAmount, PriceRounding)

                            # VATPerc = round(VATPerc, PriceRounding)
                            # VATAmount = round(VATAmount, PriceRounding)
                            # SGSTPerc = round(SGSTPerc, PriceRounding)
                            # SGSTAmount = round(SGSTAmount, PriceRounding)
                            # CGSTPerc = round(CGSTPerc, PriceRounding)

                            # CGSTAmount = round(CGSTAmount, PriceRounding)
                            # IGSTPerc = round(IGSTPerc, PriceRounding)
                            # IGSTAmount = round(IGSTAmount, PriceRounding)
                            # NetAmount = round(NetAmount, PriceRounding)
                            # TAX1Perc = round(TAX1Perc, PriceRounding)

                            # TAX1Amount = round(TAX1Amount, PriceRounding)
                            # TAX2Perc = round(TAX2Perc, PriceRounding)
                            # TAX2Amount = round(TAX2Amount, PriceRounding)
                            # TAX3Perc = round(TAX3Perc, PriceRounding)
                            # TAX3Amount = round(TAX3Amount, PriceRounding)
                            # KFCAmount = round(KFCAmount, PriceRounding)

                            try:
                                SerialNos = salesdetail['SerialNos']
                            except:
                                SerialNos = []

                            try:
                                Description = salesdetail['Description']
                            except:
                                Description = ""

                            try:
                                KFCPerc = salesdetail['KFCPerc']
                            except:
                                KFCPerc = 0

                            try:
                                ProductTaxID = salesdetail['ProductTaxID']
                            except:
                                ProductTaxID = ""

                            # KFCPerc = round(KFCPerc, PriceRounding)
                            # BatchCode = ""

                            if is_inclusive == True:
                                Batch_salesPrice = InclusivePrice
                            else:
                                Batch_salesPrice = UnitPrice

                            product_is_Service = table.Product.objects.get(
                                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).is_Service

                            product_purchasePrice = table.PriceList.objects.get(
                                CompanyID=CompanyID, BranchID=BranchID, PriceListID=PriceListID).PurchasePrice
                            MultiFactor = table.PriceList.objects.get(
                                CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).MultiFactor

                            qty_batch = float(FreeQty) + float(Qty)
                            Qty_batch = float(MultiFactor) * float(qty_batch)

                            check_AllowUpdateBatchPriceInSales = False
                            if product_is_Service == False:
                                if table.GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="AllowUpdateBatchPriceInSales").exists():
                                    check_AllowUpdateBatchPriceInSales = table.GeneralSettings.objects.get(
                                        CompanyID=CompanyID, SettingsType="AllowUpdateBatchPriceInSales").SettingsValue

                                if table.GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
                                    check_EnableProductBatchWise = table.GeneralSettings.objects.get(
                                        CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
                                    # check_BatchCriteria = "PurchasePriceAndSalesPrice"

                                    if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                                        if table.Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
                                            if check_AllowUpdateBatchPriceInSales == "True" or check_AllowUpdateBatchPriceInSales == True:
                                                batch_ins = table.Batch.objects.get(
                                                    CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode)
                                                StockOut = batch_ins.StockOut
                                                BatchCode = batch_ins.BatchCode
                                                NewStock = float(
                                                    StockOut) + float(Qty_batch)
                                                batch_ins.StockOut = NewStock
                                                batch_ins.SalesPrice = Batch_salesPrice
                                                batch_ins.save()
                                            else:
                                                batch_ins = table.Batch.objects.get(
                                                    CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode)
                                                StockOut = batch_ins.StockOut
                                                BatchCode = batch_ins.BatchCode
                                                NewStock = float(
                                                    StockOut) + float(Qty_batch)
                                                batch_ins.StockOut = NewStock
                                                batch_ins.save()
                                        else:
                                            BatchCode = get_auto_AutoBatchCode(
                                                table.Batch, BranchID, CompanyID)
                                            table.Batch.objects.create(
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
                                        if table.Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PriceListID=PriceListID).exists():
                                            batch_ins = table.Batch.objects.get(
                                                CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PriceListID=PriceListID)
                                            StockOut = batch_ins.StockOut
                                            BatchCode = batch_ins.BatchCode
                                            NewStock = float(
                                                StockOut) + float(Qty_batch)
                                            batch_ins.StockOut = NewStock
                                            batch_ins.save()
                                        else:
                                            BatchCode = get_auto_AutoBatchCode(
                                                table.Batch, BranchID, CompanyID)
                                            table.Batch.objects.create(
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

                            SalesDetailsID = get_auto_id(
                                table.SalesDetails, BranchID, CompanyID)

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

                                    table.SerialNumbers.objects.create(
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

                            log_instance = table.SalesDetails_Log.objects.create(
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

                            table.SalesDetails.objects.create(
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

                            if table.GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="SalesPriceUpdate").exists():
                                check_SalesPriceUpdate = table.GeneralSettings.objects.get(
                                    CompanyID=CompanyID, SettingsType="SalesPriceUpdate", BranchID=BranchID).SettingsValue
                                if check_SalesPriceUpdate == "True" or check_SalesPriceUpdate == True:
                                    pri_ins = table.PriceList.objects.get(
                                        CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID)
                                    pri_ins.SalesPrice = Batch_salesPrice
                                    pri_ins.save()

                            if product_is_Service == False:
                                PriceListID_DefUnit = table.PriceList.objects.get(
                                    CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True, BranchID=BranchID).PriceListID

                                qty = float(FreeQty) + float(Qty)

                                Qty = float(MultiFactor) * float(qty)
                                Cost = float(CostPerPrice) / float(MultiFactor)

                                princeList_instance = table.PriceList.objects.get(
                                    CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID_DefUnit, BranchID=BranchID)
                                PurchasePrice = princeList_instance.PurchasePrice
                                SalesPrice = princeList_instance.SalesPrice

                                StockPostingID = get_auto_stockPostid(
                                    table.StockPosting, BranchID, CompanyID)
                                table.StockPosting.objects.create(
                                    StockPostingID=StockPostingID,
                                    BranchID=BranchID,
                                    Action=Action,
                                    Date=Date,
                                    VoucherMasterID=SalesMasterID,
                                    VoucherDetailID=SalesDetailsID,
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

                                table.StockPosting_Log.objects.create(
                                    TransactionID=StockPostingID,
                                    BranchID=BranchID,
                                    Action=Action,
                                    Date=Date,
                                    VoucherMasterID=SalesMasterID,
                                    VoucherDetailID=SalesDetailsID,
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

                response_data = {
                    "StatusCode": 6000,
                    "id": sales_instance.id,
                    "qr_url": qr_instance.qr_code.url,
                    "message": "Sales created Successfully!!!",
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Sales Invoice',
                             'Create', 'Sales Invoice created Failed.', 'VoucherNo already exist')

                response_data = {
                    "StatusCode": 6001,
                    "message": "VoucherNo already exist.Please Change Your Prefix!"
                }

                return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        CompanyID = data['CompanyID']
        CompanyID = get_company(CompanyID)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again",
            "err_descrb": err_descrb
        }

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Sales',
                     'Create', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def pos_create_sale_return(request):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            CreatedUserID = data['CreatedUserID']
            PriceRounding = data['PriceRounding']

            today = datetime.datetime.now()
            BranchID = data['BranchID']
            VoucherDate = data['VoucherDate']
            VoucherNo = data['VoucherNo']
            RefferenceBillNo = data['RefferenceBillNo']
            RefferenceBillDate = data['RefferenceBillDate']
            CreditPeriod = data['CreditPeriod']
            LedgerID = data['LedgerID']
            PriceCategoryID = data['PriceCategoryID']
            EmployeeID = data['EmployeeID']
            SalesAccount = data['SalesAccount']
            DeliveryMasterID = data['DeliveryMasterID']
            OrderMasterID = data['OrderMasterID']
            CustomerName = data['CustomerName']
            Address1 = data['Address1']
            Address2 = data['Address2']
            Address3 = data['Address3']
            Notes = data['Notes']
            FinacialYearID = data['FinacialYearID']
            WarehouseID = data['WarehouseID']
            TableID = data['TableID']
            SeatNumber = data['SeatNumber']
            NoOfGuests = data['NoOfGuests']
            INOUT = data['INOUT']
            TokenNumber = data['TokenNumber']
            IsActive = data['IsActive']
            IsPosted = data['IsPosted']
            SalesType = data['SalesType']
            BatchID = data['BatchID']
            TaxID = data['TaxID']
            TaxType = data['TaxType']
            # CashAmount = data['CashAmount']

            TotalGrossAmt = float(data['TotalGrossAmt'])
            TotalTax = float(data['TotalTax'])
            NetTotal = float(data['NetTotal'])
            AdditionalCost = float(data['AdditionalCost'])
            GrandTotal = float(data['GrandTotal'])
            RoundOff = float(data['RoundOff'])
            CashReceived = float(data['CashReceived'])
            BankAmount = float(data['BankAmount'])
            VATAmount = float(data['VATAmount'])
            SGSTAmount = float(data['SGSTAmount'])
            CGSTAmount = float(data['CGSTAmount'])
            IGSTAmount = float(data['IGSTAmount'])
            TAX1Amount = float(data['TAX1Amount'])
            TAX2Amount = float(data['TAX2Amount'])
            TAX3Amount = float(data['TAX3Amount'])
            AddlDiscPercent = float(data['AddlDiscPercent'])
            AddlDiscAmt = float(data['AddlDiscAmt'])
            TotalDiscount = float(data['TotalDiscount'])
            BillDiscPercent = float(data['BillDiscPercent'])
            BillDiscAmt = float(data['BillDiscAmt'])

            try:
                KFCAmount = float(data['KFCAmount'])
            except:
                KFCAmount = 0

            salesReturnDetails = data["SalesReturnDetails"]
            TotalTaxableAmount = 0
            for salesReturnDetail in salesReturnDetails:
                TaxableAmount = salesReturnDetail['TaxableAmount']
                TotalTaxableAmount += float(TaxableAmount)

            Action = "A"

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
                VAT_Treatment = data['VAT_Treatment']
            except:
                VAT_Treatment = ""

            VoucherType = "SR"

            # VoucherNo Updated
            try:
                PreFix = data['PreFix']
            except:
                PreFix = "SR"

            try:
                Seperator = data['Seperator']
            except:
                Seperator = ""

            try:
                InvoiceNo = data['InvoiceNo']
            except:
                InvoiceNo = 1

            # checking voucher number already exist
            VoucherNoLow = VoucherNo.lower()
            is_voucherExist = False
            insts = table.SalesReturnMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
            if insts:
                for i in insts:
                    voucher_no = i.VoucherNo
                    voucherNo = voucher_no.lower()
                    if VoucherNoLow == voucherNo:
                        is_voucherExist = True

            check_VoucherNoAutoGenerate = False
            is_SalesReturnOK = True

            if table.GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="VoucherNoAutoGenerate").exists():
                check_VoucherNoAutoGenerate = table.GeneralSettings.objects.get(
                    CompanyID=CompanyID, SettingsType="VoucherNoAutoGenerate").SettingsValue

            if is_voucherExist == True and check_VoucherNoAutoGenerate == "True":
                VoucherNo = get_Genrate_VoucherNo(
                    SalesReturnMaster, BranchID, CompanyID, "SR")
                is_SalesReturnOK = True
            elif is_voucherExist == False:
                is_SalesReturnOK = True
            else:
                is_SalesReturnOK = False

            if is_SalesReturnOK:

                SalesReturnMasterID = get_returnMasterID(
                    table.SalesReturnMaster, BranchID, CompanyID)

                if table.Parties.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID).exists():

                    party_instances = table.Parties.objects.filter(
                        CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID)

                    for party_instance in party_instances:

                        party_instance.PartyName = CustomerName

                        party_instance.save()

                CashAmount = float(GrandTotal) - float(BankAmount)

                LoyaltyCustomerID = data['LoyaltyCustomerID']

                loyalty_customer = None
                is_LoyaltyCustomer = False
                if LoyaltyCustomerID:
                    if table.LoyaltyCustomer.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LoyaltyCustomerID=LoyaltyCustomerID).exists():
                        loyalty_customer = table.LoyaltyCustomer.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, LoyaltyCustomerID=LoyaltyCustomerID)
                        is_LoyaltyCustomer = True

                update_voucher_table(
                    CompanyID, CreatedUserID, VoucherType, PreFix, Seperator, InvoiceNo)

                table.SalesReturnMaster_Log.objects.create(
                    LoyaltyCustomerID=loyalty_customer,
                    TotalTaxableAmount=TotalTaxableAmount,
                    TransactionID=SalesReturnMasterID,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    VoucherDate=VoucherDate,
                    RefferenceBillNo=RefferenceBillNo,
                    RefferenceBillDate=RefferenceBillDate,
                    CreditPeriod=CreditPeriod,
                    LedgerID=LedgerID,
                    PriceCategoryID=PriceCategoryID,
                    EmployeeID=EmployeeID,
                    SalesAccount=SalesAccount,
                    DeliveryMasterID=DeliveryMasterID,
                    OrderMasterID=OrderMasterID,
                    CustomerName=CustomerName,
                    Address1=Address1,
                    Address2=Address2,
                    Address3=Address3,
                    Notes=Notes,
                    FinacialYearID=FinacialYearID,
                    TotalGrossAmt=TotalGrossAmt,
                    TotalTax=TotalTax,
                    NetTotal=NetTotal,
                    AdditionalCost=AdditionalCost,
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
                    IsPosted=IsPosted,
                    SalesType=SalesType,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    TaxID=TaxID,
                    TaxType=TaxType,
                    VATAmount=VATAmount,
                    SGSTAmount=SGSTAmount,
                    CGSTAmount=CGSTAmount,
                    IGSTAmount=IGSTAmount,
                    TAX1Amount=TAX1Amount,
                    TAX2Amount=TAX2Amount,
                    TAX3Amount=TAX3Amount,
                    AddlDiscPercent=AddlDiscPercent,
                    AddlDiscAmt=AddlDiscAmt,
                    TotalDiscount=TotalDiscount,
                    BillDiscPercent=BillDiscPercent,
                    BillDiscAmt=BillDiscAmt,
                    CompanyID=CompanyID,
                    KFCAmount=KFCAmount,
                    Country_of_Supply=Country_of_Supply,
                    State_of_Supply=State_of_Supply,
                    GST_Treatment=GST_Treatment,
                    VAT_Treatment=VAT_Treatment,
                )

                sales_return_instance = table.SalesReturnMaster.objects.create(
                    LoyaltyCustomerID=loyalty_customer,
                    TotalTaxableAmount=TotalTaxableAmount,
                    SalesReturnMasterID=SalesReturnMasterID,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    VoucherDate=VoucherDate,
                    RefferenceBillNo=RefferenceBillNo,
                    RefferenceBillDate=RefferenceBillDate,
                    CreditPeriod=CreditPeriod,
                    LedgerID=LedgerID,
                    PriceCategoryID=PriceCategoryID,
                    EmployeeID=EmployeeID,
                    SalesAccount=SalesAccount,
                    DeliveryMasterID=DeliveryMasterID,
                    OrderMasterID=OrderMasterID,
                    CustomerName=CustomerName,
                    Address1=Address1,
                    Address2=Address2,
                    Address3=Address3,
                    Notes=Notes,
                    FinacialYearID=FinacialYearID,
                    TotalGrossAmt=TotalGrossAmt,
                    TotalTax=TotalTax,
                    NetTotal=NetTotal,
                    AdditionalCost=AdditionalCost,
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
                    IsPosted=IsPosted,
                    SalesType=SalesType,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    TaxID=TaxID,
                    TaxType=TaxType,
                    VATAmount=VATAmount,
                    SGSTAmount=SGSTAmount,
                    CGSTAmount=CGSTAmount,
                    IGSTAmount=IGSTAmount,
                    TAX1Amount=TAX1Amount,
                    TAX2Amount=TAX2Amount,
                    TAX3Amount=TAX3Amount,
                    AddlDiscPercent=AddlDiscPercent,
                    AddlDiscAmt=AddlDiscAmt,
                    TotalDiscount=TotalDiscount,
                    BillDiscPercent=BillDiscPercent,
                    BillDiscAmt=BillDiscAmt,
                    CompanyID=CompanyID,
                    KFCAmount=KFCAmount,
                    Country_of_Supply=Country_of_Supply,
                    State_of_Supply=State_of_Supply,
                    GST_Treatment=GST_Treatment,
                    VAT_Treatment=VAT_Treatment,
                )
                # ======QRCODE==========
                # url = request.META['HTTP_ORIGIN'] + "/invoice/" + str(sales_return_instance.pk)+str('/')+ str('SR')
                # url = str("http://localhost:3000/invoice/") + str(sales_return_instance.pk)+str('/')+ str('SR')
                url = str("https://viknbooks.com/invoice/") + \
                    str(sales_return_instance.pk)+str('/') + str('SR')
                print(url)
                qr_instance = table.QrCode.objects.create(
                    voucher_type="SR",
                    master_id=sales_return_instance.pk,
                    url=url,
                )

                # ======END============

                # new posting starting from here

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID)

                table.LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=LedgerID,
                    Debit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                table.LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=LedgerID,
                    Debit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, SalesAccount, SalesReturnMasterID, VoucherType, GrandTotal, "Dr", "create")

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID)

                table.LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=SalesAccount,
                    Credit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                table.LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=SalesAccount,
                    Credit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, LedgerID, SalesReturnMasterID, VoucherType, GrandTotal, "Cr", "create")

                if TaxType == 'VAT':
                    if float(VATAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)

                        table.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=55,
                            RelatedLedgerID=SalesAccount,
                            Debit=VATAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        table.LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=55,
                            RelatedLedgerID=SalesAccount,
                            Debit=VATAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, 55, SalesReturnMasterID, VoucherType, VATAmount, "Dr", "create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)

                        table.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=55,
                            Credit=VATAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        table.LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=55,
                            Credit=VATAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, SalesAccount, SalesReturnMasterID, VoucherType, VATAmount, "Cr", "create")
                # new posting ending  here

                elif TaxType == 'GST Intra-state B2B' or TaxType == 'GST Intra-state B2C':
                    if float(CGSTAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)

                        table.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=3,
                            RelatedLedgerID=SalesAccount,
                            Debit=CGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )
                        table.LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=3,
                            RelatedLedgerID=SalesAccount,
                            Debit=CGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, 3, SalesReturnMasterID, VoucherType, CGSTAmount, "Dr", "create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)

                        table.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=3,
                            Credit=CGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        table.LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=3,
                            Credit=CGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, SalesAccount, SalesReturnMasterID, VoucherType, CGSTAmount, "Cr", "create")

                    if float(SGSTAmount) > 0:

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)

                        table.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=10,
                            RelatedLedgerID=SalesAccount,
                            Debit=SGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )
                        table.LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=10,
                            RelatedLedgerID=SalesAccount,
                            Debit=SGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, 10, SalesReturnMasterID, VoucherType, SGSTAmount, "Dr", "create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)

                        table.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=10,
                            Credit=SGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        table.LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=10,
                            Credit=SGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, SalesAccount, SalesReturnMasterID, VoucherType, SGSTAmount, "Cr", "create")

                    if float(KFCAmount) > 0:

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)

                        table.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=93,
                            RelatedLedgerID=SalesAccount,
                            Debit=KFCAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )
                        table.LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=93,
                            RelatedLedgerID=SalesAccount,
                            Debit=KFCAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, 93, SalesReturnMasterID, VoucherType, KFCAmount, "Dr", "create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)

                        table.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=93,
                            Credit=KFCAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        table.LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=93,
                            Credit=KFCAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, SalesAccount, SalesReturnMasterID, VoucherType, KFCAmount, "Cr", "create")

                elif TaxType == 'GST Inter-state B2B' or TaxType == 'GST Inter-state B2C':
                    if float(IGSTAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)

                        table.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=17,
                            RelatedLedgerID=SalesAccount,
                            Debit=IGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        table.LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=17,
                            RelatedLedgerID=SalesAccount,
                            Debit=IGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, 17, SalesReturnMasterID, VoucherType, IGSTAmount, "Dr", "create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)

                        table.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=17,
                            Credit=IGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        table.LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=17,
                            Credit=IGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, SalesAccount, SalesReturnMasterID, VoucherType, IGSTAmount, "Cr", "create")

                if not TaxType == 'Export':
                    if float(TAX1Amount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)
                        table.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=16,
                            RelatedLedgerID=SalesAccount,
                            Debit=TAX1Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        table.LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=16,
                            RelatedLedgerID=SalesAccount,
                            Debit=TAX1Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, 16, SalesReturnMasterID, VoucherType, TAX1Amount, "Dr", "create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)
                        table.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=16,
                            Credit=TAX1Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        table.LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=16,
                            Credit=TAX1Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, SalesAccount, SalesReturnMasterID, VoucherType, TAX1Amount, "Cr", "create")

                    if float(TAX2Amount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)
                        table.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=19,
                            RelatedLedgerID=SalesAccount,
                            Debit=TAX2Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        table.LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=19,
                            RelatedLedgerID=SalesAccount,
                            Debit=TAX2Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, 19, SalesReturnMasterID, VoucherType, TAX2Amount, "Dr", "create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)
                        table.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=19,
                            Credit=TAX2Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        table.LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=19,
                            Credit=TAX2Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, SalesAccount, SalesReturnMasterID, VoucherType, TAX2Amount, "Cr", "create")

                    if float(TAX3Amount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)
                        table.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=22,
                            RelatedLedgerID=SalesAccount,
                            Debit=TAX3Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        table.LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=22,
                            RelatedLedgerID=SalesAccount,
                            Debit=TAX3Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, 22, SalesReturnMasterID, VoucherType, TAX3Amount, "Dr", "create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)
                        table.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=22,
                            Credit=TAX3Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        table.LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=22,
                            Credit=TAX3Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, SalesAccount, SalesReturnMasterID, VoucherType, TAX3Amount, "Cr", "create")

                if float(RoundOff) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
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

                    table.LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, 78, SalesReturnMasterID, VoucherType, RoundOff, "Dr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
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

                    table.LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, SalesAccount, SalesReturnMasterID, VoucherType, RoundOff, "Cr", "create")

                if float(RoundOff) < 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    RoundOff = abs(float(RoundOff))

                    table.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
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

                    table.LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, 78, SalesReturnMasterID, VoucherType, RoundOff, "Cr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
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

                    table.LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, SalesAccount, SalesReturnMasterID, VoucherType, RoundOff, "Dr", "create")

                if float(TotalDiscount) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=74,
                        RelatedLedgerID=SalesAccount,
                        Credit=TotalDiscount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    table.LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=74,
                        RelatedLedgerID=SalesAccount,
                        Credit=TotalDiscount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, 74, SalesReturnMasterID, VoucherType, TotalDiscount, "Cr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=74,
                        Debit=TotalDiscount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    table.LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=74,
                        Debit=TotalDiscount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, SalesAccount, SalesReturnMasterID, VoucherType, TotalDiscount, "Dr", "create")

                salesReturnDetails = data["SalesReturnDetails"]
                for salesReturnDetail in salesReturnDetails:
                    ProductID = salesReturnDetail['ProductID']
                    if ProductID:
                        # SalesReturnMasterID = serialized.data['SalesReturnMasterID']
                        DeliveryDetailsID = salesReturnDetail['DeliveryDetailsID']
                        OrderDetailsID = salesReturnDetail['OrderDetailsID']
                        Qty = salesReturnDetail['Qty']
                        FreeQty = salesReturnDetail['FreeQty']
                        Flavour = salesReturnDetail['Flavour']

                        UnitPrice = float(salesReturnDetail['UnitPrice'])
                        InclusivePrice = float(
                            salesReturnDetail['InclusivePrice'])
                        RateWithTax = float(salesReturnDetail['RateWithTax'])
                        # CostPerPrice = float(salesReturnDetail['CostPerPrice'])
                        PriceListID = salesReturnDetail['PriceListID']
                        DiscountPerc = float(salesReturnDetail['DiscountPerc'])
                        DiscountAmount = float(
                            salesReturnDetail['DiscountAmount'])
                        GrossAmount = float(salesReturnDetail['GrossAmount'])
                        TaxableAmount = float(
                            salesReturnDetail['TaxableAmount'])
                        VATPerc = float(salesReturnDetail['VATPerc'])
                        VATAmount = float(salesReturnDetail['VATAmount'])
                        SGSTPerc = float(salesReturnDetail['SGSTPerc'])
                        SGSTAmount = float(salesReturnDetail['SGSTAmount'])
                        CGSTPerc = float(salesReturnDetail['CGSTPerc'])
                        CGSTAmount = float(salesReturnDetail['CGSTAmount'])
                        IGSTPerc = float(salesReturnDetail['IGSTPerc'])
                        IGSTAmount = float(salesReturnDetail['IGSTAmount'])
                        NetAmount = float(salesReturnDetail['NetAmount'])
                        AddlDiscPercent = float(
                            salesReturnDetail['AddlDiscPerc'])
                        AddlDiscAmt = float(salesReturnDetail['AddlDiscAmt'])
                        TAX1Perc = float(salesReturnDetail['TAX1Perc'])
                        TAX1Amount = float(salesReturnDetail['TAX1Amount'])
                        TAX2Perc = float(salesReturnDetail['TAX2Perc'])
                        TAX2Amount = float(salesReturnDetail['TAX2Amount'])
                        TAX3Perc = float(salesReturnDetail['TAX3Perc'])
                        TAX3Amount = float(salesReturnDetail['TAX3Amount'])
                        try:
                            KFCAmount = float(salesReturnDetail['KFCAmount'])
                        except:
                            KFCAmount = 0

                        try:
                            ProductTaxID = salesReturnDetail['ProductTaxID']
                        except:
                            ProductTaxID = ""

                        CostPerPrice = table.PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).PurchasePrice

                        try:
                            SerialNos = salesReturnDetail['SerialNos']
                        except:
                            SerialNos = []

                        try:
                            Description = salesReturnDetail['Description']
                        except:
                            Description = ""
                        try:
                            KFCPerc = salesReturnDetail['KFCPerc']
                        except:
                            KFCPerc = 0

                        try:
                            BatchCode = salesReturnDetail['BatchCode']
                        except:
                            BatchCode = 0
                        try:
                            is_inclusive = salesReturnDetail['is_inclusive']
                        except:
                            is_inclusive = False

                        if is_inclusive == True:
                            Batch_salesPrice = InclusivePrice
                        else:
                            Batch_salesPrice = UnitPrice

                        product_is_Service = table.Product.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).is_Service

                        product_purchasePrice = table.PriceList.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, PriceListID=PriceListID).PurchasePrice
                        MultiFactor = table.PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).MultiFactor

                        qty_batch = float(FreeQty) + float(Qty)
                        Qty_batch = float(MultiFactor) * float(qty_batch)

                        SalesReturnQty = Qty
                        SalesReturnDetailsID = get_returnDetailID(
                            table.SalesReturnDetails, BranchID, CompanyID)

                        if SerialNos:
                            for sn in SerialNos:
                                table.SerialNumbers.objects.create(
                                    VoucherType="SR",
                                    CompanyID=CompanyID,
                                    SerialNo=sn["SerialNo"],
                                    ItemCode=sn["ItemCode"],
                                    SalesMasterID=SalesReturnMasterID,
                                    SalesDetailsID=SalesReturnDetailsID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CreatedUserID=CreatedUserID,
                                )

                        ledger_instance = table.SalesReturnDetails_Log.objects.create(
                            TransactionID=SalesReturnDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            SalesReturnMasterID=SalesReturnMasterID,
                            DeliveryDetailsID=DeliveryDetailsID,
                            OrderDetailsID=OrderDetailsID,
                            ProductID=ProductID,
                            Qty=Qty,
                            FreeQty=FreeQty,
                            UnitPrice=UnitPrice,
                            InclusivePrice=InclusivePrice,
                            RateWithTax=RateWithTax,
                            CostPerPrice=CostPerPrice,
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
                            NetAmount=NetAmount,
                            Flavour=Flavour,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            AddlDiscPercent=AddlDiscPercent,
                            AddlDiscAmt=AddlDiscAmt,
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            CompanyID=CompanyID,
                            BatchCode=BatchCode,
                            KFCAmount=KFCAmount,
                            KFCPerc=KFCPerc,
                            Description=Description,
                            ProductTaxID=ProductTaxID
                        )

                        table.SalesReturnDetails.objects.create(
                            SalesReturnDetailsID=SalesReturnDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            SalesReturnMasterID=SalesReturnMasterID,
                            DeliveryDetailsID=DeliveryDetailsID,
                            OrderDetailsID=OrderDetailsID,
                            ProductID=ProductID,
                            Qty=Qty,
                            FreeQty=FreeQty,
                            UnitPrice=UnitPrice,
                            InclusivePrice=InclusivePrice,
                            RateWithTax=RateWithTax,
                            CostPerPrice=CostPerPrice,
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
                            NetAmount=NetAmount,
                            Flavour=Flavour,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            AddlDiscPercent=AddlDiscPercent,
                            AddlDiscAmt=AddlDiscAmt,
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            CompanyID=CompanyID,
                            BatchCode=BatchCode,
                            LogID=ledger_instance.ID,
                            KFCAmount=KFCAmount,
                            KFCPerc=KFCPerc,
                            Description=Description,
                            ProductTaxID=ProductTaxID
                        )

                        MultiFactor = table.PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).MultiFactor
                        PriceListID = table.PriceList.objects.get(
                            CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True, BranchID=BranchID).PriceListID

                        qty = float(FreeQty) + float(Qty)

                        Qty = float(MultiFactor) * float(qty)
                        Cost = float(CostPerPrice) / float(MultiFactor)

                        princeList_instance = table.PriceList.objects.get(
                            CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID, BranchID=BranchID)
                        PurchasePrice = princeList_instance.PurchasePrice
                        SalesPrice = princeList_instance.SalesPrice

                        if product_is_Service == False:
                            StockPostingID = get_auto_stockPostid(
                                table.StockPosting, BranchID, CompanyID)

                            table.StockPosting.objects.create(
                                StockPostingID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=VoucherDate,
                                VoucherMasterID=SalesReturnMasterID,
                                VoucherDetailID=SalesReturnDetailsID,
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

                            table.StockPosting_Log.objects.create(
                                TransactionID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=VoucherDate,
                                VoucherMasterID=SalesReturnMasterID,
                                VoucherDetailID=SalesReturnDetailsID,
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

                            update_stock(CompanyID, BranchID, ProductID)

                        if table.SalesMaster.objects.filter(CompanyID=CompanyID, VoucherNo=RefferenceBillNo, BranchID=BranchID).exists():
                            SalesMaster_instance = table.SalesMaster.objects.get(
                                CompanyID=CompanyID, VoucherNo=RefferenceBillNo, BranchID=BranchID)
                            SalesMasterID = SalesMaster_instance.SalesMasterID

                            if table.SalesDetails.objects.filter(CompanyID=CompanyID, SalesMasterID=SalesMasterID, BranchID=BranchID, ProductID=ProductID).exists():
                                SalesDetails_instances = table.SalesDetails.objects.filter(
                                    CompanyID=CompanyID, SalesMasterID=SalesMasterID, BranchID=BranchID, ProductID=ProductID)

                                for i in SalesDetails_instances:
                                    ReturnQty = i.ReturnQty
                                    SalesReturnQty = SalesReturnQty
                                    ReturnQty = float(ReturnQty) - \
                                        float(SalesReturnQty)
                                    i.ReturnQty = ReturnQty

                                    i.save()

                response_data = {
                    "StatusCode": 6000,
                    "id": sales_return_instance.id,
                    "qr_url": qr_instance.qr_code.url,
                    "message": "Sales Return created Successfully!!!",
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Sales Return',
                             'Create', 'Sales Return created Failed.', 'VoucherNo already exist')

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
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Sales Return',
                     'Create', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def pos_get_device_data(request):
    today = datetime.datetime.now()
    data = request.data
    DeviceMachineID = data['DeviceMachineID']
    UserID = data['UserID']

    if table.POS_Devices.objects.filter(IsActive=True, DeviceMachineID=DeviceMachineID).exists():
        device_instance = table.POS_Devices.objects.filter(
            IsActive=True, DeviceMachineID=DeviceMachineID).first()

        BranchID = 1
        user_role = ""
        if table.UserTable.objects.filter(CompanyID=device_instance.CompanyID, customer__user__id=UserID).exists():
            user_table = table.UserTable.objects.filter(
                CompanyID=device_instance.CompanyID, customer__user__id=UserID).first()
            BranchID = user_table.BranchID
            user_role = user_table.UserType.ID

        response_data = {
            "StatusCode": 6000,
            "CompanyID": device_instance.CompanyID.id,
            "ExpiryDate": device_instance.CompanyID.ExpiryDate,
            "DeviceMachineID": DeviceMachineID,
            "warehouse_id": device_instance.WareHouseID.id,
            "warehouse_name": device_instance.WareHouseID.WarehouseName,
            "AutoIncrimentQty": device_instance.AutoIncrimentQty,
            "IsActive": device_instance.IsActive,
            "CompanyState": device_instance.CompanyID.State.id,
            "CompanyStateName": device_instance.CompanyID.State.Name,
            "BranchID": BranchID,
            "user_role": user_role,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "No Activated Device has Registered with Device MachineID under this Company",
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def pos_branch_list(request):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data['CompanyID']

    if table.Branch.objects.filter(CompanyID=CompanyID).exists():
        instances = table.Branch.objects.filter(CompanyID=CompanyID)
        serialized = POS_BranchList_Serializer(
            instances, many=True, context={"request": request, "CompanyID": CompanyID})
        data = serialized.data
        response_data = {
            "StatusCode": 6000,
            "data": data,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Product not found!",
        }

        return Response(response_data, status=status.HTTP_200_OK)
