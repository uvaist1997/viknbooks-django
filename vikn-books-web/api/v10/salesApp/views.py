from fatoora import Fatoora
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from api.v10.accountLedgers.functions import UpdateLedgerBalance
from api.v10.companySettings.serializers import CompanySettingsPrintRestSerializer
from api.v10.payments.serializers import BillwiseMasterSerializer
from api.v10.reportQuerys.functions import query_stock_report_data
from api.v10.sales.functions import SetBatchInSales, edit_LoyaltyCalculation, get_BillwiseDetailsID, get_BillwiseMasterID, get_CashAmount, get_Genrate_VoucherNo, get_actual_point, get_auto_id, get_auto_idMaster, get_auto_stockPostid, handleBillwiseChanges, set_LoyaltyCalculation
from api.v10.sales.serializers import SalesMasterRestSerializer
from api.v10.sales.views import salesMaster
from api.v10.salesApp.serializers import ExpenseListSerializer, LedgerSerializer, POS_ProductList_Serializer, PaymentListSerializer, ReceiptListSerializer, SalesFaeraSerializer, SalesListSerializer, SalesOrderListSerializer, SalesReturnListSerializer, SalesReturnMasterSerializer, StockOrderListSerializer
from api.v10.brands.serializers import ListSerializer
from api.v10.salesApp.functions import generate_serializer_errors, get_pin_no, get_TokenNo, get_KitchenID
from rest_framework import status
import datetime
from api.v10.stockTransfers.serializers import StockTransferMaster_IDRestSerializer
from main.functions import converted_float, generateVoucherNoFunction, get_BalanceFromLedgerPost, get_BranchLedgerId_for_LedgerPosting, get_GeneralSettings, get_LedgerBalance, get_ModelInstance, get_ProductStock, get_ProductWareHouseStock, get_company, activity_log, get_financial_year_dates, get_financialYearDates, get_nth_day_date
from random import randint
from django.db import transaction, IntegrityError
from main.functions import update_voucher_table
import re
import sys
import os
from api.v10.accountLedgers.functions import get_auto_LedgerPostid
from api.v10.products.functions import get_auto_AutoBatchCode, update_stock
from api.v10.ledgerPosting.functions import convertOrderdDict
from api.v10.users.serializers import ImageSerializer, MyCompaniesSerializer, CompaniesSerializer
from brands import models as table
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from datetime import date
from api.v10.parties.serializers import PartiesRestSerializer, PartyListSerializer
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Max, Q, Prefetch, Sum, F
from api.v10.users.serializers import LoginSerializer
from api.v10.general.functions import get_current_role
from api.v10.posholds.serializers import POS_Product_Serializer
from django.db.models import Q
from api.v10.payments.functions import get_auto_id as payment_detailid, get_auto_idMaster as payment_masterid
from api.v10.receipts.functions import get_auto_id as receipt_detailid, get_auto_idMaster as receipt_masterid
from api.v10.users.functions import get_general_settings
from api.v10.salesReturns.functions import (
    generate_serializer_errors,
    get_auto_id as salesReturnDetailID,
    get_auto_idMaster as salesReturnMasterid,
    sales_return_point,
)
from api.v10.loyaltyProgram.functions import get_point_auto_id
from api.v10.salesReturns.serializers import (
    SalesReturnMasterRestSerializer,
)
from api.v10.salesOrders.serializers import (
    SalesOrderMasterRestSerializer,
)
from api.v10.expense.functions import get_masterID as expenseMasterID, get_detailID as expenseDetailID
from api.v10.expense.serializers import ExpenseMasterSerializer
from api.v10.stockTransfers.functions import (
    get_auto_id as stockdetailsid,
    get_auto_idMaster as stockmasterid,
)
from api.v10.salesOrders.functions import get_auto_idMaster as OrderMasterID, get_auto_id as OrderDetailID
from django.db.models.functions import TruncMonth
from django.db.models import Count, Sum
from django.utils.translation import activate
from django.template.loader import get_template
import pdfkit
from django.http import HttpResponse
import json
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render
from api.v10.accountLedgers.serializers import (
    AccountLedgerListSerializer
)


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
def salesApp_companies(request):
    userId = request.data['userId']
    userId = get_object_or_404(User.objects.filter(id=userId))
    my_company_instances = table.CompanySettings.objects.filter(
        owner=userId, is_deleted=False).exclude(business_type__Name="Restaurant")
    my_company_serialized = MyCompaniesSerializer(
        my_company_instances, many=True)
    my_company_json = convertOrderdDict(my_company_serialized.data)

    member_company_instances = table.UserTable.objects.filter(
        customer__user=userId).exclude(CompanyID__business_type__Name="Restaurant")
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
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def pos_product_list(request):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    PriceRounding = data['PriceRounding']
    page_number = data['page_no']
    items_per_page = data['items_per_page']
    DeviceCode = data['DeviceCode']

    if table.Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        instances = table.Product.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID)
        if page_number and items_per_page:
            instances = list_pagination(
                instances,
                items_per_page,
                page_number
            )

        serialized = POS_Product_Serializer(instances, many=True, context={
            "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding})

        data = serialized.data
        StockAlert = ""
        WarehouseID = None
        final_data = []
        if table.POS_Devices.objects.filter(DeviceCode=DeviceCode).exists():
            device = table.POS_Devices.objects.filter(
                DeviceCode=DeviceCode).first()
            StockAlert = device.StockAlert
            WarehouseID = device.WareHouseID.WarehouseID

            for d in data:
                ProductID = d["ProductID"]
                BatchCode = ""
                Stock = get_ProductWareHouseStock(
                    CompanyID, BranchID, ProductID, WarehouseID, BatchCode)
                d["Stock"] = Stock
                d["StockAlert"] = StockAlert
                final_data.append(d)
                # if ((StockAlert == "block" and Stock > 0) or (StockAlert in ["warning", "ignore"])):
                #     final_data.append(d)

        response_data = {
            "StatusCode": 6000,
            "data": final_data
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
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def pos_product_search(request):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    PriceRounding = data['PriceRounding']
    product_name = data['product_name']
    length = data['length']
    DeviceCode = data['DeviceCode']

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

        serialized = POS_Product_Serializer(instances, many=True, context={
            "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding})

        data = serialized.data
        StockAlert = ""
        WarehouseID = None
        final_data = []
        if table.POS_Devices.objects.filter(DeviceCode=DeviceCode).exists():
            device = table.POS_Devices.objects.filter(
                DeviceCode=DeviceCode).first()
            StockAlert = device.StockAlert
            WarehouseID = device.WareHouseID.WarehouseID

            for d in data:
                ProductID = d["ProductID"]
                BatchCode = ""
                Stock = get_ProductWareHouseStock(
                    CompanyID, BranchID, ProductID, WarehouseID, BatchCode)
                d["Stock"] = Stock
                d["StockAlert"] = StockAlert
                final_data.append(d)
                # if ((StockAlert == "block" and Stock > 0) or (StockAlert in ["warning", "ignore"])):
                #     final_data.append(d)

        response_data = {
            "StatusCode": 6000,
            "data": final_data
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
@authentication_classes((JWTTokenUserAuthentication,))
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
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def salesApp_login(request):
    serialized = LoginSerializer(data=request.data)
    CreatedUserID = ""
    is_verified = False
    customer_ins = None
    data = request.data

    try:
        is_mobile = data['is_mobile']
    except:
        is_mobile = False

    if serialized.is_valid():
        username = serialized.data['username']
        password = serialized.data['password']

        if User.objects.filter(email=username).exists():
            email = username
            username = User.objects.get(email=email).username

        if User.objects.filter(username=username).exists():
            user_ins = User.objects.get(username=username)
            if user_ins.is_active == True:
                is_verified = True

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            request.session['current_role'] = get_current_role(request)
            headers = {
                'Content-Type': 'application/json',
            }
            data = '{"username": "' + username + \
                '", "password": "' + password + '" }'
            protocol = "http://"
            if request.is_secure():
                protocol = "https://"

            web_host = request.get_host()
            request_url = protocol + web_host + "/api/v1/auth/token/"
            response = requests.post(request_url, headers=headers, data=data)
            if response.status_code == 200:
                token_datas = response.json()
                LastToken = token_datas['access']

                if table.Customer.objects.filter(user__username=username).exists():
                    customer_ins = table.Customer.objects.filter(
                        user__username=username).first()
                    if is_mobile == True:
                        customer_ins.LastLoginTokenMobile = LastToken
                    else:
                        customer_ins.LastLoginToken = LastToken
                    customer_ins.save()

                data = response.json()
                success = 6000
                message = "Login successfully"

                return Response(
                    {
                        'success': success,
                        'data': data,
                        'refresh': data['refresh'],
                        'access': data['access'],
                        'user_id': data['user_id'],
                        'role': data['role'],
                        'message': message,
                        'error': None,
                        "CreatedUserID": CreatedUserID,
                        'username': username,
                    },
                    status=status.HTTP_200_OK)
            else:
                success = 6001
                data = None
                error = "please contact admin to solve this problem."
                return Response(
                    {
                        'success': success,
                        'data': data,
                        'error': error
                    },
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            success = 6001
            data = None
            if is_verified == False:
                error = "Please Verify Your Email to Login"
            else:
                error = "User not found"
            return Response(
                {
                    'success': success,
                    'data': data,
                    'error': error
                },
                status=status.HTTP_400_BAD_REQUEST)
    else:
        message = generate_serializer_errors(serialized._errors)
        success = 6001
        data = None
        return Response(
            {
                'success': success,
                'data': data,
                'error': message,
            },
            status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def salesApp_create_sale(request):
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

            TotalGrossAmt = converted_float(data['TotalGrossAmt'])
            TotalTax = converted_float(data['TotalTax'])
            NetTotal = converted_float(data['NetTotal'])
            AddlDiscAmt = converted_float(data['AddlDiscAmt'])
            AdditionalCost = converted_float(data['AdditionalCost'])
            TotalDiscount = converted_float(data['TotalDiscount'])
            RoundOff = converted_float(data['RoundOff'])
            AddlDiscPercent = converted_float(data['AddlDiscPercent'])
            GrandTotal = converted_float(data['GrandTotal'])

            VATAmount = converted_float(data['VATAmount'])
            SGSTAmount = converted_float(data['SGSTAmount'])
            CGSTAmount = converted_float(data['CGSTAmount'])
            IGSTAmount = converted_float(data['IGSTAmount'])
            TAX1Amount = converted_float(data['TAX1Amount'])
            TAX2Amount = converted_float(data['TAX2Amount'])
            TAX3Amount = converted_float(data['TAX3Amount'])
            KFCAmount = converted_float(data['KFCAmount'])
            BillDiscPercent = converted_float(data['BillDiscPercent'])
            BankAmount = converted_float(data['BankAmount'])
            BillDiscAmt = converted_float(data['BillDiscAmt'])
            Balance = converted_float(data['Balance'])
            OldLedgerBalance = converted_float(data['OldLedgerBalance'])

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
                TotalTaxableAmount += converted_float(i['TaxableAmount'])
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

            if table.UserTable.objects.filter(CompanyID=CompanyID, customer__user__pk=CreatedUserID,Active=True).exists():
                Cash_Account = table.UserTable.objects.get(
                    CompanyID=CompanyID, customer__user__pk=CreatedUserID,Active=True).Cash_Account
                Bank_Account = table.UserTable.objects.get(
                    CompanyID=CompanyID, customer__user__pk=CreatedUserID, Active=True).Bank_Account

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

            check_VoucherNoAutoGenerate = True
            is_SaleOK = True

            if table.GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="VoucherNoAutoGenerate").exists():
                check_VoucherNoAutoGenerate = table.GeneralSettings.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, SettingsType="VoucherNoAutoGenerate").SettingsValue

            if is_voucherExist == True and check_VoucherNoAutoGenerate == "True" or check_VoucherNoAutoGenerate == True:
                # VoucherNo = get_Genrate_VoucherNo(
                #     SalesMaster, BranchID, CompanyID, "SI")
                VoucherNo, InvoiceNo, PreFix, Seperator = generateVoucherNoFunction(
                    CompanyID,  CreatedUserID, VoucherType, BranchID)
                is_SaleOK = True
            elif is_voucherExist == False:
                is_SaleOK = True
            else:
                is_SaleOK = False

            if is_SaleOK:
                SalesMasterID = get_auto_idMaster(
                    table.SalesMaster, BranchID, CompanyID)

                if AllowCashReceiptMoreSaleAmt == True or AllowCashReceiptMoreSaleAmt == "true":
                    CashAmount = CashReceived
                elif converted_float(Balance) < 0:
                    CashAmount = converted_float(
                        GrandTotal) - converted_float(BankAmount)
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
                
                # billwise table insertion
                handleBillwiseChanges(CompanyID,BranchID,CashReceived,BankAmount,GrandTotal,LedgerID,VoucherNo,VoucherType,"create",CreditPeriod,SalesMasterID,Date)
                # enable_billwise = get_GeneralSettings(
                #     CompanyID, BranchID, "EnableBillwise")
                # total_amount_received = converted_float(
                #     CashReceived) + converted_float(BankAmount)
                # if enable_billwise and converted_float(total_amount_received) <= converted_float(GrandTotal) and table.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder__in=[10, 29]).exists():
                #     BillwiseMasterID = get_BillwiseMasterID(
                #         BranchID, CompanyID)
                #     DueDate = get_nth_day_date(CreditPeriod)
                #     table.BillWiseMaster.objects.create(
                #         CompanyID=CompanyID,
                #         BranchID=BranchID,
                #         BillwiseMasterID=BillwiseMasterID,
                #         InvoiceNo=VoucherNo,
                #         TransactionID=SalesMasterID,
                #         VoucherType=VoucherType,
                #         VoucherDate=Date,
                #         InvoiceAmount=GrandTotal,
                #         Payments=total_amount_received,
                #         DueDate=DueDate,
                #         CustomerID=LedgerID
                #     )

                #     BillwiseDetailsID = get_BillwiseDetailsID(
                #         BranchID, CompanyID)
                #     table.BillWiseDetails.objects.create(
                #         CompanyID=CompanyID,
                #         BranchID=BranchID,
                #         BillwiseDetailsID=BillwiseDetailsID,
                #         BillwiseMasterID=BillwiseMasterID,
                #         InvoiceNo=VoucherNo,
                #         VoucherType=VoucherType,
                #         PaymentDate=Date,
                #         Payments=total_amount_received,
                #         PaymentVoucherType=VoucherType,
                #         PaymentInvoiceNo=VoucherNo
                #     )
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
                    CompanyID=CompanyID, LedgerID=LedgerID).AccountGroupUnder

                # new posting starting from here

                if TaxType == 'VAT':
                    if converted_float(VATAmount) > 0:
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
                    if converted_float(CGSTAmount) > 0:
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

                    if converted_float(SGSTAmount) > 0:
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

                    if converted_float(KFCAmount) > 0:
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
                    if converted_float(IGSTAmount) > 0:
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
                    if converted_float(TAX1Amount) > 0:
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

                    if converted_float(TAX2Amount) > 0:
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

                    if converted_float(TAX3Amount) > 0:
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

                if converted_float(RoundOff) > 0:

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

                if converted_float(RoundOff) < 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)
                    RoundOff = abs(converted_float(RoundOff))
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

                if converted_float(TotalDiscount) > 0:

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
                if converted_float(CashReceived) == 0 and converted_float(BankAmount) == 0:
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
                elif (account_group == 10 or account_group == 29 or account_group == 32) and converted_float(CashReceived) > 0 and converted_float(BankAmount) == 0:
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
                elif (account_group == 10 or account_group == 29 or account_group == 32) and converted_float(CashReceived) == 0 and converted_float(BankAmount) > 0:
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
                elif (account_group == 8 or account_group == 9) and converted_float(CashReceived) > 0 and converted_float(BankAmount) == 0:
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

                    csh_value = converted_float(
                        GrandTotal) - converted_float(CashReceived)
                    if converted_float(csh_value) > 0:
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
                elif (account_group == 8 or account_group == 9) and converted_float(CashReceived) == 0 and converted_float(BankAmount) > 0:
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

                    bnk_value = converted_float(
                        GrandTotal) - converted_float(BankAmount)
                    if not converted_float(bnk_value) == 0:
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
                elif (account_group == 10 or account_group == 29 or account_group == 32) and converted_float(CashReceived) > 0 and converted_float(BankAmount) > 0:
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
                elif (account_group == 9 or account_group == 8) and converted_float(CashReceived) > 0 and converted_float(BankAmount) > 0:
                    if converted_float(Balance) > 0:
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
                            try:
                                IsReturn = salesdetail['IsReturn']
                            except:
                                IsReturn = False

                            UnitPrice = converted_float(
                                salesdetail['UnitPrice'])
                            InclusivePrice = converted_float(
                                salesdetail['InclusivePrice'])
                            RateWithTax = converted_float(
                                salesdetail['RateWithTax'])
                            CostPerPrice = converted_float(
                                salesdetail['CostPerPrice'])
                            AddlDiscPerc = converted_float(
                                salesdetail['AddlDiscPerc'])
                            AddlDiscAmt = converted_float(
                                salesdetail['AddlDiscAmt'])
                            DiscountPerc = salesdetail['DiscountPerc']
                            DiscountAmount = salesdetail['DiscountAmount']
                            GrossAmount = converted_float(
                                salesdetail['GrossAmount'])
                            TaxableAmount = converted_float(
                                salesdetail['TaxableAmount'])
                            VATPerc = converted_float(salesdetail['VATPerc'])
                            VATAmount = converted_float(
                                salesdetail['VATAmount'])
                            SGSTPerc = converted_float(salesdetail['SGSTPerc'])
                            SGSTAmount = converted_float(
                                salesdetail['SGSTAmount'])
                            CGSTPerc = converted_float(salesdetail['CGSTPerc'])
                            CGSTAmount = converted_float(
                                salesdetail['CGSTAmount'])
                            IGSTPerc = converted_float(salesdetail['IGSTPerc'])
                            IGSTAmount = converted_float(
                                salesdetail['IGSTAmount'])
                            NetAmount = converted_float(
                                salesdetail['NetAmount'])
                            KFCAmount = converted_float(
                                salesdetail['KFCAmount'])
                            TAX1Perc = converted_float(salesdetail['TAX1Perc'])
                            TAX1Amount = converted_float(
                                salesdetail['TAX1Amount'])
                            TAX2Perc = converted_float(salesdetail['TAX2Perc'])
                            TAX2Amount = converted_float(
                                salesdetail['TAX2Amount'])
                            TAX3Perc = converted_float(salesdetail['TAX3Perc'])
                            TAX3Amount = converted_float(
                                salesdetail['TAX3Amount'])

                            CostPerPrice = table.PriceList.objects.get(
                                CompanyID=CompanyID, PriceListID=PriceListID).PurchasePrice

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

                            if is_inclusive == True:
                                Batch_salesPrice = InclusivePrice
                            else:
                                Batch_salesPrice = UnitPrice

                            product_is_Service = table.Product.objects.get(
                                CompanyID=CompanyID, ProductID=ProductID).is_Service

                            product_purchasePrice = table.PriceList.objects.get(
                                CompanyID=CompanyID, PriceListID=PriceListID).PurchasePrice
                            MultiFactor = table.PriceList.objects.get(
                                CompanyID=CompanyID, PriceListID=PriceListID).MultiFactor

                            qty_batch = converted_float(
                                FreeQty) + converted_float(Qty)
                            Qty_batch = converted_float(
                                MultiFactor) * converted_float(qty_batch)

                            check_AllowUpdateBatchPriceInSales = False
                            if product_is_Service == False:
                                if table.GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="AllowUpdateBatchPriceInSales").exists():
                                    check_AllowUpdateBatchPriceInSales = table.GeneralSettings.objects.get(
                                        CompanyID=CompanyID, BranchID=BranchID, SettingsType="AllowUpdateBatchPriceInSales").SettingsValue

                                if table.GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
                                    check_EnableProductBatchWise = table.GeneralSettings.objects.get(
                                        CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").SettingsValue

                                    if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                                        if table.Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
                                            if check_AllowUpdateBatchPriceInSales == "True" or check_AllowUpdateBatchPriceInSales == True:
                                                batch_ins = table.Batch.objects.get(
                                                    CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode)
                                                StockOut = batch_ins.StockOut
                                                BatchCode = batch_ins.BatchCode
                                                NewStock = converted_float(
                                                    StockOut) + converted_float(Qty_batch)
                                                batch_ins.StockOut = NewStock
                                                batch_ins.SalesPrice = Batch_salesPrice
                                                batch_ins.save()
                                            else:
                                                batch_ins = table.Batch.objects.get(
                                                    CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode)
                                                StockOut = batch_ins.StockOut
                                                BatchCode = batch_ins.BatchCode
                                                NewStock = converted_float(
                                                    StockOut) + converted_float(Qty_batch)
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
                                            NewStock = converted_float(
                                                StockOut) + converted_float(Qty_batch)
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
                                ProductTaxID=ProductTaxID,
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
                                ProductTaxID=ProductTaxID,
                                IsReturn=IsReturn
                            )

                            if table.GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="SalesPriceUpdate").exists():
                                check_SalesPriceUpdate = table.GeneralSettings.objects.get(
                                    CompanyID=CompanyID, SettingsType="SalesPriceUpdate", BranchID=BranchID).SettingsValue
                                if check_SalesPriceUpdate == "True" or check_SalesPriceUpdate == True:
                                    pri_ins = table.PriceList.objects.get(
                                        CompanyID=CompanyID, PriceListID=PriceListID)
                                    pri_ins.SalesPrice = Batch_salesPrice
                                    pri_ins.save()

                            if product_is_Service == False:
                                PriceListID_DefUnit = table.PriceList.objects.get(
                                    CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).PriceListID

                                qty = converted_float(
                                    FreeQty) + converted_float(Qty)

                                Qty = converted_float(
                                    MultiFactor) * converted_float(qty)
                                Cost = converted_float(
                                    CostPerPrice) / converted_float(MultiFactor)

                                princeList_instance = table.PriceList.objects.get(
                                    CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID_DefUnit)
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

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'POS Sales',
                     'Create', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def pos_product_barcode(request):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    PriceRounding = data['PriceRounding']
    Barcode = data['Barcode']
    ProductID = None
    if table.PriceList.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Barcode=Barcode).exists():
        ProductID = table.PriceList.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Barcode=Barcode).first().ProductID
    elif table.PriceList.objects.filter(CompanyID=CompanyID, BranchID=BranchID, AutoBarcode=Barcode).exists():
        ProductID = table.PriceList.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, AutoBarcode=Barcode).first().ProductID
        
    if ProductID:
        instance = table.Product.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).first()
        serialized = POS_Product_Serializer(instance, context={
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


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def list_sales(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    BranchID = data["BranchID"]
    PriceRounding = data["PriceRounding"]
    page_number = data["page_no"]
    items_per_page = data["items_per_page"]
    FromDate = data["FromDate"]
    ToDate = data["ToDate"]
    search_val = data["search_val"]
    length = len(search_val)
    
    try:
        UserID = request.user.id
    except:
        UserID = data["UserID"]

    instances = None
    count = 0
    if table.SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, CreatedUserID=UserID).exists():
        instances = table.SalesMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, CreatedUserID=UserID)

    if FromDate and ToDate:
        instances = instances.filter(Date__gte=FromDate, Date__lte=ToDate)
    if length > 0:
        ledger_ids = []
        if table.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerName__icontains=search_val).exists():
            ledger_ins = table.AccountLedger.objects.filter(
                CompanyID=CompanyID, LedgerName__icontains=search_val
            )
            ledger_ids = ledger_ins.values_list('LedgerID', flat=True)
        condition1 = (Q(CompanyID=CompanyID, BranchID=BranchID))
        condition2 = (Q(VoucherNo__icontains=search_val)
                      | Q(LedgerID__in=ledger_ids))

        instances = instances.filter(condition1 & condition2)
        if length < 3:
            instances = instances.filter()[:10]
    else:
        count = len(instances)
        instances = list_pagination(
            instances, items_per_page, page_number
        )
    if instances:
        sale_serializer = SalesListSerializer(
            instances,
            many=True,
            context={
                "request": request,
                "CompanyID": CompanyID,
                "PriceRounding": PriceRounding,
            },
        )
        data = sale_serializer.data
        if not data == None:
            response_data = {
                "StatusCode": 6000,
                "data": data,
                "count": count,
            }
        else:
            response_data = {"StatusCode": 6001}
    else:
        response_data = {"StatusCode": 6001}
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def list_sales_return(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    BranchID = data["BranchID"]
    PriceRounding = data["PriceRounding"]

    page_number = data["page_no"]
    items_per_page = data["items_per_page"]

    FromDate = data["FromDate"]
    ToDate = data["ToDate"]
    search_val = data["search_val"]
    length = len(search_val)
    
    try:
        UserID = request.user.id
    except:
        UserID = data["UserID"]

    instances = None
    count = 0
    if table.SalesReturnMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID,CreatedUserID=UserID).exists():
        instances = table.SalesReturnMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID,CreatedUserID=UserID)

    if FromDate and ToDate:
        instances = instances.filter(
            VoucherDate__gte=FromDate, VoucherDate__lte=ToDate)
    if length > 0 and instances:
        ledger_ids = []
        if table.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerName__icontains=search_val).exists():
            ledger_ins = table.AccountLedger.objects.filter(
                CompanyID=CompanyID, LedgerName__icontains=search_val
            )
            ledger_ids = ledger_ins.values_list('LedgerID', flat=True)
        condition1 = (Q(CompanyID=CompanyID, BranchID=BranchID))
        condition2 = (Q(VoucherNo__icontains=search_val)
                      | Q(LedgerID__in=ledger_ids))

        instances = instances.filter(condition1 & condition2)
        if length < 3:
            instances = instances.filter()[:10]
    elif instances:
        count = len(instances)
        instances = list_pagination(
            instances, items_per_page, page_number
        )
    if instances:
        sale_serializer = SalesReturnListSerializer(
            instances,
            many=True,
            context={
                "request": request,
                "CompanyID": CompanyID,
                "PriceRounding": PriceRounding,
            },
        )
        data = sale_serializer.data
        if not data == None:
            response_data = {
                "StatusCode": 6000,
                "data": data,
                "count": count,
            }
        else:
            response_data = {"StatusCode": 6001}
    else:
        response_data = {"StatusCode": 6001}
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def list_sales_order(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    BranchID = data["BranchID"]
    PriceRounding = data["PriceRounding"]

    page_number = data["page_no"]
    items_per_page = data["items_per_page"]

    FromDate = data["FromDate"]
    ToDate = data["ToDate"]
    search_val = data["search_val"]
    length = len(search_val)
    
    try:
        UserID = request.user.id
    except:
        UserID = data["UserID"]

    instances = None
    count = 0
    if table.SalesOrderMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID,CreatedUserID=UserID).exists():
        instances = table.SalesOrderMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID,CreatedUserID=UserID)

    if FromDate and ToDate:
        instances = instances.filter(Date__gte=FromDate, Date__lte=ToDate)
    if length > 0:
        ledger_ids = []
        if table.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerName__icontains=search_val).exists():
            ledger_ins = table.AccountLedger.objects.filter(
                CompanyID=CompanyID, LedgerName__icontains=search_val
            )
            ledger_ids = ledger_ins.values_list('LedgerID', flat=True)
        condition1 = (Q(CompanyID=CompanyID, BranchID=BranchID))
        condition2 = (Q(VoucherNo__icontains=search_val)
                      | Q(LedgerID__in=ledger_ids))

        instances = instances.filter(condition1 & condition2)
        if length < 3:
            instances = instances.filter()[:10]
    else:
        count = len(instances)
        instances = list_pagination(
            instances, items_per_page, page_number
        )
    if instances:
        sale_serializer = SalesOrderListSerializer(
            instances,
            many=True,
            context={
                "request": request,
                "CompanyID": CompanyID,
                "PriceRounding": PriceRounding,
            },
        )
        data = sale_serializer.data
        if not data == None:
            response_data = {
                "StatusCode": 6000,
                "data": data,
                "count": count,
            }
        else:
            response_data = {"StatusCode": 6001}
    else:
        response_data = {"StatusCode": 6001}
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def list_payment(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    BranchID = data["BranchID"]
    PriceRounding = data["PriceRounding"]

    page_number = data["page_no"]
    items_per_page = data["items_per_page"]

    FromDate = data["FromDate"]
    ToDate = data["ToDate"]
    search_val = data["search_val"]
    length = len(search_val)
    VoucherType = data["VoucherType"]
    
    try:
        UserID = request.user.id
    except:
        UserID = data["UserID"]

    instances = None
    count = 0
    voucher_search = False
    if table.PaymentMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType,CreatedUserID=UserID).exists():
        instances = table.PaymentMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType,CreatedUserID=UserID)
        if FromDate and ToDate:
            instances = instances.filter(Date__gte=FromDate, Date__lte=ToDate)
        if length > 0 and instances.filter(VoucherNo__icontains=search_val):
            instances = instances.filter(VoucherNo__icontains=search_val)
            voucher_search = True

        payemnt_ids = instances.filter().values_list('PaymentMasterID', flat=True)
        if table.PaymentDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID__in=payemnt_ids).exists():
            details_ins = table.PaymentDetails.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID__in=payemnt_ids)
            if voucher_search == False and length > 0:
                ledger_ids = []
                if table.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerName__icontains=search_val).exists():
                    ledger_ins = table.AccountLedger.objects.filter(
                        CompanyID=CompanyID, LedgerName__icontains=search_val
                    )
                    ledger_ids = ledger_ins.values_list('LedgerID', flat=True)
                details_ins = details_ins.filter(LedgerID__in=ledger_ids)
                if length < 3:
                    details_ins = details_ins.filter()[:10]
            else:
                count = len(details_ins)
                details_ins = list_pagination(
                    details_ins, items_per_page, page_number
                )
            sale_serializer = PaymentListSerializer(
                details_ins,
                many=True,
                context={
                    "request": request,
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                },
            )
            data = sale_serializer.data
            if not data == None:
                response_data = {
                    "StatusCode": 6000,
                    "data": data,
                    "count": count,
                }
            else:
                response_data = {"StatusCode": 6001}
        else:
            response_data = {"StatusCode": 6001}
    else:
        response_data = {"StatusCode": 6001}
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def salesApp_payment(request, pk):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    BranchID = data["BranchID"]
    PriceRounding = data["PriceRounding"]

    instances = None
    count = 0
    voucher_search = False
    if table.PaymentDetails.objects.filter(pk=pk).exists():
        instances = table.PaymentDetails.objects.get(pk=pk)
        payment_serializer = PaymentListSerializer(
            instances,
            context={
                "request": request,
                "CompanyID": CompanyID,
                "PriceRounding": PriceRounding,
            },
        )
        data = payment_serializer.data
        if not data == None:
            response_data = {
                "StatusCode": 6000,
                "data": data,
            }
        else:
            response_data = {"StatusCode": 6001}
    else:
        response_data = {"StatusCode": 6001}
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def salesApp_delete_payment(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    detail_ins = None
    if table.PaymentDetails.objects.filter(pk=pk).exists():
        detail_ins = table.PaymentDetails.objects.get(pk=pk)
    instances = None
    if detail_ins:
        BranchID = detail_ins.BranchID
        PaymentMasterID = detail_ins.PaymentMasterID
        if table.PaymentMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID).exists():
            instance = table.PaymentMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID).first()

    ledgerPostInstances = None

    if instance:
        PaymentMasterID = instance.PaymentMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        VoucherType = instance.VoucherType
        LedgerID = instance.LedgerID
        EmployeeID = instance.EmployeeID
        PaymentNo = instance.PaymentNo
        FinancialYearID = instance.FinancialYearID
        Date = instance.Date
        TotalAmount = instance.TotalAmount
        Notes = instance.Notes
        IsActive = instance.IsActive
        Action = "D"

        table.PaymentMaster_Log.objects.create(
            TransactionID=PaymentMasterID,
            BranchID=BranchID,
            Action=Action,
            VoucherNo=VoucherNo,
            VoucherType=VoucherType,
            LedgerID=LedgerID,
            EmployeeID=EmployeeID,
            PaymentNo=PaymentNo,
            FinancialYearID=FinancialYearID,
            Date=Date,
            TotalAmount=TotalAmount,
            Notes=Notes,
            IsActive=IsActive,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            UpdatedUserID=CreatedUserID,
            CompanyID=CompanyID,
        )

        detail_instances = table.PaymentDetails.objects.filter(
            CompanyID=CompanyID, PaymentMasterID=PaymentMasterID, BranchID=BranchID, VoucherType=VoucherType)

        for detail_instance in detail_instances:

            PaymentDetailsID = detail_instance.PaymentDetailsID
            BranchID = detail_instance.BranchID
            PaymentMasterID = detail_instance.PaymentMasterID
            PaymentGateway = detail_instance.PaymentGateway
            RefferenceNo = detail_instance.RefferenceNo
            CardNetwork = detail_instance.CardNetwork
            PaymentStatus = detail_instance.PaymentStatus
            DueDate = detail_instance.DueDate
            LedgerID = detail_instance.LedgerID
            Amount = detail_instance.Amount
            Balance = detail_instance.Balance
            Discount = detail_instance.Discount
            NetAmount = detail_instance.NetAmount
            Narration = detail_instance.Narration
            CreatedUserID = detail_instance.CreatedUserID
            UpdatedUserID = detail_instance.UpdatedUserID

            table.PaymentDetails_Log.objects.create(
                TransactionID=PaymentDetailsID,
                BranchID=BranchID,
                Action=Action,
                PaymentMasterID=PaymentMasterID,
                PaymentGateway=PaymentGateway,
                RefferenceNo=RefferenceNo,
                CardNetwork=CardNetwork,
                PaymentStatus=PaymentStatus,
                DueDate=DueDate,
                LedgerID=LedgerID,
                Amount=Amount,
                Balance=Balance,
                Discount=Discount,
                NetAmount=NetAmount,
                Narration=Narration,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                UpdatedUserID=UpdatedUserID,
                CompanyID=CompanyID,
                VoucherType=VoucherType
            )

            detail_instance.delete()

        if table.LedgerPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=PaymentMasterID, BranchID=BranchID, VoucherType=VoucherType).exists():
            ledgerPostInstances = table.LedgerPosting.objects.filter(
                CompanyID=CompanyID, VoucherMasterID=PaymentMasterID, BranchID=BranchID, VoucherType=VoucherType)

            update_ledger = UpdateLedgerBalance(
                CompanyID, BranchID, 0, PaymentMasterID, VoucherType, 0, "Cr", "update")
            for ledgerPostInstance in ledgerPostInstances:

                LedgerPostingID = ledgerPostInstance.LedgerPostingID
                VoucherType = ledgerPostInstance.VoucherType
                Debit = ledgerPostInstance.Debit
                Credit = ledgerPostInstance.Credit
                IsActive = ledgerPostInstance.IsActive
                Date = ledgerPostInstance.Date
                LedgerID = ledgerPostInstance.LedgerID
                CreatedUserID = ledgerPostInstance.CreatedUserID
                PaymentDetailsID = ledgerPostInstance.VoucherDetailID

                table.LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PaymentMasterID,
                    VoucherDetailID=PaymentDetailsID,
                    VoucherNo=VoucherNo,
                    VoucherType=VoucherType,
                    LedgerID=LedgerID,
                    Debit=Debit,
                    Credit=Credit,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                ledgerPostInstance.delete()
        
        if table.BillWiseDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PaymentInvoiceNo=VoucherNo, PaymentVoucherType=VoucherType).exists():
            billwise_instances = table.BillWiseDetails.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, PaymentInvoiceNo=VoucherNo, PaymentVoucherType=VoucherType)
            for billwise_instance in billwise_instances:
                Amount = billwise_instance.Payments
                BillwiseMasterID = billwise_instance.BillwiseMasterID
                if table.BillWiseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID).exists():
                    master_inst = table.BillWiseMaster.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID).first()
                    Payments = master_inst.Payments
                    Payments = converted_float(
                        Payments) - converted_float(Amount)
                    master_inst.Payments = Payments
                    master_inst.save()
                billwise_instance.delete()
        
        instance.delete()
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Payment',
                     'Delete', 'Payment Deleted Successfully.', 'Payment Deleted Successfully.')

        response_data = {
            "StatusCode": 6000,
            "message": "Payment Master Deleted Successfully!",
            "title": "Success",
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID,
                     'Payment', 'Delete', 'Payment Deleted Failed.', 'Payment Not Found!')
        response_data = {
            "StatusCode": 6001,
            "message": "Payment Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def create_payment(request):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            BranchID = data['BranchID']
            CreatedUserID = data['CreatedUserID']
            today = datetime.datetime.now()
            VoucherNo = data['VoucherNo']
            Date = data['Date']
            MasterLedgerID = data['MasterLedgerID']
            LedgerID = data['LedgerID']
            Balance = converted_float(data['Balance'])
            Amount = converted_float(data['Amount'])
            Discount = converted_float(data['Discount'])
            NetAmount = converted_float(data['NetAmount'])
            TotalAmount = converted_float(data['TotalAmount'])
            Notes = data['Notes']
            VoucherType = data['VoucherType']
            Action = "A"

            PreFix = data['PreFix']
            Seperator = data['Seperator']
            InvoiceNo = data['InvoiceNo']

            update_voucher_table(
                CompanyID, CreatedUserID, VoucherType, PreFix, Seperator, InvoiceNo)

            PaymentMasterID = payment_masterid(
                table.PaymentMaster, BranchID, CompanyID)
            table.PaymentMaster_Log.objects.create(
                TransactionID=PaymentMasterID,
                BranchID=BranchID,
                Action=Action,
                VoucherNo=VoucherNo,
                VoucherType=VoucherType,
                LedgerID=MasterLedgerID,
                PaymentNo=VoucherNo,
                Date=Date,
                TotalAmount=TotalAmount,
                Notes=Notes,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                UpdatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            instance = table.PaymentMaster.objects.create(
                PaymentMasterID=PaymentMasterID,
                BranchID=BranchID,
                Action=Action,
                VoucherNo=VoucherNo,
                VoucherType=VoucherType,
                LedgerID=MasterLedgerID,
                PaymentNo=VoucherNo,
                Date=Date,
                TotalAmount=TotalAmount,
                Notes=Notes,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                UpdatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            if VoucherType == "CP":
                transactionType = table.TransactionTypes.objects.get(
                    Name="Cash", CompanyID=CompanyID)
                transactionTypeID = transactionType.TransactionTypesID
                PaymentGateway = transactionTypeID

                PaymentDetailsID = payment_detailid(
                    table.PaymentDetails, BranchID, CompanyID)

                log_instance = table.PaymentDetails_Log.objects.create(
                    TransactionID=PaymentDetailsID,
                    BranchID=BranchID,
                    Action=Action,
                    PaymentMasterID=PaymentMasterID,
                    PaymentGateway=PaymentGateway,
                    LedgerID=LedgerID,
                    Amount=Amount,
                    Balance=Balance,
                    Discount=Discount,
                    NetAmount=NetAmount,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    UpdatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                    VoucherType=VoucherType
                )

                detail_ins = table.PaymentDetails.objects.create(
                    PaymentDetailsID=PaymentDetailsID,
                    BranchID=BranchID,
                    Action=Action,
                    # payment_master=instance,
                    PaymentMasterID=PaymentMasterID,
                    PaymentGateway=PaymentGateway,
                    LedgerID=LedgerID,
                    Amount=Amount,
                    Balance=Balance,
                    Discount=Discount,
                    NetAmount=NetAmount,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    UpdatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                    VoucherType=VoucherType,
                    LogID=log_instance.ID
                )
            if VoucherType == "BP":
                transactionType = table.TransactionTypes.objects.filter(
                    Name="None", CompanyID=CompanyID).first()
                transactionTypeID = transactionType.TransactionTypesID
                PaymentGateway = transactionTypeID
                PaymentDetailsID = payment_detailid(
                    table.PaymentDetails, BranchID, CompanyID)

                log_instance = table.PaymentDetails_Log.objects.create(
                    TransactionID=PaymentDetailsID,
                    BranchID=BranchID,
                    Action=Action,
                    PaymentMasterID=PaymentMasterID,
                    PaymentGateway=PaymentGateway,
                    LedgerID=LedgerID,
                    Amount=Amount,
                    Balance=Balance,
                    Discount=Discount,
                    NetAmount=NetAmount,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    UpdatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                    VoucherType=VoucherType
                )

                detail_ins = table.PaymentDetails.objects.create(
                    PaymentDetailsID=PaymentDetailsID,
                    BranchID=BranchID,
                    Action=Action,
                    # payment_master=instance,
                    PaymentMasterID=PaymentMasterID,
                    PaymentGateway=PaymentGateway,
                    LedgerID=LedgerID,
                    Amount=Amount,
                    Balance=Balance,
                    Discount=Discount,
                    NetAmount=NetAmount,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    UpdatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                    VoucherType=VoucherType,
                    LogID=log_instance.ID
                )

            LedgerPostingID = get_auto_LedgerPostid(
                table.LedgerPosting, BranchID, CompanyID)

            table.LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=PaymentMasterID,
                VoucherDetailID=PaymentDetailsID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=LedgerID,
                RelatedLedgerID=MasterLedgerID,
                Debit=NetAmount,
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
                VoucherMasterID=PaymentMasterID,
                VoucherDetailID=PaymentDetailsID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=LedgerID,
                RelatedLedgerID=MasterLedgerID,
                Debit=NetAmount,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )

            update_ledger = UpdateLedgerBalance(
                CompanyID, BranchID, LedgerID, PaymentMasterID, VoucherType, NetAmount, "Dr", "create")

            LedgerPostingID = get_auto_LedgerPostid(
                table.LedgerPosting, BranchID, CompanyID)

            table.LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=PaymentMasterID,
                VoucherDetailID=PaymentDetailsID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=MasterLedgerID,
                RelatedLedgerID=LedgerID,
                Credit=NetAmount,
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
                VoucherMasterID=PaymentMasterID,
                VoucherDetailID=PaymentDetailsID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=MasterLedgerID,
                RelatedLedgerID=LedgerID,
                Credit=NetAmount,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )

            update_ledger = UpdateLedgerBalance(
                CompanyID, BranchID, MasterLedgerID, PaymentMasterID, VoucherType, NetAmount, "Cr", "create")

            if converted_float(Discount) > 0:
                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID)
                # Discount on Payment
                discount_on_payment = get_BranchLedgerId_for_LedgerPosting(
                    BranchID, CompanyID, 'discount_on_payment')

                table.LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PaymentMasterID,
                    VoucherDetailID=PaymentDetailsID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=discount_on_payment,
                    RelatedLedgerID=LedgerID,
                    Credit=Discount,
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
                    VoucherMasterID=PaymentMasterID,
                    VoucherDetailID=PaymentDetailsID,
                    VoucherNo=VoucherNo,
                    VoucherType=VoucherType,
                    LedgerID=discount_on_payment,
                    RelatedLedgerID=LedgerID,
                    Credit=Discount,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, discount_on_payment, PaymentMasterID, VoucherType, Discount, "Cr", "create")

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID)

                table.LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PaymentMasterID,
                    VoucherDetailID=PaymentDetailsID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=discount_on_payment,
                    Debit=Discount,
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
                    VoucherMasterID=PaymentMasterID,
                    VoucherDetailID=PaymentDetailsID,
                    VoucherNo=VoucherNo,
                    VoucherType=VoucherType,
                    LedgerID=LedgerID,
                    RelatedLedgerID=discount_on_payment,
                    Debit=Discount,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, LedgerID, PaymentMasterID, VoucherType, Discount, "Dr", "create")

            try:
                billwiseDetails_datas = data['billwiseDetails_datas']
            except:
                billwiseDetails_datas = []

            if billwiseDetails_datas:
                for b in billwiseDetails_datas:
                    BillwiseMasterID = b["BillwiseMasterID"]
                    Amount = b["Amount"]
                    BillwiseDetailsID = get_BillwiseDetailsID(
                        BranchID, CompanyID)
                    if table.BillWiseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID).exists():
                        bill_master_instance = table.BillWiseMaster.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID).first()
                        master_payment = bill_master_instance.Payments
                        bill_master_instance.Payments = converted_float(
                            master_payment) + converted_float(Amount)
                        bill_master_instance.save()

                        table.BillWiseDetails.objects.create(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            BillwiseDetailsID=BillwiseDetailsID,
                            BillwiseMasterID=BillwiseMasterID,
                            InvoiceNo=bill_master_instance.InvoiceNo,
                            VoucherType=bill_master_instance.VoucherType,
                            PaymentDate=Date,
                            Payments=Amount,
                            PaymentVoucherType=VoucherType,
                            PaymentInvoiceNo=VoucherNo
                        )
            
            response_data = {
                "StatusCode": 6000,
                "message": "Payment created Successfully!!!",
                "id": instance.id,
                "detail_unq": detail_ins.id,

            }

            return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        VoucherType = request.data['VoucherType']
        payment_type = "Payments" + str(VoucherType)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again",
            "err_descrb": err_descrb
        }

        activity_id = activity_log(request._request, CompanyID, 'Error', CreatedUserID, payment_type,
                                   'Create', str(e), err_descrb)
        body_params = str(request.data)
        table.Activity_Log.objects.filter(
            id=activity_id).update(body_params=body_params)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def salesApp_edit_payment(request, pk):
    try:
        with transaction.atomic():
            today = datetime.datetime.now()
            data = request.data
            CompanyID = data['CompanyID']
            BranchID = data['BranchID']
            CreatedUserID = data['CreatedUserID']
            detail_instance = table.PaymentDetails.objects.get(pk=pk)
            PaymentMasterID = detail_instance.PaymentMasterID
            instance = table.PaymentMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID).first()
            CompanyID = get_company(CompanyID)
            VoucherNo = instance.VoucherNo
            Date = data['Date']
            MasterLedgerID = data['MasterLedgerID']
            LedgerID = data['LedgerID']
            Balance = converted_float(data['Balance'])
            Amount = converted_float(data['Amount'])
            Discount = converted_float(data['Discount'])
            NetAmount = converted_float(data['NetAmount'])
            TotalAmount = converted_float(data['TotalAmount'])
            Notes = data['Notes']
            VoucherType = data['VoucherType']
            Action = "M"

            table.PaymentMaster_Log.objects.create(
                TransactionID=PaymentMasterID,
                BranchID=BranchID,
                Action=Action,
                VoucherNo=VoucherNo,
                VoucherType=VoucherType,
                LedgerID=MasterLedgerID,
                PaymentNo=VoucherNo,
                Date=Date,
                TotalAmount=TotalAmount,
                Notes=Notes,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                UpdatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            update_ledger = UpdateLedgerBalance(
                CompanyID, BranchID, 0, PaymentMasterID, VoucherType, 0, "Cr", "update")

            if table.LedgerPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=PaymentMasterID, BranchID=BranchID, VoucherType=VoucherType).exists():
                ledgerPostInstances = table.LedgerPosting.objects.filter(
                    CompanyID=CompanyID, VoucherMasterID=PaymentMasterID, BranchID=BranchID, VoucherType=VoucherType).delete()

            instance.VoucherType = VoucherType
            instance.LedgerID = MasterLedgerID
            instance.Date = Date
            instance.TotalAmount = TotalAmount
            instance.Notes = Notes
            instance.UpdatedDate = today
            instance.UpdatedUserID = CreatedUserID
            instance.Action = Action
            instance.save()
            payment_details = table.PaymentDetails.objects.filter(
                CompanyID=CompanyID, PaymentMasterID=PaymentMasterID, BranchID=BranchID).first()
            if VoucherType == "CP":
                transactionType = table.TransactionTypes.objects.get(
                    Name="Cash", CompanyID=CompanyID)
            else:
                transactionType = table.TransactionTypes.objects.filter(
                    Name="None", CompanyID=CompanyID).first()
            transactionTypeID = transactionType.TransactionTypesID
            PaymentGateway = transactionTypeID

            PaymentDetailsID = payment_details.PaymentDetailsID

            log_instance = table.PaymentDetails_Log.objects.create(
                TransactionID=PaymentDetailsID,
                BranchID=BranchID,
                Action=Action,
                PaymentMasterID=PaymentMasterID,
                PaymentGateway=PaymentGateway,
                LedgerID=LedgerID,
                Amount=Amount,
                Balance=Balance,
                Discount=Discount,
                NetAmount=NetAmount,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                UpdatedUserID=CreatedUserID,
                CompanyID=CompanyID,
                VoucherType=VoucherType
            )

            payment_details.Action = Action
            payment_details.PaymentGateway = PaymentGateway
            payment_details.LedgerID = LedgerID
            payment_details.Amount = Amount
            payment_details.Balance = Balance
            payment_details.Discount = Discount
            payment_details.NetAmount = NetAmount
            payment_details.UpdatedDate = today
            payment_details.UpdatedUserID = CreatedUserID
            payment_details.VoucherType = VoucherType
            payment_details.LogID = log_instance.ID
            payment_details.save()

            LedgerPostingID = get_auto_LedgerPostid(
                table.LedgerPosting, BranchID, CompanyID)

            table.LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=PaymentMasterID,
                VoucherDetailID=PaymentDetailsID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=LedgerID,
                RelatedLedgerID=MasterLedgerID,
                Debit=NetAmount,
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
                VoucherMasterID=PaymentMasterID,
                VoucherDetailID=PaymentDetailsID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=LedgerID,
                RelatedLedgerID=MasterLedgerID,
                Debit=NetAmount,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )

            update_ledger = UpdateLedgerBalance(
                CompanyID, BranchID, LedgerID, PaymentMasterID, VoucherType, NetAmount, "Dr", "create")

            LedgerPostingID = get_auto_LedgerPostid(
                table.LedgerPosting, BranchID, CompanyID)

            table.LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=PaymentMasterID,
                VoucherDetailID=PaymentDetailsID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=MasterLedgerID,
                RelatedLedgerID=LedgerID,
                Credit=NetAmount,
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
                VoucherMasterID=PaymentMasterID,
                VoucherDetailID=PaymentDetailsID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=MasterLedgerID,
                RelatedLedgerID=LedgerID,
                Credit=NetAmount,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )

            update_ledger = UpdateLedgerBalance(
                CompanyID, BranchID, MasterLedgerID, PaymentMasterID, VoucherType, NetAmount, "Cr", "create")

            if converted_float(Discount) > 0:
                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID)
                # Discount on Payment
                discount_on_payment = get_BranchLedgerId_for_LedgerPosting(
                    BranchID, CompanyID, 'discount_on_payment')

                table.LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PaymentMasterID,
                    VoucherDetailID=PaymentDetailsID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=discount_on_payment,
                    RelatedLedgerID=LedgerID,
                    Credit=Discount,
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
                    VoucherMasterID=PaymentMasterID,
                    VoucherDetailID=PaymentDetailsID,
                    VoucherNo=VoucherNo,
                    VoucherType=VoucherType,
                    LedgerID=discount_on_payment,
                    RelatedLedgerID=LedgerID,
                    Credit=Discount,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, discount_on_payment, PaymentMasterID, VoucherType, Discount, "Cr", "create")

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID)

                table.LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PaymentMasterID,
                    VoucherDetailID=PaymentDetailsID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=discount_on_payment,
                    Debit=Discount,
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
                    VoucherMasterID=PaymentMasterID,
                    VoucherDetailID=PaymentDetailsID,
                    VoucherNo=VoucherNo,
                    VoucherType=VoucherType,
                    LedgerID=LedgerID,
                    RelatedLedgerID=discount_on_payment,
                    Debit=Discount,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, LedgerID, PaymentMasterID, VoucherType, Discount, "Dr", "create")

            try:
                billwiseDetails_datas = data['billwiseDetails_datas']
            except:
                billwiseDetails_datas = []

            if billwiseDetails_datas:
                for b in billwiseDetails_datas:
                    BillwiseMasterID = b["BillwiseMasterID"]
                    Amount = b["Amount"]

                    if table.BillWiseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID).exists():
                        bill_master_instance = table.BillWiseMaster.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID).first()
                        if table.BillWiseDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID, PaymentInvoiceNo=VoucherNo, PaymentVoucherType=VoucherType).exists():
                            bill_details_instance = table.BillWiseDetails.objects.filter(
                                CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID, PaymentInvoiceNo=VoucherNo, PaymentVoucherType=VoucherType).first()
                            bill_master_instance.Payments = converted_float(
                                bill_master_instance.Payments) + converted_float(Amount)
                            bill_details_instance.InvoiceNo = bill_master_instance.InvoiceNo
                            bill_details_instance.PaymentDate = Date
                            bill_details_instance.Payments = Amount
                            bill_details_instance.save()
                        else:
                            BillwiseDetailsID = get_BillwiseDetailsID(
                                BranchID, CompanyID)
                            table.BillWiseDetails.objects.create(
                                CompanyID=CompanyID,
                                BranchID=BranchID,
                                BillwiseDetailsID=BillwiseDetailsID,
                                BillwiseMasterID=BillwiseMasterID,
                                InvoiceNo=bill_master_instance.InvoiceNo,
                                VoucherType=bill_master_instance.VoucherType,
                                PaymentDate=Date,
                                Payments=Amount,
                                PaymentVoucherType=VoucherType,
                                PaymentInvoiceNo=VoucherNo
                            )

                        all_details = table.BillWiseDetails.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID)
                        payment_sum = all_details.aggregate(Sum("Payments"))
                        payment_sum = payment_sum["Payments__sum"]
                        bill_master_instance.Payments = converted_float(
                            payment_sum)
                        # bill_master_instance.Payments = converted_float(
                        #     bill_master_instance.Payments) + converted_float(Amount)
                        bill_master_instance.save()
            
            response_data = {
                "StatusCode": 6000,
                "message": "Payment created Successfully!!!",
                "id": instance.id,
                "detail_unq": payment_details.id,
            }

            return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        VoucherType = request.data['VoucherType']
        payment_type = "Payments" + str(VoucherType)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again",
            "err_descrb": err_descrb
        }

        activity_id = activity_log(request._request, CompanyID, 'Error', CreatedUserID, payment_type,
                                   'Create', str(e), err_descrb)
        body_params = str(request.data)
        table.Activity_Log.objects.filter(
            id=activity_id).update(body_params=body_params)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def list_receipt(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    BranchID = data["BranchID"]
    PriceRounding = data["PriceRounding"]

    page_number = data["page_no"]
    items_per_page = data["items_per_page"]

    FromDate = data["FromDate"]
    ToDate = data["ToDate"]
    search_val = data["search_val"]
    length = len(search_val)
    VoucherType = data["VoucherType"]
    
    try:
        UserID = request.user.id
    except:
        UserID = data["UserID"]

    instances = None
    count = 0
    voucher_search = False
    if table.ReceiptMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType,CreatedUserID=UserID).exists():
        instances = table.ReceiptMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType,CreatedUserID=UserID)
        if FromDate and ToDate:
            instances = instances.filter(Date__gte=FromDate, Date__lte=ToDate)
        if length > 0 and instances.filter(VoucherNo__icontains=search_val):
            instances = instances.filter(VoucherNo__icontains=search_val)
            voucher_search = True

        receipt_ids = instances.filter().values_list('ReceiptMasterID', flat=True)
        if table.ReceiptDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ReceiptMasterID__in=receipt_ids).exists():
            details_ins = table.ReceiptDetails.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ReceiptMasterID__in=receipt_ids)
            if voucher_search == False and length > 0:
                ledger_ids = []
                if table.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerName__icontains=search_val).exists():
                    ledger_ins = table.AccountLedger.objects.filter(
                        CompanyID=CompanyID, LedgerName__icontains=search_val
                    )
                    ledger_ids = ledger_ins.values_list('LedgerID', flat=True)
                details_ins = details_ins.filter(LedgerID__in=ledger_ids)
                if length < 3:
                    details_ins = details_ins.filter()[:10]
            else:
                count = len(details_ins)
                details_ins = list_pagination(
                    details_ins, items_per_page, page_number
                )
            sale_serializer = ReceiptListSerializer(
                details_ins,
                many=True,
                context={
                    "request": request,
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                },
            )
            data = sale_serializer.data
            if not data == None:
                response_data = {
                    "StatusCode": 6000,
                    "data": data,
                    "count": count,
                }
            else:
                response_data = {"StatusCode": 6001}
        else:
            response_data = {"StatusCode": 6001}
    else:
        response_data = {"StatusCode": 6001}
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def create_receipt(request):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            BranchID = data['BranchID']
            CreatedUserID = data['CreatedUserID']
            today = datetime.datetime.now()
            VoucherNo = data['VoucherNo']
            Date = data['Date']
            MasterLedgerID = data['MasterLedgerID']
            LedgerID = data['LedgerID']
            Balance = converted_float(data['Balance'])
            Amount = converted_float(data['Amount'])
            Discount = converted_float(data['Discount'])
            NetAmount = converted_float(data['NetAmount'])
            TotalAmount = converted_float(data['TotalAmount'])
            Notes = data['Notes']
            VoucherType = data['VoucherType']
            Action = "A"

            PreFix = data['PreFix']
            Seperator = data['Seperator']
            InvoiceNo = data['InvoiceNo']

            update_voucher_table(
                CompanyID, CreatedUserID, VoucherType, PreFix, Seperator, InvoiceNo)
            ReceiptMasterID = receipt_masterid(
                table.ReceiptMaster, BranchID, CompanyID)
            ReceiptNo = str(VoucherType) + str(VoucherNo)
            table.ReceiptMaster_Log.objects.create(
                TransactionID=ReceiptMasterID,
                BranchID=BranchID,
                Action=Action,
                VoucherNo=VoucherNo,
                VoucherType=VoucherType,
                ReceiptNo=ReceiptNo,
                LedgerID=MasterLedgerID,
                Date=Date,
                TotalAmount=TotalAmount,
                Notes=Notes,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                UpdatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            instance = table.ReceiptMaster.objects.create(
                ReceiptMasterID=ReceiptMasterID,
                BranchID=BranchID,
                Action=Action,
                VoucherNo=VoucherNo,
                VoucherType=VoucherType,
                ReceiptNo=ReceiptNo,
                LedgerID=MasterLedgerID,
                Date=Date,
                TotalAmount=TotalAmount,
                Notes=Notes,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                UpdatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            transactionType = table.TransactionTypes.objects.get(
                CompanyID=CompanyID, Name="Cash")
            transactionTypeID = transactionType.TransactionTypesID
            PaymentGateway = transactionTypeID
            if VoucherType == "CR":

                ReceiptDetailID = receipt_detailid(
                    table.ReceiptDetails, BranchID, CompanyID)

                log_instance = table.ReceiptDetails_Log.objects.create(
                    TransactionID=ReceiptDetailID,
                    BranchID=BranchID,
                    Action=Action,
                    ReceiptMasterID=ReceiptMasterID,
                    VoucherType=VoucherType,
                    PaymentGateway=PaymentGateway,
                    LedgerID=LedgerID,
                    Amount=Amount,
                    Discount=Discount,
                    NetAmount=NetAmount,
                    Balance=Balance,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    UpdatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                )

                detail_ins = table.ReceiptDetails.objects.create(
                    ReceiptDetailID=ReceiptDetailID,
                    BranchID=BranchID,
                    Action=Action,
                    # receipt_master=instance,
                    ReceiptMasterID=ReceiptMasterID,
                    VoucherType=VoucherType,
                    PaymentGateway=PaymentGateway,
                    LedgerID=LedgerID,
                    Amount=Amount,
                    Discount=Discount,
                    NetAmount=NetAmount,
                    Balance=Balance,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    UpdatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                    LogID=log_instance.ID
                )

            if VoucherType == "BR":
                ReceiptDetailID = receipt_detailid(
                    table.ReceiptDetails, BranchID, CompanyID)
                log_instance = table.ReceiptDetails_Log.objects.create(
                    TransactionID=ReceiptDetailID,
                    BranchID=BranchID,
                    Action=Action,
                    ReceiptMasterID=ReceiptMasterID,
                    VoucherType=VoucherType,
                    PaymentGateway=PaymentGateway,
                    LedgerID=LedgerID,
                    Amount=Amount,
                    Discount=Discount,
                    NetAmount=NetAmount,
                    Balance=Balance,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    UpdatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                )

                detail_ins = table.ReceiptDetails.objects.create(
                    # receipt_master=instance,
                    ReceiptDetailID=ReceiptDetailID,
                    BranchID=BranchID,
                    Action=Action,
                    ReceiptMasterID=ReceiptMasterID,
                    VoucherType=VoucherType,
                    PaymentGateway=PaymentGateway,
                    LedgerID=LedgerID,
                    Amount=Amount,
                    Discount=Discount,
                    NetAmount=NetAmount,
                    Balance=Balance,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    UpdatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                    LogID=log_instance.ID
                )

            LedgerPostingID = get_auto_LedgerPostid(
                table.LedgerPosting, BranchID, CompanyID)

            table.LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=ReceiptMasterID,
                VoucherDetailID=ReceiptDetailID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=LedgerID,
                RelatedLedgerID=MasterLedgerID,
                Credit=NetAmount,
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
                VoucherMasterID=ReceiptMasterID,
                VoucherDetailID=ReceiptDetailID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=LedgerID,
                RelatedLedgerID=MasterLedgerID,
                Credit=NetAmount,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )

            update_ledger = UpdateLedgerBalance(
                CompanyID, BranchID, LedgerID, ReceiptMasterID, VoucherType, NetAmount, "Cr", "create")

            LedgerPostingID = get_auto_LedgerPostid(
                table.LedgerPosting, BranchID, CompanyID)

            table.LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=ReceiptMasterID,
                VoucherDetailID=ReceiptDetailID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=MasterLedgerID,
                RelatedLedgerID=LedgerID,
                Debit=NetAmount,
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
                VoucherMasterID=ReceiptMasterID,
                VoucherDetailID=ReceiptDetailID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=MasterLedgerID,
                RelatedLedgerID=LedgerID,
                Debit=NetAmount,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )

            update_ledger = UpdateLedgerBalance(
                CompanyID, BranchID, MasterLedgerID, ReceiptMasterID, VoucherType, NetAmount, "Dr", "create")

            if converted_float(Discount) > 0:
                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID)
                # Discount on Receipt
                discount_on_receipt = get_BranchLedgerId_for_LedgerPosting(
                    BranchID, CompanyID, 'discount_on_receipt')

                table.LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ReceiptMasterID,
                    VoucherDetailID=ReceiptDetailID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=discount_on_receipt,
                    RelatedLedgerID=LedgerID,
                    Debit=Discount,
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
                    VoucherMasterID=ReceiptMasterID,
                    VoucherDetailID=ReceiptDetailID,
                    VoucherNo=VoucherNo,
                    VoucherType=VoucherType,
                    LedgerID=discount_on_receipt,
                    RelatedLedgerID=LedgerID,
                    Debit=Discount,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, discount_on_receipt, ReceiptMasterID, VoucherType, Discount, "Dr", "create")

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID)

                table.LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ReceiptMasterID,
                    VoucherDetailID=ReceiptDetailID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=discount_on_receipt,
                    Credit=Discount,
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
                    VoucherMasterID=ReceiptMasterID,
                    VoucherDetailID=ReceiptDetailID,
                    VoucherNo=VoucherNo,
                    VoucherType=VoucherType,
                    LedgerID=LedgerID,
                    RelatedLedgerID=discount_on_receipt,
                    Credit=Discount,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, LedgerID, ReceiptMasterID, VoucherType, Discount, "Cr", "create")

            try:
                billwiseDetails_datas = data['billwiseDetails_datas']
            except:
                billwiseDetails_datas = []

            if billwiseDetails_datas:
                for b in billwiseDetails_datas:
                    BillwiseMasterID = b["BillwiseMasterID"]
                    Amount = b["Amount"]
                    BillwiseDetailsID = get_BillwiseDetailsID(
                        BranchID, CompanyID)
                    if table.BillWiseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID).exists():
                        bill_master_instance = table.BillWiseMaster.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID).first()
                        master_payment = bill_master_instance.Payments
                        bill_master_instance.Payments = converted_float(
                            master_payment) + converted_float(Amount)
                        bill_master_instance.save()

                        table.BillWiseDetails.objects.create(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            BillwiseDetailsID=BillwiseDetailsID,
                            BillwiseMasterID=BillwiseMasterID,
                            InvoiceNo=bill_master_instance.InvoiceNo,
                            VoucherType=bill_master_instance.VoucherType,
                            PaymentDate=Date,
                            Payments=Amount,
                            PaymentVoucherType=VoucherType,
                            PaymentInvoiceNo=VoucherNo
                        )
            
            response_data = {
                "StatusCode": 6000,
                "message": "Receipt created Successfully!!!",
                "id": instance.id,
                "detail_unq": detail_ins.id,
            }

            return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        VoucherType = request.data['VoucherType']
        payment_type = "Receipts" + str(VoucherType)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again",
            "err_descrb": err_descrb
        }

        activity_id = activity_log(request._request, CompanyID, 'Error', CreatedUserID, payment_type,
                                   'Create', str(e), err_descrb)
        body_params = str(request.data)
        table.Activity_Log.objects.filter(
            id=activity_id).update(body_params=body_params)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def salesApp_receipt(request, pk):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    BranchID = data["BranchID"]
    PriceRounding = data["PriceRounding"]

    instances = None
    count = 0
    voucher_search = False
    if table.ReceiptDetails.objects.filter(pk=pk).exists():
        instances = table.ReceiptDetails.objects.get(pk=pk)
        receipt_serializer = ReceiptListSerializer(
            instances,
            context={
                "request": request,
                "CompanyID": CompanyID,
                "PriceRounding": PriceRounding,
            },
        )
        data = receipt_serializer.data
        if not data == None:
            response_data = {
                "StatusCode": 6000,
                "data": data,
            }
        else:
            response_data = {"StatusCode": 6001}
    else:
        response_data = {"StatusCode": 6001}
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def salesApp_edit_receipt(request, pk):
    try:
        with transaction.atomic():
            today = datetime.datetime.now()
            data = request.data
            CompanyID = data['CompanyID']
            BranchID = data['BranchID']
            CreatedUserID = data['CreatedUserID']
            detail_instance = table.ReceiptDetails.objects.get(pk=pk)
            ReceiptMasterID = detail_instance.ReceiptMasterID
            instance = table.ReceiptMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ReceiptMasterID=ReceiptMasterID).first()
            CompanyID = get_company(CompanyID)
            VoucherNo = instance.VoucherNo
            Date = data['Date']
            MasterLedgerID = data['MasterLedgerID']
            LedgerID = data['LedgerID']
            Balance = converted_float(data['Balance'])
            Amount = converted_float(data['Amount'])
            Discount = converted_float(data['Discount'])
            NetAmount = converted_float(data['NetAmount'])
            TotalAmount = converted_float(data['TotalAmount'])
            Notes = data['Notes']
            VoucherType = data['VoucherType']
            Action = "M"

            table.ReceiptMaster_Log.objects.create(
                TransactionID=ReceiptMasterID,
                BranchID=BranchID,
                Action=Action,
                VoucherNo=VoucherNo,
                VoucherType=VoucherType,
                LedgerID=MasterLedgerID,
                ReceiptNo=VoucherNo,
                Date=Date,
                TotalAmount=TotalAmount,
                Notes=Notes,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                UpdatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            update_ledger = UpdateLedgerBalance(
                CompanyID, BranchID, 0, ReceiptMasterID, VoucherType, 0, "Cr", "update")

            if table.LedgerPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=ReceiptMasterID, BranchID=BranchID, VoucherType=VoucherType).exists():
                ledgerPostInstances = table.LedgerPosting.objects.filter(
                    CompanyID=CompanyID, VoucherMasterID=ReceiptMasterID, BranchID=BranchID, VoucherType=VoucherType).delete()

            instance.VoucherType = VoucherType
            instance.LedgerID = MasterLedgerID
            instance.Date = Date
            instance.TotalAmount = TotalAmount
            instance.Notes = Notes
            instance.UpdatedDate = today
            instance.UpdatedUserID = CreatedUserID
            instance.Action = Action
            instance.save()
            receipt_details = table.ReceiptDetails.objects.filter(
                CompanyID=CompanyID, ReceiptMasterID=ReceiptMasterID, BranchID=BranchID).first()
            if VoucherType == "CP":
                transactionType = table.TransactionTypes.objects.get(
                    Name="Cash", CompanyID=CompanyID)
            else:
                transactionType = table.TransactionTypes.objects.filter(
                    Name="None", CompanyID=CompanyID).first()
            transactionTypeID = transactionType.TransactionTypesID
            PaymentGateway = transactionTypeID

            ReceiptDetailsID = receipt_details.ReceiptDetailID

            log_instance = table.ReceiptDetails_Log.objects.create(
                TransactionID=ReceiptDetailsID,
                BranchID=BranchID,
                Action=Action,
                ReceiptMasterID=ReceiptMasterID,
                PaymentGateway=PaymentGateway,
                LedgerID=LedgerID,
                Amount=Amount,
                Balance=Balance,
                Discount=Discount,
                NetAmount=NetAmount,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                UpdatedUserID=CreatedUserID,
                CompanyID=CompanyID,
                VoucherType=VoucherType
            )

            receipt_details.Action = Action
            receipt_details.PaymentGateway = PaymentGateway
            receipt_details.LedgerID = LedgerID
            receipt_details.Amount = Amount
            receipt_details.Balance = Balance
            receipt_details.Discount = Discount
            receipt_details.NetAmount = NetAmount
            receipt_details.UpdatedDate = today
            receipt_details.UpdatedUserID = CreatedUserID
            receipt_details.VoucherType = VoucherType
            receipt_details.LogID = log_instance.ID
            receipt_details.save()

            LedgerPostingID = get_auto_LedgerPostid(
                table.LedgerPosting, BranchID, CompanyID)

            table.LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=ReceiptMasterID,
                VoucherDetailID=ReceiptDetailsID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=LedgerID,
                RelatedLedgerID=MasterLedgerID,
                Debit=NetAmount,
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
                VoucherMasterID=ReceiptMasterID,
                VoucherDetailID=ReceiptDetailsID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=LedgerID,
                RelatedLedgerID=MasterLedgerID,
                Debit=NetAmount,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )

            update_ledger = UpdateLedgerBalance(
                CompanyID, BranchID, LedgerID, ReceiptMasterID, VoucherType, NetAmount, "Dr", "create")

            LedgerPostingID = get_auto_LedgerPostid(
                table.LedgerPosting, BranchID, CompanyID)

            table.LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=ReceiptMasterID,
                VoucherDetailID=ReceiptDetailsID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=MasterLedgerID,
                RelatedLedgerID=LedgerID,
                Credit=NetAmount,
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
                VoucherMasterID=ReceiptMasterID,
                VoucherDetailID=ReceiptDetailsID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=MasterLedgerID,
                RelatedLedgerID=LedgerID,
                Credit=NetAmount,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )

            update_ledger = UpdateLedgerBalance(
                CompanyID, BranchID, MasterLedgerID, ReceiptMasterID, VoucherType, NetAmount, "Cr", "create")

            if converted_float(Discount) > 0:
                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID)
                # Discount on Payment
                discount_on_receipt = get_BranchLedgerId_for_LedgerPosting(
                    BranchID, CompanyID, 'discount_on_receipt')

                table.LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ReceiptMasterID,
                    VoucherDetailID=ReceiptDetailsID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=discount_on_receipt,
                    RelatedLedgerID=LedgerID,
                    Credit=Discount,
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
                    VoucherMasterID=ReceiptMasterID,
                    VoucherDetailID=ReceiptDetailsID,
                    VoucherNo=VoucherNo,
                    VoucherType=VoucherType,
                    LedgerID=discount_on_receipt,
                    RelatedLedgerID=LedgerID,
                    Credit=Discount,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, discount_on_receipt, ReceiptMasterID, VoucherType, Discount, "Cr", "create")

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID)

                table.LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ReceiptMasterID,
                    VoucherDetailID=ReceiptDetailsID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=discount_on_receipt,
                    Debit=Discount,
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
                    VoucherMasterID=ReceiptMasterID,
                    VoucherDetailID=ReceiptDetailsID,
                    VoucherNo=VoucherNo,
                    VoucherType=VoucherType,
                    LedgerID=LedgerID,
                    RelatedLedgerID=discount_on_receipt,
                    Debit=Discount,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, LedgerID, ReceiptMasterID, VoucherType, Discount, "Dr", "create")

            try:
                billwiseDetails_datas = data['billwiseDetails_datas']
            except:
                billwiseDetails_datas = []

            if billwiseDetails_datas:
                for b in billwiseDetails_datas:
                    BillwiseMasterID = b["BillwiseMasterID"]
                    Amount = b["Amount"]

                    if table.BillWiseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID).exists():
                        bill_master_instance = table.BillWiseMaster.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID).first()
                        if table.BillWiseDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID, PaymentInvoiceNo=VoucherNo, PaymentVoucherType=VoucherType).exists():
                            bill_details_instance = table.BillWiseDetails.objects.filter(
                                CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID, PaymentInvoiceNo=VoucherNo, PaymentVoucherType=VoucherType).first()
                            bill_master_instance.Payments = converted_float(
                                bill_master_instance.Payments) + converted_float(Amount)
                            bill_details_instance.InvoiceNo = bill_master_instance.InvoiceNo
                            bill_details_instance.PaymentDate = Date
                            bill_details_instance.Payments = Amount
                            bill_details_instance.save()
                        else:
                            BillwiseDetailsID = get_BillwiseDetailsID(
                                BranchID, CompanyID)
                            table.BillWiseDetails.objects.create(
                                CompanyID=CompanyID,
                                BranchID=BranchID,
                                BillwiseDetailsID=BillwiseDetailsID,
                                BillwiseMasterID=BillwiseMasterID,
                                InvoiceNo=bill_master_instance.InvoiceNo,
                                VoucherType=bill_master_instance.VoucherType,
                                PaymentDate=Date,
                                Payments=Amount,
                                PaymentVoucherType=VoucherType,
                                PaymentInvoiceNo=VoucherNo
                            )

                        all_details = table.BillWiseDetails.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID)
                        payment_sum = all_details.aggregate(Sum("Payments"))
                        payment_sum = payment_sum["Payments__sum"]
                        bill_master_instance.Payments = converted_float(
                            payment_sum)
                        # bill_master_instance.Payments = converted_float(
                        #     bill_master_instance.Payments) + converted_float(Amount)
                        bill_master_instance.save()
            
            response_data = {
                "StatusCode": 6000,
                "message": "Payment updated Successfully!!!",
                "id": instance.id,
                "detail_unq": receipt_details.id,
            }

            return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        VoucherType = request.data['VoucherType']
        payment_type = "Receipts" + str(VoucherType)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again",
            "err_descrb": err_descrb
        }

        activity_id = activity_log(request._request, CompanyID, 'Error', CreatedUserID, payment_type,
                                   'Create', str(e), err_descrb)
        body_params = str(request.data)
        table.Activity_Log.objects.filter(
            id=activity_id).update(body_params=body_params)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def salesApp_delete_receipt(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    detail_ins = None
    if table.ReceiptDetails.objects.filter(pk=pk).exists():
        detail_ins = table.ReceiptDetails.objects.get(pk=pk)
    instances = None
    if detail_ins:
        BranchID = detail_ins.BranchID
        ReceiptMasterID = detail_ins.ReceiptMasterID
        if table.ReceiptMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ReceiptMasterID=ReceiptMasterID).exists():
            instance = table.ReceiptMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ReceiptMasterID=ReceiptMasterID).first()

    ledgerPostInstances = None

    if instance and detail_ins:
        ReceiptMasterID = instance.ReceiptMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        VoucherType = instance.VoucherType
        LedgerID = instance.LedgerID
        EmployeeID = instance.EmployeeID
        ReceiptNo = instance.ReceiptNo
        FinancialYearID = instance.FinancialYearID
        Date = instance.Date
        TotalAmount = instance.TotalAmount
        Notes = instance.Notes
        IsActive = instance.IsActive
        Action = "D"

        table.ReceiptMaster_Log.objects.create(
            TransactionID=ReceiptMasterID,
            BranchID=BranchID,
            Action=Action,
            VoucherNo=VoucherNo,
            VoucherType=VoucherType,
            LedgerID=LedgerID,
            EmployeeID=EmployeeID,
            ReceiptNo=ReceiptNo,
            FinancialYearID=FinancialYearID,
            Date=Date,
            TotalAmount=TotalAmount,
            Notes=Notes,
            IsActive=IsActive,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            UpdatedUserID=CreatedUserID,
            CompanyID=CompanyID,
        )

        ReceiptDetailsID = detail_ins.ReceiptDetailID
        BranchID = detail_ins.BranchID
        ReceiptMasterID = detail_ins.ReceiptMasterID
        PaymentGateway = detail_ins.PaymentGateway
        RefferenceNo = detail_ins.RefferenceNo
        CardNetwork = detail_ins.CardNetwork
        PaymentStatus = detail_ins.PaymentStatus
        DueDate = detail_ins.DueDate
        LedgerID = detail_ins.LedgerID
        Amount = detail_ins.Amount
        Balance = detail_ins.Balance
        Discount = detail_ins.Discount
        NetAmount = detail_ins.NetAmount
        Narration = detail_ins.Narration
        CreatedUserID = detail_ins.CreatedUserID
        UpdatedUserID = detail_ins.UpdatedUserID

        table.ReceiptDetails_Log.objects.create(
            TransactionID=ReceiptDetailsID,
            BranchID=BranchID,
            Action=Action,
            ReceiptMasterID=ReceiptMasterID,
            PaymentGateway=PaymentGateway,
            RefferenceNo=RefferenceNo,
            CardNetwork=CardNetwork,
            PaymentStatus=PaymentStatus,
            DueDate=DueDate,
            LedgerID=LedgerID,
            Amount=Amount,
            Balance=Balance,
            Discount=Discount,
            NetAmount=NetAmount,
            Narration=Narration,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            UpdatedUserID=UpdatedUserID,
            CompanyID=CompanyID,
            VoucherType=VoucherType
        )

        detail_ins.delete()

        if table.LedgerPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=ReceiptMasterID, BranchID=BranchID, VoucherType=VoucherType).exists():
            ledgerPostInstances = table.LedgerPosting.objects.filter(
                CompanyID=CompanyID, VoucherMasterID=ReceiptMasterID, BranchID=BranchID, VoucherType=VoucherType)

            update_ledger = UpdateLedgerBalance(
                CompanyID, BranchID, 0, ReceiptMasterID, VoucherType, 0, "Cr", "update")
            for ledgerPostInstance in ledgerPostInstances:

                LedgerPostingID = ledgerPostInstance.LedgerPostingID
                VoucherType = ledgerPostInstance.VoucherType
                Debit = ledgerPostInstance.Debit
                Credit = ledgerPostInstance.Credit
                IsActive = ledgerPostInstance.IsActive
                Date = ledgerPostInstance.Date
                LedgerID = ledgerPostInstance.LedgerID
                CreatedUserID = ledgerPostInstance.CreatedUserID
                ReceiptDetailsID = ledgerPostInstance.VoucherDetailID

                table.LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ReceiptMasterID,
                    VoucherDetailID=ReceiptDetailsID,
                    VoucherNo=VoucherNo,
                    VoucherType=VoucherType,
                    LedgerID=LedgerID,
                    Debit=Debit,
                    Credit=Credit,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                ledgerPostInstance.delete()
        if table.BillWiseDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PaymentInvoiceNo=VoucherNo, PaymentVoucherType=VoucherType).exists():
            billwise_instances = table.BillWiseDetails.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, PaymentInvoiceNo=VoucherNo, PaymentVoucherType=VoucherType)
            for billwise_instance in billwise_instances:
                Amount = billwise_instance.Payments
                BillwiseMasterID = billwise_instance.BillwiseMasterID
                if table.BillWiseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID).exists():
                    master_inst = table.BillWiseMaster.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID).first()
                    Payments = master_inst.Payments
                    Payments = converted_float(
                        Payments) - converted_float(Amount)
                    master_inst.Payments = Payments
                    master_inst.save()
                billwise_instance.delete()
        instance.delete()
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Payment',
                     'Delete', 'Receipt Deleted Successfully.', 'Payment Deleted Successfully.')

        response_data = {
            "StatusCode": 6000,
            "message": "Receipt Master Deleted Successfully!",
            "title": "Success",
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID,
                     'Payment', 'Delete', 'Payment Deleted Failed.', 'Payment Not Found!')
        response_data = {
            "StatusCode": 6001,
            "message": "Payment Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def salesApp_edit_sales(request, pk):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data["CompanyID"]
            CompanyID = get_company(CompanyID)
            CreatedUserID = data["CreatedUserID"]
            PriceRounding = data["PriceRounding"]

            today = datetime.datetime.now()
            salesMaster_instance = None
            ledgerPostInstances = None
            salesDetails = None

            salesMaster_instance = table.SalesMaster.objects.get(
                CompanyID=CompanyID, pk=pk)

            SalesMasterID = salesMaster_instance.SalesMasterID
            VoucherNo = salesMaster_instance.VoucherNo
            BranchID = salesMaster_instance.BranchID
            OldLedgerBalance = salesMaster_instance.OldLedgerBalance

            Action = "M"

            try:
                LoyaltyCustomerID = data["LoyaltyCustomerID"]
            except:
                LoyaltyCustomerID = None

            Date = data["Date"]
            CreditPeriod = data["CreditPeriod"]
            LedgerID = data["LedgerID"]
            PriceCategoryID = data["PriceCategoryID"]
            EmployeeID = data["EmployeeID"]
            SalesAccount = data["SalesAccount"]
            try:
                CustomerName = data['CustomerName']
            except:
                CustomerName = ""
            Address1 = data["Address1"]
            Address2 = data["Address2"]
            Address3 = data["Address3"]
            Notes = data["Notes"]
            FinacialYearID = data["FinacialYearID"]
            TaxID = data["TaxID"]
            TaxType = data["TaxType"]
            WarehouseID = data["WarehouseID"]
            TableID = data["TableID"]
            SeatNumber = data["SeatNumber"]
            NoOfGuests = data["NoOfGuests"]
            INOUT = data["INOUT"]
            TokenNumber = data["TokenNumber"]
            CardTypeID = data["CardTypeID"]
            CardNumber = data["CardNumber"]
            IsActive = data["IsActive"]
            IsPosted = data["IsPosted"]
            SalesType = data["SalesType"]
            BatchID = data["BatchID"]

            TotalGrossAmt = converted_float(data["TotalGrossAmt"])
            AddlDiscPercent = converted_float(data["AddlDiscPercent"])
            AddlDiscAmt = converted_float(data["AddlDiscAmt"])
            TotalDiscount = converted_float(data["TotalDiscount"])
            TotalTax = converted_float(data["TotalTax"])
            NetTotal = converted_float(data["NetTotal"])
            AdditionalCost = converted_float(data["AdditionalCost"])
            GrandTotal = converted_float(data["GrandTotal"])
            RoundOff = converted_float(data["RoundOff"])
            CashReceived = converted_float(data["CashReceived"])
            if not CashReceived:
                CashReceived = 0
            BankAmount = converted_float(data["BankAmount"])
            if not BankAmount:
                BankAmount = 0
            BillDiscPercent = converted_float(data["BillDiscPercent"])
            BillDiscAmt = converted_float(data["BillDiscAmt"])
            VATAmount = converted_float(data["VATAmount"])
            SGSTAmount = converted_float(data["SGSTAmount"])
            CGSTAmount = converted_float(data["CGSTAmount"])
            IGSTAmount = converted_float(data["IGSTAmount"])
            TAX1Amount = converted_float(data["TAX1Amount"])
            TAX2Amount = converted_float(data["TAX2Amount"])
            TAX3Amount = converted_float(data["TAX3Amount"])

            try:
                KFCAmount = converted_float(data["KFCAmount"])
            except:
                KFCAmount = 0

            Cash_Account = None
            Bank_Account = None

            if table.UserTable.objects.filter(
                CompanyID=CompanyID, customer__user__pk=CreatedUserID,Active=True
            ).exists():
                Cash_Account = table.UserTable.objects.get(
                    CompanyID=CompanyID, customer__user__pk=CreatedUserID,Active=True
                ).Cash_Account
                Bank_Account = table.UserTable.objects.get(
                    CompanyID=CompanyID, customer__user__pk=CreatedUserID,Active=True
                ).Bank_Account

            try:
                CashID = data["CashID"]
            except:
                CashID = Cash_Account

            try:
                BankID = data["BankID"]
            except:
                BankID = Bank_Account

            Balance = converted_float(data["Balance"])

            try:
                TaxTaxableAmount = converted_float(data["TaxTaxableAmount"])
            except:
                TaxTaxableAmount = 0
            try:
                NonTaxTaxableAmount = converted_float(
                    data["NonTaxTaxableAmount"])
            except:
                NonTaxTaxableAmount = 0
            AllowCashReceiptMoreSaleAmt = data["AllowCashReceiptMoreSaleAmt"]

            TransactionTypeID = data["TransactionTypeID"]
            account_group = table.AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=LedgerID
            ).AccountGroupUnder
            CashAmount, PostingCashAmount = get_CashAmount(
                account_group, AllowCashReceiptMoreSaleAmt, CashReceived, BankAmount, GrandTotal)

            try:
                ShippingCharge = data["ShippingCharge"]
            except:
                ShippingCharge = 0

            try:
                shipping_tax_amount = data["shipping_tax_amount"]
            except:
                shipping_tax_amount = 0

            try:
                TaxTypeID = data["TaxTypeID"]
            except:
                TaxTypeID = ""

            try:
                SAC = data["SAC"]
            except:
                SAC = ""

            try:
                SalesTax = data["SalesTax"]
            except:
                SalesTax = 0

            try:
                Country_of_Supply = data["Country_of_Supply"]
            except:
                Country_of_Supply = ""

            try:
                State_of_Supply = data["State_of_Supply"]
            except:
                State_of_Supply = ""

            try:
                GST_Treatment = data["GST_Treatment"]
            except:
                GST_Treatment = ""

            try:
                VAT_Treatment = data["VAT_Treatment"]
            except:
                VAT_Treatment = ""

            try:
                ShippingAddress = data["ShippingAddress"]
            except:
                ShippingAddress = None

            try:
                BillingAddress = data["BillingAddress"]
            except:
                BillingAddress = None

            try:
                is_manual_roundoff = data["is_manual_roundoff"]
            except:
                is_manual_roundoff = False

            if ShippingAddress:
                if table.UserAdrress.objects.filter(id=ShippingAddress).exists():
                    ShippingAddress = table.UserAdrress.objects.get(
                        id=ShippingAddress)
                else:
                    ShippingAddress = None

            if BillingAddress:
                if table.UserAdrress.objects.filter(id=BillingAddress).exists():
                    BillingAddress = table.UserAdrress.objects.get(
                        id=BillingAddress)
                else:
                    BillingAddress = None

            # =========
            details = data["SalesDetails"]
            TotalTaxableAmount = 0
            for i in details:
                TotalTaxableAmount += converted_float(i["TaxableAmount"])
            # =========

            # Loyalty Customer instance
            is_LoyaltyCustomer = False
            loyalty_customer = None
            if LoyaltyCustomerID:
                if table.LoyaltyCustomer.objects.filter(pk=LoyaltyCustomerID).exists():
                    loyalty_customer = table.LoyaltyCustomer.objects.get(
                        pk=LoyaltyCustomerID)
                    is_LoyaltyCustomer = True

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
                UpdatedUserID=CreatedUserID,
                Action=Action,
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
                Balance=Balance,
                TransactionTypeID=TransactionTypeID,
                CompanyID=CompanyID,
                KFCAmount=KFCAmount,
                OldLedgerBalance=OldLedgerBalance,
                CashID=CashID,
                BankID=BankID,
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
                BillingAddress=BillingAddress,
                TaxTaxableAmount=TaxTaxableAmount,
                NonTaxTaxableAmount=NonTaxTaxableAmount,
                is_manual_roundoff=is_manual_roundoff
            )
            if table.SerialNumbers.objects.filter(
                CompanyID=CompanyID,
                SalesMasterID=SalesMasterID,
                BranchID=BranchID,
                VoucherType="SI",
            ).exists():
                SerialNumbersInstances = table.SerialNumbers.objects.filter(
                    CompanyID=CompanyID,
                    SalesMasterID=SalesMasterID,
                    BranchID=BranchID,
                    VoucherType="SI",
                ).delete()

            update_ledger = UpdateLedgerBalance(
                CompanyID, BranchID, 0, SalesMasterID, "SI", 0, "Cr", "update"
            )

            if table.LedgerPosting.objects.filter(
                CompanyID=CompanyID,
                VoucherMasterID=SalesMasterID,
                BranchID=BranchID,
                VoucherType="SI",
            ).exists():
                ledgerPostInstances = table.LedgerPosting.objects.filter(
                    CompanyID=CompanyID,
                    VoucherMasterID=SalesMasterID,
                    BranchID=BranchID,
                    VoucherType="SI",
                ).delete()

            if table.SalesDetails.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, SalesMasterID=SalesMasterID
            ).exists():
                sale_ins = table.SalesDetails.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, SalesMasterID=SalesMasterID
                )
                for i in sale_ins:
                    BatchCode = i.BatchCode
                    Qty = i.Qty
                    instance_MultiFactor = table.PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=i.PriceListID
                    ).MultiFactor

                    instance_qty_sum = converted_float(
                        i.FreeQty) + converted_float(i.Qty)
                    instance_Qty = converted_float(
                        instance_MultiFactor) * converted_float(instance_qty_sum)
                    if table.Batch.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode
                    ).exists():
                        batch_ins = table.Batch.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode
                        )
                        StockOut = batch_ins.StockOut
                        batch_ins.StockOut = converted_float(
                            StockOut) - converted_float(instance_Qty)
                        batch_ins.save()

                    if not table.StockPosting.objects.filter(
                        CompanyID=CompanyID,
                        VoucherMasterID=SalesMasterID,
                        VoucherDetailID=i.SalesDetailsID,
                        BranchID=BranchID,
                        VoucherType="SI",
                    ).exists():
                        table.StockPosting.objects.filter(
                            CompanyID=CompanyID,
                            VoucherMasterID=SalesMasterID,
                            BranchID=BranchID,
                            VoucherType="SI",
                        ).delete()
                        update_stock(CompanyID, BranchID, i.ProductID)

                    if table.StockPosting.objects.filter(
                        CompanyID=CompanyID,
                        VoucherMasterID=SalesMasterID,
                        VoucherDetailID=i.SalesDetailsID,
                        ProductID=i.ProductID,
                        BranchID=BranchID,
                        VoucherType="SI",
                    ).exists():
                        stock_inst = table.StockPosting.objects.filter(
                            CompanyID=CompanyID,
                            VoucherMasterID=SalesMasterID,
                            VoucherDetailID=i.SalesDetailsID,
                            ProductID=i.ProductID,
                            BranchID=BranchID,
                            VoucherType="SI",
                        ).first()
                        stock_inst.QtyOut = converted_float(stock_inst.QtyOut) - converted_float(
                            instance_Qty
                        )
                        stock_inst.save()
                        update_stock(CompanyID, BranchID, i.ProductID)

            salesMaster_instance.Date = Date
            salesMaster_instance.CreditPeriod = CreditPeriod
            salesMaster_instance.LedgerID = LedgerID
            salesMaster_instance.PriceCategoryID = PriceCategoryID
            salesMaster_instance.EmployeeID = EmployeeID
            salesMaster_instance.SalesAccount = SalesAccount
            salesMaster_instance.CustomerName = CustomerName
            salesMaster_instance.Address1 = Address1
            salesMaster_instance.Address2 = Address2
            salesMaster_instance.Address3 = Address3
            salesMaster_instance.Notes = Notes
            salesMaster_instance.FinacialYearID = FinacialYearID
            salesMaster_instance.TotalGrossAmt = TotalGrossAmt
            salesMaster_instance.AddlDiscPercent = AddlDiscPercent
            salesMaster_instance.AddlDiscAmt = AddlDiscAmt
            salesMaster_instance.TotalDiscount = TotalDiscount
            salesMaster_instance.TotalTax = TotalTax
            salesMaster_instance.NetTotal = NetTotal
            salesMaster_instance.AdditionalCost = AdditionalCost
            salesMaster_instance.GrandTotal = GrandTotal
            salesMaster_instance.RoundOff = RoundOff
            salesMaster_instance.CashReceived = CashReceived
            salesMaster_instance.CashAmount = CashAmount
            salesMaster_instance.BankAmount = BankAmount
            salesMaster_instance.WarehouseID = WarehouseID
            salesMaster_instance.TableID = TableID
            salesMaster_instance.SeatNumber = SeatNumber
            salesMaster_instance.NoOfGuests = NoOfGuests
            salesMaster_instance.INOUT = INOUT
            salesMaster_instance.TokenNumber = TokenNumber
            salesMaster_instance.CardTypeID = CardTypeID
            salesMaster_instance.CardNumber = CardNumber
            salesMaster_instance.IsActive = IsActive
            salesMaster_instance.IsPosted = IsPosted
            salesMaster_instance.SalesType = SalesType
            salesMaster_instance.UpdatedUserID = CreatedUserID
            salesMaster_instance.UpdatedDate = today
            salesMaster_instance.Action = Action
            salesMaster_instance.TaxID = TaxID
            salesMaster_instance.TaxType = TaxType
            salesMaster_instance.BillDiscPercent = BillDiscPercent
            salesMaster_instance.BillDiscAmt = BillDiscAmt
            salesMaster_instance.VATAmount = VATAmount
            salesMaster_instance.SGSTAmount = SGSTAmount
            salesMaster_instance.CGSTAmount = CGSTAmount
            salesMaster_instance.IGSTAmount = IGSTAmount
            salesMaster_instance.TAX1Amount = TAX1Amount
            salesMaster_instance.TAX2Amount = TAX2Amount
            salesMaster_instance.TAX3Amount = TAX3Amount
            salesMaster_instance.KFCAmount = KFCAmount
            salesMaster_instance.Balance = Balance
            salesMaster_instance.TransactionTypeID = TransactionTypeID
            salesMaster_instance.CashID = CashID
            salesMaster_instance.BankID = BankID
            salesMaster_instance.ShippingCharge = ShippingCharge
            salesMaster_instance.shipping_tax_amount = shipping_tax_amount
            salesMaster_instance.TaxTypeID = TaxTypeID
            salesMaster_instance.SAC = SAC
            salesMaster_instance.SalesTax = SalesTax
            salesMaster_instance.TotalTaxableAmount = TotalTaxableAmount
            salesMaster_instance.Country_of_Supply = Country_of_Supply
            salesMaster_instance.State_of_Supply = State_of_Supply
            salesMaster_instance.GST_Treatment = GST_Treatment
            salesMaster_instance.VAT_Treatment = VAT_Treatment
            salesMaster_instance.ShippingAddress = ShippingAddress
            salesMaster_instance.BillingAddress = BillingAddress
            salesMaster_instance.TaxTaxableAmount = TaxTaxableAmount
            salesMaster_instance.NonTaxTaxableAmount = NonTaxTaxableAmount
            salesMaster_instance.is_manual_roundoff = is_manual_roundoff

            # Taiking Loyalty Customer instance
            if loyalty_customer:
                salesMaster_instance.LoyaltyCustomerID = loyalty_customer

            LoyaltyCustomerID = (loyalty_customer,)
            salesMaster_instance.save()

            # billwise table insertion
            VoucherType = "SI"
            handleBillwiseChanges(CompanyID, BranchID, CashReceived, BankAmount, GrandTotal,
                                  LedgerID, VoucherNo, VoucherType, "edit", CreditPeriod, SalesMasterID, Date)
            # enable_billwise = get_GeneralSettings(
            #     CompanyID, BranchID, "EnableBillwise")
            # total_amount_received = converted_float(
            #     CashReceived) + converted_float(BankAmount)
            # paymnt_sm = 0
            # if enable_billwise and converted_float(total_amount_received) <= converted_float(GrandTotal) and table.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder__in=[10, 29]).exists():
            #     if table.BillWiseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, InvoiceNo=VoucherNo, VoucherType=VoucherType, CustomerID=LedgerID).exists():
            #         billwise_ins = table.BillWiseMaster.objects.filter(
            #             CompanyID=CompanyID, BranchID=BranchID, InvoiceNo=VoucherNo, VoucherType=VoucherType, CustomerID=LedgerID).first()
            #         billwise_ins.VoucherDate = Date
            #         billwise_ins.InvoiceAmount = GrandTotal
            #         if table.BillWiseDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=billwise_ins.BillwiseMasterID, InvoiceNo=VoucherNo, PaymentVoucherType=VoucherType, PaymentInvoiceNo=VoucherNo).exists():
            #             billwise_details = table.BillWiseDetails.objects.filter(
            #                 CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=billwise_ins.BillwiseMasterID, InvoiceNo=VoucherNo, PaymentVoucherType=VoucherType, PaymentInvoiceNo=VoucherNo).first()
            #             billwise_details.Payments = total_amount_received
            #             billwise_details.save()
            #             billwise_details_ins = table.BillWiseDetails.objects.filter(
            #                 CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=billwise_ins.BillwiseMasterID, InvoiceNo=VoucherNo)
            #             paymnt_sm = billwise_details_ins.aggregate(
            #                 Sum("Payments"))
            #             paymnt_sm = paymnt_sm["Payments__sum"]
            #         billwise_ins.Payments = paymnt_sm
            #         billwise_ins.save()
            #     elif table.BillWiseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, InvoiceNo=VoucherNo, VoucherType=VoucherType).exists():
            #         billwise_ins = table.BillWiseMaster.objects.filter(
            #             CompanyID=CompanyID, BranchID=BranchID, InvoiceNo=VoucherNo, VoucherType=VoucherType).first()
            #         billwise_ins.VoucherDate = Date
            #         billwise_ins.InvoiceAmount = GrandTotal
            #         billwise_ins.CustomerID = LedgerID
            #         if table.BillWiseDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=billwise_ins.BillwiseMasterID, InvoiceNo=VoucherNo, PaymentVoucherType=VoucherType, PaymentInvoiceNo=VoucherNo).exists():
            #             billwise_details = table.BillWiseDetails.objects.filter(
            #                 CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=billwise_ins.BillwiseMasterID, InvoiceNo=VoucherNo, PaymentVoucherType=VoucherType, PaymentInvoiceNo=VoucherNo).first()
            #             billwise_details.Payments = total_amount_received
            #             billwise_details.save()
            #             billwise_details_ins = table.BillWiseDetails.objects.filter(
            #                 CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=billwise_ins.BillwiseMasterID, InvoiceNo=VoucherNo)
            #             paymnt_sm = billwise_details_ins.aggregate(
            #                 Sum("Payments"))
            #             paymnt_sm = paymnt_sm["Payments__sum"]
            #         billwise_ins.Payments = paymnt_sm
            #         billwise_ins.save()
            #     else:
            #         BillwiseMasterID = get_BillwiseMasterID(
            #             BranchID, CompanyID)
            #         DueDate = get_nth_day_date(CreditPeriod)
            #         table.BillWiseMaster.objects.create(
            #             CompanyID=CompanyID,
            #             BranchID=BranchID,
            #             BillwiseMasterID=BillwiseMasterID,
            #             InvoiceNo=VoucherNo,
            #             TransactionID=SalesMasterID,
            #             VoucherType=VoucherType,
            #             VoucherDate=Date,
            #             InvoiceAmount=GrandTotal,
            #             Payments=total_amount_received,
            #             DueDate=DueDate,
            #             CustomerID=LedgerID
            #         )
            #         BillwiseDetailsID = get_BillwiseDetailsID(
            #             BranchID, CompanyID)
            #         table.BillWiseDetails.objects.create(
            #             CompanyID=CompanyID,
            #             BranchID=BranchID,
            #             BillwiseDetailsID=BillwiseDetailsID,
            #             BillwiseMasterID=BillwiseMasterID,
            #             InvoiceNo=VoucherNo,
            #             VoucherType=VoucherType,
            #             PaymentDate=Date,
            #             Payments=total_amount_received,
            #             PaymentVoucherType=VoucherType,
            #             PaymentInvoiceNo=VoucherNo
            #         )

            Loyalty_Point_Expire = data["Loyalty_Point_Expire"]
            if is_LoyaltyCustomer:
                details = data["SalesDetails"]

                try:
                    RadeemPoint = data["RadeemPoint"]
                except:
                    RadeemPoint = None
                edit_LoyaltyCalculation(
                    salesMaster_instance,
                    loyalty_customer,
                    details,
                    Loyalty_Point_Expire,
                    RadeemPoint,
                )
                # ===========================

            VoucherType = "SI"

            account_group = table.AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=LedgerID
            ).AccountGroupUnder

            if TaxType == "VAT":
                if converted_float(VATAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

                    # VAT on Sales
                    vat_on_sales = get_BranchLedgerId_for_LedgerPosting(
                        BranchID, CompanyID, "vat_on_sales"
                    )

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        vat_on_sales,
                        SalesMasterID,
                        VoucherType,
                        VATAmount,
                        "Cr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesMasterID,
                        VoucherType,
                        VATAmount,
                        "Dr",
                        "create",
                    )

            elif TaxType == "GST Intra-state B2B" or TaxType == "GST Intra-state B2C":
                if converted_float(CGSTAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

                    # Central GST on Sales
                    central_gst_on_sales = get_BranchLedgerId_for_LedgerPosting(
                        BranchID, CompanyID, "central_gst_on_sales"
                    )

                    table.LedgerPosting.objects.create(
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
                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        central_gst_on_sales,
                        SalesMasterID,
                        VoucherType,
                        CGSTAmount,
                        "Cr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesMasterID,
                        VoucherType,
                        CGSTAmount,
                        "Dr",
                        "create",
                    )

                if converted_float(SGSTAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

                    # State GST on Sales
                    state_gst_on_sales = get_BranchLedgerId_for_LedgerPosting(
                        BranchID, CompanyID, "state_gst_on_sales"
                    )

                    table.LedgerPosting.objects.create(
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
                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        state_gst_on_sales,
                        SalesMasterID,
                        VoucherType,
                        SGSTAmount,
                        "Cr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesMasterID,
                        VoucherType,
                        SGSTAmount,
                        "Dr",
                        "create",
                    )

                if converted_float(KFCAmount) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

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
                        CompanyID,
                        BranchID,
                        93,
                        SalesMasterID,
                        VoucherType,
                        KFCAmount,
                        "Cr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

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
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesMasterID,
                        VoucherType,
                        KFCAmount,
                        "Dr",
                        "create",
                    )

            elif TaxType == "GST Inter-state B2B" or TaxType == "GST Inter-state B2C":
                if converted_float(IGSTAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

                    # Integrated GST on Sales
                    integrated_gst_on_sales = get_BranchLedgerId_for_LedgerPosting(
                        BranchID, CompanyID, "integrated_gst_on_sales"
                    )

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        integrated_gst_on_sales,
                        SalesMasterID,
                        VoucherType,
                        IGSTAmount,
                        "Cr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

                    table.LedgerPosting.objects.create(
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

                    table.LedgerPosting_Log.objects.create(
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

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesMasterID,
                        VoucherType,
                        IGSTAmount,
                        "Dr",
                        "create",
                    )

            if not TaxType == "Export":
                if converted_float(TAX1Amount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )
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
                        CompanyID,
                        BranchID,
                        16,
                        SalesMasterID,
                        VoucherType,
                        TAX1Amount,
                        "Cr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )
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
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesMasterID,
                        VoucherType,
                        TAX1Amount,
                        "Dr",
                        "create",
                    )

                if converted_float(TAX2Amount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )
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
                        CompanyID,
                        BranchID,
                        19,
                        SalesMasterID,
                        VoucherType,
                        TAX2Amount,
                        "Cr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )
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
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesMasterID,
                        VoucherType,
                        TAX2Amount,
                        "Dr",
                        "create",
                    )

                if converted_float(TAX3Amount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )
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
                        CompanyID,
                        BranchID,
                        22,
                        SalesMasterID,
                        VoucherType,
                        TAX3Amount,
                        "Cr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )
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
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesMasterID,
                        VoucherType,
                        TAX3Amount,
                        "Dr",
                        "create",
                    )

            if converted_float(RoundOff) > 0:

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID
                )

                # Round off Sales
                round_off_sales = get_BranchLedgerId_for_LedgerPosting(
                    BranchID, CompanyID, "round_off_sales"
                )

                table.LedgerPosting.objects.create(
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

                table.LedgerPosting_Log.objects.create(
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

                update_ledger = UpdateLedgerBalance(
                    CompanyID,
                    BranchID,
                    round_off_sales,
                    SalesMasterID,
                    VoucherType,
                    RoundOff,
                    "Cr",
                    "create",
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID
                )

                table.LedgerPosting.objects.create(
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

                table.LedgerPosting_Log.objects.create(
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

                update_ledger = UpdateLedgerBalance(
                    CompanyID,
                    BranchID,
                    SalesAccount,
                    SalesMasterID,
                    VoucherType,
                    RoundOff,
                    "Dr",
                    "create",
                )

            if converted_float(RoundOff) < 0:

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID
                )

                RoundOff = abs(converted_float(RoundOff))

                # Round off Sales
                round_off_sales = get_BranchLedgerId_for_LedgerPosting(
                    BranchID, CompanyID, "round_off_sales"
                )

                table.LedgerPosting.objects.create(
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

                table.LedgerPosting_Log.objects.create(
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

                update_ledger = UpdateLedgerBalance(
                    CompanyID,
                    BranchID,
                    round_off_sales,
                    SalesMasterID,
                    VoucherType,
                    RoundOff,
                    "Dr",
                    "create",
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID
                )

                table.LedgerPosting.objects.create(
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

                table.LedgerPosting_Log.objects.create(
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

                update_ledger = UpdateLedgerBalance(
                    CompanyID,
                    BranchID,
                    SalesAccount,
                    SalesMasterID,
                    VoucherType,
                    RoundOff,
                    "Cr",
                    "create",
                )

            if converted_float(TotalDiscount) > 0:

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID
                )
                # Discount on Sales
                discount_on_sales = get_BranchLedgerId_for_LedgerPosting(
                    BranchID, CompanyID, "discount_on_sales"
                )

                table.LedgerPosting.objects.create(
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

                table.LedgerPosting_Log.objects.create(
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

                update_ledger = UpdateLedgerBalance(
                    CompanyID,
                    BranchID,
                    discount_on_sales,
                    SalesMasterID,
                    VoucherType,
                    TotalDiscount,
                    "Dr",
                    "create",
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID
                )

                table.LedgerPosting.objects.create(
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

                table.LedgerPosting_Log.objects.create(
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

                update_ledger = UpdateLedgerBalance(
                    CompanyID,
                    BranchID,
                    SalesAccount,
                    SalesMasterID,
                    VoucherType,
                    TotalDiscount,
                    "Cr",
                    "create",
                )

            # credit sales start here
            if converted_float(CashReceived) == 0 and converted_float(BankAmount) == 0:
                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID
                )

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
                    CompanyID,
                    BranchID,
                    SalesAccount,
                    SalesMasterID,
                    VoucherType,
                    GrandTotal,
                    "Cr",
                    "create",
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID
                )

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
                    CompanyID,
                    BranchID,
                    LedgerID,
                    SalesMasterID,
                    VoucherType,
                    GrandTotal,
                    "Dr",
                    "create",
                )

            # credit sales end here

            # customer with cash and customer with partial cash start here
            elif (
                (account_group == 10 or account_group == 29 or account_group == 32)
                and converted_float(CashReceived) > 0
                and converted_float(BankAmount) == 0
            ):
                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID
                )

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
                    CompanyID,
                    BranchID,
                    SalesAccount,
                    SalesMasterID,
                    VoucherType,
                    GrandTotal,
                    "Cr",
                    "create",
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID
                )

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
                    CompanyID,
                    BranchID,
                    LedgerID,
                    SalesMasterID,
                    VoucherType,
                    GrandTotal,
                    "Dr",
                    "create",
                )
                if CashAmount > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

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
                        CompanyID,
                        BranchID,
                        CashID,
                        SalesMasterID,
                        VoucherType,
                        CashAmount,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

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
                        CompanyID,
                        BranchID,
                        LedgerID,
                        SalesMasterID,
                        VoucherType,
                        CashAmount,
                        "Cr",
                        "create",
                    )

            # customer with cash and customer with partial cash end here

            # customer with bank and customer with partial bank start here
            elif (
                (account_group == 10 or account_group == 29 or account_group == 32)
                and converted_float(CashReceived) == 0
                and converted_float(BankAmount) > 0
            ):
                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID
                )

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
                    CompanyID,
                    BranchID,
                    SalesAccount,
                    SalesMasterID,
                    VoucherType,
                    GrandTotal,
                    "Cr",
                    "create",
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID
                )

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
                    CompanyID,
                    BranchID,
                    LedgerID,
                    SalesMasterID,
                    VoucherType,
                    GrandTotal,
                    "Dr",
                    "create",
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID
                )

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
                    CompanyID,
                    BranchID,
                    BankID,
                    SalesMasterID,
                    VoucherType,
                    BankAmount,
                    "Dr",
                    "create",
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID
                )

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
                    CompanyID,
                    BranchID,
                    LedgerID,
                    SalesMasterID,
                    VoucherType,
                    BankAmount,
                    "Cr",
                    "create",
                )

            # customer with bank and customer with partial bank end here

            # bank with cash and cash with cash start here
            elif (
                (account_group == 8 or account_group == 9)
                and converted_float(CashReceived) > 0
                and converted_float(BankAmount) == 0
            ):
                if CashAmount > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

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
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesMasterID,
                        VoucherType,
                        CashAmount,
                        "Cr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

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
                        CompanyID,
                        BranchID,
                        CashID,
                        SalesMasterID,
                        VoucherType,
                        CashAmount,
                        "Dr",
                        "create",
                    )

                csh_value = converted_float(
                    GrandTotal) - converted_float(CashReceived)
                if converted_float(csh_value) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

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
                        CompanyID,
                        BranchID,
                        LedgerID,
                        SalesMasterID,
                        VoucherType,
                        csh_value,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

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
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesMasterID,
                        VoucherType,
                        csh_value,
                        "Cr",
                        "create",
                    )
            # bank with cash and cash with cash end here

            # bank with bank and cash with bank start here
            elif (
                (account_group == 8 or account_group == 9)
                and converted_float(CashReceived) == 0
                and converted_float(BankAmount) > 0
            ):
                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID
                )

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
                    CompanyID,
                    BranchID,
                    SalesAccount,
                    SalesMasterID,
                    VoucherType,
                    BankAmount,
                    "Cr",
                    "create",
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID
                )

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
                    CompanyID,
                    BranchID,
                    BankID,
                    SalesMasterID,
                    VoucherType,
                    BankAmount,
                    "Dr",
                    "create",
                )

                bnk_value = converted_float(
                    GrandTotal) - converted_float(BankAmount)
                if not converted_float(bnk_value) == 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

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
                        CompanyID,
                        BranchID,
                        LedgerID,
                        SalesMasterID,
                        VoucherType,
                        bnk_value,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

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
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesMasterID,
                        VoucherType,
                        bnk_value,
                        "Cr",
                        "create",
                    )

            # bank with bank and cash with bank end here

            # customer with partial cash /bank and customer with cash/bank
            elif (
                (account_group == 10 or account_group == 29 or account_group == 32)
                and converted_float(CashReceived) > 0
                and converted_float(BankAmount) > 0
            ):
                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID
                )

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
                    CompanyID,
                    BranchID,
                    SalesAccount,
                    SalesMasterID,
                    VoucherType,
                    GrandTotal,
                    "Cr",
                    "create",
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID
                )

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
                    CompanyID,
                    BranchID,
                    LedgerID,
                    SalesMasterID,
                    VoucherType,
                    GrandTotal,
                    "Dr",
                    "create",
                )
                if CashAmount > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

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
                        CompanyID,
                        BranchID,
                        CashID,
                        SalesMasterID,
                        VoucherType,
                        CashAmount,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

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
                        CompanyID,
                        BranchID,
                        LedgerID,
                        SalesMasterID,
                        VoucherType,
                        CashAmount,
                        "Cr",
                        "create",
                    )

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID
                )

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
                    CompanyID,
                    BranchID,
                    BankID,
                    SalesMasterID,
                    VoucherType,
                    BankAmount,
                    "Dr",
                    "create",
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID
                )

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

                update_ledger = UpdateLedgerBalance(
                    CompanyID,
                    BranchID,
                    BankID,
                    SalesMasterID,
                    VoucherType,
                    BankAmount,
                    "Cr",
                    "create",
                )
            # customer with partial cash /bank and customer with cash/bank

            # cash with cash/bank start here
            elif (
                (account_group == 9 or account_group == 8)
                and converted_float(CashReceived) > 0
                and converted_float(BankAmount) > 0
            ):

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID
                )

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
                    CompanyID,
                    BranchID,
                    BankID,
                    SalesMasterID,
                    VoucherType,
                    BankAmount,
                    "Dr",
                    "create",
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID
                )

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
                    CompanyID,
                    BranchID,
                    SalesAccount,
                    SalesMasterID,
                    VoucherType,
                    BankAmount,
                    "Cr",
                    "create",
                )
                if CashAmount > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

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
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesMasterID,
                        VoucherType,
                        CashAmount,
                        "Cr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

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
                        CompanyID,
                        BranchID,
                        CashID,
                        SalesMasterID,
                        VoucherType,
                        CashAmount,
                        "Dr",
                        "create",
                    )

            deleted_datas = data["deleted_data"]
            if deleted_datas:
                for deleted_Data in deleted_datas:
                    deleted_pk = deleted_Data["unq_id"]
                    SalesDetailsID_Deleted = deleted_Data["SalesDetailsID"]
                    ProductID_Deleted = deleted_Data["ProductID"]
                    PriceListID_Deleted = deleted_Data["PriceListID"]
                    Rate_Deleted = deleted_Data["Rate"]
                    SalesMasterID_Deleted = deleted_Data["SalesMasterID"]
                    WarehouseID_Deleted = deleted_Data["WarehouseID"]

                    if table.PriceList.objects.filter(
                        CompanyID=CompanyID,
                        ProductID=ProductID_Deleted,
                        DefaultUnit=True,
                    ).exists():
                        priceList = table.PriceList.objects.get(
                            CompanyID=CompanyID,
                            ProductID=ProductID_Deleted,
                            DefaultUnit=True,
                        )
                        MultiFactor = priceList.MultiFactor
                        Cost = converted_float(
                            Rate_Deleted) / converted_float(MultiFactor)
                        Ct = round(Cost, 4)
                        Cost_Deleted = str(Ct)

                        if not deleted_pk == "" or not deleted_pk == 0:
                            if table.SalesDetails.objects.filter(
                                CompanyID=CompanyID, pk=deleted_pk
                            ).exists():
                                deleted_detail = table.SalesDetails.objects.get(
                                    CompanyID=CompanyID, pk=deleted_pk
                                )

                                deleted_BatchCode = deleted_detail.BatchCode
                                deleted_batch = table.Batch.objects.filter(
                                    CompanyID=CompanyID,
                                    BranchID=BranchID,
                                    BatchCode=deleted_BatchCode,
                                ).first()

                                MultiFactor = table.PriceList.objects.get(
                                    CompanyID=CompanyID,
                                    PriceListID=PriceListID_Deleted,
                                    BranchID=BranchID,
                                ).MultiFactor

                                qty_batch = converted_float(deleted_detail.FreeQty) + converted_float(
                                    deleted_detail.Qty
                                )
                                Qty_batch = converted_float(
                                    MultiFactor) * converted_float(qty_batch)

                                if table.Batch.objects.filter(
                                    CompanyID=CompanyID,
                                    BranchID=BranchID,
                                    BatchCode=BatchCode,
                                ).exists():
                                    batch_ins = table.Batch.objects.get(
                                        CompanyID=CompanyID,
                                        BranchID=BranchID,
                                        BatchCode=BatchCode,
                                    )
                                    StockOut = batch_ins.StockOut
                                    batch_ins.StockOut = converted_float(StockOut) - converted_float(
                                        Qty_batch
                                    )
                                    batch_ins.save()

                                deleted_detail.delete()

                                if table.StockPosting.objects.filter(
                                    CompanyID=CompanyID,
                                    VoucherMasterID=SalesMasterID_Deleted,
                                    VoucherDetailID=SalesDetailsID_Deleted,
                                    ProductID=ProductID_Deleted,
                                    BranchID=BranchID,
                                    VoucherType="SI",
                                ).exists():
                                    stock_instances_delete = (
                                        table.StockPosting.objects.filter(
                                            CompanyID=CompanyID,
                                            VoucherMasterID=SalesMasterID_Deleted,
                                            VoucherDetailID=SalesDetailsID_Deleted,
                                            ProductID=ProductID_Deleted,
                                            BranchID=BranchID,
                                            VoucherType="SI",
                                        )
                                    )
                                    stock_instances_delete.delete()
                                    update_stock(
                                        CompanyID, BranchID, ProductID_Deleted)

            salesdetails = data["SalesDetails"]

            for salesdetail in salesdetails:
                ProductID = salesdetail["ProductID"]
                if ProductID:
                    pk = salesdetail["unq_id"]
                    detailID = salesdetail["detailID"]
                    Qty_detail = salesdetail["Qty"]
                    FreeQty = salesdetail["FreeQty"]
                    PriceListID = salesdetail["PriceListID"]
                    Flavour = salesdetail["Flavour"]
                    try:
                        BatchCode = salesdetail["BatchCode"]
                    except:
                        BatchCode = ""
                    try:
                        is_inclusive = salesdetail["is_inclusive"]
                    except:
                        is_inclusive = False
                    UnitPrice = 0
                    if salesdetail["UnitPrice"]:
                        UnitPrice = converted_float(salesdetail["UnitPrice"])
                    InclusivePrice = converted_float(
                        salesdetail["InclusivePrice"])
                    try:
                        RateWithTax = converted_float(
                            salesdetail["RateWithTax"])
                    except:
                        RateWithTax = 0
                    CostPerPrice = converted_float(salesdetail["CostPerPrice"])
                    AddlDiscPerc = converted_float(salesdetail["AddlDiscPerc"])
                    AddlDiscAmt = converted_float(salesdetail["AddlDiscAmt"])
                    DiscountPerc = converted_float(salesdetail["DiscountPerc"])
                    DiscountAmount = converted_float(
                        salesdetail["DiscountAmount"])
                    GrossAmount = converted_float(salesdetail["GrossAmount"])
                    TaxableAmount = converted_float(
                        salesdetail["TaxableAmount"])
                    VATPerc = converted_float(salesdetail["VATPerc"])
                    VATAmount = converted_float(salesdetail["VATAmount"])
                    SGSTPerc = converted_float(salesdetail["SGSTPerc"])
                    SGSTAmount = converted_float(salesdetail["SGSTAmount"])
                    CGSTPerc = converted_float(salesdetail["CGSTPerc"])
                    CGSTAmount = converted_float(salesdetail["CGSTAmount"])
                    IGSTPerc = converted_float(salesdetail["IGSTPerc"])
                    IGSTAmount = converted_float(salesdetail["IGSTAmount"])
                    NetAmount = converted_float(salesdetail["NetAmount"])
                    TAX1Perc = converted_float(salesdetail["TAX1Perc"])
                    TAX1Amount = converted_float(salesdetail["TAX1Amount"])
                    TAX2Perc = converted_float(salesdetail["TAX2Perc"])
                    TAX2Amount = converted_float(salesdetail["TAX2Amount"])
                    TAX3Perc = converted_float(salesdetail["TAX3Perc"])
                    TAX3Amount = converted_float(salesdetail["TAX3Amount"])
                    KFCAmount = converted_float(salesdetail["KFCAmount"])

                    try:
                        SerialNos = salesdetail["SerialNos"]
                    except:
                        SerialNos = []

                    try:
                        Description = salesdetail["Description"]
                    except:
                        Description = ""

                    try:
                        KFCPerc = salesdetail["KFCPerc"]
                    except:
                        KFCPerc = 0

                    try:
                        ProductTaxID = salesdetail["ProductTaxID"]
                    except:
                        ProductTaxID = ""
                    try:
                        IsReturn = salesdetail["IsReturn"]
                    except:
                        IsReturn = False

                    # UnitPrice = round(UnitPrice, PriceRounding)
                    # InclusivePrice = round(InclusivePrice, PriceRounding)
                    # RateWithTax = round(RateWithTax, PriceRounding)
                    is_pricecategory = get_general_settings(
                        BranchID, CompanyID, "PriceCategory"
                    )
                    if is_pricecategory == True:
                        price_list_ins = table.PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=PriceListID
                        )
                        if PriceCategoryID == 2:
                            price_list_ins.SalesPrice1 = UnitPrice
                        elif PriceCategoryID == 3:
                            price_list_ins.SalesPrice2 = UnitPrice
                        elif PriceCategoryID == 4:
                            price_list_ins.SalesPrice3 = UnitPrice
                        price_list_ins.save()

                    CostPerPrice = table.PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=PriceListID
                    ).PurchasePrice

                    if is_inclusive == True:
                        Batch_salesPrice = InclusivePrice
                    else:
                        Batch_salesPrice = UnitPrice

                    product_is_Service = table.Product.objects.get(
                        CompanyID=CompanyID, ProductID=ProductID
                    ).is_Service

                    MultiFactor = table.PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=PriceListID
                    ).MultiFactor

                    qty_batch = converted_float(
                        FreeQty) + converted_float(Qty_detail)
                    Qty_batch = converted_float(
                        MultiFactor) * converted_float(qty_batch)
                    if table.GeneralSettings.objects.filter(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        SettingsType="SalesPriceUpdate",
                    ).exists():
                        check_SalesPriceUpdate = table.GeneralSettings.objects.get(
                            CompanyID=CompanyID,
                            SettingsType="SalesPriceUpdate",
                            BranchID=BranchID,
                        ).SettingsValue
                        if (
                            check_SalesPriceUpdate == "True"
                            or check_SalesPriceUpdate == True
                        ):
                            pri_ins = table.PriceList.objects.get(
                                CompanyID=CompanyID, PriceListID=PriceListID
                            )
                            pri_ins.SalesPrice = Batch_salesPrice
                            pri_ins.save()

                    product_purchasePrice = table.PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=PriceListID
                    ).PurchasePrice
                    check_AllowUpdateBatchPriceInSales = False

                    check_AllowUpdateBatchPriceInSales = False
                    check_EnableProductBatchWise = False
                    if product_is_Service == False:
                        if table.GeneralSettings.objects.filter(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            SettingsType="AllowUpdateBatchPriceInSales",
                        ).exists():
                            check_AllowUpdateBatchPriceInSales = (
                                table.GeneralSettings.objects.get(
                                    CompanyID=CompanyID,
                                    BranchID=BranchID,
                                    SettingsType="AllowUpdateBatchPriceInSales",
                                ).SettingsValue
                            )

                        if table.GeneralSettings.objects.filter(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            SettingsType="EnableProductBatchWise",
                        ).exists():
                            check_EnableProductBatchWise = table.GeneralSettings.objects.get(
                                CompanyID=CompanyID,
                                BranchID=BranchID,
                                SettingsType="EnableProductBatchWise",
                            ).SettingsValue

                        if (
                            check_EnableProductBatchWise == True
                            or check_EnableProductBatchWise == "True"
                        ):
                            setbach = SetBatchInSales(
                                CompanyID,
                                BranchID,
                                Batch_salesPrice,
                                Qty_batch,
                                BatchCode,
                                check_AllowUpdateBatchPriceInSales,
                                PriceListID,
                                "SI",
                            )

                    PriceListID_DefUnit = table.PriceList.objects.get(
                        CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True
                    ).PriceListID

                    qty = converted_float(FreeQty) + \
                        converted_float(Qty_detail)

                    Qty = converted_float(MultiFactor) * converted_float(qty)
                    Cost = converted_float(
                        CostPerPrice) / converted_float(MultiFactor)

                    princeList_instance = table.PriceList.objects.get(
                        CompanyID=CompanyID,
                        ProductID=ProductID,
                        PriceListID=PriceListID_DefUnit,
                    )
                    PurchasePrice = princeList_instance.PurchasePrice
                    SalesPrice = princeList_instance.SalesPrice

                    if detailID == 0:
                        salesDetail_instance = table.SalesDetails.objects.get(
                            CompanyID=CompanyID, pk=pk
                        )
                        SalesDetailsID = salesDetail_instance.SalesDetailsID

                        log_instance = table.SalesDetails_Log.objects.create(
                            TransactionID=SalesDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            SalesMasterID=SalesMasterID,
                            ProductID=ProductID,
                            Qty=Qty_detail,
                            ReturnQty=Qty_detail,
                            FreeQty=FreeQty,
                            UnitPrice=UnitPrice,
                            InclusivePrice=InclusivePrice,
                            RateWithTax=RateWithTax,
                            CostPerPrice=CostPerPrice,
                            PriceListID=PriceListID,
                            DiscountPerc=DiscountPerc,
                            DiscountAmount=DiscountAmount,
                            AddlDiscPerc=AddlDiscPerc,
                            AddlDiscAmt=AddlDiscAmt,
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
                            UpdatedUserID=CreatedUserID,
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
                            ProductTaxID=ProductTaxID,
                        )

                        salesDetail_instance.ProductID = ProductID
                        salesDetail_instance.Qty = Qty_detail
                        salesDetail_instance.ReturnQty = Qty_detail
                        salesDetail_instance.FreeQty = FreeQty
                        salesDetail_instance.UnitPrice = UnitPrice
                        salesDetail_instance.InclusivePrice = InclusivePrice
                        salesDetail_instance.RateWithTax = RateWithTax
                        salesDetail_instance.CostPerPrice = CostPerPrice
                        salesDetail_instance.PriceListID = PriceListID
                        salesDetail_instance.DiscountPerc = DiscountPerc
                        salesDetail_instance.DiscountAmount = DiscountAmount
                        salesDetail_instance.AddlDiscPerc = AddlDiscPerc
                        salesDetail_instance.AddlDiscAmt = AddlDiscAmt
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
                        salesDetail_instance.UpdatedUserID = CreatedUserID
                        salesDetail_instance.UpdatedDate = today
                        salesDetail_instance.Flavour = Flavour
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
                        salesDetail_instance.LogID = log_instance.ID
                        salesDetail_instance.Description = Description
                        salesDetail_instance.KFCPerc = KFCPerc
                        salesDetail_instance.ProductTaxID = ProductTaxID
                        salesDetail_instance.IsReturn = IsReturn
                        salesDetail_instance.save()

                        if product_is_Service == False:
                            if table.StockPosting.objects.filter(
                                CompanyID=CompanyID,
                                WareHouseID=WarehouseID,
                                VoucherMasterID=SalesMasterID,
                                VoucherDetailID=SalesDetailsID,
                                BranchID=BranchID,
                                VoucherType="SI",
                                ProductID=ProductID,
                            ).exists():
                                stock_instance = table.StockPosting.objects.filter(
                                    CompanyID=CompanyID,
                                    WareHouseID=WarehouseID,
                                    VoucherMasterID=SalesMasterID,
                                    VoucherDetailID=SalesDetailsID,
                                    BranchID=BranchID,
                                    VoucherType="SI",
                                    ProductID=ProductID,
                                ).first()
                                stock_instance.QtyOut = Qty
                                stock_instance.Date = Date
                                stock_instance.Action = Action
                                stock_instance.save()
                            else:
                                StockPostingID = get_auto_stockPostid(
                                    table.StockPosting, BranchID, CompanyID
                                )
                                pricelist, warehouse = get_ModelInstance(
                                    CompanyID,
                                    BranchID,
                                    PriceListID_DefUnit,
                                    WarehouseID,
                                )

                                table.StockPosting.objects.create(
                                    StockPostingID=StockPostingID,
                                    BranchID=BranchID,
                                    Action=Action,
                                    Date=Date,
                                    VoucherMasterID=SalesMasterID,
                                    VoucherDetailID=SalesDetailsID,
                                    VoucherType=VoucherType,
                                    ProductID=ProductID,
                                    BatchID=BatchCode,
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
                                    warehouse=warehouse,
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
                                    BatchID=BatchCode,
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

                    if detailID == 1:

                        Action = "A"

                        SalesDetailsID = get_auto_id(
                            table.SalesDetails, BranchID, CompanyID)

                        log_instance = table.SalesDetails_Log.objects.create(
                            TransactionID=SalesDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            SalesMasterID=SalesMasterID,
                            ProductID=ProductID,
                            Qty=Qty_detail,
                            ReturnQty=Qty_detail,
                            FreeQty=FreeQty,
                            UnitPrice=UnitPrice,
                            InclusivePrice=InclusivePrice,
                            RateWithTax=RateWithTax,
                            CostPerPrice=CostPerPrice,
                            PriceListID=PriceListID,
                            DiscountPerc=DiscountPerc,
                            DiscountAmount=DiscountAmount,
                            AddlDiscPerc=AddlDiscPerc,
                            AddlDiscAmt=AddlDiscAmt,
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
                            UpdatedUserID=CreatedUserID,
                            Flavour=Flavour,
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            KFCAmount=KFCAmount,
                            CompanyID=CompanyID,
                            Description=Description,
                            KFCPerc=KFCPerc,
                            ProductTaxID=ProductTaxID,
                            BatchCode=BatchCode,
                        )

                        table.SalesDetails.objects.create(
                            SalesDetailsID=SalesDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            SalesMasterID=SalesMasterID,
                            ProductID=ProductID,
                            Qty=Qty_detail,
                            ReturnQty=Qty_detail,
                            FreeQty=FreeQty,
                            UnitPrice=UnitPrice,
                            InclusivePrice=InclusivePrice,
                            RateWithTax=RateWithTax,
                            CostPerPrice=CostPerPrice,
                            PriceListID=PriceListID,
                            DiscountPerc=DiscountPerc,
                            DiscountAmount=DiscountAmount,
                            AddlDiscPerc=AddlDiscPerc,
                            AddlDiscAmt=AddlDiscAmt,
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
                            UpdatedUserID=CreatedUserID,
                            Flavour=Flavour,
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            KFCAmount=KFCAmount,
                            CompanyID=CompanyID,
                            LogID=log_instance.ID,
                            Description=Description,
                            KFCPerc=KFCPerc,
                            ProductTaxID=ProductTaxID,
                            BatchCode=BatchCode,
                            IsReturn=IsReturn
                        )

                        if product_is_Service == False:
                            StockPostingID = get_auto_stockPostid(
                                table.StockPosting, BranchID, CompanyID
                            )
                            pricelist, warehouse = get_ModelInstance(
                                CompanyID, BranchID, PriceListID_DefUnit, WarehouseID
                            )

                            table.StockPosting.objects.create(
                                StockPostingID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=Date,
                                VoucherMasterID=SalesMasterID,
                                VoucherDetailID=SalesDetailsID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                BatchID=BatchCode,
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
                                warehouse=warehouse,
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
                                BatchID=BatchCode,
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

            cash_Balance = get_LedgerBalance(CompanyID, 1)
            response_data = {
                "StatusCode": 6000,
                "message": "Sales Updated Successfully!!!",
                "CashBalance": cash_Balance,
                "id": salesMaster_instance.id,
            }

            return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again",
            "err_descrb": err_descrb,
        }

        activity_id = activity_log(
            request._request,
            CompanyID,
            "Error",
            CreatedUserID,
            "Sales",
            "Edit",
            str(e),
            err_descrb,
        )
        body_params = str(request.data)
        table.Activity_Log.objects.filter(
            id=activity_id).update(body_params=body_params)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def salesApp_salesMaster(request, pk):
    import time
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]
    instance = None
    if table.SalesMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = table.SalesMaster.objects.get(CompanyID=CompanyID, pk=pk)
        serialized = SalesFaeraSerializer(
            instance,
            context={
                "CompanyID": CompanyID,
                "PriceRounding": PriceRounding,
            },
        )
        data = serialized.data
        response_data = {"StatusCode": 6000, "data": data}
    else:
        response_data = {"StatusCode": 6001,
                         "message": "Sales Master Not Found!"}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def salesApp_delete_salesMaster(request, pk):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    try:
        selecte_ids = data["selecte_ids"]
    except:
        selecte_ids = []

    today = datetime.datetime.now()
    instances = None
    if selecte_ids:
        if table.SalesMaster.objects.filter(CompanyID=CompanyID, pk__in=selecte_ids).exists():
            instances = table.SalesMaster.objects.filter(pk__in=selecte_ids)
    else:
        if table.SalesMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
            instances = table.SalesMaster.objects.filter(pk=pk)

    if instances:
        for instance in instances:
            # instance = SalesMaster.objects.get(pk=pk)
            SalesMasterID = instance.SalesMasterID
            LoyaltyCustomerID = instance.LoyaltyCustomerID
            BranchID = instance.BranchID
            VoucherNo = instance.VoucherNo
            Date = instance.Date
            CreditPeriod = instance.CreditPeriod
            LedgerID = instance.LedgerID
            PriceCategoryID = instance.PriceCategoryID
            EmployeeID = instance.EmployeeID
            SalesAccount = instance.SalesAccount
            CustomerName = instance.CustomerName
            Address1 = instance.Address1
            Address2 = instance.Address2
            Address3 = instance.Address3
            Notes = instance.Notes
            FinacialYearID = instance.FinacialYearID
            TotalGrossAmt = instance.TotalGrossAmt
            AddlDiscPercent = instance.AddlDiscPercent
            AddlDiscAmt = instance.AddlDiscAmt
            TotalDiscount = instance.TotalDiscount
            TotalTax = instance.TotalTax
            NetTotal = instance.NetTotal
            AdditionalCost = instance.AdditionalCost
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
            CardTypeID = instance.CardTypeID
            CardNumber = instance.CardNumber
            IsActive = instance.IsActive
            IsPosted = instance.IsPosted
            SalesType = instance.SalesType
            TaxID = instance.TaxID
            TaxType = instance.TaxType
            BillDiscPercent = instance.BillDiscPercent
            BillDiscAmt = instance.BillDiscAmt
            VATAmount = instance.VATAmount
            SGSTAmount = instance.SGSTAmount
            CGSTAmount = instance.CGSTAmount
            IGSTAmount = instance.IGSTAmount
            TAX1Amount = instance.TAX1Amount
            TAX2Amount = instance.TAX2Amount
            TAX3Amount = instance.TAX3Amount
            Balance = instance.Balance
            TransactionTypeID = instance.TransactionTypeID
            CashID = instance.CashID
            BankID = instance.BankID
            KFCAmount = instance.KFCAmount
            Country_of_Supply = instance.Country_of_Supply
            State_of_Supply = instance.State_of_Supply
            GST_Treatment = instance.GST_Treatment
            VAT_Treatment = instance.VAT_Treatment
            ShippingCharge = instance.ShippingCharge
            shipping_tax_amount = instance.shipping_tax_amount
            TaxTypeID = instance.TaxTypeID
            SAC = instance.SAC
            SalesTax = instance.SalesTax
            TaxTaxableAmount = instance.SalesTax
            NonTaxTaxableAmount = instance.SalesTax

            Action = "D"
            if table.BillWiseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, InvoiceNo=VoucherNo, TransactionID=SalesMasterID, VoucherType="SI", Payments__gt=0).exists():
                response_data = {
                    "StatusCode": 6001,
                    "title": "Failed",
                    "message": "You can't Delete this Invoice(" + VoucherNo + ")this has been Paid",
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                table.SalesMaster_Log.objects.create(
                    TransactionID=SalesMasterID,
                    LoyaltyCustomerID=LoyaltyCustomerID,
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
                    UpdatedUserID=CreatedUserID,
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
                    Balance=Balance,
                    TransactionTypeID=TransactionTypeID,
                    CompanyID=CompanyID,
                    Action=Action,
                    CashID=CashID,
                    BankID=BankID,
                    KFCAmount=KFCAmount,
                    Country_of_Supply=Country_of_Supply,
                    State_of_Supply=State_of_Supply,
                    GST_Treatment=GST_Treatment,
                    VAT_Treatment=VAT_Treatment,
                    ShippingCharge=ShippingCharge,
                    shipping_tax_amount=shipping_tax_amount,
                    TaxTypeID=TaxTypeID,
                    SAC=SAC,
                    SalesTax=SalesTax,
                    TaxTaxableAmount=TaxTaxableAmount,
                    NonTaxTaxableAmount=NonTaxTaxableAmount
                )

                if table.LedgerPosting.objects.filter(
                    CompanyID=CompanyID,
                    VoucherMasterID=SalesMasterID,
                    BranchID=BranchID,
                    VoucherType="SI",
                ).exists():
                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, 0, SalesMasterID, "SI", 0, "Cr", "update"
                    )
                    ledgerPostInstances = table.LedgerPosting.objects.filter(
                        CompanyID=CompanyID,
                        VoucherMasterID=SalesMasterID,
                        BranchID=BranchID,
                        VoucherType="SI",
                    )
                    for ledgerPostInstance in ledgerPostInstances:
                        LedgerPostingID = ledgerPostInstance.LedgerPostingID
                        VoucherType = ledgerPostInstance.VoucherType
                        VoucherNo = ledgerPostInstance.VoucherNo
                        Debit = ledgerPostInstance.Debit
                        Credit = ledgerPostInstance.Credit
                        IsActive = ledgerPostInstance.IsActive
                        Date = ledgerPostInstance.Date
                        LedgerID = ledgerPostInstance.LedgerID
                        RelatedLedgerID = ledgerPostInstance.RelatedLedgerID

                        table.LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=LedgerID,
                            RelatedLedgerID=RelatedLedgerID,
                            Credit=Credit,
                            Debit=Debit,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        ledgerPostInstance.delete()

                if table.StockPosting.objects.filter(
                    CompanyID=CompanyID,
                    VoucherMasterID=SalesMasterID,
                    BranchID=BranchID,
                    VoucherType="SI",
                ).exists():
                    stockPostingInstances = table.StockPosting.objects.filter(
                        CompanyID=CompanyID,
                        VoucherMasterID=SalesMasterID,
                        BranchID=BranchID,
                        VoucherType="SI",
                    )
                    for stockPostingInstance in stockPostingInstances:
                        StockPostingID = stockPostingInstance.StockPostingID
                        BranchID = stockPostingInstance.BranchID
                        Date = stockPostingInstance.Date
                        VoucherMasterID = stockPostingInstance.VoucherMasterID
                        VoucherDetailID = stockPostingInstance.VoucherDetailID
                        VoucherType = stockPostingInstance.VoucherType
                        ProductID = stockPostingInstance.ProductID
                        BatchID = stockPostingInstance.BatchID
                        WareHouseID = stockPostingInstance.WareHouseID
                        QtyIn = stockPostingInstance.QtyIn
                        QtyOut = stockPostingInstance.QtyOut
                        Rate = stockPostingInstance.Rate
                        PriceListID = stockPostingInstance.PriceListID
                        IsActive = stockPostingInstance.IsActive

                        table.StockPosting_Log.objects.create(
                            TransactionID=StockPostingID,
                            BranchID=BranchID,
                            Action=Action,
                            Date=Date,
                            VoucherMasterID=VoucherMasterID,
                            VoucherDetailID=VoucherDetailID,
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

                        update_stock(CompanyID, BranchID, ProductID)

                detail_instances = table.SalesDetails.objects.filter(
                    CompanyID=CompanyID, SalesMasterID=SalesMasterID, BranchID=BranchID
                )

                for detail_instance in detail_instances:
                    SalesDetailsID = detail_instance.SalesDetailsID
                    BranchID = detail_instance.BranchID
                    SalesMasterID = detail_instance.SalesMasterID
                    ProductID = detail_instance.ProductID
                    Qty = detail_instance.Qty
                    FreeQty = detail_instance.FreeQty
                    UnitPrice = detail_instance.UnitPrice
                    InclusivePrice = detail_instance.InclusivePrice
                    RateWithTax = detail_instance.RateWithTax
                    CostPerPrice = detail_instance.CostPerPrice
                    PriceListID = detail_instance.PriceListID
                    DiscountPerc = detail_instance.DiscountPerc
                    DiscountAmount = detail_instance.DiscountAmount
                    AddlDiscPerc = detail_instance.AddlDiscPerc
                    AddlDiscAmt = detail_instance.AddlDiscAmt
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
                    TAX1Perc = detail_instance.TAX1Perc
                    TAX1Amount = detail_instance.TAX1Amount
                    TAX2Perc = detail_instance.TAX2Perc
                    TAX2Amount = detail_instance.TAX2Amount
                    TAX3Perc = detail_instance.TAX3Perc
                    TAX3Amount = detail_instance.TAX3Amount
                    BatchCode = detail_instance.BatchCode
                    Description = detail_instance.Description
                    KFCAmount = detail_instance.KFCAmount
                    KFCPerc = detail_instance.KFCPerc
                    ProductTaxID = detail_instance.ProductTaxID

                    update_stock(CompanyID, BranchID, ProductID)

                    if table.Batch.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode
                    ).exists():
                        batch_ins = table.Batch.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode
                        )
                        MultiFactor = table.PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=PriceListID
                        ).MultiFactor
                        if not Qty:
                            Qty = 0
                        if not FreeQty:
                            FreeQty = 0
                        qty_batch = converted_float(
                            FreeQty) + converted_float(Qty)
                        Qty_batch = converted_float(
                            MultiFactor) * converted_float(qty_batch)
                        StockOut = batch_ins.StockOut
                        batch_ins.StockOut = converted_float(
                            StockOut) - converted_float(Qty_batch)
                        batch_ins.save()

                    if table.SerialNumbers.objects.filter(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        SalesMasterID=SalesMasterID,
                        SalesDetailsID=SalesDetailsID,
                        VoucherType="SI",
                    ).exists():
                        serial_instances = table.SerialNumbers.objects.filter(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            SalesMasterID=SalesMasterID,
                            SalesDetailsID=SalesDetailsID,
                            VoucherType="SI",
                        )
                        for sir in serial_instances:
                            sir.delete()

                    table.SalesDetails_Log.objects.create(
                        TransactionID=SalesDetailsID,
                        BranchID=BranchID,
                        Action=Action,
                        SalesMasterID=SalesMasterID,
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
                        AddlDiscPerc=AddlDiscPerc,
                        AddlDiscAmt=AddlDiscAmt,
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
                        UpdatedUserID=CreatedUserID,
                        Flavour=Flavour,
                        TAX1Perc=TAX1Perc,
                        TAX1Amount=TAX1Amount,
                        TAX2Perc=TAX2Perc,
                        TAX2Amount=TAX2Amount,
                        TAX3Perc=TAX3Perc,
                        TAX3Amount=TAX3Amount,
                        CompanyID=CompanyID,
                        BatchCode=BatchCode,
                        Description=Description,
                        KFCAmount=KFCAmount,
                        KFCPerc=KFCPerc,
                        ProductTaxID=ProductTaxID,
                    )
                    # =========Loyalty Point ==========
                    tot_Points = 0
                    if table.LoyaltyPoint.objects.filter(
                        LoyaltyCustomerID=LoyaltyCustomerID,
                        VoucherMasterID=SalesMasterID,
                        VoucherType="SI",
                        BranchID=BranchID,
                        CompanyID=CompanyID,
                    ).exists():
                        instances = table.LoyaltyPoint.objects.filter(
                            LoyaltyCustomerID=LoyaltyCustomerID,
                            VoucherMasterID=SalesMasterID,
                            VoucherType="SI",
                            BranchID=BranchID,
                            CompanyID=CompanyID,
                        )
                        for i in instances:
                            if i.is_Radeem == False:
                                tot_Points += converted_float(i.Point)
                            i.delete()
                        instances1 = table.LoyaltyPoint.objects.filter(
                            LoyaltyCustomerID=LoyaltyCustomerID,
                            VoucherMasterID=SalesMasterID,
                            VoucherType="SI",
                            BranchID=BranchID,
                            CompanyID=CompanyID,
                            is_Radeem=False,
                        )

                    detail_instance.delete()
                instance.delete()

        # request , company, log_type, user, source, action, message, description
        activity_log(
            request._request,
            CompanyID,
            "Information",
            CreatedUserID,
            "Sales Invoice",
            "Deleted",
            "Sales Invoice Deleted successfully.",
            "Sales Invoice Deleted successfully",
        )

        response_data = {
            "StatusCode": 6000,
            "title": "Success",
            "message": "Sales Invoice Deleted Successfully!",
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "title": "Failed",
            "message": "Sales Invoice Not Found!",
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def salesApp_create_salesReturn(request):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data["CompanyID"]
            CompanyID = get_company(CompanyID)
            CreatedUserID = data["CreatedUserID"]
            PriceRounding = data["PriceRounding"]

            today = datetime.datetime.now()
            BranchID = data["BranchID"]
            VoucherDate = data["VoucherDate"]
            VoucherNo = data["VoucherNo"]
            RefferenceBillNo = data["RefferenceBillNo"]
            RefferenceBillDate = data["RefferenceBillDate"]
            CreditPeriod = data["CreditPeriod"]
            LedgerID = data["LedgerID"]
            PriceCategoryID = data["PriceCategoryID"]
            EmployeeID = data["EmployeeID"]
            SalesAccount = data["SalesAccount"]
            DeliveryMasterID = data["DeliveryMasterID"]
            OrderMasterID = data["OrderMasterID"]
            CustomerName = data["CustomerName"]
            Address1 = data["Address1"]
            Address2 = data["Address2"]
            Address3 = data["Address3"]
            Notes = data["Notes"]
            FinacialYearID = data["FinacialYearID"]
            WarehouseID = data["WarehouseID"]
            TableID = data["TableID"]
            SeatNumber = data["SeatNumber"]
            NoOfGuests = data["NoOfGuests"]
            INOUT = data["INOUT"]
            TokenNumber = data["TokenNumber"]
            IsActive = data["IsActive"]
            IsPosted = data["IsPosted"]
            SalesType = data["SalesType"]
            BatchID = data["BatchID"]
            try:
                TaxID = data["TaxID"]
            except:
                TaxID = 1
            try:
                TaxType = data["TaxType"]
            except:
                TaxType = ""
            # CashAmount = data['CashAmount']

            TotalGrossAmt = converted_float(data["TotalGrossAmt"])
            TotalTax = converted_float(data["TotalTax"])
            NetTotal = converted_float(data["NetTotal"])
            AdditionalCost = converted_float(data["AdditionalCost"])
            GrandTotal = converted_float(data["GrandTotal"])
            RoundOff = converted_float(data["RoundOff"])
            CashReceived = converted_float(data["CashReceived"])
            BankAmount = converted_float(data["BankAmount"])
            VATAmount = converted_float(data["VATAmount"])
            SGSTAmount = converted_float(data["SGSTAmount"])
            CGSTAmount = converted_float(data["CGSTAmount"])
            IGSTAmount = converted_float(data["IGSTAmount"])
            TAX1Amount = converted_float(data["TAX1Amount"])
            TAX2Amount = converted_float(data["TAX2Amount"])
            TAX3Amount = converted_float(data["TAX3Amount"])
            AddlDiscPercent = converted_float(data["AddlDiscPercent"])
            AddlDiscAmt = converted_float(data["AddlDiscAmt"])
            TotalDiscount = converted_float(data["TotalDiscount"])
            BillDiscPercent = converted_float(data["BillDiscPercent"])
            BillDiscAmt = converted_float(data["BillDiscAmt"])
            try:
                TaxTaxableAmount = converted_float(data["TaxTaxableAmount"])
            except:
                TaxTaxableAmount = 0
            try:
                NonTaxTaxableAmount = converted_float(
                    data["NonTaxTaxableAmount"])
            except:
                NonTaxTaxableAmount = 0
            try:
                KFCAmount = converted_float(data["KFCAmount"])
            except:
                KFCAmount = 0

            salesReturnDetails = data["SalesReturnDetails"]
            TotalTaxableAmount = 0
            for salesReturnDetail in salesReturnDetails:
                TaxableAmount = salesReturnDetail["TaxableAmount"]
                TotalTaxableAmount += converted_float(TaxableAmount)

            Action = "A"

            try:
                Country_of_Supply = data["Country_of_Supply"]
            except:
                Country_of_Supply = ""

            try:
                State_of_Supply = data["State_of_Supply"]
            except:
                State_of_Supply = ""

            try:
                GST_Treatment = data["GST_Treatment"]
            except:
                GST_Treatment = ""

            try:
                VAT_Treatment = data["VAT_Treatment"]
            except:
                VAT_Treatment = ""

            VoucherType = "SR"

            # VoucherNo Updated
            try:
                PreFix = data["PreFix"]
            except:
                PreFix = "SR"

            try:
                Seperator = data["Seperator"]
            except:
                Seperator = ""

            try:
                InvoiceNo = data["InvoiceNo"]
            except:
                InvoiceNo = 1

            try:
                BillingAddress = data["BillingAddress"]
            except:
                BillingAddress = None

            if BillingAddress:
                if table.UserAdrress.objects.filter(id=BillingAddress).exists():
                    BillingAddress = table.UserAdrress.objects.get(
                        id=BillingAddress)
                else:
                    BillingAddress = None

            # checking voucher number already exist
            VoucherNoLow = VoucherNo.lower()
            is_voucherExist = False
            insts = table.SalesReturnMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID
            )
            if insts:
                for i in insts:
                    voucher_no = i.VoucherNo
                    voucherNo = voucher_no.lower()
                    if VoucherNoLow == voucherNo:
                        is_voucherExist = True

            check_VoucherNoAutoGenerate = False
            is_SalesReturnOK = True

            if table.GeneralSettings.objects.filter(
                CompanyID=CompanyID,
                BranchID=BranchID,
                SettingsType="VoucherNoAutoGenerate",
            ).exists():
                check_VoucherNoAutoGenerate = table.GeneralSettings.objects.get(
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    SettingsType="VoucherNoAutoGenerate",
                ).SettingsValue

            if is_voucherExist == True and check_VoucherNoAutoGenerate == "True":
                VoucherNo = get_Genrate_VoucherNo(
                    table.SalesReturnMaster, BranchID, CompanyID, "SR"
                )
                is_SalesReturnOK = True
            elif is_voucherExist == False:
                is_SalesReturnOK = True
            else:
                is_SalesReturnOK = False

            if is_SalesReturnOK:

                SalesReturnMasterID = salesReturnMasterid(
                    table.SalesReturnMaster, BranchID, CompanyID
                )

                CashAmount = converted_float(
                    GrandTotal) - converted_float(BankAmount)

                LoyaltyCustomerID = data["LoyaltyCustomerID"]

                loyalty_customer = None
                is_LoyaltyCustomer = False
                if LoyaltyCustomerID:
                    if table.LoyaltyCustomer.objects.filter(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        LoyaltyCustomerID=LoyaltyCustomerID,
                    ).exists():
                        loyalty_customer = table.LoyaltyCustomer.objects.get(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            LoyaltyCustomerID=LoyaltyCustomerID,
                        )
                        is_LoyaltyCustomer = True

                update_voucher_table(
                    CompanyID, CreatedUserID, VoucherType, PreFix, Seperator, InvoiceNo
                )

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
                    UpdatedUserID=CreatedUserID,
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
                    TaxTaxableAmount=TaxTaxableAmount,
                    NonTaxTaxableAmount=NonTaxTaxableAmount,
                    BillingAddress=BillingAddress,
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
                    UpdatedUserID=CreatedUserID,
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
                    TaxTaxableAmount=TaxTaxableAmount,
                    NonTaxTaxableAmount=NonTaxTaxableAmount,
                    BillingAddress=BillingAddress,
                )

                # ======QRCODE==========
                # url = request.META['HTTP_ORIGIN'] + "/invoice/" + str(sales_return_instance.pk)+str('/')+ str('SR')
                # url = str("http://localhost:3000/invoice/") + str(sales_return_instance.pk)+str('/')+ str('SR')
                if CompanyID.is_vat and CompanyID.VATNumber:
                    tax_number = CompanyID.VATNumber
                elif CompanyID.is_gst and CompanyID.GSTNumber:
                    tax_number = CompanyID.GSTNumber
                else:
                    tax_number = ""

                invoice_date = sales_return_instance.CreatedDate.strftime(
                    "%d-%b-%y %I:%M:%S %p"
                )
                fatoora_obj = Fatoora(
                    seller_name=CompanyID.CompanyName,
                    tax_number=tax_number,  # or "1234567891"
                    invoice_date=str(
                        sales_return_instance.CreatedDate),  # Timestamp
                    total_amount=GrandTotal,  # or 100.0, 100.00, "100.0", "100.00"
                    tax_amount=TotalTax,  # or 15.0, 15.00, "15.0", "15.00"
                )
                url = fatoora_obj.base64

                qr_instance = table.QrCode.objects.create(
                    voucher_type="SR",
                    master_id=sales_return_instance.pk,
                    url=url,
                )

                # ======END============
                # billwise table insertion
                handleBillwiseChanges(CompanyID,BranchID,CashReceived,BankAmount,GrandTotal,LedgerID,VoucherNo,VoucherType,"create",CreditPeriod,SalesReturnMasterID,VoucherDate)
                # enable_billwise = get_GeneralSettings(
                #     CompanyID, BranchID, "EnableBillwise")
                # total_amount_received = converted_float(
                #     CashReceived) + converted_float(BankAmount)
                # if enable_billwise and converted_float(total_amount_received) < converted_float(GrandTotal) and table.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder__in=[10, 29]).exists():
                #     BillwiseMasterID = get_BillwiseMasterID(
                #         BranchID, CompanyID)
                #     DueDate = get_nth_day_date(CreditPeriod)
                #     table.BillWiseMaster.objects.create(
                #         CompanyID=CompanyID,
                #         BranchID=BranchID,
                #         BillwiseMasterID=BillwiseMasterID,
                #         InvoiceNo=VoucherNo,
                #         TransactionID=SalesReturnMasterID,
                #         VoucherType=VoucherType,
                #         VoucherDate=VoucherDate,
                #         InvoiceAmount=GrandTotal,
                #         Payments=total_amount_received,
                #         DueDate=DueDate,
                #         CustomerID=LedgerID
                #     )

                # =====================Loyal Custpmer Point=====================
                is_MinimumSalePrice = data["is_Loyalty_SalesReturn_MinimumSalePrice"]
                today_date = datetime.datetime.now().date()
                print(is_LoyaltyCustomer, "is_LoyaltyCustomeris_LoyaltyCustomer")
                if is_LoyaltyCustomer:
                    if table.LoyaltyProgram.objects.filter(
                        BranchID=BranchID,
                        CompanyID=CompanyID,
                        FromDate__lte=today_date,
                        ToDate__gte=today_date,
                    ).exists():
                        instance = table.LoyaltyProgram.objects.get(
                            BranchID=BranchID,
                            CompanyID=CompanyID,
                            FromDate__lte=today_date,
                            ToDate__gte=today_date,
                        )
                        print(instance.ProductType)
                        return_point = 0
                        tot_taxable_amnt = 0
                        salesReturnDetails = data["SalesReturnDetails"]
                        for salesReturnDetail in salesReturnDetails:
                            product_id = salesReturnDetail["ProductID"]
                            print(salesReturnDetail["ProductID"], "uvaissss")
                            TaxableAmount = salesReturnDetail["TaxableAmount"]
                            single_product_point = sales_return_point(
                                instance,
                                product_id,
                                TaxableAmount,
                                BranchID,
                                CompanyID,
                                is_MinimumSalePrice,
                            )
                            tot_taxable_amnt += single_product_point

                        actual_point = get_actual_point(
                            tot_taxable_amnt, instance)
                        print(
                            loyalty_customer,
                            tot_taxable_amnt,
                            "tot_TaxableAmount actual_point",
                            actual_point,
                        )
                        CurrentPoint = 0
                        loyalty_instance = table.LoyaltyCustomer.objects.get(
                            BranchID=BranchID,
                            CompanyID=CompanyID,
                            LoyaltyCustomerID=loyalty_customer.LoyaltyCustomerID,
                        )
                        l_instances = table.LoyaltyPoint.objects.filter(
                            LoyaltyCustomerID__id=loyalty_instance.pk,
                            BranchID=BranchID,
                            CompanyID=CompanyID,
                        )
                        for i in l_instances:
                            CurrentPoint += converted_float(i.Point)
                        if converted_float(CurrentPoint) >= converted_float(actual_point):
                            return_point = converted_float(
                                CurrentPoint) - converted_float(actual_point)
                            loyalty_customer.CurrentPoint = return_point
                            loyalty_customer.save()
                            if actual_point:
                                LoyaltyPointID = get_point_auto_id(
                                    table.LoyaltyPoint, BranchID, CompanyID
                                )
                                ExpiryDate = None
                                table.LoyaltyPoint.objects.create(
                                    BranchID=BranchID,
                                    LoyaltyPointID=LoyaltyPointID,
                                    Value=actual_point * -1,
                                    VoucherType=VoucherType,
                                    VoucherMasterID=SalesReturnMasterID,
                                    Point=actual_point * -1,
                                    ExpiryDate=ExpiryDate,
                                    LoyaltyCustomerID=loyalty_customer,
                                    LoyaltyProgramID=instance,
                                    is_Radeem=False,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    Action=Action,
                                    CreatedUserID=CreatedUserID,
                                    CompanyID=CompanyID,
                                )
                                table.LoyaltyPoint_Log.objects.create(
                                    BranchID=BranchID,
                                    LoyaltyPointID=LoyaltyPointID,
                                    Value=actual_point * -1,
                                    VoucherType=VoucherType,
                                    VoucherMasterID=SalesReturnMasterID,
                                    Point=actual_point * -1,
                                    ExpiryDate=ExpiryDate,
                                    LoyaltyCustomerID=loyalty_customer,
                                    LoyaltyProgramID=instance,
                                    is_Radeem=False,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    Action=Action,
                                    CreatedUserID=CreatedUserID,
                                    CompanyID=CompanyID,
                                )

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID
                )

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
                    CompanyID,
                    BranchID,
                    SalesAccount,
                    SalesReturnMasterID,
                    VoucherType,
                    GrandTotal,
                    "Dr",
                    "create",
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID
                )

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
                    CompanyID,
                    BranchID,
                    LedgerID,
                    SalesReturnMasterID,
                    VoucherType,
                    GrandTotal,
                    "Cr",
                    "create",
                )

                if TaxType == "VAT":
                    if converted_float(VATAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID
                        )

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
                            CompanyID,
                            BranchID,
                            55,
                            SalesReturnMasterID,
                            VoucherType,
                            VATAmount,
                            "Dr",
                            "create",
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID
                        )

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
                            CompanyID,
                            BranchID,
                            SalesAccount,
                            SalesReturnMasterID,
                            VoucherType,
                            VATAmount,
                            "Cr",
                            "create",
                        )
                # new posting ending  here

                elif (
                    TaxType == "GST Intra-state B2B" or TaxType == "GST Intra-state B2C"
                ):
                    if converted_float(CGSTAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID
                        )

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
                            CompanyID,
                            BranchID,
                            3,
                            SalesReturnMasterID,
                            VoucherType,
                            CGSTAmount,
                            "Dr",
                            "create",
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID
                        )

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
                            CompanyID,
                            BranchID,
                            SalesAccount,
                            SalesReturnMasterID,
                            VoucherType,
                            CGSTAmount,
                            "Cr",
                            "create",
                        )

                    if converted_float(SGSTAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID
                        )

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
                            CompanyID,
                            BranchID,
                            10,
                            SalesReturnMasterID,
                            VoucherType,
                            SGSTAmount,
                            "Dr",
                            "create",
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID
                        )

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
                            CompanyID,
                            BranchID,
                            SalesAccount,
                            SalesReturnMasterID,
                            VoucherType,
                            SGSTAmount,
                            "Cr",
                            "create",
                        )

                    if converted_float(KFCAmount) > 0:

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID
                        )

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
                            CompanyID,
                            BranchID,
                            93,
                            SalesReturnMasterID,
                            VoucherType,
                            KFCAmount,
                            "Dr",
                            "create",
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID
                        )

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
                            CompanyID,
                            BranchID,
                            SalesAccount,
                            SalesReturnMasterID,
                            VoucherType,
                            KFCAmount,
                            "Cr",
                            "create",
                        )

                elif (
                    TaxType == "GST Inter-state B2B" or TaxType == "GST Inter-state B2C"
                ):
                    if converted_float(IGSTAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID
                        )

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
                            CompanyID,
                            BranchID,
                            17,
                            SalesReturnMasterID,
                            VoucherType,
                            IGSTAmount,
                            "Dr",
                            "create",
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID
                        )

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
                            CompanyID,
                            BranchID,
                            SalesAccount,
                            SalesReturnMasterID,
                            VoucherType,
                            IGSTAmount,
                            "Cr",
                            "create",
                        )

                if not TaxType == "Export":
                    if converted_float(TAX1Amount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID
                        )
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
                            CompanyID,
                            BranchID,
                            16,
                            SalesReturnMasterID,
                            VoucherType,
                            TAX1Amount,
                            "Dr",
                            "create",
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID
                        )
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
                            CompanyID,
                            BranchID,
                            SalesAccount,
                            SalesReturnMasterID,
                            VoucherType,
                            TAX1Amount,
                            "Cr",
                            "create",
                        )

                    if converted_float(TAX2Amount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID
                        )
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
                            CompanyID,
                            BranchID,
                            19,
                            SalesReturnMasterID,
                            VoucherType,
                            TAX2Amount,
                            "Dr",
                            "create",
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID
                        )
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
                            CompanyID,
                            BranchID,
                            SalesAccount,
                            SalesReturnMasterID,
                            VoucherType,
                            TAX2Amount,
                            "Cr",
                            "create",
                        )

                    if converted_float(TAX3Amount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID
                        )
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
                            CompanyID,
                            BranchID,
                            22,
                            SalesReturnMasterID,
                            VoucherType,
                            TAX3Amount,
                            "Dr",
                            "create",
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID
                        )
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
                            CompanyID,
                            BranchID,
                            SalesAccount,
                            SalesReturnMasterID,
                            VoucherType,
                            TAX3Amount,
                            "Cr",
                            "create",
                        )

                if converted_float(RoundOff) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

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
                        CompanyID,
                        BranchID,
                        78,
                        SalesReturnMasterID,
                        VoucherType,
                        RoundOff,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

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
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        RoundOff,
                        "Cr",
                        "create",
                    )

                if converted_float(RoundOff) < 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

                    RoundOff = abs(converted_float(RoundOff))

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
                        CompanyID,
                        BranchID,
                        78,
                        SalesReturnMasterID,
                        VoucherType,
                        RoundOff,
                        "Cr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

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
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        RoundOff,
                        "Dr",
                        "create",
                    )

                if converted_float(TotalDiscount) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

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
                        CompanyID,
                        BranchID,
                        74,
                        SalesReturnMasterID,
                        VoucherType,
                        TotalDiscount,
                        "Cr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

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
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        TotalDiscount,
                        "Dr",
                        "create",
                    )

                salesReturnDetails = data["SalesReturnDetails"]
                for salesReturnDetail in salesReturnDetails:
                    ProductID = salesReturnDetail["ProductID"]
                    if ProductID:
                        # SalesReturnMasterID = serialized.data['SalesReturnMasterID']
                        DeliveryDetailsID = salesReturnDetail["DeliveryDetailsID"]
                        OrderDetailsID = salesReturnDetail["OrderDetailsID"]
                        Qty = salesReturnDetail["Qty"]
                        FreeQty = salesReturnDetail["FreeQty"]
                        Flavour = salesReturnDetail["Flavour"]

                        UnitPrice = converted_float(
                            salesReturnDetail["UnitPrice"])
                        InclusivePrice = converted_float(
                            salesReturnDetail["InclusivePrice"])
                        RateWithTax = converted_float(
                            salesReturnDetail["RateWithTax"])
                        # CostPerPrice = converted_float(salesReturnDetail['CostPerPrice'])
                        PriceListID = salesReturnDetail["PriceListID"]
                        DiscountPerc = converted_float(
                            salesReturnDetail["DiscountPerc"])
                        DiscountAmount = converted_float(
                            salesReturnDetail["DiscountAmount"])
                        GrossAmount = converted_float(
                            salesReturnDetail["GrossAmount"])
                        TaxableAmount = converted_float(
                            salesReturnDetail["TaxableAmount"])
                        VATPerc = converted_float(salesReturnDetail["VATPerc"])
                        VATAmount = converted_float(
                            salesReturnDetail["VATAmount"])
                        SGSTPerc = converted_float(
                            salesReturnDetail["SGSTPerc"])
                        SGSTAmount = converted_float(
                            salesReturnDetail["SGSTAmount"])
                        CGSTPerc = converted_float(
                            salesReturnDetail["CGSTPerc"])
                        CGSTAmount = converted_float(
                            salesReturnDetail["CGSTAmount"])
                        IGSTPerc = converted_float(
                            salesReturnDetail["IGSTPerc"])
                        IGSTAmount = converted_float(
                            salesReturnDetail["IGSTAmount"])
                        NetAmount = converted_float(
                            salesReturnDetail["NetAmount"])
                        AddlDiscPercent = converted_float(
                            salesReturnDetail["AddlDiscPerc"])
                        AddlDiscAmt = converted_float(
                            salesReturnDetail["AddlDiscAmt"])
                        TAX1Perc = converted_float(
                            salesReturnDetail["TAX1Perc"])
                        TAX1Amount = converted_float(
                            salesReturnDetail["TAX1Amount"])
                        TAX2Perc = converted_float(
                            salesReturnDetail["TAX2Perc"])
                        TAX2Amount = converted_float(
                            salesReturnDetail["TAX2Amount"])
                        TAX3Perc = converted_float(
                            salesReturnDetail["TAX3Perc"])
                        TAX3Amount = converted_float(
                            salesReturnDetail["TAX3Amount"])
                        try:
                            KFCAmount = converted_float(
                                salesReturnDetail["KFCAmount"])
                        except:
                            KFCAmount = 0

                        try:
                            ProductTaxID = salesReturnDetail["ProductTaxID"]
                        except:
                            ProductTaxID = 1

                        CostPerPrice = table.PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=PriceListID
                        ).PurchasePrice

                        try:
                            SerialNos = salesReturnDetail["SerialNos"]
                        except:
                            SerialNos = []

                        try:
                            Description = salesReturnDetail["Description"]
                        except:
                            Description = ""
                        try:
                            KFCPerc = salesReturnDetail["KFCPerc"]
                        except:
                            KFCPerc = 0

                        # KFCPerc = round(KFCPerc, PriceRounding)

                        try:
                            BatchCode = salesReturnDetail["BatchCode"]
                        except:
                            BatchCode = 0
                        try:
                            is_inclusive = salesReturnDetail["is_inclusive"]
                        except:
                            is_inclusive = False

                        if is_inclusive == True:
                            Batch_salesPrice = InclusivePrice
                        else:
                            Batch_salesPrice = UnitPrice

                        product_is_Service = table.Product.objects.get(
                            CompanyID=CompanyID, ProductID=ProductID
                        ).is_Service

                        product_purchasePrice = table.PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=PriceListID
                        ).PurchasePrice
                        MultiFactor = table.PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=PriceListID
                        ).MultiFactor

                        qty_batch = converted_float(
                            FreeQty) + converted_float(Qty)
                        Qty_batch = converted_float(
                            MultiFactor) * converted_float(qty_batch)

                        check_AllowUpdateBatchPriceInSales = False
                        check_EnableProductBatchWise = False
                        if product_is_Service == False:
                            if table.GeneralSettings.objects.filter(
                                CompanyID=CompanyID,
                                BranchID=BranchID,
                                SettingsType="AllowUpdateBatchPriceInSales",
                            ).exists():
                                check_AllowUpdateBatchPriceInSales = (
                                    table.GeneralSettings.objects.get(
                                        CompanyID=CompanyID,
                                        BranchID=BranchID,
                                        SettingsType="AllowUpdateBatchPriceInSales",
                                    ).SettingsValue
                                )

                            if table.GeneralSettings.objects.filter(
                                CompanyID=CompanyID,
                                BranchID=BranchID,
                                SettingsType="EnableProductBatchWise",
                            ).exists():
                                check_EnableProductBatchWise = (
                                    table.GeneralSettings.objects.get(
                                        CompanyID=CompanyID,
                                        BranchID=BranchID,
                                        SettingsType="EnableProductBatchWise",
                                    ).SettingsValue
                                )

                            if (
                                check_EnableProductBatchWise == True
                                or check_EnableProductBatchWise == "True"
                            ):
                                setbach = SetBatchInSales(
                                    CompanyID,
                                    BranchID,
                                    Batch_salesPrice,
                                    Qty_batch,
                                    BatchCode,
                                    check_AllowUpdateBatchPriceInSales,
                                    PriceListID,
                                    "SR",
                                )

                        SalesReturnQty = Qty
                        SalesReturnDetailsID = salesReturnDetailID(
                            table.SalesReturnDetails, BranchID, CompanyID
                        )

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
                            UpdatedUserID=CreatedUserID,
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
                            ProductTaxID=ProductTaxID,
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
                            UpdatedUserID=CreatedUserID,
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
                            ProductTaxID=ProductTaxID,
                        )

                        MultiFactor = table.PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=PriceListID
                        ).MultiFactor
                        PriceListID = table.PriceList.objects.get(
                            CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True
                        ).PriceListID

                        qty = converted_float(FreeQty) + converted_float(Qty)

                        Qty = converted_float(
                            MultiFactor) * converted_float(qty)
                        Cost = converted_float(
                            CostPerPrice) / converted_float(MultiFactor)

                        princeList_instance = table.PriceList.objects.get(
                            CompanyID=CompanyID,
                            ProductID=ProductID,
                            PriceListID=PriceListID,
                        )
                        PurchasePrice = princeList_instance.PurchasePrice
                        SalesPrice = princeList_instance.SalesPrice

                        if product_is_Service == False:
                            StockPostingID = get_auto_stockPostid(
                                table.StockPosting, BranchID, CompanyID
                            )

                            pricelist, warehouse = get_ModelInstance(
                                CompanyID, BranchID, PriceListID, WarehouseID
                            )

                            table.StockPosting.objects.create(
                                StockPostingID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=VoucherDate,
                                VoucherMasterID=SalesReturnMasterID,
                                VoucherDetailID=SalesReturnDetailsID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                BatchID=BatchCode,
                                WareHouseID=WarehouseID,
                                QtyIn=Qty,
                                Rate=Cost,
                                PriceListID=PriceListID,
                                IsActive=IsActive,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                                pricelist=pricelist,
                                warehouse=warehouse,
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
                                BatchID=BatchCode,
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

                        if table.SalesMaster.objects.filter(
                            CompanyID=CompanyID,
                            VoucherNo=RefferenceBillNo,
                            BranchID=BranchID,
                        ).exists():
                            SalesMaster_instance = table.SalesMaster.objects.get(
                                CompanyID=CompanyID,
                                VoucherNo=RefferenceBillNo,
                                BranchID=BranchID,
                            )
                            SalesMasterID = SalesMaster_instance.SalesMasterID

                            if table.SalesDetails.objects.filter(
                                CompanyID=CompanyID,
                                SalesMasterID=SalesMasterID,
                                BranchID=BranchID,
                                ProductID=ProductID,
                            ).exists():
                                SalesDetails_instances = table.SalesDetails.objects.filter(
                                    CompanyID=CompanyID,
                                    SalesMasterID=SalesMasterID,
                                    BranchID=BranchID,
                                    ProductID=ProductID,
                                )

                                for i in SalesDetails_instances:
                                    ReturnQty = i.ReturnQty
                                    SalesReturnQty = SalesReturnQty
                                    ReturnQty = converted_float(
                                        ReturnQty) - converted_float(SalesReturnQty)
                                    i.ReturnQty = ReturnQty

                                    i.save()

                # request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sales Return',
                #              'Create', 'Sales Return created successfully.', 'Sales Return saved successfully.')
                cash_Balance = get_LedgerBalance(CompanyID, 1)
                response_data = {
                    "StatusCode": 6000,
                    "id": sales_return_instance.id,
                    "qr_url": qr_instance.qr_code.url,
                    "message": "Sales Return created Successfully!!!",
                    "CashBalance": cash_Balance
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                # request , company, log_type, user, source, action, message, description
                activity_log(
                    request._request,
                    CompanyID,
                    "Warning",
                    CreatedUserID,
                    "Sales Return",
                    "Create",
                    "Sales Return created Failed.",
                    "VoucherNo already exist",
                )

                response_data = {
                    "StatusCode": 6001,
                    "message": "VoucherNo already exist.Please Change Your Prefix!",
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
            "Sales Return",
            "Create",
            str(e),
            err_descrb,
        )
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def salesApp_edit_salesReturn(request, pk):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data["CompanyID"]
            CompanyID = get_company(CompanyID)
            PriceRounding = data["PriceRounding"]
            CreatedUserID = data["CreatedUserID"]

            today = datetime.datetime.now()
            salesReturnkMaster_instance = None
            salesReturnDetails = None
            salesReturnkMaster_instance = table.SalesReturnMaster.objects.get(
                CompanyID=CompanyID, pk=pk
            )
            SalesReturnMasterID = salesReturnkMaster_instance.SalesReturnMasterID
            BranchID = salesReturnkMaster_instance.BranchID
            VoucherNo = salesReturnkMaster_instance.VoucherNo

            Action = "M"

            if table.SalesReturnDetails.objects.filter(
                CompanyID=CompanyID,
                BranchID=BranchID,
                SalesReturnMasterID=SalesReturnMasterID,
            ).exists():
                sale_ins = table.SalesReturnDetails.objects.filter(
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    SalesReturnMasterID=SalesReturnMasterID,
                )
                for i in sale_ins:
                    BatchCode = i.BatchCode
                    Qty = i.Qty
                    instance_MultiFactor = table.PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=i.PriceListID
                    ).MultiFactor

                    instance_qty_sum = converted_float(
                        i.FreeQty) + converted_float(i.Qty)
                    instance_Qty = converted_float(
                        instance_MultiFactor) * converted_float(instance_qty_sum)
                    if table.Batch.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode
                    ).exists():
                        batch_ins = table.Batch.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode
                        )
                        StockIn = batch_ins.StockIn
                        batch_ins.StockIn = converted_float(
                            StockIn) - converted_float(instance_Qty)
                        batch_ins.save()

                    if not table.StockPosting.objects.filter(
                        CompanyID=CompanyID,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherDetailID=i.SalesReturnDetailsID,
                        BranchID=BranchID,
                        VoucherType="SR",
                    ).exists():
                        table.StockPosting.objects.filter(
                            CompanyID=CompanyID,
                            VoucherMasterID=SalesReturnMasterID,
                            BranchID=BranchID,
                            VoucherType="SR",
                        ).delete()
                        update_stock(CompanyID, BranchID, i.ProductID)

                    if table.StockPosting.objects.filter(
                        CompanyID=CompanyID,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherDetailID=i.SalesReturnDetailsID,
                        ProductID=i.ProductID,
                        BranchID=BranchID,
                        VoucherType="SR",
                    ).exists():
                        stock_inst = table.StockPosting.objects.filter(
                            CompanyID=CompanyID,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherDetailID=i.SalesReturnDetailsID,
                            ProductID=i.ProductID,
                            BranchID=BranchID,
                            VoucherType="SR",
                        ).first()
                        stock_inst.QtyIn = converted_float(
                            stock_inst.QtyIn) - converted_float(instance_Qty)
                        stock_inst.save()
                        update_stock(CompanyID, BranchID, i.ProductID)

            data = request.data

            VoucherDate = data["VoucherDate"]
            RefferenceBillNo = data["RefferenceBillNo"]
            RefferenceBillDate = data["RefferenceBillDate"]
            CreditPeriod = data["CreditPeriod"]
            LedgerID = data["LedgerID"]
            PriceCategoryID = data["PriceCategoryID"]
            EmployeeID = data["EmployeeID"]
            SalesAccount = data["SalesAccount"]
            DeliveryMasterID = data["DeliveryMasterID"]
            OrderMasterID = data["OrderMasterID"]
            CustomerName = data["CustomerName"]
            Address1 = data["Address1"]
            Address2 = data["Address2"]
            Address3 = data["Address3"]
            Notes = data["Notes"]
            FinacialYearID = data["FinacialYearID"]
            WarehouseID = data["WarehouseID"]
            TableID = data["TableID"]
            SeatNumber = data["SeatNumber"]
            NoOfGuests = data["NoOfGuests"]
            INOUT = data["INOUT"]
            TokenNumber = data["TokenNumber"]
            IsActive = data["IsActive"]
            IsPosted = data["IsPosted"]
            SalesType = data["SalesType"]
            BatchID = data["BatchID"]
            try:
                TaxID = data["TaxID"]
            except:
                TaxID = 1
            try:
                TaxType = data["TaxType"]
            except:
                TaxType = ""

            TotalGrossAmt = converted_float(data["TotalGrossAmt"])
            TotalTax = converted_float(data["TotalTax"])
            NetTotal = converted_float(data["NetTotal"])
            AdditionalCost = converted_float(data["AdditionalCost"])
            GrandTotal = converted_float(data["GrandTotal"])
            RoundOff = converted_float(data["RoundOff"])
            CashReceived = converted_float(data["CashReceived"])
            BankAmount = converted_float(data["BankAmount"])
            VATAmount = converted_float(data["VATAmount"])
            SGSTAmount = converted_float(data["SGSTAmount"])
            CGSTAmount = converted_float(data["CGSTAmount"])
            IGSTAmount = converted_float(data["IGSTAmount"])
            TAX1Amount = converted_float(data["TAX1Amount"])
            TAX2Amount = converted_float(data["TAX2Amount"])
            TAX3Amount = converted_float(data["TAX3Amount"])
            AddlDiscPercent = converted_float(data["AddlDiscPercent"])
            AddlDiscAmt = converted_float(data["AddlDiscAmt"])
            TotalDiscount = converted_float(data["TotalDiscount"])
            BillDiscPercent = converted_float(data["BillDiscPercent"])
            BillDiscAmt = converted_float(data["BillDiscAmt"])

            try:
                KFCAmount = converted_float(data["KFCAmount"])
            except:
                KFCAmount = 0

            try:
                Country_of_Supply = data["Country_of_Supply"]
            except:
                Country_of_Supply = ""

            try:
                State_of_Supply = data["State_of_Supply"]
            except:
                State_of_Supply = ""

            try:
                GST_Treatment = data["GST_Treatment"]
            except:
                GST_Treatment = ""

            try:
                VAT_Treatment = data["VAT_Treatment"]
            except:
                VAT_Treatment = ""
            try:
                TaxTaxableAmount = converted_float(data["TaxTaxableAmount"])
            except:
                TaxTaxableAmount = 0
            try:
                NonTaxTaxableAmount = converted_float(
                    data["NonTaxTaxableAmount"])
            except:
                NonTaxTaxableAmount = 0

            try:
                BillingAddress = data["BillingAddress"]
            except:
                BillingAddress = None

            if BillingAddress:
                if table.UserAdrress.objects.filter(id=BillingAddress).exists():
                    BillingAddress = table.UserAdrress.objects.get(
                        id=BillingAddress)
                else:
                    BillingAddress = None

            CashAmount = converted_float(
                GrandTotal) - converted_float(BankAmount)

            TotalTaxableAmount = 0
            salesReturnDetails = data["SalesReturnDetails"]
            for salesReturnDetail in salesReturnDetails:
                TaxableAmount = salesReturnDetail["TaxableAmount"]
                TotalTaxableAmount += converted_float(TaxableAmount)

            update_ledger = UpdateLedgerBalance(
                CompanyID, BranchID, 0, SalesReturnMasterID, "SR", 0, "Cr", "update"
            )
            if table.LedgerPosting.objects.filter(
                CompanyID=CompanyID,
                VoucherMasterID=SalesReturnMasterID,
                BranchID=BranchID,
                VoucherType="SR",
            ).exists():
                ledgerPostInstances = table.LedgerPosting.objects.filter(
                    CompanyID=CompanyID,
                    VoucherMasterID=SalesReturnMasterID,
                    BranchID=BranchID,
                    VoucherType="SR",
                ).delete()

            table.SalesReturnMaster_Log.objects.create(
                TransactionID=SalesReturnMasterID,
                TotalTaxableAmount=TotalTaxableAmount,
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
                UpdatedUserID=CreatedUserID,
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
                TaxTaxableAmount=TaxTaxableAmount,
                NonTaxTaxableAmount=NonTaxTaxableAmount,
                BillingAddress=BillingAddress,
            )

            if table.SerialNumbers.objects.filter(
                CompanyID=CompanyID,
                SalesMasterID=SalesReturnMasterID,
                BranchID=BranchID,
                VoucherType="SR",
            ).exists():
                SerialNumbersInstances = table.SerialNumbers.objects.filter(
                    CompanyID=CompanyID,
                    SalesMasterID=SalesReturnMasterID,
                    BranchID=BranchID,
                    VoucherType="SR",
                )
                for sli in SerialNumbersInstances:
                    sli.delete()

            LoyaltyCustomerID = data["LoyaltyCustomerID"]

            loyalty_customer = None
            is_LoyaltyCustomer = False
            if LoyaltyCustomerID:
                if table.LoyaltyCustomer.objects.filter(
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    LoyaltyCustomerID=LoyaltyCustomerID,
                ).exists():
                    loyalty_customer = table.LoyaltyCustomer.objects.get(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        LoyaltyCustomerID=LoyaltyCustomerID,
                    )
                    is_LoyaltyCustomer = True

            salesReturnkMaster_instance.VoucherDate = VoucherDate
            salesReturnkMaster_instance.RefferenceBillNo = RefferenceBillNo
            salesReturnkMaster_instance.RefferenceBillDate = RefferenceBillDate
            salesReturnkMaster_instance.CreditPeriod = CreditPeriod
            salesReturnkMaster_instance.LedgerID = LedgerID
            salesReturnkMaster_instance.PriceCategoryID = PriceCategoryID
            salesReturnkMaster_instance.EmployeeID = EmployeeID
            salesReturnkMaster_instance.SalesAccount = SalesAccount
            salesReturnkMaster_instance.DeliveryMasterID = DeliveryMasterID
            salesReturnkMaster_instance.OrderMasterID = OrderMasterID
            salesReturnkMaster_instance.CustomerName = CustomerName
            salesReturnkMaster_instance.Address1 = Address1
            salesReturnkMaster_instance.Address2 = Address2
            salesReturnkMaster_instance.Address3 = Address3
            salesReturnkMaster_instance.Notes = Notes
            salesReturnkMaster_instance.FinacialYearID = FinacialYearID
            salesReturnkMaster_instance.TotalGrossAmt = TotalGrossAmt
            salesReturnkMaster_instance.TotalTax = TotalTax
            salesReturnkMaster_instance.NetTotal = NetTotal
            salesReturnkMaster_instance.AdditionalCost = AdditionalCost
            salesReturnkMaster_instance.GrandTotal = GrandTotal
            salesReturnkMaster_instance.RoundOff = RoundOff
            salesReturnkMaster_instance.CashReceived = CashReceived
            salesReturnkMaster_instance.CashAmount = CashAmount
            salesReturnkMaster_instance.BankAmount = BankAmount
            salesReturnkMaster_instance.WarehouseID = WarehouseID
            salesReturnkMaster_instance.TableID = TableID
            salesReturnkMaster_instance.SeatNumber = SeatNumber
            salesReturnkMaster_instance.NoOfGuests = NoOfGuests
            salesReturnkMaster_instance.INOUT = INOUT
            salesReturnkMaster_instance.TokenNumber = TokenNumber
            salesReturnkMaster_instance.IsActive = IsActive
            salesReturnkMaster_instance.IsPosted = IsPosted
            salesReturnkMaster_instance.SalesType = SalesType
            salesReturnkMaster_instance.Action = Action
            salesReturnkMaster_instance.UpdatedUserID = CreatedUserID
            salesReturnkMaster_instance.UpdatedDate = today
            salesReturnkMaster_instance.TaxID = TaxID
            salesReturnkMaster_instance.TaxType = TaxType
            salesReturnkMaster_instance.VATAmount = VATAmount
            salesReturnkMaster_instance.SGSTAmount = SGSTAmount
            salesReturnkMaster_instance.CGSTAmount = CGSTAmount
            salesReturnkMaster_instance.IGSTAmount = IGSTAmount
            salesReturnkMaster_instance.TAX1Amount = TAX1Amount
            salesReturnkMaster_instance.TAX2Amount = TAX2Amount
            salesReturnkMaster_instance.TAX3Amount = TAX3Amount
            salesReturnkMaster_instance.AddlDiscPercent = AddlDiscPercent
            salesReturnkMaster_instance.AddlDiscAmt = AddlDiscAmt
            salesReturnkMaster_instance.TotalDiscount = TotalDiscount
            salesReturnkMaster_instance.BillDiscPercent = BillDiscPercent
            salesReturnkMaster_instance.BillDiscAmt = BillDiscAmt
            salesReturnkMaster_instance.TotalTaxableAmount = TotalTaxableAmount
            salesReturnkMaster_instance.Country_of_Supply = Country_of_Supply
            salesReturnkMaster_instance.State_of_Supply = State_of_Supply
            salesReturnkMaster_instance.GST_Treatment = GST_Treatment
            salesReturnkMaster_instance.VAT_Treatment = VAT_Treatment
            salesReturnkMaster_instance.TaxTaxableAmount = TaxTaxableAmount
            salesReturnkMaster_instance.NonTaxTaxableAmount = NonTaxTaxableAmount
            if loyalty_customer:
                salesReturnkMaster_instance.LoyaltyCustomerID = loyalty_customer
            salesReturnkMaster_instance.KFCAmount = KFCAmount
            salesReturnkMaster_instance.BillingAddress = BillingAddress
            salesReturnkMaster_instance.save()

            # billwise table insertion
            VoucherType = "SR"
            handleBillwiseChanges(CompanyID, BranchID, CashReceived, BankAmount, GrandTotal,
                                  LedgerID, VoucherNo, VoucherType, "edit", CreditPeriod, SalesReturnMasterID, VoucherDate)
            # enable_billwise = get_GeneralSettings(
            #     CompanyID, BranchID, "EnableBillwise")
            # total_amount_received = converted_float(
            #     CashReceived) + converted_float(BankAmount)
            # if enable_billwise and converted_float(total_amount_received) < converted_float(GrandTotal) and table.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder__in=[10, 29]).exists():
            #     if table.BillWiseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, InvoiceNo=VoucherNo, VoucherType=VoucherType, CustomerID=LedgerID).exists():
            #         billwise_ins = table.BillWiseMaster.objects.filter(
            #             CompanyID=CompanyID, BranchID=BranchID, InvoiceNo=VoucherNo, VoucherType=VoucherType, CustomerID=LedgerID).first()
            #         billwise_ins.VoucherDate = VoucherDate
            #         billwise_ins.InvoiceAmount = GrandTotal
            #         billwise_ins.Payments = total_amount_received
            #         billwise_ins.save()
            #     elif table.BillWiseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, InvoiceNo=VoucherNo, VoucherType=VoucherType).exists():
            #         billwise_ins = table.BillWiseMaster.objects.filter(
            #             CompanyID=CompanyID, BranchID=BranchID, InvoiceNo=VoucherNo, VoucherType=VoucherType).first()
            #         billwise_ins.VoucherDate = VoucherDate
            #         billwise_ins.InvoiceAmount = GrandTotal
            #         billwise_ins.Payments = total_amount_received
            #         billwise_ins.CustomerID = LedgerID
            #         billwise_ins.save()
            #     else:
            #         BillwiseMasterID = get_BillwiseMasterID(
            #             BranchID, CompanyID)
            #         DueDate = get_nth_day_date(CreditPeriod)
            #         table.BillWiseMaster.objects.create(
            #             CompanyID=CompanyID,
            #             BranchID=BranchID,
            #             BillwiseMasterID=BillwiseMasterID,
            #             InvoiceNo=VoucherNo,
            #             TransactionID=SalesReturnMasterID,
            #             VoucherType=VoucherType,
            #             VoucherDate=VoucherDate,
            #             InvoiceAmount=GrandTotal,
            #             Payments=total_amount_received,
            #             DueDate=DueDate,
            #             CustomerID=LedgerID
            #         )

            # =====================Loyal Custpmer Point=====================
            is_MinimumSalePrice = data["is_Loyalty_SalesReturn_MinimumSalePrice"]
            today_date = datetime.datetime.now().date()
            if is_LoyaltyCustomer:
                if table.LoyaltyProgram.objects.filter(
                    BranchID=BranchID,
                    CompanyID=CompanyID,
                    FromDate__lte=today_date,
                    ToDate__gte=today_date,
                ).exists():
                    program_instance = table.LoyaltyProgram.objects.get(
                        BranchID=BranchID,
                        CompanyID=CompanyID,
                        FromDate__lte=today_date,
                        ToDate__gte=today_date,
                    )
                    print(program_instance.ProductType)
                    return_point = 0
                    tot_taxable_amnt = 0
                    salesReturnDetails = data["SalesReturnDetails"]
                    for salesReturnDetail in salesReturnDetails:
                        product_id = salesReturnDetail["ProductID"]
                        print(salesReturnDetail["ProductID"], "uvaissss")
                        TaxableAmount = salesReturnDetail["TaxableAmount"]
                        single_product_point = sales_return_point(
                            program_instance,
                            product_id,
                            TaxableAmount,
                            BranchID,
                            CompanyID,
                            is_MinimumSalePrice,
                        )
                        tot_taxable_amnt += single_product_point

                    actual_point = get_actual_point(
                        tot_taxable_amnt, program_instance)
                    print(
                        loyalty_customer,
                        tot_taxable_amnt,
                        "tot_TaxableAmount actual_point",
                        actual_point,
                    )
                    CurrentPoint = 0
                    # loyalty_instance = LoyaltyCustomer.objects.get(
                    #     BranchID=BranchID, CompanyID=CompanyID, LoyaltyCustomerID=loyalty_customer.LoyaltyCustomerID)
                    if table.LoyaltyPoint.objects.filter(
                        BranchID=BranchID,
                        CompanyID=CompanyID,
                        LoyaltyCustomerID__pk=loyalty_customer.pk,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                    ).exists():
                        loyalty_point_instance = table.LoyaltyPoint.objects.get(
                            BranchID=BranchID,
                            CompanyID=CompanyID,
                            LoyaltyCustomerID__pk=loyalty_customer.pk,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                        )
                        loyalty_point_instance.delete()
                    CurrentPoint = loyalty_customer.CurrentPoint
                    if converted_float(CurrentPoint) >= converted_float(actual_point):
                        return_point = converted_float(
                            CurrentPoint) - converted_float(actual_point)
                        print(return_point, "return_pointreturn_pointreturn_point")
                        loyalty_customer.CurrentPoint = return_point
                        loyalty_customer.save()
                        if actual_point:
                            LoyaltyPointID = get_point_auto_id(
                                table.LoyaltyPoint, BranchID, CompanyID
                            )
                            ExpiryDate = None
                            table.LoyaltyPoint.objects.create(
                                BranchID=BranchID,
                                LoyaltyPointID=LoyaltyPointID,
                                Value=actual_point * -1,
                                VoucherType=VoucherType,
                                VoucherMasterID=salesReturnkMaster_instance.SalesReturnMasterID,
                                Point=actual_point * -1,
                                ExpiryDate=ExpiryDate,
                                LoyaltyCustomerID=loyalty_customer,
                                LoyaltyProgramID=program_instance,
                                is_Radeem=False,
                                CreatedDate=today,
                                UpdatedDate=today,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                            )
                            table.LoyaltyPoint_Log.objects.create(
                                BranchID=BranchID,
                                LoyaltyPointID=LoyaltyPointID,
                                Value=actual_point * -1,
                                VoucherType=VoucherType,
                                VoucherMasterID=salesReturnkMaster_instance.SalesReturnMasterID,
                                Point=actual_point * -1,
                                ExpiryDate=ExpiryDate,
                                LoyaltyCustomerID=loyalty_customer,
                                LoyaltyProgramID=program_instance,
                                is_Radeem=False,
                                CreatedDate=today,
                                UpdatedDate=today,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                            )
                    elif converted_float(CurrentPoint) <= converted_float(actual_point):
                        return_point = converted_float(
                            actual_point) - converted_float(CurrentPoint)
                        print(return_point, "return_pointreturn_pointreturn_point")
                        loyalty_customer.CurrentPoint = return_point
                        loyalty_customer.save()
                        if actual_point:
                            LoyaltyPointID = get_point_auto_id(
                                table.LoyaltyPoint, BranchID, CompanyID
                            )
                            ExpiryDate = None
                            table.LoyaltyPoint.objects.create(
                                BranchID=BranchID,
                                LoyaltyPointID=LoyaltyPointID,
                                Value=actual_point * -1,
                                VoucherType=VoucherType,
                                VoucherMasterID=salesReturnkMaster_instance.SalesReturnMasterID,
                                Point=actual_point * -1,
                                ExpiryDate=ExpiryDate,
                                LoyaltyCustomerID=loyalty_customer,
                                LoyaltyProgramID=program_instance,
                                is_Radeem=False,
                                CreatedDate=today,
                                UpdatedDate=today,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                            )
                            table.LoyaltyPoint_Log.objects.create(
                                BranchID=BranchID,
                                LoyaltyPointID=LoyaltyPointID,
                                Value=actual_point * -1,
                                VoucherType=VoucherType,
                                VoucherMasterID=salesReturnkMaster_instance.SalesReturnMasterID,
                                Point=actual_point * -1,
                                ExpiryDate=ExpiryDate,
                                LoyaltyCustomerID=loyalty_customer,
                                LoyaltyProgramID=program_instance,
                                is_Radeem=False,
                                CreatedDate=today,
                                UpdatedDate=today,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                            )
            # =================================END====================================

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
                CompanyID,
                BranchID,
                SalesAccount,
                SalesReturnMasterID,
                VoucherType,
                GrandTotal,
                "Dr",
                "create",
            )

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
                CompanyID,
                BranchID,
                LedgerID,
                SalesReturnMasterID,
                VoucherType,
                GrandTotal,
                "Cr",
                "create",
            )

            if TaxType == "VAT":
                if converted_float(VATAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

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
                        CompanyID,
                        BranchID,
                        55,
                        SalesReturnMasterID,
                        VoucherType,
                        VATAmount,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

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
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        VATAmount,
                        "Cr",
                        "create",
                    )

            elif TaxType == "GST Intra-state B2B" or TaxType == "GST Intra-state B2C":
                if converted_float(CGSTAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

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
                        CompanyID,
                        BranchID,
                        3,
                        SalesReturnMasterID,
                        VoucherType,
                        CGSTAmount,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

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
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        CGSTAmount,
                        "Cr",
                        "create",
                    )

                if converted_float(SGSTAmount) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

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
                        CompanyID,
                        BranchID,
                        10,
                        SalesReturnMasterID,
                        VoucherType,
                        SGSTAmount,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

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
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        SGSTAmount,
                        "Cr",
                        "create",
                    )

                if converted_float(KFCAmount) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

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
                        CompanyID,
                        BranchID,
                        93,
                        SalesReturnMasterID,
                        VoucherType,
                        KFCAmount,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

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
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        KFCAmount,
                        "Cr",
                        "create",
                    )

            elif TaxType == "GST Inter-state B2B" or TaxType == "GST Inter-state B2C":
                if converted_float(IGSTAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

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
                        CompanyID,
                        BranchID,
                        17,
                        SalesReturnMasterID,
                        VoucherType,
                        IGSTAmount,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )

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
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        IGSTAmount,
                        "Cr",
                        "create",
                    )

            if not TaxType == "Export":
                if converted_float(TAX1Amount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )
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
                        CompanyID,
                        BranchID,
                        16,
                        SalesReturnMasterID,
                        VoucherType,
                        TAX1Amount,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )
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
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        TAX1Amount,
                        "Cr",
                        "create",
                    )

                if converted_float(TAX2Amount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )
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
                        CompanyID,
                        BranchID,
                        19,
                        SalesReturnMasterID,
                        VoucherType,
                        TAX2Amount,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )
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
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        TAX2Amount,
                        "Cr",
                        "create",
                    )

                if converted_float(TAX3Amount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )
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
                        CompanyID,
                        BranchID,
                        22,
                        SalesReturnMasterID,
                        VoucherType,
                        TAX3Amount,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID
                    )
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
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        TAX3Amount,
                        "Cr",
                        "create",
                    )

            if converted_float(RoundOff) > 0:

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID
                )

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
                    CompanyID,
                    BranchID,
                    78,
                    SalesReturnMasterID,
                    VoucherType,
                    RoundOff,
                    "Dr",
                    "create",
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID
                )

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
                    CompanyID,
                    BranchID,
                    SalesAccount,
                    SalesReturnMasterID,
                    VoucherType,
                    RoundOff,
                    "Cr",
                    "create",
                )

            if converted_float(RoundOff) < 0:

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID
                )

                RoundOff = abs(converted_float(RoundOff))

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
                    CompanyID,
                    BranchID,
                    78,
                    SalesReturnMasterID,
                    VoucherType,
                    RoundOff,
                    "Cr",
                    "create",
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID
                )

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
                    CompanyID,
                    BranchID,
                    SalesAccount,
                    SalesReturnMasterID,
                    VoucherType,
                    RoundOff,
                    "Dr",
                    "create",
                )

            if converted_float(TotalDiscount) > 0:

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID
                )

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
                    CompanyID,
                    BranchID,
                    74,
                    SalesReturnMasterID,
                    VoucherType,
                    TotalDiscount,
                    "Cr",
                    "create",
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID
                )

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
                    CompanyID,
                    BranchID,
                    SalesAccount,
                    SalesReturnMasterID,
                    VoucherType,
                    TotalDiscount,
                    "Dr",
                    "create",
                )

            deleted_datas = data["deleted_data"]
            if deleted_datas:
                for deleted_Data in deleted_datas:
                    deleted_pk = deleted_Data["unq_id"]
                    SalesReturnDetailsID_Deleted = deleted_Data["SalesDetailID"]
                    ProductID_Deleted = deleted_Data["ProductID"]
                    PriceListID_Deleted = deleted_Data["PriceListID"]
                    Rate_Deleted = deleted_Data["Rate"]
                    SalesReturnMasterID_Deleted = deleted_Data["SalesMasterID"]
                    WarehouseID_Deleted = deleted_Data["WarehouseID"]

                    if table.PriceList.objects.filter(
                        CompanyID=CompanyID,
                        ProductID=ProductID_Deleted,
                        DefaultUnit=True,
                    ).exists():
                        priceList = table.PriceList.objects.get(
                            CompanyID=CompanyID,
                            ProductID=ProductID_Deleted,
                            DefaultUnit=True,
                        )
                        MultiFactor = priceList.MultiFactor
                        Cost = converted_float(
                            Rate_Deleted) / converted_float(MultiFactor)
                        Ct = round(Cost, 4)
                        Cost_Deleted = str(Ct)

                        if not deleted_pk == "" or not deleted_pk == 0:
                            if table.SalesReturnDetails.objects.filter(
                                CompanyID=CompanyID, pk=deleted_pk
                            ).exists():
                                deleted_detail = table.SalesReturnDetails.objects.get(
                                    CompanyID=CompanyID, pk=deleted_pk
                                )

                                deleted_BatchCode = deleted_detail.BatchCode
                                deleted_batch = table.Batch.objects.filter(
                                    CompanyID=CompanyID,
                                    BranchID=BranchID,
                                    BatchCode=deleted_BatchCode,
                                ).first()

                                MultiFactor = table.PriceList.objects.get(
                                    CompanyID=CompanyID,
                                    PriceListID=PriceListID_Deleted,
                                    BranchID=BranchID,
                                ).MultiFactor

                                qty_batch = converted_float(deleted_detail.FreeQty) + converted_float(
                                    deleted_detail.Qty
                                )
                                Qty_batch = converted_float(
                                    MultiFactor) * converted_float(qty_batch)

                                if table.Batch.objects.filter(
                                    CompanyID=CompanyID,
                                    BranchID=BranchID,
                                    BatchCode=BatchCode,
                                ).exists():
                                    batch_ins = table.Batch.objects.get(
                                        CompanyID=CompanyID,
                                        BranchID=BranchID,
                                        BatchCode=BatchCode,
                                    )
                                    StockIn = batch_ins.StockIn
                                    batch_ins.StockIn = converted_float(StockIn) - converted_float(
                                        Qty_batch
                                    )
                                    batch_ins.save()
                                deleted_detail.delete()

                                if table.StockPosting.objects.filter(
                                    CompanyID=CompanyID,
                                    VoucherMasterID=SalesReturnMasterID_Deleted,
                                    VoucherDetailID=SalesReturnDetailsID_Deleted,
                                    ProductID=ProductID_Deleted,
                                    BranchID=BranchID,
                                    VoucherType="SR",
                                ).exists():
                                    stock_instances_delete = table.StockPosting.objects.filter(
                                        CompanyID=CompanyID,
                                        VoucherMasterID=SalesReturnMasterID_Deleted,
                                        VoucherDetailID=SalesReturnDetailsID_Deleted,
                                        ProductID=ProductID_Deleted,
                                        BranchID=BranchID,
                                        VoucherType="SR",
                                    )
                                    stock_instances_delete.delete()

                                    update_stock(
                                        CompanyID, BranchID, ProductID_Deleted)

            salesReturnDetails = data["SalesReturnDetails"]

            for salesReturnDetail in salesReturnDetails:
                ProductID = salesReturnDetail["ProductID"]
                if ProductID:
                    pk = salesReturnDetail["unq_id"]
                    detailID = salesReturnDetail["detailID"]
                    # SalesReturnMasterID = serialized.data['SalesReturnMasterID']
                    DeliveryDetailsID = salesReturnDetail["DeliveryDetailsID"]
                    OrderDetailsID = salesReturnDetail["OrderDetailsID"]
                    Qty_detail = salesReturnDetail["Qty"]
                    FreeQty = salesReturnDetail["FreeQty"]
                    Flavour = salesReturnDetail["Flavour"]
                    # AddlDiscPercent = salesReturnDetail['AddlDiscPerc']

                    UnitPrice = converted_float(salesReturnDetail["UnitPrice"])
                    InclusivePrice = converted_float(
                        salesReturnDetail["InclusivePrice"])
                    RateWithTax = converted_float(
                        salesReturnDetail["RateWithTax"])
                    # CostPerPrice = converted_float(salesReturnDetail["CostPerPrice"])
                    PriceListID = converted_float(
                        salesReturnDetail["PriceListID"])
                    DiscountPerc = converted_float(
                        salesReturnDetail["DiscountPerc"])
                    DiscountAmount = converted_float(
                        salesReturnDetail["DiscountAmount"])
                    GrossAmount = converted_float(
                        salesReturnDetail["GrossAmount"])
                    TaxableAmount = converted_float(
                        salesReturnDetail["TaxableAmount"])
                    VATPerc = converted_float(salesReturnDetail["VATPerc"])
                    VATAmount = converted_float(salesReturnDetail["VATAmount"])
                    SGSTPerc = converted_float(salesReturnDetail["SGSTPerc"])
                    SGSTAmount = converted_float(
                        salesReturnDetail["SGSTAmount"])
                    CGSTPerc = converted_float(salesReturnDetail["CGSTPerc"])
                    CGSTAmount = converted_float(
                        salesReturnDetail["CGSTAmount"])
                    IGSTPerc = converted_float(salesReturnDetail["IGSTPerc"])
                    IGSTAmount = converted_float(
                        salesReturnDetail["IGSTAmount"])
                    NetAmount = converted_float(salesReturnDetail["NetAmount"])
                    AddlDiscPercent = AddlDiscPercent
                    AddlDiscAmt = converted_float(
                        salesReturnDetail["AddlDiscAmt"])
                    TAX1Perc = converted_float(salesReturnDetail["TAX1Perc"])
                    TAX1Amount = converted_float(
                        salesReturnDetail["TAX1Amount"])
                    TAX2Perc = converted_float(salesReturnDetail["TAX2Perc"])
                    TAX2Amount = converted_float(
                        salesReturnDetail["TAX2Amount"])
                    TAX3Perc = converted_float(salesReturnDetail["TAX3Perc"])
                    TAX3Amount = converted_float(
                        salesReturnDetail["TAX3Amount"])

                    try:
                        SerialNos = table.SalesDetails["SerialNos"]
                    except:
                        SerialNos = []

                    try:
                        Description = table.SalesDetails["Description"]
                    except:
                        Description = ""

                    try:
                        BatchCode = salesReturnDetail["BatchCode"]
                    except:
                        BatchCode = 0
                    try:
                        is_inclusive = salesReturnDetail["is_inclusive"]
                    except:
                        is_inclusive = False

                    if is_inclusive == True:
                        Batch_salesPrice = InclusivePrice
                    else:
                        Batch_salesPrice = UnitPrice

                    try:
                        KFCAmount = salesReturnDetail["KFCAmount"]
                    except:
                        KFCAmount = 0

                    try:
                        KFCPerc = salesReturnDetail["KFCPerc"]
                    except:
                        KFCPerc = 0

                    try:
                        ProductTaxID = salesReturnDetail["ProductTaxID"]
                    except:
                        ProductTaxID = 0

                    CostPerPrice = table.PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=PriceListID
                    ).PurchasePrice

                    product_is_Service = table.Product.objects.get(
                        CompanyID=CompanyID, ProductID=ProductID
                    ).is_Service

                    product_purchasePrice = table.PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=PriceListID
                    ).PurchasePrice
                    MultiFactor = table.PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=PriceListID
                    ).MultiFactor

                    qty_batch = converted_float(
                        FreeQty) + converted_float(Qty_detail)
                    Qty_batch = converted_float(
                        MultiFactor) * converted_float(qty_batch)

                    check_AllowUpdateBatchPriceInSales = False
                    check_EnableProductBatchWise = False
                    if product_is_Service == False:
                        if table.GeneralSettings.objects.filter(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            SettingsType="AllowUpdateBatchPriceInSales",
                        ).exists():
                            check_AllowUpdateBatchPriceInSales = (
                                table.GeneralSettings.objects.get(
                                    CompanyID=CompanyID,
                                    BranchID=BranchID,
                                    SettingsType="AllowUpdateBatchPriceInSales",
                                ).SettingsValue
                            )

                        if table.GeneralSettings.objects.filter(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            SettingsType="EnableProductBatchWise",
                        ).exists():
                            check_EnableProductBatchWise = table.GeneralSettings.objects.get(
                                CompanyID=CompanyID,
                                BranchID=BranchID,
                                SettingsType="EnableProductBatchWise",
                            ).SettingsValue

                        if (
                            check_EnableProductBatchWise == True
                            or check_EnableProductBatchWise == "True"
                        ):
                            setbach = SetBatchInSales(
                                CompanyID,
                                BranchID,
                                Batch_salesPrice,
                                Qty_batch,
                                BatchCode,
                                check_AllowUpdateBatchPriceInSales,
                                PriceListID,
                                "SR",
                            )
                    PriceListID_DefUnit = table.PriceList.objects.get(
                        CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True
                    ).PriceListID

                    qty = converted_float(FreeQty) + \
                        converted_float(Qty_detail)

                    Qty = converted_float(MultiFactor) * converted_float(qty)
                    Cost = converted_float(
                        CostPerPrice) / converted_float(MultiFactor)

                    princeList_instance = table.PriceList.objects.get(
                        CompanyID=CompanyID,
                        ProductID=ProductID,
                        PriceListID=PriceListID_DefUnit,
                    )
                    PurchasePrice = princeList_instance.PurchasePrice
                    SalesPrice = princeList_instance.SalesPrice

                    if detailID == 0:
                        salesReturnDetail_instance = table.SalesReturnDetails.objects.get(
                            CompanyID=CompanyID, pk=pk
                        )

                        SalesReturnDetailsID = (
                            salesReturnDetail_instance.SalesReturnDetailsID
                        )

                        log_instance = table.SalesReturnDetails_Log.objects.create(
                            TransactionID=SalesReturnDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            SalesReturnMasterID=SalesReturnMasterID,
                            DeliveryDetailsID=DeliveryDetailsID,
                            OrderDetailsID=OrderDetailsID,
                            ProductID=ProductID,
                            Qty=Qty_detail,
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
                            UpdatedUserID=CreatedUserID,
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
                            ProductTaxID=ProductTaxID,
                        )

                        salesReturnDetail_instance.DeliveryDetailsID = DeliveryDetailsID
                        salesReturnDetail_instance.OrderDetailsID = OrderDetailsID
                        salesReturnDetail_instance.ProductID = ProductID
                        salesReturnDetail_instance.Qty = Qty_detail
                        salesReturnDetail_instance.FreeQty = FreeQty
                        salesReturnDetail_instance.UnitPrice = UnitPrice
                        salesReturnDetail_instance.InclusivePrice = InclusivePrice
                        salesReturnDetail_instance.RateWithTax = RateWithTax
                        salesReturnDetail_instance.CostPerPrice = CostPerPrice
                        salesReturnDetail_instance.PriceListID = PriceListID
                        salesReturnDetail_instance.DiscountPerc = DiscountPerc
                        salesReturnDetail_instance.DiscountAmount = DiscountAmount
                        salesReturnDetail_instance.GrossAmount = GrossAmount
                        salesReturnDetail_instance.TaxableAmount = TaxableAmount
                        salesReturnDetail_instance.VATPerc = VATPerc
                        salesReturnDetail_instance.VATAmount = VATAmount
                        salesReturnDetail_instance.SGSTPerc = SGSTPerc
                        salesReturnDetail_instance.SGSTAmount = SGSTAmount
                        salesReturnDetail_instance.CGSTPerc = CGSTPerc
                        salesReturnDetail_instance.CGSTAmount = CGSTAmount
                        salesReturnDetail_instance.IGSTPerc = IGSTPerc
                        salesReturnDetail_instance.IGSTAmount = IGSTAmount
                        salesReturnDetail_instance.NetAmount = NetAmount
                        salesReturnDetail_instance.Flavour = Flavour
                        salesReturnDetail_instance.Action = Action
                        salesReturnDetail_instance.UpdatedUserID = CreatedUserID
                        salesReturnDetail_instance.UpdatedDate = today
                        salesReturnDetail_instance.AddlDiscPercent = AddlDiscPercent
                        salesReturnDetail_instance.AddlDiscAmt = AddlDiscAmt
                        salesReturnDetail_instance.TAX1Perc = TAX1Perc
                        salesReturnDetail_instance.TAX1Amount = TAX1Amount
                        salesReturnDetail_instance.TAX2Perc = TAX2Perc
                        salesReturnDetail_instance.TAX2Amount = TAX2Amount
                        salesReturnDetail_instance.TAX3Perc = TAX3Perc
                        salesReturnDetail_instance.TAX3Amount = TAX3Amount
                        salesReturnDetail_instance.BatchCode = BatchCode
                        salesReturnDetail_instance.LogID = log_instance.ID
                        salesReturnDetail_instance.KFCAmount = KFCAmount
                        salesReturnDetail_instance.KFCPerc = KFCPerc
                        salesReturnDetail_instance.ProductTaxID = ProductTaxID

                        salesReturnDetail_instance.save()

                        if product_is_Service == False:
                            if table.StockPosting.objects.filter(
                                CompanyID=CompanyID,
                                WareHouseID=WarehouseID,
                                VoucherMasterID=SalesReturnMasterID,
                                VoucherDetailID=SalesReturnDetailsID,
                                BranchID=BranchID,
                                VoucherType="SR",
                                ProductID=ProductID,
                            ).exists():
                                stock_instance = table.StockPosting.objects.filter(
                                    CompanyID=CompanyID,
                                    WareHouseID=WarehouseID,
                                    VoucherMasterID=SalesReturnMasterID,
                                    VoucherDetailID=SalesReturnDetailsID,
                                    BranchID=BranchID,
                                    VoucherType="SR",
                                    ProductID=ProductID,
                                ).first()
                                stock_instance.QtyIn = Qty
                                stock_instance.Action = Action
                                stock_instance.save()
                            else:
                                StockPostingID = get_auto_stockPostid(
                                    table.StockPosting, BranchID, CompanyID
                                )
                                pricelist, warehouse = get_ModelInstance(
                                    CompanyID,
                                    BranchID,
                                    PriceListID_DefUnit,
                                    WarehouseID,
                                )

                                table.StockPosting.objects.create(
                                    StockPostingID=StockPostingID,
                                    BranchID=BranchID,
                                    Action=Action,
                                    Date=VoucherDate,
                                    VoucherMasterID=SalesReturnMasterID,
                                    VoucherDetailID=SalesReturnDetailsID,
                                    VoucherType=VoucherType,
                                    ProductID=ProductID,
                                    BatchID=BatchCode,
                                    WareHouseID=WarehouseID,
                                    QtyIn=Qty,
                                    Rate=Cost,
                                    PriceListID=PriceListID_DefUnit,
                                    IsActive=IsActive,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CreatedUserID=CreatedUserID,
                                    CompanyID=CompanyID,
                                    pricelist=pricelist,
                                    warehouse=warehouse,
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
                                    BatchID=BatchCode,
                                    WareHouseID=WarehouseID,
                                    QtyIn=Qty,
                                    Rate=Cost,
                                    PriceListID=PriceListID_DefUnit,
                                    IsActive=IsActive,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CreatedUserID=CreatedUserID,
                                    CompanyID=CompanyID,
                                )

                            update_stock(CompanyID, BranchID, ProductID)

                    if detailID == 1:

                        SalesReturnDetailsID = salesReturnDetailID(
                            table.SalesReturnDetails, BranchID, CompanyID
                        )

                        Action = "A"

                        log_instance = table.SalesReturnDetails_Log.objects.create(
                            TransactionID=SalesReturnDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            SalesReturnMasterID=SalesReturnMasterID,
                            DeliveryDetailsID=DeliveryDetailsID,
                            OrderDetailsID=OrderDetailsID,
                            ProductID=ProductID,
                            Qty=Qty_detail,
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
                            UpdatedUserID=CreatedUserID,
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
                            ProductTaxID=ProductTaxID,
                        )

                        table.SalesReturnDetails.objects.create(
                            SalesReturnDetailsID=SalesReturnDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            SalesReturnMasterID=SalesReturnMasterID,
                            DeliveryDetailsID=DeliveryDetailsID,
                            OrderDetailsID=OrderDetailsID,
                            ProductID=ProductID,
                            Qty=Qty_detail,
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
                            UpdatedUserID=CreatedUserID,
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
                            LogID=log_instance.ID,
                            KFCAmount=KFCAmount,
                            KFCPerc=KFCPerc,
                            ProductTaxID=ProductTaxID,
                        )

                        if product_is_Service == False:
                            StockPostingID = get_auto_stockPostid(
                                table.StockPosting, BranchID, CompanyID
                            )
                            pricelist, warehouse = get_ModelInstance(
                                CompanyID, BranchID, PriceListID, WarehouseID
                            )

                            table.StockPosting.objects.create(
                                StockPostingID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=VoucherDate,
                                VoucherMasterID=SalesReturnMasterID,
                                VoucherDetailID=SalesReturnDetailsID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                BatchID=BatchCode,
                                WareHouseID=WarehouseID,
                                QtyIn=Qty,
                                Rate=Cost,
                                PriceListID=PriceListID_DefUnit,
                                IsActive=IsActive,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                                pricelist=pricelist,
                                warehouse=warehouse,
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
                                BatchID=BatchCode,
                                WareHouseID=WarehouseID,
                                QtyIn=Qty,
                                Rate=Cost,
                                PriceListID=PriceListID_DefUnit,
                                IsActive=IsActive,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                            )

                            update_stock(CompanyID, BranchID, ProductID)

                    if SerialNos:
                        for sn in SerialNos:
                            table.SerialNumbers.objects.create(
                                CompanyID=CompanyID,
                                VoucherType="SR",
                                SerialNo=sn["SerialNo"],
                                ItemCode=sn["ItemCode"],
                                SalesMasterID=SalesReturnMasterID,
                                SalesDetailsID=SalesReturnDetailsID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                            )

            cash_Balance = get_LedgerBalance(CompanyID, 1)
            response_data = {
                "StatusCode": 6000,
                "message": "Sales Returns Updated Successfully!!!",
                "CashBalance": cash_Balance,
                "id": salesReturnkMaster_instance.id,
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
            "Sales Return",
            "Edit",
            str(e),
            err_descrb,
        )
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def salesApp_salesReturnMaster(request, pk):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]
    instance = None
    if table.SalesReturnMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = table.SalesReturnMaster.objects.get(
            CompanyID=CompanyID, pk=pk)

        serialized = SalesReturnMasterSerializer(
            instance, context={"CompanyID": CompanyID,
                               "PriceRounding": PriceRounding}
        )

        response_data = {"StatusCode": 6000, "data": serialized.data}
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Sales Return Master Not Found!",
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def salesApp_delete_salesReturnMaster(request, pk):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    try:
        selecte_ids = data["selecte_ids"]
    except:
        selecte_ids = []

    today = datetime.datetime.now()
    instances = None
    if selecte_ids:
        if table.SalesReturnMaster.objects.filter(
            CompanyID=CompanyID, pk__in=selecte_ids
        ).exists():
            instances = table.SalesReturnMaster.objects.filter(
                pk__in=selecte_ids)
    else:
        if table.SalesReturnMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
            instances = table.SalesReturnMaster.objects.filter(pk=pk)

    if instances:
        for instance in instances:
            SalesReturnMasterID = instance.SalesReturnMasterID
            LoyaltyCustomerID = instance.LoyaltyCustomerID
            BranchID = instance.BranchID
            VoucherNo = instance.VoucherNo
            VoucherDate = instance.VoucherDate
            RefferenceBillNo = instance.RefferenceBillNo
            RefferenceBillDate = instance.RefferenceBillDate
            CreditPeriod = instance.CreditPeriod
            LedgerID = instance.LedgerID
            PriceCategoryID = instance.PriceCategoryID
            EmployeeID = instance.EmployeeID
            SalesAccount = instance.SalesAccount
            DeliveryMasterID = instance.DeliveryMasterID
            OrderMasterID = instance.OrderMasterID
            CustomerName = instance.CustomerName
            Address1 = instance.Address1
            Address2 = instance.Address2
            Address3 = instance.Address3
            Notes = instance.Notes
            FinacialYearID = instance.FinacialYearID
            TotalGrossAmt = instance.TotalGrossAmt
            TotalTax = instance.TotalTax
            NetTotal = instance.NetTotal
            AdditionalCost = instance.AdditionalCost
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
            IsPosted = instance.IsPosted
            SalesType = instance.SalesType
            TaxID = instance.TaxID
            TaxType = instance.TaxType
            VATAmount = instance.VATAmount
            SGSTAmount = instance.SGSTAmount
            CGSTAmount = instance.CGSTAmount
            IGSTAmount = instance.IGSTAmount
            TAX1Amount = instance.TAX1Amount
            TAX2Amount = instance.TAX2Amount
            TAX3Amount = instance.TAX3Amount
            AddlDiscPercent = instance.AddlDiscPercent
            AddlDiscAmt = instance.AddlDiscAmt
            TotalDiscount = instance.TotalDiscount
            BillDiscPercent = instance.BillDiscPercent
            BillDiscAmt = instance.BillDiscAmt
            KFCAmount = instance.KFCAmount
            Country_of_Supply = instance.Country_of_Supply
            State_of_Supply = instance.State_of_Supply
            GST_Treatment = instance.GST_Treatment
            VAT_Treatment = instance.VAT_Treatment
            Action = "D"
            if table.BillWiseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, InvoiceNo=VoucherNo, TransactionID=SalesReturnMasterID, VoucherType="SR", Payments__gt=0).exists():
                response_data = {
                    "StatusCode": 6001,
                    "title": "Failed",
                    "message": "You can't Delete this Invoice(" + VoucherNo + ")this has been Paid",
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                table.SalesReturnMaster_Log.objects.create(
                    TransactionID=SalesReturnMasterID,
                    LoyaltyCustomerID=LoyaltyCustomerID,
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
                    UpdatedUserID=CreatedUserID,
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

                if table.LedgerPosting.objects.filter(
                    CompanyID=CompanyID,
                    VoucherMasterID=SalesReturnMasterID,
                    BranchID=BranchID,
                    VoucherType="SR",
                ).exists():
                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, 0, SalesReturnMasterID, "SR", 0, "Cr", "update"
                    )
                    ledgerPostInstances = table.LedgerPosting.objects.filter(
                        CompanyID=CompanyID,
                        VoucherMasterID=SalesReturnMasterID,
                        BranchID=BranchID,
                        VoucherType="SR",
                    )

                    for ledgerPostInstance in ledgerPostInstances:
                        LedgerPostingID = ledgerPostInstance.LedgerPostingID
                        VoucherType = ledgerPostInstance.VoucherType
                        VoucherNo = ledgerPostInstance.VoucherNo
                        Debit = ledgerPostInstance.Debit
                        Credit = ledgerPostInstance.Credit
                        IsActive = ledgerPostInstance.IsActive
                        Date = ledgerPostInstance.Date
                        LedgerID = ledgerPostInstance.LedgerID
                        RelatedLedgerID = ledgerPostInstance.RelatedLedgerID

                        table.LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=LedgerID,
                            RelatedLedgerID=RelatedLedgerID,
                            Credit=Credit,
                            Debit=Debit,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        ledgerPostInstance.delete()

                if table.StockPosting.objects.filter(
                    CompanyID=CompanyID,
                    VoucherMasterID=SalesReturnMasterID,
                    BranchID=BranchID,
                    VoucherType="SR",
                ).exists():

                    stockPostingInstances = table.StockPosting.objects.filter(
                        CompanyID=CompanyID,
                        VoucherMasterID=SalesReturnMasterID,
                        BranchID=BranchID,
                        VoucherType="SR",
                    )

                    for stockPostingInstance in stockPostingInstances:
                        StockPostingID = stockPostingInstance.StockPostingID
                        BranchID = stockPostingInstance.BranchID
                        Date = stockPostingInstance.Date
                        VoucherMasterID = stockPostingInstance.VoucherMasterID
                        VoucherDetailID = stockPostingInstance.VoucherDetailID
                        VoucherType = stockPostingInstance.VoucherType
                        ProductID = stockPostingInstance.ProductID
                        BatchID = stockPostingInstance.BatchID
                        WareHouseID = stockPostingInstance.WareHouseID
                        QtyIn = stockPostingInstance.QtyIn
                        QtyOut = stockPostingInstance.QtyOut
                        Rate = stockPostingInstance.Rate
                        PriceListID = stockPostingInstance.PriceListID
                        IsActive = stockPostingInstance.IsActive

                        table.StockPosting_Log.objects.create(
                            TransactionID=StockPostingID,
                            BranchID=BranchID,
                            Action=Action,
                            Date=Date,
                            VoucherMasterID=VoucherMasterID,
                            VoucherDetailID=VoucherDetailID,
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

                        update_stock(CompanyID, BranchID, ProductID)

                detail_instances = table.SalesReturnDetails.objects.filter(
                    CompanyID=CompanyID, SalesReturnMasterID=SalesReturnMasterID
                )

                for detail_instance in detail_instances:
                    SalesReturnDetailsID = detail_instance.SalesReturnDetailsID
                    BranchID = detail_instance.BranchID
                    SalesReturnMasterID = detail_instance.SalesReturnMasterID
                    DeliveryDetailsID = detail_instance.DeliveryDetailsID
                    OrderDetailsID = detail_instance.OrderDetailsID
                    ProductID = detail_instance.ProductID
                    Qty = detail_instance.Qty
                    FreeQty = detail_instance.FreeQty
                    UnitPrice = detail_instance.UnitPrice
                    InclusivePrice = detail_instance.InclusivePrice
                    RateWithTax = detail_instance.RateWithTax
                    CostPerPrice = detail_instance.CostPerPrice
                    PriceListID = detail_instance.PriceListID
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
                    CreatedUserID = detail_instance.CreatedUserID
                    UpdatedUserID = detail_instance.UpdatedUserID
                    AddlDiscPercent = detail_instance.AddlDiscPercent
                    AddlDiscAmt = detail_instance.AddlDiscAmt
                    TAX1Perc = detail_instance.TAX1Perc
                    TAX1Amount = detail_instance.TAX1Amount
                    TAX2Perc = detail_instance.TAX2Perc
                    TAX2Amount = detail_instance.TAX2Amount
                    TAX3Perc = detail_instance.TAX3Perc
                    TAX3Amount = detail_instance.TAX3Amount
                    KFCAmount = detail_instance.KFCAmount
                    KFCPerc = detail_instance.KFCPerc
                    ProductTaxID = detail_instance.ProductTaxID

                    update_stock(CompanyID, BranchID, ProductID)

                    BatchCode = detail_instance.BatchCode

                    if table.Batch.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode
                    ).exists():
                        batch_ins = table.Batch.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode
                        )
                        MultiFactor = table.PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=PriceListID
                        ).MultiFactor

                        qty_batch = converted_float(
                            FreeQty) + converted_float(Qty)
                        Qty_batch = converted_float(
                            MultiFactor) * converted_float(qty_batch)
                        StockIn = batch_ins.StockIn
                        batch_ins.StockIn = converted_float(
                            StockIn) - converted_float(Qty_batch)
                        batch_ins.save()

                    table.SalesReturnDetails_Log.objects.create(
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
                        UpdatedUserID=UpdatedUserID,
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
                        ProductTaxID=ProductTaxID,
                    )

                    detail_instance.delete()
                # =========Loyalty Point ==========
                if table.LoyaltyPoint.objects.filter(
                    LoyaltyCustomerID=LoyaltyCustomerID,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType="SR",
                    BranchID=BranchID,
                    CompanyID=CompanyID,
                ).exists():
                    instances = table.LoyaltyPoint.objects.filter(
                        LoyaltyCustomerID=LoyaltyCustomerID,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType="SR",
                        BranchID=BranchID,
                        CompanyID=CompanyID,
                    ).delete()

                # =========Loyalty Point ==========
                instance.delete()
        # request , company, log_type, user, source, action, message, description
        activity_log(
            request._request,
            CompanyID,
            "Information",
            CreatedUserID,
            "Sales Return",
            "Delete",
            "Sales Return Deleted Successfully.",
            "Sales Return Deleted Successfully.",
        )

        response_data = {
            "StatusCode": 6000,
            "title": "Success",
            "message": "Sales Return Master Deleted Successfully!",
        }
    else:
        # request , company, log_type, user, source, action, message, description
        activity_log(
            request._request,
            CompanyID,
            "Warning",
            CreatedUserID,
            "Sales Return",
            "Delete",
            "Sales Return Deleted Failed.",
            "Sales Return Master Not Found",
        )

        response_data = {
            "StatusCode": 6001,
            "title": "Failed",
            "message": "Sales Return Master Not Found!",
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def salesApp_create_salesOrder(request):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data["CompanyID"]
            CompanyID = get_company(CompanyID)
            CreatedUserID = data["CreatedUserID"]
            today = datetime.datetime.now()
            BranchID = data["BranchID"]
            VoucherNo = data["VoucherNo"]
            Date = data["Date"]
            DeliveryDate = data["DeliveryDate"]
            LedgerID = data["LedgerID"]
            PriceCategoryID = data["PriceCategoryID"]
            CustomerName = data["CustomerName"]
            Address1 = data["Address1"]
            Address2 = data["Address2"]
            Notes = data["Notes"]
            FinacialYearID = data["FinacialYearID"]
            TotalTax = data["TotalTax"]
            NetTotal = data["NetTotal"]
            BillDiscAmt = data["BillDiscAmt"]
            BillDiscPercent = data["BillDiscPercent"]
            GrandTotal = data["GrandTotal"]
            RoundOff = data["RoundOff"]
            IsActive = data["IsActive"]
            IsInvoiced = data["IsInvoiced"]
            TaxID = data["TaxID"]
            TaxType = data["TaxType"]
            VATAmount = data["VATAmount"]
            SGSTAmount = data["SGSTAmount"]
            CGSTAmount = data["CGSTAmount"]
            IGSTAmount = data["IGSTAmount"]
            TAX1Amount = data["TAX1Amount"]
            TAX2Amount = data["TAX2Amount"]
            TAX3Amount = data["TAX3Amount"]

            Action = "A"

            try:
                ShippingCharge = data["ShippingCharge"]
            except:
                ShippingCharge = 0

            try:
                shipping_tax_amount = data["shipping_tax_amount"]
            except:
                shipping_tax_amount = 0

            try:
                TaxTypeID = data["TaxTypeID"]
            except:
                TaxTypeID = ""

            try:
                SAC = data["SAC"]
            except:
                SAC = ""

            try:
                SalesTax = data["SalesTax"]
            except:
                SalesTax = 0

            try:
                Country_of_Supply = data["Country_of_Supply"]
            except:
                Country_of_Supply = ""

            try:
                State_of_Supply = data["State_of_Supply"]
            except:
                State_of_Supply = ""

            try:
                GST_Treatment = data["GST_Treatment"]
            except:
                GST_Treatment = ""

            try:
                VAT_Treatment = data["VAT_Treatment"]
            except:
                VAT_Treatment = ""

            try:
                ShippingAddress = data["ShippingAddress"]
            except:
                ShippingAddress = None

            TotalDiscount = converted_float(data["TotalDiscount"])

            if ShippingAddress:
                if table.UserAdrress.objects.filter(id=ShippingAddress).exists():
                    ShippingAddress = table.UserAdrress.objects.get(
                        id=ShippingAddress)

            VoucherType = "SO"

            # VoucherNo Updated
            try:
                PreFix = data["PreFix"]
            except:
                PreFix = "SO"

            try:
                Seperator = data["Seperator"]
            except:
                Seperator = ""

            try:
                InvoiceNo = data["InvoiceNo"]
            except:
                InvoiceNo = 1

            try:
                TotalGrossAmt = data["TotalGrossAmt"]
            except:
                TotalGrossAmt = 0

            try:
                EstimateNo = data["EstimateNo"]
            except:
                EstimateNo = "SE0"

            try:
                estimate_vouchers = data["estimate_vouchers"]
            except:
                estimate_vouchers = []

            try:
                BillingAddress = data["BillingAddress"]
            except:
                BillingAddress = None

            if BillingAddress:
                if table.UserAdrress.objects.filter(id=BillingAddress).exists():
                    BillingAddress = table.UserAdrress.objects.get(
                        id=BillingAddress)
                else:
                    BillingAddress = None

            try:
                TaxTaxableAmount = converted_float(data["TaxTaxableAmount"])
            except:
                TaxTaxableAmount = 0
            try:
                NonTaxTaxableAmount = converted_float(
                    data["NonTaxTaxableAmount"])
            except:
                NonTaxTaxableAmount = 0

            if table.SalesEstimateMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, VoucherNo=EstimateNo, Status="N"
            ).exists():
                estimate_instance = table.SalesEstimateMaster.objects.get(
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    VoucherNo=EstimateNo,
                    Status="N",
                )
                estimate_instance.Status = "O"
                estimate_instance.save()
            else:
                if estimate_vouchers:
                    estimate_instances = table.SalesEstimateMaster.objects.filter(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        VoucherNo__in=estimate_vouchers,
                        Status="N",
                    )
                    for b in estimate_instances:
                        b.Status = "O"
                        b.save()

            # checking voucher number already exist
            VoucherNoLow = VoucherNo.lower()
            is_voucherExist = False
            insts = table.SalesOrderMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID
            )
            if insts:
                for i in insts:
                    voucher_no = i.VoucherNo
                    voucherNo = voucher_no.lower()
                    if VoucherNoLow == voucherNo:
                        is_voucherExist = True

            check_VoucherNoAutoGenerate = False
            is_SaleOrderOK = True

            if table.GeneralSettings.objects.filter(
                CompanyID=CompanyID,
                BranchID=BranchID,
                SettingsType="VoucherNoAutoGenerate",
            ).exists():
                check_VoucherNoAutoGenerate = table.GeneralSettings.objects.get(
                    BranchID=BranchID,
                    CompanyID=CompanyID,
                    SettingsType="VoucherNoAutoGenerate",
                ).SettingsValue

            if is_voucherExist == True and check_VoucherNoAutoGenerate == "True":
                VoucherNo = get_Genrate_VoucherNo(
                    table.SalesOrderMaster, BranchID, CompanyID, "SO"
                )
                is_SaleOrderOK = True
            elif is_voucherExist == False:
                is_SaleOrderOK = True
            else:
                is_SaleOrderOK = False

            if is_SaleOrderOK:
                update_voucher_table(
                    CompanyID, CreatedUserID, VoucherType, PreFix, Seperator, InvoiceNo
                )

                SalesOrderMasterID = OrderMasterID(
                    table.SalesOrderMaster, BranchID, CompanyID
                )

                table.SalesOrderMaster_Log.objects.create(
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
                    UpdatedUserID=CreatedUserID,
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
                    VAT_Treatment=VAT_Treatment,
                    TotalGrossAmt=TotalGrossAmt,
                    ShippingAddress=ShippingAddress,
                    EstimateNo=EstimateNo,
                    TaxTaxableAmount=TaxTaxableAmount,
                    NonTaxTaxableAmount=NonTaxTaxableAmount,
                    TotalDiscount=TotalDiscount,
                    BillingAddress=BillingAddress,
                )

                instance = table.SalesOrderMaster.objects.create(
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
                    UpdatedUserID=CreatedUserID,
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
                    VAT_Treatment=VAT_Treatment,
                    TotalGrossAmt=TotalGrossAmt,
                    ShippingAddress=ShippingAddress,
                    EstimateNo=EstimateNo,
                    TaxTaxableAmount=TaxTaxableAmount,
                    NonTaxTaxableAmount=NonTaxTaxableAmount,
                    TotalDiscount=TotalDiscount,
                    BillingAddress=BillingAddress,
                )

                saleOrdersDetails = data["saleOrdersDetails"]

                for saleOrdersDetail in saleOrdersDetails:
                    ProductID = saleOrdersDetail["ProductID"]
                    if ProductID:
                        Qty = saleOrdersDetail["Qty"]
                        FreeQty = saleOrdersDetail["FreeQty"]
                        UnitPrice = saleOrdersDetail["UnitPrice"]
                        RateWithTax = saleOrdersDetail["RateWithTax"]
                        PriceListID = saleOrdersDetail["PriceListID"]
                        DiscountPerc = saleOrdersDetail["DiscountPerc"]
                        DiscountAmount = saleOrdersDetail["DiscountAmount"]
                        GrossAmount = saleOrdersDetail["GrossAmount"]
                        TaxableAmount = saleOrdersDetail["TaxableAmount"]
                        VATPerc = saleOrdersDetail["VATPerc"]
                        VATAmount = saleOrdersDetail["VATAmount"]
                        SGSTPerc = saleOrdersDetail["SGSTPerc"]
                        SGSTAmount = saleOrdersDetail["SGSTAmount"]
                        CGSTPerc = saleOrdersDetail["CGSTPerc"]
                        CGSTAmount = saleOrdersDetail["CGSTAmount"]
                        IGSTPerc = saleOrdersDetail["IGSTPerc"]
                        IGSTAmount = saleOrdersDetail["IGSTAmount"]
                        TAX1Perc = saleOrdersDetail["TAX1Perc"]
                        TAX1Amount = saleOrdersDetail["TAX1Amount"]
                        TAX2Perc = saleOrdersDetail["TAX2Perc"]
                        TAX2Amount = saleOrdersDetail["TAX2Amount"]
                        TAX3Perc = saleOrdersDetail["TAX3Perc"]
                        TAX3Amount = saleOrdersDetail["TAX3Amount"]
                        try:
                            KFCAmount = saleOrdersDetail["KFCAmount"]
                        except:
                            KFCAmount = 0

                        NetAmount = saleOrdersDetail["NetAmount"]
                        InclusivePrice = saleOrdersDetail["InclusivePrice"]
                        BatchCode = saleOrdersDetail["BatchCode"]

                        try:
                            SerialNos = saleOrdersDetail["SerialNos"]
                        except:
                            SerialNos = []

                        try:
                            Description = saleOrdersDetail["Description"]
                        except:
                            Description = ""

                        try:
                            ProductTaxID = saleOrdersDetail["ProductTaxID"]
                        except:
                            ProductTaxID = ""

                        SalesOrderDetailsID = OrderDetailID(
                            table.SalesOrderDetails, BranchID, CompanyID
                        )

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

                        log_instance = table.SalesOrderDetails_Log.objects.create(
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
                            UpdatedUserID=CreatedUserID,
                            InclusivePrice=InclusivePrice,
                            BatchCode=BatchCode,
                            ProductTaxID=ProductTaxID,
                            Description=Description
                        )

                        table.SalesOrderDetails.objects.create(
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
                            UpdatedUserID=CreatedUserID,
                            InclusivePrice=InclusivePrice,
                            BatchCode=BatchCode,
                            LogID=log_instance.ID,
                            ProductTaxID=ProductTaxID,
                            Description=Description
                        )

                cash_Balance = get_LedgerBalance(CompanyID, 1)
                response_data = {
                    "StatusCode": 6000,
                    "message": "Sale Orders created Successfully!!!",
                    "CashBalance": cash_Balance,
                    "id": instance.id,
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                # request , company, log_type, user, source, action, message, description
                activity_log(
                    request._request,
                    CompanyID,
                    "Warning",
                    CreatedUserID,
                    "Sale Orders",
                    "Create",
                    "Sale Orders created Failed.",
                    "VoucherNo already exist!",
                )
                response_data = {
                    "StatusCode": 6001,
                    "message": "VoucherNo already exist.Please Change Your Prefix!",
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

        activity_log(
            request._request,
            CompanyID,
            "Error",
            CreatedUserID,
            "Sales Order",
            "Create",
            str(e),
            err_descrb,
        )
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def salesApp_edit_salesOrder(request, pk):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data["CompanyID"]
            CompanyID = get_company(CompanyID)
            CreatedUserID = data["CreatedUserID"]

            today = datetime.datetime.now()
            salesOrderMaster_instance = None
            salesOrderDetails = None

            salesOrderMaster_instance = table.SalesOrderMaster.objects.get(
                CompanyID=CompanyID, pk=pk
            )

            SalesOrderMasterID = salesOrderMaster_instance.SalesOrderMasterID
            BranchID = salesOrderMaster_instance.BranchID
            VoucherNo = salesOrderMaster_instance.VoucherNo

            Date = data["Date"]
            DeliveryDate = data["DeliveryDate"]
            LedgerID = data["LedgerID"]
            PriceCategoryID = data["PriceCategoryID"]
            CustomerName = data["CustomerName"]
            Address1 = data["Address1"]
            Address2 = data["Address2"]
            Notes = data["Notes"]
            FinacialYearID = data["FinacialYearID"]
            TotalTax = data["TotalTax"]
            NetTotal = data["NetTotal"]
            BillDiscAmt = data["BillDiscAmt"]
            BillDiscPercent = data["BillDiscPercent"]
            GrandTotal = data["GrandTotal"]
            RoundOff = data["RoundOff"]
            IsActive = data["IsActive"]
            IsInvoiced = data["IsInvoiced"]
            TaxID = data["TaxID"]
            TaxType = data["TaxType"]
            VATAmount = data["VATAmount"]
            SGSTAmount = data["SGSTAmount"]
            CGSTAmount = data["CGSTAmount"]
            IGSTAmount = data["IGSTAmount"]
            TAX1Amount = data["TAX1Amount"]
            TAX2Amount = data["TAX2Amount"]
            TAX3Amount = data["TAX3Amount"]

            Action = "M"

            try:
                ShippingCharge = data["ShippingCharge"]
            except:
                ShippingCharge = 0

            try:
                shipping_tax_amount = data["shipping_tax_amount"]
            except:
                shipping_tax_amount = 0

            try:
                TaxTypeID = data["TaxTypeID"]
            except:
                TaxTypeID = ""

            try:
                SAC = data["SAC"]
            except:
                SAC = ""

            try:
                SalesTax = data["SalesTax"]
            except:
                SalesTax = 0

            try:
                Country_of_Supply = data["Country_of_Supply"]
            except:
                Country_of_Supply = ""

            try:
                State_of_Supply = data["State_of_Supply"]
            except:
                State_of_Supply = ""

            try:
                GST_Treatment = data["GST_Treatment"]
            except:
                GST_Treatment = ""

            try:
                VAT_Treatment = data["VAT_Treatment"]
            except:
                VAT_Treatment = ""

            try:
                EstimateNo = data["EstimateNo"]
            except:
                EstimateNo = ""

            try:
                TaxTaxableAmount = converted_float(data["TaxTaxableAmount"])
            except:
                TaxTaxableAmount = 0
            try:
                NonTaxTaxableAmount = converted_float(
                    data["NonTaxTaxableAmount"])
            except:
                NonTaxTaxableAmount = 0

            try:
                BillingAddress = data["BillingAddress"]
            except:
                BillingAddress = None

            if BillingAddress:
                if table.UserAdrress.objects.filter(id=BillingAddress).exists():
                    BillingAddress = table.UserAdrress.objects.get(
                        id=BillingAddress)
                else:
                    BillingAddress = None

            TotalDiscount = converted_float(data["TotalDiscount"])

            table.SalesOrderMaster_Log.objects.create(
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
                UpdatedUserID=CreatedUserID,
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
                VAT_Treatment=VAT_Treatment,
                EstimateNo=EstimateNo,
                TaxTaxableAmount=TaxTaxableAmount,
                NonTaxTaxableAmount=NonTaxTaxableAmount,
                TotalDiscount=TotalDiscount,
                BillingAddress=BillingAddress,
            )
            if table.SerialNumbers.objects.filter(
                CompanyID=CompanyID,
                SalesMasterID=SalesOrderMasterID,
                BranchID=BranchID,
                VoucherType="SO",
            ).exists():
                SerialNumbersInstances = table.SerialNumbers.objects.filter(
                    CompanyID=CompanyID,
                    SalesMasterID=SalesOrderMasterID,
                    BranchID=BranchID,
                    VoucherType="SO",
                )
                for sli in SerialNumbersInstances:
                    sli.delete()

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
            salesOrderMaster_instance.UpdatedUserID = CreatedUserID
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
            salesOrderMaster_instance.VAT_Treatment = VAT_Treatment
            salesOrderMaster_instance.EstimateNo = EstimateNo

            salesOrderMaster_instance.TaxTaxableAmount = TaxTaxableAmount
            salesOrderMaster_instance.NonTaxTaxableAmount = NonTaxTaxableAmount
            salesOrderMaster_instance.TotalDiscount = TotalDiscount
            salesOrderMaster_instance.BillingAddress = BillingAddress
            salesOrderMaster_instance.save()

            deleted_datas = data["deleted_data"]
            if deleted_datas:
                for deleted_Data in deleted_datas:
                    deleted_pk = deleted_Data["unq_id"]

                    if not deleted_pk == "" or not deleted_pk == 0:
                        if table.SalesOrderDetails.objects.filter(
                            CompanyID=CompanyID, pk=deleted_pk
                        ).exists():
                            deleted_detail = table.SalesOrderDetails.objects.filter(
                                CompanyID=CompanyID, pk=deleted_pk
                            )
                            deleted_detail.delete()

            salesOrderDetails = data["saleOrdersDetails"]
            for salesOrderDetail in salesOrderDetails:

                unq_id = salesOrderDetail["unq_id"]
                ProductID = salesOrderDetail["ProductID"]
                if ProductID:
                    Qty = salesOrderDetail["Qty"]
                    FreeQty = salesOrderDetail["FreeQty"]
                    UnitPrice = salesOrderDetail["UnitPrice"]
                    RateWithTax = salesOrderDetail["RateWithTax"]
                    PriceListID = salesOrderDetail["PriceListID"]
                    DiscountPerc = salesOrderDetail["DiscountPerc"]
                    DiscountAmount = salesOrderDetail["DiscountAmount"]
                    GrossAmount = salesOrderDetail["GrossAmount"]
                    TaxableAmount = salesOrderDetail["TaxableAmount"]
                    VATPerc = salesOrderDetail["VATPerc"]
                    VATAmount = salesOrderDetail["VATAmount"]
                    SGSTPerc = salesOrderDetail["SGSTPerc"]
                    SGSTAmount = salesOrderDetail["SGSTAmount"]
                    CGSTPerc = salesOrderDetail["CGSTPerc"]
                    CGSTAmount = salesOrderDetail["CGSTAmount"]
                    IGSTPerc = salesOrderDetail["IGSTPerc"]
                    IGSTAmount = salesOrderDetail["IGSTAmount"]
                    TAX1Perc = salesOrderDetail["TAX1Perc"]
                    TAX1Amount = salesOrderDetail["TAX1Amount"]
                    TAX2Perc = salesOrderDetail["TAX2Perc"]
                    TAX2Amount = salesOrderDetail["TAX2Amount"]
                    TAX3Perc = salesOrderDetail["TAX3Perc"]
                    TAX3Amount = salesOrderDetail["TAX3Amount"]
                    KFCAmount = salesOrderDetail["KFCAmount"]
                    NetAmount = salesOrderDetail["NetAmount"]
                    BatchCode = salesOrderDetail["BatchCode"]
                    InclusivePrice = salesOrderDetail["InclusivePrice"]
                    detailID = salesOrderDetail["detailID"]

                    try:
                        SerialNos = salesOrderDetail["SerialNos"]
                    except:
                        SerialNos = []

                    try:
                        Description = salesOrderDetail["Description"]
                    except:
                        Description = ""

                    try:
                        ProductTaxID = salesOrderDetail["ProductTaxID"]
                    except:
                        ProductTaxID = ""

                    try:
                        Description = salesOrderDetail["Description"]
                    except:
                        Description = ""

                    if detailID == 0:
                        Action = "M"
                        salesDetail_instance = table.SalesOrderDetails.objects.get(
                            CompanyID=CompanyID, pk=unq_id
                        )
                        SalesOrderDetailsID = salesDetail_instance.SalesOrderDetailsID

                        log_instance = table.SalesOrderDetails_Log.objects.create(
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
                            UpdatedUserID=CreatedUserID,
                            ProductTaxID=ProductTaxID,
                            Description=Description
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
                        salesDetail_instance.UpdatedUserID = CreatedUserID
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
                        salesDetail_instance.Description = Description
                        salesDetail_instance.save()

                    if detailID == 1:
                        SalesOrderDetailsID = get_auto_id(
                            table.SalesOrderDetails, BranchID, CompanyID
                        )
                        Action = "A"

                        log_instance = table.SalesOrderDetails_Log.objects.create(
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
                            UpdatedUserID=CreatedUserID,
                            BatchCode=BatchCode,
                            ProductTaxID=ProductTaxID,
                            Description=Description
                        )

                        table.SalesOrderDetails.objects.create(
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
                            UpdatedUserID=CreatedUserID,
                            BatchCode=BatchCode,
                            LogID=log_instance.ID,
                            ProductTaxID=ProductTaxID,
                            Description=Description
                        )

                    # ======
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
                                CompanyID=CompanyID,
                                VoucherType="SO",
                                SerialNo=SerialNo,
                                ItemCode=ItemCode,
                                SalesMasterID=SalesOrderMasterID,
                                SalesDetailsID=SalesOrderDetailsID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                            )
                    # ======

            # request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sale Orders',
            #              'Edit', 'Sale Orders Updated successfully.', 'Sale Orders Updated successfully.')
            cash_Balance = get_LedgerBalance(CompanyID, 1)
            response_data = {
                "StatusCode": 6000,
                "message": "SalesOrder Updated Successfully!!!",
                "CashBalance": cash_Balance,
                "id": salesOrderMaster_instance.id,
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
            "Sales Order",
            "Create",
            str(e),
            err_descrb,
        )
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def salesApp_salesOrderMaster(request, pk):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]
    instance = None
    if table.SalesOrderMaster.objects.filter(pk=pk).exists():
        instance = table.SalesOrderMaster.objects.get(
            CompanyID=CompanyID, pk=pk)
        serialized = SalesOrderMasterRestSerializer(
            instance, context={"CompanyID": CompanyID,
                               "PriceRounding": PriceRounding}
        )

        response_data = {"StatusCode": 6000, "data": serialized.data}
    else:
        response_data = {"StatusCode": 6001,
                         "message": "Sales Order Master Not Found!"}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def salesApp_delete_salesOrderMaster(request, pk):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]

    try:
        selecte_ids = data["selecte_ids"]
    except:
        selecte_ids = []

    today = datetime.datetime.now()
    instance = None
    if selecte_ids:
        if table.SalesOrderMaster.objects.filter(
            CompanyID=CompanyID, pk__in=selecte_ids
        ).exists():
            instances = table.SalesOrderMaster.objects.filter(
                pk__in=selecte_ids)
    else:
        if table.SalesOrderMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
            instances = table.SalesOrderMaster.objects.filter(pk=pk)

    if instances:
        for instance in instances:
            SalesOrderMasterID = instance.SalesOrderMasterID
            BranchID = instance.BranchID
            VoucherNo = instance.VoucherNo
            Date = instance.Date
            LedgerID = instance.LedgerID
            PriceCategoryID = instance.PriceCategoryID
            CustomerName = instance.CustomerName
            Address1 = instance.Address1
            Address2 = instance.Address2
            Notes = instance.Notes
            FinacialYearID = instance.FinacialYearID
            TotalTax = instance.TotalTax
            NetTotal = instance.NetTotal
            # BillDiscount = instance.BillDiscount
            GrandTotal = instance.GrandTotal
            RoundOff = instance.RoundOff
            IsActive = instance.IsActive
            DeliveryDate = instance.DeliveryDate
            IsInvoiced = instance.IsInvoiced
            VATAmount = instance.VATAmount
            SGSTAmount = instance.SGSTAmount
            CGSTAmount = instance.CGSTAmount
            IGSTAmount = instance.IGSTAmount
            TAX1Amount = instance.TAX1Amount
            TAX2Amount = instance.TAX2Amount
            TAX3Amount = instance.TAX3Amount
            Country_of_Supply = instance.Country_of_Supply
            State_of_Supply = instance.State_of_Supply
            GST_Treatment = instance.GST_Treatment

            Action = "D"

            table.SalesOrderMaster_Log.objects.create(
                CompanyID=CompanyID,
                TransactionID=SalesOrderMasterID,
                BranchID=BranchID,
                Action=Action,
                VoucherNo=VoucherNo,
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
                # BillDiscount=BillDiscount,
                GrandTotal=GrandTotal,
                RoundOff=RoundOff,
                IsActive=IsActive,
                IsInvoiced=IsInvoiced,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                UpdatedUserID=CreatedUserID,
                DeliveryDate=DeliveryDate,
                VATAmount=VATAmount,
                SGSTAmount=SGSTAmount,
                CGSTAmount=CGSTAmount,
                IGSTAmount=IGSTAmount,
                TAX1Amount=TAX1Amount,
                TAX2Amount=TAX2Amount,
                TAX3Amount=TAX3Amount,
                Country_of_Supply=Country_of_Supply,
                State_of_Supply=State_of_Supply,
                GST_Treatment=GST_Treatment,
            )

            instance.delete()

            detail_instances = table.SalesOrderDetails.objects.filter(
                CompanyID=CompanyID,
                SalesOrderMasterID=SalesOrderMasterID,
                BranchID=BranchID,
            )

            for detail_instance in detail_instances:
                SalesOrderDetailsID = detail_instance.SalesOrderDetailsID
                BranchID = detail_instance.BranchID
                SalesOrderMasterID = detail_instance.SalesOrderMasterID
                ProductID = detail_instance.ProductID
                Qty = detail_instance.Qty
                FreeQty = detail_instance.FreeQty
                UnitPrice = detail_instance.UnitPrice
                RateWithTax = detail_instance.RateWithTax
                PriceListID = detail_instance.PriceListID
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
                InclusivePrice = detail_instance.InclusivePrice
                BatchCode = detail_instance.BatchCode
                ProductTaxID = detail_instance.ProductTaxID
                Description = detail_instance.Description

                table.SalesOrderDetails_Log.objects.create(
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
                    NetAmount=NetAmount,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    UpdatedUserID=CreatedUserID,
                    BatchCode=BatchCode,
                    ProductTaxID=ProductTaxID,
                    Description=Description
                )

                detail_instance.delete()

        # request , company, log_type, user, source, action, message, description
        activity_log(
            request._request,
            CompanyID,
            "Information",
            CreatedUserID,
            "Sale Orders",
            "Delete",
            "Sale Orders Deleted successfully.",
            "Sale Orders Deleted successfully",
        )

        response_data = {
            "StatusCode": 6000,
            "message": "Sales Order Master Deleted Successfully!",
        }
    else:
        response_data = {"StatusCode": 6001,
                         "message": "Sales Order Master Not Found!"}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def list_salesApp_expense(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    BranchID = data["BranchID"]
    PriceRounding = data["PriceRounding"]

    page_number = data["page_no"]
    items_per_page = data["items_per_page"]

    FromDate = data["FromDate"]
    ToDate = data["ToDate"]
    search_val = data["search_val"]
    length = len(search_val)
    
    try:
        UserID = request.user.id
    except:
        UserID = data["UserID"]

    instances = None
    count = 0
    voucher_search = False
    if table.ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID,CreatedUserID=UserID).exists():
        instances = table.ExpenseMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, CreatedUserID=UserID)
        if FromDate and ToDate:
            instances = instances.filter(Date__gte=FromDate, Date__lte=ToDate)
        if length > 0 and instances.filter(VoucherNo__icontains=search_val):
            instances = instances.filter(VoucherNo__icontains=search_val)
            voucher_search = True

        expense_ids = instances.filter().values_list('ExpenseMasterID', flat=True)
        if table.ExpenseDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID__in=expense_ids).exists():
            details_ins = table.ExpenseDetails.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID__in=expense_ids)
            if voucher_search == False and length > 0:
                ledger_ids = []
                if table.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerName__icontains=search_val).exists():
                    ledger_ins = table.AccountLedger.objects.filter(
                        CompanyID=CompanyID, LedgerName__icontains=search_val
                    )
                    ledger_ids = ledger_ins.values_list('LedgerID', flat=True)
                details_ins = details_ins.filter(
                    Ledger__LedgerID__in=ledger_ids)
                if length < 3:
                    details_ins = details_ins.filter()[:10]
            else:
                count = len(details_ins)
                details_ins = list_pagination(
                    details_ins, items_per_page, page_number
                )
            expense_serializer = ExpenseListSerializer(
                details_ins,
                many=True,
                context={
                    "request": request,
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                },
            )
            data = expense_serializer.data
            if not data == None:
                response_data = {
                    "StatusCode": 6000,
                    "data": data,
                    "count": count,
                }
            else:
                response_data = {"StatusCode": 6001}
        else:
            response_data = {"StatusCode": 6001}
    else:
        response_data = {"StatusCode": 6001}
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def salesApp_create_expense(request):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data['CompanyID']
            CreatedUserID = data['CreatedUserID']
            PriceRounding = data['PriceRounding']
            CompanyID = get_company(CompanyID)

            today = datetime.datetime.now()
            BranchID = data['BranchID']
            VoucherNo = data['VoucherNo']
            Date = data['Date']
            Supplier = data['Supplier']
            GST_Treatment = data['GST_Treatment']
            Notes = data['Notes']
            TotalGrossAmt = data['TotalGrossAmt']
            TotalTaxableAmount = data['TotalTaxableAmount']
            TotalDiscount = data['TotalDiscount']
            TotalTaxAmount = data['TotalTaxAmount']
            TotalNetAmount = data['TotalNetAmount']
            RoundOff = data['RoundOff']
            GrandTotal = data['GrandTotal']
            TaxInclusive = data['TaxInclusive']
            TaxType = data['TaxType']
            TaxTypeID = data['TaxTypeID']
            TotalVATAmount = data['TotalVATAmount']
            TotalIGSTAmount = data['TotalIGSTAmount']
            TotalSGSTAmount = data['TotalSGSTAmount']
            TotalCGSTAmount = data['TotalCGSTAmount']
            TaxNo = data['TaxNo']
            PaymentMode = data['PaymentMode']
            PaymentID = data['PaymentID']
            Amount = data['MasterAmount']

            IsActive = True

            VoucherType = "EX"
            # VoucherNo Updated
            try:
                PreFix = data['PreFix']
            except:
                PreFix = "EX"

            try:
                Seperator = data['Seperator']
            except:
                Seperator = ""

            try:
                InvoiceNo = data['InvoiceNo']
            except:
                InvoiceNo = 1

            Action = "A"

            Supplier = table.AccountLedger.objects.get(id=Supplier)

            # checking voucher number already exist
            VoucherNoLow = VoucherNo.lower()
            is_voucherExist = False
            insts = table.ExpenseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
            if insts:
                for i in insts:
                    voucher_no = i.VoucherNo
                    voucherNo = voucher_no.lower()
                    if VoucherNoLow == voucherNo:
                        is_voucherExist = True

            check_VoucherNoAutoGenerate = False
            is_ExpenseOK = True

            if table.GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="VoucherNoAutoGenerate").exists():
                check_VoucherNoAutoGenerate = table.GeneralSettings.objects.get(
                    BranchID=BranchID, CompanyID=CompanyID, SettingsType="VoucherNoAutoGenerate").SettingsValue

            if is_voucherExist == True and check_VoucherNoAutoGenerate == "True":
                VoucherNo = get_Genrate_VoucherNo(
                    table.ExpenseMaster, BranchID, CompanyID, "EX")
                is_ExpenseOK = True
            elif is_voucherExist == False:
                is_ExpenseOK = True
            else:
                is_ExpenseOK = False

            Payment = None
            PaymentLedgerID = None
            if PaymentID:
                Payment = table.AccountLedger.objects.get(id=PaymentID)
                PaymentLedgerID = Payment.LedgerID

            if is_ExpenseOK:
                ExpenseMasterID = expenseMasterID(
                    table.ExpenseMaster, BranchID, CompanyID)

                update_voucher_table(
                    CompanyID, CreatedUserID, VoucherType, PreFix, Seperator, InvoiceNo)

                table.ExpenseMaster_Log.objects.create(
                    TransactionID=ExpenseMasterID,
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    Date=Date,
                    Supplier=Supplier,
                    GST_Treatment=GST_Treatment,
                    InvoiceNo=InvoiceNo,
                    Notes=Notes,
                    TotalGrossAmt=TotalGrossAmt,
                    TotalTaxableAmount=TotalTaxableAmount,
                    TotalDiscount=TotalDiscount,
                    TotalTaxAmount=TotalTaxAmount,
                    TotalNetAmount=TotalNetAmount,
                    RoundOff=RoundOff,
                    GrandTotal=GrandTotal,
                    TaxInclusive=TaxInclusive,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    TaxType=TaxType,
                    TaxTypeID=TaxTypeID,
                    TotalVATAmount=TotalVATAmount,
                    TotalIGSTAmount=TotalIGSTAmount,
                    TotalSGSTAmount=TotalSGSTAmount,
                    TotalCGSTAmount=TotalCGSTAmount,
                    TaxNo=TaxNo,
                    BillDiscAmount=TotalDiscount,
                    PaymentMode=PaymentMode,
                    PaymentID=Payment,
                    Amount=Amount
                )

                instance = table.ExpenseMaster.objects.create(
                    ExpenseMasterID=ExpenseMasterID,
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    Date=Date,
                    Supplier=Supplier,
                    GST_Treatment=GST_Treatment,
                    InvoiceNo=InvoiceNo,
                    Notes=Notes,
                    TotalGrossAmt=TotalGrossAmt,
                    TotalTaxableAmount=TotalTaxableAmount,
                    TotalDiscount=TotalDiscount,
                    TotalTaxAmount=TotalTaxAmount,
                    TotalNetAmount=TotalNetAmount,
                    RoundOff=RoundOff,
                    GrandTotal=GrandTotal,
                    TaxInclusive=TaxInclusive,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    TaxType=TaxType,
                    TaxTypeID=TaxTypeID,
                    TotalVATAmount=TotalVATAmount,
                    TotalIGSTAmount=TotalIGSTAmount,
                    TotalSGSTAmount=TotalSGSTAmount,
                    TotalCGSTAmount=TotalCGSTAmount,
                    TaxNo=TaxNo,
                    BillDiscAmount=TotalDiscount,
                    PaymentMode=PaymentMode,
                    PaymentID=Payment,
                    Amount=Amount
                )

                if TaxType == 'VAT':
                    if converted_float(TotalVATAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)

                        # VAT on Expense
                        vat_on_expense = get_BranchLedgerId_for_LedgerPosting(
                            BranchID, CompanyID, 'vat_on_expense')

                        table.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=ExpenseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=vat_on_expense,
                            RelatedLedgerID=Supplier.LedgerID,
                            Debit=TotalVATAmount,
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
                            VoucherMasterID=ExpenseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=vat_on_expense,
                            RelatedLedgerID=Supplier.LedgerID,
                            Debit=TotalVATAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, vat_on_expense, ExpenseMasterID, VoucherType, TotalVATAmount, "Dr", "create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)

                        table.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=ExpenseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=Supplier.LedgerID,
                            RelatedLedgerID=vat_on_expense,
                            Credit=TotalVATAmount,
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
                            VoucherMasterID=ExpenseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=Supplier.LedgerID,
                            RelatedLedgerID=vat_on_expense,
                            Credit=TotalVATAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, TotalVATAmount, "Cr", "create")

                elif TaxType == 'GST Intra-state B2B':
                    if converted_float(TotalCGSTAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)
                        # Central GST on Expense
                        central_gst_on_expense = get_BranchLedgerId_for_LedgerPosting(
                            BranchID, CompanyID, 'central_gst_on_expense')

                        table.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=ExpenseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=central_gst_on_expense,
                            RelatedLedgerID=Supplier.LedgerID,
                            Debit=TotalCGSTAmount,
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
                            VoucherMasterID=ExpenseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=central_gst_on_expense,
                            RelatedLedgerID=Supplier.LedgerID,
                            Debit=TotalCGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, central_gst_on_expense, ExpenseMasterID, VoucherType, TotalCGSTAmount, "Dr", "create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)

                        table.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=ExpenseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=Supplier.LedgerID,
                            RelatedLedgerID=central_gst_on_expense,
                            Credit=TotalCGSTAmount,
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
                            VoucherMasterID=ExpenseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=Supplier.LedgerID,
                            RelatedLedgerID=central_gst_on_expense,
                            Credit=TotalCGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, TotalCGSTAmount, "Cr", "create")

                    if converted_float(TotalSGSTAmount) > 0:

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)
                        # State GST on Payment
                        state_gst_on_payment = get_BranchLedgerId_for_LedgerPosting(
                            BranchID, CompanyID, 'state_gst_on_payment')

                        table.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=ExpenseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=state_gst_on_payment,
                            RelatedLedgerID=Supplier.LedgerID,
                            Debit=TotalSGSTAmount,
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
                            VoucherMasterID=ExpenseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=state_gst_on_payment,
                            RelatedLedgerID=Supplier.LedgerID,
                            Debit=TotalSGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, state_gst_on_payment, ExpenseMasterID, VoucherType, TotalSGSTAmount, "Dr", "create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)

                        table.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=ExpenseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=Supplier.LedgerID,
                            RelatedLedgerID=state_gst_on_payment,
                            Credit=TotalSGSTAmount,
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
                            VoucherMasterID=ExpenseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=Supplier.LedgerID,
                            RelatedLedgerID=state_gst_on_payment,
                            Credit=TotalSGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, TotalSGSTAmount, "Cr", "create")

                elif TaxType == 'GST Inter-state B2B':
                    if converted_float(TotalIGSTAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)
                        # Central GST on Expense
                        central_gst_on_expense = get_BranchLedgerId_for_LedgerPosting(
                            BranchID, CompanyID, 'central_gst_on_expense')

                        table.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=ExpenseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=central_gst_on_expense,
                            RelatedLedgerID=Supplier.LedgerID,
                            Debit=TotalIGSTAmount,
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
                            VoucherMasterID=ExpenseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=central_gst_on_expense,
                            RelatedLedgerID=Supplier.LedgerID,
                            Debit=TotalIGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, central_gst_on_expense, ExpenseMasterID, VoucherType, TotalIGSTAmount, "Dr", "create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            table.LedgerPosting, BranchID, CompanyID)

                        table.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=ExpenseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=Supplier.LedgerID,
                            RelatedLedgerID=central_gst_on_expense,
                            Credit=TotalIGSTAmount,
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
                            VoucherMasterID=ExpenseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=Supplier.LedgerID,
                            RelatedLedgerID=central_gst_on_expense,
                            Credit=TotalIGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, TotalIGSTAmount, "Cr", "create")

                if converted_float(RoundOff) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)
                    # Round off Purchase
                    round_off_purchase = get_BranchLedgerId_for_LedgerPosting(
                        BranchID, CompanyID, 'round_off_purchase')

                    table.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=round_off_purchase,
                        RelatedLedgerID=Supplier.LedgerID,
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
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=round_off_purchase,
                        RelatedLedgerID=Supplier.LedgerID,
                        Debit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, round_off_purchase, ExpenseMasterID, VoucherType, RoundOff, "Dr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=round_off_purchase,
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
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=round_off_purchase,
                        Credit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, RoundOff, "Cr", "create")

                if converted_float(RoundOff) < 0:
                    # Round off Purchase
                    round_off_purchase = get_BranchLedgerId_for_LedgerPosting(
                        BranchID, CompanyID, 'round_off_purchase')

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    RoundOff = abs(converted_float(RoundOff))

                    table.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=round_off_purchase,
                        RelatedLedgerID=Supplier.LedgerID,
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
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=round_off_purchase,
                        RelatedLedgerID=Supplier.LedgerID,
                        Credit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, round_off_purchase, ExpenseMasterID, VoucherType, RoundOff, "Cr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=round_off_purchase,
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
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=round_off_purchase,
                        Debit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, RoundOff, "Dr", "create")

                if converted_float(TotalDiscount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)
                    # Discount on Purchase
                    discount_on_purchase = get_BranchLedgerId_for_LedgerPosting(
                        BranchID, CompanyID, 'discount_on_purchase')

                    table.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=discount_on_purchase,
                        RelatedLedgerID=Supplier.LedgerID,
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
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=discount_on_purchase,
                        RelatedLedgerID=Supplier.LedgerID,
                        Credit=TotalDiscount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, discount_on_purchase, ExpenseMasterID, VoucherType, TotalDiscount, "Cr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=discount_on_purchase,
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
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=discount_on_purchase,
                        Debit=TotalDiscount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, TotalDiscount, "Dr", "create")

                if converted_float(Amount) > 0:
                    # payment LedgerPosting
                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PaymentLedgerID,
                        RelatedLedgerID=Supplier.LedgerID,
                        Credit=Amount,
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
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PaymentLedgerID,
                        RelatedLedgerID=Supplier.LedgerID,
                        Credit=Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, PaymentLedgerID, ExpenseMasterID, VoucherType, Amount, "Cr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=PaymentLedgerID,
                        Debit=Amount,
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
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=PaymentLedgerID,
                        Debit=Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, Amount, "Dr", "create")

                LedgerID = data['LedgerID']
                Amount = data['Amount']
                TaxID = data['TaxID']
                DiscountAmount = converted_float(
                    data['DiscountAmount'])
                TaxableAmount = converted_float(
                    data['TaxableAmount'])
                TaxPerc = converted_float(data['TaxPerc'])
                TaxAmount = converted_float(data['TaxAmount'])
                NetTotal = converted_float(data['Total'])
                VATPerc = converted_float(data['VATPerc'])
                VATAmount = converted_float(data['VATAmount'])
                IGSTPerc = converted_float(data['IGSTPerc'])
                IGSTAmount = converted_float(
                    data['IGSTAmount'])
                SGSTPerc = converted_float(data['SGSTPerc'])
                SGSTAmount = converted_float(
                    data['SGSTAmount'])
                CGSTPerc = converted_float(data['CGSTPerc'])
                CGSTAmount = converted_float(
                    data['CGSTAmount'])

                Ledger = table.AccountLedger.objects.get(id=LedgerID)
                if not TaxID:
                    TaxID = None

                ExpenseDetailsID = expenseDetailID(
                    table.ExpenseDetails, BranchID, CompanyID)

                log_instance = table.ExpenseDetails_Log.objects.create(
                    CompanyID=CompanyID,
                    TransactionID=ExpenseDetailsID,
                    BranchID=BranchID,
                    Action=Action,
                    ExpenseMasterID=ExpenseMasterID,
                    Ledger=Ledger,
                    Amount=Amount,
                    TaxID=TaxID,
                    TaxableAmount=TaxableAmount,
                    DiscountAmount=DiscountAmount,
                    TaxPerc=TaxPerc,
                    TaxAmount=TaxAmount,
                    NetTotal=NetTotal,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    VATPerc=VATPerc,
                    VATAmount=VATAmount,
                    IGSTPerc=IGSTPerc,
                    IGSTAmount=IGSTAmount,
                    SGSTPerc=SGSTPerc,
                    SGSTAmount=SGSTAmount,
                    CGSTPerc=CGSTPerc,
                    CGSTAmount=CGSTAmount,
                )
                detail_ins = table.ExpenseDetails.objects.create(
                    CompanyID=CompanyID,
                    ExpenseDetailsID=ExpenseDetailsID,
                    BranchID=BranchID,
                    Action=Action,
                    ExpenseMasterID=ExpenseMasterID,
                    Ledger=Ledger,
                    Amount=Amount,
                    TaxID=TaxID,
                    TaxableAmount=TaxableAmount,
                    DiscountAmount=DiscountAmount,
                    TaxPerc=TaxPerc,
                    TaxAmount=TaxAmount,
                    NetTotal=NetTotal,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    VATPerc=VATPerc,
                    VATAmount=VATAmount,
                    IGSTPerc=IGSTPerc,
                    IGSTAmount=IGSTAmount,
                    SGSTPerc=SGSTPerc,
                    SGSTAmount=SGSTAmount,
                    CGSTPerc=CGSTPerc,
                    CGSTAmount=CGSTAmount,
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID)

                table.LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ExpenseMasterID,
                    VoucherDetailID=ExpenseDetailsID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=Ledger.LedgerID,
                    RelatedLedgerID=Supplier.LedgerID,
                    Debit=Amount,
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
                    VoucherMasterID=ExpenseMasterID,
                    VoucherDetailID=ExpenseDetailsID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=Ledger.LedgerID,
                    RelatedLedgerID=Supplier.LedgerID,
                    Debit=Amount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, Ledger.LedgerID, ExpenseMasterID, VoucherType, Amount, "Dr", "create")

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID)

                table.LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ExpenseMasterID,
                    VoucherDetailID=ExpenseDetailsID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=Supplier.LedgerID,
                    RelatedLedgerID=Ledger.LedgerID,
                    Credit=Amount,
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
                    VoucherMasterID=ExpenseMasterID,
                    VoucherDetailID=ExpenseDetailsID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=Supplier.LedgerID,
                    RelatedLedgerID=Ledger.LedgerID,
                    Credit=Amount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, Amount, "Cr", "create")

                response_data = {
                    "StatusCode": 6000,
                    "id": instance.id,
                    "detail_unq": detail_ins.id,
                    "message": "Expense created Successfully!!!",
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Expense',
                             'Create', 'Expense created Failed.', 'VoucherNo already exist')
                response_data = {
                    "StatusCode": 6001,
                    "message": "VoucherNo already exist.Please Change Your Prefix!"
                }

                return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("======================exception test")
        print(exc_type, fname, exc_tb.tb_lineno)
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again",
            "err_descrb": err_descrb
        }

        # transaction.rollback()
        # transaction.set_rollback(True)
        # transaction.set_rollback(False)
        activity_id = activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Expense',
                                   'Create', str(e), err_descrb)
        body_params = str(request.data)
        table.Activity_Log.objects.filter(
            id=activity_id).update(body_params=body_params)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def salesApp_edit_expense(request, pk):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data['CompanyID']
            CreatedUserID = data['CreatedUserID']
            PriceRounding = data['PriceRounding']
            CompanyID = get_company(CompanyID)

            today = datetime.datetime.now()
            detail_instance = table.ExpenseDetails.objects.get(pk=pk)
            ExpenseMasterID = detail_instance.ExpenseMasterID
            BranchID = detail_instance.BranchID
            expense_instance = table.ExpenseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).first()
            VoucherNo = expense_instance.VoucherNo

            Date = data['Date']
            Supplier = data['Supplier']
            GST_Treatment = data['GST_Treatment']
            Notes = data['Notes']
            TotalGrossAmt = data['TotalGrossAmt']
            TotalTaxableAmount = data['TotalTaxableAmount']
            TotalDiscount = data['TotalDiscount']
            TotalTaxAmount = data['TotalTaxAmount']
            TotalNetAmount = data['TotalNetAmount']
            RoundOff = data['RoundOff']
            GrandTotal = data['GrandTotal']
            TaxInclusive = data['TaxInclusive']
            TaxType = data['TaxType']
            TaxTypeID = data['TaxTypeID']
            TotalVATAmount = data['TotalVATAmount']
            TotalIGSTAmount = data['TotalIGSTAmount']
            TotalSGSTAmount = data['TotalSGSTAmount']
            TotalCGSTAmount = data['TotalCGSTAmount']
            TaxNo = data['TaxNo']
            PaymentMode = data['PaymentMode']
            PaymentID = data['PaymentID']
            Amount = data['MasterAmount']

            IsActive = True

            VoucherType = "EX"
            # VoucherNo Updated
            try:
                PreFix = data['PreFix']
            except:
                PreFix = "EX"

            try:
                Seperator = data['Seperator']
            except:
                Seperator = ""

            try:
                InvoiceNo = data['InvoiceNo']
            except:
                InvoiceNo = 1

            Action = "M"

            Supplier = table.AccountLedger.objects.get(id=Supplier)
            Payment = None
            PaymentLedgerID = None
            if PaymentID:
                Payment = table.AccountLedger.objects.get(id=PaymentID)
                PaymentLedgerID = Payment.LedgerID

            table.ExpenseMaster_Log.objects.create(
                TransactionID=ExpenseMasterID,
                CompanyID=CompanyID,
                BranchID=BranchID,
                Action=Action,
                VoucherNo=VoucherNo,
                Date=Date,
                Supplier=Supplier,
                GST_Treatment=GST_Treatment,
                InvoiceNo=InvoiceNo,
                Notes=Notes,
                TotalGrossAmt=TotalGrossAmt,
                TotalTaxableAmount=TotalTaxableAmount,
                TotalDiscount=TotalDiscount,
                TotalTaxAmount=TotalTaxAmount,
                TotalNetAmount=TotalNetAmount,
                RoundOff=RoundOff,
                GrandTotal=GrandTotal,
                TaxInclusive=TaxInclusive,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                TaxType=TaxType,
                TaxTypeID=TaxTypeID,
                TotalVATAmount=TotalVATAmount,
                TotalIGSTAmount=TotalIGSTAmount,
                TotalSGSTAmount=TotalSGSTAmount,
                TotalCGSTAmount=TotalCGSTAmount,
                TaxNo=TaxNo,
                BillDiscAmount=TotalDiscount,
                PaymentMode=PaymentMode,
                PaymentID=Payment,
                Amount=Amount
            )

            update_ledger = UpdateLedgerBalance(
                CompanyID, BranchID, 0, ExpenseMasterID, "EX", 0, "Cr", "update")

            if table.LedgerPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=ExpenseMasterID, BranchID=BranchID, VoucherType="EX").exists():
                ledgerPostInstances = table.LedgerPosting.objects.filter(
                    CompanyID=CompanyID, VoucherMasterID=ExpenseMasterID, BranchID=BranchID, VoucherType="EX").delete()

            expense_instance.Action = Action
            expense_instance.Date = Date
            expense_instance.Supplier = Supplier
            expense_instance.GST_Treatment = GST_Treatment
            expense_instance.MasterInvoiceNo = InvoiceNo
            expense_instance.Notes = Notes
            expense_instance.TotalGrossAmt = TotalGrossAmt
            expense_instance.TotalTaxableAmount = TotalTaxableAmount
            expense_instance.TotalDiscount = TotalDiscount
            expense_instance.TotalTaxAmount = TotalTaxAmount
            expense_instance.TotalNetAmount = TotalNetAmount
            expense_instance.RoundOff = RoundOff
            expense_instance.GrandTotal = GrandTotal
            expense_instance.TaxInclusive = TaxInclusive
            expense_instance.UpdatedDate = today
            expense_instance.CreatedUserID = CreatedUserID
            expense_instance.TaxType = TaxType
            expense_instance.TaxTypeID = TaxTypeID
            expense_instance.TotalVATAmount = TotalVATAmount
            expense_instance.TotalIGSTAmount = TotalIGSTAmount
            expense_instance.TotalSGSTAmount = TotalSGSTAmount
            expense_instance.TotalCGSTAmount = TotalCGSTAmount
            expense_instance.TaxNo = TaxNo
            expense_instance.BillDiscAmount = TotalDiscount
            expense_instance.PaymentMode = PaymentMode
            expense_instance.PaymentID = Payment
            expense_instance.Amount = Amount
            expense_instance.save()

            if TaxType == 'VAT':
                if converted_float(TotalVATAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)
                    # VAT on Expense
                    vat_on_expense = get_BranchLedgerId_for_LedgerPosting(
                        BranchID, CompanyID, 'vat_on_expense')

                    table.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=vat_on_expense,
                        RelatedLedgerID=Supplier.LedgerID,
                        Debit=TotalVATAmount,
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
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=vat_on_expense,
                        RelatedLedgerID=Supplier.LedgerID,
                        Debit=TotalVATAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, vat_on_expense, ExpenseMasterID, VoucherType, TotalVATAmount, "Dr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=vat_on_expense,
                        Credit=TotalVATAmount,
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
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=vat_on_expense,
                        Credit=TotalVATAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, TotalVATAmount, "Cr", "create")

            elif TaxType == 'GST Intra-state B2B':
                if converted_float(TotalCGSTAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    # Central GST on Expense
                    central_gst_on_expense = get_BranchLedgerId_for_LedgerPosting(
                        BranchID, CompanyID, 'central_gst_on_expense')

                    table.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=central_gst_on_expense,
                        RelatedLedgerID=Supplier.LedgerID,
                        Debit=TotalCGSTAmount,
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
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=central_gst_on_expense,
                        RelatedLedgerID=Supplier.LedgerID,
                        Debit=TotalCGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, central_gst_on_expense, ExpenseMasterID, VoucherType, TotalCGSTAmount, "Dr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=central_gst_on_expense,
                        Credit=TotalCGSTAmount,
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
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=central_gst_on_expense,
                        Credit=TotalCGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, TotalCGSTAmount, "Cr", "create")

                if converted_float(TotalSGSTAmount) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)
                    # State GST on Payment
                    state_gst_on_payment = get_BranchLedgerId_for_LedgerPosting(
                        BranchID, CompanyID, 'state_gst_on_payment')

                    table.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=state_gst_on_payment,
                        RelatedLedgerID=Supplier.LedgerID,
                        Debit=TotalSGSTAmount,
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
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=state_gst_on_payment,
                        RelatedLedgerID=Supplier.LedgerID,
                        Debit=TotalSGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, state_gst_on_payment, ExpenseMasterID, VoucherType, TotalSGSTAmount, "Dr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=state_gst_on_payment,
                        Credit=TotalSGSTAmount,
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
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=state_gst_on_payment,
                        Credit=TotalSGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, TotalSGSTAmount, "Cr", "create")

            elif TaxType == 'GST Inter-state B2B':
                if converted_float(TotalIGSTAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)
                    # Central GST on Expense
                    central_gst_on_expense = get_BranchLedgerId_for_LedgerPosting(
                        BranchID, CompanyID, 'central_gst_on_expense')

                    table.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=central_gst_on_expense,
                        RelatedLedgerID=Supplier.LedgerID,
                        Debit=TotalIGSTAmount,
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
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=central_gst_on_expense,
                        RelatedLedgerID=Supplier.LedgerID,
                        Debit=TotalIGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, central_gst_on_expense, ExpenseMasterID, VoucherType, TotalIGSTAmount, "Dr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        table.LedgerPosting, BranchID, CompanyID)

                    table.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=central_gst_on_expense,
                        Credit=TotalIGSTAmount,
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
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=central_gst_on_expense,
                        Credit=TotalIGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, TotalIGSTAmount, "Cr", "create")

            if converted_float(RoundOff) > 0:

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID)
                # Round off Purchase
                round_off_purchase = get_BranchLedgerId_for_LedgerPosting(
                    BranchID, CompanyID, 'round_off_purchase')

                table.LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ExpenseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=round_off_purchase,
                    RelatedLedgerID=Supplier.LedgerID,
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
                    VoucherMasterID=ExpenseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=round_off_purchase,
                    RelatedLedgerID=Supplier.LedgerID,
                    Debit=RoundOff,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, round_off_purchase, ExpenseMasterID, VoucherType, RoundOff, "Dr", "create")

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID)

                table.LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ExpenseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=Supplier.LedgerID,
                    RelatedLedgerID=round_off_purchase,
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
                    VoucherMasterID=ExpenseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=Supplier.LedgerID,
                    RelatedLedgerID=round_off_purchase,
                    Credit=RoundOff,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, RoundOff, "Cr", "create")

            if converted_float(RoundOff) < 0:
                # Round off Purchase
                round_off_purchase = get_BranchLedgerId_for_LedgerPosting(
                    BranchID, CompanyID, 'round_off_purchase')
                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID)

                RoundOff = abs(converted_float(RoundOff))

                table.LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ExpenseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=round_off_purchase,
                    RelatedLedgerID=Supplier.LedgerID,
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
                    VoucherMasterID=ExpenseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=round_off_purchase,
                    RelatedLedgerID=Supplier.LedgerID,
                    Credit=RoundOff,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, round_off_purchase, ExpenseMasterID, VoucherType, RoundOff, "Cr", "create")

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID)

                table.LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ExpenseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=Supplier.LedgerID,
                    RelatedLedgerID=round_off_purchase,
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
                    VoucherMasterID=ExpenseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=Supplier.LedgerID,
                    RelatedLedgerID=round_off_purchase,
                    Debit=RoundOff,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, RoundOff, "Dr", "create")

            if converted_float(TotalDiscount) > 0:

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID)
                # Discount on Purchase
                discount_on_purchase = get_BranchLedgerId_for_LedgerPosting(
                    BranchID, CompanyID, 'discount_on_purchase')

                table.LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ExpenseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=discount_on_purchase,
                    RelatedLedgerID=Supplier.LedgerID,
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
                    VoucherMasterID=ExpenseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=discount_on_purchase,
                    RelatedLedgerID=Supplier.LedgerID,
                    Credit=TotalDiscount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, discount_on_purchase, ExpenseMasterID, VoucherType, TotalDiscount, "Cr", "create")

                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID)

                table.LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ExpenseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=Supplier.LedgerID,
                    RelatedLedgerID=discount_on_purchase,
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
                    VoucherMasterID=ExpenseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=Supplier.LedgerID,
                    RelatedLedgerID=discount_on_purchase,
                    Debit=TotalDiscount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, TotalDiscount, "Dr", "create")

            # payment LedgerPosting
            if converted_float(Amount) > 0:
                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID)
                table.LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ExpenseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PaymentLedgerID,
                    RelatedLedgerID=Supplier.LedgerID,
                    Credit=Amount,
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
                    VoucherMasterID=ExpenseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PaymentLedgerID,
                    RelatedLedgerID=Supplier.LedgerID,
                    Credit=Amount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, PaymentLedgerID, ExpenseMasterID, VoucherType, Amount, "Cr", "create")
                LedgerPostingID = get_auto_LedgerPostid(
                    table.LedgerPosting, BranchID, CompanyID)

                table.LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ExpenseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=Supplier.LedgerID,
                    RelatedLedgerID=PaymentLedgerID,
                    Debit=Amount,
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
                    VoucherMasterID=ExpenseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=Supplier.LedgerID,
                    RelatedLedgerID=PaymentLedgerID,
                    Debit=Amount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

            update_ledger = UpdateLedgerBalance(
                CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, Amount, "Dr", "create")

            LedgerID = data['LedgerID']
            Amount = data['Amount']
            TaxID = data['TaxID']
            DiscountAmount = converted_float(
                data['DiscountAmount'])
            TaxableAmount = converted_float(
                data['TaxableAmount'])
            TaxPerc = converted_float(data['TaxPerc'])
            TaxAmount = converted_float(data['TaxAmount'])
            NetTotal = converted_float(data['Total'])
            VATPerc = converted_float(data['VATPerc'])
            VATAmount = converted_float(data['VATAmount'])
            IGSTPerc = converted_float(data['IGSTPerc'])
            IGSTAmount = converted_float(data['IGSTAmount'])
            SGSTPerc = converted_float(data['SGSTPerc'])
            SGSTAmount = converted_float(data['SGSTAmount'])
            CGSTPerc = converted_float(data['CGSTPerc'])
            CGSTAmount = converted_float(data['CGSTAmount'])

            Ledger = table.AccountLedger.objects.get(id=LedgerID)
            if not TaxID:
                TaxID = None

            ExpenseDetailsID = detail_instance.ExpenseDetailsID

            log_instance = table.ExpenseDetails_Log.objects.create(
                CompanyID=CompanyID,
                TransactionID=ExpenseDetailsID,
                BranchID=BranchID,
                Action=Action,
                ExpenseMasterID=ExpenseMasterID,
                Ledger=Ledger,
                Amount=Amount,
                TaxID=TaxID,
                TaxableAmount=TaxableAmount,
                DiscountAmount=DiscountAmount,
                TaxPerc=TaxPerc,
                TaxAmount=TaxAmount,
                NetTotal=NetTotal,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                VATPerc=VATPerc,
                VATAmount=VATAmount,
                IGSTPerc=IGSTPerc,
                IGSTAmount=IGSTAmount,
                SGSTPerc=SGSTPerc,
                SGSTAmount=SGSTAmount,
                CGSTPerc=CGSTPerc,
                CGSTAmount=CGSTAmount,
            )

            detail_instance.Action = Action
            detail_instance.Ledger = Ledger
            detail_instance.Amount = Amount
            detail_instance.TaxID = TaxID
            detail_instance.TaxableAmount = TaxableAmount
            detail_instance.DiscountAmount = DiscountAmount
            detail_instance.TaxPerc = TaxPerc
            detail_instance.TaxAmount = TaxAmount
            detail_instance.NetTotal = NetTotal
            detail_instance.UpdatedDate = today
            detail_instance.CreatedUserID = CreatedUserID
            detail_instance.VATPerc = VATPerc
            detail_instance.VATAmount = VATAmount
            detail_instance.IGSTPerc = IGSTPerc
            detail_instance.IGSTAmount = IGSTAmount
            detail_instance.SGSTPerc = SGSTPerc
            detail_instance.SGSTAmount = SGSTAmount
            detail_instance.CGSTPerc = CGSTPerc
            detail_instance.CGSTAmount = CGSTAmount

            detail_instance.save()
            LedgerPostingID = get_auto_LedgerPostid(
                table.LedgerPosting, BranchID, CompanyID)

            table.LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=ExpenseMasterID,
                VoucherDetailID=ExpenseDetailsID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=Ledger.LedgerID,
                RelatedLedgerID=Supplier.LedgerID,
                Debit=Amount,
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
                VoucherMasterID=ExpenseMasterID,
                VoucherDetailID=ExpenseDetailsID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=Ledger.LedgerID,
                RelatedLedgerID=Supplier.LedgerID,
                Debit=Amount,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )

            update_ledger = UpdateLedgerBalance(
                CompanyID, BranchID, Ledger.LedgerID, ExpenseMasterID, VoucherType, Amount, "Dr", "create")

            LedgerPostingID = get_auto_LedgerPostid(
                table.LedgerPosting, BranchID, CompanyID)

            table.LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=ExpenseMasterID,
                VoucherDetailID=ExpenseDetailsID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=Supplier.LedgerID,
                RelatedLedgerID=Ledger.LedgerID,
                Credit=Amount,
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
                VoucherMasterID=ExpenseMasterID,
                VoucherDetailID=ExpenseDetailsID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=Supplier.LedgerID,
                RelatedLedgerID=Ledger.LedgerID,
                Credit=Amount,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )

            update_ledger = UpdateLedgerBalance(
                CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, Amount, "Cr", "edit")

            response_data = {
                "StatusCode": 6000,
                "message": "Expense Updated Successfully!!!",
                "id": expense_instance.id,
                "detail_unq": detail_instance.id,
            }

            return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("======================exception test")
        print(exc_type, fname, exc_tb.tb_lineno)
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again",
            "err_descrb": err_descrb
        }

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Expense',
                     'Edit', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def salesApp_expense(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    CreatedUserID = data['CreatedUserID']

    if table.ExpenseDetails.objects.filter(pk=pk).exists():
        instance = table.ExpenseDetails.objects.get(pk=pk)
        serialized = ExpenseListSerializer(
            instance, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding})

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data,
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Expense Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def salesApp_delete_expense(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    detail_ins = None
    if table.ExpenseDetails.objects.filter(pk=pk).exists():
        detail_ins = table.ExpenseDetails.objects.get(pk=pk)
    instances = None
    instances = None
    if detail_ins:
        BranchID = detail_ins.BranchID
        ExpenseMasterID = detail_ins.ExpenseMasterID
        if table.ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).exists():
            instance = table.ExpenseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).first()
    ledgerPostInstances = None

    if instance:
        ExpenseMasterID = instance.ExpenseMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        VoucherType = "EX"
        Date = instance.Date
        Supplier = instance.Supplier
        GST_Treatment = instance.GST_Treatment
        PlaceOfSupply = instance.PlaceOfSupply
        MasterInvoiceNo = instance.InvoiceNo
        Notes = instance.Notes
        PaymentMode = instance.PaymentMode
        Payment = instance.PaymentID
        Amount = instance.Amount
        BillDiscPercent = instance.BillDiscPercent
        BillDiscAmount = instance.BillDiscAmount
        TotalGrossAmt = instance.TotalGrossAmt
        TotalTaxableAmount = instance.TotalTaxableAmount
        TotalDiscount = instance.TotalDiscount
        TotalTaxAmount = instance.TotalTaxAmount
        TotalNetAmount = instance.TotalNetAmount
        RoundOff = instance.RoundOff
        GrandTotal = instance.GrandTotal
        TaxInclusive = instance.TaxInclusive
        CreatedUserID = instance.CreatedUserID
        TaxType = instance.TaxType
        TaxTypeID = instance.TaxTypeID
        TotalVATAmount = instance.TotalVATAmount
        TotalIGSTAmount = instance.TotalIGSTAmount
        TotalSGSTAmount = instance.TotalSGSTAmount
        TotalCGSTAmount = instance.TotalCGSTAmount
        Action = "D"

        table.ExpenseMaster_Log.objects.create(
            TransactionID=ExpenseMasterID,
            CompanyID=CompanyID,
            BranchID=BranchID,
            Action=Action,
            VoucherNo=VoucherNo,
            Date=Date,
            Supplier=Supplier,
            GST_Treatment=GST_Treatment,
            PlaceOfSupply=PlaceOfSupply,
            InvoiceNo=MasterInvoiceNo,
            Notes=Notes,
            PaymentMode=PaymentMode,
            PaymentID=Payment,
            Amount=Amount,
            BillDiscPercent=BillDiscPercent,
            BillDiscAmount=BillDiscAmount,
            TotalGrossAmt=TotalGrossAmt,
            TotalTaxableAmount=TotalTaxableAmount,
            TotalDiscount=TotalDiscount,
            TotalTaxAmount=TotalTaxAmount,
            TotalNetAmount=TotalNetAmount,
            RoundOff=RoundOff,
            GrandTotal=GrandTotal,
            TaxInclusive=TaxInclusive,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            TaxType=TaxType,
            TaxTypeID=TaxTypeID,
            TotalVATAmount=TotalVATAmount,
            TotalIGSTAmount=TotalIGSTAmount,
            TotalSGSTAmount=TotalSGSTAmount,
            TotalCGSTAmount=TotalCGSTAmount,
        )

        detail_instances = table.ExpenseDetails.objects.filter(
            CompanyID=CompanyID, ExpenseMasterID=ExpenseMasterID, BranchID=BranchID)

        for detail_instance in detail_instances:
            ExpenseDetailsID = detail_instance.ExpenseDetailsID
            BranchID = detail_instance.BranchID
            ExpenseMasterID = detail_instance.ExpenseMasterID
            Ledger = detail_instance.Ledger
            Amount = detail_instance.Amount
            TaxID = detail_instance.TaxID
            TaxableAmount = detail_instance.TaxableAmount
            DiscountAmount = detail_instance.DiscountAmount
            TaxPerc = detail_instance.TaxPerc
            TaxAmount = detail_instance.TaxAmount
            NetTotal = detail_instance.NetTotal
            CreatedDate = detail_instance.CreatedDate
            UpdatedDate = detail_instance.UpdatedDate
            CreatedUserID = detail_instance.CreatedUserID
            VATPerc = detail_instance.VATPerc
            VATAmount = detail_instance.VATAmount
            IGSTPerc = detail_instance.IGSTPerc
            IGSTAmount = detail_instance.IGSTAmount
            SGSTPerc = detail_instance.SGSTPerc
            SGSTAmount = detail_instance.SGSTAmount
            CGSTPerc = detail_instance.CGSTPerc
            CGSTAmount = detail_instance.CGSTAmount

            log_instance = table.ExpenseDetails_Log.objects.create(
                CompanyID=CompanyID,
                TransactionID=ExpenseDetailsID,
                BranchID=BranchID,
                Action=Action,
                ExpenseMasterID=ExpenseMasterID,
                Ledger=Ledger,
                Amount=Amount,
                TaxID=TaxID,
                TaxableAmount=TaxableAmount,
                DiscountAmount=DiscountAmount,
                TaxPerc=TaxPerc,
                TaxAmount=TaxAmount,
                NetTotal=NetTotal,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                VATPerc=VATPerc,
                VATAmount=VATAmount,
                IGSTPerc=IGSTPerc,
                IGSTAmount=IGSTAmount,
                SGSTPerc=SGSTPerc,
                SGSTAmount=SGSTAmount,
                CGSTPerc=CGSTPerc,
                CGSTAmount=CGSTAmount,
            )

            detail_instance.delete()

        if table.LedgerPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=ExpenseMasterID, BranchID=BranchID, VoucherType=VoucherType).exists():
            ledgerPostInstances = table.LedgerPosting.objects.filter(
                CompanyID=CompanyID, VoucherMasterID=ExpenseMasterID, BranchID=BranchID, VoucherType=VoucherType)

            update_ledger = UpdateLedgerBalance(
                CompanyID, BranchID, 0, ExpenseMasterID, VoucherType, 0, "Cr", "update")
            for ledgerPostInstance in ledgerPostInstances:

                LedgerPostingID = ledgerPostInstance.LedgerPostingID
                VoucherType = ledgerPostInstance.VoucherType
                Debit = ledgerPostInstance.Debit
                Credit = ledgerPostInstance.Credit
                IsActive = ledgerPostInstance.IsActive
                Date = ledgerPostInstance.Date
                LedgerID = ledgerPostInstance.LedgerID
                CreatedUserID = ledgerPostInstance.CreatedUserID

                table.LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ExpenseMasterID,
                    VoucherNo=VoucherNo,
                    VoucherType=VoucherType,
                    LedgerID=LedgerID,
                    Debit=Debit,
                    Credit=Credit,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                ledgerPostInstance.delete()

        instance.delete()

        response_data = {
            "StatusCode": 6000,
            "message": "Expense Master Deleted Successfully!",
            "title": "Success",
        }
    else:
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID,
                     'Expense', 'Delete', 'Expense Deleted Failed.', 'Expense Not Found!')
        response_data = {
            "StatusCode": 6001,
            "message": "Expense Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def list_stock_order(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    BranchID = data["BranchID"]
    PriceRounding = data["PriceRounding"]

    page_number = data["page_no"]
    items_per_page = data["items_per_page"]

    FromDate = data["FromDate"]
    ToDate = data["ToDate"]
    WarehouseFromID = data["WarehouseFromID"]
    WarehouseToID = data["WarehouseToID"]
    search_val = data["search_val"]
    length = len(search_val)
    
    try:
        UserID = request.user.id
    except:
        UserID = data["UserID"]

    instances = None
    count = 0
    if table.StockTransferMaster_ID.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherType="STO",CreatedUserID=UserID).exists():
        instances = table.StockTransferMaster_ID.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, VoucherType="STO", CreatedUserID=UserID)

        if FromDate and ToDate:
            instances = instances.filter(Date__gte=FromDate, Date__lte=ToDate)
        if WarehouseFromID:
            instances = instances.filter(WarehouseFromID=WarehouseFromID)
        if WarehouseToID:
            instances = instances.filter(WarehouseToID=WarehouseToID)

        if length > 0:
            instances = instances.filter(
                CompanyID=CompanyID, BranchID=BranchID, VoucherNo__icontains=search_val)
            if length < 3:
                instances = instances.filter()[:10]
        else:
            count = len(instances)
            instances = list_pagination(
                instances, items_per_page, page_number
            )
    if instances:
        stock_order_serializer = StockOrderListSerializer(
            instances,
            many=True,
            context={
                "request": request,
                "CompanyID": CompanyID,
                "PriceRounding": PriceRounding,
            },
        )
        data = stock_order_serializer.data
        if not data == None or data:
            response_data = {
                "StatusCode": 6000,
                "data": data,
                "count": count,
            }
        else:
            response_data = {"StatusCode": 6001}
    else:
        response_data = {"StatusCode": 6001}
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def salesApp_create_stockOrder(request):
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
            WarehouseFromID = data["WarehouseFromID"]
            WarehouseToID = data["WarehouseToID"]
            TotalQty = data["TotalQty"]
            GrandTotal = data["GrandTotal"]
            IsActive = data["IsActive"]

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
            StockTransferMasterID = stockmasterid(
                table.StockTransferMaster_ID, BranchID, CompanyID
            )
            # VoucherNo = get_auto_VoucherNo(StockTransferMaster_ID,BranchID)
            table.StockTransferMasterID_Log.objects.create(
                TransactionID=StockTransferMasterID,
                BranchID=BranchID,
                VoucherNo=VoucherNo,
                Date=Date,
                Notes=Notes,
                WarehouseFromID=WarehouseFromID,
                WarehouseToID=WarehouseToID,
                TotalQty=TotalQty,
                GrandTotal=GrandTotal,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                CompanyID=CompanyID,
                BranchFromID=BranchFromID,
                BranchToID=BranchToID,
                VoucherType=VoucherType
            )

            stock_transfer_create = table.StockTransferMaster_ID.objects.create(
                StockTransferMasterID=StockTransferMasterID,
                BranchID=BranchID,
                VoucherNo=VoucherNo,
                Date=Date,
                Notes=Notes,
                WarehouseFromID=WarehouseFromID,
                WarehouseToID=WarehouseToID,
                TotalQty=TotalQty,
                GrandTotal=GrandTotal,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                CompanyID=CompanyID,
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
                Amount = i["Amount"]

                StockTransferDetailsID = stockdetailsid(
                    table.StockTransferDetails, BranchID, CompanyID
                )

                log_instance = table.StockTransferDetails_Log.objects.create(
                    TransactionID=StockTransferDetailsID,
                    BranchID=BranchID,
                    StockTransferMasterID=StockTransferMasterID,
                    ProductID=ProductID,
                    Qty=Qty,
                    PriceListID=PriceListID,
                    Rate=Rate,
                    Action=Action,
                    CompanyID=CompanyID,
                    Amount=Amount
                )
                table.StockTransferDetails.objects.create(
                    StockTransferDetailsID=StockTransferDetailsID,
                    BranchID=BranchID,
                    StockTransferMasterID=StockTransferMasterID,
                    ProductID=ProductID,
                    Qty=Qty,
                    PriceListID=PriceListID,
                    Rate=Rate,
                    Action=Action,
                    CompanyID=CompanyID,
                    LogID=log_instance.ID,
                    Amount=Amount
                )

            response_data = {
                "id": stock_transfer_create.id,
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
        table.Activity_Log.objects.filter(
            id=activity_id).update(body_params=body_params)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def salesApp_edit_stockOrder(request, pk):
    try:
        with transaction.atomic():
            today = datetime.datetime.now()
            data = request.data
            CreatedUserID = data["CreatedUserID"]
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

            try:
                BranchFromID = data["BranchFromID"]
            except:
                BranchFromID = 1

            try:
                BranchToID = data["BranchToID"]
            except:
                BranchToID = 1

            stockTransferMaster_instance = table.StockTransferMaster_ID.objects.get(
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

            table.StockTransferMasterID_Log.objects.create(
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
                        if table.StockTransferDetails.objects.filter(
                            CompanyID=CompanyID, pk=deleted_pk
                        ).exists():
                            deleted_detail = table.StockTransferDetails.objects.filter(
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

                if detailID == 0:
                    stockTransferDetail_instance = table.StockTransferDetails.objects.get(
                        pk=pk
                    )
                    StockTransferDetailsID = (
                        stockTransferDetail_instance.StockTransferDetailsID
                    )

                    log_instance = table.StockTransferDetails_Log.objects.create(
                        TransactionID=StockTransferDetailsID,
                        BranchID=BranchID,
                        StockTransferMasterID=StockTransferMasterID,
                        ProductID=ProductID,
                        Qty=Qty_detail,
                        PriceListID=PriceListID,
                        Rate=Rate,
                        Action=Action,
                        CompanyID=CompanyID,
                    )

                    stockTransferDetail_instance.ProductID = ProductID
                    stockTransferDetail_instance.Qty = Qty_detail
                    stockTransferDetail_instance.PriceListID = PriceListID
                    stockTransferDetail_instance.Rate = Rate
                    stockTransferDetail_instance.Action = Action
                    stockTransferDetail_instance.LogID = log_instance.ID

                    stockTransferDetail_instance.save()

                if detailID == 1:
                    Action = "A"

                    log_instance = table.StockTransferDetails_Log.objects.create(
                        TransactionID=StockTransferDetailsID,
                        BranchID=BranchID,
                        StockTransferMasterID=StockTransferMasterID,
                        ProductID=ProductID,
                        Qty=Qty_detail,
                        PriceListID=PriceListID,
                        Rate=Rate,
                        Action=Action,
                        CompanyID=CompanyID,
                    )
                    table.StockTransferDetails.objects.create(
                        StockTransferDetailsID=StockTransferDetailsID,
                        BranchID=BranchID,
                        StockTransferMasterID=StockTransferMasterID,
                        ProductID=ProductID,
                        Qty=Qty_detail,
                        PriceListID=PriceListID,
                        Rate=Rate,
                        Action=Action,
                        CompanyID=CompanyID,
                        LogID=log_instance.ID,
                    )

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
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def salesApp_stockOrderMasterID(request, pk):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]
    if table.StockTransferMaster_ID.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = table.StockTransferMaster_ID.objects.get(
            CompanyID=CompanyID, pk=pk)

        serialized = StockTransferMaster_IDRestSerializer(
            instance, context={"CompanyID": CompanyID,
                               "PriceRounding": PriceRounding}
        )
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
def salesApp_delete_stockOrderMasterID(request, pk):
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
        if table.StockTransferMaster_ID.objects.filter(
            CompanyID=CompanyID, pk__in=selecte_ids
        ).exists():
            instances = table.StockTransferMaster_ID.objects.filter(
                pk__in=selecte_ids)
    else:
        if table.StockTransferMaster_ID.objects.filter(CompanyID=CompanyID, pk=pk).exists():
            instances = table.StockTransferMaster_ID.objects.filter(pk=pk)

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

            detail_instances = table.StockTransferDetails.objects.filter(
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

                table.StockTransferDetails_Log.objects.create(
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

            table.StockTransferMasterID_Log.objects.create(
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


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def list_stock_transfer(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    BranchID = data["BranchID"]
    PriceRounding = data["PriceRounding"]

    page_number = data["page_no"]
    items_per_page = data["items_per_page"]

    FromDate = data["FromDate"]
    ToDate = data["ToDate"]
    WarehouseFromID = data["WarehouseFromID"]
    WarehouseToID = data["WarehouseToID"]
    search_val = data["search_val"]
    length = len(search_val)
    
    try:
        UserID = request.user.id
    except:
        UserID = data["UserID"]

    instances = None
    count = 0
    if table.StockTransferMaster_ID.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherType="ST", CreatedUserID=UserID).exists():
        instances = table.StockTransferMaster_ID.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, VoucherType="ST",CreatedUserID=UserID)

        if not FromDate == 0 and not ToDate == 0:
            instances = instances.filter(Date__gte=FromDate, Date__lte=ToDate)
        if not WarehouseFromID == 0:
            instances = instances.filter(WarehouseFromID=WarehouseFromID)
        if not WarehouseToID == 0:
            instances = instances.filter(WarehouseToID=WarehouseToID)

        if length > 0:
            instances = instances.filter(
                CompanyID=CompanyID, BranchID=BranchID, VoucherNo__icontains=search_val)
            if length < 3:
                instances = instances.filter()[:10]
        else:
            count = len(instances)
            instances = list_pagination(
                instances, items_per_page, page_number
            )
    if instances:
        stock_order_serializer = StockOrderListSerializer(
            instances,
            many=True,
            context={
                "request": request,
                "CompanyID": CompanyID,
                "PriceRounding": PriceRounding,
            },
        )
        data = stock_order_serializer.data
        if not data == None:
            response_data = {
                "StatusCode": 6000,
                "data": data,
                "count": count,
            }
        else:
            response_data = {"StatusCode": 6001}
    else:
        response_data = {"StatusCode": 6001}
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def salesApp_create_stockTransfer(request):
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
            WarehouseFromID = data["WarehouseFromID"]
            WarehouseToID = data["WarehouseToID"]
            TotalQty = data["TotalQty"]
            GrandTotal = data["GrandTotal"]
            IsActive = data["IsActive"]

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

            if table.StockTransferMaster_ID.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherNo=StockOrderNo).exists():
                stock_order = table.StockTransferMaster_ID.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, VoucherNo=StockOrderNo).first()
                stock_order.IsTaken = True
                stock_order.save()

            update_voucher_table(
                CompanyID, CreatedUserID, VoucherType, PreFix, Seperator, InvoiceNo
            )
            StockTransferMasterID = stockmasterid(
                table.StockTransferMaster_ID, BranchID, CompanyID
            )
            # VoucherNo = get_auto_VoucherNo(StockTransferMaster_ID,BranchID)
            table.StockTransferMasterID_Log.objects.create(
                TransactionID=StockTransferMasterID,
                BranchID=BranchID,
                VoucherNo=VoucherNo,
                Date=Date,
                Notes=Notes,
                WarehouseFromID=WarehouseFromID,
                WarehouseToID=WarehouseToID,
                TotalQty=TotalQty,
                GrandTotal=GrandTotal,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                CompanyID=CompanyID,
                BranchFromID=BranchFromID,
                BranchToID=BranchToID,
                VoucherType=VoucherType,
                StockOrderNo=StockOrderNo,
            )

            stock_transfer_create = table.StockTransferMaster_ID.objects.create(
                StockTransferMasterID=StockTransferMasterID,
                BranchID=BranchID,
                VoucherNo=VoucherNo,
                Date=Date,
                Notes=Notes,
                WarehouseFromID=WarehouseFromID,
                WarehouseToID=WarehouseToID,
                TotalQty=TotalQty,
                GrandTotal=GrandTotal,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                CompanyID=CompanyID,
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
                Amount = i["Amount"]

                StockTransferDetailsID = stockdetailsid(
                    table.StockTransferDetails, BranchID, CompanyID
                )

                log_instance = table.StockTransferDetails_Log.objects.create(
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
                table.StockTransferDetails.objects.create(
                    StockTransferDetailsID=StockTransferDetailsID,
                    BranchID=BranchID,
                    StockTransferMasterID=StockTransferMasterID,
                    ProductID=ProductID,
                    Qty=Qty,
                    PriceListID=PriceListID,
                    Rate=Rate,
                    Amount=Amount,
                    Action=Action,
                    CompanyID=CompanyID,
                    LogID=log_instance.ID,
                )

                MultiFactor = table.PriceList.objects.get(
                    CompanyID=CompanyID, PriceListID=PriceListID
                ).MultiFactor
                PriceListID = table.PriceList.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True
                ).PriceListID

                princeList_instance = table.PriceList.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID
                )
                PurchasePrice = princeList_instance.PurchasePrice
                SalesPrice = princeList_instance.SalesPrice

                Qty = converted_float(MultiFactor) * converted_float(Qty)
                Cost = converted_float(Rate) / converted_float(MultiFactor)

                princeList_instance = table.PriceList.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID
                )
                PurchasePrice = princeList_instance.PurchasePrice
                SalesPrice = princeList_instance.SalesPrice

                # transfer from warehouse stock post

                StockPostingID = get_auto_stockPostid(
                    table.StockPosting, BranchFromID, CompanyID
                )

                pricelist, warehouse = get_ModelInstance(
                    CompanyID, BranchID, PriceListID, WarehouseFromID
                )

                table.StockPosting.objects.create(
                    StockPostingID=StockPostingID,
                    BranchID=BranchFromID,
                    Action=Action,
                    Date=Date,
                    VoucherMasterID=StockTransferMasterID,
                    VoucherDetailID=StockTransferDetailsID,
                    VoucherType=VoucherType,
                    ProductID=ProductID,
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

                table.StockPosting_Log.objects.create(
                    TransactionID=StockPostingID,
                    BranchID=BranchFromID,
                    Action=Action,
                    Date=Date,
                    VoucherMasterID=StockTransferMasterID,
                    VoucherDetailID=StockTransferDetailsID,
                    VoucherType=VoucherType,
                    ProductID=ProductID,
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
                    table.StockPosting, BranchToID, CompanyID
                )

                pricelist, warehouse = get_ModelInstance(
                    CompanyID, BranchID, PriceListID, WarehouseToID
                )

                table.StockPosting.objects.create(
                    StockPostingID=StockPostingID,
                    BranchID=BranchToID,
                    Action=Action,
                    Date=Date,
                    VoucherMasterID=StockTransferMasterID,
                    VoucherDetailID=StockTransferDetailsID,
                    VoucherType=VoucherType,
                    ProductID=ProductID,
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

                table.StockPosting_Log.objects.create(
                    TransactionID=StockPostingID,
                    BranchID=BranchToID,
                    Action=Action,
                    Date=Date,
                    VoucherMasterID=StockTransferMasterID,
                    VoucherDetailID=StockTransferDetailsID,
                    VoucherType=VoucherType,
                    ProductID=ProductID,
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
        table.Activity_Log.objects.filter(
            id=activity_id).update(body_params=body_params)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def salesApp_edit_stockTransfer(request, pk):
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

            try:
                BranchFromID = data["BranchFromID"]
            except:
                BranchFromID = 1

            try:
                BranchToID = data["BranchToID"]
            except:
                BranchToID = 1

            stockTransferMaster_instance = table.StockTransferMaster_ID.objects.get(
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

            table.StockTransferMasterID_Log.objects.create(
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
                BranchFromID=BranchFromID,
                BranchToID=BranchToID,
                VoucherType=VoucherType,
            )

            if table.StockTransferDetails.objects.filter(
                CompanyID=CompanyID, StockTransferMasterID=StockTransferMasterID
            ).exists():
                stockTransferInstances = table.StockTransferDetails.objects.filter(
                    CompanyID=CompanyID, StockTransferMasterID=StockTransferMasterID
                )
                for i in stockTransferInstances:
                    if not table.StockPosting.objects.filter(
                        CompanyID=CompanyID,
                        VoucherMasterID=StockTransferMasterID,
                        VoucherDetailID=i.StockTransferDetailsID,
                        VoucherType="ST",
                    ).exists():
                        table.StockPosting.objects.filter(
                            CompanyID=CompanyID,
                            VoucherMasterID=StockTransferMasterID,
                            VoucherDetailID=i.StockTransferDetailsID,
                            VoucherType="ST",
                        ).delete()

                    instance_MultiFactor = table.PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=i.PriceListID
                    ).MultiFactor

                    instance_qty_sum = converted_float(i.Qty)
                    instance_Qty = converted_float(
                        instance_MultiFactor
                    ) * converted_float(instance_qty_sum)
                    if table.StockPosting.objects.filter(
                        CompanyID=CompanyID,
                        WareHouseID=instance_to_warehouse,
                        VoucherMasterID=StockTransferMasterID,
                        VoucherDetailID=i.StockTransferDetailsID,
                        ProductID=i.ProductID,
                        VoucherType="ST",
                    ).exists():
                        stock_inst = table.StockPosting.objects.filter(
                            CompanyID=CompanyID,
                            WareHouseID=instance_to_warehouse,
                            VoucherMasterID=StockTransferMasterID,
                            VoucherDetailID=i.StockTransferDetailsID,
                            ProductID=i.ProductID,
                            VoucherType="ST",
                        ).first()
                        stock_inst.QtyIn = converted_float(
                            stock_inst.QtyIn
                        ) - converted_float(instance_Qty)
                        stock_inst.save()
                        update_stock(CompanyID, BranchID, i.ProductID)

                    if table.StockPosting.objects.filter(
                        CompanyID=CompanyID,
                        WareHouseID=instance_from_warehouse,
                        VoucherMasterID=StockTransferMasterID,
                        VoucherDetailID=i.StockTransferDetailsID,
                        ProductID=i.ProductID,
                        VoucherType="ST",
                    ).exists():
                        stock_inst = table.StockPosting.objects.filter(
                            CompanyID=CompanyID,
                            WareHouseID=instance_from_warehouse,
                            VoucherMasterID=StockTransferMasterID,
                            VoucherDetailID=i.StockTransferDetailsID,
                            ProductID=i.ProductID,
                            VoucherType="ST",
                        ).first()
                        stock_inst.QtyOut = converted_float(
                            stock_inst.QtyIn
                        ) - converted_float(instance_Qty)
                        stock_inst.save()
                        update_stock(CompanyID, BranchID, i.ProductID)

            stockTransferMaster_instance.Date = Date
            stockTransferMaster_instance.Notes = Notes
            stockTransferMaster_instance.TransferredByID = TransferredByID
            stockTransferMaster_instance.WarehouseFromID = WarehouseFromID
            stockTransferMaster_instance.WarehouseToID = WarehouseToID
            stockTransferMaster_instance.TotalQty = TotalQty
            stockTransferMaster_instance.GrandTotal = GrandTotal
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

                    if salesApp_edit_stockTransfer.objects.filter(
                        CompanyID=CompanyID,
                        ProductID=ProductID_Deleted,
                        DefaultUnit=True,
                    ).exists():
                        priceList = table.PriceList.objects.get(
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
                            if table.StockTransferDetails.objects.filter(
                                CompanyID=CompanyID, pk=deleted_pk
                            ).exists():
                                deleted_detail = table.StockTransferDetails.objects.filter(
                                    CompanyID=CompanyID, pk=deleted_pk
                                )
                                deleted_detail.delete()

                                if table.StockPosting.objects.filter(
                                    CompanyID=CompanyID,
                                    VoucherMasterID=StockTransferMasterID_Deleted,
                                    VoucherDetailID=StockTransferDetailsID_Deleted,
                                    ProductID=ProductID_Deleted,
                                    VoucherType="ST",
                                ).exists():
                                    stock_instances_delete = table.StockPosting.objects.filter(
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

            stockTransferDetails = data["StockTransferDetails"]
            table.StockPosting.objects.filter(
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
                Amount = stockTransferDetail["Amount"]

                MultiFactor = table.PriceList.objects.get(
                    CompanyID=CompanyID, PriceListID=PriceListID
                ).MultiFactor
                PriceListID_DefUnit = table.PriceList.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True
                ).PriceListID

                Qty = converted_float(MultiFactor) * \
                    converted_float(Qty_detail)
                Cost = converted_float(Rate) / converted_float(MultiFactor)

                princeList_instance = table.PriceList.objects.get(
                    CompanyID=CompanyID,
                    ProductID=ProductID,
                    PriceListID=PriceListID_DefUnit,
                )
                PurchasePrice = princeList_instance.PurchasePrice
                SalesPrice = princeList_instance.SalesPrice

                product_is_Service = table.Product.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID
                ).is_Service

                StockTransferDetailsID = get_auto_id(
                    table.StockTransferDetails, BranchID, CompanyID
                )

                if detailID == 0:
                    stockTransferDetail_instance = table.StockTransferDetails.objects.get(
                        pk=pk
                    )
                    StockTransferDetailsID = (
                        stockTransferDetail_instance.StockTransferDetailsID
                    )

                    log_instance = table.StockTransferDetails_Log.objects.create(
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
                    stockTransferDetail_instance.Amount = Amount
                    stockTransferDetail_instance.Action = Action
                    stockTransferDetail_instance.LogID = log_instance.ID

                    stockTransferDetail_instance.save()
                    if product_is_Service == False:
                        pricelist, warehouse = get_ModelInstance(
                            CompanyID, BranchID, PriceListID, WarehouseToID
                        )

                if detailID == 1:
                    Action = "A"

                    log_instance = table.StockTransferDetails_Log.objects.create(
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
                    table.StockTransferDetails.objects.create(
                        StockTransferDetailsID=StockTransferDetailsID,
                        BranchID=BranchID,
                        StockTransferMasterID=StockTransferMasterID,
                        ProductID=ProductID,
                        Qty=Qty,
                        PriceListID=PriceListID,
                        Rate=Rate,
                        Amount=Amount,
                        Action=Action,
                        CompanyID=CompanyID,
                        LogID=log_instance.ID,
                    )
                    pricelist, warehouse = get_ModelInstance(
                        CompanyID, BranchToID, PriceListID, WarehouseToID
                    )

                # transfer from warehouse stock post

                StockPostingID = get_auto_stockPostid(
                    table.StockPosting, BranchFromID, CompanyID
                )

                pricelist, warehouse = get_ModelInstance(
                    CompanyID, BranchID, PriceListID, WarehouseFromID
                )

                table.StockPosting.objects.create(
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

                table.StockPosting_Log.objects.create(
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
                    table.StockPosting, BranchToID, CompanyID
                )

                pricelist, warehouse = get_ModelInstance(
                    CompanyID, BranchID, PriceListID, WarehouseToID
                )

                table.StockPosting.objects.create(
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

                table.StockPosting_Log.objects.create(
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
        table.Activity_Log.objects.filter(
            id=activity_id).update(body_params=body_params)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def salesApp_stockTransferMasterID(request, pk):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]
    if table.StockTransferMaster_ID.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = table.StockTransferMaster_ID.objects.get(
            CompanyID=CompanyID, pk=pk)
        serialized = StockTransferMaster_IDRestSerializer(
            instance, context={"CompanyID": CompanyID,
                               "PriceRounding": PriceRounding}
        )
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
def salesApp_delete_stockTransferMasterID(request, pk):
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
        if table.StockTransferMaster_ID.objects.filter(
            CompanyID=CompanyID, pk__in=selecte_ids
        ).exists():
            instances = table.StockTransferMaster_ID.objects.filter(
                pk__in=selecte_ids)
    else:
        if table.StockTransferMaster_ID.objects.filter(CompanyID=CompanyID, pk=pk).exists():
            instances = table.StockTransferMaster_ID.objects.filter(pk=pk)

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

            if table.StockPosting.objects.filter(
                CompanyID=CompanyID,
                VoucherType="ST",
                VoucherMasterID=StockTransferMasterID,
            ).exists():
                table.StockPosting.objects.filter(
                    CompanyID=CompanyID,
                    VoucherType="ST",
                    VoucherMasterID=StockTransferMasterID,
                ).delete()

            detail_instances = table.StockTransferDetails.objects.filter(
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

                table.StockTransferDetails_Log.objects.create(
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

            table.StockTransferMasterID_Log.objects.create(
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
def salesApp_summary(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    BranchID = data["BranchID"]
    FromDate = data["FromDate"]
    ToDate = data["ToDate"]
    
    try:
        UserID = request.user.id
    except:
        UserID = data["UserID"]

    Gross_Sale = 0
    TaxOnSales = 0
    TotalSales = 0
    GrossReturn = 0
    TaxOnReturn = 0
    TotalReturn = 0
    CashSale = 0
    BankSale = 0
    CreditSale = 0
    CashReceipt = 0
    BankReceipt = 0
    CashPayments = 0
    BankPayments = 0
    Expense = 0
    
    # cash sale
    cash_ids = table.AccountLedger.objects.filter(CompanyID=CompanyID, AccountGroupUnder=9).values_list("LedgerID", flat=True)
    if table.LedgerPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID,LedgerID__in=cash_ids,VoucherType="SI", Date__gte=FromDate, Date__lte=ToDate,CreatedUserID=UserID).exists():
        ledger_ins = table.LedgerPosting.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID__in=cash_ids, VoucherType="SI", Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID)
        DebitSum = ledger_ins.aggregate(Sum("Debit"))
        DebitSum = DebitSum["Debit__sum"]
        CreditSum = ledger_ins.aggregate(Sum("Credit"))
        CreditSum = CreditSum["Credit__sum"]
        CashSale = converted_float(DebitSum) - converted_float(CreditSum)
        
    # bank sale
    bank_ids = table.AccountLedger.objects.filter(CompanyID=CompanyID, AccountGroupUnder=8).values_list("LedgerID", flat=True)
    if table.LedgerPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID,LedgerID__in=bank_ids,VoucherType="SI", Date__gte=FromDate, Date__lte=ToDate,CreatedUserID=UserID).exists():
        ledger_ins = table.LedgerPosting.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID__in=bank_ids, VoucherType="SI", Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID)
        DebitSum = ledger_ins.aggregate(Sum("Debit"))
        DebitSum = DebitSum["Debit__sum"]
        CreditSum = ledger_ins.aggregate(Sum("Credit"))
        CreditSum = CreditSum["Credit__sum"]
        BankSale = converted_float(DebitSum) - converted_float(CreditSum)
        
    # credit sale
    party_ids = []
    if table.AccountLedger.objects.filter(CompanyID=CompanyID, AccountGroupUnder__in=[10, 29]).exists():
        party_ids = table.AccountLedger.objects.filter(
                CompanyID=CompanyID, AccountGroupUnder__in=[10, 29]).values_list("LedgerID", flat=True)
        if table.SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID,LedgerID__in=party_ids, Date__gte=FromDate, Date__lte=ToDate,CreatedUserID=UserID).exists():
            credit_sale_ins = table.SalesMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID__in=party_ids, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID)
            credit_sale_ins = credit_sale_ins.filter(GrandTotal__gt=(F('CashReceived')+ F('BankAmount')))
            credit_sum_ins = credit_sale_ins.aggregate(CreditSum=Sum((F('GrandTotal') - (F('CashReceived') + F('BankAmount')))))
            CreditSale = credit_sum_ins["CreditSum"]
    

    if table.SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate,CreatedUserID=UserID).exists():
        sales_ins = table.SalesMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate,CreatedUserID=UserID)
        Gross_Sale = sales_ins.aggregate(Sum("TotalGrossAmt"))
        TaxOnSales = sales_ins.aggregate(Sum("TotalTax"))
        TotalSales = sales_ins.aggregate(Sum("GrandTotal"))
        Gross_Sale = Gross_Sale["TotalGrossAmt__sum"]
        TaxOnSales = TaxOnSales["TotalTax__sum"]
        TotalSales = TotalSales["GrandTotal__sum"]
    
    
    if table.SalesReturnMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate,CreatedUserID=UserID).exists():
        sales_ins = table.SalesReturnMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate,CreatedUserID=UserID)
        GrossReturn = sales_ins.aggregate(Sum("TotalGrossAmt"))
        TaxOnReturn = sales_ins.aggregate(Sum("TotalTax"))
        TotalReturn = sales_ins.aggregate(Sum("GrandTotal"))
        GrossReturn = GrossReturn["TotalGrossAmt__sum"]
        TaxOnReturn = TaxOnReturn["TotalTax__sum"]
        TotalReturn = TotalReturn["GrandTotal__sum"]

    if table.ReceiptMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherType="CR",Date__gte=FromDate, Date__lte=ToDate,CreatedUserID=UserID).exists():
        cash_receipt_ins = table.ReceiptMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, VoucherType="CR", Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID)
        CashReceipt = cash_receipt_ins.aggregate(Sum("TotalAmount"))
        CashReceipt = CashReceipt["TotalAmount__sum"]

    if table.ReceiptMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherType="BR",Date__gte=FromDate, Date__lte=ToDate,CreatedUserID=UserID).exists():
        bank_receipt_ins = table.ReceiptMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, VoucherType="BR",Date__gte=FromDate, Date__lte=ToDate,CreatedUserID=UserID)
        BankReceipt = bank_receipt_ins.aggregate(Sum("TotalAmount"))
        BankReceipt = BankReceipt["TotalAmount__sum"]

    if table.PaymentMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherType="CP",Date__gte=FromDate, Date__lte=ToDate,CreatedUserID=UserID).exists():
        cash_payment_ins = table.PaymentMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, VoucherType="CP",Date__gte=FromDate, Date__lte=ToDate,CreatedUserID=UserID)
        CashPayments = cash_payment_ins.aggregate(Sum("TotalAmount"))
        CashPayments = CashPayments["TotalAmount__sum"]

    if table.PaymentMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherType="BP",Date__gte=FromDate, Date__lte=ToDate,CreatedUserID=UserID).exists():
        bank_payment_ins = table.PaymentMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, VoucherType="BP",Date__gte=FromDate, Date__lte=ToDate,CreatedUserID=UserID)
        BankPayments = bank_payment_ins.aggregate(Sum("TotalAmount"))
        BankPayments = BankPayments["TotalAmount__sum"]

    if table.ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID,Date__gte=FromDate, Date__lte=ToDate,CreatedUserID=UserID).exists():
        expense_ins = table.ExpenseMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID)
        Expense = expense_ins.aggregate(Sum("GrandTotal"))
        Expense = Expense["GrandTotal__sum"]

    NetCash = (converted_float(CashSale) + converted_float(BankSale) + converted_float(
        CashReceipt) + converted_float(BankReceipt)) - converted_float(CashPayments) + (converted_float(BankPayments) + converted_float(Expense))
    response_data = {
        "StatusCode": 6000,
        "Gross_Sale": Gross_Sale,
        "TaxOnSales": TaxOnSales,
        "TotalSales": TotalSales,
        "GrossReturn": GrossReturn,
        "TaxOnReturn": TaxOnReturn,
        "TotalReturn": TotalReturn,
        "CashSale": CashSale,
        "BankSale": BankSale,
        "CreditSale": CreditSale,
        "CashReceipt": CashReceipt,
        "BankReceipt": BankReceipt,
        "CashPayments": CashPayments,
        "BankPayments": BankPayments,
        "Expense": Expense,
        "NetCash": NetCash,
    }
    return Response(response_data, status=status.HTTP_200_OK)


# @api_view(["POST"])
# @permission_classes((IsAuthenticated,))
# @authentication_classes((JWTTokenUserAuthentication,))
# @renderer_classes((JSONRenderer,))
# def salesApp_dashboard(request):
#     data = request.data
#     CompanyID = data["CompanyID"]
#     CompanyID = get_company(CompanyID)
#     BranchID = data["BranchID"]
#     UserID = data["UserID"]
#     financial_years = get_financial_year_dates(CompanyID)
#     FromDate = financial_years[0]
#     ToDate = financial_years[1]

#     data = []
#     TotalSales = 0
#     TotalReturn = 0
#     CashBalance = 0
#     BankBalance = 0
#     TotalExpense = 0
#     if table.SalesMaster.objects.filter(CompanyID=CompanyID,Date__gte=FromDate,Date__lte=ToDate,CreatedUserID=UserID).exists():
#         sales_ins = table.SalesMaster.objects.filter(CompanyID=CompanyID, Date__gte=FromDate, Date__lte=ToDate,CreatedUserID=UserID)
#         # this filter will take queryset from each month
#         sum_each = sales_ins.annotate(month=TruncMonth('Date')).values(
#             'month').annotate(c=Sum('GrandTotal')).values('month', 'c').order_by()

#         for i in sum_each:
#             date = i["month"]
#             total = i["c"]
#             month = date.strftime('%B')
#             result = {
#                 "month": month,
#                 "total": total
#             }
#             data.append(result)

#         TotalSales = sales_ins.aggregate(Sum("GrandTotal"))
#         TotalSales = TotalSales["GrandTotal__sum"]

#     if table.SalesReturnMaster.objects.filter(CompanyID=CompanyID,VoucherDate__gte=FromDate,VoucherDate__lte=ToDate,CreatedUserID=UserID).exists():
#         return_ins = table.SalesReturnMaster.objects.filter(CompanyID=CompanyID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate,CreatedUserID=UserID)
#         TotalReturn = return_ins.aggregate(Sum("GrandTotal"))
#         TotalReturn = TotalReturn["GrandTotal__sum"]

#     cash_ledgerids = table.AccountLedger.objects.filter(CompanyID=CompanyID, AccountGroupUnder=9).values_list("LedgerID",flat=True)
#     bank_ledgerids = table.AccountLedger.objects.filter(CompanyID=CompanyID, AccountGroupUnder=8).values_list("LedgerID",flat=True)
#     if table.LedgerPosting.objects.filter(CompanyID=CompanyID, LedgerID__in=cash_ledgerids, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID).exists():
#         cash_ins = table.LedgerPosting.objects.filter(CompanyID=CompanyID, LedgerID__in=cash_ledgerids, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID)
#         DebitSum = cash_ins.aggregate(Sum("Debit"))
#         DebitSum = DebitSum["Debit__sum"]
#         CreditSum = cash_ins.aggregate(Sum("Credit"))
#         CreditSum = CreditSum["Credit__sum"]
#         CashBalance = converted_float(DebitSum) - converted_float(CreditSum)

#     if table.LedgerPosting.objects.filter(CompanyID=CompanyID, LedgerID__in=bank_ledgerids, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID).exists():
#         bank_ins = table.LedgerPosting.objects.filter(CompanyID=CompanyID, LedgerID__in=bank_ledgerids, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID)
#         DebitSum = bank_ins.aggregate(Sum("Debit"))
#         DebitSum = DebitSum["Debit__sum"]
#         CreditSum = bank_ins.aggregate(Sum("Credit"))
#         CreditSum = CreditSum["Credit__sum"]
#         BankBalance = converted_float(DebitSum) - converted_float(CreditSum)

#     if table.ExpenseMaster.objects.filter(CompanyID=CompanyID,Date__gte=FromDate,Date__lte=ToDate,CreatedUserID=UserID).exists():
#         expense_ins = table.ExpenseMaster.objects.filter(CompanyID=CompanyID, Date__gte=FromDate, Date__lte=ToDate,CreatedUserID=UserID)
#         TotalExpense = expense_ins.aggregate(Sum("GrandTotal"))
#         TotalExpense = TotalExpense["GrandTotal__sum"]

#     response_data = {
#         "StatusCode": 6000,
#         "data": data,
#         "TotalSales": TotalSales,
#         "TotalReturn": TotalReturn,
#         "CashBalance": CashBalance,
#         "BankBalance": BankBalance,
#         "TotalExpense": TotalExpense,
#     }
#     return Response(response_data, status=status.HTTP_200_OK)


# @api_view(["POST"])
# @permission_classes((IsAuthenticated,))
# @authentication_classes((JWTTokenUserAuthentication,))
# @renderer_classes((JSONRenderer,))
# def salesApp_dashboard(request):
#     data = request.data
#     CompanyID = data["CompanyID"]
#     CompanyID = get_company(CompanyID)
#     BranchID = data["BranchID"]
#     UserID = data["UserID"]
#     financial_years = get_financial_year_dates(CompanyID)
#     FromDate = financial_years[0]
#     ToDate = financial_years[1]

#     data = []
#     TotalSales = 0
#     TotalReturn = 0
#     CashBalance = 0
#     BankBalance = 0
#     TotalExpense = 0
#     this_month = datetime.datetime.now().month
#     if table.SalesMaster.objects.filter(CompanyID=CompanyID, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID).exists():
#         sales_ins = table.SalesMaster.objects.filter(
#             CompanyID=CompanyID, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID)
#         # this filter will take queryset from each month
#         # sum_each = sales_ins.annotate(month=TruncMonth('Date')).values(
#         #     'month').annotate(c=Sum('GrandTotal')).values('month', 'c').order_by()
#         sum_each = sales_ins.values('Date').order_by(
#             'Date').annotate(sum=Sum('GrandTotal'))[:60]

#         for i in sum_each:
#             date = i["Date"]
#             total = i["sum"]
#             month = date.strftime('%B')
#             result = {
#                 "date": date,
#                 "total": total
#             }
#             data.append(result)

#         TotalSales = sales_ins.aggregate(Sum("GrandTotal"))
#         TotalSales = TotalSales["GrandTotal__sum"]

#     if table.SalesReturnMaster.objects.filter(CompanyID=CompanyID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate, CreatedUserID=UserID).exists():
#         return_ins = table.SalesReturnMaster.objects.filter(
#             CompanyID=CompanyID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate, CreatedUserID=UserID)
#         TotalReturn = return_ins.aggregate(Sum("GrandTotal"))
#         TotalReturn = TotalReturn["GrandTotal__sum"]

#     cash_ledgerids = table.AccountLedger.objects.filter(
#         CompanyID=CompanyID, AccountGroupUnder=9).values_list("LedgerID", flat=True)
#     bank_ledgerids = table.AccountLedger.objects.filter(
#         CompanyID=CompanyID, AccountGroupUnder=8).values_list("LedgerID", flat=True)
#     if table.LedgerPosting.objects.filter(CompanyID=CompanyID, LedgerID__in=cash_ledgerids, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID).exists():
#         cash_ins = table.LedgerPosting.objects.filter(
#             CompanyID=CompanyID, LedgerID__in=cash_ledgerids, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID)
#         DebitSum = cash_ins.aggregate(Sum("Debit"))
#         DebitSum = DebitSum["Debit__sum"]
#         CreditSum = cash_ins.aggregate(Sum("Credit"))
#         CreditSum = CreditSum["Credit__sum"]
#         CashBalance = converted_float(DebitSum) - converted_float(CreditSum)

#     if table.LedgerPosting.objects.filter(CompanyID=CompanyID, LedgerID__in=bank_ledgerids, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID).exists():
#         bank_ins = table.LedgerPosting.objects.filter(
#             CompanyID=CompanyID, LedgerID__in=bank_ledgerids, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID)
#         DebitSum = bank_ins.aggregate(Sum("Debit"))
#         DebitSum = DebitSum["Debit__sum"]
#         CreditSum = bank_ins.aggregate(Sum("Credit"))
#         CreditSum = CreditSum["Credit__sum"]
#         BankBalance = converted_float(DebitSum) - converted_float(CreditSum)

#     if table.ExpenseMaster.objects.filter(CompanyID=CompanyID, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID).exists():
#         expense_ins = table.ExpenseMaster.objects.filter(
#             CompanyID=CompanyID, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID)
#         TotalExpense = expense_ins.aggregate(Sum("GrandTotal"))
#         TotalExpense = TotalExpense["GrandTotal__sum"]

#     response_data = {
#         "StatusCode": 6000,
#         "data": data,
#         "TotalSales": TotalSales,
#         "TotalReturn": TotalReturn,
#         "CashBalance": CashBalance,
#         "BankBalance": BankBalance,
#         "TotalExpense": TotalExpense
#     }
#     return Response(response_data, status=status.HTTP_200_OK)



@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def salesApp_dashboard(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    BranchID = data["BranchID"]
    UserID = data["UserID"]
    financial_years = get_financial_year_dates(CompanyID)
    FromDate = financial_years[0]
    ToDate = financial_years[1]

    data = []
    TotalSales = 0
    TotalReturn = 0
    CashBalance = 0
    BankBalance = 0
    TotalExpense = 0
    this_month = datetime.datetime.now().month
    print("========================================")
    print(this_month)
    if table.SalesMaster.objects.filter(CompanyID=CompanyID, Date__month=this_month, CreatedUserID=UserID).exists():
        sales_ins = table.SalesMaster.objects.filter(
            CompanyID=CompanyID, Date__month=this_month, CreatedUserID=UserID)
        # this filter will take queryset from each month
        # sum_each = sales_ins.annotate(month=TruncMonth('Date')).values(
        #     'month').annotate(c=Sum('GrandTotal')).values('month', 'c').order_by()
        sum_each = sales_ins.values('Date').order_by(
            'Date').annotate(sum=Sum('GrandTotal'))

        for i in sum_each:
            date = i["Date"]
            total = i["sum"]
            month = date.strftime('%B')
            result = {
                "date": date,
                "total": total
            }
            data.append(result)
        TotalSales = sales_ins.aggregate(Sum("GrandTotal"))
        TotalSales = TotalSales["GrandTotal__sum"]
        print(TotalSales,"TotalSales")
    if table.SalesReturnMaster.objects.filter(CompanyID=CompanyID, VoucherDate__month=this_month, CreatedUserID=UserID).exists():
        return_ins = table.SalesReturnMaster.objects.filter(
            CompanyID=CompanyID, VoucherDate__month=this_month, CreatedUserID=UserID)
        TotalReturn = return_ins.aggregate(Sum("GrandTotal"))
        TotalReturn = TotalReturn["GrandTotal__sum"]

    cash_ledgerids = table.AccountLedger.objects.filter(
        CompanyID=CompanyID, AccountGroupUnder=9).values_list("LedgerID", flat=True)
    bank_ledgerids = table.AccountLedger.objects.filter(
        CompanyID=CompanyID, AccountGroupUnder=8).values_list("LedgerID", flat=True)
    if table.LedgerPosting.objects.filter(CompanyID=CompanyID, LedgerID__in=cash_ledgerids, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID).exists():
        cash_ins = table.LedgerPosting.objects.filter(
            CompanyID=CompanyID, LedgerID__in=cash_ledgerids, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID)
        DebitSum = cash_ins.aggregate(Sum("Debit"))
        DebitSum = DebitSum["Debit__sum"]
        CreditSum = cash_ins.aggregate(Sum("Credit"))
        CreditSum = CreditSum["Credit__sum"]
        CashBalance = converted_float(DebitSum) - converted_float(CreditSum)

    if table.LedgerPosting.objects.filter(CompanyID=CompanyID, LedgerID__in=bank_ledgerids, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID).exists():
        bank_ins = table.LedgerPosting.objects.filter(
            CompanyID=CompanyID, LedgerID__in=bank_ledgerids, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID)
        DebitSum = bank_ins.aggregate(Sum("Debit"))
        DebitSum = DebitSum["Debit__sum"]
        CreditSum = bank_ins.aggregate(Sum("Credit"))
        CreditSum = CreditSum["Credit__sum"]
        BankBalance = converted_float(DebitSum) - converted_float(CreditSum)

    if table.ExpenseMaster.objects.filter(CompanyID=CompanyID, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID).exists():
        expense_ins = table.ExpenseMaster.objects.filter(
            CompanyID=CompanyID, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID)
        TotalExpense = expense_ins.aggregate(Sum("GrandTotal"))
        TotalExpense = TotalExpense["GrandTotal__sum"]

    response_data = {
        "StatusCode": 6000,
        "data": data,
        "TotalSales": TotalSales,
        "TotalReturn": TotalReturn,
        "CashBalance": CashBalance,
        "BankBalance": BankBalance,
        "TotalExpense": TotalExpense
    }
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def salesApp_profile(request):
    today = datetime.datetime.now()
    data = request.data
    UserID = data['UserID']
    type = data['type']
    try:
        photo = data["photo"]
    except:
        photo = None

    if table.Customer.objects.filter(user__id=UserID).exists():
        customer = table.Customer.objects.filter(user__id=UserID).first()
        if type == "list":
            photo = ImageSerializer(
                customer, many=False, context={"request": request}
            ).data.get("photo")
            country = ""
            CountryCode = ""
            state = ""
            if customer.Country:
                country = customer.Country.Country_Name
                CountryCode = customer.Country.CountryCode
            if customer.State:
                state = customer.State.Name
            data = {
                "username": customer.user.username,
                "email": customer.user.email,
                "phone": customer.Phone,
                "Country": country,
                "photo": photo,
                "CountryCode": CountryCode,
                "state": state
            }
        else:
            customer.photo = photo
            customer.save()
            data = {}

        response_data = {
            "StatusCode": 6000,
            "data": data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "No data",
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def faera_stock_report(request):
    whose_report = ""
    lang = request.GET.get("lang")
    download_type = request.GET.get("download_type")
    if lang and download_type == "EXCEL":
        activate(lang)

    CompanyID = request.GET.get("CompanyID")
    company = get_company(CompanyID)
    BranchID = request.GET.get("BranchID")
    FromDate = get_financial_year_dates(company)
    # ToDate = date.today()
    ToDate = request.GET.get("ToDate")
    PriceRounding = request.GET.get("PriceRounding")
    invoice_type = request.GET.get("invoice_type")
    VoucherType = request.GET.get("VoucherType")

    DeviceCode = request.GET.get("DeviceCode")
    WareHouseID = 0
    if table.POS_Devices.objects.filter(CompanyID__id=CompanyID, DeviceCode=DeviceCode).exists():
        WareHouseID = table.POS_Devices.objects.filter(
            CompanyID__id=CompanyID, DeviceCode=DeviceCode).first().WareHouseID.WarehouseID
    ProductFilter = "1"
    StockFilter = 0
    ProductID = 0
    CategoryID = 0
    BrandID = 0
    GroupID = 0
    Barcode = 0

    try:
        PriceRounding = int(request.GET.get("PriceRounding"))
    except:
        PriceRounding = 2

    columns = request.GET.get("columns")
    columns_heads = []
    if columns:
        columns_heads = json.loads(columns)

    company_instance = table.CompanySettings.objects.get(id=CompanyID)
    country_instance = table.Country.objects.get(
        id=company_instance.Country.id)
    ShowProfitinSalesRegisterReport = False
    data = {}
    details = {}
    total = {}
    page_type = ""
    report_title = ""
    # Stock Report
    if invoice_type == "stock_report":
        df, details = query_stock_report_data(
            CompanyID,
            BranchID,
            FromDate,
            ToDate,
            PriceRounding,
            ProductFilter,
            StockFilter,
            ProductID,
            CategoryID,
            GroupID,
            WareHouseID,
            Barcode,
            BrandID,
        )
        df.style.set_caption("Hello World")
        if table.Warehouse.objects.filter(
            CompanyID=CompanyID, WarehouseID=WareHouseID
        ).exists():
            whose_report = table.Warehouse.objects.get(
                CompanyID=CompanyID, WarehouseID=WareHouseID
            ).WarehouseName
        elif table.ProductCategory.objects.filter(
            CompanyID=CompanyID, ProductCategoryID=CategoryID
        ).exists():
            whose_report = table.ProductCategory.objects.get(
                CompanyID=CompanyID, ProductCategoryID=CategoryID
            ).CategoryName
        elif table.ProductGroup.objects.filter(
            CompanyID=CompanyID, ProductGroupID=GroupID
        ).exists():
            whose_report = table.ProductGroup.objects.get(
                CompanyID=CompanyID, ProductGroupID=GroupID
            ).GroupName
        elif table.Brand.objects.filter(
            CompanyID=CompanyID, BrandID=BrandID
        ).exists():
            whose_report = table.Brand.objects.get(
                CompanyID=CompanyID, BrandID=BrandID
            ).BrandName

    # For PDF
    if lang:
        activate(lang)

    if invoice_type == "stock_report":
        report_name = "STOCK REPORT"
        report_title = str(_("STOCK REPORT"))
        template = get_template("reports/stock_report_print.html")

    company_instance = table.CompanySettings.objects.get(id=CompanyID)
    serialized = CompanySettingsPrintRestSerializer(
        company_instance, many=False, context={"request": request}
    )
    data = {
        "country": country_instance,
        "page_type": page_type,
        "invoice_type": invoice_type,
        "VoucherType": VoucherType,
        "type": "pdf",
        "company": serialized.data,
        "details": details,
        "total": total,
        "PriceRounding": int(PriceRounding),
        "FromDate": FromDate,
        "ToDate": ToDate,
        "report_title": report_title,
        "print_template": True,
        "columns_heads": columns_heads,
        "whose_report": whose_report,
        "ShowProfitinSalesRegisterReport": ShowProfitinSalesRegisterReport,
    }

    response = render(request, "reports/stock_report_print.html", data)
    return response


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def faera_payment_modes(request):
    today = datetime.datetime.now()
    data = request.data
    UserID = data['UserID']
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)

    if table.UserTable.objects.filter(CompanyID=CompanyID, customer__user__id=UserID,Active=True).exists():
        user_instance = table.UserTable.objects.filter(
            CompanyID=CompanyID, customer__user__id=UserID,Active=True).first()
        ledger_ins = table.AccountLedger.objects.filter(
            CompanyID=CompanyID, AccountGroupUnder__in=[8, 9])
        if user_instance.DefaultAccountForUser == True:
            Cash_Account = user_instance.Cash_Account
            Bank_Account = user_instance.Bank_Account
            ledger_ins = ledger_ins.filter(
                LedgerID__in=[Cash_Account, Bank_Account])

        data = []
        if ledger_ins:
            for i in ledger_ins:
                balance = get_BalanceFromLedgerPost(
                    CompanyID, i.LedgerID, i.BranchID)
                data.append({
                    "id": i.id,
                    "LedgerID": i.LedgerID,
                    "LedgerName": i.LedgerName,
                    "Balance": balance,
                    "Group": i.AccountGroupUnder
                })
        if data:
            StatusCode = 6000
        else:
            StatusCode = 6001

        response_data = {
            "StatusCode": StatusCode,
            "data": data
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
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def default_values(request):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data["CompanyID"]
    company = get_company(CompanyID)
    BranchID = data["BranchID"]
    userId = data["userId"]
    
    financial_dates = get_financial_year_dates(company)
    financial_FromDate = financial_dates[0]
    financial_ToDate = financial_dates[1]
    CompanyName = company.CompanyName
    Cash_Account = 1
    Cash_Account_name = ""
    Bank_Account = 92
    Bank_Account_name = ""
    Sales_Account = 85
    Sales_Return_Account = 86
    Purchase_Account = 69
    Purchase_Return_Account = 70
    Sales_Account_name = ""
    Sales_Return_Account_name = ""
    Purchase_Account_name = ""
    Purchase_Return_Account_name = ""
    DefaultAccountForUser = False
    user_type = ""
    Country = None
    CountryName = ""
    CurrencySymbol = ""
    State_Code = ""
    State = None
    StateName = ""
    
    if company.Country:
        Country = company.Country.id
        CountryName = company.Country.Country_Name
        CurrencySymbol = company.Country.Symbol
    if company.State:
        State = company.State.id
        StateName = company.State.Name
        State_Code = company.State.State_Code
    
    VAT = get_general_settings(BranchID, company, "VAT")
    GST = get_general_settings(BranchID, company, "GST")
    AllowAdvanceReceiptinSales = get_general_settings(BranchID, company, "AllowAdvanceReceiptinSales")
    
    if table.UserTable.objects.filter(CompanyID=company, customer__user=userId,Active=True).exists():
        user_table_instance = table.UserTable.objects.get(CompanyID=company, customer__user=userId,Active=True)
        Cash_Account = user_table_instance.Cash_Account
        Bank_Account = user_table_instance.Bank_Account
        Sales_Account = user_table_instance.Sales_Account
        Sales_Return_Account = user_table_instance.Sales_Return_Account
        Purchase_Account = user_table_instance.Purchase_Account
        Purchase_Return_Account = user_table_instance.Purchase_Return_Account
        DefaultAccountForUser = user_table_instance.DefaultAccountForUser
        user_type = user_table_instance.UserType.ID
    
    if table.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Cash_Account).exists():
        Cash_Account_name = get_object_or_404(table.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Cash_Account)).LedgerName

    if table.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Bank_Account).exists():
        Bank_Account_name = get_object_or_404(table.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Bank_Account)).LedgerName
    
    if table.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Sales_Account).exists():
        Sales_Account_name = get_object_or_404(table.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Sales_Account)).LedgerName
            
    if table.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Sales_Return_Account).exists():
        Sales_Return_Account_name = get_object_or_404(table.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Sales_Return_Account)).LedgerName
            
    if table.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Purchase_Account).exists():
        Purchase_Account_name = get_object_or_404(table.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Purchase_Account)).LedgerName
        
    if table.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Purchase_Return_Account).exists():
        Purchase_Return_Account_name = get_object_or_404(table.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Purchase_Return_Account)).LedgerName
    
    EnableZatca = company.EnableZatca
    EnableBillwise = get_general_settings(BranchID, company, "EnableBillwise")
    settingsData = {
        "VAT": VAT,
        "GST": GST,
        "AllowAdvanceReceiptinSales": AllowAdvanceReceiptinSales,
        "EnableZatca": EnableZatca,
        "EnableBillwise": EnableBillwise,
    }
    
    response_data = {
        "StatusCode": 6000,
        "settingsData": settingsData,
        "financial_FromDate": financial_FromDate,
        "financial_ToDate": financial_ToDate,
        "CompanyName": CompanyName,
        "Cash_Account": Cash_Account,
        "Cash_Account_name": Cash_Account_name,
        "Bank_Account": Bank_Account,
        "Bank_Account_name": Bank_Account_name,
        "Sales_Account": Sales_Account,
        "Sales_Return_Account": Sales_Return_Account,
        "Purchase_Account": Purchase_Account,
        "Purchase_Return_Account": Purchase_Return_Account,
        "Sales_Account_name": Sales_Account_name,
        "Sales_Return_Account_name": Sales_Return_Account_name,
        "Purchase_Account_name": Purchase_Account_name,
        "Purchase_Return_Account_name": Purchase_Return_Account_name,
        "DefaultAccountForUser": DefaultAccountForUser,
        "user_type": user_type,
        "Country": Country,
        "CountryName": CountryName,
        "CurrencySymbol": CurrencySymbol,
        "State_Code": State_Code,
        "State": State,
        "StateName": StateName,
    }
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def billwise_list_customer(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    CreatedUserID = data['CreatedUserID']
    BranchID = data['BranchID']
    LedgerID = data['LedgerID']
    call_type = data['call_type']
    PaymentVoucherNo = data['PaymentVoucherNo']
    PaymentVoucherType = data['PaymentVoucherType']

    if call_type == "create":
        if table.BillWiseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, CustomerID=LedgerID, InvoiceAmount__gt=F('Payments')).exists():
            bill_wise_instances = table.BillWiseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, CustomerID=LedgerID, InvoiceAmount__gt=F('Payments')).order_by("-VoucherDate")
            serialized = BillwiseMasterSerializer(bill_wise_instances, many=True, context={
                "CompanyID": CompanyID, "PaymentVoucherNo": PaymentVoucherNo, "PaymentVoucherType": PaymentVoucherType, "call_type": call_type})

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "no billwise found"
            }
    else:
        if table.BillWiseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, CustomerID=LedgerID).exists():
            bill_wise_instances = table.BillWiseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, CustomerID=LedgerID).order_by("-VoucherDate")
            serialized = BillwiseMasterSerializer(bill_wise_instances, many=True, context={
                "CompanyID": CompanyID, "PaymentVoucherNo": PaymentVoucherNo, "PaymentVoucherType": PaymentVoucherType, "call_type": call_type})

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "no billwise found"
            }
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def ledgerListByGroups(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]
    GroupUnder = data["GroupUnder"]

    try:
        name = data["name"]
    except:
        name = ""

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data["BranchID"]
        if table.AccountLedger.objects.filter(
            CompanyID=CompanyID, AccountGroupUnder__in=GroupUnder
        ).exists():

            instances = table.AccountLedger.objects.filter(
                CompanyID=CompanyID, AccountGroupUnder__in=GroupUnder
            )
            if name:
                instances = instances.filter(LedgerName__icontains=name)

            serialized = LedgerSerializer(
                instances,
                many=True,
                context={"CompanyID": CompanyID,
                         "PriceRounding": PriceRounding},
            )

            response_data = {"StatusCode": 6000, "data": serialized.data}

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Account Ledger Not Found in this BranchID!",
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)
