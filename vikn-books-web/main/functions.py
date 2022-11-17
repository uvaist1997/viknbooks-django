import string
import random
from unittest import result
from django.http import HttpResponse
from decimal import Decimal
from fatoora import Fatoora
from users.models import CustomerUser
from django.shortcuts import render, get_object_or_404
from users.models import DatabaseStore
from brands.models import AccountLedger, Branch, BranchSettings, CompanySettings, FinancialYear, LedgerPosting, Parties, PriceCategory, QrCode, Route, UserTable, Warehouse
import datetime
import geocoder
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from geopy.geocoders import Nominatim
from django.contrib.auth.models import User
from device_detector import DeviceDetector
from brands.models import Activity_Log, VoucherNoTable
import requests
import geoip2.database
from ipware import get_client_ip
import re
import json
# from urllib2 import urlopen
from urllib.request import urlopen
import platform
import socket
import re
import uuid
import json
from random import randint
from brands import models as table
import calendar
from django.db.models import Q, Sum, F
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone
from datetime import date
import pandas as pd
import psycopg2
from datetime import datetime as date_time, timedelta
from collections import OrderedDict


def get_company(CompanyID):
    if CompanySettings.objects.filter(id=CompanyID).exists():
        CompanyID = get_object_or_404(
            CompanySettings.objects.filter(id=CompanyID))
    else:
        CompanyID = "Company Not Found"
    return CompanyID


def get_ledger(id):
    if AccountLedger.objects.filter(id=id).exists():
        ledger = get_object_or_404(
            AccountLedger.objects.filter(id=id))
    else:
        ledger = "Ledger Not Found"
    return ledger


def get_warehouse(id):
    if Warehouse.objects.filter(id=id).exists():
        WarehouseID = get_object_or_404(
            Warehouse.objects.filter(id=id))
    else:
        WarehouseID = "Warehouse Not Found"
    return WarehouseID


def get_price_category(id):
    if PriceCategory.objects.filter(id=id).exists():
        PriceCategoryID = get_object_or_404(
            PriceCategory.objects.filter(id=id))
    else:
        PriceCategoryID = "Warehouse Not Found"
    return PriceCategoryID


def get_route(id):
    if Route.objects.filter(id=id).exists():
        RouteID = get_object_or_404(
            Route.objects.filter(id=id))
    else:
        RouteID = "Route Not Found"
    return RouteID


def get_BranchSettings(CompanyID, SettingsType):
    productsForAllBranches = False
    if BranchSettings.objects.filter(CompanyID=CompanyID, SettingsType=SettingsType).exists():
        if SettingsType == "productsForAllBranches":
            branch_instance = get_object_or_404(
                BranchSettings.objects.filter(CompanyID=CompanyID, SettingsType=SettingsType)).SettingsValue
            print(branch_instance, 'branch_instancebranch_instance')
            if branch_instance == True or branch_instance == "True":
                productsForAllBranches = True

    return productsForAllBranches


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_access_token(request):
    authorization = request.META.get('HTTP_AUTHORIZATION')
    # access_token = authorization.split(' ')[1]
    return authorization


def get_auto_id(model):
    auto_id = 1
    latest_auto_id = model.objects.all().order_by("-id")[:1]
    if latest_auto_id:
        for auto in latest_auto_id:
            auto_id = auto.auto_id + 1
    return auto_id


def get_current_role(request):
    current_role = "user"
    if request.user.is_authenticated:
        if request.user.is_superuser:
            current_role = "superadmin"
        elif CustomerUser.objects.filter(user=request.user).exists():
            current_role = "customeruser"
    return current_role

# current_role = get_current_role(request)


def generate_unique_id(size=8, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def generate_form_errors(args, formset=False):
    message = ''
    if not formset:
        for field in args:
            if field.errors:
                message += field.errors + "|"
        for err in args.non_field_errors():
            message += str(err) + "|"

    elif formset:
        for form in args:
            for field in form:
                if field.errors:
                    message += field.errors + "|"
            for err in form.non_field_errors():
                message += str(err) + "|"
    return message[:-1]


def get_timezone(request):
    if "set_user_timezone" in request.session:
        user_time_zone = request.session['set_user_timezone']
    else:
        user_time_zone = "Asia/Kolkata"
    return user_time_zone


def get_DataBase(request):
    user = request.user
    customer_instance = get_object_or_404(
        CustomerUser.objects.filter(user=user))
    db_id = customer_instance.databaseid
    datastore = get_object_or_404(DatabaseStore.objects.filter(id=db_id))
    DataBase = datastore.DefaultDatabase

    return DataBase


def get_location(request):
    # ip_address = get_client_ip(request)
    # coordinates = geocoder.ip(ip_address).latlng
    # geolocator = Nominatim(user_agent="geoapiExercises")
    # location = geolocator.reverse(coordinates)
    location = ""
    return str(location)


def get_device_name(request):
    # http_user_agent = request.META.get('HTTP_USER_AGENT')
    # device = DeviceDetector(http_user_agent).parse()
    # device_brand_name = device.device_brand_name()
    # device_model = device.device_model()
    # device_type = device.device_type()
    # client_name = device.client_name()
    # os_name = device.os_name()
    # device_name = device_brand_name+ " "+device_model+" "+device_type+" "+client_name+" "+os_name
    device_name = ""
    return device_name


def get_user(user):
    user = User.objects.get(pk=user)
    return user


def get_geolocation_for_ip(ip):
    token = '660a6f8a8892c4373d1984b09d69ff89'
    
    url = f"http://api.ipstack.com/{ip}?access_key={token}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def get_visitors_details(request):
    is_mobile = request.user_agent.is_mobile
    is_pc = request.user_agent.is_pc
    browser = request.user_agent.browser.family
    device = request.user_agent.device.family
    os = request.user_agent.os.family
    # test = platform.machine()
    # print(test,"test")
    # print(platform.platform())
    info = {}
    info['platform'] = platform.system()
    info['platform-release'] = platform.release()
    info['platform-version'] = platform.version()
    info['architecture'] = platform.machine()
    info['hostname'] = socket.gethostname()
    info['ip-address'] = socket.gethostbyname(socket.gethostname())
    info['mac-address'] = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
    info['processor'] = platform.processor()
    info['is_mobile'] = is_mobile
    info['is_pc'] = is_pc
    info['browser'] = browser
    info['device'] = device
    info['os'] = os
    # from pprint import pprint
    # pprint(request.META)
    print(info, "info")
    return info


def activity_log(request, company, log_type, user, source, action, message, description):
    # geo_info = get_geolocation_for_ip(get_client_ip(request))
    # location = get_location(request)
    api_url = request.build_absolute_uri()
    visitors = get_visitors_details(request)
    is_pc = visitors['is_pc']
    browser = visitors['browser']
    device_name = visitors['device']
    location = "location"
    # location = "location"
    # device_name = get_device_name(request)
    user = get_user(user)
    username = user.username
    activity_instance = Activity_Log.objects.create(
        company=company,
        log_type=log_type,
        user=user,
        device_name=device_name,
        location=location,
        source=source,
        action=action,
        message=message,
        description=description,
        is_pc=is_pc,
        browser=browser,
        api_url=api_url
    )
    return activity_instance.id


def call_paginator_all(model_object, page_number, items_per_page):
    paginator = Paginator(model_object, items_per_page)
    content = paginator.page(page_number)
    return content


def list_pagination(list_value, items_per_page, page_no):
    paginator_object = Paginator(list_value, items_per_page)
    get_value = paginator_object.page(page_no).object_list
    return get_value


def update_voucher_table(CompanyID, CreatedUserID, VoucherType, PreFix, Seperator, InvoiceNo):
    if table.VoucherNoGenerateTable.objects.filter(CompanyID=CompanyID, VoucherType=VoucherType).exists():
        table.VoucherNoGenerateTable.objects.filter(CompanyID=CompanyID, VoucherType=VoucherType).update(
            PreFix=PreFix,
            Seperater=Seperator,
            LastInvoiceNo=InvoiceNo,
            UserID=CreatedUserID,
        )
    else:
        table.VoucherNoGenerateTable.objects.create(
            UserID=CreatedUserID,
            CompanyID=CompanyID,
            VoucherType=VoucherType,
            PreFix=PreFix,
            Seperater=Seperator,
            LastInvoiceNo=InvoiceNo,
        )
    # if VoucherNoTable.objects.filter(CompanyID=CompanyID,UserID=CreatedUserID,VoucherType=VoucherType).exists():
    #     VoucherNoTable.objects.filter(CompanyID=CompanyID,UserID=CreatedUserID,VoucherType=VoucherType).update(
    #         PreFix=PreFix,
    #         Seperater=Seperator,
    #         LastInvoiceNo=InvoiceNo,
    #         )
    # else:
    #     VoucherNoTable.objects.create(
    #             UserID=CreatedUserID,
    #             CompanyID=CompanyID,
    #             VoucherType=VoucherType,
    #             PreFix=PreFix,
    #             Seperater=Seperator,
    #             LastInvoiceNo=InvoiceNo,
    #         )


def extract_alphabet_from_string(string):
    only_alpha = "".join(filter(lambda x: not x.isdigit(), string))
    return only_alpha


def generateVoucherNoFunction(CompanyID, UserID, VoucherType, BranchID):
    old_invoiceNo = 0
    PreFix = VoucherType
    seperator = ""
    model = get_model(VoucherType)
    if table.VoucherNoGenerateTable.objects.filter(CompanyID=CompanyID, VoucherType=VoucherType, LastInvoiceNo__isnull=False).exists():
        # instances = table.VoucherNoGenerateTable.objects.filter(
        #     CompanyID=CompanyID, VoucherType=VoucherType).exclude(LastInvoiceNo__isnull=True)
        voucher = table.VoucherNoGenerateTable.objects.filter(
            CompanyID=CompanyID, VoucherType=VoucherType).exclude(LastInvoiceNo__isnull=True).first()
        old_invoiceNo = voucher.LastInvoiceNo
        PreFix = voucher.PreFix
        seperator = voucher.Seperater

        new_invoiceNo = int(old_invoiceNo) + 1
        new_VoucherNo = PreFix + seperator + str(new_invoiceNo)
    else:
        new_VoucherNo, new_invoiceNo, PreFix, seperator = get_voucher(
            model, CompanyID, BranchID, UserID, VoucherType)

    return new_VoucherNo, new_invoiceNo, PreFix, seperator


def get_voucher(model, CompanyID, BranchID, CreatedUserID, VoucherType):
    new_VoucherNo = VoucherType + str(1)
    new_num = 1
    prefix = VoucherType
    if VoucherType == "PC":
        ProductCode = "PC1000"
        if table.Product.objects.filter(CompanyID=CompanyID).exists():
            latest_ProductCode = table.Product.objects.filter(
                CompanyID=CompanyID).order_by("ProductID").last()

            ProductCode = latest_ProductCode.ProductCode
            if not ProductCode.isdecimal():
                temp = re.compile("([a-zA-Z]+)([0-9]+)")
                if temp.match(ProductCode):
                    res = temp.match(ProductCode).groups()
                    code, number = res
                    number = int(number) + 1
                    print(number)
                    ProductCode = str(code) + str(number)
                else:
                    if ProductCode == '':
                        ProductCode = "0"
                    try:
                        ProductCodeNumber = re.findall(r'\d+', ProductCode)[-1]
                    except:
                        ProductCodeNumber = "0"
                    rest = ProductCode.split(ProductCodeNumber)[0]
                    ProductCode = str(int(ProductCodeNumber) +
                                      1).zfill(len(ProductCodeNumber))
                    ProductCode = str(rest) + str(ProductCode)
            else:
                code = str(converted_float(ProductCode) + 1)
                code = code.rstrip('0').rstrip('.') if '.' in code else code
                ProductCode = code.zfill(len(ProductCode))

        new_VoucherNo = ProductCode
    elif VoucherType == "STO" or VoucherType == "ST":
        if model.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType).exists():
            instance = model.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID).first()
            OldVoucherNo = instance.VoucherNo
            if not OldVoucherNo.isdecimal():
                res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
                prefix = extract_alphabet_from_string(OldVoucherNo)
                num = res.group(0)
                new_num = int(num) + 1
                new_VoucherNo = prefix + str(new_num)
            else:
                # new_VoucherNo = float(OldVoucherNo) + 1
                prefix = VoucherType
                new_num = int(OldVoucherNo) + 1
                new_VoucherNo = str(int(OldVoucherNo) +
                                    1).zfill(len(OldVoucherNo))

    elif VoucherType == "PT" or VoucherType == "RT":
        prefix = VoucherType
        new_num = "0001"
        new_VoucherNo = prefix + new_num

    elif model.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        instance = model.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID).first()
        OldVoucherNo = instance.VoucherNo
        if VoucherType == "AG":
            OldVoucherNo = instance.GroupCode
        elif VoucherType == "CP" or VoucherType == "BP":
            instance = model.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType).first()
            if instance:
                OldVoucherNo = instance.VoucherNo
            else:
                OldVoucherNo = VoucherType + str(0)
        elif VoucherType == "CR" or VoucherType == "BR":
            instance = model.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType).first()
            print(VoucherType)
            if instance:
                OldVoucherNo = instance.VoucherNo
            else:
                OldVoucherNo = VoucherType + str(0)
        if not OldVoucherNo.isdecimal():
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            prefix = extract_alphabet_from_string(OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = prefix + str(new_num)
        else:
            # new_VoucherNo = float(OldVoucherNo) + 1
            prefix = VoucherType
            new_num = int(OldVoucherNo) + 1
            new_VoucherNo = str(int(OldVoucherNo) +
                                1).zfill(len(OldVoucherNo))
        if VoucherType == "SM":
            new_VoucherNo = "SM1"
            new_num = "1"
            prefix = "SM"

    return new_VoucherNo, new_num, prefix, ""


def get_model(VoucherType):
    model = ""
    if VoucherType == "SI":
        model = table.SalesMaster
    elif VoucherType == "PI":
        model = table.PurchaseMaster
    elif VoucherType == "SO":
        model = table.SalesOrderMaster
    elif VoucherType == "SE":
        model = table.SalesEstimateMaster
    elif VoucherType == "PO":
        model = table.PurchaseOrderMaster
    elif VoucherType == "SR":
        model = table.SalesReturnMaster
    elif VoucherType == "PR":
        model = table.PurchaseReturnMaster
    elif VoucherType == "OS":
        model = table.OpeningStockMaster
    elif VoucherType == "JL":
        model = table.JournalMaster
    elif VoucherType == "CP" or VoucherType == "BP":
        model = table.PaymentMaster
    elif VoucherType == "CR" or VoucherType == "BR":
        model = table.ReceiptMaster
    elif VoucherType == "ST":
        model = table.StockTransferMaster_ID
    elif VoucherType == "AG":
        model = table.AccountGroup
    elif VoucherType == "ES":
        model = table.ExcessStockMaster
    elif VoucherType == "SS":
        model = table.ShortageStockMaster
    elif VoucherType == "DS":
        model = table.DamageStockMaster
    elif VoucherType == "US":
        model = table.UsedStockMaster
    elif VoucherType == "WO":
        model = table.WorkOrderMaster
    elif VoucherType == "EX":
        model = table.ExpenseMaster
    elif VoucherType == "PC":
        model = table.Product
    elif VoucherType == "SM":
        model = table.StockManagementMaster
    elif VoucherType == "BRC":
        model = table.BankReconciliationMaster
    elif VoucherType == "STO":
        model = table.StockTransferMaster_ID

    return model


def get_userDateTime(timezone, dateTime):
    from datetime import datetime, timezone
    utc_dt = datetime.now(timezone.utc)
    dt = utc_dt.astimezone()
    import pytz
    tz = pytz.timezone(timezone)
    user_date_time = datetime.now(tz)
    return user_date_time


def generateTokenNo():
    range_start = 10**(6-1)
    range_end = (10**6)-1
    PinNo = randint(range_start, range_end)
    return PinNo


# def ConvertedTime(TimeZone,Time):
#     import datetime,pytz
#     mytimezone=pytz.timezone('Asia/Riyadh')
#     dtobj4=mytimezone.localize(Time)
#     dtobj_hongkong=dtobj4.astimezone(pytz.timezone(TimeZone))
#     # converted_time = dtobj_hongkong.time()
#     return dtobj_hongkong

def ConvertedTime(Time):
    import datetime
    import pytz
    from datetime import datetime, timezone

    dtobj_time = Time.replace(tzinfo=timezone.utc).astimezone(tz=None)
    return dtobj_time


def CheckTokenExpired(TimeZone, VerificationTokenTime):
    is_token_expired = False
    today = datetime.datetime.now()
    today = datetime.datetime.strptime(
        str(today).split(".")[0], "%Y-%m-%d %H:%M:%S")
    converted_today = ConvertedTime(today)
    VerificationTokenTime = datetime.datetime.strptime(
        str(VerificationTokenTime).split(".")[0], "%Y-%m-%d %H:%M:%S")
    converted_token_time = ConvertedTime(VerificationTokenTime)
    diff = converted_today - converted_token_time
    mint_diff = diff.seconds / 60
    if mint_diff > 5:
        is_token_expired = True
    return is_token_expired


def get_BranchLedgerId_for_LedgerPosting(BranchID, CompanyID, ledger):
    ledger_id = None
    if Branch.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
        if ledger == "vat_on_sales":
            ledger = Branch.objects.get(
                BranchID=BranchID, CompanyID=CompanyID).vat_on_sales
            ledger_id = ledger.LedgerID
        elif ledger == "vat_on_purchase":
            ledger = Branch.objects.get(
                BranchID=BranchID, CompanyID=CompanyID).vat_on_purchase
            ledger_id = ledger.LedgerID
        elif ledger == "vat_on_expense":
            ledger = Branch.objects.get(
                BranchID=BranchID, CompanyID=CompanyID).vat_on_expense
            ledger_id = ledger.LedgerID
        elif ledger == "central_gst_on_sales":
            ledger = Branch.objects.get(
                BranchID=BranchID, CompanyID=CompanyID).central_gst_on_sales
            ledger_id = ledger.LedgerID
        elif ledger == "state_gst_on_sales":
            ledger = Branch.objects.get(
                BranchID=BranchID, CompanyID=CompanyID).state_gst_on_sales
            ledger_id = ledger.LedgerID
        elif ledger == "integrated_gst_on_sales":
            ledger = Branch.objects.get(
                BranchID=BranchID, CompanyID=CompanyID).integrated_gst_on_sales
            ledger_id = ledger.LedgerID
        elif ledger == "central_gst_on_expense":
            ledger = Branch.objects.get(
                BranchID=BranchID, CompanyID=CompanyID).central_gst_on_expense
            ledger_id = ledger.LedgerID
        elif ledger == "central_gst_on_purchase":
            ledger = Branch.objects.get(
                BranchID=BranchID, CompanyID=CompanyID).central_gst_on_purchase
            ledger_id = ledger.LedgerID
        elif ledger == "state_gst_on_purchase":
            ledger = Branch.objects.get(
                BranchID=BranchID, CompanyID=CompanyID).state_gst_on_purchase
            ledger_id = ledger.LedgerID
        elif ledger == "integrated_gst_on_purchase":
            ledger = Branch.objects.get(
                BranchID=BranchID, CompanyID=CompanyID).integrated_gst_on_purchase
            ledger_id = ledger.LedgerID
        elif ledger == "state_gst_on_payment":
            ledger = Branch.objects.get(
                BranchID=BranchID, CompanyID=CompanyID).state_gst_on_payment
            ledger_id = ledger.LedgerID
        elif ledger == "round_off_sales":
            ledger = Branch.objects.get(
                BranchID=BranchID, CompanyID=CompanyID).round_off_sales
            ledger_id = ledger.LedgerID
        elif ledger == "discount_on_sales":
            ledger = Branch.objects.get(
                BranchID=BranchID, CompanyID=CompanyID).discount_on_sales
            ledger_id = ledger.LedgerID
        elif ledger == "discount_on_purchase":
            ledger = Branch.objects.get(
                BranchID=BranchID, CompanyID=CompanyID).discount_on_purchase
            ledger_id = ledger.LedgerID
        elif ledger == "discount_on_payment":
            ledger = Branch.objects.get(
                BranchID=BranchID, CompanyID=CompanyID).discount_on_payment
            ledger_id = ledger.LedgerID
        elif ledger == "discount_on_receipt":
            ledger = Branch.objects.get(
                BranchID=BranchID, CompanyID=CompanyID).discount_on_receipt
            ledger_id = ledger.LedgerID
        elif ledger == "discount_on_loyalty":
            ledger = Branch.objects.get(
                BranchID=BranchID, CompanyID=CompanyID).discount_on_loyalty
            ledger_id = ledger.LedgerID
        elif ledger == "round_off_purchase":
            ledger = Branch.objects.get(
                BranchID=BranchID, CompanyID=CompanyID).round_off_purchase
            ledger_id = ledger.LedgerID
    return ledger_id


def FormatedDate(Date):
    year = Date.split("-")[0]
    month = Date.split("-")[1]
    last_day = calendar.monthrange(int(year), int(month))[1]
    new_date = str(year) + str("-") + str(month) + str("-") + str(last_day)
    return new_date


def convert_to_datetime(date_time):
    format = "%Y-%m-%d"  # The format
    datetime_str = datetime.datetime.strptime(date_time, format)

    return datetime_str


def get_CompanyBranches(CompanyID):
    CompanyBranches = []
    if Branch.objects.filter(CompanyID=CompanyID).exists():
        CompanyBranches = Branch.objects.filter(
            CompanyID=CompanyID).values_list('BranchID', flat=True)
    return CompanyBranches


def get_BranchList(CompanyID, BranchID):
    SettingsType = "productsForAllBranches"
    BranchList = [BranchID]
    productsForAllBranches = get_BranchSettings(CompanyID, SettingsType)
    if productsForAllBranches == True or productsForAllBranches == "True":
        BranchList = get_CompanyBranches(CompanyID)
    return BranchList


def get_ModelInstance(CompanyID, BranchID, PriceListID, WarehouseID):
    pricelist = None
    warehouse = None
    if table.PriceList.objects.filter(CompanyID=CompanyID, PriceListID=PriceListID).exists():
        pricelist = table.PriceList.objects.get(
            CompanyID=CompanyID, PriceListID=PriceListID)

    if table.Warehouse.objects.filter(CompanyID=CompanyID, WarehouseID=WarehouseID).exists():
        warehouse = table.Warehouse.objects.get(
            CompanyID=CompanyID, WarehouseID=WarehouseID)

    return pricelist, warehouse


def delete_model_datas(model, CompanyID, BranchID, mode):
    if mode == "company_wise":
        if model.objects.filter(CompanyID=CompanyID).exists():
            model.objects.filter(CompanyID=CompanyID).delete()
    else:
        if model.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            model.objects.filter(CompanyID=CompanyID,
                                 BranchID=BranchID).delete()
    return ""


def remove_from_string(value, rm):
    value = value.replace(rm, '')
    return value


def guess_date(string):
    for fmt in ["%Y/%m/%d", "%d-%m-%Y", "%Y%m%d"]:
        try:
            return datetime.datetime.strptime(string, fmt).date()
        except ValueError:
            continue
    raise ValueError(string)


def get_GeneralSettings(CompanyID, BranchID, SettingsType):
    result_value = False
    if table.GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType=SettingsType).exists():
        settings_instance = table.GeneralSettings.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, SettingsType=SettingsType).first()
        if settings_instance.SettingsValue == True or settings_instance.SettingsValue == "True":
            result_value = True
        elif settings_instance.SettingsValue == False or settings_instance.SettingsValue == "False":
            result_value = False
        else:
            result_value = settings_instance.SettingsValue
    return result_value


def get_LedgerBalance(CompanyID, LedgerID):
    LedgerBalance = 0
    if table.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID).exists():
        LedgerBalance = table.AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID).first().Balance
    return LedgerBalance


def get_BalanceFromLedgerPost(CompanyID, LedgerID, BranchID):
    LedgerBalance = 0
    if LedgerPosting.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID).exists():
        ledger_instances = LedgerPosting.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID)
        Debit_sum = ledger_instances.aggregate(Sum('Debit'))
        Debit_sum = Debit_sum['Debit__sum']
        Credit_sum = ledger_instances.aggregate(Sum('Credit'))
        Credit_sum = Credit_sum['Credit__sum']
        LedgerBalance = converted_float(
            Debit_sum) - converted_float(Credit_sum)
    return LedgerBalance


def get_ProductStock(CompanyID, BranchID, ProductID, WarehouseID, BatchCode):
    CurrentStock = 0
    check_EnableProductBatchWise = get_GeneralSettings(
        CompanyID, BranchID, "EnableProductBatchWise")
    if check_EnableProductBatchWise == True:
        if WarehouseID:
            if table.Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, WareHouseID=WarehouseID).exists():
                Batch_ins = table.Batch.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, WareHouseID=WarehouseID).order_by('BatchCode').first()
                batch_pricelistID = Batch_ins.PriceListID
                batch_MultiFactor = table.PriceList.objects.get(
                    CompanyID=CompanyID, PriceListID=batch_pricelistID).MultiFactor
                total_stockIN = converted_float(Batch_ins.StockIn) / \
                    converted_float(batch_MultiFactor)
                total_stockOUT = converted_float(Batch_ins.StockOut) / \
                    converted_float(batch_MultiFactor)

                CurrentStock = converted_float(
                    total_stockIN) - converted_float(total_stockOUT)
        else:
            if table.Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
                Batch_ins = table.Batch.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode)
                batch_pricelistID = Batch_ins.PriceListID
                batch_MultiFactor = table.PriceList.objects.get(
                    CompanyID=CompanyID, PriceListID=batch_pricelistID).MultiFactor
                total_stockIN = converted_float(Batch_ins.StockIn) / \
                    converted_float(batch_MultiFactor)
                total_stockOUT = converted_float(Batch_ins.StockOut) / \
                    converted_float(batch_MultiFactor)

                CurrentStock = converted_float(
                    total_stockIN) - converted_float(total_stockOUT)
    else:
        if table.StockPosting.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).exists():
            QtyIn_sum = table.StockPosting.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).aggregate(Sum('QtyIn'))
            QtyIn_sum = QtyIn_sum['QtyIn__sum']
            QtyOut_sum = table.StockPosting.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).aggregate(Sum('QtyOut'))
            QtyOut_sum = QtyOut_sum['QtyOut__sum']
            CurrentStock = converted_float(
                QtyIn_sum) - converted_float(QtyOut_sum)
    return CurrentStock


def get_ProductWareHouseStock(CompanyID, BranchID, ProductID, WarehouseID, BatchCode):
    CurrentStock = 0
    check_EnableProductBatchWise = get_GeneralSettings(
        CompanyID, BranchID, "EnableProductBatchWise")
    if check_EnableProductBatchWise == True:
        if WarehouseID:
            if table.Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, WareHouseID=WarehouseID).exists():
                Batch_ins = table.Batch.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, WareHouseID=WarehouseID).order_by('BatchCode').first()
                batch_pricelistID = Batch_ins.PriceListID
                batch_MultiFactor = table.PriceList.objects.get(
                    CompanyID=CompanyID, PriceListID=batch_pricelistID).MultiFactor
                total_stockIN = converted_float(Batch_ins.StockIn) / \
                    converted_float(batch_MultiFactor)
                total_stockOUT = converted_float(Batch_ins.StockOut) / \
                    converted_float(batch_MultiFactor)

                CurrentStock = converted_float(
                    total_stockIN) - converted_float(total_stockOUT)
        else:
            if table.Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
                Batch_ins = table.Batch.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode)
                batch_pricelistID = Batch_ins.PriceListID
                batch_MultiFactor = table.PriceList.objects.get(
                    CompanyID=CompanyID, PriceListID=batch_pricelistID).MultiFactor
                total_stockIN = converted_float(Batch_ins.StockIn) / \
                    converted_float(batch_MultiFactor)
                total_stockOUT = converted_float(Batch_ins.StockOut) / \
                    converted_float(batch_MultiFactor)

                CurrentStock = converted_float(
                    total_stockIN) - converted_float(total_stockOUT)
    else:
        if table.StockPosting.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).exists():
            QtyIn_sum = table.StockPosting.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, WareHouseID=WarehouseID).aggregate(Sum('QtyIn'))
            QtyIn_sum = QtyIn_sum['QtyIn__sum']
            QtyOut_sum = table.StockPosting.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, WareHouseID=WarehouseID).aggregate(Sum('QtyOut'))
            QtyOut_sum = QtyOut_sum['QtyOut__sum']
            CurrentStock = converted_float(
                QtyIn_sum) - converted_float(QtyOut_sum)
    return CurrentStock


def get_all_logged_in_users():
    # Query all non-expired sessions
    # use timezone.now() instead of datetime.now() in latest versions of Django
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    uid_list = []

    # Build a list of user ids from that query
    for session in sessions:
        data = session.get_decoded()
        uid_list.append(data.get('_auth_user_id', None))

    # Query all logged in users based on id list
    return User.objects.filter(id__in=uid_list)


def get_VoucherName(VoucherType):
    if VoucherType == 'SI':
        VoucherName = 'Sales Invoice'
    elif VoucherType == 'SR':
        VoucherName = 'Sales Return'
    elif VoucherType == 'SO':
        VoucherName = 'Sales Order'
    elif VoucherType == 'SE':
        VoucherName = 'Sales Estimate'
    elif VoucherType == 'PI':
        VoucherName = 'Purchase Invoice'
    elif VoucherType == 'PR':
        VoucherName = 'Purchase Return'
    elif VoucherType == 'PO':
        VoucherName = 'Purchase Order'
    elif VoucherType == 'PE':
        VoucherName = 'Purchase Estimate'
    elif VoucherType == 'OS':
        VoucherName = 'Opening Stock'
    elif VoucherType == 'JL':
        VoucherName = 'Journal'
    elif VoucherType == 'CP':
        VoucherName = 'Cash Payment'
    elif VoucherType == 'BP':
        VoucherName = 'Bank Payment'
    elif VoucherType == 'CR':
        VoucherName = 'Cash Receipt'
    elif VoucherType == 'BR':
        VoucherName = 'Bank Receipt'
    elif VoucherType == 'ST':
        VoucherName = 'Stock Transfer'
    elif VoucherType == 'AG':
        VoucherName = 'Account Group'
    elif VoucherType == 'LOB':
        VoucherName = 'Opening Balance'
    elif VoucherType == 'EX':
        VoucherName = 'Expense'
    elif VoucherType == 'ES':
        VoucherName = 'Excess Stock'
    elif VoucherType == 'SS':
        VoucherName = 'Shortage Stock'
    elif VoucherType == 'SA':
        VoucherName = 'Stock Adjustments'
    elif VoucherType == 'BRC':
        VoucherName = 'Bank Reconciliation'

    return VoucherName


def get_all_dates_bwn2dates(sdate, edate):
    import pandas
    from datetime import timedelta
    from datetime import datetime
    sdate = datetime.strptime(sdate, '%Y-%m-%d')
    edate = datetime.strptime(edate, '%Y-%m-%d')
    date_list = pandas.date_range(sdate, edate-timedelta(days=0), freq='d')
    if sdate == edate:
        date_list = [sdate]
    return date_list


def converted_float(Val):
    # try:
    #     result = float(Val)
    # except:
    #     result = 0
    if Val == None or Val == '':
        result = 0
    else:
        result = float(Val)
    return result


def get_nth_day_date(day):
    import datetime as DT
    today = DT.date.today()
    if not day:
        day = 0
    try:
        nth_date_obj = today + DT.timedelta(days=day)
    except:
        nth_date_obj = today
    nth_date = nth_date_obj.strftime('%Y-%m-%d')
    return nth_date


def get_party_credit_period(CompanyID, LedgerID):
    credit_period = 0
    if Parties.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID).exists():
        credit_period = Parties.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID).first().CreditPeriod
    return credit_period


def get_no_of_days_bwn_dates(date):
    import datetime as DT
    today = DT.date.today()
    deference = (date - today).days
    return deference


def get_sum_same_name_val(list):
    import itertools as it
    def keyfunc(x): return x['Name']

    groups = it.groupby(sorted(list, key=keyfunc), keyfunc)
    [{'Name': k, 'amt': sum(x['amt'] for x in g)} for k, g in groups]


def get_treatment(type, treatment):
    Treatments = []
    result = ""
    if type == "gst":
        Treatments = [
            {"value": "0", "name": "Registered Business - Regular"},
            {"value": "1", "name": "Registered Business - Composition"},
            {"value": "2", "name": "Unregistered Business"},
            {"value": "3", "name": "Consumer"},
            {"value": "4", "name": "Overseas"},
            {"value": "5", "name": "Special Economic Zone"},
            {"value": "6", "name": "Deemed Export"}
        ]
    elif type == "vat":
        Treatments = [
            {"value": "0", "name": "Business to Business(B2B)"},
            {"value": "1", "name": "Business to Customer(B2C)"}
        ]
    if Treatments and treatment:
        result = next(
            (item for item in Treatments if item['value'] == treatment), None)
        result = result['name']
    return result


def get_first_date_of_month(date=None):
    import datetime
    if date:
        todayDate = date
    else:
        todayDate = datetime.date.today()
    # if todayDate.day > 25:
    #     todayDate += datetime.timedelta(7)
    if type(todayDate) == str:
        todayDate = datetime.datetime.strptime(todayDate, "%Y-%m-%d").date()
    todayDate = todayDate.replace(day=1)
    return todayDate


def get_no_of_days_in_month(year, month):
    from calendar import monthrange
    result = monthrange(year, month)
    result = result[1]
    return result

# this function call when to list months names between 2 dates
def list_months_2_dates(FromDate, ToDate):
    # month_list = [i.strftime("%b")
    #               for i in pd.date_range(start=FromDate, end=ToDate, freq='MS')]
    month_list = pd.date_range(FromDate, ToDate,
                  freq='MS').strftime("%b").tolist()
    return month_list


def get_week_start_end_date(day):
    from datetime import datetime, timedelta
    dt = datetime.strptime(day, '%Y-%m-%d')
    start = dt - timedelta(days=dt.weekday())
    end = start + timedelta(days=6)
    start = start.strftime('%Y-%m-%d')
    end = end.strftime('%Y-%m-%d')
    return start, end


def get_companyDataPerc(company):
    result = 80
    total = 16
    value = 0
    if company.CompanyName:
        value += 1
    if company.Description:
        value += 1
    if company.Email:
        value += 1
    if company.Phone:
        value += 1
    if company.Mobile:
        value += 1
    if company.Website:
        value += 1
    if company.Address1:
        value += 1
    if company.Address2:
        value += 1
    if company.Country:
        value += 1
    if company.State:
        value += 1
    if company.City:
        value += 1
    if company.RegistrationType:
        value += 1
    if company.CRNumber:
        value += 1
    if company.is_vat or company.is_gst:
        value += 1
    if company.VATNumber or company.GSTNumber:
        value += 1
    if company.CompanyLogo:
        value += 1
    result = (converted_float(value)/converted_float(total))*100
    return result


def generate_random_nos(length):
    import random
    return int(''.join([str(random.randint(0, 10)) for _ in range(length)]))


def get_financialYearDates(CompanyID):
    result = {"financial_FromDate": "", "financial_ToDate": ""}
    if FinancialYear.objects.filter(CompanyID=CompanyID, IsClosed=False).exists():
        financialyear = FinancialYear.objects.filter(
            CompanyID=CompanyID, IsClosed=False).first()
        financial_FromDate = financialyear.FromDate
        financial_ToDate = financialyear.ToDate
        result["financial_FromDate"] = financial_FromDate
        result["financial_ToDate"] = financial_ToDate
    return result


def generateQrCode(instance, VoucherType):
    if QrCode.objects.filter(voucher_type=VoucherType, master_id=instance.pk).exists():
        QrCode.objects.filter(voucher_type=VoucherType,
                              master_id=instance.pk).delete()
    CompanyID = instance.CompanyID
    if CompanyID.is_vat and CompanyID.VATNumber:
        tax_number = CompanyID.VATNumber
    elif CompanyID.is_gst and CompanyID.GSTNumber:
        tax_number = CompanyID.GSTNumber
    else:
        tax_number = 0

    fatoora_obj = Fatoora(
        seller_name=CompanyID.CompanyName,
        tax_number=tax_number,  # or "1234567891"
        invoice_date=str(instance.CreatedDate),  # Timestamp
        total_amount=instance.GrandTotal,  # or 100.0, 100.00, "100.0", "100.00"
        tax_amount=instance.TotalTax,  # or 15.0, 15.00, "15.0", "15.00"
    )
    url = fatoora_obj.base64
    qr_instance = QrCode.objects.create(
        voucher_type=VoucherType,
        master_id=instance.pk,
        url=url,
    )
    return ""


def get_financial_year_dates(company):
    # company = CompanySettings.objects.get(id=CompanyID)
    financial_year_period = company.financial_year_period
    current_year = date.today().year
    current_month = date.today().month
    next_year = current_year + 1
    prev_year = current_year - 1
    FromDate = ""
    ToDate = ""
    if financial_year_period:
        if int(financial_year_period) < int(10):
            financial_year_period = "0" + str(financial_year_period)
        if int(financial_year_period) == 1:
            last_month = 12
        else:
            last_month = int(financial_year_period) - 1

        if last_month < 10:
            last_month = "0" + str(last_month)
        if int(financial_year_period) >= int(current_month):
            FromDate = str(prev_year) + "-" + \
                str(financial_year_period) + "-" + "01"
            last_day = calendar.monthrange(
                int(current_year), int(last_month))[1]
            ToDate = str(current_year) + "-" + \
                str(last_month) + "-" + str(last_day)
        elif int(financial_year_period) < int(current_month):
            FromDate = str(current_year) + "-" + \
                str(financial_year_period) + "-" + "01"
            last_day = calendar.monthrange(int(next_year), int(last_month))[1]
            ToDate = str(next_year) + "-" + \
                str(last_month) + "-" + str(last_day)
    else:
        dates = get_financialYearDates(company)
        FromDate = dates["financial_FromDate"]
        ToDate = dates["financial_ToDate"]
        present = date.today()
        if ToDate < present:
            FromDate = FromDate.replace(FromDate.year + 1)
            ToDate = ToDate.replace(ToDate.year + 1)
    return [FromDate, ToDate]


def getUrl(action):
    if action == "signup_verification":
        url = "http://localhost:3000/signUp-verification/"
        # url = "https://accounts.vikncodes.com/signUp-verification/"
        # url = "https://accounts.vikncodes.in/signUp-verification/"
    elif action == "password_confirm":
        url = "http://localhost:3000/password-confirm"
        # url = "https://accounts.vikncodes.com/password-confirm"
        # url = "https://accounts.vikncodes.in/password-confirm"
    elif action == "signin":
        url = "http://localhost:3000/signin?service=viknbooks"
        # url = "https://accounts.vikncodes.com/signin?service=viknbooks"
        # url = "https://accounts.vikncodes.in/signin?service=viknbooks"
    elif action == "signup":
        url = "http://localhost:3000/sign-up?service=viknbooks"
        # url = "https://accounts.vikncodes.com/sign-up?service=viknbooks"
        # url = "https://accounts.vikncodes.in/sign-up?service=viknbooks"
    elif action == "domain":
        url = "http://localhost:3002"
        # url = "https://viknbooks.com"
        # url = "https://vikncodes.in"
        # url = "localhost"
    elif action == "sub_domain":
        url = "http://localhost:3000"
        # url = "https://viknbooks.com"
        # url = ".vikncodes.in"
        # url = ".rabbaniperfume.com"
        # url = "localhost"
    return url


def company_insert_query_to_accounts(company):
    # host = '139.59.44.104'
    host = '127.0.0.1'
    print("company_insert_query_to_accounts=======================>>>>>>>>>>>>")
    connection = None
    try:
        connection = psycopg2.connect(
        database="accounts", user='vikncodes', password='vikncodes123', host=host, port= '5432'
        )
        cursor = connection.cursor()
        postgres_comp_query = """ INSERT INTO public."companySettings_companySettings" VALUES (%(id)s,%(Action)s,%(CompanyName)s,%(CompanyLogo)s, %(Address1)s,%(Address2)s,%(Address3)s,%(City)s,%(PostalCode)s,%(Phone)s,%(Mobile)s,%(Email)s,%(Website)s,%(VATNumber)s,%(GSTNumber)s,%(Tax1)s,%(Tax2)s,%(Tax3)s,%(ExpiryDate)s,%(NoOfUsers)s,%(CreatedDate)s,%(UpdatedDate)s,%(DeletedDate)s,%(CreatedUserID)s,%(UpdatedUserID)s,%(is_deleted)s,%(is_vat)s,%(is_gst)s,%(CRNumber)s,%(CINNumber)s,%(Description)s,%(IsTrialVersion)s,%(Edition)s,%(Permission)s,%(IsPosUser)s,%(RegistrationType)s,%(IsBranch)s,%(NoOfBrances)s,%(Country_id)s,%(State_id)s,%(business_type_id)s,%(owner_id)s,%(EnableZatca)s,%(financial_year_period)s,'True','False','False')"""
        comp_dict = CompanySettings.objects.filter(pk=company.pk).values()[0]
        
        cursor.execute(postgres_comp_query,comp_dict)
        connection.commit()

    except (Exception, psycopg2.Error) as error:
        print("Failed to insert record into mobile table", error)

    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed11111")


def company_update_query_to_accounts(company):
    # host = '139.59.44.104'
    host = '127.0.0.1'
    connection = None
    try:
        connection = psycopg2.connect(
        database="accounts", user='vikncodes', password='vikncodes123', host=host, port= '5432'
        )
        cursor = connection.cursor()

        
        comp_dict = CompanySettings.objects.filter(pk=company.pk).values()[0]
        
        postgres_comp_query = """ UPDATE public."companySettings_companySettings" SET "Action"=%(Action)s,"CompanyName"=%(CompanyName)s,"CompanyLogo"=%(CompanyLogo)s, "Address1"=%(Address1)s,"Address2"=%(Address2)s,"Address3"=%(Address3)s,"City"=%(City)s,"PostalCode"=%(PostalCode)s,"Phone"=%(Phone)s,"Mobile"=%(Mobile)s,"Email"=%(Email)s,"Website"=%(Website)s,"VATNumber"=%(VATNumber)s,"GSTNumber"=%(GSTNumber)s,"Tax1"=%(Tax1)s,"Tax2"=%(Tax2)s,"Tax3"=%(Tax3)s,"ExpiryDate"=%(ExpiryDate)s,"NoOfUsers"=%(NoOfUsers)s,"CreatedDate"=%(CreatedDate)s,"UpdatedDate"=%(UpdatedDate)s,"DeletedDate"=%(DeletedDate)s,"CreatedUserID"=%(CreatedUserID)s,"UpdatedUserID"=%(UpdatedUserID)s,"is_deleted"=%(is_deleted)s,"is_vat"=%(is_vat)s,"is_gst"=%(is_gst)s,"CRNumber"=%(CRNumber)s,"CINNumber"=%(CINNumber)s,"Description"=%(Description)s,"IsTrialVersion"=%(IsTrialVersion)s,"Edition"=%(Edition)s,"Permission"=%(Permission)s,"IsPosUser"=%(IsPosUser)s,"RegistrationType"=%(RegistrationType)s,"IsBranch"=%(IsBranch)s,"NoOfBrances"=%(NoOfBrances)s,"Country_id"=%(Country_id)s,"State_id"=%(State_id)s,"business_type_id"=%(business_type_id)s,"owner_id"=%(owner_id)s,"EnableZatca"=%(EnableZatca)s,"financial_year_period"=%(financial_year_period)s WHERE id = %(id)s"""
        cursor.execute(postgres_comp_query,comp_dict)
        connection.commit()

    except (Exception, psycopg2.Error) as error:
        print("Failed to insert record into mobile table", error)

    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


def userTable_insert_query_to_accounts(user_table):
    # host = '139.59.44.104'
    host = '127.0.0.1'
    connection = None
    try:
        connection = psycopg2.connect(
        database="accounts", user='vikncodes', password='vikncodes123', host=host, port= '5432'
        )
        cursor = connection.cursor()
        postgres_user_query = """ INSERT INTO public."users_userTable" ("id","DefaultAccountForUser","CreatedUserID","CreatedDate","UpdatedDate","Cash_Account","Bank_Account","Sales_Account","Sales_Return_Account","Purchase_Account","Purchase_Return_Account","JoinedDate","ExpiryDate","LeaveDate","Action","is_owner","is_web","is_mobile","is_pos","BranchID","show_all_warehouse","DefaultWarehouse","CompanyID_id","customer_id") VALUES (%(id)s,%(DefaultAccountForUser)s,%(CreatedUserID)s, %(CreatedDate)s,%(UpdatedDate)s,%(Cash_Account)s,%(Bank_Account)s,%(Sales_Account)s,%(Sales_Return_Account)s,%(Purchase_Account)s,%(Purchase_Return_Account)s,%(JoinedDate)s,%(ExpiryDate)s,%(LeaveDate)s,%(Action)s,%(is_owner)s,%(is_web)s,%(is_mobile)s,%(is_pos)s,%(BranchID)s,%(show_all_warehouse)s,%(DefaultWarehouse)s,%(CompanyID_id)s,%(customer_id)s)"""
        user_table_dict = UserTable.objects.filter(pk=user_table.pk).values()[0]
        
        cursor.execute(postgres_user_query,user_table_dict)
        connection.commit()

    except (Exception, psycopg2.Error) as error:
        print("Failed to insert record into mobile table", error)

    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed22222")



def get_today():
    today = date_time.today().strftime('%Y-%m-%d')
    return today


