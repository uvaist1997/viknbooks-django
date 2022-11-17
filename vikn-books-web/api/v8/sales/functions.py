import math
from os import write
import string
import random
from decimal import Decimal
from django.db.models import Max
import re
from api.v8.sales.serializers import SalesMasterReportSerializer, StockValueInventoryFlowSerializer
from brands.models import State, StockPosting, Product
from django.db.models import Sum
from api.v4.ledgerPosting.functions import convertOrderdDict
from datetime import date, timedelta
import calendar
import datetime
from api.v4.loyaltyProgram.functions import get_point_auto_id
from api.v4.accountLedgers.functions import get_auto_LedgerPostid
from brands.models import QrCode, SalesMaster, SalesMaster_Log, SalesDetails, SalesDetails_Log, StockPosting, LedgerPosting,\
    StockPosting_Log, LedgerPosting_Log, Parties, SalesDetailsDummy, StockRate, StockTrans, PriceList, DamageStockMaster, JournalMaster,\
    OpeningStockMaster, PaymentMaster, PurchaseMaster, PurchaseOrderMaster, PurchaseReturnMaster, ReceiptMaster, SalesOrderMaster, SalesEstimateMaster,\
    SalesReturnMaster, StockReceiptMaster_ID, DamageStockMaster, StockTransferMaster_ID, AccountGroup, SalesReturnDetails,\
    AccountLedger, PurchaseDetails, PurchaseReturnDetails, Product, UserTable, ProductGroup, ExcessStockMaster, ShortageStockMaster, DamageStockMaster,\
    UsedStockMaster, GeneralSettings, CompanySettings, WorkOrderMaster, Batch, SerialNumbers, LoyaltyCustomer, LoyaltyProgram, LoyaltyPoint, LoyaltyPoint_Log,\
    SalesOrderDetails, AccountLedger_Log, UQCTable, Unit
from api.v8.sales.serializers import SalesGSTReportSerializer, GST_CDNR_Serializer, GST_B2B_Serializer
from operator import itemgetter
import pandas as pd
import numpy as np
from django.http import HttpResponse
import xlwt
from xlwt import Workbook, XFStyle, Borders, Pattern, Font, easyxf, Alignment
from api.v8.salesReturns.serializers import SalesReturnMasterRestSerializer, SalesReturnMasterReportSerializer
from brands import models as table


def generate_serializer_errors(args):
    message = ""
    for key, values in args.items():
        error_message = ""
        for value in values:
            error_message += value + ","
        error_message = error_message[:-1]

        message += "%s : %s | " % (key, error_message)
    return message[:-3]


def get_auto_idMaster(model, BranchID, CompanyID):
    SalesMasterID = 1
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id = model.objects.filter(
        CompanyID=CompanyID).aggregate(Max('SalesMasterID'))
    if model.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        max_value = model.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID).aggregate(Max('SalesMasterID'))
        if max_value:
            max_salesMasterId = max_value.get('SalesMasterID__max', 0)
            SalesMasterID = max_salesMasterId + 1
        else:
            SalesMasterID = 1
    return SalesMasterID


def get_auto_id(model, BranchID, CompanyID):
    SalesDetailsID = 1
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id = model.objects.filter(
        CompanyID=CompanyID).aggregate(Max('SalesDetailsID'))

    if model.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        max_value = model.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID).aggregate(Max('SalesDetailsID'))

        if max_value:
            max_salesDetailsId = max_value.get('SalesDetailsID__max', 0)

            SalesDetailsID = max_salesDetailsId + 1

        else:
            SalesDetailsID = 1

    return SalesDetailsID


def get_auto_stockPostid(model, BranchID, CompanyID):
    StockPostingID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id = model.objects.filter(
        CompanyID=CompanyID).aggregate(Max('StockPostingID'))

    if model.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        max_value = model.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID).aggregate(Max('StockPostingID'))

        if max_value:
            max_stockPostingId = max_value.get('StockPostingID__max', 0)

            StockPostingID = max_stockPostingId + 1

        else:
            StockPostingID = 1

    return StockPostingID


def get_auto_VoucherNo(model, BranchID, CompanyID):
    VoucherNo = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id = model.objects.filter(
        CompanyID=CompanyID).aggregate(Max('VoucherNo'))

    if model.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        max_value = model.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID).aggregate(Max('VoucherNo'))

        if max_value:
            max_VoucherNo = max_value.get('VoucherNo__max', 0)

            VoucherNo = max_VoucherNo + 1

        else:
            VoucherNo = 1

    return VoucherNo


def get_Genrate_VoucherNo(model, BranchID, CompanyID, VoucherType):
    VoucherNo = VoucherType + str(1)
    if model.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        instance = model.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID).first()
        OldVoucherNo = instance.VoucherNo
        if not OldVoucherNo.isdecimal():
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            VoucherNo = VoucherType + str(new_num)
        else:
            # VoucherNo = float(OldVoucherNo) + 1
            VoucherNo = str(int(OldVoucherNo) +
                            1).zfill(len(OldVoucherNo))

    if model.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherNo=VoucherNo).exists():
        instances = model.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID)
        list_vouchers = instances.values_list('VoucherNo', flat=True)
        all_nos = []
        for v in list_vouchers:
            res = re.search(r"\d+(\.\d+)?", v)
            num = res.group(0)
            all_nos.append(int(num))
        max_no = max(all_nos)
        nxt_no = int(max_no) + 1
        VoucherNo = VoucherType + str(nxt_no)

    return VoucherNo


def get_month(m):
    month = m
    if m == "01":
        month = "January"
    elif m == "02":
        month = "February"
    elif m == "03":
        month = "March"
    elif m == "04":
        month = "April"
    elif m == "05":
        month = "May"
    elif m == "06":
        month = "June"
    elif m == "07":
        month = "July"
    elif m == "08":
        month = "August"
    elif m == "09":
        month = "September"
    elif m == "10":
        month = "October"
    elif m == "11":
        month = "November"
    elif m == "12":
        month = "December"
    return month


def get_stock_value(CompanyID, BranchID, FromDate, ToDate, WarehouseID, PriceRounding):
    GrandTotalCost = 0
    if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
        stock_instances = StockPosting.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)
        if not WarehouseID == 0:
            stock_instances = stock_instances.filter(WareHouseID=WarehouseID)

        product_arry = []
        product_ids = stock_instances.values_list('ProductID')

        for product_id in product_ids:
            if product_id[0] not in product_arry:
                product_arry.append(product_id[0])

        qurried_instances = stock_instances.values('ProductID').annotate(
            in_stock_quantity=Sum('QtyIn') - Sum('QtyOut')).order_by('ProductID')

        product_instances = Product.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, ProductID__in=product_arry)

        stockSerializer = StockValueInventoryFlowSerializer(product_instances, many=True, context={
            "CompanyID": CompanyID, "PriceRounding": PriceRounding, "WareHouseID": WarehouseID, "FromDate": FromDate, "ToDate": ToDate})

        orderdDict = stockSerializer.data
        jsnDatas = convertOrderdDict(orderdDict)
        TotalQty = 0

        for i in jsnDatas:
            if not float(i['Qty']) == 0:
                cost = i['Cost']
                qty = i['Qty']
                TotalCost = float(cost) * float(qty)

                TotalQty += float(i['Qty'])
                GrandTotalCost += TotalCost

    return GrandTotalCost


def get_date_list(start_date):

    # start_date = date(y, m, d)
    days_in_month = calendar.monthrange(start_date.year, start_date.month)[1]
    print("----------------------------")
    # date_month1 = start_date - timedelta(days=days_in_month)
    date_month1 = start_date.date()
    date_month2 = date_month1 - timedelta(days=days_in_month)
    date_month3 = date_month2 - timedelta(days=days_in_month)
    date_month4 = date_month3 - timedelta(days=days_in_month)
    date_month5 = date_month4 - timedelta(days=days_in_month)
    date_month6 = date_month5 - timedelta(days=days_in_month)
    date_month = [date_month1, date_month2, date_month3,
                  date_month4, date_month5, date_month6]
    print(date_month)
    return date_month

# month_list = previous_six_month(2014,12,25)

# month_one = month_list[0]
# print(month_one.year)


def get_Program(instance, loyalty_customer, details, Loyalty_Point_Expire, Action, RadeemPoint):
    today = datetime.datetime.now()
    for salesdetail in details:
        ProductID = salesdetail['ProductID']
        group_id = Product.objects.get(
            BranchID=instance.BranchID, CompanyID=instance.CompanyID, ProductID=ProductID).ProductGroupID
        print(ProductID, '##################################', group_id)
        if LoyaltyProgram.objects.filter(CardTypeID=loyalty_customer.CardTypeID, FromDate__lte=instance.Date, ToDate__gte=instance.Date).exists():
            loyalty_program_insrances = LoyaltyProgram.objects.filter(
                CardTypeID=loyalty_customer.CardTypeID, FromDate__lte=instance.Date, ToDate__gte=instance.Date)
            for i in loyalty_program_insrances:
                if i.ProductType == "Product_group":
                    ProductGroupIDs_arry1 = i.ProductGroupIDs.split(",")
                    while("" in ProductGroupIDs_arry1):
                        ProductGroupIDs_arry1.remove("")
                    if str(group_id) in ProductGroupIDs_arry1:
                        print(group_id, "qqqqqqqqqqqqqqqqqqqqqqqq")
                        loyalty_program = i
                        # ExpiryDate
                        # import datetime
                        # Loyalty_Point_Expire = data['Loyalty_Point_Expire']
                        ExpiryDate = None
                        if Loyalty_Point_Expire:
                            current_date = "12/6/20"
                            current_date_temp = datetime.datetime.strptime(
                                instance.Date, "%Y-%m-%d")
                            ExpiryDate = current_date_temp + \
                                datetime.timedelta(
                                    days=int(loyalty_program.NoOFDayExpPoint))
                        else:
                            current_date_temp = datetime.datetime.strptime(
                                instance.Date, "%Y-%m-%d")
                            ExpiryDate = current_date_temp + \
                                datetime.timedelta(days=int(365))
                        # ====

                        # Loyalty Calculation Start heare************
                        salesdetails = details
                        Group_ids = loyalty_program.ProductGroupIDs.split(',')
                        Cat_ids = loyalty_program.ProductCategoryIDs.split(',')

                        ProductGroupIDs = [i for i in Group_ids if i]
                        ProductCategoryIDs = [i for i in Cat_ids if i]
                        print(ProductGroupIDs, "QQQQQUVAISQQQQQQ",
                              ProductCategoryIDs)
                        # test_list.remove("")
                        tot_TaxableAmount = 0
                        if SalesDetails:
                            for salesdetail in salesdetails:

                                ProductID = salesdetail['ProductID']
                                if ProductGroupIDs:
                                    if Product.objects.filter(BranchID=instance.BranchID, CompanyID=instance.CompanyID, ProductGroupID__in=ProductGroupIDs):
                                        pro_instance = Product.objects.filter(
                                            BranchID=instance.BranchID, CompanyID=instance.CompanyID, ProductGroupID__in=ProductGroupIDs)
                                        for i in pro_instance:
                                            if ProductID == i.ProductID:
                                                tot_TaxableAmount += int(
                                                    salesdetail['TaxableAmount'])
                                elif ProductCategoryIDs:
                                    ProductGroupID = ProductGroup.objects.filter(
                                        BranchID=instance.BranchID, CompanyID=instance.CompanyID, CategoryID__in=ProductCategoryIDs).values_list('ProductGroupID', flat=True)
                                    if Product.objects.filter(BranchID=instance.BranchID, CompanyID=instance.CompanyID, ProductGroupID__in=ProductGroupID):
                                        pro_instance = Product.objects.filter(
                                            BranchID=instance.BranchID, CompanyID=instance.CompanyID, ProductGroupID__in=ProductGroupID)
                                        for i in pro_instance:
                                            if ProductID == i.ProductID:
                                                tot_TaxableAmount += int(
                                                    salesdetail['TaxableAmount'])
                                else:
                                    if Product.objects.filter(BranchID=instance.BranchID, CompanyID=instance.CompanyID):
                                        pro_instance = Product.objects.filter(
                                            BranchID=instance.BranchID, CompanyID=instance.CompanyID)
                                        for i in pro_instance:
                                            if ProductID == i.ProductID:
                                                tot_TaxableAmount += int(
                                                    salesdetail['TaxableAmount'])
                                        TaxableAmount = float(
                                            salesdetail['TaxableAmount'])
                                        # =======*******************============
                        actual_point = 0
                        if tot_TaxableAmount > loyalty_program.MinimumSalePrice:
                            print("VALUTHAAAAN")
                            MinimumSalePrice = loyalty_program.MinimumSalePrice
                            Calculate_with = loyalty_program.Calculate_with

                            if Calculate_with == "Amount":
                                Amount = loyalty_program.Amount
                                Amount_Point = loyalty_program.Amount_Point
                                # ======1st
                                p_amount = Amount_Point/Amount*100
                                # ======2st
                                print(tot_TaxableAmount, "Amount......")
                                actual_point = int(
                                    tot_TaxableAmount)/100*int(p_amount)
                            elif Calculate_with == "Percentage":
                                print("Percentage......")
                                Percentage = loyalty_program.Percentage
                                actual_point = int(
                                    tot_TaxableAmount)/100*int(Percentage)

                            print(tot_TaxableAmount, "tot_TaxableAmount")

                            if actual_point:
                                LoyaltyPointID = get_point_auto_id(
                                    LoyaltyPoint, instance.BranchID, instance.CompanyID)
                                LoyaltyPoint.objects.create(
                                    BranchID=instance.BranchID,
                                    LoyaltyPointID=LoyaltyPointID,
                                    Value=actual_point,
                                    VoucherType="SI",
                                    VoucherMasterID=instance.SalesMasterID,
                                    Point=actual_point,
                                    ExpiryDate=ExpiryDate,
                                    LoyaltyCustomerID=loyalty_customer,
                                    LoyaltyProgramID=loyalty_program,
                                    is_Radeem=False,

                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    Action=instance.Action,
                                    CreatedUserID=instance.CreatedUserID,
                                    CompanyID=instance.CompanyID,
                                )
                                LoyaltyPoint_Log.objects.create(
                                    BranchID=instance.BranchID,
                                    LoyaltyPointID=LoyaltyPointID,
                                    Value=actual_point,
                                    VoucherType="SI",
                                    VoucherMasterID=instance.SalesMasterID,
                                    Point=actual_point,
                                    ExpiryDate=ExpiryDate,
                                    LoyaltyCustomerID=loyalty_customer,
                                    LoyaltyProgramID=loyalty_program,
                                    is_Radeem=False,

                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    Action=instance.Action,
                                    CreatedUserID=instance.CreatedUserID,
                                    CompanyID=instance.CompanyID,
                                )
                        print(loyalty_program.MinimumSalePrice, actual_point,
                              'LoyaltyCustomerIDLoyaltyCustomerIDLoyaltyCustomerID')
                        # Loyalty Calculation END heare******************
                        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<Radeem Loyalty Point Start heare>>>>>>>>>>>>

                        if RadeemPoint:
                            radeem = RadeemPoint.split("")
                            radeem_value = radeem[1]
                            radeem_point = int(radeem[0]) * -1
                            if int(instance.GrandTotal) >= int(radeem_value):
                                print(
                                    radeem_point, 'radeem_point +++++++++++++++++ RadeemPoint', RadeemPoint)
                                LoyaltyPointID = get_point_auto_id(
                                    LoyaltyPoint, instance.BranchID, instance.CompanyID)
                                LoyaltyPoint.objects.create(
                                    BranchID=instance.BranchID,
                                    LoyaltyPointID=LoyaltyPointID,
                                    Value=radeem_value,
                                    VoucherType="SI",
                                    VoucherMasterID=instance.SalesMasterID,
                                    Point=radeem_point,
                                    ExpiryDate=ExpiryDate,
                                    LoyaltyCustomerID=loyalty_customer,
                                    LoyaltyProgramID=loyalty_program,
                                    is_Radeem=True,

                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    Action=instance.Action,
                                    CreatedUserID=instance.CreatedUserID,
                                    CompanyID=instance.CompanyID,
                                )
                                LoyaltyPoint_Log.objects.create(
                                    BranchID=instance.BranchID,
                                    LoyaltyPointID=LoyaltyPointID,
                                    Value=radeem_value,
                                    VoucherType="SI",
                                    VoucherMasterID=instance.SalesMasterID,
                                    Point=radeem_point,
                                    ExpiryDate=ExpiryDate,
                                    LoyaltyCustomerID=loyalty_customer,
                                    LoyaltyProgramID=loyalty_program,
                                    is_Radeem=True,

                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    Action=instance.Action,
                                    CreatedUserID=instance.CreatedUserID,
                                    CompanyID=instance.CompanyID,
                                )

                                # <<<<<LedgerPosting>>>
                                LedgerPostingID = get_auto_LedgerPostid(
                                    LedgerPosting, instance.BranchID, instance.CompanyID)
                                LedgerPosting.objects.create(
                                    LedgerPostingID=LedgerPostingID,
                                    BranchID=instance.BranchID,
                                    Date=instance.Date,
                                    VoucherMasterID=instance.SalesMasterID,
                                    VoucherType="SI",
                                    VoucherNo=instance.VoucherNo,
                                    LedgerID=73,
                                    Debit=radeem_value,
                                    IsActive=instance.IsActive,
                                    Action=instance.Action,
                                    CreatedUserID=instance.CreatedUserID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CompanyID=instance.CompanyID,
                                )

                                LedgerPosting_Log.objects.create(
                                    TransactionID=LedgerPostingID,
                                    BranchID=instance.BranchID,
                                    Date=instance.Date,
                                    VoucherMasterID=instance.SalesMasterID,
                                    VoucherType="SI",
                                    VoucherNo=instance.VoucherNo,
                                    LedgerID=73,
                                    Debit=radeem_value,
                                    IsActive=instance.IsActive,
                                    Action=instance.Action,
                                    CreatedUserID=instance.CreatedUserID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CompanyID=instance.CompanyID,
                                )
                                # <<<<<LedgerPosting END HEARE>>>

                            print(radeem_point, RadeemPoint.split("-"))
                            sale_date = str_To_Date(instance.Date)
                            if LoyaltyPoint.objects.filter(BranchID=instance.BranchID, CompanyID=instance.CompanyID, LoyaltyCustomerID=loyalty_customer, VoucherType="SI", ExpiryDate__gte=sale_date, is_Radeem=False).exists():
                                point_instances = LoyaltyPoint.objects.filter(
                                    BranchID=instance.BranchID, CompanyID=instance.CompanyID, LoyaltyCustomerID=loyalty_customer, VoucherType="SI", ExpiryDate__gte=sale_date, is_Radeem=False).order_by("LoyaltyPointID")
                                balance_point = float(radeem[0])
                                for i in point_instances:
                                    Point = float(i.Point)
                                    if i.Radeemed_Point:
                                        Radeemed_Point = float(
                                            i.Radeemed_Point)
                                        float(i.Radeemed_Point)
                                    else:
                                        Radeemed_Point = 0
                                    Point = float(i.Point)
                                    if not balance_point <= 0:
                                        w = Point - Radeemed_Point
                                        if float(w) <= float(balance_point) and Point != Radeemed_Point:

                                            # =================

                                            # =================

                                            print(
                                                Point, 'ifAAAAAAAAAAA', Radeemed_Point, 'UVAISANNNNNNNNNNNNN', balance_point)
                                            print("IFFFFFFF")
                                            balance_point -= w
                                            # balance_point = balance_point+Radeemed_Point - Point
                                            b = float(Radeemed_Point) + w
                                            i.Radeemed_Point = b
                                        elif w >= balance_point and Point != Radeemed_Point:
                                            print(
                                                Point, 'ElseAAAAAAAAAAA', Radeemed_Point, 'UVAISANNNNNNNNNNNNN', balance_point)

                                            i.Radeemed_Point = balance_point+Radeemed_Point
                                            balance_point -= balance_point

                                            # b = Radeemed_Point + balance_point
                                            # q = Point - Radeemed_Point
                                            # ==========
                                            # i.Radeemed_Point = Radeemed_Point + q
                                            # ==========

                                            # if Point <= q:
                                            #     i.Radeemed_Point = balance_point
                                            #     balance_point = 0
                                            #     print(balance_point,"ELSEIFFFFFFF1")
                                            # elif Point >= Radeemed_Point:
                                            #     balance_point = balance_point - q
                                            #     if balance_point > 0:
                                            #         i.Radeemed_Point = Radeemed_Point + q
                                            #         print(balance_point,"!!!!!!!!!!!!!!!!!!!!1")
                                            #     else:
                                            #         print(balance_point,"2222222222222222222")
                                            #         i.Radeemed_Point = Radeemed_Point+abs(balance_point)
                                            #         balance_point = 0
                                            #     print(balance_point,"ELSEIFFFFFFF2")
                                        i.save()
                                        if balance_point <= 0:
                                            break

                        # TOTAL LOYALTY Customer Point
                        is_edit = False
                        if LoyaltyPoint.objects.filter(BranchID=instance.BranchID, CompanyID=instance.CompanyID, VoucherType="SI", LoyaltyCustomerID=loyalty_customer, is_Radeem=True).exists():
                            is_edit = True
                        if LoyaltyPoint.objects.filter(LoyaltyCustomerID=loyalty_customer, BranchID=instance.BranchID, CompanyID=instance.CompanyID).exists():
                            loyalty_instances = LoyaltyPoint.objects.filter(
                                LoyaltyCustomerID=loyalty_customer, BranchID=instance.BranchID, CompanyID=instance.CompanyID)

                            tot_Point = 0
                            # today_date = datetime.datetime.now().date()
                            today_date = str_To_Date(instance.Date)

                            for i in loyalty_instances:
                                if i.Point:
                                    if Loyalty_Point_Expire:
                                        if i.ExpiryDate:
                                            if not today_date >= i.ExpiryDate:
                                                if Action == "M":
                                                    if is_edit:
                                                        tot_Point = float(
                                                            tot_Point) + float(i.Point)
                                                elif Action == "A":
                                                    tot_Point = float(
                                                        tot_Point) + float(i.Point)
                                    else:
                                        if Action == "M":
                                            if is_edit:
                                                tot_Point = float(
                                                    tot_Point) + float(i.Point)
                                        elif Action == "A":
                                            tot_Point += float(i.Point)
                            if LoyaltyCustomer.objects.filter(pk=loyalty_customer.pk).exists():
                                ins = LoyaltyCustomer.objects.get(
                                    pk=loyalty_customer.pk)
                                ins.CurrentPoint = tot_Point
                                ins.save()
                    print(ProductGroupIDs_arry1, 'oooooooooooProduct_group')


def set_LoyaltyCalculation(instance, loyalty_customer, details, Loyalty_Point_Expire, Action, RadeemPoint):
    print("CUSTPOMEERRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")
    # ====== Loyalty Program Point
    today = datetime.datetime.now()
    loyalty_program = None
    if LoyaltyProgram.objects.filter(CardTypeID=loyalty_customer.CardTypeID, FromDate__lte=instance.Date, ToDate__gte=instance.Date).exists():
        loyalty_program = LoyaltyProgram.objects.get(
            CardTypeID=loyalty_customer.CardTypeID, FromDate__lte=instance.Date, ToDate__gte=instance.Date)
    if loyalty_program:
        # ExpiryDate
        # import datetime
        # Loyalty_Point_Expire = data['Loyalty_Point_Expire']
        ExpiryDate = None
        if Loyalty_Point_Expire:
            current_date = "12/6/20"
            current_date_temp = datetime.datetime.strptime(
                instance.Date, "%Y-%m-%d")
            ExpiryDate = current_date_temp + \
                datetime.timedelta(days=int(loyalty_program.NoOFDayExpPoint))
        else:
            current_date_temp = datetime.datetime.strptime(
                instance.Date, "%Y-%m-%d")
            ExpiryDate = current_date_temp + datetime.timedelta(days=int(365))
        # ====

        # Loyalty Calculation Start heare************
        salesdetails = details
        Group_ids = loyalty_program.ProductGroupIDs.split(',')
        Cat_ids = loyalty_program.ProductCategoryIDs.split(',')

        ProductGroupIDs = [i for i in Group_ids if i]
        ProductCategoryIDs = [i for i in Cat_ids if i]

        # test_list.remove("")
        tot_TaxableAmount = 0
        if SalesDetails:
            for salesdetail in salesdetails:

                ProductID = salesdetail['ProductID']
                if ProductGroupIDs:
                    if Product.objects.filter(BranchID=instance.BranchID, CompanyID=instance.CompanyID, ProductGroupID__in=ProductGroupIDs):
                        pro_instance = Product.objects.filter(
                            BranchID=instance.BranchID, CompanyID=instance.CompanyID, ProductGroupID__in=ProductGroupIDs)
                        print(pro_instance, "QQQQQUVA*****2******ISQQQQQQ",
                              tot_TaxableAmount)
                        for i in pro_instance:
                            if ProductID == i.ProductID:
                                tot_TaxableAmount += int(
                                    salesdetail['TaxableAmount'])
                                print(loyalty_program.MinimumSalePrice,
                                      "QQQQQUVA*****3******ISQQQQQQ", tot_TaxableAmount)
                elif ProductCategoryIDs:
                    ProductGroupID = ProductGroup.objects.filter(
                        BranchID=instance.BranchID, CompanyID=instance.CompanyID, CategoryID__in=ProductCategoryIDs).values_list('ProductGroupID', flat=True)
                    if Product.objects.filter(BranchID=instance.BranchID, CompanyID=instance.CompanyID, ProductGroupID__in=ProductGroupID):
                        pro_instance = Product.objects.filter(
                            BranchID=instance.BranchID, CompanyID=instance.CompanyID, ProductGroupID__in=ProductGroupID)
                        for i in pro_instance:
                            if ProductID == i.ProductID:
                                tot_TaxableAmount += int(
                                    salesdetail['TaxableAmount'])
                else:
                    if Product.objects.filter(BranchID=instance.BranchID, CompanyID=instance.CompanyID):
                        pro_instance = Product.objects.filter(
                            BranchID=instance.BranchID, CompanyID=instance.CompanyID)
                        for i in pro_instance:
                            if ProductID == i.ProductID:
                                tot_TaxableAmount += int(
                                    salesdetail['TaxableAmount'])
                        TaxableAmount = float(salesdetail['TaxableAmount'])
                        # =======*******************============
        actual_point = 0
        print(loyalty_program.MinimumSalePrice,
              "QQQQQUVA*****laast******ISQQQQQQ", tot_TaxableAmount)
        if tot_TaxableAmount > loyalty_program.MinimumSalePrice:
            print("VALUTHAAAAN")
            MinimumSalePrice = loyalty_program.MinimumSalePrice
            Calculate_with = loyalty_program.Calculate_with

            if Calculate_with == "Amount":
                Amount = loyalty_program.Amount
                Amount_Point = loyalty_program.Amount_Point
                # ======1st
                p_amount = Amount_Point/Amount*100
                # ======2st
                print(tot_TaxableAmount, "Amount......")
                actual_point = int(tot_TaxableAmount)/100*int(p_amount)
            elif Calculate_with == "Percentage":
                print("Percentage......")
                Percentage = loyalty_program.Percentage
                actual_point = int(tot_TaxableAmount)/100*int(Percentage)

            print(tot_TaxableAmount, "tot_TaxableAmount")

            if actual_point:
                LoyaltyPointID = get_point_auto_id(
                    LoyaltyPoint, instance.BranchID, instance.CompanyID)
                LoyaltyPoint.objects.create(
                    BranchID=instance.BranchID,
                    LoyaltyPointID=LoyaltyPointID,
                    Value=actual_point,
                    VoucherType="SI",
                    VoucherMasterID=instance.SalesMasterID,
                    Point=actual_point,
                    ExpiryDate=ExpiryDate,
                    LoyaltyCustomerID=loyalty_customer,
                    LoyaltyProgramID=loyalty_program,
                    is_Radeem=False,

                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=instance.Action,
                    CreatedUserID=instance.CreatedUserID,
                    CompanyID=instance.CompanyID,
                )
                LoyaltyPoint_Log.objects.create(
                    BranchID=instance.BranchID,
                    LoyaltyPointID=LoyaltyPointID,
                    Value=actual_point,
                    VoucherType="SI",
                    VoucherMasterID=instance.SalesMasterID,
                    Point=actual_point,
                    ExpiryDate=ExpiryDate,
                    LoyaltyCustomerID=loyalty_customer,
                    LoyaltyProgramID=loyalty_program,
                    is_Radeem=False,

                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=instance.Action,
                    CreatedUserID=instance.CreatedUserID,
                    CompanyID=instance.CompanyID,
                )
        print(loyalty_program.MinimumSalePrice, actual_point,
              'LoyaltyCustomerIDLoyaltyCustomerIDLoyaltyCustomerID')
        # Loyalty Calculation END heare******************
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<Radeem Loyalty Point Start heare>>>>>>>>>>>>
        loyalty_point_value = None
        if GeneralSettings.objects.filter(CompanyID=instance.CompanyID, SettingsType="loyalty_point_value").exists():
            loyalty_point_value = GeneralSettings.objects.get(
                CompanyID=instance.CompanyID, SettingsType="loyalty_point_value").SettingsValue
        if RadeemPoint and loyalty_point_value:
            print(RadeemPoint, "*********************************************************************************************************", loyalty_point_value)
            # radeem = RadeemPoint.split("-")
            # radeem_value = radeem[1]
            # radeem_point = int(radeem[0]) * -1
            radeem_value = int(loyalty_point_value)*int(RadeemPoint)
            radeem_point = int(RadeemPoint) * -1
            if int(instance.GrandTotal) >= int(radeem_value):
                LoyaltyPointID = get_point_auto_id(
                    LoyaltyPoint, instance.BranchID, instance.CompanyID)
                a = LoyaltyPoint.objects.create(
                    BranchID=instance.BranchID,
                    LoyaltyPointID=LoyaltyPointID,
                    Value=radeem_value,
                    VoucherType="SI",
                    VoucherMasterID=instance.SalesMasterID,
                    Point=radeem_point,
                    ExpiryDate=ExpiryDate,
                    LoyaltyCustomerID=loyalty_customer,
                    LoyaltyProgramID=loyalty_program,
                    is_Radeem=True,

                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=instance.Action,
                    CreatedUserID=instance.CreatedUserID,
                    CompanyID=instance.CompanyID,
                )
                LoyaltyPoint_Log.objects.create(
                    BranchID=instance.BranchID,
                    LoyaltyPointID=LoyaltyPointID,
                    Value=radeem_value,
                    VoucherType="SI",
                    VoucherMasterID=instance.SalesMasterID,
                    Point=radeem_point,
                    ExpiryDate=ExpiryDate,
                    LoyaltyCustomerID=loyalty_customer,
                    LoyaltyProgramID=loyalty_program,
                    is_Radeem=True,

                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=instance.Action,
                    CreatedUserID=instance.CreatedUserID,
                    CompanyID=instance.CompanyID,
                )

                # <<<<<LedgerPosting>>>
                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, instance.BranchID, instance.CompanyID)
                print(radeem_point, 'radeem_point ++++++++*********HAB',
                      a, 'EEB*********+++++++++ RadeemPoint', RadeemPoint)
                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=instance.BranchID,
                    Date=instance.Date,
                    VoucherMasterID=instance.SalesMasterID,
                    VoucherType="SI",
                    VoucherNo=instance.VoucherNo,
                    LedgerID=73,
                    Debit=radeem_value,
                    IsActive=instance.IsActive,
                    Action=instance.Action,
                    CreatedUserID=instance.CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=instance.CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=instance.BranchID,
                    Date=instance.Date,
                    VoucherMasterID=instance.SalesMasterID,
                    VoucherType="SI",
                    VoucherNo=instance.VoucherNo,
                    LedgerID=73,
                    Debit=radeem_value,
                    IsActive=instance.IsActive,
                    Action=instance.Action,
                    CreatedUserID=instance.CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=instance.CompanyID,
                )
                # <<<<<LedgerPosting END HEARE>>>

            # print(radeem_point,RadeemPoint.split("-"))
            sale_date = str_To_Date(instance.Date)
            if LoyaltyPoint.objects.filter(BranchID=instance.BranchID, CompanyID=instance.CompanyID, LoyaltyCustomerID=loyalty_customer, VoucherType="SI", ExpiryDate__gte=sale_date, is_Radeem=False).exists():
                point_instances = LoyaltyPoint.objects.filter(BranchID=instance.BranchID, CompanyID=instance.CompanyID, LoyaltyCustomerID=loyalty_customer,
                                                              VoucherType="SI", ExpiryDate__gte=sale_date, is_Radeem=False).order_by("LoyaltyPointID")
                # balance_point = float(radeem[0])
                balance_point = int(RadeemPoint)
                for i in point_instances:
                    Point = float(i.Point)
                    if i.Radeemed_Point:
                        Radeemed_Point = float(i.Radeemed_Point)
                        float(i.Radeemed_Point)
                    else:
                        Radeemed_Point = 0
                    Point = float(i.Point)
                    if not balance_point <= 0:
                        w = Point - Radeemed_Point
                        if float(w) <= float(balance_point) and Point != Radeemed_Point:

                            # =================

                            # =================

                            print(Point, 'ifAAAAAAAAAAA', Radeemed_Point,
                                  'UVAISANNNNNNNNNNNNN', balance_point)
                            print("IFFFFFFF")
                            balance_point -= w
                            # balance_point = balance_point+Radeemed_Point - Point
                            b = float(Radeemed_Point) + w
                            i.Radeemed_Point = b
                        elif w >= balance_point and Point != Radeemed_Point:
                            print(Point, 'ElseAAAAAAAAAAA', Radeemed_Point,
                                  'UVAISANNNNNNNNNNNNN', balance_point)

                            i.Radeemed_Point = balance_point+Radeemed_Point
                            balance_point -= balance_point

                            # b = Radeemed_Point + balance_point
                            # q = Point - Radeemed_Point
                            # ==========
                            # i.Radeemed_Point = Radeemed_Point + q
                            # ==========

                            # if Point <= q:
                            #     i.Radeemed_Point = balance_point
                            #     balance_point = 0
                            #     print(balance_point,"ELSEIFFFFFFF1")
                            # elif Point >= Radeemed_Point:
                            #     balance_point = balance_point - q
                            #     if balance_point > 0:
                            #         i.Radeemed_Point = Radeemed_Point + q
                            #         print(balance_point,"!!!!!!!!!!!!!!!!!!!!1")
                            #     else:
                            #         print(balance_point,"2222222222222222222")
                            #         i.Radeemed_Point = Radeemed_Point+abs(balance_point)
                            #         balance_point = 0
                            #     print(balance_point,"ELSEIFFFFFFF2")
                        i.save()
                        if balance_point <= 0:
                            break

        # TOTAL LOYALTY Customer Point
        is_edit = False
        if LoyaltyPoint.objects.filter(BranchID=instance.BranchID, CompanyID=instance.CompanyID, VoucherType="SI", LoyaltyCustomerID=loyalty_customer, is_Radeem=True).exists():
            is_edit = True
        if LoyaltyPoint.objects.filter(LoyaltyCustomerID=loyalty_customer, BranchID=instance.BranchID, CompanyID=instance.CompanyID).exists():
            loyalty_instances = LoyaltyPoint.objects.filter(
                LoyaltyCustomerID=loyalty_customer, BranchID=instance.BranchID, CompanyID=instance.CompanyID)

            tot_Point = 0
            # today_date = datetime.datetime.now().date()
            today_date = str_To_Date(instance.Date)

            for i in loyalty_instances:
                if i.Point:
                    if Loyalty_Point_Expire:
                        if i.ExpiryDate:
                            if not today_date >= i.ExpiryDate:
                                if Action == "M":
                                    if is_edit:
                                        tot_Point = float(
                                            tot_Point) + float(i.Point)
                                elif Action == "A":
                                    tot_Point = float(
                                        tot_Point) + float(i.Point)
                    else:
                        if Action == "M":
                            if is_edit:
                                tot_Point = float(tot_Point) + float(i.Point)
                        elif Action == "A":
                            tot_Point += float(i.Point)
            if LoyaltyCustomer.objects.filter(pk=loyalty_customer.pk).exists():
                ins = LoyaltyCustomer.objects.get(pk=loyalty_customer.pk)
                ins.CurrentPoint = tot_Point
                ins.save()

        # >>>>>>>>>>>>>>>Radeem Loyalty Point End heare>>>>>>>>>>>>>>


def str_To_Date(date):
    # converting string type to date type
    date_time_str = str(date) + str(" ") + str('00:00:00')
    date_time_obj = datetime.datetime.strptime(
        date_time_str, '%Y-%m-%d %H:%M:%S')
    date = date_time_obj.date()
    return date


def get_actual_point(tot_TaxableAmount, instance):
    if instance.Calculate_with == "Amount":
        Amount = instance.Amount
        Amount_Point = instance.Amount_Point
        # ======1st
        p_amount = Amount_Point/Amount*100
        # ======2st
        print(tot_TaxableAmount, "Amount......")
        actual_point = int(tot_TaxableAmount)/100*int(p_amount)
    elif instance.Calculate_with == "Percentage":
        print("Percentage......")
        Percentage = instance.Percentage
        actual_point = int(tot_TaxableAmount)/100*int(Percentage)
    return actual_point


def edit_LoyaltyCalculation(instance, loyalty_customer, details, Loyalty_Point_Expire, RadeemPoint):
    today = datetime.datetime.now()
    print(loyalty_customer.CardTypeID.Name)
    loyalty_program = None
    if LoyaltyProgram.objects.filter(CardTypeID=loyalty_customer.CardTypeID, FromDate__lte=instance.Date, ToDate__gte=instance.Date).exists():
        loyalty_program = LoyaltyProgram.objects.get(
            CardTypeID=loyalty_customer.CardTypeID, FromDate__lte=instance.Date, ToDate__gte=instance.Date)

    # ExpiryDate
    # import datetime
    # Loyalty_Point_Expire = data['Loyalty_Point_Expire']
    ExpiryDate = None
    if Loyalty_Point_Expire:
        current_date = "12/6/20"
        current_date_temp = datetime.datetime.strptime(
            instance.Date, "%Y-%m-%d")
        ExpiryDate = current_date_temp + \
            datetime.timedelta(days=int(loyalty_program.NoOFDayExpPoint))
    else:
        current_date_temp = datetime.datetime.strptime(
            instance.Date, "%Y-%m-%d")
        ExpiryDate = current_date_temp + datetime.timedelta(days=int(365))
    # ====

    # Loyalty Calculation Start heare************
    salesdetails = details
    Group_ids = loyalty_program.ProductGroupIDs.split(',')
    Cat_ids = loyalty_program.ProductCategoryIDs.split(',')

    ProductGroupIDs = [i for i in Group_ids if i]
    ProductCategoryIDs = [i for i in Cat_ids if i]
    print(ProductGroupIDs, "QQQQQUVAISQQQQQQ", ProductCategoryIDs)
    tot_TaxableAmount = 0
    if SalesDetails:
        for salesdetail in salesdetails:

            ProductID = salesdetail['ProductID']
            # BranchID = instance.BranchID
            # CompanyID = instance.CompanyID
            if ProductGroupIDs:
                if Product.objects.filter(BranchID=instance.BranchID, CompanyID=instance.CompanyID, ProductGroupID__in=ProductGroupIDs):
                    pro_instance = Product.objects.filter(
                        BranchID=instance.BranchID, CompanyID=instance.CompanyID, ProductGroupID__in=ProductGroupIDs)
                    for i in pro_instance:
                        if ProductID == i.ProductID:
                            tot_TaxableAmount += int(
                                salesdetail['TaxableAmount'])
            elif ProductCategoryIDs:
                ProductGroupID = ProductGroup.objects.filter(
                    BranchID=instance.BranchID, CompanyID=instance.CompanyID, CategoryID__in=ProductCategoryIDs).values_list('ProductGroupID', flat=True)
                if Product.objects.filter(BranchID=instance.BranchID, CompanyID=instance.CompanyID, ProductGroupID__in=ProductGroupID):
                    pro_instance = Product.objects.filter(
                        BranchID=instance.BranchID, CompanyID=instance.CompanyID, ProductGroupID__in=ProductGroupID)
                    for i in pro_instance:
                        if ProductID == i.ProductID:
                            tot_TaxableAmount += int(
                                salesdetail['TaxableAmount'])
            else:
                if Product.objects.filter(BranchID=instance.BranchID, CompanyID=instance.CompanyID):
                    pro_instance = Product.objects.filter(
                        BranchID=instance.BranchID, CompanyID=instance.CompanyID)
                    for i in pro_instance:
                        if ProductID == i.ProductID:
                            tot_TaxableAmount += int(
                                salesdetail['TaxableAmount'])
                    TaxableAmount = float(salesdetail['TaxableAmount'])
                    # =======*******************============
    actual_point = 0
    if tot_TaxableAmount > loyalty_program.MinimumSalePrice:
        print("VALUTHAAAAN")
        MinimumSalePrice = loyalty_program.MinimumSalePrice
        Calculate_with = loyalty_program.Calculate_with

        if Calculate_with == "Amount":
            Amount = loyalty_program.Amount
            Amount_Point = loyalty_program.Amount_Point
            # ======1st
            p_amount = Amount_Point/Amount*100
            # ======2st
            print(tot_TaxableAmount, "Amount......")
            actual_point = int(tot_TaxableAmount)/100*int(p_amount)
        elif Calculate_with == "Percentage":
            print("Percentage......")
            Percentage = loyalty_program.Percentage
            actual_point = int(tot_TaxableAmount)/100*int(Percentage)

        print(actual_point, "instance")

        if actual_point:
            point_radeemd = []
            LoyaltyPointID = None
            if LoyaltyPoint.objects.filter(BranchID=instance.BranchID, CompanyID=instance.CompanyID, VoucherType="SI", VoucherMasterID=instance.SalesMasterID, is_Radeem=False).exists():
                point_instance = LoyaltyPoint.objects.get(
                    BranchID=instance.BranchID, CompanyID=instance.CompanyID, VoucherType="SI", VoucherMasterID=instance.SalesMasterID, is_Radeem=False)
                # point_instance.Point = actual_point
                # point_instance.Value = actual_point
                # LoyaltyPointID = point_instance.LoyaltyPointID
                point_radeemd.append(point_instance.Radeemed_Point)
                point_instance.delete()
            print(point_radeemd, 'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY')

            LoyaltyPointID = get_point_auto_id(
                LoyaltyPoint, instance.BranchID, instance.CompanyID)
            LoyaltyPoint.objects.create(
                BranchID=instance.BranchID,
                LoyaltyPointID=LoyaltyPointID,
                Value=actual_point,
                VoucherType="SI",
                VoucherMasterID=instance.SalesMasterID,
                Point=actual_point,
                ExpiryDate=ExpiryDate,
                LoyaltyCustomerID=loyalty_customer,
                LoyaltyProgramID=loyalty_program,
                is_Radeem=False,

                CreatedDate=today,
                UpdatedDate=today,
                Action=instance.Action,
                CreatedUserID=instance.CreatedUserID,
                CompanyID=instance.CompanyID,
            )
            LoyaltyPoint_Log.objects.create(
                BranchID=instance.BranchID,
                LoyaltyPointID=LoyaltyPointID,
                Value=actual_point,
                VoucherType="SI",
                VoucherMasterID=instance.SalesMasterID,
                Point=actual_point,
                ExpiryDate=ExpiryDate,
                LoyaltyCustomerID=loyalty_customer,
                LoyaltyProgramID=loyalty_program,
                is_Radeem=False,

                CreatedDate=today,
                UpdatedDate=today,
                Action=instance.Action,
                CreatedUserID=instance.CreatedUserID,
                CompanyID=instance.CompanyID,
            )
    # Loyalty Calculation END heare******************
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<Radeem Loyalty Point Start heare>>>>>>>>>>>>
    if RadeemPoint:
        RadeemPoint = RadeemPoint
    else:
        RadeemPoint = None
    loyalty_point_value = None
    if GeneralSettings.objects.filter(CompanyID=instance.CompanyID, SettingsType="loyalty_point_value").exists():
        loyalty_point_value = GeneralSettings.objects.get(
            CompanyID=instance.CompanyID, SettingsType="loyalty_point_value").SettingsValue
    if RadeemPoint and loyalty_point_value:
        # radeem = RadeemPoint.split("-")
        # radeem_value = radeem[1]
        radeem_value = int(loyalty_point_value)*int(RadeemPoint)
        radeem_point = int(RadeemPoint) * -1
        if int(instance.GrandTotal) >= int(radeem_value):
            if LoyaltyPoint.objects.filter(BranchID=instance.BranchID, CompanyID=instance.CompanyID, VoucherType="SI", VoucherMasterID=instance.SalesMasterID, is_Radeem=True).exists():
                radeem_instance = LoyaltyPoint.objects.get(
                    BranchID=instance.BranchID, CompanyID=instance.CompanyID, VoucherType="SI", VoucherMasterID=instance.SalesMasterID, is_Radeem=True)
                # radeem_instance.Value=radeem_value,
                # radeem_instance.VoucherType="SI",
                # radeem_instance.VoucherMasterID=instance.SalesMasterID,
                # radeem_instance.Point=radeem_point,
                # radeem_instance.ExpiryDate=ExpiryDate,
                # radeem_instance.LoyaltyCustomerID=loyalty_customer,
                # radeem_instance.LoyaltyProgramID=loyalty_program,
                radeem_instance.delete()
            print(radeem_point,
                  'radeem_point +++++++++++++++++ RadeemPoint', RadeemPoint)
            LoyaltyPointID = get_point_auto_id(
                LoyaltyPoint, instance.BranchID, instance.CompanyID)
            LoyaltyPoint.objects.create(
                BranchID=instance.BranchID,
                LoyaltyPointID=LoyaltyPointID,
                Value=radeem_value,
                VoucherType="SI",
                VoucherMasterID=instance.SalesMasterID,
                Point=radeem_point,
                ExpiryDate=ExpiryDate,
                LoyaltyCustomerID=loyalty_customer,
                LoyaltyProgramID=loyalty_program,
                is_Radeem=True,

                CreatedDate=today,
                UpdatedDate=today,
                Action=instance.Action,
                CreatedUserID=instance.CreatedUserID,
                CompanyID=instance.CompanyID,
            )
            LoyaltyPoint_Log.objects.create(
                BranchID=instance.BranchID,
                LoyaltyPointID=LoyaltyPointID,
                Value=radeem_value,
                VoucherType="SI",
                VoucherMasterID=instance.SalesMasterID,
                Point=radeem_point,
                ExpiryDate=ExpiryDate,
                LoyaltyCustomerID=loyalty_customer,
                LoyaltyProgramID=loyalty_program,
                is_Radeem=True,

                CreatedDate=today,
                UpdatedDate=today,
                Action=instance.Action,
                CreatedUserID=instance.CreatedUserID,
                CompanyID=instance.CompanyID,
            )

            # <<<<<LedgerPosting>>>
            # delete and add LedgerPosting
            if LedgerPosting.objects.filter(CompanyID=instance.CompanyID, BranchID=instance.BranchID, VoucherMasterID=instance.SalesMasterID, VoucherType="SI", LedgerID=73).exists():
                print("DELETELEDGERPOST....")
                ledger_ins = LedgerPosting.objects.get(
                    CompanyID=instance.CompanyID, BranchID=instance.BranchID, VoucherMasterID=instance.SalesMasterID, VoucherType="SI", LedgerID=73)
                ledger_ins.delete()
            LedgerPostingID = get_auto_LedgerPostid(
                LedgerPosting, instance.BranchID, instance.CompanyID)
            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=instance.BranchID,
                Date=instance.Date,
                VoucherMasterID=instance.SalesMasterID,
                VoucherType="SI",
                VoucherNo=instance.VoucherNo,
                LedgerID=73,
                Debit=radeem_value,
                IsActive=instance.IsActive,
                Action=instance.Action,
                CreatedUserID=instance.CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=instance.CompanyID,
            )

            LedgerPosting_Log.objects.create(
                TransactionID=LedgerPostingID,
                BranchID=instance.BranchID,
                Date=instance.Date,
                VoucherMasterID=instance.SalesMasterID,
                VoucherType="SI",
                VoucherNo=instance.VoucherNo,
                LedgerID=73,
                Debit=radeem_value,
                IsActive=instance.IsActive,
                Action=instance.Action,
                CreatedUserID=instance.CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=instance.CompanyID,
            )
            # <<<<<LedgerPosting END HEARE>>>

            print(radeem_point, RadeemPoint.split("-"))
            sale_date = str_To_Date(instance.Date)
            if LoyaltyPoint.objects.filter(BranchID=instance.BranchID, CompanyID=instance.CompanyID, LoyaltyCustomerID=loyalty_customer, VoucherType="SI", ExpiryDate__gte=sale_date, is_Radeem=False).exists():
                point_instances = LoyaltyPoint.objects.filter(BranchID=instance.BranchID, CompanyID=instance.CompanyID,
                                                              LoyaltyCustomerID=loyalty_customer, VoucherType="SI", ExpiryDate__gte=sale_date, is_Radeem=False)
                print(
                    radeem_point, '2POOOOOOOOOOOOOOO(++++++++++++++++++++++++++++++++++++++++++++++++++))NNNNNNNNNTTTTTTT')
                balance_point = int(RadeemPoint)
                for i in point_instances:
                    Point = float(i.Point)
                    if i.Radeemed_Point:
                        Radeemed_Point = float(i.Radeemed_Point)
                        float(i.Radeemed_Point)
                    else:
                        Radeemed_Point = 0
                    Point = float(i.Point)
                    print(Point, 'EQUALAAAAAAAAAAA', Radeemed_Point,
                          'UVAISANNNNNNNNNNNNN', balance_point)
                    if float(Point) <= float(balance_point)+float(Radeemed_Point) and Point != Radeemed_Point:
                        # if Point <= balance_point+Radeemed_Point and Point != Radeemed_Point:
                        print("IFFFFFFF")
                        balance_point = balance_point+Radeemed_Point - Point
                        b = float(Radeemed_Point) + Point
                        i.Radeemed_Point = b
                    elif Point >= balance_point and Point != Radeemed_Point:
                        i.Radeemed_Point = Radeemed_Point + balance_point
                        # i.Radeemed_Point =  balance_point
                        balance_point = 0
                        print(balance_point, "ELSEIFFFFFFF")
                    i.save()

            print(radeem_point, RadeemPoint.split("-"))
    # >>>>>>>>>>>>>>>Radeem Loyalty Point End heare>>>>>>>>>>>>>>
    # TOTAL LOYALTY Customer Point
    is_edit = False
    if LoyaltyPoint.objects.filter(BranchID=instance.BranchID, CompanyID=instance.CompanyID, VoucherType="SI", LoyaltyCustomerID=loyalty_customer, is_Radeem=True).exists():
        is_edit = True
    if LoyaltyPoint.objects.filter(LoyaltyCustomerID=loyalty_customer, BranchID=instance.BranchID, CompanyID=instance.CompanyID, VoucherType="SI").exists():
        instances = LoyaltyPoint.objects.filter(
            LoyaltyCustomerID=loyalty_customer, BranchID=instance.BranchID, CompanyID=instance.CompanyID, VoucherType="SI")

        tot_Point = 0
        # today_date = datetime.datetime.now().date()
        today_date = str_To_Date(instance.Date)

        for i in instances:
            print(tot_Point, i.Point)
            if i.Point:
                if Loyalty_Point_Expire:
                    if i.ExpiryDate:
                        if not today_date >= i.ExpiryDate:
                            if instance.Action == "M":
                                # if is_edit:
                                tot_Point = float(tot_Point) + float(i.Point)
                                print(("1 i.ExpiryDate Kayaryyyyyyyyyyyyyy"))
                            elif instance.Action == "A":
                                tot_Point = float(tot_Point) + float(i.Point)
                                print(("2 i.ExpiryDate Kayaryyyyyyyyyyyyyy"))
                else:
                    if instance.Action == "M":
                        # if is_edit:
                        tot_Point = float(tot_Point) + float(i.Point)
                        print(
                            (tot_Point, "3 i.ExpiryDate Kayaryyyyyyyyyyyyyy", i.Point))
                    elif instance.Action == "A":
                        tot_Point = float(tot_Point) + float(i.Point)
                        print(("4 i.ExpiryDate Kayaryyyyyyyyyyyyyy"))
        if LoyaltyCustomer.objects.filter(pk=loyalty_customer.pk).exists():
            print((tot_Point, "i.ExpiryDate Kayaryyyyyyyyyyyyyy()_()_()_()_"))
            ins = LoyaltyCustomer.objects.get(pk=loyalty_customer.pk)
            ins.CurrentPoint = tot_Point
            ins.save()


def gstr1_data(CompanyID, BranchID, FromDate, ToDate, PriceRounding):
    count_sales = 0
    final_data_b2b_suppliers = []
    final_data_b2c_small = []
    final_data_b2c_large = []
    final_data_cdnr = []
    final_data_cdnur = []
    final_data_HSN_summary = []
    final_data_docs = []
    is_ok = False

    Total_invoice_value_b2b_suppliers = 0
    Total_taxable_value_b2b_suppliers = 0
    Total_cess_value_b2b_suppliers = 0
    No_of_recipients_b2b_suppliers = 0
    No_of_invoices_b2b_suppliers = 0

    unq_recipient_b2b_supply = []
    unq_invoices_b2b_supply = []

    Total_invoice_value_b2cs = 0
    Total_taxable_value_b2cs = 0
    Total_cess_value_b2cs = 0
    No_of_recipients_b2cs = 0
    No_of_invoices_b2cs = 0

    unq_recipient_b2cs = []
    unq_invoices_b2cs = []

    Total_invoice_value_b2cl = 0
    Total_taxable_value_b2cl = 0
    Total_cess_value_b2cl = 0
    No_of_recipients_b2cl = 0
    No_of_invoices_b2cl = 0

    unq_recipient_b2cl = []
    unq_invoices_b2cl = []

    Total_invoice_value_cdnr = 0
    Total_taxable_value_cdnr = 0
    Total_cess_value_cdnr = 0
    No_of_recipients_cdnr = 0
    No_of_invoices_cdnr = 0

    unq_recipient_cdnr = []
    unq_invoices_cdnr = []

    Total_invoice_value_cdnur = 0
    Total_taxable_value_cdnur = 0
    Total_cess_value_cdnur = 0
    No_of_recipients_cdnur = 0
    No_of_invoices_cdnur = 0

    unq_recipient_cdnur = []
    unq_invoices_cdnur = []

    # b2b suppliers start
    tax_types = ["GST Inter-state B2B", "GST Intra-state B2B"]
    if SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, TaxType__in=tax_types).exists():
        sales_instances = SalesMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, TaxType__in=tax_types)

        serialized_sales = GST_B2B_Serializer(sales_instances, many=True, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding,
                                                                                   "FromDate": FromDate, "ToDate": ToDate})
        orderdDict = serialized_sales.data
        jsnDatas = convertOrderdDict(orderdDict)

        unq_master_ids = []

        for i in jsnDatas:
            SalesMasterID = i['SalesMasterID']
            if not SalesMasterID in unq_master_ids:
                Customer_GST_No = i['Customer_GST_No']
                CustomerName = i['CustomerName']
                VoucherNo = i['VoucherNo']
                Date = i['Date']
                GrandTotal = i['GrandTotal']
                PlaceOfSupply = i['PlaceOfSupply']
                ApplicableTaxRate = i['ApplicableTaxRate']
                ReverseCharge = i['ReverseCharge']
                InvoiceType = i['InvoiceType']
                E_Commerce_GSTIN = i['E_Commerce_GSTIN']
                ShippingCharge = i['ShippingCharge']
                # IGSTPerc = i['IGSTPerc']
                CESS_amount = i['CESS_amount']
                if Customer_GST_No:
                    Customer_GST_No = Customer_GST_No
                else:
                    Customer_GST_No = ""
                if CustomerName:
                    CustomerName = CustomerName
                else:
                    CustomerName = ""
                if VoucherNo:
                    VoucherNo = VoucherNo
                else:
                    VoucherNo = ""
                if Date:
                    Date = Date
                else:
                    Date = ""
                if GrandTotal:
                    GrandTotal = GrandTotal
                else:
                    GrandTotal = ""
                if PlaceOfSupply:
                    PlaceOfSupply = PlaceOfSupply
                else:
                    PlaceOfSupply = ""

                if ApplicableTaxRate:
                    ApplicableTaxRate = ApplicableTaxRate
                else:
                    ApplicableTaxRate = ""

                if ReverseCharge:
                    ReverseCharge = ReverseCharge
                else:
                    ReverseCharge = ""

                if InvoiceType:
                    InvoiceType = InvoiceType
                else:
                    InvoiceType = ""

                if E_Commerce_GSTIN:
                    E_Commerce_GSTIN = E_Commerce_GSTIN
                else:
                    E_Commerce_GSTIN = ""

                if ShippingCharge:
                    ShippingCharge = ShippingCharge
                else:
                    ShippingCharge = ""

                details_instances = SalesDetails.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, SalesMasterID=SalesMasterID)
                sales_gsts = details_instances.values_list(
                    'IGSTPerc', flat=True)
                unq_sales_gsts = []
                for s in sales_gsts:
                    if not s in unq_sales_gsts:
                        i['Rate'] = s
                        taxable_value = details_instances.filter(
                            IGSTPerc=s).aggregate(Sum('TaxableAmount'))
                        taxable_value = taxable_value['TaxableAmount__sum']
                        i['taxable_value'] = taxable_value
                        GrandTotal = round(
                            float(GrandTotal), int(PriceRounding))
                        taxable_value = round(
                            float(taxable_value), int(PriceRounding))

                        final_data_b2b_suppliers.append({
                            "SalesMasterID": SalesMasterID,
                            "Customer_GST_No": Customer_GST_No,
                            "CustomerName": CustomerName,
                            "VoucherNo": VoucherNo,
                            "Date": Date,
                            "GrandTotal": (GrandTotal),
                            "PlaceOfSupply": PlaceOfSupply,
                            "ApplicableTaxRate": ApplicableTaxRate,
                            "ReverseCharge": ReverseCharge,
                            "InvoiceType": "Regular",
                            "E_Commerce_GSTIN": E_Commerce_GSTIN,
                            # "IGSTPerc" : IGSTPerc,
                            "CESS_amount": CESS_amount,
                            "Rate": s,
                            "taxable_value": (taxable_value),
                            "ShippingCharge": ShippingCharge,
                        })
                        Total_invoice_value_b2b_suppliers += float(GrandTotal)
                        Total_taxable_value_b2b_suppliers += float(
                            taxable_value)
                        Total_cess_value_b2b_suppliers += float(CESS_amount)

                        if not Customer_GST_No in unq_recipient_b2b_supply:
                            unq_recipient_b2b_supply.append(Customer_GST_No)
                        if not VoucherNo in unq_invoices_b2b_supply:
                            unq_invoices_b2b_supply.append(VoucherNo)

                        unq_sales_gsts.append(s)
                        is_ok = True
                unq_master_ids.append(SalesMasterID)

    if SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, shipping_tax_amount__gt=0, Date__gte=FromDate, Date__lte=ToDate, TaxType__in=tax_types).exists():
        sales_ins = SalesMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, shipping_tax_amount__gt=0, Date__gte=FromDate, Date__lte=ToDate, TaxType__in=tax_types)

        serialized_sales = GST_B2B_Serializer(sales_ins, many=True, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding,
                                                                             "FromDate": FromDate, "ToDate": ToDate})
        orderdDict = serialized_sales.data
        jsnDatas = convertOrderdDict(orderdDict)

        unq_master_ids = []

        for i in jsnDatas:
            SalesMasterID = i['SalesMasterID']
            if not SalesMasterID in unq_master_ids:
                Customer_GST_No = i['Customer_GST_No']
                CustomerName = i['CustomerName']
                VoucherNo = i['VoucherNo']
                Date = i['Date']
                GrandTotal = i['GrandTotal']
                PlaceOfSupply = i['PlaceOfSupply']
                ApplicableTaxRate = i['ApplicableTaxRate']
                ReverseCharge = i['ReverseCharge']
                InvoiceType = i['InvoiceType']
                E_Commerce_GSTIN = i['E_Commerce_GSTIN']
                ShippingCharge = i['ShippingCharge']
                # IGSTPerc = i['IGSTPerc']
                CESS_amount = i['CESS_amount']
                shipping_tax_amount = i['shipping_tax_amount']
                SalesTax = i['SalesTax']

                GrandTotal = round(float(GrandTotal), int(PriceRounding))
                ShippingCharge = round(
                    float(ShippingCharge), int(PriceRounding))

                final_data_b2b_suppliers.append({
                    "SalesMasterID": SalesMasterID,
                    "Customer_GST_No": Customer_GST_No,
                    "CustomerName": CustomerName,
                    "VoucherNo": VoucherNo,
                    "Date": Date,
                    "GrandTotal": (GrandTotal),
                    "PlaceOfSupply": PlaceOfSupply,
                    "ApplicableTaxRate": ApplicableTaxRate,
                    "ReverseCharge": ReverseCharge,
                    "InvoiceType": "Regular",
                    "E_Commerce_GSTIN": E_Commerce_GSTIN,
                    # "IGSTPerc" : IGSTPerc,
                    "CESS_amount": CESS_amount,
                    "Rate": SalesTax,
                    "taxable_value": (ShippingCharge),
                    "ShippingCharge": ShippingCharge,
                })
                is_ok = True

                Total_invoice_value_b2b_suppliers += float(GrandTotal)
                Total_taxable_value_b2b_suppliers += float(ShippingCharge)
                Total_cess_value_b2b_suppliers += float(CESS_amount)

                if not Customer_GST_No in unq_recipient_b2b_supply:
                    unq_recipient_b2b_supply.append(Customer_GST_No)
                if not VoucherNo in unq_invoices_b2b_supply:
                    unq_invoices_b2b_supply.append(VoucherNo)

    # B2c small start
    tax_types = ["GST Inter-state B2C", "GST Intra-state B2C"]
    rate_placeofsupplay_arr = []
    if SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, TaxType__in=tax_types).exists():
        sales_instances = SalesMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, TaxType__in=tax_types)

        serialized_sales = GST_B2B_Serializer(sales_instances, many=True, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding,
                                                                                   "FromDate": FromDate, "ToDate": ToDate})
        orderdDict = serialized_sales.data
        jsnDatas = convertOrderdDict(orderdDict)

        unq_master_ids = []
        for i in jsnDatas:
            SalesMasterID = i['SalesMasterID']
            if not SalesMasterID in unq_master_ids:
                Customer_GST_No = i['Customer_GST_No']
                CustomerName = i['CustomerName']
                VoucherNo = i['VoucherNo']
                Date = i['Date']
                GrandTotal = i['GrandTotal']
                PlaceOfSupply = i['PlaceOfSupply']
                ApplicableTaxRate = i['ApplicableTaxRate']
                ReverseCharge = i['ReverseCharge']
                InvoiceType = i['InvoiceType']
                E_Commerce_GSTIN = i['E_Commerce_GSTIN']
                Type = i['Type']
                CESS_amount = i['CESS_amount']
                ShippingCharge = i['ShippingCharge']

                details_instances = SalesDetails.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, SalesMasterID=SalesMasterID)
                sales_gsts = details_instances.values_list(
                    'IGSTPerc', flat=True)
                unq_sales_gsts = []

                for s in sales_gsts:
                    if not s in unq_sales_gsts and float(GrandTotal) < 250000:
                        i['Rate'] = s
                        taxable_value = details_instances.filter(
                            IGSTPerc=s).aggregate(Sum('TaxableAmount'))
                        taxable_value = taxable_value['TaxableAmount__sum']
                        i['taxable_value'] = taxable_value

                        GrandTotal = round(
                            float(GrandTotal), int(PriceRounding))
                        taxable_value = round(
                            float(taxable_value), int(PriceRounding))

                        if ApplicableTaxRate == "":
                            ApplicableTaxRate = 0
                        ApplicableTaxRate = round(
                            float(ApplicableTaxRate), int(PriceRounding))
                        # reate
                        s = round(float(s), int(s))

                        # Remove Same Rate and Place of Supplay Duplication and Add its TotalTaxableValue
                        # if PlaceOfSupply and s:

                        old_taxable_value = taxable_value
                        rate = abs(s)
                        if not str(PlaceOfSupply)+str(rate) in rate_placeofsupplay_arr:
                            final_data_b2c_small.append({
                                "rate_placeofsupplay": str(PlaceOfSupply)+str(rate),
                                "SalesMasterID": SalesMasterID,
                                "Customer_GST_No": Customer_GST_No,
                                "CustomerName": CustomerName,
                                "VoucherNo": VoucherNo,
                                "Date": Date,
                                "GrandTotal": (GrandTotal),
                                "PlaceOfSupply": PlaceOfSupply,
                                "ApplicableTaxRate": (ApplicableTaxRate),
                                "ReverseCharge": ReverseCharge,
                                "InvoiceType": InvoiceType,
                                "E_Commerce_GSTIN": E_Commerce_GSTIN,
                                "Type": Type,
                                "CESS_amount": CESS_amount,
                                "Rate": (s),
                                "taxable_value": (taxable_value),
                                "ShippingCharge": ShippingCharge,
                            })
                        else:
                            b2cs_data = [i for i in final_data_b2c_small if i['rate_placeofsupplay'] == str(
                                PlaceOfSupply)+str(rate)]
                            curent_taxable_value = b2cs_data[0]['taxable_value']
                            new_taxable_value = float(
                                curent_taxable_value) + float(old_taxable_value)
                            b2cs_data[0]['taxable_value'] = (new_taxable_value)
                        rate_placeofsupplay_arr.append(
                            str(PlaceOfSupply)+str(rate))

                        Total_invoice_value_b2cs += float(GrandTotal)
                        Total_taxable_value_b2cs += float(taxable_value)
                        Total_cess_value_b2cs += float(CESS_amount)

                        if not Customer_GST_No in unq_recipient_b2cs:
                            unq_recipient_b2cs.append(Customer_GST_No)
                        if not VoucherNo in unq_invoices_b2cs:
                            unq_invoices_b2cs.append(VoucherNo)
                        unq_sales_gsts.append(s)
                        is_ok = True
                unq_master_ids.append(SalesMasterID)

    if SalesReturnMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate, TaxType__in=tax_types).exists():
        sales_return_instances = SalesReturnMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate, TaxType__in=tax_types)

        serialized_sales_return = GST_CDNR_Serializer(sales_return_instances, many=True, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding,
                                                                                                  "FromDate": FromDate, "ToDate": ToDate})
        orderdDict = serialized_sales_return.data
        jsnDatas = convertOrderdDict(orderdDict)

        unq_master_ids = []
        # rate_placeofsupplay_arr = []
        for i in jsnDatas:
            SalesReturnMasterID = i['SalesReturnMasterID']
            if not SalesReturnMasterID in unq_master_ids:
                Customer_GST_No = i['Customer_GST_No']
                CustomerName = i['CustomerName']
                VoucherNo = i['VoucherNo']
                Date = i['VoucherDate']
                GrandTotal = i['GrandTotal']
                PlaceOfSupply = i['PlaceOfSupply']
                ApplicableTaxRate = i['ApplicableTaxRate']
                ReverseCharge = i['ReverseCharge']
                InvoiceType = i['InvoiceType']
                E_Commerce_GSTIN = i['E_Commerce_GSTIN']
                Type = i['Type']
                CESS_amount = i['CESS_amount']

                details_instances = SalesReturnDetails.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, SalesReturnMasterID=SalesReturnMasterID)
                sales_gsts = details_instances.values_list(
                    'IGSTPerc', flat=True)
                unq_sales_gsts = []

                for s in sales_gsts:
                    if not s in unq_sales_gsts and float(GrandTotal) < 250000:
                        i['Rate'] = s
                        taxable_value = details_instances.filter(
                            IGSTPerc=s).aggregate(Sum('TaxableAmount'))
                        taxable_value = taxable_value['TaxableAmount__sum']
                        i['taxable_value'] = taxable_value

                        GrandTotal = round(
                            float(GrandTotal), int(PriceRounding))
                        taxable_value = round(
                            float(taxable_value), int(PriceRounding))

                        if ApplicableTaxRate == "":
                            ApplicableTaxRate = 0
                        ApplicableTaxRate = round(
                            float(ApplicableTaxRate), int(PriceRounding))

                        # reate
                        s = round(float(s), int(s))

                        # Remove Same Rate and Place of Supplay Duplication and Add its TotalTaxableValue
                        # if PlaceOfSupply and s:
                        old_taxable_value = float(taxable_value) * -1
                        rate = abs(float(s) * -1)
                        print(str(PlaceOfSupply)+str(rate),
                              '----', taxable_value,)
                        if not str(PlaceOfSupply)+str(rate) in rate_placeofsupplay_arr:
                            final_data_b2c_small.append({
                                "rate_placeofsupplay": str(PlaceOfSupply)+str(rate),
                                "SalesMasterID": SalesReturnMasterID,
                                "Customer_GST_No": Customer_GST_No,
                                "CustomerName": CustomerName,
                                "VoucherNo": VoucherNo,
                                "Date": Date,
                                "GrandTotal": (float(GrandTotal) * -1),
                                "PlaceOfSupply": PlaceOfSupply,
                                "ApplicableTaxRate": (ApplicableTaxRate),
                                "ReverseCharge": ReverseCharge,
                                "InvoiceType": InvoiceType,
                                "E_Commerce_GSTIN": E_Commerce_GSTIN,
                                "Type": Type,
                                "CESS_amount": CESS_amount,
                                "Rate": (float(s) * -1),
                                "taxable_value": (float(taxable_value) * -1),
                            })

                        else:
                            b2cs_data = [i for i in final_data_b2c_small if i['rate_placeofsupplay'] == str(
                                PlaceOfSupply)+str(rate)]
                            curent_taxable_value = b2cs_data[0]['taxable_value']
                            new_taxable_value = float(
                                curent_taxable_value) + float(old_taxable_value)
                            b2cs_data[0]['taxable_value'] = (new_taxable_value)
                        rate_placeofsupplay_arr.append(
                            str(PlaceOfSupply)+str(rate))
                        # ============END==========

                        Total_invoice_value_b2cs += float(GrandTotal)
                        Total_taxable_value_b2cs += (float(taxable_value) * -1)
                        Total_cess_value_b2cs += float(CESS_amount)

                        if not Customer_GST_No in unq_recipient_b2cs:
                            unq_recipient_b2cs.append(Customer_GST_No)
                        if not VoucherNo in unq_invoices_b2cs:
                            unq_invoices_b2cs.append(VoucherNo)
                        unq_sales_gsts.append(s)
                        is_ok = True
                unq_master_ids.append(SalesReturnMasterID)

    if SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, shipping_tax_amount__gt=0, Date__gte=FromDate, Date__lte=ToDate, TaxType__in=tax_types).exists():
        sales_ins = SalesMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, shipping_tax_amount__gt=0, Date__gte=FromDate, Date__lte=ToDate, TaxType__in=tax_types)

        serialized_sales = GST_B2B_Serializer(sales_ins, many=True, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding,
                                                                             "FromDate": FromDate, "ToDate": ToDate})
        orderdDict = serialized_sales.data
        jsnDatas = convertOrderdDict(orderdDict)

        unq_master_ids = []
        # rate_placeofsupplay_arr = []
        for i in jsnDatas:
            SalesMasterID = i['SalesMasterID']
            if not SalesMasterID in unq_master_ids:
                Customer_GST_No = i['Customer_GST_No']
                CustomerName = i['CustomerName']
                VoucherNo = i['VoucherNo']
                Date = i['Date']
                GrandTotal = i['GrandTotal']
                PlaceOfSupply = i['PlaceOfSupply']
                ApplicableTaxRate = i['ApplicableTaxRate']
                ReverseCharge = i['ReverseCharge']
                InvoiceType = i['InvoiceType']
                E_Commerce_GSTIN = i['E_Commerce_GSTIN']
                ShippingCharge = i['ShippingCharge']
                # IGSTPerc = i['IGSTPerc']
                CESS_amount = i['CESS_amount']
                shipping_tax_amount = i['shipping_tax_amount']
                SalesTax = i['SalesTax']

                rate_place = str(PlaceOfSupply)+str(SalesTax)

                GrandTotal = round(float(GrandTotal), int(PriceRounding))
                ShippingCharge = round(
                    float(ShippingCharge), int(PriceRounding))

                if ApplicableTaxRate == "":
                    ApplicableTaxRate = 0
                ApplicableTaxRate = round(
                    float(ApplicableTaxRate), int(PriceRounding))

                # reate
                SalesTax = round(float(SalesTax), int(PriceRounding))

                # Remove Same Rate and Place of Supplay Duplication and Add its TotalTaxableValue
                # if PlaceOfSupply and SalesTax:
                old_taxable_value = ShippingCharge
                rate = abs(SalesTax)
                if not str(PlaceOfSupply)+str(rate) in rate_placeofsupplay_arr:
                    final_data_b2c_small.append({
                        "rate_placeofsupplay": str(PlaceOfSupply)+str(rate),
                        "SalesMasterID": SalesMasterID,
                        "Customer_GST_No": Customer_GST_No,
                        "CustomerName": CustomerName,
                        "VoucherNo": VoucherNo,
                        "Date": Date,
                        "GrandTotal": (GrandTotal),
                        "PlaceOfSupply": PlaceOfSupply,
                        "ApplicableTaxRate": (ApplicableTaxRate),
                        "ReverseCharge": ReverseCharge,
                        "InvoiceType": InvoiceType,
                        "E_Commerce_GSTIN": E_Commerce_GSTIN,
                        "Type": Type,
                        "CESS_amount": CESS_amount,
                        "Rate": (SalesTax),
                        "taxable_value": (ShippingCharge),
                        "ShippingCharge": ShippingCharge,
                        "rate_place": rate_place,
                    })
                else:
                    b2cs_data = [i for i in final_data_b2c_small if i['rate_placeofsupplay'] == str(
                        PlaceOfSupply)+str(rate)]
                    curent_taxable_value = b2cs_data[0]['taxable_value']
                    new_taxable_value = float(
                        curent_taxable_value) + float(old_taxable_value)
                    b2cs_data[0]['taxable_value'] = (new_taxable_value)
                rate_placeofsupplay_arr.append(str(PlaceOfSupply)+str(rate))

                Total_invoice_value_b2cs += float(GrandTotal)
                Total_taxable_value_b2cs += float(ShippingCharge)
                Total_cess_value_b2cs += float(CESS_amount)

                if not Customer_GST_No in unq_recipient_b2cs:
                    unq_recipient_b2cs.append(Customer_GST_No)
                if not VoucherNo in unq_invoices_b2cs:
                    unq_invoices_b2cs.append(VoucherNo)
                is_ok = True
        # =======================================END B2cs==================

    # B2c large start
    tax_types = ["GST Inter-state B2C"]
    if SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, TaxType__in=tax_types).exists():
        sales_instances = SalesMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, TaxType__in=tax_types)

        serialized_sales = GST_B2B_Serializer(sales_instances, many=True, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding,
                                                                                   "FromDate": FromDate, "ToDate": ToDate})
        orderdDict = serialized_sales.data
        jsnDatas = convertOrderdDict(orderdDict)

        unq_master_ids = []

        for i in jsnDatas:
            SalesMasterID = i['SalesMasterID']
            if not SalesMasterID in unq_master_ids:
                Customer_GST_No = i['Customer_GST_No']
                CustomerName = i['CustomerName']
                VoucherNo = i['VoucherNo']
                Date = i['Date']
                GrandTotal = i['GrandTotal']
                PlaceOfSupply = i['PlaceOfSupply']
                ApplicableTaxRate = i['ApplicableTaxRate']
                ReverseCharge = i['ReverseCharge']
                InvoiceType = i['InvoiceType']
                E_Commerce_GSTIN = i['E_Commerce_GSTIN']
                Type = i['Type']
                CESS_amount = i['CESS_amount']

                details_instances = SalesDetails.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, SalesMasterID=SalesMasterID)
                sales_gsts = details_instances.values_list(
                    'IGSTPerc', flat=True)
                unq_sales_gsts = []
                for s in sales_gsts:
                    if not s in unq_sales_gsts and float(GrandTotal) >= 250000:
                        i['Rate'] = s
                        taxable_value = details_instances.filter(
                            IGSTPerc=s).aggregate(Sum('TaxableAmount'))
                        taxable_value = taxable_value['TaxableAmount__sum']
                        i['taxable_value'] = taxable_value

                        # ======
                        GrandTotal1 = round(
                            float(GrandTotal), int(PriceRounding))
                        taxable_value1 = round(
                            float(taxable_value), int(PriceRounding))

                        final_data_b2c_large.append({
                            "SalesMasterID": SalesMasterID,
                            "Customer_GST_No": Customer_GST_No,
                            "CustomerName": CustomerName,
                            "VoucherNo": VoucherNo,
                            "Date": Date,
                            "GrandTotal": (GrandTotal1),
                            "PlaceOfSupply": PlaceOfSupply,
                            "ApplicableTaxRate": ApplicableTaxRate,
                            "ReverseCharge": ReverseCharge,
                            "InvoiceType": InvoiceType,
                            "E_Commerce_GSTIN": E_Commerce_GSTIN,
                            "Type": Type,
                            "CESS_amount": CESS_amount,
                            "Rate": s,
                            "taxable_value": (taxable_value1),
                        })

                        Total_invoice_value_b2cl += float(GrandTotal)
                        Total_taxable_value_b2cl += float(taxable_value)
                        Total_cess_value_b2cl += float(CESS_amount)

                        if not Customer_GST_No in unq_recipient_b2cl:
                            unq_recipient_b2cl.append(Customer_GST_No)
                        if not VoucherNo in unq_invoices_b2cl:
                            unq_invoices_b2cl.append(VoucherNo)

                        unq_sales_gsts.append(s)
                        is_ok = True
                unq_master_ids.append(SalesMasterID)

    if SalesReturnMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate, TaxType__in=tax_types).exists():
        sales_return_instances = SalesReturnMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate, TaxType__in=tax_types)

        serialized_sales_return = GST_CDNR_Serializer(sales_return_instances, many=True, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding,
                                                                                                  "FromDate": FromDate, "ToDate": ToDate})
        orderdDict = serialized_sales_return.data
        jsnDatas = convertOrderdDict(orderdDict)

        unq_master_ids = []

        for i in jsnDatas:
            SalesReturnMasterID = i['SalesReturnMasterID']
            if not SalesReturnMasterID in unq_master_ids:
                Customer_GST_No = i['Customer_GST_No']
                CustomerName = i['CustomerName']
                VoucherNo = i['VoucherNo']
                Date = i['VoucherDate']
                GrandTotal = i['GrandTotal']
                PlaceOfSupply = i['PlaceOfSupply']
                ApplicableTaxRate = i['ApplicableTaxRate']
                ReverseCharge = i['ReverseCharge']
                InvoiceType = i['InvoiceType']
                E_Commerce_GSTIN = i['E_Commerce_GSTIN']
                Type = i['Type']
                CESS_amount = i['CESS_amount']

                details_instances = SalesReturnDetails.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, SalesReturnMasterID=SalesReturnMasterID)
                sales_gsts = details_instances.values_list(
                    'IGSTPerc', flat=True)
                unq_sales_gsts = []
                for s in sales_gsts:
                    if not s in unq_sales_gsts and float(GrandTotal) >= 250000:
                        i['Rate'] = s
                        taxable_value = details_instances.filter(
                            IGSTPerc=s).aggregate(Sum('TaxableAmount'))
                        taxable_value = taxable_value['TaxableAmount__sum']
                        i['taxable_value'] = taxable_value

                        # ======
                        GrandTotal1 = round(
                            float(GrandTotal), int(PriceRounding))
                        taxable_value1 = round(
                            float(taxable_value), int(PriceRounding))

                        final_data_b2c_large.append({
                            "SalesMasterID": SalesReturnMasterID,
                            "Customer_GST_No": Customer_GST_No,
                            "CustomerName": CustomerName,
                            "VoucherNo": VoucherNo,
                            "Date": Date,
                            "GrandTotal": (float(GrandTotal1) * -1),
                            "ApplicableTaxRate": ApplicableTaxRate,
                            "PlaceOfSupply": PlaceOfSupply,
                            "ReverseCharge": ReverseCharge,
                            "InvoiceType": InvoiceType,
                            "E_Commerce_GSTIN": E_Commerce_GSTIN,
                            "Type": Type,
                            "Rate": float(s) * -1,
                            "taxable_value": (float(taxable_value1) * -1),
                            "CESS_amount": CESS_amount,
                        })

                        Total_invoice_value_b2cl += float(GrandTotal)
                        Total_taxable_value_b2cl += float(taxable_value) * -1
                        Total_cess_value_b2cl += float(CESS_amount)

                        if not Customer_GST_No in unq_recipient_b2cl:
                            unq_recipient_b2cl.append(Customer_GST_No)
                        if not VoucherNo in unq_invoices_b2cl:
                            unq_invoices_b2cl.append(VoucherNo)
                        unq_sales_gsts.append(s)
                        is_ok = True
                unq_master_ids.append(SalesReturnMasterID)

    # CDNR report start
    tax_types = ["GST Inter-state B2B",
                 "GST Intra-state B2B Unregistered", "GST Intra-state B2B"]
    if SalesReturnMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate, TaxType__in=tax_types).exists():
        sales_return_instances = SalesReturnMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate, TaxType__in=tax_types)

        serialized_sales_return = GST_CDNR_Serializer(sales_return_instances, many=True, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding,
                                                                                                  "FromDate": FromDate, "ToDate": ToDate})
        orderdDict = serialized_sales_return.data
        jsnDatas = convertOrderdDict(orderdDict)

        unq_master_ids = []

        for i in jsnDatas:
            SalesReturnMasterID = i['SalesReturnMasterID']
            if not SalesReturnMasterID in unq_master_ids:
                Customer_GST_No = i['Customer_GST_No']
                CustomerName = i['CustomerName']
                VoucherNo = i['VoucherNo']
                Date = i['VoucherDate']
                GrandTotal = i['GrandTotal']
                PlaceOfSupply = i['PlaceOfSupply']
                ApplicableTaxRate = i['ApplicableTaxRate']
                ReverseCharge = i['ReverseCharge']
                InvoiceType = i['InvoiceType']
                E_Commerce_GSTIN = i['E_Commerce_GSTIN']
                Type = i['Type']
                CESS_amount = i['CESS_amount']
                DocumentType = i['DocumentType']
                RefferenceBillNo = i['RefferenceBillNo']
                RefferenceBillDate = i['RefferenceBillDate']

                details_instances = SalesReturnDetails.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, SalesReturnMasterID=SalesReturnMasterID)
                sales_gsts = details_instances.values_list(
                    'IGSTPerc', flat=True)
                unq_sales_gsts = []
                for s in sales_gsts:
                    if not s in unq_sales_gsts:
                        i['Rate'] = s
                        taxable_value = details_instances.filter(
                            IGSTPerc=s).aggregate(Sum('TaxableAmount'))
                        taxable_value = taxable_value['TaxableAmount__sum']
                        i['taxable_value'] = taxable_value

                        if Customer_GST_No:
                            Customer_GST_No = Customer_GST_No
                        else:
                            Customer_GST_No = ""

                        if CustomerName:
                            CustomerName = CustomerName
                        else:
                            CustomerName = ""

                        if VoucherNo:
                            VoucherNo = VoucherNo
                        else:
                            VoucherNo = ""

                        if Date:
                            Date = Date
                        else:
                            Date = ""

                        if GrandTotal:
                            GrandTotal = GrandTotal
                        else:
                            GrandTotal = 0

                        if PlaceOfSupply:
                            PlaceOfSupply = PlaceOfSupply
                        else:
                            PlaceOfSupply = ""

                        if ApplicableTaxRate:
                            ApplicableTaxRate = ApplicableTaxRate
                        else:
                            ApplicableTaxRate = ""

                        if ReverseCharge:
                            ReverseCharge = ReverseCharge
                        else:
                            ReverseCharge = ""

                        if InvoiceType:
                            InvoiceType = InvoiceType
                        else:
                            InvoiceType = ""

                        if E_Commerce_GSTIN:
                            E_Commerce_GSTIN = E_Commerce_GSTIN
                        else:
                            E_Commerce_GSTIN = ""

                        if Type:
                            Type = Type
                        else:
                            Type = ""

                        if CESS_amount:
                            CESS_amount = CESS_amount
                        else:
                            CESS_amount = 0

                        if s:
                            s = s
                        else:
                            s = ""

                        if taxable_value:
                            taxable_value = taxable_value
                        else:
                            taxable_value = 0

                        if DocumentType:
                            DocumentType = DocumentType
                        else:
                            DocumentType = ""

                        if RefferenceBillNo:
                            RefferenceBillNo = RefferenceBillNo
                        else:
                            RefferenceBillNo = ""

                        if RefferenceBillDate:
                            RefferenceBillDate = RefferenceBillDate
                        else:
                            RefferenceBillDate = ""

                        # ======
                        GrandTotal1 = round(
                            float(GrandTotal), int(PriceRounding))
                        taxable_value1 = round(
                            float(taxable_value), int(PriceRounding))
                        final_data_cdnr.append({
                            "SalesReturnMasterID": SalesReturnMasterID,
                            "Customer_GST_No": Customer_GST_No,
                            "CustomerName": CustomerName,
                            "VoucherNo": VoucherNo,
                            "Date": Date,
                            "GrandTotal": (GrandTotal1),
                            "PlaceOfSupply": PlaceOfSupply,
                            "ApplicableTaxRate": ApplicableTaxRate,
                            "ReverseCharge": ReverseCharge,
                            "InvoiceType": InvoiceType,
                            "E_Commerce_GSTIN": E_Commerce_GSTIN,
                            "Type": Type,
                            "CESS_amount": CESS_amount,
                            "Rate": s,
                            "taxable_value": (taxable_value1),
                            "DocumentType": DocumentType,
                            "RefferenceBillNo": RefferenceBillNo,
                            "RefferenceBillDate": RefferenceBillDate,
                        })

                        Total_invoice_value_cdnr += float(GrandTotal)
                        Total_taxable_value_cdnr += float(taxable_value)
                        Total_cess_value_cdnr += float(CESS_amount)

                        if not Customer_GST_No in unq_recipient_cdnr:
                            unq_recipient_cdnr.append(Customer_GST_No)
                        if not VoucherNo in unq_invoices_cdnr:
                            unq_invoices_cdnr.append(VoucherNo)
                        unq_sales_gsts.append(s)
                        is_ok = True
                unq_master_ids.append(SalesReturnMasterID)

    # CDNUR report start
    tax_types = ["GST Intra-state B2C", "GST Inter-state B2C"]
    # if SalesReturnMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate, TaxType__in=tax_types).exists():
    #     sales_return_instances = SalesReturnMaster.objects.filter(
    #         CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate, TaxType__in=tax_types)

    #     serialized_sales_return = GST_CDNR_Serializer(sales_return_instances, many=True, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding,
    #                                                                                               "FromDate": FromDate, "ToDate": ToDate})
    #     orderdDict = serialized_sales_return.data
    #     jsnDatas = convertOrderdDict(orderdDict)

    #     unq_master_ids = []

    #     for i in jsnDatas:
    #         SalesReturnMasterID = i['SalesReturnMasterID']
    #         if not SalesReturnMasterID in unq_master_ids:
    #             Customer_GST_No = i['Customer_GST_No']
    #             CustomerName = i['CustomerName']
    #             VoucherNo = i['VoucherNo']
    #             Date = i['VoucherDate']
    #             GrandTotal = i['GrandTotal']
    #             PlaceOfSupply = i['PlaceOfSupply']
    #             ApplicableTaxRate = i['ApplicableTaxRate']
    #             ReverseCharge = i['ReverseCharge']
    #             InvoiceType = i['InvoiceType']
    #             E_Commerce_GSTIN = i['E_Commerce_GSTIN']
    #             Type = i['Type']
    #             CESS_amount = i['CESS_amount']
    #             DocumentType = i['DocumentType']
    #             UR_Type = i['UR_Type']
    #             RefferenceBillNo = i['RefferenceBillNo']
    #             RefferenceBillDate = i['RefferenceBillDate']

    #             details_instances = SalesReturnDetails.objects.filter(
    #                 CompanyID=CompanyID, BranchID=BranchID, SalesReturnMasterID=SalesReturnMasterID)
    #             sales_gsts = details_instances.values_list(
    #                 'IGSTPerc', flat=True)
    #             unq_sales_gsts = []
    #             for s in sales_gsts:
    #                 if not s in unq_sales_gsts and float(GrandTotal) < 250000:
    #                     i['Rate'] = s
    #                     taxable_value = details_instances.filter(
    #                         IGSTPerc=s).aggregate(Sum('TaxableAmount'))
    #                     taxable_value = taxable_value['TaxableAmount__sum']
    #                     i['taxable_value'] = taxable_value

    #                     if Customer_GST_No:
    #                         Customer_GST_No = Customer_GST_No
    #                     else:
    #                         Customer_GST_No = ""

    #                     if CustomerName:
    #                         CustomerName = CustomerName
    #                     else:
    #                         CustomerName = ""

    #                     if VoucherNo:
    #                         VoucherNo = VoucherNo
    #                     else:
    #                         VoucherNo = ""

    #                     if Date:
    #                         Date = Date
    #                     else:
    #                         Date = ""

    #                     if GrandTotal:
    #                         GrandTotal = GrandTotal
    #                     else:
    #                         GrandTotal = ""

    #                     if PlaceOfSupply:
    #                         PlaceOfSupply = PlaceOfSupply
    #                     else:
    #                         PlaceOfSupply = ""

    #                     if ApplicableTaxRate:
    #                         ApplicableTaxRate = ApplicableTaxRate
    #                     else:
    #                         ApplicableTaxRate = ""

    #                     if ReverseCharge:
    #                         ReverseCharge = ReverseCharge
    #                     else:
    #                         ReverseCharge = ""

    #                     if InvoiceType:
    #                         InvoiceType = InvoiceType
    #                     else:
    #                         InvoiceType = ""

    #                     if E_Commerce_GSTIN:
    #                         E_Commerce_GSTIN = E_Commerce_GSTIN
    #                     else:
    #                         E_Commerce_GSTIN = ""

    #                     if Type:
    #                         Type = Type
    #                     else:
    #                         Type = ""

    #                     if CESS_amount:
    #                         CESS_amount = CESS_amount
    #                     else:
    #                         CESS_amount = ""

    #                     if s:
    #                         s = s
    #                     else:
    #                         s = ""

    #                     if taxable_value:
    #                         taxable_value = taxable_value
    #                     else:
    #                         taxable_value = ""

    #                     if DocumentType:
    #                         DocumentType = DocumentType
    #                     else:
    #                         DocumentType = ""

    #                     if UR_Type:
    #                         UR_Type = UR_Type
    #                     else:
    #                         UR_Type = ""

    #                     if RefferenceBillNo:
    #                         RefferenceBillNo = RefferenceBillNo
    #                     else:
    #                         RefferenceBillNo = ""

    #                     if RefferenceBillDate:
    #                         RefferenceBillDate = RefferenceBillDate
    #                     else:
    #                         RefferenceBillDate = ""

    #                     # ======
    #                     GrandTotal1 = round(
    #                         float(GrandTotal), int(PriceRounding))
    #                     taxable_value1 = round(
    #                         float(taxable_value), int(PriceRounding))

    #                     final_data_cdnur.append({
    #                         "SalesReturnMasterID": SalesReturnMasterID,
    #                         "Customer_GST_No": Customer_GST_No,
    #                         "CustomerName": CustomerName,
    #                         "VoucherNo": VoucherNo,
    #                         "Date": Date,
    #                         "GrandTotal": (GrandTotal1),
    #                         "PlaceOfSupply": PlaceOfSupply,
    #                         "ApplicableTaxRate": ApplicableTaxRate,
    #                         "ReverseCharge": ReverseCharge,
    #                         "InvoiceType": InvoiceType,
    #                         "E_Commerce_GSTIN": E_Commerce_GSTIN,
    #                         "Type": Type,
    #                         "CESS_amount": CESS_amount,
    #                         "Rate": s,
    #                         "taxable_value": (taxable_value1),
    #                         "DocumentType": DocumentType,
    #                         "UR_Type": UR_Type,
    #                         "RefferenceBillNo": RefferenceBillNo,
    #                         "RefferenceBillDate": RefferenceBillDate,
    #                     })

    #                     Total_invoice_value_cdnur += float(GrandTotal)
    #                     Total_taxable_value_cdnur += float(taxable_value)
    #                     if CESS_amount == "":
    #                         CESS_amount = 0
    #                     Total_cess_value_cdnur += float(CESS_amount)

    #                     if not Customer_GST_No in unq_recipient_cdnur:
    #                         unq_recipient_cdnur.append(Customer_GST_No)
    #                     if not VoucherNo in unq_invoices_cdnur:
    #                         unq_invoices_cdnur.append(VoucherNo)
    #                     unq_sales_gsts.append(s)
    #                     is_ok = True
    #             unq_master_ids.append(SalesReturnMasterID)

    # HSN summary start
    HSN_values = Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exclude(
        HSNCode="null").values_list('HSNCode', flat=True)
    HSN_values = set(HSN_values)
    no_of_hsn = 0
    total_value_hsn = 0
    total_taxable_value_hsn = 0
    total_igst_tax_hsn = 0
    total_cgst_tax_hsn = 0
    total_sgst_tax_hsn = 0
    total_cess_hsn = 0
    unq_hsn = []

    price = []
    for h in HSN_values:
        sales_instances = SalesMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)
        master_ids = sales_instances.values_list('SalesMasterID', flat=True)
        product_ins_ids = Product.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, HSNCode=h).values_list('ProductID', flat=True)

        if SalesDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID__in=product_ins_ids, SalesMasterID__in=master_ids).exists():
            salesDetails_ins = SalesDetails.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID__in=product_ins_ids, SalesMasterID__in=master_ids)
            Rate = salesDetails_ins.first().IGSTPerc
            # priceList_ids = salesDetails_ins.values_list('PriceListID', flat=True)
            # price_list_ins = PriceList.objects.filter(CompanyID=CompanyID,BranchID=BranchID,PriceListID__in=priceList_ids)
            uqc_ins = UQCTable.objects.all()

            for uq in uqc_ins:
                if Unit.objects.filter(CompanyID=CompanyID, BranchID=BranchID, UQC=uq).exists():
                    unit_ins = Unit.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, UQC=uq)
                    unit_ids = unit_ins.values_list('UnitID', flat=True)
                    price_list_ins = PriceList.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, UnitID__in=unit_ids)
                    priceList_ids = price_list_ins.values_list(
                        'PriceListID', flat=True)
                    # priceList_ids = list(priceList_ids)
                    salesDetails_instances = salesDetails_ins.filter(
                        PriceListID__in=priceList_ids)

                    TotalQuantity = salesDetails_instances.aggregate(
                        Sum('Qty'))
                    TotalQuantity = TotalQuantity['Qty__sum']
                    TotalNetAmount = salesDetails_instances.aggregate(
                        Sum('NetAmount'))
                    TotalNetAmount = TotalNetAmount['NetAmount__sum']
                    TotalTaxableValue = salesDetails_instances.aggregate(
                        Sum('TaxableAmount'))
                    TotalTaxableValue = TotalTaxableValue['TaxableAmount__sum']
                    TotalIGSTAmount = salesDetails_instances.aggregate(
                        Sum('IGSTAmount'))
                    TotalIGSTAmount = TotalIGSTAmount['IGSTAmount__sum']
                    TotalCGSTAmount = salesDetails_instances.aggregate(
                        Sum('CGSTAmount'))
                    TotalCGSTAmount = TotalCGSTAmount['CGSTAmount__sum']
                    TotalSGSTAmount = salesDetails_instances.aggregate(
                        Sum('SGSTAmount'))
                    TotalSGSTAmount = TotalSGSTAmount['SGSTAmount__sum']

                    if TotalQuantity:
                        TotalQuantity = TotalQuantity
                    else:
                        TotalQuantity = 0
                    if TotalNetAmount:
                        TotalNetAmount = TotalNetAmount
                    else:
                        TotalNetAmount = 0
                    if TotalTaxableValue:
                        TotalTaxableValue = TotalTaxableValue
                    else:
                        TotalTaxableValue = 0
                    if TotalIGSTAmount:
                        TotalIGSTAmount = TotalIGSTAmount
                    else:
                        TotalIGSTAmount = 0
                    if TotalCGSTAmount:
                        TotalCGSTAmount = TotalCGSTAmount
                    else:
                        TotalCGSTAmount = 0
                    if TotalSGSTAmount:
                        TotalSGSTAmount = TotalSGSTAmount
                    else:
                        TotalSGSTAmount = 0

                    if not h:
                        h = ""
                    if not TotalQuantity == 0 and not TotalNetAmount == 0:
                        # ======
                        TotalNetAmount1 = round(
                            float(TotalNetAmount), int(PriceRounding))
                        TotalTaxableValue1 = round(
                            float(TotalTaxableValue), int(PriceRounding))
                        TotalIGSTAmount1 = round(
                            float(TotalIGSTAmount), int(PriceRounding))
                        TotalCGSTAmount1 = round(
                            float(TotalCGSTAmount), int(PriceRounding))
                        TotalSGSTAmount1 = round(
                            float(TotalSGSTAmount), int(PriceRounding))

                        final_data_HSN_summary.append({
                            "rate_saletax": "",
                            "HSN_Code": h,
                            "Description": "",
                            "UQC": uq.UQC_Name,
                            "TotalQuantity": TotalQuantity,
                            "TotalNetAmount": (TotalNetAmount1),
                            "TotalTaxableValue": (TotalTaxableValue1),
                            "TotalIGSTAmount": (TotalIGSTAmount1),
                            "TotalCGSTAmount": (TotalCGSTAmount1),
                            "TotalSGSTAmount": (TotalSGSTAmount1),
                            "CessAmount": 0,
                            "Rate": Rate,
                        })

                        if not h in unq_hsn:
                            unq_hsn.append(h)
                        total_value_hsn += float(TotalNetAmount)
                        total_taxable_value_hsn += float(TotalTaxableValue)
                        total_igst_tax_hsn += float(TotalIGSTAmount)
                        total_cgst_tax_hsn += float(TotalCGSTAmount)
                        total_sgst_tax_hsn += float(TotalSGSTAmount)
                        is_ok = True

        if SalesReturnDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID__in=product_ins_ids).exists():
            sales_instances = SalesReturnMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate,)
            master_ids = sales_instances.values_list(
                'SalesReturnMasterID', flat=True)
            salesReturnDetails_ins = SalesReturnDetails.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID__in=product_ins_ids, SalesReturnMasterID__in=master_ids)
            Rate = ""
            if salesReturnDetails_ins:
                Rate = salesReturnDetails_ins.first().IGSTPerc
            uqc_ins = UQCTable.objects.all()

            for uq in uqc_ins:
                if Unit.objects.filter(CompanyID=CompanyID, BranchID=BranchID, UQC=uq).exists():
                    unit_ins = Unit.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, UQC=uq)
                    unit_ids = unit_ins.values_list('UnitID', flat=True)
                    price_list_ins = PriceList.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, UnitID__in=unit_ids)
                    priceList_ids = price_list_ins.values_list(
                        'PriceListID', flat=True)
                    # priceList_ids = list(priceList_ids)
                    salesReturnDetails_instances = salesReturnDetails_ins.filter(
                        PriceListID__in=priceList_ids)

                    TotalQuantity = salesReturnDetails_instances.aggregate(
                        Sum('Qty'))
                    TotalQuantity = TotalQuantity['Qty__sum']
                    TotalNetAmount = salesReturnDetails_instances.aggregate(
                        Sum('NetAmount'))
                    TotalNetAmount = TotalNetAmount['NetAmount__sum']
                    TotalTaxableValue = salesReturnDetails_instances.aggregate(
                        Sum('TaxableAmount'))
                    TotalTaxableValue = TotalTaxableValue['TaxableAmount__sum']
                    TotalIGSTAmount = salesReturnDetails_instances.aggregate(
                        Sum('IGSTAmount'))
                    TotalIGSTAmount = TotalIGSTAmount['IGSTAmount__sum']
                    TotalCGSTAmount = salesReturnDetails_instances.aggregate(
                        Sum('CGSTAmount'))
                    TotalCGSTAmount = TotalCGSTAmount['CGSTAmount__sum']
                    TotalSGSTAmount = salesReturnDetails_instances.aggregate(
                        Sum('SGSTAmount'))
                    TotalSGSTAmount = TotalSGSTAmount['SGSTAmount__sum']

                    if TotalQuantity:
                        TotalQuantity = TotalQuantity
                    else:
                        TotalQuantity = 0
                    if TotalNetAmount:
                        TotalNetAmount = TotalNetAmount
                    else:
                        TotalNetAmount = 0
                    if TotalTaxableValue:
                        TotalTaxableValue = TotalTaxableValue
                    else:
                        TotalTaxableValue = 0
                    if TotalIGSTAmount:
                        TotalIGSTAmount = TotalIGSTAmount
                    else:
                        TotalIGSTAmount = 0
                    if TotalCGSTAmount:
                        TotalCGSTAmount = TotalCGSTAmount
                    else:
                        TotalCGSTAmount = 0
                    if TotalSGSTAmount:
                        TotalSGSTAmount = TotalSGSTAmount
                    else:
                        TotalSGSTAmount = 0

                    if not h:
                        h = ""
                    if not TotalQuantity == 0 and not TotalNetAmount == 0:
                        # ======
                        TotalNetAmount1 = round(
                            float(TotalNetAmount), int(PriceRounding))
                        TotalTaxableValue1 = round(
                            float(TotalTaxableValue), int(PriceRounding))
                        TotalIGSTAmount1 = round(
                            float(TotalIGSTAmount), int(PriceRounding))
                        TotalCGSTAmount1 = round(
                            float(TotalCGSTAmount), int(PriceRounding))
                        TotalSGSTAmount1 = round(
                            float(TotalSGSTAmount), int(PriceRounding))
                        final_data_HSN_summary.append({
                            "rate_saletax": "",
                            "HSN_Code": h,
                            "Description": "",
                            "UQC": uq.UQC_Name,
                            "TotalQuantity": float(TotalQuantity) * -1,
                            "TotalNetAmount": (float(TotalNetAmount1) * -1),
                            "TotalTaxableValue": (float(TotalTaxableValue1) * -1),
                            "TotalIGSTAmount": (float(TotalIGSTAmount1) * -1),
                            "TotalCGSTAmount": (float(TotalCGSTAmount1) * -1),
                            "TotalSGSTAmount": (float(TotalSGSTAmount1) * -1),
                            "Rate": Rate,
                            "CessAmount": 0,
                        })

                        if not h in unq_hsn:
                            unq_hsn.append(h)
                        total_value_hsn += float(TotalNetAmount) * -1
                        total_taxable_value_hsn += float(
                            TotalTaxableValue) * -1
                        total_igst_tax_hsn += float(TotalIGSTAmount) * -1
                        total_cgst_tax_hsn += float(TotalCGSTAmount) * -1
                        total_sgst_tax_hsn += float(TotalSGSTAmount) * -1

                        is_ok = True

    if SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, shipping_tax_amount__gt=0, Date__gte=FromDate, Date__lte=ToDate,).exists():
        sales_ins = SalesMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, shipping_tax_amount__gt=0, Date__gte=FromDate, Date__lte=ToDate,)
        rate_saletax = []
        for s in sales_ins:
            HSN_Code = s.SAC

            if not HSN_Code:
                HSN_Code = ""
            total_value = float(s.shipping_tax_amount) + \
                float(s.ShippingCharge)
            IGSTAmount = 0
            CGSTAmount = 0
            SGSTAmount = 0
            shipping_tax_amount = s.shipping_tax_amount
            if float(s.IGSTAmount) > 0:
                IGSTAmount = shipping_tax_amount
            if float(s.CGSTAmount) > 0:
                CGSTAmount = float(shipping_tax_amount) / 2
            if float(s.SGSTAmount) > 0:
                SGSTAmount = float(shipping_tax_amount) / 2

            total_value1 = round(float(total_value), int(PriceRounding))
            ShippingCharge1 = round(
                float(s.ShippingCharge), int(PriceRounding))
            IGSTAmount1 = round(float(IGSTAmount), int(PriceRounding))
            CGSTAmount1 = round(float(CGSTAmount), int(PriceRounding))
            SGSTAmount1 = round(float(SGSTAmount), int(PriceRounding))
            # ====Rate=====
            SalesTax = math.trunc(s.SalesTax)
            if HSN_Code and SalesTax:
                Rate = s.ShippingCharge+s.SGSTAmount+s.CGSTAmount+s.IGSTAmount
                if not str(HSN_Code)+str(SalesTax) in rate_saletax:

                    final_data_HSN_summary.append({
                        "rate_saletax": str(HSN_Code)+str(SalesTax),
                        "HSN_Code": HSN_Code,
                        "Description": "",
                        # "UQC" : ["Nos","Piece"],
                        "UQC": "OTH",
                        "TotalQuantity": 1,
                        "TotalNetAmount": (total_value1),
                        "TotalTaxableValue": (ShippingCharge1),
                        "TotalIGSTAmount": (IGSTAmount1),
                        "TotalCGSTAmount": (CGSTAmount1),
                        "TotalSGSTAmount": (SGSTAmount1),
                        "Rate": Rate,
                        "CessAmount": 0,
                    })
                else:
                    # final_data_HSN_summary
                    superplayers = [user for user in final_data_HSN_summary if user['rate_saletax'] == str(
                        HSN_Code)+str(SalesTax)]
                    rate = superplayers[0]['Rate']
                    newrate = float(rate) + float(Rate)
                    superplayers[0]['Rate'] = (newrate)

                rate_saletax.append(str(HSN_Code)+str(SalesTax))
            # ====Rate End=====

            if not HSN_Code in unq_hsn:
                unq_hsn.append(HSN_Code)
            total_value_hsn += float(total_value)
            total_taxable_value_hsn += float(s.ShippingCharge)
            total_igst_tax_hsn += float(IGSTAmount)
            total_cgst_tax_hsn += float(CGSTAmount)
            total_sgst_tax_hsn += float(SGSTAmount)

    # docs(Invoices for outward supply) start heare
    total_Total_num = 0
    total_Total_cancelled = 0
    if SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
        sales_instances = SalesMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).order_by('SalesMasterID')
        cancelled_sales_instances = SalesMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, Status="Cancelled")
        first_instance = sales_instances.first()
        last_instance = sales_instances.last()
        cancelled_count = len(cancelled_sales_instances)
        total_count = len(sales_instances)
        print(first_instance.VoucherNo, last_instance.VoucherNo,
              cancelled_count, total_count, "SalesMasterID")
        final_data_docs.append({
            "Nature_of_document": "Invoices for outward supply",
            "Sr_no_from": first_instance.VoucherNo,
            "Sr_no_to": last_instance.VoucherNo,
            "Total_num": total_count,
            "Total_cancelled": cancelled_count,
        })
        total_Total_cancelled += cancelled_count
        total_Total_num += total_count

    # Credit Note
    if SalesReturnMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate).exists():
        sales_instances = SalesReturnMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate).order_by('SalesReturnMasterID')
        first_instance = sales_instances.first()
        last_instance = sales_instances.last()
        total_count = len(sales_instances)
        final_data_docs.append({
            "Nature_of_document": "Credit Note",
            "Sr_no_from": first_instance.VoucherNo,
            "Sr_no_to": last_instance.VoucherNo,
            "Total_num": total_count,
            "Total_cancelled": "",
        })
        total_Total_num += total_count
    # docs(Invoices for outward supply) end heare

    if is_ok == True:
        No_of_recipients_b2b_suppliers = len(unq_recipient_b2b_supply)
        No_of_invoices_b2b_suppliers = len(unq_invoices_b2cs)

        No_of_recipients_b2cs = len(unq_recipient_b2cs)
        No_of_invoices_b2cs = len(unq_invoices_b2cs)

        No_of_recipients_b2cl = len(unq_recipient_b2cl)
        No_of_invoices_b2cl = len(unq_invoices_b2cl)

        No_of_recipients_cdnr = len(unq_recipient_cdnr)
        No_of_invoices_cdnr = len(unq_invoices_cdnr)

        No_of_recipients_cdnur = len(unq_recipient_cdnur)
        No_of_invoices_cdnur = len(unq_invoices_cdnur)

        final_data_b2b_suppliers = sorted(
            final_data_b2b_suppliers, key=itemgetter('Date'))
        if len(final_data_b2b_suppliers) > 0:
            final_data_b2b_suppliers.append({
                "Total_invoice_value_b2b_suppliers": (Total_invoice_value_b2b_suppliers),
                "Total_taxable_value_b2b_suppliers": (Total_taxable_value_b2b_suppliers),
                "Total_cess_value_b2b_suppliers": (Total_cess_value_b2b_suppliers),
                "No_of_recipients_b2b_suppliers": No_of_recipients_b2b_suppliers,
                "No_of_invoices_b2b_suppliers": No_of_invoices_b2b_suppliers,
            })
        final_data_b2c_small = sorted(
            final_data_b2c_small, key=itemgetter('Date'))
        if len(final_data_b2c_small) > 0:
            final_data_b2c_small.append({
                "Total_invoice_value_b2cs": (Total_invoice_value_b2cs),
                "Total_taxable_value_b2cs": (Total_taxable_value_b2cs),
                "Total_cess_value_b2cs": (Total_cess_value_b2cs),
                "No_of_recipients_b2cs": No_of_recipients_b2cs,
                "No_of_invoices_b2cs": No_of_invoices_b2cs,
            })
        final_data_b2c_large = sorted(
            final_data_b2c_large, key=itemgetter('Date'))
        if len(final_data_b2c_large) > 0:
            final_data_b2c_large.append({
                "Total_invoice_value_b2cl": (Total_invoice_value_b2cl),
                "Total_taxable_value_b2cl": (Total_taxable_value_b2cl),
                "Total_cess_value_b2cl": (Total_cess_value_b2cl),
                "No_of_recipients_b2cl": No_of_recipients_b2cl,
                "No_of_invoices_b2cl": No_of_invoices_b2cl,
            })
        final_data_cdnr = sorted(final_data_cdnr, key=itemgetter('Date'))
        if len(final_data_cdnr) > 0:
            final_data_cdnr.append({
                "Total_invoice_value_cdnr": (Total_invoice_value_cdnr),
                "Total_taxable_value_cdnr": (Total_taxable_value_cdnr),
                "Total_cess_value_cdnr": (Total_cess_value_cdnr),
                "No_of_recipients_cdnr": No_of_recipients_cdnr,
                "No_of_invoices_cdnr": No_of_invoices_cdnr,
            })
        final_data_cdnur = sorted(final_data_cdnur, key=itemgetter('Date'))
        if len(final_data_cdnur) > 0:
            final_data_cdnur.append({
                "Total_invoice_value_cdnur": (Total_invoice_value_cdnur),
                "Total_taxable_value_cdnur": (Total_taxable_value_cdnur),
                "Total_cess_value_cdnur": (Total_cess_value_cdnur),
                "No_of_recipients_cdnur": No_of_recipients_cdnur,
                "No_of_invoices_cdnur": No_of_invoices_cdnur,
            })

        if len(final_data_HSN_summary) > 0:
            final_data_HSN_summary.append({
                "no_of_hsn": len(unq_hsn),
                "total_value_hsn": total_value_hsn,
                "total_taxable_value_hsn": (total_taxable_value_hsn),
                "total_igst_tax_hsn": (total_igst_tax_hsn),
                "total_cgst_tax_hsn": (total_cgst_tax_hsn),
                "total_sgst_tax_hsn": (total_sgst_tax_hsn),
            })
        if len(final_data_docs) > 0:
            final_data_docs.append({
                "total_Total_num": (total_Total_num),
                "total_Total_cancelled": (total_Total_cancelled),
            })

    return [final_data_b2b_suppliers, final_data_b2c_large, final_data_b2c_small, final_data_cdnr, final_data_cdnur, final_data_HSN_summary, final_data_docs]

# EXcel Start heare


def b2b_suppliers_excel(wb, b2b_data):
    ws = wb.add_sheet("b2b")

    # custome color
    xlwt.add_palette_colour("custom_colour", 0x21)
    wb.set_colour_RGB(0x21, 248, 203, 173)

    # custome color1
    xlwt.add_palette_colour("custom_colour1", 0x22)
    wb.set_colour_RGB(0x22, 0, 112, 192)

    # freeze first 3 row
    ws.set_panes_frozen(True)
    ws.set_horz_split_pos(4)

    # adjust the row width
    ws.col(0).width = int(100)*int(100)
    ws.col(1).width = 100*90
    ws.col(4).width = 100*90

    # adjust the row height
    ws.row(3).height_mismatch = True
    ws.row(3).height = 100*6
    ws.row(0).height = 300

    # header style
    b2b_header_style = xlwt.XFStyle()

    # borders
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN
    b2b_header_style.borders = borders

    # column value alighn center
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    b2b_header_style.alignment = center

    # font size
    font = xlwt.Font()
    font.bold = True
    font.height = 11 * 20
    font.colour_index = 1
    b2b_header_style.font = font

    # header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    b2b_header_style.pattern = pattern

    # header
    ws.write(0, 0, "Summary For B2B(4)", b2b_header_style)
    ws.write(0, 1, "", b2b_header_style)

    # sub header font
    b2b_subheader_style = xlwt.XFStyle()
    b2b_subheader_style.font = font

    # column value alighn center
    center.horz = Alignment.HORZ_CENTER
    b2b_subheader_style.alignment = center

    # sub header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    b2b_subheader_style.pattern = pattern

    b2b_subheader_style.borders = borders

    # alighn right
    right_b2b_subheader_style = xlwt.XFStyle()
    right = Alignment()
    right.horz = Alignment.HORZ_RIGHT
    right_b2b_subheader_style.alignment = right
    right_b2b_subheader_style.pattern = pattern
    right_b2b_subheader_style.borders = borders
    right_b2b_subheader_style.font = font

    # sub header
    # ======= Label ==========
    ws.write(1, 0, "No. of Recipients", b2b_subheader_style)
    ws.write(1, 1, "", b2b_subheader_style)
    ws.write(1, 2, "No. of Invoices", b2b_subheader_style)
    ws.write(1, 3, "", b2b_subheader_style)
    ws.write(1, 4, "Total Invoice Value", right_b2b_subheader_style)
    ws.write(1, 5, "", b2b_subheader_style)
    ws.write(1, 6, "", b2b_subheader_style)
    ws.write(1, 7, "", b2b_subheader_style)
    ws.write(1, 8, "", b2b_subheader_style)
    ws.write(1, 9, "", b2b_subheader_style)
    ws.write(1, 10, "", b2b_subheader_style)
    ws.write(1, 11, "Total Taxable Value", b2b_subheader_style)
    ws.write(1, 12, "Total Cess", b2b_subheader_style)
    # ======= Label value ==========
    # sub header value font
    b2b_subheader_value_style = xlwt.XFStyle()
    # font size
    font = xlwt.Font()
    font.height = 11 * 20
    b2b_subheader_value_style.font = font
    b2b_subheader_value_style.borders = borders

    b2b_subheader_decimal_style = xlwt.XFStyle()
    b2b_subheader_decimal_style.font = font
    b2b_subheader_decimal_style.borders = borders
    b2b_subheader_decimal_style.num_format_str = '0.00'

    no_of_reciepts = ""
    no_of_invoices = ""
    total_invoice_value = ""
    total_taxable_value = ""
    total_cess = ""

    if b2b_data:
        if not b2b_data[-1]['No_of_recipients_b2b_suppliers'] == 0:
            no_of_reciepts = b2b_data[-1]['No_of_recipients_b2b_suppliers']
        if not b2b_data[-1]['No_of_invoices_b2b_suppliers'] == 0:
            no_of_invoices = b2b_data[-1]['No_of_invoices_b2b_suppliers']
        if not b2b_data[-1]['Total_invoice_value_b2b_suppliers'] == 0:
            total_invoice_value = b2b_data[-1]['Total_invoice_value_b2b_suppliers']
        if not b2b_data[-1]['Total_taxable_value_b2b_suppliers'] == 0:
            total_taxable_value = b2b_data[-1]['Total_taxable_value_b2b_suppliers']
        if not b2b_data[-1]['Total_cess_value_b2b_suppliers'] == 0:
            total_cess = b2b_data[-1]['Total_cess_value_b2b_suppliers']

    ws.write(2, 0, no_of_reciepts, b2b_subheader_value_style)
    ws.write(2, 1, "", b2b_subheader_value_style)
    ws.write(2, 2, no_of_invoices, b2b_subheader_value_style)
    ws.write(2, 3, "", b2b_subheader_value_style)
    ws.write(2, 4, total_invoice_value, b2b_subheader_decimal_style)
    ws.write(2, 5, "", b2b_subheader_value_style)
    ws.write(2, 6, "", b2b_subheader_value_style)
    ws.write(2, 7, "", b2b_subheader_value_style)
    ws.write(2, 8, "", b2b_subheader_value_style)
    ws.write(2, 9, "", b2b_subheader_value_style)
    ws.write(2, 10, "", b2b_subheader_value_style)
    ws.write(2, 11, total_taxable_value, b2b_subheader_decimal_style)
    ws.write(2, 12, total_cess, b2b_subheader_decimal_style)
    # ws.write_merge(1,1,0,1,'No. of Recipients',b2b_subheader_style)

    # column header style
    b2b_column_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()

    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    b2b_column_header_style.pattern = pattern

    # column value center
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    b2b_column_header_style.alignment = center
    # font size
    b2b_column_header_style.font = font
    b2b_column_header_style.alignment.wrap = 1

    # column header names, you can use your own headers here
    columns = ['GSTIN/UIN of Recipient', 'Receiver Name', 'Invoice Number', 'Invoice date', 'Invoice Value', 'Place Of Supply',
               'Reverse Charge', 'Applicable%of Tax Rate', 'Invoice Type', 'E-Commerce GSTIN', 'Rate', 'Taxable Value', 'Cess Amount', ]

    # Sheet header, first row
    row_num = 3
    # font_style = xlwt.XFStyle()
    # write column headers in sheet
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], b2b_column_header_style)

     # alighn right
    b2b_values = xlwt.XFStyle()
    right = Alignment()
    right.horz = Alignment.HORZ_RIGHT
    b2b_values.alignment = right
    b2b_values.font = font

    # decimal 0.00 style
    grandtotal_b2b_values = xlwt.XFStyle()
    grandtotal_b2b_values.font = font
    grandtotal_b2b_values.num_format_str = '0.00'

    # alighn right
    b2b_date_values = xlwt.XFStyle()
    b2b_date_values.alignment = center
    b2b_date_values.font = font

    # font_size_11
    common_style = xlwt.XFStyle()
    common_style.font = font

    # laast items remove from array
    if b2b_data:
        del b2b_data[-1]

    for i in b2b_data:
        try:
            Customer_GST_No = i['Customer_GST_No']
        except:
            Customer_GST_No = ""
        try:
            CustomerName = i['CustomerName']
        except:
            CustomerName = ""
        try:
            VoucherNo = i['VoucherNo']
        except:
            VoucherNo = ""
        try:
            Date = i['Date']
        except:
            Date = ""
        try:
            GrandTotal = i['GrandTotal']
            if GrandTotal == 0:
                GrandTotal = ""
        except:
            GrandTotal = ""
        try:
            PlaceOfSupply = i['PlaceOfSupply']
        except:
            PlaceOfSupply = ""
        try:
            ApplicableTaxRate = i['ApplicableTaxRate']
        except:
            ApplicableTaxRate = ""
        try:
            ReverseCharge = i['ReverseCharge']
        except:
            ReverseCharge = ""
        try:
            InvoiceType = i['InvoiceType']
        except:
            InvoiceType = ""
        try:
            E_Commerce_GSTIN = i['E_Commerce_GSTIN']
        except:
            E_Commerce_GSTIN = ""
        try:
            Rate = i['Rate']
            if Rate == 0:
                Rate = ""
        except:
            Rate = ""
        try:
            taxable_value = i['taxable_value']
            if taxable_value == 0:
                taxable_value = ""
        except:
            taxable_value = ""
        try:
            CESS_amount = i['CESS_amount']
            if CESS_amount == 0:
                CESS_amount = ""
        except:
            CESS_amount = ""

        row_num = row_num + 1
        ws.write(row_num, 0, Customer_GST_No, common_style)
        ws.write(row_num, 1, CustomerName, common_style)
        ws.write(row_num, 2, VoucherNo, common_style)
        ws.write(row_num, 3, Date, b2b_date_values)
        ws.write(row_num, 4, GrandTotal, grandtotal_b2b_values)
        ws.write(row_num, 5, PlaceOfSupply, common_style)
        ws.write(row_num, 6, ReverseCharge, common_style)
        ws.write(row_num, 7, ApplicableTaxRate, common_style)
        ws.write(row_num, 8, InvoiceType, common_style)
        ws.write(row_num, 9, E_Commerce_GSTIN, common_style)
        ws.write(row_num, 10, Rate, common_style)
        ws.write(row_num, 11, taxable_value, grandtotal_b2b_values)
        ws.write(row_num, 12, CESS_amount, grandtotal_b2b_values)


def b2cl_excel(wb, b2cl_data):
    ws = wb.add_sheet("b2cl")

    # custome color
    xlwt.add_palette_colour("custom_colour", 0x21)
    wb.set_colour_RGB(0x21, 248, 203, 173)

    # custome color1
    xlwt.add_palette_colour("custom_colour1", 0x22)
    wb.set_colour_RGB(0x22, 0, 112, 192)

    # freeze first 3 row
    ws.set_panes_frozen(True)
    ws.set_horz_split_pos(4)

    # adjust the row width
    ws.col(0).width = int(100)*int(100)
    ws.col(1).width = 100*90
    ws.col(4).width = 100*90

    # adjust the row height
    ws.row(3).height_mismatch = True
    ws.row(3).height = 100*6
    ws.row(0).height = 300

    # header style
    b2cl_header_style = xlwt.XFStyle()

    # column value alighn center
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    b2cl_header_style.alignment = center

    # borders
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN

    # header font
    font = xlwt.Font()
    font.bold = True
    font.height = 11 * 20
    font.colour_index = 1
    b2cl_header_style.font = font
    b2cl_header_style.borders = borders

    # header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    b2cl_header_style.pattern = pattern

    # header
    ws.write(0, 0, "Summary For B2CL(5)", b2cl_header_style)
    ws.write(0, 1, "", b2cl_header_style)

    # sub header font
    b2cl_subheader_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True
    font.height = 11 * 20
    font.colour_index = 1
    b2cl_subheader_style.font = font

    # column value alighn center
    center.horz = Alignment.HORZ_CENTER
    b2cl_subheader_style.alignment = center

    # sub header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    b2cl_subheader_style.pattern = pattern
    b2cl_subheader_style.borders = borders

    # sub header
    # ======= Label ==========
    ws.write(1, 0, "No. of Invoices", b2cl_subheader_style)
    ws.write(1, 1, "", b2cl_subheader_style)
    ws.write(1, 2, "Total Note Value", b2cl_subheader_style)
    ws.write(1, 3, "", b2cl_subheader_style)
    ws.write(1, 4, "", b2cl_subheader_style)
    ws.write(1, 5, "", b2cl_subheader_style)
    ws.write(1, 6, "Total Taxable Value", b2cl_subheader_style)
    ws.write(1, 7, "Total Cess", b2cl_subheader_style)
    ws.write(1, 8, "", b2cl_subheader_style)
    # ======= Label value ==========
    # sub header value font
    b2cl_subheader_value_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.height = 11 * 20
    b2cl_subheader_value_style.borders = borders
    b2cl_subheader_value_style.font = font

    decimal_b2cl_subheader_style = xlwt.XFStyle()
    decimal_b2cl_subheader_style.num_format_str = "0.00"
    decimal_b2cl_subheader_style.borders = borders
    decimal_b2cl_subheader_style.font = font

    # No_of_invoices_b2cl = b2cl_data[-1]['No_of_invoices_b2cl']
    # Total_invoice_value_b2cl = b2cl_data[-1]['Total_invoice_value_b2cl']
    # Total_taxable_value_b2cl = b2cl_data[-1]['Total_taxable_value_b2cl']
    # total_cess = b2cl_data[-1]['Total_cess_value_b2cl']

    No_of_invoices_b2cl = ""
    Total_invoice_value_b2cl = ""
    Total_taxable_value_b2cl = ""
    total_cess = ""

    if b2cl_data:
        if not b2cl_data[-1]['No_of_invoices_b2cl'] == 0:
            No_of_invoices_b2cl = b2cl_data[-1]['No_of_invoices_b2cl']
        if not b2cl_data[-1]['Total_invoice_value_b2cl'] == 0:
            Total_invoice_value_b2cl = b2cl_data[-1]['Total_invoice_value_b2cl']
        if not b2cl_data[-1]['Total_taxable_value_b2cl'] == 0:
            Total_taxable_value_b2cl = b2cl_data[-1]['Total_taxable_value_b2cl']
        if not b2cl_data[-1]['Total_cess_value_b2cl'] == 0:
            total_cess = b2cl_data[-1]['Total_cess_value_b2cl']

    ws.write(2, 0, No_of_invoices_b2cl, b2cl_subheader_value_style)
    ws.write(2, 1, "", b2cl_subheader_value_style)
    ws.write(2, 2, Total_invoice_value_b2cl, decimal_b2cl_subheader_style)
    ws.write(2, 3, "", b2cl_subheader_value_style)
    ws.write(2, 4, "", b2cl_subheader_value_style)
    ws.write(2, 5, "", b2cl_subheader_value_style)
    ws.write(2, 6, Total_taxable_value_b2cl, decimal_b2cl_subheader_style)
    ws.write(2, 7, total_cess, decimal_b2cl_subheader_style)
    ws.write(2, 8, "", b2cl_subheader_value_style)

    # column header style
    b2cl_column_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    b2cl_column_header_style.pattern = pattern

    # font size
    b2cl_column_header_style.font = font
    # alighn center
    b2cl_column_header_style.alignment = center
    b2cl_column_header_style.alignment.wrap = 1

    # column header names, you can use your own headers here
    columns = ['Invoice Number', 'Invoice date', 'Invoice Value', 'Place Of Supply',
               'Applicable % of Tax Rate', 'Rate', 'Taxable Value', 'Cess Amount', 'E-Commerce GSTIN']

    # Sheet header, first row
    row_num = 3
    # write column headers in sheet
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], b2cl_column_header_style)

    if b2cl_data:
        del b2cl_data[-1]
    for i in b2cl_data:
        try:
            VoucherNo = i['VoucherNo']
        except:
            VoucherNo = ""
        try:
            Date = i['Date']
        except:
            Date = ""
        try:
            GrandTotal = i['GrandTotal']
            if GrandTotal == 0:
                GrandTotal = ""
        except:
            GrandTotal = ""
        try:
            ApplicableTaxRate = i['ApplicableTaxRate']
        except:
            ApplicableTaxRate = ""
        try:
            PlaceOfSupply = i['PlaceOfSupply']
        except:
            PlaceOfSupply = ""
        try:
            Rate = i['Rate']
            if Rate == 0:
                Rate = ""
        except:
            Rate = ""
        try:
            taxable_value = i['taxable_value']
            if taxable_value == 0:
                taxable_value = ""
        except:
            taxable_value = ""
        try:
            CESS_amount = i['CESS_amount']
            if CESS_amount == 0:
                CESS_amount = ""
        except:
            CESS_amount = ""

        try:
            E_Commerce_GSTIN = i['E_Commerce_GSTIN']
        except:
            E_Commerce_GSTIN = ""

       # alighn center
        b2cl_column_values = xlwt.XFStyle()
        b2cl_column_values.alignment = center
        b2cl_column_values.num_format_str = "0.00"
        b2cl_column_values.font = font

        # common style
        common_style = xlwt.XFStyle()
        common_style.font = font

        decimal_common_style = xlwt.XFStyle()
        decimal_common_style.font = font
        decimal_common_style.num_format_str = "0.00"

        row_num = row_num + 1
        ws.write(row_num, 0, VoucherNo, common_style)
        ws.write(row_num, 1, Date, b2cl_column_values)
        ws.write(row_num, 2, GrandTotal, decimal_common_style)
        ws.write(row_num, 3, PlaceOfSupply, common_style)
        ws.write(row_num, 4, ApplicableTaxRate, b2cl_column_values)
        ws.write(row_num, 5, Rate, decimal_common_style)
        ws.write(row_num, 6, taxable_value, decimal_common_style)
        ws.write(row_num, 7, 0, decimal_common_style)
        ws.write(row_num, 8, E_Commerce_GSTIN, common_style)


def b2cs_excel(wb, b2cs_data):
    b2cs = wb.add_sheet("b2cs")

    # custome color
    xlwt.add_palette_colour("custom_colour", 0x21)
    wb.set_colour_RGB(0x21, 248, 203, 173)

    # custome color1
    xlwt.add_palette_colour("custom_colour1", 0x22)
    wb.set_colour_RGB(0x22, 0, 112, 192)

    # freeze first 3 row
    b2cs.set_panes_frozen(True)
    b2cs.set_horz_split_pos(4)

    # adjust the row width
    b2cs.col(0).width = int(100)*int(100)
    b2cs.col(1).width = 100*90
    b2cs.col(4).width = 100*90

    # adjust the row height
    b2cs.row(3).height_mismatch = True
    b2cs.row(3).height = 100*6
    b2cs.row(0).height = 300

    # header style
    b2cs_header_style = xlwt.XFStyle()

    # borders
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN

    # column value alighn center
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    b2cs_header_style.alignment = center

    # font size
    font = xlwt.Font()
    font.bold = True
    font.height = 11 * 20
    font.colour_index = 1
    b2cs_header_style.font = font
    b2cs_header_style.borders = borders

    # header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    b2cs_header_style.pattern = pattern

    # header
    b2cs.write(0, 0, "Summary For B2CS(7)", b2cs_header_style)
    b2cs.write(0, 1, "", b2cs_header_style)

    # sub header font
    b2cs_subheader_style = xlwt.XFStyle()
    b2cs_subheader_style.font = font

    # column value alighn center
    # center.horz = Alignment.HORZ_CENTER
    b2cs_subheader_style.alignment = center

    # sub header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    b2cs_subheader_style.pattern = pattern

    b2cs_subheader_style.borders = borders

    # sub header
    # ======= Label ==========
    b2cs.write(1, 0, "", b2cs_subheader_style)
    b2cs.write(1, 1, "", b2cs_subheader_style)
    b2cs.write(1, 2, "", b2cs_subheader_style)
    b2cs.write(1, 3, "", b2cs_subheader_style)
    b2cs.write(1, 4, "Total Taxable Value", b2cs_subheader_style)
    b2cs.write(1, 5, "Total Cess", b2cs_subheader_style)
    b2cs.write(1, 6, "", b2cs_subheader_style)

    # ======= Label value ==========
    # sub header value font
    b2cs_subheader_value_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.height = 11 * 20
    b2cs_subheader_value_style.font = font
    b2cs_subheader_value_style.borders = borders

    decimal_b2cs_subheader_value_style = xlwt.XFStyle()
    decimal_b2cs_subheader_value_style.font = font
    decimal_b2cs_subheader_value_style.borders = borders
    decimal_b2cs_subheader_value_style.num_format_str = '0.00'

    total_taxable_value = ""
    total_cess = ""
    if b2cs_data:
        if not b2cs_data[-1]['Total_taxable_value_b2cs'] == 0:
            total_taxable_value = b2cs_data[-1]['Total_taxable_value_b2cs']
        if not b2cs_data[-1]['Total_cess_value_b2cs'] == 0:
            total_cess = b2cs_data[-1]['Total_cess_value_b2cs']

    b2cs.write(2, 0, "", b2cs_subheader_value_style)
    b2cs.write(2, 1, "", b2cs_subheader_value_style)
    b2cs.write(2, 2, "", b2cs_subheader_value_style)
    b2cs.write(2, 3, "", b2cs_subheader_value_style)
    b2cs.write(2, 4, total_taxable_value, decimal_b2cs_subheader_value_style)
    b2cs.write(2, 5, total_cess, decimal_b2cs_subheader_value_style)
    b2cs.write(2, 6, "", b2cs_subheader_value_style)

    # column header style
    b2cs_column_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    b2cs_column_header_style.pattern = pattern

    # column value center
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    b2cs_column_header_style.alignment = center
    # font size
    b2cs_column_header_style.font = font
    b2cs_column_header_style.alignment.wrap = 1

    # column header names, you can use your own headers here
    columns = ['Type', 'Place Of Supply', 'Applicable% of Tax Rate',
               'Rate', 'Taxable Value',  'Cess Amount', 'E-Commerce GSTIN']

    # Sheet header, first row
    row_num = 3
    # font_style = xlwt.XFStyle()
    # write column headers in sheet
    for col_num in range(len(columns)):
        b2cs.write(row_num, col_num,
                   columns[col_num], b2cs_column_header_style)

    if b2cs_data:
        del b2cs_data[-1]

    for i in b2cs_data:
        try:
            Type = i['Type']
        except:
            Type = ""
        try:
            PlaceOfSupply = i['PlaceOfSupply']
        except:
            PlaceOfSupply = ""
        try:
            ApplicableTaxRate = i['ApplicableTaxRate']
            if ApplicableTaxRate == 0:
                ApplicableTaxRate = ""
        except:
            ApplicableTaxRate = ""
        try:
            Rate = i['Rate']
            if Rate == 0:
                Rate = ""
        except:
            Rate = ""
        try:
            taxable_value = i['taxable_value']
            if taxable_value == 0:
                taxable_value = ""
        except:
            taxable_value = ""
        try:
            E_Commerce_GSTIN = i['E_Commerce_GSTIN']
        except:
            E_Commerce_GSTIN = ""
        try:
            CESS_amount = i['CESS_amount']
            if CESS_amount == 0:
                CESS_amount = ""
        except:
            CESS_amount = ""

        # column header value style
         # alighn center
        b2cs_column_values = xlwt.XFStyle()
        b2cs_column_values.font = font
        b2cs_column_values.alignment = center

        # common_style
        common_style = xlwt.XFStyle()
        common_style.font = font

        # common_style
        decimal_common_style = xlwt.XFStyle()
        decimal_common_style.font = font
        decimal_common_style.num_format_str = '0.00'

        row_num = row_num + 1
        b2cs.write(row_num, 0, Type, common_style)
        b2cs.write(row_num, 1, PlaceOfSupply, common_style)
        b2cs.write(row_num, 2, ApplicableTaxRate, decimal_common_style)
        b2cs.write(row_num, 3, Rate, decimal_common_style)
        b2cs.write(row_num, 4, taxable_value, decimal_common_style)
        b2cs.write(row_num, 5, CESS_amount, decimal_common_style)
        b2cs.write(row_num, 6, E_Commerce_GSTIN, common_style)


def cdnr_excel(wb, cdnr_data):
    ws = wb.add_sheet("cdnr")

    # custome color
    xlwt.add_palette_colour("custom_colour", 0x21)
    wb.set_colour_RGB(0x21, 248, 203, 173)

    # custome color1
    xlwt.add_palette_colour("custom_colour1", 0x22)
    wb.set_colour_RGB(0x22, 0, 112, 192)

    # freeze first 3 row
    ws.set_panes_frozen(True)
    ws.set_horz_split_pos(4)

    # adjust the row width
    ws.col(0).width = int(100)*int(100)
    ws.col(1).width = 100*90

    # adjust the row height
    ws.row(3).height_mismatch = True
    ws.row(3).height = 100*6
    ws.row(0).height = 300

    # header style
    cdnr_header_style = xlwt.XFStyle()

    # borders
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN

    # column value alighn center
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    cdnr_header_style.alignment = center

    # font size
    font = xlwt.Font()
    font.bold = True
    font.height = 11 * 20
    font.colour_index = 1
    cdnr_header_style.font = font
    cdnr_header_style.borders = borders

    # header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    cdnr_header_style.pattern = pattern

    # header
    ws.write(0, 0, "Summary For CDNR(9B)", cdnr_header_style)
    ws.write(0, 1, "", cdnr_header_style)

    # sub header font
    cdnr_subheader_style = xlwt.XFStyle()
    cdnr_subheader_style.font = font

    # column value alighn center
    cdnr_subheader_style.alignment = center

    # sub header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    cdnr_subheader_style.pattern = pattern
    cdnr_subheader_style.borders = borders

    # sub header
    # ======= Label ==========
    ws.write(1, 0, "No. of Recipients", cdnr_subheader_style)
    ws.write(1, 1, "", cdnr_subheader_style)
    ws.write(1, 2, "No. of Notes", cdnr_subheader_style)
    ws.write(1, 3, "", cdnr_subheader_style)
    ws.write(1, 4, "", cdnr_subheader_style)
    ws.write(1, 5, "", cdnr_subheader_style)
    ws.write(1, 6, "", cdnr_subheader_style)
    ws.write(1, 7, "", cdnr_subheader_style)
    ws.write(1, 8, "Total Note Value", cdnr_subheader_style)
    ws.write(1, 9, "", cdnr_subheader_style)
    ws.write(1, 10, "", cdnr_subheader_style)
    ws.write(1, 11, "Total Taxable Value", cdnr_subheader_style)
    ws.write(1, 12, "Total Cess", cdnr_subheader_style)
    # ======= Label value ==========
    # sub header value font
    cdnr_subheader_value_style = xlwt.XFStyle()
    # font size
    font = xlwt.Font()
    font.height = 11 * 20
    cdnr_subheader_value_style.font = font
    cdnr_subheader_value_style.borders = borders

    no_of_reciepts = ""
    no_of_invoices = ""
    total_invoice_value = ""
    total_taxable_value = ""
    total_cess = ""

    if cdnr_data:
        if not cdnr_data[-1]['No_of_recipients_cdnr'] == 0:
            no_of_reciepts = cdnr_data[-1]['No_of_recipients_cdnr']
        if not cdnr_data[-1]['No_of_invoices_cdnr'] == 0:
            no_of_invoices = cdnr_data[-1]['No_of_invoices_cdnr']
        if not cdnr_data[-1]['Total_invoice_value_cdnr'] == 0:
            total_invoice_value = cdnr_data[-1]['Total_invoice_value_cdnr']
        if not cdnr_data[-1]['Total_taxable_value_cdnr'] == 0:
            total_taxable_value = cdnr_data[-1]['Total_taxable_value_cdnr']
        if not cdnr_data[-1]['Total_cess_value_cdnr'] == 0:
            total_cess = cdnr_data[-1]['Total_cess_value_cdnr']

    decimal_cdnr_subheader_style = xlwt.XFStyle()
    decimal_cdnr_subheader_style.font = font
    decimal_cdnr_subheader_style.borders = borders
    decimal_cdnr_subheader_style.num_format_str = "0.00"

    ws.write(2, 0, no_of_reciepts, cdnr_subheader_value_style)
    ws.write(2, 1, "", cdnr_subheader_value_style)
    ws.write(2, 2, no_of_invoices, cdnr_subheader_value_style)
    ws.write(2, 3, "", cdnr_subheader_value_style)
    ws.write(2, 4, "", cdnr_subheader_value_style)
    ws.write(2, 5, "", cdnr_subheader_value_style)
    ws.write(2, 6, "", cdnr_subheader_value_style)
    ws.write(2, 7, "", cdnr_subheader_value_style)
    ws.write(2, 8, total_invoice_value, decimal_cdnr_subheader_style)
    ws.write(2, 9, "", cdnr_subheader_value_style)
    ws.write(2, 10, "", cdnr_subheader_value_style)
    ws.write(2, 11, total_taxable_value, decimal_cdnr_subheader_style)
    ws.write(2, 12, total_cess, decimal_cdnr_subheader_style)

    # column header style
    cdnr_column_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    cdnr_column_header_style.pattern = pattern

    # column value center
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    cdnr_column_header_style.alignment = center
    cdnr_column_header_style.font = font

    # font size
    cdnr_column_header_style.font = font
    cdnr_column_header_style.alignment.wrap = 1

    # column header names, you can use your own headers here
    columns = ['GSTIN/UIN of Recipient', 'Receiver Name', 'Note Number', 'Note Date', 'Note Type', 'Place Of Supply',
               'Reverse Charge', 'Note Supply Type', 'Note Value', 'Applicable % of Tax Rate', 'Rate', 'Taxable Value', 'Cess Amount']

    # Sheet header, first row
    row_num = 3
    # font_style = xlwt.XFStyle()
    # write column headers in sheet
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], cdnr_column_header_style)

    if cdnr_data:
        del cdnr_data[-1]
    for i in cdnr_data:
        try:
            Customer_GST_No = i['Customer_GST_No']
        except:
            Customer_GST_No = ""
        try:
            CustomerName = i['CustomerName']
        except:
            CustomerName = ""
        try:
            RefferenceBillNo = i['RefferenceBillNo']
        except:
            RefferenceBillNo = ""
        try:
            RefferenceBillDate = i['RefferenceBillDate']
        except:
            RefferenceBillDate = ""
        try:
            VoucherNo = i['VoucherNo']
        except:
            VoucherNo = ""
        try:
            Date = i['Date']
        except:
            Date = ""
        try:
            DocumentType = i['DocumentType']
        except:
            DocumentType = ""

        try:
            PlaceOfSupply = i['PlaceOfSupply']
        except:
            PlaceOfSupply = ""
        try:
            GrandTotal = i['GrandTotal']
            if GrandTotal == 0:
                GrandTotal = ""
        except:
            GrandTotal = ""
        try:
            ApplicableTaxRate = i['ApplicableTaxRate']
            if ApplicableTaxRate == 0:
                ApplicableTaxRate = ""
        except:
            ApplicableTaxRate = ""
        try:
            Rate = i['Rate']
            if Rate == 0:
                Rate = ""
        except:
            Rate = ""
        try:
            taxable_value = i['taxable_value']
            if taxable_value == 0:
                taxable_value = ""
        except:
            taxable_value = ""
        try:
            CESS_amount = i['CESS_amount']
            if CESS_amount == 0:
                CESS_amount = ""
        except:
            CESS_amount = ""
        try:
            ReverseCharge = i['ReverseCharge']
        except:
            ReverseCharge = ""

        cdnr_column_value_style = xlwt.XFStyle()
        cdnr_column_value_style.alignment = center
        cdnr_column_value_style.font = font

        # common_style
        common_style = xlwt.XFStyle()
        common_style.font = font

        # decimal common_style
        decimal_common_style = xlwt.XFStyle()
        decimal_common_style.font = font
        decimal_common_style.num_format_str = "0.00"

        row_num = row_num + 1
        ws.write(row_num, 0, Customer_GST_No, common_style)
        ws.write(row_num, 1, CustomerName, common_style)
        # ws.write(row_num, 2, RefferenceBillNo)
        # ws.write(row_num, 3, RefferenceBillDate)
        ws.write(row_num, 2, VoucherNo, common_style)
        ws.write(row_num, 3, Date, cdnr_column_value_style)
        ws.write(row_num, 4, DocumentType, cdnr_column_value_style)
        ws.write(row_num, 5, PlaceOfSupply, common_style)
        ws.write(row_num, 6, ReverseCharge, cdnr_column_value_style)
        ws.write(row_num, 7, 'Regular', common_style)
        ws.write(row_num, 8, GrandTotal, decimal_common_style)
        ws.write(row_num, 9, ApplicableTaxRate, decimal_common_style)
        ws.write(row_num, 10, Rate, decimal_common_style)
        ws.write(row_num, 11, taxable_value, decimal_common_style)
        ws.write(row_num, 12, CESS_amount, decimal_common_style)


def cdnur_excel(wb, cdnur_data):
    ws = wb.add_sheet("cdnur")

    # custome color
    xlwt.add_palette_colour("custom_colour", 0x21)
    wb.set_colour_RGB(0x21, 248, 203, 173)

    # custome color1
    xlwt.add_palette_colour("custom_colour1", 0x22)
    wb.set_colour_RGB(0x22, 0, 112, 192)

    # freeze first 3 row
    ws.set_panes_frozen(True)
    ws.set_horz_split_pos(4)

    # adjust the row width
    ws.col(0).width = int(100)*int(100)
    ws.col(1).width = 100*90
    ws.col(4).width = 100*90

    # adjust the row height
    ws.row(3).height_mismatch = True
    ws.row(3).height = 100*6
    ws.row(0).height = 300

    # header style
    cdnur_header_style = xlwt.XFStyle()

    # borders
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN

    # column value alighn center
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    cdnur_header_style.alignment = center

    # font size
    font = xlwt.Font()
    font.bold = True
    font.height = 11 * 20
    font.colour_index = 1
    cdnur_header_style.font = font
    cdnur_header_style.borders = borders

    # header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    cdnur_header_style.pattern = pattern

    # header
    ws.write(0, 0, "Summary For CDNUR(9B)", cdnur_header_style)
    ws.write(0, 1, "", cdnur_header_style)

    # sub header font
    cdnur_subheader_style = xlwt.XFStyle()
    cdnur_subheader_style.font = font

    # column value alighn center
    cdnur_subheader_style.alignment = center

    # sub header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    cdnur_subheader_style.pattern = pattern

    cdnur_subheader_style.borders = borders

    # sub header
    # ======= Label ==========
    ws.write(1, 0, "", cdnur_subheader_style)
    ws.write(1, 1, "No. of Notes/Vouchers", cdnur_subheader_style)
    ws.write(1, 2, "", cdnur_subheader_style)
    ws.write(1, 3, "", cdnur_subheader_style)
    ws.write(1, 4, "", cdnur_subheader_style)
    ws.write(1, 5, "Total Note Value", cdnur_subheader_style)
    ws.write(1, 6, "", cdnur_subheader_style)
    ws.write(1, 7, "", cdnur_subheader_style)
    ws.write(1, 8, "Total Taxable Value", cdnur_subheader_style)
    ws.write(1, 9, "Total Cess", cdnur_subheader_style)
    # ======= Label value ==========
    # sub header value font
    cdnur_subheader_value_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.height = 11 * 20
    cdnur_subheader_value_style.borders = borders
    cdnur_subheader_value_style.font = font

    No_of_invoices_cdnur = ""
    Total_invoice_value_cdnur = ""
    Total_taxable_value_cdnur = ""
    total_cess = ""

    if cdnur_data:
        if not cdnur_data[-1]['No_of_invoices_cdnur'] == 0:
            No_of_invoices_cdnur = cdnur_data[-1]['No_of_invoices_cdnur']
        if not cdnur_data[-1]['Total_invoice_value_cdnur'] == 0:
            Total_invoice_value_cdnur = cdnur_data[-1]['Total_invoice_value_cdnur']
        if not cdnur_data[-1]['Total_taxable_value_cdnur'] == 0:
            Total_taxable_value_cdnur = cdnur_data[-1]['Total_taxable_value_cdnur']
        if not cdnur_data[-1]['Total_cess_value_cdnur'] == 0:
            total_cess = cdnur_data[-1]['Total_cess_value_cdnur']

    decimal_cdnur_subheader_value_style = xlwt.XFStyle()

    decimal_cdnur_subheader_value_style.borders = borders
    decimal_cdnur_subheader_value_style.font = font
    decimal_cdnur_subheader_value_style.num_format_str = "0.00"

    ws.write(2, 0, "", cdnur_subheader_value_style)
    ws.write(2, 1, No_of_invoices_cdnur, cdnur_subheader_value_style)
    ws.write(2, 2, "", cdnur_subheader_value_style)
    ws.write(2, 3, "", cdnur_subheader_value_style)
    ws.write(2, 4, "", cdnur_subheader_value_style)
    ws.write(2, 5, Total_invoice_value_cdnur,
             decimal_cdnur_subheader_value_style)
    ws.write(2, 6, "", cdnur_subheader_value_style)
    ws.write(2, 7, "", cdnur_subheader_value_style)
    ws.write(2, 8, Total_taxable_value_cdnur,
             decimal_cdnur_subheader_value_style)
    ws.write(2, 9, total_cess, decimal_cdnur_subheader_value_style)

    # column header style
    cdnur_column_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    cdnur_column_header_style.pattern = pattern

    # column value center
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    cdnur_column_header_style.alignment = center

    # font size
    cdnur_column_header_style.font = font
    cdnur_column_header_style.alignment.wrap = 1

    # column header names, you can use your own headers here
    columns = ['UR Type', 'Note Number', 'Note Date', 'Note Type', 'Place Of Supply',
               'Note Value', 'Applicable % of Tax Rate', 'Rate', 'Taxable Value', 'Cess Amount']

    # Sheet header, first row
    row_num = 3
    # font_style = xlwt.XFStyle()
    # write column headers in sheet
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], cdnur_column_header_style)

    if cdnur_data:
        del cdnur_data[-1]

    for i in cdnur_data:
        try:
            UR_Type = i['UR_Type']
        except:
            UR_Type = ""
        try:
            VoucherNo = i['VoucherNo']
        except:
            VoucherNo = ""
        try:
            Date = i['Date']
        except:
            Date = ""
        try:
            DocumentType = i['DocumentType']
        except:
            DocumentType = ""
        try:
            RefferenceBillNo = i['RefferenceBillNo']
        except:
            RefferenceBillNo = ""
        try:
            RefferenceBillDate = i['RefferenceBillDate']
        except:
            RefferenceBillDate = ""

        try:
            PlaceOfSupply = i['PlaceOfSupply']
        except:
            PlaceOfSupply = ""
        try:
            GrandTotal = i['GrandTotal']
            if GrandTotal == 0:
                GrandTotal = ""
        except:
            GrandTotal = ""
        try:
            ApplicableTaxRate = i['ApplicableTaxRate']
            if ApplicableTaxRate == 0:
                ApplicableTaxRate = ""
        except:
            ApplicableTaxRate = ""
        try:
            Rate = i['Rate']
            if Rate == 0:
                Rate = ""
        except:
            Rate = ""
        try:
            taxable_value = i['taxable_value']
            if taxable_value == 0:
                taxable_value = ""
        except:
            taxable_value = ""
        try:
            CESS_amount = i['CESS_amount']
            if CESS_amount == 0:
                CESS_amount = ""
        except:
            CESS_amount = ""

        cdnur_column_value_style = xlwt.XFStyle()
        cdnur_column_value_style.alignment = center
        cdnur_column_value_style.font = font

        # common_style
        common_style = xlwt.XFStyle()
        common_style.font = font

        # common_style
        decimal_cdnur_subheader_value_style = xlwt.XFStyle()
        decimal_cdnur_subheader_value_style.font = font
        decimal_cdnur_subheader_value_style.num_format_str = "0.00"

        row_num = row_num + 1
        ws.write(row_num, 0, UR_Type, cdnur_column_value_style)
        ws.write(row_num, 1, VoucherNo, common_style)
        ws.write(row_num, 2, Date, cdnur_column_value_style)
        ws.write(row_num, 3, DocumentType, cdnur_column_value_style)
        ws.write(row_num, 4, PlaceOfSupply, common_style)
        ws.write(row_num, 5, GrandTotal, decimal_cdnur_subheader_value_style)
        ws.write(row_num, 6, ApplicableTaxRate,
                 decimal_cdnur_subheader_value_style)
        ws.write(row_num, 7, Rate, decimal_cdnur_subheader_value_style)
        ws.write(row_num, 8, taxable_value,
                 decimal_cdnur_subheader_value_style)
        ws.write(row_num, 9, CESS_amount, decimal_cdnur_subheader_value_style)


def hsn_excel(wb, hsn_data):
    ws = wb.add_sheet("hsn")

    # custome color
    xlwt.add_palette_colour("custom_colour", 0x21)
    wb.set_colour_RGB(0x21, 248, 203, 173)

    # custome color1
    xlwt.add_palette_colour("custom_colour1", 0x22)
    wb.set_colour_RGB(0x22, 0, 112, 192)

    # freeze first 3 row
    ws.set_panes_frozen(True)
    ws.set_horz_split_pos(4)

    # adjust the row width
    ws.col(0).width = int(100)*int(100)
    ws.col(1).width = 100*90
    ws.col(4).width = 100*90

    # adjust the row height
    ws.row(3).height_mismatch = True
    ws.row(0).height = 300
    ws.row(1).height = 300
    ws.row(2).height = 300
    ws.row(3).height = 100*4

    # header style
    cdnur_header_style = xlwt.XFStyle()

    # borders THIN
    borders_thin = xlwt.Borders()
    borders_thin.left = xlwt.Borders.THIN
    borders_thin.right = xlwt.Borders.THIN
    borders_thin.top = xlwt.Borders.THIN
    borders_thin.bottom = xlwt.Borders.THIN

    # borders THICK
    borders_thick = xlwt.Borders()
    borders_thick.left = xlwt.Borders.THIN
    borders_thick.right = xlwt.Borders.THIN
    borders_thick.top = xlwt.Borders.THICK
    borders_thick.bottom = xlwt.Borders.THICK

    # column value alighn center
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    cdnur_header_style.alignment = center

    # font size
    font = xlwt.Font()
    font.bold = True
    font.height = 11 * 20
    font.colour_index = 1
    cdnur_header_style.font = font
    cdnur_header_style.borders = borders_thick

    # header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    cdnur_header_style.pattern = pattern

    # header
    ws.write(0, 0, "Summary For HSN(12)", cdnur_header_style)
    ws.write(0, 1, "", cdnur_header_style)

    # sub header font
    cdnur_subheader_style = xlwt.XFStyle()
    cdnur_subheader_style.font = font

    # column value alighn center
    # center.horz = Alignment.HORZ_CENTER
    cdnur_subheader_style.alignment = center

    # sub header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    cdnur_subheader_style.pattern = pattern
    # border
    cdnur_subheader_style.borders = borders_thick
    # font
    cdnur_subheader_style.borders = borders_thick

    # sub header
    # ======= Label ==========
    ws.write(1, 0, "No. of HSN", cdnur_subheader_style)
    ws.write(1, 1, "", cdnur_subheader_style)
    ws.write(1, 2, "", cdnur_subheader_style)
    ws.write(1, 3, "", cdnur_subheader_style)
    ws.write(1, 4, "Total Value", cdnur_subheader_style)
    ws.write(1, 5, "", cdnur_subheader_style)
    ws.write(1, 6, "Total Taxable Value", cdnur_subheader_style)
    ws.write(1, 7, "Total Integrated Tax", cdnur_subheader_style)
    ws.write(1, 8, "Total Central Tax", cdnur_subheader_style)
    ws.write(1, 9, "Total State/UT Tax", cdnur_subheader_style)
    ws.write(1, 10, "Total Cess", cdnur_subheader_style)
    # ======= Label value ==========
    # sub header value font
    cdnur_subheader_value_style = xlwt.XFStyle()
    font_size_11 = xlwt.Font()
    font_size_11.height = 11 * 20
    cdnur_subheader_value_style.borders = borders_thin
    cdnur_subheader_value_style.font = font_size_11

    decimal_cdnur_subheader_value_style = xlwt.XFStyle()
    decimal_cdnur_subheader_value_style.borders = borders_thin
    decimal_cdnur_subheader_value_style.font = font_size_11
    decimal_cdnur_subheader_value_style.num_format_str = "0.00"

    no_of_hsn = ""
    total_value_hsn = ""
    total_taxable_value_hsn = ""
    total_igst_tax_hsn = ""
    total_cgst_tax_hsn = ""
    total_sgst_tax_hsn = ""
    if hsn_data:
        if not hsn_data[-1]['no_of_hsn'] == 0:
            no_of_hsn = hsn_data[-1]['no_of_hsn']
        if not hsn_data[-1]['total_value_hsn'] == 0:
            total_value_hsn = hsn_data[-1]['total_value_hsn']
        if not hsn_data[-1]['total_taxable_value_hsn'] == 0:
            total_taxable_value_hsn = hsn_data[-1]['total_taxable_value_hsn']
        if not hsn_data[-1]['total_igst_tax_hsn'] == 0:
            total_igst_tax_hsn = hsn_data[-1]['total_igst_tax_hsn']
        if not hsn_data[-1]['total_cgst_tax_hsn'] == 0:
            total_cgst_tax_hsn = hsn_data[-1]['total_cgst_tax_hsn']
        if not hsn_data[-1]['total_sgst_tax_hsn'] == 0:
            total_sgst_tax_hsn = hsn_data[-1]['total_sgst_tax_hsn']

    total_cess = ""

    ws.write(2, 0, no_of_hsn, cdnur_subheader_value_style)
    ws.write(2, 1, "", cdnur_subheader_value_style)
    ws.write(2, 2, "", cdnur_subheader_value_style)
    ws.write(2, 3, "", cdnur_subheader_value_style)
    ws.write(2, 4, total_value_hsn, decimal_cdnur_subheader_value_style)
    ws.write(2, 5, "", cdnur_subheader_value_style)
    ws.write(2, 6, total_taxable_value_hsn,
             decimal_cdnur_subheader_value_style)
    ws.write(2, 7, total_igst_tax_hsn, decimal_cdnur_subheader_value_style)
    ws.write(2, 8, total_cgst_tax_hsn, decimal_cdnur_subheader_value_style)
    ws.write(2, 9, total_sgst_tax_hsn, decimal_cdnur_subheader_value_style)
    ws.write(2, 10, total_cess, decimal_cdnur_subheader_value_style)

    # column header style
    cdnur_column_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    cdnur_column_header_style.pattern = pattern

    # column value center
    cdnur_column_header_style.alignment = center

    # font size
    cdnur_column_header_style.font = font_size_11

    # column header names, you can use your own headers here
    columns = ['HSN', 'Description', 'UQC', 'Total Quantity', 'Total Value', 'Rate',
               'Taxable Value', 'IGST Amount', 'CGST Amount', 'SGST Amount', 'Cess Amount']

    # Sheet header, first row
    row_num = 3
    # font_style = xlwt.XFStyle()
    # write column headers in sheet
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], cdnur_column_header_style)

    if hsn_data:
        del hsn_data[-1]
    for i in hsn_data:
        try:
            HSN_Code = i['HSN_Code']
        except:
            HSN_Code = ""
        try:
            Description = i['Description']
        except:
            Description = ""
        try:
            UQC = i['UQC']
        except:
            UQC = ""
        try:
            TotalQuantity = i['TotalQuantity']
            if TotalQuantity == 0:
                TotalQuantity = ""
        except:
            TotalQuantity = ""
        try:
            TotalNetAmount = i['TotalNetAmount']
            if TotalNetAmount == 0:
                TotalNetAmount = ""
        except:
            TotalNetAmount = ""
        try:
            TotalTaxableValue = i['TotalTaxableValue']
            if TotalTaxableValue == 0:
                TotalTaxableValue = ""
        except:
            TotalTaxableValue = ""

        try:
            TotalIGSTAmount = i['TotalIGSTAmount']
            if TotalIGSTAmount == 0:
                TotalIGSTAmount = ""
        except:
            TotalIGSTAmount = ""
        try:
            TotalCGSTAmount = i['TotalCGSTAmount']
            if TotalCGSTAmount == 0:
                TotalCGSTAmount = ""
        except:
            TotalCGSTAmount = ""
        try:
            TotalSGSTAmount = i['TotalSGSTAmount']
            if TotalSGSTAmount == 0:
                TotalSGSTAmount = ""
        except:
            TotalSGSTAmount = ""
        try:
            CessAmount = i['CessAmount']
            if CessAmount == 0:
                CessAmount = ""
        except:
            CessAmount = ""

        try:
            Rate = i['Rate']
            if Rate == 0:
                Rate = ""
        except:
            Rate = ""

        cdnur_column_value_style = xlwt.XFStyle()
        cdnur_column_value_style.font = font_size_11
        cdnur_column_value_style.alignment = center

        # font size
        common_style = xlwt.XFStyle()
        common_style.font = font_size_11

        # font size
        decimal_cdnur_subheader_value_style = xlwt.XFStyle()
        decimal_cdnur_subheader_value_style.font = font_size_11

        decimal_cdnur_subheader_value_style.num_format_str = "0.00"

        row_num = row_num + 1
        ws.write(row_num, 0, HSN_Code, cdnur_column_value_style)
        ws.write(row_num, 1, Description, common_style)
        ws.write(row_num, 2, UQC, common_style)
        ws.write(row_num, 3, TotalQuantity,
                 decimal_cdnur_subheader_value_style)
        ws.write(row_num, 4, TotalNetAmount,
                 decimal_cdnur_subheader_value_style)
        ws.write(row_num, 5, Rate, decimal_cdnur_subheader_value_style)
        ws.write(row_num, 6, TotalTaxableValue,
                 decimal_cdnur_subheader_value_style)
        ws.write(row_num, 7, TotalIGSTAmount,
                 decimal_cdnur_subheader_value_style)
        ws.write(row_num, 8, TotalCGSTAmount,
                 decimal_cdnur_subheader_value_style)
        ws.write(row_num, 9, TotalSGSTAmount,
                 decimal_cdnur_subheader_value_style)
        ws.write(row_num, 10, 0, decimal_cdnur_subheader_value_style)


def default_b2cl_excel(wb, b2cl_data):
    ws = wb.add_sheet("b2cl")

    # custome color
    xlwt.add_palette_colour("custom_colour", 0x21)
    wb.set_colour_RGB(0x21, 248, 203, 173)

    # custome color1
    xlwt.add_palette_colour("custom_colour1", 0x22)
    wb.set_colour_RGB(0x22, 0, 112, 192)

    # freeze first 3 row
    ws.set_panes_frozen(True)
    ws.set_horz_split_pos(4)

    # adjust the row width
    ws.col(0).width = int(100)*int(100)
    ws.col(1).width = 100*90
    ws.col(4).width = 100*90

    # adjust the row height
    ws.row(3).height_mismatch = True
    ws.row(3).height = 100*6
    ws.row(0).height = 300

    # header style
    b2cl_header_style = xlwt.XFStyle()

    # column value alighn center
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    b2cl_header_style.alignment = center

    # borders
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN

    # header font
    font = xlwt.Font()
    font.bold = True
    font.height = 11 * 20
    font.colour_index = 1
    b2cl_header_style.font = font
    b2cl_header_style.borders = borders

    # header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    b2cl_header_style.pattern = pattern

    # header
    ws.write(0, 0, "Summary For B2CL(7)", b2cl_header_style)
    ws.write(0, 1, "", b2cl_header_style)

    # sub header font
    b2cl_subheader_style = xlwt.XFStyle()
    b2cl_subheader_style.font = font

    # column value alighn center
    center.horz = Alignment.HORZ_CENTER
    b2cl_subheader_style.alignment = center

    # sub header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    b2cl_subheader_style.pattern = pattern

    b2cl_subheader_style.borders = borders

    # sub header
    # ======= Label ==========
    ws.write(1, 0, "No. of Invoice", b2cl_subheader_style)
    ws.write(1, 1, "", b2cl_subheader_style)
    ws.write(1, 2, "Total Note Value", b2cl_subheader_style)
    ws.write(1, 3, "", b2cl_subheader_style)
    ws.write(1, 4, "", b2cl_subheader_style)
    ws.write(1, 5, "", b2cl_subheader_style)
    ws.write(1, 6, "", b2cl_subheader_style)
    ws.write(1, 7, "Total Taxable Value", b2cl_subheader_style)
    # ws.write(1, 8, "Total Cess", b2cl_subheader_style)
    # ======= Label value ==========
    # sub header value font
    b2cl_subheader_value_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.height = 11 * 20
    b2cl_subheader_value_style.borders = borders
    b2cl_subheader_value_style.font = font

    no_of_reciepts = ""
    no_of_invoices = ""
    total_invoice_value = ""
    total_taxable_value = ""
    total_cess = '0.0'
    ws.write(2, 0, "", b2cl_subheader_value_style)
    ws.write(2, 1, "", b2cl_subheader_value_style)
    ws.write(2, 2, "", b2cl_subheader_value_style)
    ws.write(2, 3, "", b2cl_subheader_value_style)
    ws.write(2, 4, "", b2cl_subheader_value_style)
    ws.write(2, 5, "", b2cl_subheader_value_style)
    ws.write(2, 6, "", b2cl_subheader_value_style)
    ws.write(2, 7, "", b2cl_subheader_value_style)
    # ws.write_merge(1,1,0,1,'No. of Recipients',b2cl_subheader_style)

    # column header style
    b2cl_column_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    b2cl_column_header_style.pattern = pattern
    b2cl_column_header_style.font = font

    # column value style
    al = Alignment()
    al.horz = Alignment.HORZ_CENTER
    b2cl_column_header_style.alignment = al

    # column header names, you can use your own headers here
    columns = ['Invoice  number', 'Invoice Date', 'Invoice value', 'Applicable % of Tax Rate',
               'Place of Supply(POS)', 'Rate', 'Taxable Value', 'Cess Amount']

    # Sheet header, first row
    row_num = 3
    # font_style = xlwt.XFStyle()
    # write column headers in sheet
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], b2cl_column_header_style)

    for i in b2cl_data:
        try:
            VoucherNo = i['VoucherNo']
        except:
            VoucherNo = ""
        try:
            Date = i['Date']
        except:
            Date = ""
        try:
            GrandTotal = i['GrandTotal']
        except:
            GrandTotal = ""
        try:
            ApplicableTaxRate = i['ApplicableTaxRate']
        except:
            ApplicableTaxRate = ""
        try:
            PlaceOfSupply = i['PlaceOfSupply']
        except:
            PlaceOfSupply = ""
        try:
            Rate = i['Rate']
        except:
            Rate = ""
        try:
            taxable_value = i['taxable_value']
        except:
            taxable_value = ""
        try:
            CESS_amount = i['CESS_amount']
        except:
            CESS_amount = ""

        # row_num = row_num + 1
        # ws.write(row_num, 0, VoucherNo)
        # ws.write(row_num, 1, Date)
        # ws.write(row_num, 2, GrandTotal)
        # ws.write(row_num, 3, ApplicableTaxRate)
        # ws.write(row_num, 4, PlaceOfSupply)
        # ws.write(row_num, 5, Rate)
        # ws.write(row_num, 6, taxable_value)
        # ws.write(row_num, 7, '0.0')


def b2ba_excel(wb, b2ba_data):
    ws = wb.add_sheet("b2ba")

    # orange custome color
    xlwt.add_palette_colour("custom_colour", 0x21)
    wb.set_colour_RGB(0x21, 248, 203, 173)

    # blue custome color1
    xlwt.add_palette_colour("custom_colour1", 0x22)
    wb.set_colour_RGB(0x22, 0, 112, 192)

    # light blue custome color1
    xlwt.add_palette_colour("custom_colour2", 0x23)
    wb.set_colour_RGB(0x23, 180, 198, 231)

    # freeze first 3 row
    ws.set_panes_frozen(True)
    ws.set_horz_split_pos(4)

    # adjust the row width
    ws.col(0).width = int(100)*int(100)
    ws.col(1).width = 100*90
    ws.col(4).width = 100*90

    # adjust the row height
    ws.row(3).height_mismatch = True
    ws.row(3).height = 100*6
    ws.row(0).height = 300

    # header style
    header_style = xlwt.XFStyle()

    # column value alighn center
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    header_style.alignment = center

    # borders
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN

    # header font
    font = xlwt.Font()
    font.bold = True
    font.height = 11 * 20
    font.colour_index = 1
    header_style.font = font
    header_style.borders = borders

    # header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    header_style.pattern = pattern

    # second header style
    seond_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    seond_header_style.pattern = pattern
    seond_header_style.borders = borders
    seond_header_style.alignment = center
    font_1 = xlwt.Font()
    font_1.bold = True
    font_1.height = 11 * 20
    font_1.colour_index = 0
    seond_header_style.font = font_1

    # color light orange second header style
    seond_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    seond_header_style.pattern = pattern
    seond_header_style.borders = borders
    seond_header_style.alignment = center
    font_1 = xlwt.Font()
    font_1.bold = True
    font_1.height = 11 * 20
    font_1.colour_index = 0
    seond_header_style.font = font_1

 # color light blue third header style
    third_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour2']
    third_header_style.pattern = pattern
    third_header_style.borders = borders
    third_header_style.alignment = center
    third_header_style.font = font_1

    # header
    ws.write(0, 0, "Summary For B2BA", header_style)
    ws.write(0, 1, "Original details", seond_header_style)
    ws.write(0, 2, "", seond_header_style)
    ws.write(0, 3, "", seond_header_style)
    ws.write_merge(0, 0, 4, 14, 'Revised Details', third_header_style)

    # sub header font
    subheader_style = xlwt.XFStyle()
    subheader_style.font = font

    # column value alighn center
    center.horz = Alignment.HORZ_CENTER
    subheader_style.alignment = center

    # sub header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    subheader_style.pattern = pattern

    subheader_style.borders = borders

    # sub header
    # ======= Label ==========
    ws.write(1, 0, "No. of Recipients", subheader_style)
    ws.write(1, 1, "", subheader_style)
    ws.write(1, 2, "No. of Invoices", subheader_style)
    ws.write(1, 3, "", subheader_style)
    ws.write(1, 4, "", subheader_style)
    ws.write(1, 5, "", subheader_style)
    ws.write(1, 6, "Total Invoice Value", subheader_style)
    ws.write(1, 7, "", subheader_style)
    ws.write(1, 8, "", subheader_style)
    ws.write(1, 9, "", subheader_style)
    ws.write(1, 10, "", subheader_style)
    ws.write(1, 11, "", subheader_style)
    ws.write(1, 12, "Total Taxable Value", subheader_style)
    ws.write(1, 13, "Total Cess", subheader_style)
    ws.write(1, 14, "", subheader_style)
    # ws.write(1, 8, "Total Cess", subheader_style)
    # ======= Label value ==========
    # sub header value font
    subheader_value_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.height = 11 * 20
    subheader_value_style.borders = borders
    subheader_value_style.font = font

    no_of_reciepts = ""
    no_of_invoices = ""
    total_invoice_value = ""
    total_taxable_value = ""
    total_cess = '0.0'
    ws.write(2, 0, "", subheader_value_style)
    ws.write(2, 1, "", subheader_value_style)
    ws.write(2, 2, "", subheader_value_style)
    ws.write(2, 3, "", subheader_value_style)
    ws.write(2, 4, "", subheader_value_style)
    ws.write(2, 5, "", subheader_value_style)
    ws.write(2, 6, "", subheader_value_style)
    ws.write(2, 7, "", subheader_value_style)
    ws.write(2, 8, "", subheader_value_style)
    ws.write(2, 9, "", subheader_value_style)
    ws.write(2, 10, "", subheader_value_style)
    ws.write(2, 11, "", subheader_value_style)
    ws.write(2, 12, "", subheader_value_style)
    ws.write(2, 13, "", subheader_value_style)
    ws.write(2, 14, "", subheader_value_style)

    # column header style
    column_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    column_header_style.pattern = pattern
    column_header_style.font = font

    # column value style
    al = Alignment()
    al.horz = Alignment.HORZ_CENTER
    column_header_style.alignment = al
    column_header_style.alignment.wrap = 1

    # column header names, you can use your own headers here
    columns = ['GSTIN/UIN of Recipient', 'Receiver Name', 'Original Invoice Number', 'Original Invoice date', 'Revised Invoice Number', 'Revised Invoice date',
               'Invoice Value', 'Place Of Supply', 'Reverse Charge', 'Applicable % of Tax Rate', 'Invoice Type', 'E-Commerce GSTIN', 'Rate', 'Taxable Value', 'Cess Amount']

    # Sheet header, first row
    row_num = 3
    # font_style = xlwt.XFStyle()
    # write column headers in sheet
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], column_header_style)

        # row_num = row_num + 1
        # ws.write(row_num, 0, VoucherNo)
        # ws.write(row_num, 1, Date)
        # ws.write(row_num, 2, GrandTotal)
        # ws.write(row_num, 3, ApplicableTaxRate)
        # ws.write(row_num, 4, PlaceOfSupply)
        # ws.write(row_num, 5, Rate)
        # ws.write(row_num, 6, taxable_value)
        # ws.write(row_num, 7, '0.0')


def b2cla_excel(wb, b2ba_data):
    ws = wb.add_sheet("b2cla")

    # orange custome color
    xlwt.add_palette_colour("custom_colour", 0x21)
    wb.set_colour_RGB(0x21, 248, 203, 173)

    # blue custome color1
    xlwt.add_palette_colour("custom_colour1", 0x22)
    wb.set_colour_RGB(0x22, 0, 112, 192)

    # light blue custome color1
    xlwt.add_palette_colour("custom_colour2", 0x23)
    wb.set_colour_RGB(0x23, 180, 198, 231)

    # freeze first 3 row
    ws.set_panes_frozen(True)
    ws.set_horz_split_pos(4)

    # adjust the row width
    ws.col(0).width = int(100)*int(100)
    ws.col(1).width = 100*90
    ws.col(4).width = 100*90

    # adjust the row height
    ws.row(3).height_mismatch = True
    ws.row(3).height = 100*6
    ws.row(0).height = 300

    # header style
    header_style = xlwt.XFStyle()

    # column value alighn center
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    header_style.alignment = center

    # borders
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN

    # header font
    font = xlwt.Font()
    font.bold = True
    font.height = 11 * 20
    font.colour_index = 1
    header_style.font = font
    header_style.borders = borders

    # header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    header_style.pattern = pattern

    # second header style
    seond_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    seond_header_style.pattern = pattern
    seond_header_style.borders = borders
    seond_header_style.alignment = center
    font_1 = xlwt.Font()
    font_1.bold = True
    font_1.height = 11 * 20
    font_1.colour_index = 0
    seond_header_style.font = font_1

    # color light orange second header style
    seond_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    seond_header_style.pattern = pattern
    seond_header_style.borders = borders
    seond_header_style.alignment = center
    font_1 = xlwt.Font()
    font_1.height = 11 * 20
    font_1.colour_index = 0
    seond_header_style.font = font_1

 # color light blue third header style
    third_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour2']
    third_header_style.pattern = pattern
    third_header_style.borders = borders
    third_header_style.alignment = center
    third_header_style.font = font_1

    # header
    ws.write(0, 0, "Summary For B2CLA", header_style)
    ws.write(0, 1, "Original details", seond_header_style)
    ws.write(0, 2, "", seond_header_style)
    ws.write_merge(0, 0, 3, 10, 'Revised Details', third_header_style)

    # sub header font
    subheader_style = xlwt.XFStyle()
    subheader_style.font = font

    # column value alighn center
    center.horz = Alignment.HORZ_CENTER
    subheader_style.alignment = center

    # sub header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    subheader_style.pattern = pattern

    subheader_style.borders = borders

    # sub header
    # ======= Label ==========
    ws.write(1, 0, "No. of Invoices", subheader_style)
    ws.write(1, 1, "", subheader_style)
    ws.write(1, 2, "", subheader_style)
    ws.write(1, 3, "", subheader_style)
    ws.write(1, 4, "", subheader_style)
    ws.write(1, 5, "Total Inv Value", subheader_style)
    ws.write(1, 6, "", subheader_style)
    ws.write(1, 7, "", subheader_style)
    ws.write(1, 8, "Total Taxable Value", subheader_style)
    ws.write(1, 9, "Total Cess", subheader_style)
    ws.write(1, 10, "", subheader_style)
    # ws.write(1, 8, "Total Cess", subheader_style)
    # ======= Label value ==========
    # sub header value font
    subheader_value_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.height = 11 * 20
    subheader_value_style.borders = borders
    subheader_value_style.font = font

    no_of_reciepts = ""
    no_of_invoices = ""
    total_invoice_value = ""
    total_taxable_value = ""
    total_cess = '0.0'
    ws.write(2, 0, "", subheader_value_style)
    ws.write(2, 1, "", subheader_value_style)
    ws.write(2, 2, "", subheader_value_style)
    ws.write(2, 3, "", subheader_value_style)
    ws.write(2, 4, "", subheader_value_style)
    ws.write(2, 5, "", subheader_value_style)
    ws.write(2, 6, "", subheader_value_style)
    ws.write(2, 7, "", subheader_value_style)
    ws.write(2, 8, "", subheader_value_style)
    ws.write(2, 9, "", subheader_value_style)
    ws.write(2, 10, "", subheader_value_style)

    # column header style
    column_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    column_header_style.pattern = pattern
    column_header_style.font = font

    # column value style
    al = Alignment()
    al.horz = Alignment.HORZ_CENTER
    column_header_style.alignment = al
    column_header_style.alignment.wrap = 1

    # column header names, you can use your own headers here
    columns = ['Original Invoice Number', 'Original Invoice date', 'Original Place Of Supply', 'Revised Invoice Number',
               'Revised Invoice date', 'Invoice Value', 'Applicable % of Tax Rate', 'Rate', 'Taxable Value', 'Cess Amount', 'E-Commerce GSTIN', ]

    # Sheet header, first row
    row_num = 3
    # font_style = xlwt.XFStyle()
    # write column headers in sheet
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], column_header_style)

        # row_num = row_num + 1
        # ws.write(row_num, 0, VoucherNo)
        # ws.write(row_num, 1, Date)
        # ws.write(row_num, 2, GrandTotal)
        # ws.write(row_num, 3, ApplicableTaxRate)
        # ws.write(row_num, 4, PlaceOfSupply)
        # ws.write(row_num, 5, Rate)
        # ws.write(row_num, 6, taxable_value)
        # ws.write(row_num, 7, '0.0')


def b2csa_excel(wb, b2ba_data):
    ws = wb.add_sheet("b2csa")

    # orange custome color
    xlwt.add_palette_colour("custom_colour", 0x21)
    wb.set_colour_RGB(0x21, 248, 203, 173)

    # blue custome color1
    xlwt.add_palette_colour("custom_colour1", 0x22)
    wb.set_colour_RGB(0x22, 0, 112, 192)

    # light blue custome color1
    xlwt.add_palette_colour("custom_colour2", 0x23)
    wb.set_colour_RGB(0x23, 180, 198, 231)

    # freeze first 3 row
    ws.set_panes_frozen(True)
    ws.set_horz_split_pos(4)

    # adjust the row width
    ws.col(0).width = int(100)*int(100)
    ws.col(1).width = 100*90
    ws.col(4).width = 100*90

    # adjust the row height
    ws.row(3).height_mismatch = True
    ws.row(3).height = 100*6
    ws.row(0).height = 300

    # header style
    header_style = xlwt.XFStyle()

    # column value alighn center
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    header_style.alignment = center

    # borders
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN

    # header font
    font = xlwt.Font()
    font.bold = True
    font.height = 11 * 20
    font.colour_index = 1
    header_style.font = font
    header_style.borders = borders

    # header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    header_style.pattern = pattern

    # second header style
    seond_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    seond_header_style.pattern = pattern
    seond_header_style.borders = borders
    seond_header_style.alignment = center
    font_1 = xlwt.Font()
    font_1.bold = True
    font_1.height = 11 * 20
    font_1.colour_index = 0
    seond_header_style.font = font_1

    # color light orange second header style
    seond_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    seond_header_style.pattern = pattern
    seond_header_style.borders = borders
    seond_header_style.alignment = center
    font_1 = xlwt.Font()
    font_1.height = 11 * 20
    font_1.colour_index = 0
    seond_header_style.font = font_1

 # color light blue third header style
    third_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour2']
    third_header_style.pattern = pattern
    third_header_style.borders = borders
    third_header_style.alignment = center
    third_header_style.font = font_1

    # header
    ws.write(0, 0, "Summary For B2CSA", header_style)
    ws.write(0, 1, "Original details", seond_header_style)
    ws.write_merge(0, 0, 2, 8, 'Revised Details', third_header_style)

    # sub header font
    subheader_style = xlwt.XFStyle()
    subheader_style.font = font

    # column value alighn center
    center.horz = Alignment.HORZ_CENTER
    subheader_style.alignment = center

    # sub header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    subheader_style.pattern = pattern

    subheader_style.borders = borders

    # sub header
    # ======= Label ==========
    ws.write(1, 0, "", subheader_style)
    ws.write(1, 1, "", subheader_style)
    ws.write(1, 2, "", subheader_style)
    ws.write(1, 3, "", subheader_style)
    ws.write(1, 4, "", subheader_style)
    ws.write(1, 5, "", subheader_style)
    ws.write(1, 6, "Total Taxable Value", subheader_style)
    ws.write(1, 7, "Total Cess", subheader_style)
    ws.write(1, 8, "", subheader_style)
    # ws.write(1, 8, "Total Cess", subheader_style)
    # ======= Label value ==========
    # sub header value font
    subheader_value_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.height = 11 * 20
    subheader_value_style.borders = borders
    subheader_value_style.font = font

    no_of_reciepts = ""
    no_of_invoices = ""
    total_invoice_value = ""
    total_taxable_value = ""
    total_cess = '0.0'
    ws.write(2, 0, "", subheader_value_style)
    ws.write(2, 1, "", subheader_value_style)
    ws.write(2, 2, "", subheader_value_style)
    ws.write(2, 3, "", subheader_value_style)
    ws.write(2, 4, "", subheader_value_style)
    ws.write(2, 5, "", subheader_value_style)
    ws.write(2, 6, "", subheader_value_style)
    ws.write(2, 7, "", subheader_value_style)
    ws.write(2, 8, "", subheader_value_style)

    # column header style
    column_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    column_header_style.pattern = pattern
    column_header_style.font = font

    # column value style
    al = Alignment()
    al.horz = Alignment.HORZ_CENTER
    column_header_style.alignment = al
    column_header_style.alignment.wrap = 1

    # column header names, you can use your own headers here
    columns = ['Financial Year', 'Original Month', 'Place Of Supply', 'Type',
               'Applicable % of Tax Rate', 'Rate', 'Taxable Value', 'Cess Amount', 'E-Commerce GSTIN']

    # Sheet header, first row
    row_num = 3
    # font_style = xlwt.XFStyle()
    # write column headers in sheet
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], column_header_style)

        # row_num = row_num + 1
        # ws.write(row_num, 0, VoucherNo)
        # ws.write(row_num, 1, Date)
        # ws.write(row_num, 2, GrandTotal)
        # ws.write(row_num, 3, ApplicableTaxRate)
        # ws.write(row_num, 4, PlaceOfSupply)
        # ws.write(row_num, 5, Rate)
        # ws.write(row_num, 6, taxable_value)
        # ws.write(row_num, 7, '0.0')


def cdnra_excel(wb, b2ba_data):
    ws = wb.add_sheet("cdnra")

    # orange custome color
    xlwt.add_palette_colour("custom_colour", 0x21)
    wb.set_colour_RGB(0x21, 248, 203, 173)

    # blue custome color1
    xlwt.add_palette_colour("custom_colour1", 0x22)
    wb.set_colour_RGB(0x22, 0, 112, 192)

    # light blue custome color1
    xlwt.add_palette_colour("custom_colour2", 0x23)
    wb.set_colour_RGB(0x23, 180, 198, 231)

    # freeze first 3 row
    ws.set_panes_frozen(True)
    ws.set_horz_split_pos(4)

    # adjust the row width
    ws.col(0).width = int(100)*int(100)
    ws.col(1).width = 100*90
    ws.col(4).width = 100*90

    # adjust the row height
    ws.row(3).height_mismatch = True
    ws.row(3).height = 100*6
    ws.row(0).height = 300

    # header style
    header_style = xlwt.XFStyle()

    # column value alighn center
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    header_style.alignment = center

    # borders
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN

    # header font
    font = xlwt.Font()
    font.bold = True
    font.height = 11 * 20
    font.colour_index = 1
    header_style.font = font
    header_style.borders = borders

    # header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    header_style.pattern = pattern

    # second header style
    seond_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    seond_header_style.pattern = pattern
    seond_header_style.borders = borders
    seond_header_style.alignment = center
    font_1 = xlwt.Font()
    font_1.bold = True
    font_1.height = 11 * 20
    font_1.colour_index = 0
    seond_header_style.font = font_1

    # color light orange second header style
    seond_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    seond_header_style.pattern = pattern
    seond_header_style.borders = borders
    seond_header_style.alignment = center
    font_1 = xlwt.Font()
    font_1.height = 11 * 20
    font_1.colour_index = 0
    seond_header_style.font = font_1

 # color light blue third header style
    third_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour2']
    third_header_style.pattern = pattern
    third_header_style.borders = borders
    third_header_style.alignment = center
    third_header_style.font = font_1

    # header
    ws.write(0, 0, "Summary For CDNRA", header_style)
    # ws.write(0, 1, "Original details", seond_header_style)
    ws.write_merge(0, 0, 1, 3, 'Original details', seond_header_style)
    ws.write_merge(0, 0, 4, 14, 'Revised Details', third_header_style)

    # sub header font
    subheader_style = xlwt.XFStyle()
    subheader_style.font = font

    # column value alighn center
    center.horz = Alignment.HORZ_CENTER
    subheader_style.alignment = center

    # sub header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    subheader_style.pattern = pattern

    subheader_style.borders = borders

    # sub header
    # ======= Label ==========
    ws.write(1, 0, "No. of Recipients", subheader_style)
    ws.write(1, 1, "", subheader_style)
    ws.write(1, 2, "No. of Notes/Vouchers", subheader_style)
    ws.write(1, 3, "", subheader_style)
    ws.write(1, 4, "", subheader_style)
    ws.write(1, 5, "", subheader_style)
    ws.write(1, 6, "", subheader_style)
    ws.write(1, 7, "", subheader_style)
    ws.write(1, 8, "", subheader_style)
    ws.write(1, 9, "", subheader_style)
    ws.write(1, 10, "Total Note Value", subheader_style)
    ws.write(1, 11, "", subheader_style)
    ws.write(1, 12, "", subheader_style)
    ws.write(1, 13, "Total Taxable Value", subheader_style)
    ws.write(1, 14, "Total Cess", subheader_style)
    # ws.write(1, 8, "Total Cess", subheader_style)
    # ======= Label value ==========
    # sub header value font
    subheader_value_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.height = 11 * 20
    subheader_value_style.borders = borders
    subheader_value_style.font = font

    no_of_reciepts = ""
    no_of_invoices = ""
    total_invoice_value = ""
    total_taxable_value = ""
    total_cess = '0.0'
    ws.write(2, 0, "", subheader_value_style)
    ws.write(2, 1, "", subheader_value_style)
    ws.write(2, 2, "", subheader_value_style)
    ws.write(2, 3, "", subheader_value_style)
    ws.write(2, 4, "", subheader_value_style)
    ws.write(2, 5, "", subheader_value_style)
    ws.write(2, 6, "", subheader_value_style)
    ws.write(2, 7, "", subheader_value_style)
    ws.write(2, 8, "", subheader_value_style)
    ws.write(2, 9, "", subheader_value_style)
    ws.write(2, 10, "", subheader_value_style)
    ws.write(2, 11, "", subheader_value_style)
    ws.write(2, 12, "", subheader_value_style)
    ws.write(2, 13, "", subheader_value_style)
    ws.write(2, 14, "", subheader_value_style)

    # first column header style
    orange_column_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    orange_column_header_style.pattern = pattern
    orange_column_header_style.font = font
    orange_column_header_style.alignment = center
    orange_column_header_style.alignment.wrap = 1

    # second column header style
    l_blue_column_header_style = xlwt.XFStyle()
    light_blue = xlwt.Pattern()
    light_blue.pattern = xlwt.Pattern.SOLID_PATTERN

    light_blue.pattern_fore_colour = xlwt.Style.colour_map['custom_colour2']
    l_blue_column_header_style.pattern = light_blue
    l_blue_column_header_style.font = font
    l_blue_column_header_style.alignment = center
    l_blue_column_header_style.alignment.wrap = 1

    # column header names, you can use your own headers here
    columns = ['GSTIN/UIN of Recipient', 'Receiver Name', 'Original Note Number', 'Original Note Date', 'Revised Note Number', 'Revised Note Date',
               'Note Type', 'Place Of Supply', 'Reverse Charge', 'Note Supply Type', 'Note Value', 'Applicable % of Tax Rate', 'Rate', 'Taxable Value', 'Cess Amount', ]

    # Sheet header, first row
    row_num = 3
    # font_style = xlwt.XFStyle()
    # write column headers in sheet
    for col_num in range(len(columns)):
        if col_num < 4:
            ws.write(row_num, col_num,
                     columns[col_num], orange_column_header_style)
        else:
            ws.write(row_num, col_num,
                     columns[col_num], l_blue_column_header_style)

        # row_num = row_num + 1
        # ws.write(row_num, 0, VoucherNo)
        # ws.write(row_num, 1, Date)
        # ws.write(row_num, 2, GrandTotal)
        # ws.write(row_num, 3, ApplicableTaxRate)
        # ws.write(row_num, 4, PlaceOfSupply)
        # ws.write(row_num, 5, Rate)
        # ws.write(row_num, 6, taxable_value)
        # ws.write(row_num, 7, '0.0')


def cdnura_excel(wb, cdnura_data):
    ws = wb.add_sheet("cdnura")

    # orange custome color
    xlwt.add_palette_colour("custom_colour", 0x21)
    wb.set_colour_RGB(0x21, 248, 203, 173)

    # blue custome color1
    xlwt.add_palette_colour("custom_colour1", 0x22)
    wb.set_colour_RGB(0x22, 0, 112, 192)

    # light blue custome color1
    xlwt.add_palette_colour("custom_colour2", 0x23)
    wb.set_colour_RGB(0x23, 180, 198, 231)

    # freeze first 3 row
    ws.set_panes_frozen(True)
    ws.set_horz_split_pos(4)

    # adjust the row width
    ws.col(0).width = int(100)*int(100)
    ws.col(1).width = 100*90
    ws.col(4).width = 100*90

    # adjust the row height
    ws.row(3).height_mismatch = True
    ws.row(3).height = 100*6
    ws.row(0).height = 300

    # header style
    header_style = xlwt.XFStyle()

    # column value alighn center
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    header_style.alignment = center

    # borders
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN

    # header font
    font = xlwt.Font()
    font.bold = True
    font.height = 11 * 20
    font.colour_index = 1
    header_style.font = font
    header_style.borders = borders

    # header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    header_style.pattern = pattern

    # second header style
    seond_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    seond_header_style.pattern = pattern
    seond_header_style.borders = borders
    seond_header_style.alignment = center
    font_1 = xlwt.Font()
    font_1.bold = True
    font_1.height = 11 * 20
    font_1.colour_index = 0
    seond_header_style.font = font_1

    # color light orange second header style
    seond_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    seond_header_style.pattern = pattern
    seond_header_style.borders = borders
    seond_header_style.alignment = center
    font_1 = xlwt.Font()
    font_1.height = 11 * 20
    font_1.colour_index = 0
    seond_header_style.font = font_1

 # color light blue third header style
    third_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour2']
    third_header_style.pattern = pattern
    third_header_style.borders = borders
    third_header_style.alignment = center
    third_header_style.font = font_1

    # header
    ws.write(0, 0, "Summary For CDNURA", header_style)
    ws.write_merge(0, 0, 1, 2, 'Original details', seond_header_style)
    ws.write_merge(0, 0, 3, 11, 'Revised Details', third_header_style)

    # sub header font
    subheader_style = xlwt.XFStyle()
    subheader_style.font = font

    # column value alighn center
    center.horz = Alignment.HORZ_CENTER
    subheader_style.alignment = center

    # sub header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    subheader_style.pattern = pattern

    subheader_style.borders = borders

    # sub header
    # ======= Label ==========
    ws.write(1, 0, "", subheader_style)
    ws.write(1, 1, "No. of Notes/Vouchers", subheader_style)
    ws.write(1, 2, "", subheader_style)
    ws.write(1, 3, "", subheader_style)
    ws.write(1, 4, "", subheader_style)
    ws.write(1, 5, "", subheader_style)
    ws.write(1, 6, "", subheader_style)
    ws.write(1, 7, "Total Note Value", subheader_style)
    ws.write(1, 8, "", subheader_style)
    ws.write(1, 9, "", subheader_style)
    ws.write(1, 10, "Total Taxable Value", subheader_style)
    ws.write(1, 11, "Total Cess", subheader_style)
    # ws.write(1, 8, "Total Cess", subheader_style)
    # ======= Label value ==========
    # sub header value font
    subheader_value_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.height = 11 * 20
    subheader_value_style.borders = borders
    subheader_value_style.font = font

    no_of_reciepts = ""
    no_of_invoices = ""
    total_invoice_value = ""
    total_taxable_value = ""
    total_cess = '0.0'
    ws.write(2, 0, "", subheader_value_style)
    ws.write(2, 1, "", subheader_value_style)
    ws.write(2, 2, "", subheader_value_style)
    ws.write(2, 3, "", subheader_value_style)
    ws.write(2, 4, "", subheader_value_style)
    ws.write(2, 5, "", subheader_value_style)
    ws.write(2, 6, "", subheader_value_style)
    ws.write(2, 7, "", subheader_value_style)
    ws.write(2, 8, "", subheader_value_style)
    ws.write(2, 9, "", subheader_value_style)
    ws.write(2, 10, "", subheader_value_style)
    ws.write(2, 11, "", subheader_value_style)

    # column header style
    orange_column_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    orange_column_header_style.pattern = pattern
    orange_column_header_style.font = font

    orange_column_header_style.alignment = center
    orange_column_header_style.alignment.wrap = 1

    # column header style
    l_blue_column_header_style = xlwt.XFStyle()
    pattern1 = xlwt.Pattern()
    pattern1.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern1.pattern_fore_colour = xlwt.Style.colour_map['custom_colour2']
    l_blue_column_header_style.pattern = pattern1
    l_blue_column_header_style.font = font

    l_blue_column_header_style.alignment = center
    l_blue_column_header_style.alignment.wrap = 1

    # column header names, you can use your own headers here
    columns = ['UR Type', 'Original Note Number', 'Original Note Date', 'Revised Note Number', 'Revised Note Date',
               'Note Type', 'Place Of Supply', 'Note Value', 'Applicable % of Tax Rate', 'Rate', 'Taxable Value', 'Cess Amount']

    # Sheet header, first row
    row_num = 3
    # font_style = xlwt.XFStyle()
    # write column headers in sheet
    for col_num in range(len(columns)):
        if col_num < 4:
            ws.write(row_num, col_num,
                     columns[col_num], orange_column_header_style)
        else:
            ws.write(row_num, col_num,
                     columns[col_num], l_blue_column_header_style)

        # row_num = row_num + 1
        # ws.write(row_num, 0, VoucherNo)
        # ws.write(row_num, 1, Date)
        # ws.write(row_num, 2, GrandTotal)
        # ws.write(row_num, 3, ApplicableTaxRate)
        # ws.write(row_num, 4, PlaceOfSupply)
        # ws.write(row_num, 5, Rate)
        # ws.write(row_num, 6, taxable_value)
        # ws.write(row_num, 7, '0.0')


def exp_excel(wb, exp_data):
    ws = wb.add_sheet("exp")

    # orange custome color
    xlwt.add_palette_colour("custom_colour", 0x21)
    wb.set_colour_RGB(0x21, 248, 203, 173)

    # blue custome color1
    xlwt.add_palette_colour("custom_colour1", 0x22)
    wb.set_colour_RGB(0x22, 0, 112, 192)

    # light blue custome color1
    xlwt.add_palette_colour("custom_colour2", 0x23)
    wb.set_colour_RGB(0x23, 180, 198, 231)

    # freeze first 3 row
    ws.set_panes_frozen(True)
    ws.set_horz_split_pos(4)

    # adjust the row width
    ws.col(0).width = int(100)*int(100)
    ws.col(1).width = 100*90
    ws.col(4).width = 100*90

    # adjust the row height
    ws.row(3).height_mismatch = True
    ws.row(3).height = 100*6
    ws.row(0).height = 300

    # header style
    header_style = xlwt.XFStyle()

    # column value alighn center
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    header_style.alignment = center

    # borders
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN

    # header font
    font = xlwt.Font()
    font.bold = True
    font.height = 11 * 20
    font.colour_index = 1
    header_style.font = font
    header_style.borders = borders

    # header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    header_style.pattern = pattern

    # second header style
    seond_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    seond_header_style.pattern = pattern
    seond_header_style.borders = borders
    seond_header_style.alignment = center
    font_1 = xlwt.Font()
    font_1.bold = True
    font_1.height = 11 * 20
    font_1.colour_index = 0
    seond_header_style.font = font_1

    # color light orange second header style
    seond_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    seond_header_style.pattern = pattern
    seond_header_style.borders = borders
    seond_header_style.alignment = center
    font_1 = xlwt.Font()
    font_1.height = 11 * 20
    font_1.colour_index = 0
    seond_header_style.font = font_1

 # color light blue third header style
    third_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour2']
    third_header_style.pattern = pattern
    third_header_style.borders = borders
    third_header_style.alignment = center
    third_header_style.font = font_1

    # header
    ws.write(0, 0, "Summary For EXP(6)", header_style)

    # sub header font
    subheader_style = xlwt.XFStyle()
    subheader_style.font = font

    # column value alighn center
    center.horz = Alignment.HORZ_CENTER
    subheader_style.alignment = center

    # sub header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    subheader_style.pattern = pattern

    subheader_style.borders = borders

    # sub header
    # ======= Label ==========
    ws.write(1, 0, "", subheader_style)
    ws.write(1, 1, "No. of Invoices", subheader_style)
    ws.write(1, 2, "", subheader_style)
    ws.write(1, 3, "Total Invoice Value", subheader_style)
    ws.write(1, 4, "", subheader_style)
    ws.write(1, 5, "No. of Shipping Bill", subheader_style)
    ws.write(1, 6, "", subheader_style)
    ws.write(1, 7, "", subheader_style)
    ws.write(1, 8, "", subheader_style)
    ws.write(1, 9, "Total Taxable Value", subheader_style)
    # ws.write(1, 8, "Total Cess", subheader_style)
    # ======= Label value ==========
    # sub header value font
    subheader_value_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.height = 11 * 20
    subheader_value_style.borders = borders
    subheader_value_style.font = font

    no_of_reciepts = ""
    no_of_invoices = ""
    total_invoice_value = ""
    total_taxable_value = ""
    total_cess = '0.0'
    ws.write(2, 0, "", subheader_value_style)
    ws.write(2, 1, "", subheader_value_style)
    ws.write(2, 2, "", subheader_value_style)
    ws.write(2, 3, "", subheader_value_style)
    ws.write(2, 4, "", subheader_value_style)
    ws.write(2, 5, "", subheader_value_style)
    ws.write(2, 6, "", subheader_value_style)
    ws.write(2, 7, "", subheader_value_style)
    ws.write(2, 8, "", subheader_value_style)
    ws.write(2, 9, "", subheader_value_style)

    # column header style
    column_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    column_header_style.pattern = pattern
    column_header_style.font = font

    # column value style
    al = Alignment()
    al.horz = Alignment.HORZ_CENTER
    column_header_style.alignment = al

    # column header names, you can use your own headers here
    columns = ['Export Type', 'Invoice Number', 'Invoice date', 'Invoice Value', 'Port Code',
               'Shipping Bill Number', 'Shipping Bill Date', 'Rate', 'Taxable Value', 'Cess Amount', ]

    # Sheet header, first row
    row_num = 3
    # font_style = xlwt.XFStyle()
    # write column headers in sheet
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], column_header_style)

        # row_num = row_num + 1
        # ws.write(row_num, 0, VoucherNo)
        # ws.write(row_num, 1, Date)
        # ws.write(row_num, 2, GrandTotal)
        # ws.write(row_num, 3, ApplicableTaxRate)
        # ws.write(row_num, 4, PlaceOfSupply)
        # ws.write(row_num, 5, Rate)
        # ws.write(row_num, 6, taxable_value)
        # ws.write(row_num, 7, '0.0')


def expa_excel(wb, expa_data):
    ws = wb.add_sheet("expa")

    # orange custome color
    xlwt.add_palette_colour("custom_colour", 0x21)
    wb.set_colour_RGB(0x21, 248, 203, 173)

    # blue custome color1
    xlwt.add_palette_colour("custom_colour1", 0x22)
    wb.set_colour_RGB(0x22, 0, 112, 192)

    # light blue custome color1
    xlwt.add_palette_colour("custom_colour2", 0x23)
    wb.set_colour_RGB(0x23, 180, 198, 231)

    # freeze first 3 row
    ws.set_panes_frozen(True)
    ws.set_horz_split_pos(4)

    # adjust the row width
    ws.col(0).width = int(100)*int(100)
    ws.col(1).width = 100*90
    ws.col(4).width = 100*90

    # adjust the row height
    ws.row(3).height_mismatch = True
    ws.row(3).height = 100*6
    ws.row(0).height = 300

    # header style
    header_style = xlwt.XFStyle()

    # column value alighn center
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    header_style.alignment = center

    # borders
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN

    # header font
    font = xlwt.Font()
    font.bold = True
    font.height = 11 * 20
    font.colour_index = 1
    header_style.font = font
    header_style.borders = borders

    # header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    header_style.pattern = pattern

    # second header style
    seond_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    seond_header_style.pattern = pattern
    seond_header_style.borders = borders
    seond_header_style.alignment = center
    font_1 = xlwt.Font()
    font_1.bold = True
    font_1.height = 11 * 20
    font_1.colour_index = 0
    seond_header_style.font = font_1

    # color light orange second header style
    seond_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    seond_header_style.pattern = pattern
    seond_header_style.borders = borders
    seond_header_style.alignment = center
    font_1 = xlwt.Font()
    font_1.height = 11 * 20
    font_1.colour_index = 0
    seond_header_style.font = font_1

 # color light blue third header style
    third_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour2']
    third_header_style.pattern = pattern
    third_header_style.borders = borders
    third_header_style.alignment = center
    third_header_style.font = font_1

    # header
    ws.write(0, 0, "Summary For EXPA", header_style)
    ws.write_merge(0, 0, 1, 2, 'Original details', seond_header_style)
    ws.write_merge(0, 0, 3, 11, 'Revised Details', third_header_style)

    # sub header font
    subheader_style = xlwt.XFStyle()
    subheader_style.font = font

    # column value alighn center
    center.horz = Alignment.HORZ_CENTER
    subheader_style.alignment = center

    # sub header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    subheader_style.pattern = pattern
    subheader_style.borders = borders

    # sub header
    # ======= Label ==========
    ws.write(1, 0, "", subheader_style)
    ws.write(1, 1, "No. of Invoices", subheader_style)
    ws.write(1, 2, "", subheader_style)
    ws.write(1, 3, "", subheader_style)
    ws.write(1, 4, "", subheader_style)
    ws.write(1, 5, "Total Invoice Value", subheader_style)
    ws.write(1, 6, "", subheader_style)
    ws.write(1, 7, "No. of Shipping Bill", subheader_style)
    ws.write(1, 8, "", subheader_style)
    ws.write(1, 9, "", subheader_style)
    ws.write(1, 10, "", subheader_style)
    ws.write(1, 11, "Total Taxable Value", subheader_style)
    # ws.write(1, 8, "Total Cess", subheader_style)
    # ======= Label value ==========
    # sub header value font
    subheader_value_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.height = 11 * 20
    subheader_value_style.borders = borders
    subheader_value_style.font = font

    no_of_reciepts = ""
    no_of_invoices = ""
    total_invoice_value = ""
    total_taxable_value = ""
    total_cess = '0.0'
    ws.write(2, 0, "", subheader_value_style)
    ws.write(2, 1, "", subheader_value_style)
    ws.write(2, 2, "", subheader_value_style)
    ws.write(2, 3, "", subheader_value_style)
    ws.write(2, 4, "", subheader_value_style)
    ws.write(2, 5, "", subheader_value_style)
    ws.write(2, 6, "", subheader_value_style)
    ws.write(2, 7, "", subheader_value_style)
    ws.write(2, 8, "", subheader_value_style)
    ws.write(2, 9, "", subheader_value_style)
    ws.write(2, 10, "", subheader_value_style)
    ws.write(2, 11, "", subheader_value_style)

    # column header style
    orange_column_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    orange_column_header_style.pattern = pattern
    orange_column_header_style.font = font
    orange_column_header_style.alignment = center

    # column header style
    l_blue_column_header_style = xlwt.XFStyle()
    pattern1 = xlwt.Pattern()
    pattern1.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern1.pattern_fore_colour = xlwt.Style.colour_map['custom_colour2']
    l_blue_column_header_style.pattern = pattern1
    l_blue_column_header_style.font = font
    l_blue_column_header_style.alignment = center

    # column value style
    # al = Alignment()
    # center.horz = Alignment.HORZ_CENTER

    # column header names, you can use your own headers here
    columns = ['Export Type', 'Original Invoice Number', 'Original Invoice date', 'Revised Invoice Number', 'Revised Invoice date',
               'Invoice Value', 'Port Code', 'Shipping Bill Number', 'Shipping Bill Date', 'Rate', 'Taxable Value', 'Cess Amount', ]

    # Sheet header, first row
    row_num = 3
    # font_style = xlwt.XFStyle()
    # write column headers in sheet
    for col_num in range(len(columns)):
        if col_num < 3:
            ws.write(row_num, col_num,
                     columns[col_num], orange_column_header_style)
        else:
            ws.write(row_num, col_num,
                     columns[col_num], l_blue_column_header_style)

        # row_num = row_num + 1
        # ws.write(row_num, 0, VoucherNo)
        # ws.write(row_num, 1, Date)
        # ws.write(row_num, 2, GrandTotal)
        # ws.write(row_num, 3, ApplicableTaxRate)
        # ws.write(row_num, 4, PlaceOfSupply)
        # ws.write(row_num, 5, Rate)
        # ws.write(row_num, 6, taxable_value)
        # ws.write(row_num, 7, '0.0')


def at_excel(wb, at_data):
    ws = wb.add_sheet("at")

    # orange custome color
    xlwt.add_palette_colour("custom_colour", 0x21)
    wb.set_colour_RGB(0x21, 248, 203, 173)

    # blue custome color1
    xlwt.add_palette_colour("custom_colour1", 0x22)
    wb.set_colour_RGB(0x22, 0, 112, 192)

    # light blue custome color1
    xlwt.add_palette_colour("custom_colour2", 0x23)
    wb.set_colour_RGB(0x23, 180, 198, 231)

    # freeze first 3 row
    ws.set_panes_frozen(True)
    ws.set_horz_split_pos(4)

    # adjust the row width
    ws.col(0).width = int(100)*int(100)
    ws.col(1).width = 100*90
    ws.col(4).width = 100*90

    # adjust the row height
    ws.row(3).height_mismatch = True
    ws.row(3).height = 100*6
    ws.row(0).height = 300

    # header style
    header_style = xlwt.XFStyle()

    # column value alighn center
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    header_style.alignment = center

    # borders
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN

    # header font
    font = xlwt.Font()
    font.bold = True
    font.height = 11 * 20
    font.colour_index = 1
    header_style.font = font
    header_style.borders = borders

    header_style.alignment.wrap = 1

    # header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    header_style.pattern = pattern

    # header
    ws.write(0, 0, "Summary For Advance Received (11B) ", header_style)

    # sub header font
    subheader_style = xlwt.XFStyle()
    subheader_style.font = font

    # column value alighn center
    center.horz = Alignment.HORZ_CENTER
    subheader_style.alignment = center

    # sub header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    subheader_style.pattern = pattern

    subheader_style.borders = borders

    # sub header
    # ======= Label ==========
    ws.write(1, 0, "", subheader_style)
    ws.write(1, 1, "", subheader_style)
    ws.write(1, 2, "", subheader_style)
    ws.write(1, 3, "Total Advance Received", subheader_style)
    ws.write(1, 4, "Total Cess", subheader_style)
    # ws.write(1, 8, "Total Cess", subheader_style)
    # ======= Label value ==========
    # sub header value font
    subheader_value_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.height = 11 * 20
    subheader_value_style.borders = borders
    subheader_value_style.font = font

    no_of_reciepts = ""
    no_of_invoices = ""
    total_invoice_value = ""
    total_taxable_value = ""
    total_cess = '0.0'
    ws.write(2, 0, "", subheader_value_style)
    ws.write(2, 1, "", subheader_value_style)
    ws.write(2, 2, "", subheader_value_style)
    ws.write(2, 3, "", subheader_value_style)
    ws.write(2, 4, "", subheader_value_style)

    # column header style
    column_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    column_header_style.pattern = pattern
    column_header_style.font = font

    # column value style
    al = Alignment()
    al.horz = Alignment.HORZ_CENTER
    column_header_style.alignment = al
    column_header_style.alignment.wrap = 1

    # column header names, you can use your own headers here
    columns = ['Place Of Supply', 'Applicable % of Tax Rate',
               'Rate', 'Gross Advance Received', 'Cess Amount']

    # Sheet header, first row
    row_num = 3
    # font_style = xlwt.XFStyle()
    # write column headers in sheet
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], column_header_style)

        # row_num = row_num + 1
        # ws.write(row_num, 0, VoucherNo)
        # ws.write(row_num, 1, Date)
        # ws.write(row_num, 2, GrandTotal)
        # ws.write(row_num, 3, ApplicableTaxRate)
        # ws.write(row_num, 4, PlaceOfSupply)
        # ws.write(row_num, 5, Rate)
        # ws.write(row_num, 6, taxable_value)
        # ws.write(row_num, 7, '0.0')


def ata_excel(wb, ata_data):
    ws = wb.add_sheet("ata")

    # orange custome color
    xlwt.add_palette_colour("custom_colour", 0x21)
    wb.set_colour_RGB(0x21, 248, 203, 173)

    # blue custome color1
    xlwt.add_palette_colour("custom_colour1", 0x22)
    wb.set_colour_RGB(0x22, 0, 112, 192)

    # light blue custome color1
    xlwt.add_palette_colour("custom_colour2", 0x23)
    wb.set_colour_RGB(0x23, 180, 198, 231)

    # freeze first 3 row
    ws.set_panes_frozen(True)
    ws.set_horz_split_pos(4)

    # adjust the row width
    ws.col(0).width = int(100)*int(100)
    ws.col(1).width = 100*90
    ws.col(4).width = 100*90

    # adjust the row height
    ws.row(3).height_mismatch = True
    ws.row(3).height = 100*6
    ws.row(0).height = 300

    # header style
    header_style = xlwt.XFStyle()

    # column value alighn center
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    header_style.alignment = center

    # borders
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN

    # header font
    font = xlwt.Font()
    font.bold = True
    font.height = 11 * 20
    font.colour_index = 1
    header_style.font = font
    header_style.borders = borders

    # header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    header_style.pattern = pattern
    header_style.alignment.wrap = 1

    # second header style
    seond_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    seond_header_style.pattern = pattern
    seond_header_style.borders = borders
    seond_header_style.alignment = center
    font_1 = xlwt.Font()
    font_1.bold = True
    font_1.height = 11 * 20
    font_1.colour_index = 0
    seond_header_style.font = font_1

    # color light orange second header style
    seond_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    seond_header_style.pattern = pattern
    seond_header_style.borders = borders
    seond_header_style.alignment = center
    font_1 = xlwt.Font()
    font_1.height = 11 * 20
    font_1.colour_index = 0
    seond_header_style.font = font_1

 # color light blue third header style
    third_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour2']
    third_header_style.pattern = pattern
    third_header_style.borders = borders
    third_header_style.alignment = center
    third_header_style.font = font_1

    # header
    ws.write(
        0, 0, "Summary For Amended Tax Liability(Advance Received) ", header_style)
    ws.write_merge(0, 0, 1, 2, 'Original details', seond_header_style)
    ws.write_merge(0, 0, 3, 6, 'Revised Details', third_header_style)

    # sub header font
    subheader_style = xlwt.XFStyle()
    subheader_style.font = font

    # column value alighn center
    center.horz = Alignment.HORZ_CENTER
    subheader_style.alignment = center

    # sub header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    subheader_style.pattern = pattern

    subheader_style.borders = borders

    # sub header
    # ======= Label ==========
    ws.write(1, 0, "", subheader_style)
    ws.write(1, 1, "", subheader_style)
    ws.write(1, 2, "", subheader_style)
    ws.write(1, 3, "", subheader_style)
    ws.write(1, 4, "", subheader_style)
    ws.write(1, 5, "Total Advance Received", subheader_style)
    ws.write(1, 6, "Total Cess", subheader_style)
    # ws.write(1, 8, "Total Cess", subheader_style)
    # ======= Label value ==========
    # sub header value font
    subheader_value_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.height = 11 * 20
    subheader_value_style.borders = borders
    subheader_value_style.font = font

    no_of_reciepts = ""
    no_of_invoices = ""
    total_invoice_value = ""
    total_taxable_value = ""
    total_cess = '0.0'
    ws.write(2, 0, "", subheader_value_style)
    ws.write(2, 1, "", subheader_value_style)
    ws.write(2, 2, "", subheader_value_style)
    ws.write(2, 3, "", subheader_value_style)
    ws.write(2, 4, "", subheader_value_style)
    ws.write(2, 5, "", subheader_value_style)
    ws.write(2, 6, "", subheader_value_style)

    # orange column header style
    orange_column_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    orange_column_header_style.pattern = pattern
    orange_column_header_style.font = font
    orange_column_header_style.alignment = center
    orange_column_header_style.alignment.wrap = 1

    # l_blue column header style
    l_blue_column_header_style = xlwt.XFStyle()
    pattern1 = xlwt.Pattern()
    pattern1.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern1.pattern_fore_colour = xlwt.Style.colour_map['custom_colour2']
    l_blue_column_header_style.pattern = pattern1
    l_blue_column_header_style.font = font
    l_blue_column_header_style.alignment = center
    l_blue_column_header_style.alignment.wrap = 1

    # column header names, you can use your own headers here
    columns = ['Financial Year', 'Original Month', 'Original Place Of Supply',
               'Applicable % of Tax Rate', 'Rate', 'Gross Advance Received', 'Cess Amount', ]

    # Sheet header, first row
    row_num = 3
    # font_style = xlwt.XFStyle()
    # write column headers in sheet
    for col_num in range(len(columns)):
        if col_num < 3:
            ws.write(row_num, col_num,
                     columns[col_num], orange_column_header_style)
        else:
            ws.write(row_num, col_num,
                     columns[col_num], l_blue_column_header_style)

        # row_num = row_num + 1
        # ws.write(row_num, 0, VoucherNo)
        # ws.write(row_num, 1, Date)
        # ws.write(row_num, 2, GrandTotal)
        # ws.write(row_num, 3, ApplicableTaxRate)
        # ws.write(row_num, 4, PlaceOfSupply)
        # ws.write(row_num, 5, Rate)
        # ws.write(row_num, 6, taxable_value)
        # ws.write(row_num, 7, '0.0')


def atadj_excel(wb, atadj_data):
    ws = wb.add_sheet("atadj")

    # orange custome color
    xlwt.add_palette_colour("custom_colour", 0x21)
    wb.set_colour_RGB(0x21, 248, 203, 173)

    # blue custome color1
    xlwt.add_palette_colour("custom_colour1", 0x22)
    wb.set_colour_RGB(0x22, 0, 112, 192)

    # light blue custome color1
    xlwt.add_palette_colour("custom_colour2", 0x23)
    wb.set_colour_RGB(0x23, 180, 198, 231)

    # freeze first 3 row
    ws.set_panes_frozen(True)
    ws.set_horz_split_pos(4)

    # adjust the row width
    ws.col(0).width = int(100)*int(100)
    ws.col(1).width = 100*90
    ws.col(4).width = 100*90

    # adjust the row height
    ws.row(3).height_mismatch = True
    ws.row(3).height = 100*6
    ws.row(0).height = 300

    # header style
    header_style = xlwt.XFStyle()

    # column value alighn center
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    header_style.alignment = center
    header_style.alignment.wrap = 1

    # borders
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN

    # header font
    font = xlwt.Font()
    font.bold = True
    font.height = 11 * 20
    font.colour_index = 1
    header_style.font = font
    header_style.borders = borders

    # header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    header_style.pattern = pattern

    # second header style
    seond_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    seond_header_style.pattern = pattern
    seond_header_style.borders = borders
    seond_header_style.alignment = center
    font_1 = xlwt.Font()
    font_1.bold = True
    font_1.height = 11 * 20
    font_1.colour_index = 0
    seond_header_style.font = font_1

    # color light orange second header style
    seond_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    seond_header_style.pattern = pattern
    seond_header_style.borders = borders
    seond_header_style.alignment = center
    font_1 = xlwt.Font()
    font_1.height = 11 * 20
    font_1.colour_index = 0
    seond_header_style.font = font_1

 # color light blue third header style
    third_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour2']
    third_header_style.pattern = pattern
    third_header_style.borders = borders
    third_header_style.alignment = center
    third_header_style.font = font_1

    # header
    ws.write(0, 0, "Summary For Advance Adjusted (11B)  ", header_style)

    # sub header font
    subheader_style = xlwt.XFStyle()
    subheader_style.font = font

    # column value alighn center
    center.horz = Alignment.HORZ_CENTER
    subheader_style.alignment = center

    # sub header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    subheader_style.pattern = pattern

    subheader_style.borders = borders

    # sub header
    # ======= Label ==========
    ws.write(1, 0, "", subheader_style)
    ws.write(1, 1, "", subheader_style)
    ws.write(1, 2, "", subheader_style)
    ws.write(1, 3, "Total Advance Adjusted", subheader_style)
    ws.write(1, 4, "Total Cess", subheader_style)
    # ws.write(1, 8, "Total Cess", subheader_style)
    # ======= Label value ==========
    # sub header value font
    subheader_value_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.height = 11 * 20
    subheader_value_style.borders = borders
    subheader_value_style.font = font

    no_of_reciepts = ""
    no_of_invoices = ""
    total_invoice_value = ""
    total_taxable_value = ""
    total_cess = '0.0'
    ws.write(2, 0, "", subheader_value_style)
    ws.write(2, 1, "", subheader_value_style)
    ws.write(2, 2, "", subheader_value_style)
    ws.write(2, 3, "", subheader_value_style)
    ws.write(2, 4, "", subheader_value_style)

    # column header style
    column_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    column_header_style.pattern = pattern
    column_header_style.font = font

    # column value style
    al = Alignment()
    al.horz = Alignment.HORZ_CENTER
    column_header_style.alignment = al
    column_header_style.alignment.wrap = 1

    # column header names, you can use your own headers here
    columns = ['Place Of Supply', 'Applicable % of Tax Rate',
               'Rate', 'Gross Advance Adjusted', 'Cess Amount']

    # Sheet header, first row
    row_num = 3
    # font_style = xlwt.XFStyle()
    # write column headers in sheet
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], column_header_style)

        # row_num = row_num + 1
        # ws.write(row_num, 0, VoucherNo)
        # ws.write(row_num, 1, Date)
        # ws.write(row_num, 2, GrandTotal)
        # ws.write(row_num, 3, ApplicableTaxRate)
        # ws.write(row_num, 4, PlaceOfSupply)
        # ws.write(row_num, 5, Rate)
        # ws.write(row_num, 6, taxable_value)
        # ws.write(row_num, 7, '0.0')


def atadja_excel(wb, exemp_data):
    ws = wb.add_sheet("atadja")

    # orange custome color
    xlwt.add_palette_colour("custom_colour", 0x21)
    wb.set_colour_RGB(0x21, 248, 203, 173)

    # blue custome color1
    xlwt.add_palette_colour("custom_colour1", 0x22)
    wb.set_colour_RGB(0x22, 0, 112, 192)

    # light blue custome color1
    xlwt.add_palette_colour("custom_colour2", 0x23)
    wb.set_colour_RGB(0x23, 180, 198, 231)

    # freeze first 3 row
    ws.set_panes_frozen(True)
    ws.set_horz_split_pos(4)

    # adjust the row width
    ws.col(0).width = int(100)*int(100)
    ws.col(1).width = 100*90
    ws.col(4).width = 100*90

    # adjust the row height
    ws.row(3).height_mismatch = True
    ws.row(3).height = 100*6
    ws.row(0).height = 300

    # header style
    header_style = xlwt.XFStyle()

    # column value alighn center
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    header_style.alignment = center
    header_style.alignment.wrap = 1

    # borders
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN

    # header font
    font = xlwt.Font()
    font.bold = True
    font.height = 11 * 20
    font.colour_index = 1
    header_style.font = font
    header_style.borders = borders

    # header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    header_style.pattern = pattern

    # second header style
    seond_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    seond_header_style.pattern = pattern
    seond_header_style.borders = borders
    seond_header_style.alignment = center
    font_1 = xlwt.Font()
    font_1.bold = True
    font_1.height = 11 * 20
    font_1.colour_index = 0
    seond_header_style.font = font_1

    # color light orange second header style
    seond_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    seond_header_style.pattern = pattern
    seond_header_style.borders = borders
    seond_header_style.alignment = center
    font_1 = xlwt.Font()
    font_1.height = 11 * 20
    font_1.colour_index = 0
    seond_header_style.font = font_1

 # color light blue third header style
    third_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour2']
    third_header_style.pattern = pattern
    third_header_style.borders = borders
    third_header_style.alignment = center
    third_header_style.font = font_1

    # header
    ws.write(0, 0, "Summary For Amendement Of Adjustment Advances", header_style)
    ws.write_merge(0, 0, 1, 2, 'Original details', seond_header_style)
    ws.write_merge(0, 0, 3, 6, 'Revised Details', third_header_style)

    # sub header font
    subheader_style = xlwt.XFStyle()
    subheader_style.font = font

    # column value alighn center
    center.horz = Alignment.HORZ_CENTER
    subheader_style.alignment = center

    # sub header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    subheader_style.pattern = pattern

    subheader_style.borders = borders

    # sub header
    # ======= Label ==========
    ws.write(1, 0, "", subheader_style)
    ws.write(1, 1, "", subheader_style)
    ws.write(1, 2, "", subheader_style)
    ws.write(1, 3, "", subheader_style)
    ws.write(1, 4, "", subheader_style)
    ws.write(1, 5, "Total Advance Adjusted", subheader_style)
    ws.write(1, 6, "Total Cess", subheader_style)
    # ws.write(1, 8, "Total Cess", subheader_style)
    # ======= Label value ==========
    # sub header value font
    subheader_value_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.height = 11 * 20
    subheader_value_style.borders = borders
    subheader_value_style.font = font

    no_of_reciepts = ""
    no_of_invoices = ""
    total_invoice_value = ""
    total_taxable_value = ""
    total_cess = '0.0'
    ws.write(2, 0, "", subheader_value_style)
    ws.write(2, 1, "", subheader_value_style)
    ws.write(2, 2, "", subheader_value_style)
    ws.write(2, 3, "", subheader_value_style)
    ws.write(2, 4, "", subheader_value_style)
    ws.write(2, 5, "", subheader_value_style)
    ws.write(2, 6, "", subheader_value_style)

    # column header style
    column_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    column_header_style.pattern = pattern
    column_header_style.font = font
    column_header_style.alignment = center
    column_header_style.alignment.wrap = 1

    # l_blue column header style
    l_blue_column_header_style = xlwt.XFStyle()
    pattern1 = xlwt.Pattern()
    pattern1.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern1.pattern_fore_colour = xlwt.Style.colour_map['custom_colour2']
    l_blue_column_header_style.pattern = pattern1
    l_blue_column_header_style.font = font
    l_blue_column_header_style.alignment = center
    l_blue_column_header_style.alignment.wrap = 1

    # column header names, you can use your own headers here
    columns = ['Financial Year', 'Original Month', 'Original Place Of Supply',
               'Applicable % of Tax Rate', 'Rate', 'Gross Advance Adjusted', 'Cess Amount', ]

    # Sheet header, first row
    row_num = 3
    # font_style = xlwt.XFStyle()
    # write column headers in sheet
    for col_num in range(len(columns)):
        if col_num < 3:
            ws.write(row_num, col_num, columns[col_num], column_header_style)
        else:
            ws.write(row_num, col_num,
                     columns[col_num], l_blue_column_header_style)

        # row_num = row_num + 1
        # ws.write(row_num, 0, VoucherNo)
        # ws.write(row_num, 1, Date)
        # ws.write(row_num, 2, GrandTotal)
        # ws.write(row_num, 3, ApplicableTaxRate)
        # ws.write(row_num, 4, PlaceOfSupply)
        # ws.write(row_num, 5, Rate)
        # ws.write(row_num, 6, taxable_value)
        # ws.write(row_num, 7, '0.0')


def exemp_excel(wb, exemp_data):
    ws = wb.add_sheet("exemp")

    # orange custome color
    xlwt.add_palette_colour("custom_colour", 0x21)
    wb.set_colour_RGB(0x21, 248, 203, 173)

    # blue custome color1
    xlwt.add_palette_colour("custom_colour1", 0x22)
    wb.set_colour_RGB(0x22, 0, 112, 192)

    # light blue custome color1
    xlwt.add_palette_colour("custom_colour2", 0x23)
    wb.set_colour_RGB(0x23, 180, 198, 231)

    # freeze first 3 row
    ws.set_panes_frozen(True)
    ws.set_horz_split_pos(4)

    # adjust the row width
    ws.col(0).width = int(100)*int(100)
    ws.col(1).width = 100*90
    ws.col(4).width = 100*90

    # adjust the row height
    ws.row(3).height_mismatch = True
    ws.row(3).height = 100*6
    ws.row(0).height = 300

    # header style
    header_style = xlwt.XFStyle()

    # column value alighn center
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    header_style.alignment = center
    header_style.alignment.wrap = 1

    # borders
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN

    # header font
    font = xlwt.Font()
    font.bold = True
    font.height = 11 * 20
    font.colour_index = 1
    header_style.font = font
    header_style.borders = borders

    # header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    header_style.pattern = pattern

    # second header style
    seond_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    seond_header_style.pattern = pattern
    seond_header_style.borders = borders
    seond_header_style.alignment = center
    font_1 = xlwt.Font()
    font_1.bold = True
    font_1.height = 11 * 20
    font_1.colour_index = 0
    seond_header_style.font = font_1

    # color light orange second header style
    seond_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    seond_header_style.pattern = pattern
    seond_header_style.borders = borders
    seond_header_style.alignment = center
    font_1 = xlwt.Font()
    font_1.height = 11 * 20
    font_1.colour_index = 0
    seond_header_style.font = font_1

 # color light blue third header style
    third_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour2']
    third_header_style.pattern = pattern
    third_header_style.borders = borders
    third_header_style.alignment = center
    third_header_style.font = font_1

    # header
    ws.write(
        0, 0, "Summary For Nil rated, exempted and non GST outward supplies (8)", header_style)

    # sub header font
    subheader_style = xlwt.XFStyle()
    subheader_style.font = font

    # column value alighn center
    center.horz = Alignment.HORZ_CENTER
    subheader_style.alignment = center

    # sub header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    subheader_style.pattern = pattern

    subheader_style.borders = borders

    # sub header
    # ======= Label ==========
    ws.write(1, 0, "", subheader_style)
    ws.write(1, 1, "Total Nil Rated Supplies", subheader_style)
    ws.write(1, 2, "Total Exempted Supplies", subheader_style)
    ws.write(1, 3, "Total Non-GST Supplies", subheader_style)
    # ws.write(1, 8, "Total Cess", subheader_style)
    # ======= Label value ==========
    # sub header value font
    subheader_value_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.height = 11 * 20
    subheader_value_style.borders = borders
    subheader_value_style.font = font

    no_of_reciepts = ""
    no_of_invoices = ""
    total_invoice_value = ""
    total_taxable_value = ""
    total_cess = '0.0'
    ws.write(2, 0, "", subheader_value_style)
    ws.write(2, 1, "", subheader_value_style)
    ws.write(2, 2, "", subheader_value_style)
    ws.write(2, 3, "", subheader_value_style)

    # column header style
    column_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    column_header_style.pattern = pattern
    column_header_style.font = font

    # column value style
    al = Alignment()
    al.horz = Alignment.HORZ_CENTER
    column_header_style.alignment = al
    column_header_style.alignment.wrap = 1

    # column header names, you can use your own headers here
    columns = ['Description', 'Nil Rated Supplies',
               'Exempted(other than nil rated/non GST supply)', 'Non-GST Supplies', ]

    # Sheet header, first row
    row_num = 3
    # font_style = xlwt.XFStyle()
    # write column headers in sheet
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], column_header_style)

        # row_num = row_num + 1
        # ws.write(row_num, 0, VoucherNo)
        # ws.write(row_num, 1, Date)
        # ws.write(row_num, 2, GrandTotal)
        # ws.write(row_num, 3, ApplicableTaxRate)
        # ws.write(row_num, 4, PlaceOfSupply)
        # ws.write(row_num, 5, Rate)
        # ws.write(row_num, 6, taxable_value)
        # ws.write(row_num, 7, '0.0')


def docs_excel(wb, docs_data):
    ws = wb.add_sheet("docs")

    # orange custome color
    xlwt.add_palette_colour("custom_colour", 0x21)
    wb.set_colour_RGB(0x21, 248, 203, 173)

    # blue custome color1
    xlwt.add_palette_colour("custom_colour1", 0x22)
    wb.set_colour_RGB(0x22, 0, 112, 192)

    # light blue custome color1
    xlwt.add_palette_colour("custom_colour2", 0x23)
    wb.set_colour_RGB(0x23, 180, 198, 231)

    # freeze first 3 row
    ws.set_panes_frozen(True)
    ws.set_horz_split_pos(4)

    # adjust the row width
    ws.col(0).width = int(100)*int(100)
    ws.col(1).width = 100*90
    ws.col(4).width = 100*90

    # adjust the row height
    ws.row(3).height_mismatch = True
    ws.row(3).height = 100*6
    ws.row(0).height = 300

    # header style
    header_style = xlwt.XFStyle()

    # column value alighn center
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    header_style.alignment = center
    header_style.alignment.wrap = 1

    # borders
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN

    # header font
    font = xlwt.Font()
    font.bold = True
    font.height = 11 * 20
    font.colour_index = 1
    header_style.font = font
    header_style.borders = borders

    # header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    header_style.pattern = pattern

    # second header style
    seond_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    seond_header_style.pattern = pattern
    seond_header_style.borders = borders
    seond_header_style.alignment = center
    font_1 = xlwt.Font()
    font_1.bold = True
    font_1.height = 11 * 20
    font_1.colour_index = 0
    seond_header_style.font = font_1

    # color light orange second header style
    seond_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    seond_header_style.pattern = pattern
    seond_header_style.borders = borders
    seond_header_style.alignment = center
    font_1 = xlwt.Font()
    font_1.height = 11 * 20
    font_1.colour_index = 0
    seond_header_style.font = font_1

 # color light blue third header style
    third_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour2']
    third_header_style.pattern = pattern
    third_header_style.borders = borders
    third_header_style.alignment = center
    third_header_style.font = font_1

    # header
    ws.write(
        0, 0, "Summary of documents issued during the tax period (13)", header_style)

    # sub header font
    subheader_style = xlwt.XFStyle()
    subheader_style.font = font

    # column value alighn center
    center.horz = Alignment.HORZ_CENTER
    subheader_style.alignment = center

    # sub header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    subheader_style.pattern = pattern

    subheader_style.borders = borders

    # sub header
    # ======= Label ==========
    ws.write(1, 0, "", subheader_style)
    ws.write(1, 1, "", subheader_style)
    ws.write(1, 2, "", subheader_style)
    ws.write(1, 3, "Total Number", subheader_style)
    ws.write(1, 4, "Total Cancelled", subheader_style)
    # ws.write(1, 8, "Total Cess", subheader_style)
    # ======= Label value ==========
    # sub header value font
    subheader_value_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.height = 11 * 20
    subheader_value_style.borders = borders
    subheader_value_style.font = font

    total_Total_num = ""
    total_Total_cancelled = ""
    if not docs_data[-1]['total_Total_num'] == 0:
        total_Total_num = docs_data[-1]['total_Total_num']
    if not docs_data[-1]['total_Total_cancelled'] == 0:
        total_Total_cancelled = docs_data[-1]['total_Total_cancelled']

    ws.write(2, 0, "", subheader_value_style)
    ws.write(2, 1, "", subheader_value_style)
    ws.write(2, 2, "", subheader_value_style)
    ws.write(2, 3, total_Total_num, subheader_value_style)
    ws.write(2, 4, total_Total_cancelled, subheader_value_style)

    # column header style
    column_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    column_header_style.pattern = pattern
    column_header_style.font = font

    # column value style
    al = Alignment()
    al.horz = Alignment.HORZ_CENTER
    column_header_style.alignment = al
    column_header_style.alignment.wrap = 1

    # column header names, you can use your own headers here
    columns = ['Nature of Document', 'Sr. No. From',
               'Sr. No. To', 'Total Number', 'Cancelled', ]

    # Sheet header, first row
    row_num = 3
    # font_style = xlwt.XFStyle()
    # write column headers in sheet
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], column_header_style)

        # font_size_11
    common_style = xlwt.XFStyle()
    common_style.font = font

    del docs_data[-1]
    for i in docs_data:
        try:
            Nature_of_document = i['Nature_of_document']
        except:
            Nature_of_document = ""

        try:
            Sr_no_from = i['Sr_no_from']
        except:
            Sr_no_from = ""

        try:
            Sr_no_to = i['Sr_no_to']
        except:
            Sr_no_to = ""

        try:
            Total_num = i['Total_num']
        except:
            Total_num = ""

        try:
            Total_cancelled = i['Total_cancelled']
        except:
            Total_cancelled = ""

        row_num = row_num + 1
        ws.write(row_num, 0, Nature_of_document, common_style)
        ws.write(row_num, 1, Sr_no_from, common_style)
        ws.write(row_num, 2, Sr_no_to, common_style)
        ws.write(row_num, 3, Total_num, common_style)
        ws.write(row_num, 4, Total_cancelled, common_style)


def master_excel(wb, master_data):
    ws = wb.add_sheet("master")

    # orange custome color
    xlwt.add_palette_colour("custom_colour", 0x21)
    wb.set_colour_RGB(0x21, 248, 203, 173)

    # blue custome color1
    xlwt.add_palette_colour("custom_colour1", 0x22)
    wb.set_colour_RGB(0x22, 0, 112, 192)

    # light blue custome color1
    xlwt.add_palette_colour("custom_colour2", 0x23)
    wb.set_colour_RGB(0x23, 180, 198, 231)

    # freeze first 3 row
    ws.set_panes_frozen(True)
    ws.set_horz_split_pos(1)

    # adjust the row width
    ws.col(0).width = int(100)*int(100)

    # adjust the row height
    ws.row(0).height = 300

    # header style
    header_style = xlwt.XFStyle()

    # column value alighn center
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    header_style.alignment = center

    # borders
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN

    # header font
    font = xlwt.Font()
    font.bold = True
    font.height = 11 * 20
    font.colour_index = 1
    header_style.font = font
    header_style.borders = borders

    # header background color
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour1']
    header_style.pattern = pattern

    # second header style
    seond_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour2']
    seond_header_style.pattern = pattern
    seond_header_style.borders = borders
    seond_header_style.alignment = center
    font_1 = xlwt.Font()
    font_1.bold = True
    font_1.height = 11 * 20
    font_1.colour_index = 0
    seond_header_style.font = font_1

    # color light orange second header style
    seond_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    seond_header_style.pattern = pattern
    seond_header_style.borders = borders
    seond_header_style.alignment = center
    font_1 = xlwt.Font()
    font_1.height = 11 * 20
    font_1.colour_index = 0
    seond_header_style.font = font_1

 # color light blue third header style
    third_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    # pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour2']
    third_header_style.pattern = pattern
    third_header_style.borders = borders
    third_header_style.alignment = center
    third_header_style.font = font_1

    # header
    ws.write(0, 0, "UQC", header_style)
    ws.write(0, 1, "Export Type", header_style)
    ws.write(0, 2, "Reverse Charge/Provisional Assessment", header_style)
    ws.write(0, 3, "Note Type", header_style)
    ws.write(0, 4, "Type", header_style)
    ws.write(0, 5, "Tax Rate", header_style)
    ws.write(0, 6, "POS", header_style)
    ws.write(0, 7, "Invoice Type", header_style)
    ws.write(0, 8, "Nature  of Document", header_style)
    ws.write(0, 9, "UR Type", header_style)
    ws.write(0, 10, "Supply Type ", header_style)
    ws.write(0, 11, "Month", header_style)
    ws.write(0, 12, "Financial Year", header_style)
    ws.write(0, 13, "Differential Percentage", header_style)
    ws.write(0, 14, "POS96", header_style)

    # column header style
    column_header_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['custom_colour']
    column_header_style.pattern = pattern
    column_header_style.font = font

    # column value style
    al = Alignment()
    al.horz = Alignment.HORZ_CENTER
    column_header_style.alignment = al


def sales_gst_excel_data(CompanyID, BranchID, FromDate, ToDate, PriceRounding, UserID):
    PriceRounding = 2
    Total_TaxableValue = 0
    Total_TotalQty = 0

    Total_TotalTaxableAmount = 0
    Total_TotalTax = 0
    Total_SGSTAmount = 0
    Total_CGSTAmount = 0
    Total_IGSTAmount = 0
    Total_KFCAmount = 0
    print(UserID, "UserIDUserIDUserIDUserIDUserID")
    TaxType_Arr = ["GST Intra-state B2C", "Export", "GST Inter-state B2B",
                   "GST Intra-state B2C", "GST Intra-state B2B", "GST"]

    if UserID:
        UserID = UserTable.objects.get(id=UserID).customer.user.pk
        if SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID).exists():
            instances = SalesMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID)
            return_instances = SalesReturnMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate, CreatedUserID=UserID)
            serialized_sales = SalesGSTReportSerializer(instances, many=True, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding,
                                                                                       "FromDate": FromDate, "ToDate": ToDate})

            serialized_return = SalesReturnMasterRestSerializer(return_instances, many=True, context={"CompanyID": CompanyID,
                                                                                                      "PriceRounding": PriceRounding})

            sales_data = serialized_sales.data
            sales_return_data = serialized_return.data

            final_array = []
            # =======

            orderdDict = sales_data
            return_orderdDict = sales_return_data

            jsnDatas = convertOrderdDict(orderdDict)
            return_jsnDatas = convertOrderdDict(return_orderdDict)

            party_gstin = ""
            for i in jsnDatas:
                LedgerID = i['LedgerID']
                if AccountLedger.objects.filter(LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID).exists():
                    Particulars = AccountLedger.objects.get(
                        LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID)
                    LedgerName = Particulars.LedgerName
                    if Particulars.AccountGroupUnder == 10:
                        party_gstin = Parties.objects.get(
                            LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID, PartyType="customer", PartyCode=Particulars.LedgerCode).GSTNumber

                dic = {
                    "Date": i['Date'],
                    "VoucherNo": i['VoucherNo'],
                    "VoucherType": "SI",
                    "Particulars": LedgerName,
                    "party_gstin": party_gstin,
                    "TaxType": i['TaxType'],
                    "TotalTax": i['TotalTax'],
                    "SGSTAmount": i['SGSTAmount'],
                    "IGSTAmount": i['IGSTAmount'],
                    "CGSTAmount": i['CGSTAmount'],
                    "CESSAmount": 0,
                    "KFCAmount": i['KFCAmount'],
                    "TotalTaxableAmount": i['TotalTaxableAmount'],
                }
                if float(i['TotalTax']) > 0:
                    print("SALEMASTER", i['TotalTax'])
                    final_array.append(dic)

            party_gstin = ""
            for i in return_jsnDatas:
                LedgerID = i['LedgerID']
                if AccountLedger.objects.filter(LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID).exists():
                    LedgerName = Particulars.LedgerName
                    Particulars = AccountLedger.objects.get(
                        LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID)
                    if Particulars.AccountGroupUnder == 10:
                        party_gstin = Parties.objects.get(
                            LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID, PartyType="customer", PartyCode=Particulars.LedgerCode).GSTNumber
                try:
                    KFCAmount = int(i['KFCAmount'])
                except:
                    KFCAmount = 0

                TotalTaxableAmount = float(i['TotalTaxableAmount'])
                if TotalTaxableAmount:
                    TotalTaxableAmount = float(i['TotalTaxableAmount'])
                else:
                    TotalTaxableAmount = 0

                dic = {
                    "Date": i['VoucherDate'],
                    "VoucherNo": i['VoucherNo'],
                    "VoucherType": "SR",
                    "Particulars": LedgerName,
                    "party_gstin": party_gstin,
                    "TaxType": i['TaxType'],
                    "TotalTax": int(i['TotalTax']*-1),
                    "SGSTAmount": int(i['SGSTAmount']*-1),
                    "IGSTAmount": int(i['IGSTAmount']*-1),
                    "CGSTAmount": int(i['CGSTAmount']*-1),
                    "CESSAmount": 0,
                    "KFCAmount": KFCAmount*-1,
                    "TotalTaxableAmount": TotalTaxableAmount*-1,
                }
                if float(i['TotalTax']) > 0:
                    final_array.append(dic)
                    print("SALERETURN.........", i['TotalTax'])

            for i in final_array:
                Total_TotalTaxableAmount += float(i['TotalTaxableAmount'])
                Total_TotalTax += float(i['TotalTax'])

                Total_SGSTAmount += float(i['SGSTAmount'])
                Total_CGSTAmount += float(i['CGSTAmount'])
                Total_IGSTAmount += float(i['IGSTAmount'])
                Total_KFCAmount += float(i['KFCAmount'])
            print(final_array, "IF>>>")
            response_data = {
                "StatusCode": 6000,
                "sales_data": final_array,
                "Total_TaxableValue": Total_TaxableValue,
                "Total_TotalQty": Total_TotalQty,
                "Total_TotalTaxableAmount": Total_TotalTaxableAmount,
                "Total_TotalTax": Total_TotalTax,
                "Total_SGSTAmount": Total_SGSTAmount,
                "Total_CGSTAmount": Total_CGSTAmount,
                "Total_IGSTAmount": Total_IGSTAmount,
                "Total_KFCAmount": Total_KFCAmount,
            }
            return response_data

    elif SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
        # if SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
        instances = SalesMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)
        serialized_sales = SalesGSTReportSerializer(instances, many=True, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding,
                                                                                   "FromDate": FromDate, "ToDate": ToDate})

        # ======
        return_instances = SalesReturnMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate)
        serialized_return = SalesReturnMasterRestSerializer(return_instances, many=True, context={"CompanyID": CompanyID,
                                                                                                  "PriceRounding": PriceRounding})

        sales_data = serialized_sales.data
        sales_return_data = serialized_return.data
        final_array = []
        # =======

        orderdDict = sales_data
        return_orderdDict = sales_return_data

        jsnDatas = convertOrderdDict(orderdDict)
        return_jsnDatas = convertOrderdDict(return_orderdDict)

        for i in jsnDatas:
            LedgerID = i['LedgerID']
            LedgerName = ""
            party_gstin = ""

            if AccountLedger.objects.filter(LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID).exists():
                Particulars = AccountLedger.objects.get(
                    LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID)
                LedgerName = Particulars.LedgerName
                if Particulars.AccountGroupUnder == 10:
                    party_gstin = Parties.objects.get(
                        LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID, PartyType="customer", PartyCode=Particulars.LedgerCode).GSTNumber
            dic = {
                "Date": i['Date'],
                "VoucherNo": i['VoucherNo'],
                "VoucherType": "SI",
                "Particulars": LedgerName,
                "party_gstin": party_gstin,
                "TaxType": i['TaxType'],
                "TotalTax": float(i['TotalTax']),
                "SGSTAmount": float(i['SGSTAmount']),
                "IGSTAmount": float(i['IGSTAmount']),
                "CGSTAmount": float(i['CGSTAmount']),
                "CESSAmount": 0,
                "KFCAmount": float(i['KFCAmount']),
                "TotalTaxableAmount": float(i['TotalTaxableAmount']),
            }
            if float(i['TotalTax']) > 0:
                final_array.append(dic)

        for i in return_jsnDatas:
            LedgerID = i['LedgerID']

            LedgerName = ""
            party_gstin = ""
            if AccountLedger.objects.filter(LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID).exists():
                Particulars = AccountLedger.objects.get(
                    LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID)
                LedgerName = Particulars.LedgerName
                if Particulars.AccountGroupUnder == 10:
                    party_gstin = Parties.objects.get(
                        LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID, PartyType="customer", PartyCode=Particulars.LedgerCode).GSTNumber
            try:
                KFCAmount = int(i['KFCAmount'])
            except:
                KFCAmount = 0

            TotalTaxableAmount = float(i['TotalTaxableAmount'])
            if TotalTaxableAmount:
                TotalTaxableAmount = float(i['TotalTaxableAmount'])
            else:
                TotalTaxableAmount = 0

            dic = {
                "Date": i['VoucherDate'],
                "VoucherNo": i['VoucherNo'],
                "VoucherType": "SR",
                "Particulars": LedgerName,
                "party_gstin": party_gstin,
                "TaxType": i['TaxType'],
                "TotalTax": int(i['TotalTax']*-1),
                "SGSTAmount": int(i['SGSTAmount']*-1),
                "IGSTAmount": int(i['IGSTAmount']*-1),
                "CGSTAmount": int(i['CGSTAmount']*-1),
                "CESSAmount": 0,
                "KFCAmount": KFCAmount*-1,
                "TotalTaxableAmount": TotalTaxableAmount*-1,
            }
            if float(i['TotalTax']) > 0:
                final_array.append(dic)

        for i in final_array:
            Total_TotalTaxableAmount += float(i['TotalTaxableAmount'])
            Total_TotalTax += float(i['TotalTax'])

            Total_SGSTAmount += float(i['SGSTAmount'])
            Total_CGSTAmount += float(i['CGSTAmount'])
            Total_IGSTAmount += float(i['IGSTAmount'])
            Total_KFCAmount += float(i['KFCAmount'])
        print(final_array, 'final_array')
        response_data = {
            "StatusCode": 6000,
            "sales_data": final_array,
            "Total_TaxableValue": Total_TaxableValue,
            "Total_TotalQty": Total_TotalQty,
            "Total_TotalTaxableAmount": Total_TotalTaxableAmount,
            "Total_TotalTax": Total_TotalTax,
            "Total_SGSTAmount": Total_SGSTAmount,
            "Total_CGSTAmount": Total_CGSTAmount,
            "Total_IGSTAmount": Total_IGSTAmount,
            "Total_KFCAmount": Total_KFCAmount,
        }
        return response_data


def export_to_excel_sales_gst(wb, data, FromDate, ToDate):
    ws = wb.add_sheet("Purchase GST Report")

    columns = ['Date', 'Voucher No', 'Particulars', 'GSTIN/UIN', 'Voucher Type', 'Tax Type',
               'Taxable Amount', 'SGST', 'CGST', 'IGST', 'Cess', 'KFC', 'Total Tax Amount']
    row_num = 0
    # write column headers in sheet

    # xl sheet styles
    # header font
    font = xlwt.Font()
    font.bold = True
    font.height = 11 * 20

    sub_header_style = xlwt.XFStyle()
    sub_header_style.font = font

    total_values_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True
    total_values_style.num_format_str = '0.00'
    total_values_style.font = font

    total_label_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True
    font.colour_index = 2
    total_label_style.font = font

    value_decimal_style = xlwt.XFStyle()
    value_decimal_style.num_format_str = '0.00'

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], sub_header_style)

    data_col = 0
    data_row = 1
    SlNo = 1

    print(data['sales_data'], 'oppppppppppppopopopo')
    Total_TotalTaxableAmount = data['Total_TotalTaxableAmount']
    Total_SGSTAmount = data['Total_SGSTAmount']
    Total_CGSTAmount = data['Total_CGSTAmount']
    Total_IGSTAmount = data['Total_IGSTAmount']

    Total_KFCAmount = data['Total_KFCAmount']
    Total_TotalTax = data['Total_TotalTax']

    for j in data['sales_data']:
        KFCAmount = j['KFCAmount']
        SGSTAmount = j['SGSTAmount']
        CGSTAmount = j['CGSTAmount']
        IGSTAmount = j['IGSTAmount']
        TotalTax = j['TotalTax']
        TotalTaxableAmount = j['TotalTaxableAmount']

        print(type(KFCAmount), 'KFCAmount')
        ws.write(data_row, 0, j['Date'])
        ws.write(data_row, 1, j['VoucherNo'])
        ws.write(data_row, 2, j['Particulars'])
        ws.write(data_row, 3, j['party_gstin'])
        ws.write(data_row, 4, j['VoucherType'])
        ws.write(data_row, 5, j['TaxType'])
        ws.write(data_row, 6, TotalTaxableAmount, value_decimal_style)
        ws.write(data_row, 7, SGSTAmount, value_decimal_style)
        ws.write(data_row, 8, CGSTAmount, value_decimal_style)
        ws.write(data_row, 9, IGSTAmount, value_decimal_style)
        ws.write(data_row, 10, 0, value_decimal_style)
        ws.write(data_row, 11, KFCAmount, value_decimal_style)
        ws.write(data_row, 12, TotalTax, value_decimal_style)
        data_row += 1
    print(data_row, "&&&&&&&&&&&")
    ws.write(data_row, 5, "Total", total_label_style)
    ws.write(data_row, 6, Total_TotalTaxableAmount, total_values_style)
    ws.write(data_row, 7, Total_SGSTAmount, total_values_style)
    ws.write(data_row, 8, Total_CGSTAmount, total_values_style)
    ws.write(data_row, 9, Total_IGSTAmount, total_values_style)
    ws.write(data_row, 10, 0, total_values_style)
    ws.write(data_row, 11, Total_KFCAmount, total_values_style)
    ws.write(data_row, 12, Total_TotalTax, total_values_style)



def taxSummary_OutwardSupplies(Heading, GST_Treatment_ids, CompanyID, BranchID, FromDate, ToDate):
    total_tax_sale = 0
    total_tax_sale_return = 0
    total_tax_amount_sale = 0
    total_tax_amount_sale_return = 0
    total_sale_igst = 0
    total_sale_cgst = 0
    total_sale_sgst = 0
    total_sale_return_igst = 0
    total_sale_return_cgst = 0
    total_sale_return_sgst = 0
    outward_supplies = []
    if SalesMaster.objects.filter(GST_Treatment__in=GST_Treatment_ids, CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
        instances = SalesMaster.objects.filter(
            GST_Treatment__in=GST_Treatment_ids, CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)

        total_tax_amount_sale = instances.aggregate(Sum('TotalTaxableAmount'))[
            'TotalTaxableAmount__sum']

        total_sale_igst = instances.aggregate(Sum('SGSTAmount'))[
            'SGSTAmount__sum']
        total_sale_cgst = instances.aggregate(Sum('CGSTAmount'))[
            'CGSTAmount__sum']
        total_sale_sgst = instances.aggregate(Sum('IGSTAmount'))[
            'IGSTAmount__sum']

        print(total_tax_amount_sale, "total_tax_amount_sale")
    if SalesReturnMaster.objects.filter(GST_Treatment__in=GST_Treatment_ids, CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate).exists():
        instances = SalesReturnMaster.objects.filter(
            GST_Treatment__in=GST_Treatment_ids, CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate)

        total_tax_amount_sale_return = instances.aggregate(Sum('TotalTaxableAmount'))[
            'TotalTaxableAmount__sum']
        print(total_tax_amount_sale_return, "total_tax_amount_sale_return")
        total_sale_return_igst = instances.aggregate(Sum('SGSTAmount'))[
            'SGSTAmount__sum']
        total_sale_return_cgst = instances.aggregate(Sum('CGSTAmount'))[
            'CGSTAmount__sum']
        total_sale_return_sgst = instances.aggregate(Sum('IGSTAmount'))[
            'IGSTAmount__sum']

    registerd_TaxableAmount = total_tax_amount_sale - total_tax_amount_sale_return
    registerd_IGST = total_sale_igst - total_sale_return_igst
    registerd_CGST = total_sale_cgst - total_sale_return_cgst
    registerd_SGST = total_sale_sgst - total_sale_return_sgst
    registerd_TotalTax = registerd_IGST + registerd_CGST + registerd_SGST
    dic = {
        'Heading': Heading,
        'TaxableAmount': registerd_TaxableAmount,
        'IGST': registerd_IGST,
        'CGST': registerd_CGST,
        'SGST': registerd_SGST,
        'TotalTax': registerd_TotalTax,
    }
    return dic


def taxSummary_InwardSupplies(Heading, GST_Treatment_ids, CompanyID, BranchID, FromDate, ToDate):
    total_tax_sale = 0
    total_tax_sale_return = 0
    total_tax_amount_sale = 0
    total_tax_amount_sale_return = 0
    total_sale_igst = 0
    total_sale_cgst = 0
    total_sale_sgst = 0
    total_sale_return_igst = 0
    total_sale_return_cgst = 0
    total_sale_return_sgst = 0
    outward_supplies = []
    if PurchaseMaster.objects.filter(GST_Treatment__in=GST_Treatment_ids, CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
        instances = PurchaseMaster.objects.filter(
            GST_Treatment__in=GST_Treatment_ids, CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)

        total_tax_amount_sale = instances.aggregate(Sum('TotalTaxableAmount'))[
            'TotalTaxableAmount__sum']

        total_sale_igst = instances.aggregate(Sum('SGSTAmount'))[
            'SGSTAmount__sum']
        total_sale_cgst = instances.aggregate(Sum('CGSTAmount'))[
            'CGSTAmount__sum']
        total_sale_sgst = instances.aggregate(Sum('IGSTAmount'))[
            'IGSTAmount__sum']

        print(total_tax_amount_sale, "total_tax_amount_sale")
    if PurchaseReturnMaster.objects.filter(GST_Treatment__in=GST_Treatment_ids, CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate).exists():
        instances = PurchaseReturnMaster.objects.filter(
            GST_Treatment__in=GST_Treatment_ids, CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate)

        total_tax_amount_sale_return = instances.aggregate(Sum('TotalTaxableAmount'))[
            'TotalTaxableAmount__sum']
        print(total_tax_amount_sale_return, "total_tax_amount_sale_return")
        total_sale_return_igst = instances.aggregate(Sum('SGSTAmount'))[
            'SGSTAmount__sum']
        total_sale_return_cgst = instances.aggregate(Sum('CGSTAmount'))[
            'CGSTAmount__sum']
        total_sale_return_sgst = instances.aggregate(Sum('IGSTAmount'))[
            'IGSTAmount__sum']

    registerd_TaxableAmount = total_tax_amount_sale - total_tax_amount_sale_return
    registerd_IGST = total_sale_igst - total_sale_return_igst
    registerd_CGST = total_sale_cgst - total_sale_return_cgst
    registerd_SGST = total_sale_sgst - total_sale_return_sgst
    registerd_TotalTax = registerd_IGST + registerd_CGST + registerd_SGST
    dic = {
        'Heading': Heading,
        'TaxableAmount': registerd_TaxableAmount,
        'IGST': registerd_IGST,
        'CGST': registerd_CGST,
        'SGST': registerd_SGST,
        'TotalTax': registerd_TotalTax,
    }
    return dic


def zeroRated_taxSummary_OutwardSupplies(Heading, GST_Treatment_ids, CompanyID, BranchID, FromDate, ToDate):
    total_tax_sale = 0
    total_tax_sale_return = 0
    total_tax_amount_sale = 0
    total_tax_amount_sale_return = 0
    total_sale_igst = 0
    total_sale_cgst = 0
    total_sale_sgst = 0
    total_sale_return_igst = 0
    total_sale_return_cgst = 0
    total_sale_return_sgst = 0
    outward_supplies = []
    if SalesMaster.objects.filter(GST_Treatment__in=GST_Treatment_ids, CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
        instances = SalesMaster.objects.filter(
            GST_Treatment__in=GST_Treatment_ids, CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)

        total_tax_amount_sale = instances.aggregate(Sum('TotalTaxableAmount'))[
            'TotalTaxableAmount__sum']

        total_sale_igst = instances.aggregate(Sum('SGSTAmount'))[
            'SGSTAmount__sum']
        total_sale_cgst = instances.aggregate(Sum('CGSTAmount'))[
            'CGSTAmount__sum']
        total_sale_sgst = instances.aggregate(Sum('IGSTAmount'))[
            'IGSTAmount__sum']
    # zeroRated in Master
    if SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
        instances = SalesMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exclude(GST_Treatment__in=GST_Treatment_ids)
        ids = instances.values_list('SalesMasterID', flat=True)
        sum_taxableAmount = SalesDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SalesMasterID__in=ids, SGSTAmount=0, CGSTAmount=0, IGSTAmount=0).aggregate(Sum('TaxableAmount'))[
            'TaxableAmount__sum']
        if sum_taxableAmount:
            total_tax_amount_sale += sum_taxableAmount

    if SalesReturnMaster.objects.filter(GST_Treatment__in=GST_Treatment_ids, CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate).exists():
        instances = SalesReturnMaster.objects.filter(
            GST_Treatment__in=GST_Treatment_ids, CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate)

        total_tax_amount_sale_return = instances.aggregate(Sum('TotalTaxableAmount'))[
            'TotalTaxableAmount__sum']
        print(total_tax_amount_sale_return, "total_tax_amount_sale_return")
        total_sale_return_igst = instances.aggregate(Sum('SGSTAmount'))[
            'SGSTAmount__sum']
        total_sale_return_cgst = instances.aggregate(Sum('CGSTAmount'))[
            'CGSTAmount__sum']
        total_sale_return_sgst = instances.aggregate(Sum('IGSTAmount'))[
            'IGSTAmount__sum']
    # zeroRated in Master
    if SalesReturnMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate).exists():
        instances = SalesReturnMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate).exclude(GST_Treatment__in=GST_Treatment_ids)
        ids = instances.values_list('SalesReturnMasterID', flat=True)
        sum_taxableAmount = SalesReturnDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SalesReturnMasterID__in=ids, SGSTAmount=0, CGSTAmount=0, IGSTAmount=0).aggregate(Sum('TaxableAmount'))[
            'TaxableAmount__sum']
        if sum_taxableAmount:
            total_tax_amount_sale_return += sum_taxableAmount

    registerd_TaxableAmount = total_tax_amount_sale - total_tax_amount_sale_return
    registerd_IGST = total_sale_igst - total_sale_return_igst
    registerd_CGST = total_sale_cgst - total_sale_return_cgst
    registerd_SGST = total_sale_sgst - total_sale_return_sgst
    registerd_TotalTax = registerd_IGST + registerd_CGST + registerd_SGST
    dic = {
        'Heading': Heading,
        'TaxableAmount': registerd_TaxableAmount,
        'IGST': registerd_IGST,
        'CGST': registerd_CGST,
        'SGST': registerd_SGST,
        'TotalTax': registerd_TotalTax,
    }
    return dic


def zeroRated_taxSummary_InwardSupplies(Heading, GST_Treatment_ids, CompanyID, BranchID, FromDate, ToDate):
    total_tax_sale = 0
    total_tax_sale_return = 0
    total_tax_amount_sale = 0
    total_tax_amount_sale_return = 0
    total_sale_igst = 0
    total_sale_cgst = 0
    total_sale_sgst = 0
    total_sale_return_igst = 0
    total_sale_return_cgst = 0
    total_sale_return_sgst = 0
    outward_supplies = []
    if PurchaseMaster.objects.filter(GST_Treatment__in=GST_Treatment_ids, CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
        instances = PurchaseMaster.objects.filter(
            GST_Treatment__in=GST_Treatment_ids, CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)

        total_tax_amount_sale = instances.aggregate(Sum('TotalTaxableAmount'))[
            'TotalTaxableAmount__sum']

        total_sale_igst = instances.aggregate(Sum('SGSTAmount'))[
            'SGSTAmount__sum']
        total_sale_cgst = instances.aggregate(Sum('CGSTAmount'))[
            'CGSTAmount__sum']
        total_sale_sgst = instances.aggregate(Sum('IGSTAmount'))[
            'IGSTAmount__sum']
    # zeroRated in Master
    if PurchaseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
        instances = PurchaseMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exclude(GST_Treatment__in=GST_Treatment_ids)
        ids = instances.values_list('PurchaseMasterID', flat=True)
        sum_taxableAmount = PurchaseDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PurchaseMasterID__in=ids, SGSTAmount=0, CGSTAmount=0, IGSTAmount=0).aggregate(Sum('TaxableAmount'))[
            'TaxableAmount__sum']
        if sum_taxableAmount:
            total_tax_amount_sale += sum_taxableAmount

    if PurchaseReturnMaster.objects.filter(GST_Treatment__in=GST_Treatment_ids, CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate).exists():
        instances = PurchaseReturnMaster.objects.filter(
            GST_Treatment__in=GST_Treatment_ids, CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate)

        total_tax_amount_sale_return = instances.aggregate(Sum('TotalTaxableAmount'))[
            'TotalTaxableAmount__sum']
        print(total_tax_amount_sale_return, "total_tax_amount_sale_return")
        total_sale_return_igst = instances.aggregate(Sum('SGSTAmount'))[
            'SGSTAmount__sum']
        total_sale_return_cgst = instances.aggregate(Sum('CGSTAmount'))[
            'CGSTAmount__sum']
        total_sale_return_sgst = instances.aggregate(Sum('IGSTAmount'))[
            'IGSTAmount__sum']
    # zeroRated in Return Master
    if PurchaseReturnMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate).exists():
        instances = PurchaseReturnMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate).exclude(GST_Treatment__in=GST_Treatment_ids)
        ids = instances.values_list('PurchaseReturnMasterID', flat=True)
        sum_taxableAmount = PurchaseReturnDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PurchaseReturnMasterID__in=ids, SGSTAmount=0, CGSTAmount=0, IGSTAmount=0).aggregate(Sum('TaxableAmount'))[
            'TaxableAmount__sum']
        if sum_taxableAmount:
            total_tax_amount_sale_return += sum_taxableAmount
        print(total_tax_amount_sale, total_tax_amount_sale_return,
              'zeroRated in Return Master')

    registerd_TaxableAmount = total_tax_amount_sale - total_tax_amount_sale_return
    registerd_IGST = total_sale_igst - total_sale_return_igst
    registerd_CGST = total_sale_cgst - total_sale_return_cgst
    registerd_SGST = total_sale_sgst - total_sale_return_sgst
    registerd_TotalTax = registerd_IGST + registerd_CGST + registerd_SGST
    dic = {
        'Heading': Heading,
        'TaxableAmount': registerd_TaxableAmount,
        'IGST': registerd_IGST,
        'CGST': registerd_CGST,
        'SGST': registerd_SGST,
        'TotalTax': registerd_TotalTax,
    }
    return dic


def vat_taxSummary_OutwardSupplies(Heading, VAT_Treatment_ids, CompanyID, BranchID, FromDate, ToDate):
    total_tax_sale = 0
    total_tax_sale_return = 0
    total_tax_amount_sale = 0
    total_tax_amount_sale_return = 0
    total_sale_vat = 0
    total_sale_return_vat = 0
    outward_supplies = []
    if SalesMaster.objects.filter(VAT_Treatment__in=VAT_Treatment_ids, CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
        instances = SalesMaster.objects.filter(
            VAT_Treatment__in=VAT_Treatment_ids, CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)

        total_tax_amount_sale = instances.aggregate(Sum('TotalTaxableAmount'))[
            'TotalTaxableAmount__sum']

        total_sale_vat = instances.aggregate(Sum('VATAmount'))[
            'VATAmount__sum']
        # total_sale_cgst = instances.aggregate(Sum('CGSTAmount'))[
        #     'CGSTAmount__sum']
        # total_sale_sgst = instances.aggregate(Sum('IGSTAmount'))[
        #     'IGSTAmount__sum']

        # total_sale_vat = total_sale_igst+total_sale_cgst+total_sale_sgst

        print(total_tax_amount_sale, "total_tax_amount_sale")
    if SalesReturnMaster.objects.filter(VAT_Treatment__in=VAT_Treatment_ids, CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate).exists():
        instances = SalesReturnMaster.objects.filter(
            VAT_Treatment__in=VAT_Treatment_ids, CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate)

        total_tax_amount_sale_return = instances.aggregate(Sum('TotalTaxableAmount'))[
            'TotalTaxableAmount__sum']

        total_sale_return_vat = instances.aggregate(Sum('VATAmount'))[
            'VATAmount__sum']
        # total_sale_cgst = instances.aggregate(Sum('CGSTAmount'))[
        #     'CGSTAmount__sum']
        # total_sale_sgst = instances.aggregate(Sum('IGSTAmount'))[
        #     'IGSTAmount__sum']

        # total_sale_return_vat = total_sale_igst+total_sale_cgst+total_sale_sgst

    registerd_TaxableAmount = total_tax_amount_sale - total_tax_amount_sale_return
    registerd_VAT = total_sale_vat - total_sale_return_vat
    dic = {
        'Heading': Heading,
        'TaxableAmount': registerd_TaxableAmount,
        'VAT': registerd_VAT,
    }
    return dic


def vat_taxSummary_InwardSupplies(Heading, VAT_Treatment_ids, CompanyID, BranchID, FromDate, ToDate):
    total_tax_amount_purchase = 0
    total_tax_amount_purchase_return = 0
    total_purchase_vat = 0
    total_purchase_return_vat = 0
    outward_supplies = []
    if PurchaseMaster.objects.filter(VAT_Treatment__in=VAT_Treatment_ids, CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
        instances = PurchaseMaster.objects.filter(
            VAT_Treatment__in=VAT_Treatment_ids, CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)

        total_tax_amount_purchase = instances.aggregate(Sum('TotalTaxableAmount'))[
            'TotalTaxableAmount__sum']

        # total_sale_igst = instances.aggregate(Sum('SGSTAmount'))[
        #     'SGSTAmount__sum']
        # total_sale_cgst = instances.aggregate(Sum('CGSTAmount'))[
        #     'CGSTAmount__sum']
        # total_sale_sgst = instances.aggregate(Sum('IGSTAmount'))[
        #     'IGSTAmount__sum']
        total_purchase_vat = instances.aggregate(Sum('VATAmount'))[
            'VATAmount__sum']

    if PurchaseReturnMaster.objects.filter(VAT_Treatment__in=VAT_Treatment_ids, CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate).exists():
        instances = PurchaseReturnMaster.objects.filter(
            VAT_Treatment__in=VAT_Treatment_ids, CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate)

        total_tax_amount_purchase_return = instances.aggregate(Sum('TotalTaxableAmount'))[
            'TotalTaxableAmount__sum']
        # total_sale_igst = instances.aggregate(Sum('SGSTAmount'))[
        #     'SGSTAmount__sum']
        # total_sale_cgst = instances.aggregate(Sum('CGSTAmount'))[
        #     'CGSTAmount__sum']
        # total_sale_sgst = instances.aggregate(Sum('IGSTAmount'))[
        #     'IGSTAmount__sum']
        total_purchase_return_vat = instances.aggregate(Sum('VATAmount'))[
            'VATAmount__sum']

    registerd_TaxableAmount = total_tax_amount_purchase - total_tax_amount_purchase_return
    registerd_VAT = total_purchase_vat - total_purchase_return_vat

    dic = {
        'Heading': Heading,
        'TaxableAmount': registerd_TaxableAmount,
        'VAT': registerd_VAT,
    }
    return dic


def vat_zeroRated_taxSummary_OutwardSupplies(Heading, VAT_Treatment_ids, CompanyID, BranchID, FromDate, ToDate):

    total_tax_amount_sale = 0
    total_tax_amount_sale_return = 0
    total_sale_vat = 0
    total_sale_return_vat = 0
    outward_supplies = []

    # zeroRated in Master
    if SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
        instances = SalesMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)
        ids = instances.values_list('SalesMasterID', flat=True)
        # sum_taxableAmount = SalesDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SalesMasterID__in=ids, VATAmount=0).aggregate(Sum('TaxableAmount'))[
        #     'TaxableAmount__sum']
        # print('<<<<<<<<<,', sum_taxableAmount)
        # if sum_taxableAmount:
        #     total_tax_amount_sale += sum_taxableAmount
        details_instances = SalesDetails.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, SalesMasterID__in=ids, VATAmount=0)
        for detail in details_instances:
            product_id = detail.ProductID
            if Product.objects.filter(CompanyID=CompanyID, ProductID=product_id).exists():
                product = Product.objects.get(
                    CompanyID=CompanyID, ProductID=product_id)
                if product.VatID == 1:
                    total_tax_amount_sale += detail.TaxableAmount

    # zeroRated in ReturMaster
    if SalesReturnMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate).exists():
        instances = SalesReturnMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate)
        ids = instances.values_list('SalesReturnMasterID', flat=True)
        sum_taxableAmount = SalesReturnDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SalesReturnMasterID__in=ids, VATAmount=0).aggregate(Sum('TaxableAmount'))[
            'TaxableAmount__sum']
        if sum_taxableAmount:
            total_tax_amount_sale_return += sum_taxableAmount

    registerd_TaxableAmount = total_tax_amount_sale - total_tax_amount_sale_return
    registerd_VAT = total_sale_vat - total_sale_return_vat
    dic = {
        'Heading': Heading,
        'TaxableAmount': registerd_TaxableAmount,
        'VAT': registerd_VAT,
    }
    return dic


def vat_zeroRated_taxSummary_InwardSupplies(Heading, VAT_Treatment_ids, CompanyID, BranchID, FromDate, ToDate):

    total_tax_amount_sale = 0
    total_tax_amount_sale_return = 0
    total_sale_vat = 0
    total_sale_return_vat = 0
    outward_supplies = []

    # zeroRated in Master
    if PurchaseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
        instances = PurchaseMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)
        ids = instances.values_list('PurchaseMasterID', flat=True)
        # sum_taxableAmount = PurchaseDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PurchaseMasterID__in=ids, VATAmount=0).aggregate(Sum('TaxableAmount'))[
        #     'TaxableAmount__sum']
        details_instances = PurchaseDetails.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, PurchaseMasterID__in=ids, VATAmount=0)
        for detail in details_instances:
            product_id = detail.ProductID
            if Product.objects.filter(CompanyID=CompanyID, ProductID=product_id).exists():
                product = Product.objects.get(
                    CompanyID=CompanyID, ProductID=product_id)
                if product.VatID == 1:
                    total_tax_amount_sale += detail.TaxableAmount

        # if sum_taxableAmount:
        #     total_tax_amount_sale += sum_taxableAmount

    # zeroRated in Return Master
    if PurchaseReturnMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate).exists():
        instances = PurchaseReturnMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate)
        ids = instances.values_list('PurchaseReturnMasterID', flat=True)
        sum_taxableAmount = PurchaseReturnDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PurchaseReturnMasterID__in=ids, VATAmount=0).aggregate(Sum('TaxableAmount'))[
            'TaxableAmount__sum']
        if sum_taxableAmount:
            total_tax_amount_sale_return += sum_taxableAmount
        print(total_tax_amount_sale, total_tax_amount_sale_return,
              'zeroRated in Return Master')

    registerd_TaxableAmount = total_tax_amount_sale - total_tax_amount_sale_return
    registerd_VAT = total_sale_vat - total_sale_return_vat
    dic = {
        'Heading': Heading,
        'TaxableAmount': registerd_TaxableAmount,
        'VAT': registerd_VAT,
    }
    return dic


def export_to_excel_sales(wb, data, FromDate, ToDate, title):
    ws = wb.add_sheet("Sales Report")

    columns = ['Voucher No', 'Voucher Date', 'Ledger Name', 'Cash Sales', 'Bank Sales',
               'Credit Sales', 'Gross Amount', 'Total Tax', 'Bill Discount', 'Grand Total', ]
    # write column headers in sheet

    # xl sheet styles

    center = Alignment()
    center.horz = Alignment.HORZ_CENTER

    # header font
    font = xlwt.Font()
    font.bold = True
    font.height = 11 * 20

    sub_header_style = xlwt.XFStyle()
    sub_header_style.font = font

    total_values_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True
    total_values_style.num_format_str = '0.00'
    total_values_style.font = font

    total_label_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True
    font.colour_index = 2
    total_label_style.font = font

    value_decimal_style = xlwt.XFStyle()
    value_decimal_style.num_format_str = '0.00'

    main_title = xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True
    main_title.font = font
    main_title.alignment = center

    ws.write_merge(0, 0, 0, 3, title, main_title)

    row_num = 1
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], sub_header_style)

    data_row = 2

    try:
        data_list = data['new_sales_data']
    except:
        data_list = []

    for j in data_list:
        print(data_row, 'oppppppppppppopopopo')
        try:
            VoucherNo = j['VoucherNo']
        except:
            VoucherNo = '-'
        try:
            Date = j['Date']
        except:
            Date = '-'
        try:
            LedgerName = j['LedgerName']
        except:
            LedgerName = '-'
        try:
            CashSales = j['CashSales']
        except:
            CashSales = '-'
        try:
            BankSales = j['BankSales']
        except:
            BankSales = '-'
        try:
            CreditSales = j['CreditSales']
        except:
            CreditSales = '-'
        try:
            TotalGrossAmt = j['TotalGrossAmt']
        except:
            TotalGrossAmt = '-'
        try:
            TotalTax = j['TotalTax']
        except:
            TotalTax = '-'
        try:
            BillDiscAmt = j['BillDiscAmt']
        except:
            BillDiscAmt = '-'
        try:
            GrandTotal = j['GrandTotal']
        except:
            GrandTotal = '-'

        ws.write(data_row, 0, VoucherNo)
        ws.write(data_row, 1, Date)
        if LedgerName == "Total":
            ws.write(data_row, 2, LedgerName, total_label_style)
        else:
            ws.write(data_row, 2, LedgerName)
        ws.write(data_row, 3, float(CashSales), value_decimal_style)
        ws.write(data_row, 4, float(BankSales), value_decimal_style)
        ws.write(data_row, 5, float(CreditSales), value_decimal_style)
        ws.write(data_row, 6, float(TotalGrossAmt), value_decimal_style)
        ws.write(data_row, 7, float(TotalTax), value_decimal_style)
        ws.write(data_row, 8, float(BillDiscAmt), value_decimal_style)
        ws.write(data_row, 9, float(GrandTotal), value_decimal_style)
        data_row += 1


def sales_excel_data(CompanyID, BranchID, FromDate, ToDate, PriceRounding, UserID, EmployeeID):
    sales_data = []
    Total_netAmt_sale = 0
    Total_tax_sale = 0
    Total_billDiscount_sale = 0
    Total_grandTotal_sale = 0
    Total_cashSales = 0
    Total_bankSales = 0
    Total_creditSales = 0

    if SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
        instances = SalesMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)

        is_filterd = False
        if UserID:
            UserID_id = UserTable.objects.get(id=UserID).customer.user.pk
            instances = instances.filter(CreatedUserID=UserID_id)

            is_filterd = True

        if EmployeeID:
            instances = instances.filter(EmployeeID=EmployeeID)
            is_filterd = True

        # if is_filterd == True and not instances:

        serialized_sales = SalesMasterReportSerializer(instances, many=True, context={"CompanyID": CompanyID, "PriceRounding": int(PriceRounding),
                                                                                      "FromDate": FromDate, "ToDate": ToDate})
        sales_data = serialized_sales.data
        orderdDict = sales_data
        jsnDatas = convertOrderdDict(orderdDict)

        for i in jsnDatas:
            CashSales = i['CashSales']
            BankSales = i['BankSales']
            CreditSales = i['CreditSales']

            Total_cashSales += CashSales
            Total_bankSales += BankSales
            Total_creditSales += CreditSales

        for i_sale in instances:
            Total_netAmt_sale += i_sale.TotalGrossAmt
            Total_tax_sale += i_sale.TotalTax
            Total_billDiscount_sale += i_sale.BillDiscAmt
            Total_grandTotal_sale += i_sale.GrandTotal

    if sales_data:

        # New Design function Start
        sales_jsnDatas = convertOrderdDict(sales_data)
        sales_total = {
            "LedgerName": "Total",
            "CashSales": str(Total_cashSales),
            "BankSales": str(Total_bankSales),
            "CreditSales": str(Total_creditSales),
            "TotalGrossAmt": str(Total_netAmt_sale),
            "TotalTax": str(Total_tax_sale),
            "BillDiscAmt": str(Total_billDiscount_sale),
            "GrandTotal": str(Total_grandTotal_sale),
        }
        sales_jsnDatas.append(sales_total)

        # New Design function End
        print(sales_jsnDatas)
        response_data = {
            "StatusCode": 6000,
            "count": len(instances),
            "sales_data": sales_data,
            "new_sales_data": sales_jsnDatas,
            "sales_total": sales_total,


        }
        return response_data
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "datas not found!",
        }

    return response_data


def salesReturn_excel_data(CompanyID, BranchID, FromDate, ToDate, PriceRounding, UserID, EmployeeID):

    salesReturn_data = []
    Total_netAmt_saleRetn = 0
    Total_tax_saleRetn = 0
    Total_billDiscount_saleRetn = 0
    Total_grandTotal_saleRetn = 0
    Total_cashSalesReturn = 0
    Total_bankSalesReturn = 0
    Total_creditSalesReturn = 0

    if SalesReturnMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate).exists():
        instances_salesReturn = SalesReturnMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate)

        is_filterd = False
        if UserID:
            UserID_id = UserTable.objects.get(id=UserID).customer.user.pk
            instances_salesReturn = instances_salesReturn.filter(
                CreatedUserID=UserID_id)
            is_filterd = True

        if EmployeeID:
            instances_salesReturn = instances_salesReturn.filter(
                EmployeeID=EmployeeID)
            is_filterd = True

        serialized_salesReturn = SalesReturnMasterReportSerializer(instances_salesReturn, many=True, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding,
                                                                                                              "FromDate": FromDate, "ToDate": ToDate})
        salesReturn_data = serialized_salesReturn.data

        orderdDict = salesReturn_data
        jsnDatas = convertOrderdDict(orderdDict)

        for i in jsnDatas:
            CashSalesReturn = i['CashSalesReturn']
            BankSalesReturn = i['BankSalesReturn']
            CreditSalesReturn = i['CreditSalesReturn']

            Total_cashSalesReturn += CashSalesReturn
            Total_bankSalesReturn += BankSalesReturn
            Total_creditSalesReturn += CreditSalesReturn

        for i_saleReturn in instances_salesReturn:
            Total_netAmt_saleRetn += i_saleReturn.TotalGrossAmt
            Total_tax_saleRetn += i_saleReturn.TotalTax
            Total_billDiscount_saleRetn += i_saleReturn.BillDiscAmt
            Total_grandTotal_saleRetn += i_saleReturn.GrandTotal

        salesReturn_jsnDatas = convertOrderdDict(salesReturn_data)

        salesReturn_total = {
            "LedgerName": "Total",
            "CashSalesReturn": Total_cashSalesReturn,
            "BankSalesReturn": Total_bankSalesReturn,
            "CreditSalesReturn": Total_creditSalesReturn,
            "TotalGrossAmt": Total_netAmt_saleRetn,
            "TotalTax": Total_tax_saleRetn,
            "BillDiscAmt": Total_billDiscount_saleRetn,
            "GrandTotal": Total_grandTotal_saleRetn,
        }
        salesReturn_jsnDatas.append(salesReturn_total)
        # New Design function End
        response_data = {
            "StatusCode": 6000,
            "return_count": len(instances_salesReturn),

            "salesReturn_data": salesReturn_data,
            "new_salesReturn_data": salesReturn_jsnDatas,
            "salesReturn_total": salesReturn_total,
        }
        return response_data
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "datas not found!",
        }

    return response_data


def export_to_excel_salesReturn(wb, data, FromDate, ToDate, title):
    ws = wb.add_sheet("SalesRetun Report")

    columns = ['Voucher No', 'Voucher Date', 'Ledger Name', 'Cash Sales', 'Bank Sales',
               'Credit Sales', 'Gross Amount', 'Total Tax', 'Bill Discount', 'Grand Total', ]

    # write column headers in sheet

    # xl sheet styles
    # column value alighn center
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    # header font
    font = xlwt.Font()
    font.bold = True
    font.height = 11 * 20

    sub_header_style = xlwt.XFStyle()
    sub_header_style.font = font

    total_values_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True
    total_values_style.num_format_str = '0.00'
    total_values_style.font = font

    total_label_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True
    font.colour_index = 10
    total_label_style.font = font

    value_decimal_style = xlwt.XFStyle()
    value_decimal_style.num_format_str = '0.00'

    main_title = xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True
    main_title.font = font
    main_title.alignment = center

    ws.write_merge(0, 0, 0, 3, title, main_title)
    row_num = 1
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], sub_header_style)

    data_row = 2

    try:
        data_list = data['new_salesReturn_data']
    except:
        data_list = []

    for j in data_list:
        print(data_row, 'oppppppppppppopopopo')
        try:
            VoucherNo = j['VoucherNo']
        except:
            VoucherNo = '-'
        try:
            Date = j['Date']
        except:
            Date = '-'
        try:
            LedgerName = j['LedgerName']
        except:
            LedgerName = '-'
        try:
            CashSalesReturn = j['CashSalesReturn']
        except:
            CashSalesReturn = '-'
        try:
            BankSalesReturn = j['BankSalesReturn']
        except:
            BankSalesReturn = '-'
        try:
            CreditSalesReturn = j['CreditSalesReturn']
        except:
            CreditSalesReturn = '-'
        try:
            TotalGrossAmt = j['TotalGrossAmt']
        except:
            TotalGrossAmt = '-'
        try:
            TotalTax = j['TotalTax']
        except:
            TotalTax = '-'
        try:
            BillDiscAmt = j['BillDiscAmt']
        except:
            BillDiscAmt = '-'
        try:
            GrandTotal = j['GrandTotal']
        except:
            GrandTotal = '-'

        ws.write(data_row, 0, VoucherNo)
        ws.write(data_row, 1, Date)
        if LedgerName == "Total":
            ws.write(data_row, 2, LedgerName, total_label_style)
        else:
            ws.write(data_row, 2, LedgerName)

        ws.write(data_row, 3, float(CashSalesReturn), value_decimal_style)
        ws.write(data_row, 4, float(BankSalesReturn), value_decimal_style)
        ws.write(data_row, 5, float(CreditSalesReturn), value_decimal_style)
        ws.write(data_row, 6, float(TotalGrossAmt), value_decimal_style)
        ws.write(data_row, 7, float(TotalTax), value_decimal_style)
        ws.write(data_row, 8, float(BillDiscAmt), value_decimal_style)
        ws.write(data_row, 9, float(GrandTotal), value_decimal_style)
        data_row += 1


def taxSummary_excel_data(CompanyID, BranchID, FromDate, ToDate, Type, PriceRounding):
    if Type == "GST":
        # ============== Outward Supplies ============
        outward_supplies = []
        tot_registerd_TaxableAmount = 0
        tot_registerd_IGST = 0
        tot_registerd_CGST = 0
        tot_registerd_SGST = 0
        tot_registerd_TotalTax = 0

        # Registerd Persons
        registerd_persons = taxSummary_OutwardSupplies(
            'Registerd Persons', [0, 1], CompanyID, BranchID, FromDate, ToDate)
        # adding Total
        tot_registerd_TaxableAmount += registerd_persons['TaxableAmount']
        tot_registerd_IGST += registerd_persons['IGST']
        tot_registerd_CGST += registerd_persons['CGST']
        tot_registerd_SGST += registerd_persons['SGST']
        tot_registerd_TotalTax += registerd_persons['TotalTax']

        # Unregistered Persons
        unregisterd_persons = taxSummary_OutwardSupplies(
            'Unregisterd Persons', [2], CompanyID, BranchID, FromDate, ToDate)
        # adding Total
        tot_registerd_TaxableAmount += unregisterd_persons['TaxableAmount']
        tot_registerd_IGST += unregisterd_persons['IGST']
        tot_registerd_CGST += unregisterd_persons['CGST']
        tot_registerd_SGST += unregisterd_persons['SGST']
        tot_registerd_TotalTax += unregisterd_persons['TotalTax']

        # Zero-rated supplies and Deemed Exports
        zeroRated_taxSummary = zeroRated_taxSummary_OutwardSupplies(
            'Zero-rated supplies and Deemed Exports', [6, 4], CompanyID, BranchID, FromDate, ToDate)
        # adding Total
        tot_registerd_TaxableAmount += zeroRated_taxSummary['TaxableAmount']
        tot_registerd_IGST += zeroRated_taxSummary['IGST']
        tot_registerd_CGST += zeroRated_taxSummary['CGST']
        tot_registerd_SGST += zeroRated_taxSummary['SGST']
        tot_registerd_TotalTax += zeroRated_taxSummary['TotalTax']

        outward_supplies.append(registerd_persons)
        outward_supplies.append(unregisterd_persons)
        outward_supplies.append(zeroRated_taxSummary)
        dic = {
            'Heading': 'Total',
            'TaxableAmount': tot_registerd_TaxableAmount,
            'IGST': tot_registerd_IGST,
            'CGST': tot_registerd_CGST,
            'SGST': tot_registerd_SGST,
            'TotalTax': tot_registerd_TotalTax,
        }
        # append Total
        outward_supplies.append(dic)

        # ============== Inward Supplies ============
        inward_supplies = []
        tot_registerd_TaxableAmount = 0
        tot_registerd_IGST = 0
        tot_registerd_CGST = 0
        tot_registerd_SGST = 0
        tot_registerd_TotalTax = 0
        # Registerd Persons
        registerd_persons = taxSummary_InwardSupplies(
            'Registerd Persons', [0, 1], CompanyID, BranchID, FromDate, ToDate)
        # adding Total
        tot_registerd_TaxableAmount += registerd_persons['TaxableAmount']
        tot_registerd_IGST += registerd_persons['IGST']
        tot_registerd_CGST += registerd_persons['CGST']
        tot_registerd_SGST += registerd_persons['SGST']
        tot_registerd_TotalTax += registerd_persons['TotalTax']

        # Unregistered Persons
        unregisterd_persons = taxSummary_InwardSupplies(
            'Unregisterd Persons', [2], CompanyID, BranchID, FromDate, ToDate)
        # adding Total
        tot_registerd_TaxableAmount += unregisterd_persons['TaxableAmount']
        tot_registerd_IGST += unregisterd_persons['IGST']
        tot_registerd_CGST += unregisterd_persons['CGST']
        tot_registerd_SGST += unregisterd_persons['SGST']
        tot_registerd_TotalTax += unregisterd_persons['TotalTax']

        # Zero-rated supplies and Deemed Exports
        zeroRated_taxSummary = zeroRated_taxSummary_InwardSupplies(
            'Zero-rated supplies and Deemed Exports', [6, 4], CompanyID, BranchID, FromDate, ToDate)
        # adding Total
        tot_registerd_TaxableAmount += zeroRated_taxSummary['TaxableAmount']
        tot_registerd_IGST += zeroRated_taxSummary['IGST']
        tot_registerd_CGST += zeroRated_taxSummary['CGST']
        tot_registerd_SGST += zeroRated_taxSummary['SGST']
        tot_registerd_TotalTax += zeroRated_taxSummary['TotalTax']

        inward_supplies.append(registerd_persons)
        inward_supplies.append(unregisterd_persons)
        inward_supplies.append(zeroRated_taxSummary)
        dic = {
            'Heading': "Total",
            'TaxableAmount': tot_registerd_TaxableAmount,
            'IGST': tot_registerd_IGST,
            'CGST': tot_registerd_CGST,
            'SGST': tot_registerd_SGST,
            'TotalTax': tot_registerd_TotalTax,
        }
        # append Total
        inward_supplies.append(dic)

        # Add TotalTax Due
        due_TaxableAmount = outward_supplies[3]['TaxableAmount'] - \
            inward_supplies[3]['TaxableAmount']
        due_IGST = outward_supplies[3]['IGST'] - inward_supplies[3]['IGST']
        due_CGST = outward_supplies[3]['CGST'] - inward_supplies[3]['CGST']
        due_SGST = outward_supplies[3]['SGST'] - inward_supplies[3]['SGST']
        due_TotalTax = outward_supplies[3]['TotalTax'] - \
            inward_supplies[3]['TaxableAmount']
        due_Amount = {
            'due_TaxableAmount': due_TaxableAmount,
            'due_IGST': due_IGST,
            'due_CGST': due_CGST,
            'due_SGST': due_SGST,
            'due_TotalTax': due_TotalTax,
        }
        response_data = {
            "StatusCode": 6000,
            "outward_supplies": outward_supplies,
            "inward_supplies": inward_supplies,
            "due_Amount": due_Amount,
        }

        return response_data
    if Type == "VAT":
        # ============== Outward Supplies ============
        outward_supplies = []
        tot_registerd_TaxableAmount = 0
        tot_registerd_VAT = 0

        # Registerd Persons
        registerd_persons = vat_taxSummary_OutwardSupplies(
            'Registerd Persons', [0], CompanyID, BranchID, FromDate, ToDate)
        # adding Total
        tot_registerd_TaxableAmount += registerd_persons['TaxableAmount']
        tot_registerd_VAT += registerd_persons['VAT']

        # Unregistered Persons
        unregisterd_persons = vat_taxSummary_OutwardSupplies(
            'Unregisterd Persons', [1], CompanyID, BranchID, FromDate, ToDate)
        # adding Total
        tot_registerd_TaxableAmount += unregisterd_persons['TaxableAmount']
        tot_registerd_VAT += unregisterd_persons['VAT']

        # Zero-rated supplies and Deemed Exports
        zeroRated_taxSummary = vat_zeroRated_taxSummary_OutwardSupplies(
            'Zero-rated supplies and Deemed Exports', [None], CompanyID, BranchID, FromDate, ToDate)
        # adding Total
        tot_registerd_TaxableAmount += zeroRated_taxSummary['TaxableAmount']
        tot_registerd_VAT += zeroRated_taxSummary['VAT']

        outward_supplies.append(registerd_persons)
        outward_supplies.append(unregisterd_persons)
        outward_supplies.append(zeroRated_taxSummary)
        dic = {
            'Heading': "Total",
            'TaxableAmount': tot_registerd_TaxableAmount,
            'VAT': tot_registerd_VAT,
        }
        # append Total
        outward_supplies.append(dic)

        # ============== Inward Supplies ============
        inward_supplies = []
        tot_registerd_TaxableAmount = 0
        tot_registerd_VAT = 0
        tot_registerd_TotalTax = 0
        # Registerd Persons
        registerd_persons = vat_taxSummary_InwardSupplies(
            'Registerd Persons', [0], CompanyID, BranchID, FromDate, ToDate)
        # adding Total
        tot_registerd_TaxableAmount += registerd_persons['TaxableAmount']
        tot_registerd_VAT += registerd_persons['VAT']

        # Unregistered Persons
        unregisterd_persons = vat_taxSummary_InwardSupplies(
            'Unregisterd Persons', [1], CompanyID, BranchID, FromDate, ToDate)
        # adding Total
        tot_registerd_TaxableAmount += unregisterd_persons['TaxableAmount']
        tot_registerd_VAT += unregisterd_persons['VAT']

        # Zero-rated supplies and Deemed Exports
        zeroRated_taxSummary = vat_zeroRated_taxSummary_InwardSupplies(
            'Zero-rated supplies and Deemed Exports', [None], CompanyID, BranchID, FromDate, ToDate)
        # adding Total
        tot_registerd_TaxableAmount += zeroRated_taxSummary['TaxableAmount']
        tot_registerd_VAT += zeroRated_taxSummary['VAT']

        inward_supplies.append(registerd_persons)
        inward_supplies.append(unregisterd_persons)
        inward_supplies.append(zeroRated_taxSummary)
        dic = {
            "Heading": "Total",
            'TaxableAmount': tot_registerd_TaxableAmount,
            'VAT': tot_registerd_VAT,
        }
        # append Total
        inward_supplies.append(dic)
        # Add TotalTax Due
        due_TaxableAmount = outward_supplies[3]['TaxableAmount'] - \
            inward_supplies[3]['TaxableAmount']
        due_VAT = outward_supplies[3]['VAT'] - inward_supplies[3]['VAT']
        due_Amount = {
            'due_TaxableAmount': due_TaxableAmount,
            'due_VAT': due_VAT,
        }

        response_data = {
            "StatusCode": 6000,
            "outward_supplies": outward_supplies,
            "inward_supplies": inward_supplies,
            "due_Amount": due_Amount,
        }

        return response_data


def export_to_excel_taxSummary(wb, data, Type, title):
    print(data['outward_supplies'][0], 'oioiooioioioioioioioi')
    ws = wb.add_sheet("TaxSummary Report")

    header_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True
    header_style.font = font

    # blue custome color1
    xlwt.add_palette_colour("custom_colour2", 0x23)
    wb.set_colour_RGB(0x23, 32, 93, 153)

    # blue custome black
    xlwt.add_palette_colour("bg_black", 0x24)
    wb.set_colour_RGB(0x24, 0, 0, 0)

    # header black background color
    black = xlwt.Pattern()
    black.pattern = xlwt.Pattern.SOLID_PATTERN
    black.pattern_fore_colour = xlwt.Style.colour_map['bg_black']

    # header blue background color
    blue = xlwt.Pattern()
    blue.pattern = xlwt.Pattern.SOLID_PATTERN
    blue.pattern_fore_colour = xlwt.Style.colour_map['custom_colour2']

    # adjust the row width
    ws.col(0).width = int(100)*int(100)

    # column value alighn center
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    header_style.alignment = center

    value_decimal_style = xlwt.XFStyle()
    value_decimal_style.num_format_str = '0.00'

    sub_head = xlwt.XFStyle()
    sub_head.alignment = center
    font = xlwt.Font()
    font.bold = True
    sub_head.font = font
    font.colour_index = 1
    sub_head.pattern = black

    main_title = xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True
    main_title.font = font
    main_title.alignment = center

    due_total = xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True
    due_total.font = font
    font.colour_index = 1
    due_total.num_format_str = '0.00'
    due_total.pattern = blue

    total_label = xlwt.XFStyle()
    total_label.alignment = center
    font = xlwt.Font()
    font.bold = True
    total_label.font = font
    font.colour_index = 10

    data_col = 0
    data_row = 1
    SlNo = 0
    if Type == "GST":
        ws.write_merge(0, 0, 0, 5, title, main_title)
        # ==========Tax Summary GST==========
        columns = ['Description', 'Taxable Amount',
                   'IGST', 'CGST', 'SGST', 'Total Tax']
        row_num = 1
        # HEADING
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], header_style)
        # ====================Outward Supplies======================
        ws.write_merge(2, 2, 0, 5, 'Outward Supplies', sub_head)
        # Registered Persons
        ws.write(3, 0, "Registered Persons")
        ws.write(3, 1, float(data['outward_supplies']
                 [0]['TaxableAmount']), value_decimal_style)
        ws.write(3, 2, float(data['outward_supplies']
                 [0]['IGST']), value_decimal_style)
        ws.write(3, 3, float(data['outward_supplies']
                 [0]['CGST']), value_decimal_style)
        ws.write(3, 4, float(data['outward_supplies']
                 [0]['SGST']), value_decimal_style)
        ws.write(3, 5, float(data['outward_supplies']
                 [0]['TotalTax']), value_decimal_style)
        # Unregistered Persons
        ws.write(4, 0, "Unregistered Persons")
        ws.write(4, 1, float(data['outward_supplies']
                 [1]['TaxableAmount']), value_decimal_style)
        ws.write(4, 2, float(data['outward_supplies']
                 [1]['IGST']), value_decimal_style)
        ws.write(4, 3, float(data['outward_supplies']
                 [1]['CGST']), value_decimal_style)
        ws.write(4, 4, float(data['outward_supplies']
                 [1]['SGST']), value_decimal_style)
        ws.write(4, 5, float(data['outward_supplies']
                 [1]['TotalTax']), value_decimal_style)
        # Zero-rated supplies and Deemed Exports
        ws.write(5, 0, "Zero-rated supplies and Deemed Exports")
        ws.write(5, 1, float(data['outward_supplies']
                 [2]['TaxableAmount']), value_decimal_style)
        ws.write(5, 2, float(data['outward_supplies']
                 [2]['IGST']), value_decimal_style)
        ws.write(5, 3, float(data['outward_supplies']
                 [2]['CGST']), value_decimal_style)
        ws.write(5, 4, float(data['outward_supplies']
                 [2]['SGST']), value_decimal_style)
        ws.write(5, 5, float(data['outward_supplies']
                 [2]['TotalTax']), value_decimal_style)
        # Total
        ws.write(6, 0, "Total", total_label)
        ws.write(6, 1, float(data['outward_supplies']
                 [3]['TaxableAmount']), value_decimal_style)
        ws.write(6, 2, float(data['outward_supplies']
                 [3]['IGST']), value_decimal_style)
        ws.write(6, 3, float(data['outward_supplies']
                 [3]['CGST']), value_decimal_style)
        ws.write(6, 4, float(data['outward_supplies']
                 [3]['SGST']), value_decimal_style)
        ws.write(6, 5, float(data['outward_supplies']
                 [3]['TotalTax']), value_decimal_style)
        # ====================Inward Supplies======================
        ws.write_merge(7, 7, 0, 5, 'Inward Supplies', sub_head)
        # Registered Persons
        ws.write(8, 0, "Registered Persons")
        ws.write(8, 1, float(data['inward_supplies']
                 [0]['TaxableAmount']), value_decimal_style)
        ws.write(8, 2, float(data['inward_supplies']
                 [0]['IGST']), value_decimal_style)
        ws.write(8, 3, float(data['inward_supplies']
                 [0]['CGST']), value_decimal_style)
        ws.write(8, 4, float(data['inward_supplies']
                 [0]['SGST']), value_decimal_style)
        ws.write(8, 5, float(data['inward_supplies']
                 [0]['TotalTax']), value_decimal_style)
        # Unregistered Persons
        ws.write(9, 0, "Unregistered Persons")
        ws.write(9, 1, float(data['inward_supplies']
                 [1]['TaxableAmount']), value_decimal_style)
        ws.write(9, 2, float(data['inward_supplies']
                 [1]['IGST']), value_decimal_style)
        ws.write(9, 3, float(data['inward_supplies']
                 [1]['CGST']), value_decimal_style)
        ws.write(9, 4, float(data['inward_supplies']
                 [1]['SGST']), value_decimal_style)
        ws.write(9, 5, float(data['inward_supplies']
                 [1]['TotalTax']), value_decimal_style)
        # Zero-rated supplies and Deemed Exports
        ws.write(10, 0, "Zero-rated supplies and Deemed Exports")
        ws.write(10, 1, float(data['inward_supplies']
                 [2]['TaxableAmount']), value_decimal_style)
        ws.write(10, 2, float(data['inward_supplies']
                 [2]['IGST']), value_decimal_style)
        ws.write(10, 3, float(data['inward_supplies']
                 [2]['CGST']), value_decimal_style)
        ws.write(10, 4, float(data['inward_supplies']
                 [2]['SGST']), value_decimal_style)
        ws.write(10, 5, float(data['inward_supplies']
                 [2]['TotalTax']), value_decimal_style)
        # Total
        ws.write(11, 0, "Total", total_label)
        ws.write(11, 1, float(data['inward_supplies']
                 [3]['TaxableAmount']), value_decimal_style)
        ws.write(11, 2, float(data['inward_supplies']
                 [3]['IGST']), value_decimal_style)
        ws.write(11, 3, float(data['inward_supplies']
                 [3]['CGST']), value_decimal_style)
        ws.write(11, 4, float(data['inward_supplies']
                 [3]['SGST']), value_decimal_style)
        ws.write(11, 5, float(data['inward_supplies']
                 [3]['TotalTax']), value_decimal_style)
        # Due Total
        ws.write(12, 0, "Net GST Due", due_total)
        ws.write(12, 1, float(data['due_Amount']
                 ['due_TaxableAmount']), due_total)
        ws.write(12, 2, float(data['due_Amount']['due_IGST']), due_total)
        ws.write(12, 3, float(data['due_Amount']['due_CGST']), due_total)
        ws.write(12, 4, float(data['due_Amount']['due_SGST']), due_total)
        ws.write(12, 5, float(data['due_Amount']['due_TotalTax']), due_total)

    elif Type == "VAT":
        ws.write_merge(0, 0, 0, 2, title, main_title)
        # ==========Tax Summary VAT==========
        columns = ['Description', 'Taxable Amount', 'VAT']
        row_num = 1
        # HEADING
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], header_style)
        # ====================Outward Supplies======================
        ws.write_merge(2, 2, 0, 2, 'Outward Supplies', sub_head)
        # Registered Persons
        ws.write(3, 0, "Registered Persons")
        ws.write(3, 1, float(data['outward_supplies']
                 [0]['TaxableAmount']), value_decimal_style)
        ws.write(3, 2, float(data['outward_supplies']
                 [0]['VAT']), value_decimal_style)
        # Unregistered Persons
        ws.write(4, 0, "Unregistered Persons")
        ws.write(4, 1, float(data['outward_supplies']
                 [1]['TaxableAmount']), value_decimal_style)
        ws.write(4, 2, float(data['outward_supplies']
                 [1]['VAT']), value_decimal_style)
        # Zero-rated supplies and Deemed Exports
        ws.write(5, 0, "Zero-rated supplies and Deemed Exports")
        ws.write(5, 1, float(data['outward_supplies']
                 [2]['TaxableAmount']), value_decimal_style)
        ws.write(5, 2, float(data['outward_supplies']
                 [2]['VAT']), value_decimal_style)
        # Total
        ws.write(6, 0, "Total", total_label)
        ws.write(6, 1, float(data['outward_supplies']
                 [3]['TaxableAmount']), value_decimal_style)
        ws.write(6, 2, float(data['outward_supplies']
                 [3]['VAT']), value_decimal_style)
        # ====================Inward Supplies======================
        ws.write_merge(7, 7, 0, 2, 'Inward Supplies', sub_head)
        # Registered Persons
        ws.write(8, 0, "Registered Persons")
        ws.write(8, 1, float(data['inward_supplies']
                 [0]['TaxableAmount']), value_decimal_style)
        ws.write(8, 2, float(data['inward_supplies']
                 [0]['VAT']), value_decimal_style)
        # Unregistered Persons
        ws.write(9, 0, "Unregistered Persons")
        ws.write(9, 1, float(data['inward_supplies']
                 [1]['TaxableAmount']), value_decimal_style)
        ws.write(9, 2, float(data['inward_supplies']
                 [1]['VAT']), value_decimal_style)
        # Zero-rated supplies and Deemed Exports
        ws.write(10, 0, "Zero-rated supplies and Deemed Exports")
        ws.write(10, 1, float(data['inward_supplies']
                 [2]['TaxableAmount']), value_decimal_style)
        ws.write(10, 2, float(data['inward_supplies']
                 [2]['VAT']), value_decimal_style)
        # Total
        ws.write(11, 0, "Total", total_label)
        ws.write(11, 1, float(data['inward_supplies']
                 [3]['TaxableAmount']), value_decimal_style)
        ws.write(11, 2, float(data['inward_supplies']
                 [3]['VAT']), value_decimal_style)
        # Due Total
        ws.write(12, 0, "Net GST Due", due_total)
        ws.write(12, 1, float(data['due_Amount']
                 ['due_TaxableAmount']), due_total)
        ws.write(12, 2, float(data['due_Amount']['due_VAT']), due_total)


def sales_taxgroup_excel_data(CompanyID, BranchID, FromDate, ToDate, PriceRounding):
    final_data = []
    is_ok = False
    count = 0
    # interstate b2b
    tax_types = ["GST Inter-state B2B", "GST Inter-state B2C", "GST Intra-state B2B",
                 "GST Intra-state B2C", "GST Intra-state B2B Unregistered"]
    for tx in tax_types:
        # SalesMaster
        if SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, TaxType=tx).exists():
            sales_instances = SalesMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, TaxType=tx)
            sales_ids = sales_instances.values_list(
                'SalesMasterID', flat=True)

            sales_details = SalesDetails.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, SalesMasterID__in=sales_ids)
            # sales_details = SalesDetails.objects.filter(CompanyID=CompanyID,BranchID=BranchID,SalesMasterID__in=sales_ids).exclude(IGSTPerc=0)
            tax_list = sales_details.values_list('IGSTPerc', flat=True)
            tax_list = set(tax_list)
            print(sales_details, "+++++++++++++++++++++++++++++++++")
            # count = 0
            for t in tax_list:
                gouprd_details = sales_details.filter(IGSTPerc=t)
                if gouprd_details:
                    final_data.append({
                        "type": "Master",
                        "TaxType": tx,
                        "TaxPerc": t,
                        "total_Qty": 0,
                        "total_amount": 0,
                        "total_SGSTAmount": 0,
                        "total_CGSTAmount": 0,
                        "total_IGSTAmount": 0,
                        "total_sum_Total": 0,
                        "data": [],
                    })
                    total_Qty = 0
                    total_amount = 0
                    total_SGSTAmount = 0
                    total_CGSTAmount = 0
                    total_IGSTAmount = 0
                    total_sum_Total = 0
                    for g in gouprd_details:
                        SalesMasterID = g.SalesMasterID
                        Date = sales_instances.get(
                            SalesMasterID=SalesMasterID).Date
                        InvoiceNo = sales_instances.get(
                            SalesMasterID=SalesMasterID).VoucherNo
                        LedgerID = sales_instances.get(
                            SalesMasterID=SalesMasterID).LedgerID
                        ProductID = g.ProductID
                        party = ""
                        GSTN = ""
                        City = ""
                        State_id = ""
                        State_Code = ""
                        state_name = ""
                        if AccountLedger.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID, AccountGroupUnder__in=[10, 29]).exists():
                            parties = Parties.objects.get(
                                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID)
                            party = parties.PartyName
                            GSTN = parties.GSTNumber
                            City = parties.City
                            State_id = parties.State
                            State_Code = parties.State_Code
                            if State_id:
                                if State.objects.filter(pk=State_id).exists():
                                    state_name = State.objects.get(
                                        pk=State_id).Name

                        product = Product.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                        item_name = product.ProductName
                        HSN = product.HSNCode

                        Qty = g.Qty
                        UnitID = PriceList.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, PriceListID=g.PriceListID).UnitID
                        UnitName = Unit.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, UnitID=UnitID).UnitName
                        Amount = g.TaxableAmount

                        SGSTPerc = g.SGSTPerc
                        CGSTPerc = g.CGSTPerc
                        IGSTPerc = g.IGSTPerc
                        SGSTAmount = g.SGSTAmount
                        if SGSTAmount == 0:
                            SGSTPerc = 0
                        CGSTAmount = g.CGSTAmount
                        if CGSTAmount == 0:
                            CGSTPerc = 0
                        IGSTAmount = g.IGSTAmount
                        if IGSTAmount == 0:
                            IGSTPerc = 0
                        Total = g.NetAmount

                        total_Qty += float(Qty)
                        total_amount += float(Amount)
                        total_SGSTAmount += float(SGSTAmount)
                        total_CGSTAmount += float(CGSTAmount)
                        total_IGSTAmount += float(IGSTAmount)
                        total_sum_Total += float(Total)

                        str_date = Date.strftime('%m/%d/%Y')
                        data = {
                            "Date": str_date,
                            "InvoiceDate": str_date,
                            "InvoiceNo": InvoiceNo,
                            "party": party,
                            "GSTN": GSTN,
                            "City": City,
                            "State": state_name,
                            "State_Code": State_Code,
                            "item_name": item_name,
                            "HSN": HSN,
                            "Qty": Qty,
                            "UnitName": UnitName,
                            "Amount": Amount,
                            "SGSTPerc": SGSTPerc,
                            "CGSTPerc": CGSTPerc,
                            "IGSTPerc": IGSTPerc,
                            "SGSTAmount": SGSTAmount,
                            "CGSTAmount": CGSTAmount,
                            "IGSTAmount": IGSTAmount,
                            "Total": '%.2f' % round(Total, 2),
                        }

                        is_ok = True
                        final_data[count]['data'].append(data)

                    final_data[count]['total_Qty'] = total_Qty
                    final_data[count]['total_amount'] = total_amount
                    final_data[count]['total_SGSTAmount'] = total_SGSTAmount
                    final_data[count]['total_CGSTAmount'] = total_CGSTAmount
                    final_data[count]['total_IGSTAmount'] = total_IGSTAmount
                    final_data[count]['total_sum_Total'] = total_sum_Total

                    count += 1

        # SalesReturnMaster
        if SalesReturnMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate, TaxType=tx).exists():
            salesReturn_instances = SalesReturnMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate, TaxType=tx)
            salesReturn_ids = salesReturn_instances.values_list(
                'SalesReturnMasterID', flat=True)

            salesReturn_details = SalesReturnDetails.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, SalesReturnMasterID__in=salesReturn_ids)
            # salesReturn_details = SalesReturnDetails.objects.filter(CompanyID=CompanyID,BranchID=BranchID,SalesReturnMasterID__in=salesReturn_ids).exclude(IGSTPerc=0)
            tax_list = salesReturn_details.values_list('IGSTPerc', flat=True)
            tax_list = set(tax_list)
            print(salesReturn_details, "+++++++++++++++++++++++++++++++++")
            # count = 0
            for t in tax_list:
                gouprd_details = salesReturn_details.filter(IGSTPerc=t)
                if gouprd_details:
                    final_data.append({
                        "type": "Return",
                        "TaxType": tx,
                        "TaxPerc": t,
                        "total_Qty": 0,
                        "total_amount": 0,
                        "total_SGSTAmount": 0,
                        "total_CGSTAmount": 0,
                        "total_IGSTAmount": 0,
                        "total_sum_Total": 0,
                        "data": [],
                    })
                    total_Qty = 0
                    total_amount = 0
                    total_SGSTAmount = 0
                    total_CGSTAmount = 0
                    total_IGSTAmount = 0
                    total_sum_Total = 0
                    for g in gouprd_details:
                        SalesReturnMasterID = g.SalesReturnMasterID
                        VoucherDate = salesReturn_instances.get(
                            SalesReturnMasterID=SalesReturnMasterID).VoucherDate
                        InvoiceNo = salesReturn_instances.get(
                            SalesReturnMasterID=SalesReturnMasterID).VoucherNo
                        LedgerID = salesReturn_instances.get(
                            SalesReturnMasterID=SalesReturnMasterID).LedgerID
                        ProductID = g.ProductID
                        party = ""
                        GSTN = ""
                        City = ""
                        State_id = ""
                        State_Code = ""
                        state_name = ""
                        if AccountLedger.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID, AccountGroupUnder__in=[10, 29]).exists():
                            parties = Parties.objects.get(
                                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID)
                            party = parties.PartyName
                            GSTN = parties.GSTNumber
                            City = parties.City
                            State_id = parties.State
                            State_Code = parties.State_Code
                            if State_id:
                                if State.objects.filter(pk=State_id).exists():
                                    state_name = State.objects.get(
                                        pk=State_id).Name

                        product = Product.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                        item_name = product.ProductName
                        HSN = product.HSNCode

                        Qty = g.Qty
                        UnitID = PriceList.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, PriceListID=g.PriceListID).UnitID
                        UnitName = Unit.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, UnitID=UnitID).UnitName
                        Amount = g.TaxableAmount

                        SGSTPerc = g.SGSTPerc
                        CGSTPerc = g.CGSTPerc
                        IGSTPerc = g.IGSTPerc
                        SGSTAmount = g.SGSTAmount
                        if SGSTAmount == 0:
                            SGSTPerc = 0
                        CGSTAmount = g.CGSTAmount
                        if CGSTAmount == 0:
                            CGSTPerc = 0
                        IGSTAmount = g.IGSTAmount
                        if IGSTAmount == 0:
                            IGSTPerc = 0
                        Total = g.NetAmount

                        total_Qty += float(Qty)
                        total_amount += float(Amount)
                        total_SGSTAmount += float(SGSTAmount)
                        total_CGSTAmount += float(CGSTAmount)
                        total_IGSTAmount += float(IGSTAmount)
                        total_sum_Total += float(Total)

                        str_date = VoucherDate.strftime('%m/%d/%Y')
                        data = {
                            "Date": str_date,
                            "InvoiceDate": str_date,
                            "InvoiceNo": InvoiceNo,
                            "party": party,
                            "GSTN": GSTN,
                            "City": City,
                            "State": state_name,
                            "State_Code": State_Code,
                            "item_name": item_name,
                            "HSN": HSN,
                            "Qty": Qty,
                            "UnitName": UnitName,
                            "Amount": Amount,
                            "SGSTPerc": SGSTPerc,
                            "CGSTPerc": CGSTPerc,
                            "IGSTPerc": IGSTPerc,
                            "SGSTAmount": SGSTAmount,
                            "CGSTAmount": CGSTAmount,
                            "IGSTAmount": IGSTAmount,
                            "Total": '%.2f' % round(Total, 2),
                        }

                        is_ok = True
                        final_data[count]['data'].append(data)

                    final_data[count]['total_Qty'] = total_Qty
                    final_data[count]['total_amount'] = total_amount
                    final_data[count]['total_SGSTAmount'] = total_SGSTAmount
                    final_data[count]['total_CGSTAmount'] = total_CGSTAmount
                    final_data[count]['total_IGSTAmount'] = total_IGSTAmount
                    final_data[count]['total_sum_Total'] = total_sum_Total

                    count += 1

    if is_ok == True:
        return final_data
    else:
        return []


def export_to_excel_sales_taxgroup(wb, data, FromDate, ToDate):
    ws = wb.add_sheet("sheet1")
    # main header

    columns = ['SlNo', 'Date', 'Invoice Date', 'Invoice No', 'Party', 'GSTIN / UIN', 'City', 'State', 'State Code',
               'ItemName', 'HSN', 'Qty', 'Unit', 'Amount', 'SGST', 'CGST', 'IGST', 'SGST', 'CGST', 'IGST', 'Total']
    row_num = 0
    # write column headers in sheet

    # xl sheet styles
    # header font
    font = xlwt.Font()
    font.bold = True
    font.height = 11 * 20

    sub_header_style = xlwt.XFStyle()
    sub_header_style.font = font

    total_values_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.colour_index = 4
    total_values_style.font = font

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num])

    data_row = 0
    # print(data,"***********************************")
    for i in range(len(data)):
        data_col = 0
        data_row += 1
        try:
            invoice_type = data[i]['type']
        except:
            invoice_type = "Master"

        if invoice_type == "Master":
            invoice_head = "Sales From "
        elif invoice_type == "Return":
            invoice_head = "Sales Return From "

        ws.write(data_row, data_col, str(invoice_head)+str(data[i]['TaxType'])+str(
            " - ")+str(data[i]['TaxPerc'])+str("% Taxable"), sub_header_style)
        data_row += 1
        ws.write(data_row, data_col, str("From "+str(FromDate) +
                 str(" To ")+str(ToDate)), sub_header_style)

        data_row += 1
        SlNo = 1

        total_Qty = data[i]['total_Qty']
        total_amount = data[i]['total_amount']
        total_SGSTAmount = data[i]['total_SGSTAmount']
        total_CGSTAmount = data[i]['total_CGSTAmount']
        total_IGSTAmount = data[i]['total_IGSTAmount']
        total_sum_Total = data[i]['total_sum_Total']
        for j in data[i]['data']:
            total_row = SlNo+3
            if data_row == 3:
                total_row += 1
            ws.write(data_row, 0, SlNo)
            ws.write(data_row, 1, j['Date'])
            ws.write(data_row, 2, j['InvoiceDate'])
            ws.write(data_row, 3, j['InvoiceNo'])
            ws.write(data_row, 4, j['party'])
            ws.write(data_row, 5, j['GSTN'])
            ws.write(data_row, 6, j['City'])
            ws.write(data_row, 7, j['State'])
            ws.write(data_row, 8, j['State_Code'])
            ws.write(data_row, 9, j['item_name'])
            ws.write(data_row, 10, j['HSN'])
            ws.write(data_row, 11, j['Qty'])
            ws.write(data_row, 12, j['UnitName'])
            ws.write(data_row, 13, j['Amount'])
            ws.write(data_row, 14, j['SGSTPerc'])
            ws.write(data_row, 15, j['CGSTPerc'])
            ws.write(data_row, 16, j['IGSTPerc'])
            ws.write(data_row, 17, j['SGSTAmount'])
            ws.write(data_row, 18, j['CGSTAmount'])
            ws.write(data_row, 19, j['IGSTAmount'])
            ws.write(data_row, 20, j['Total'])
            data_row += 1
            SlNo += 1
        print(data_row, "&&&&&&&&&&&")
        ws.write(data_row, 9, "Total", total_values_style)
        ws.write(data_row, 10, "")
        ws.write(data_row, 11, total_Qty, total_values_style)
        ws.write(data_row, 12, "")
        ws.write(data_row, 13, total_amount, total_values_style)
        ws.write(data_row, 14, "")
        ws.write(data_row, 15, "")
        ws.write(data_row, 16, "")
        ws.write(data_row, 17, total_SGSTAmount, total_values_style)
        ws.write(data_row, 18, total_CGSTAmount, total_values_style)
        ws.write(data_row, 19, total_IGSTAmount, total_values_style)
        ws.write(data_row, 20, total_sum_Total, total_values_style)





def GST_finalList_fun(instance,Detail,type_tx,PriceRounding,TransactionType):
    shipping_tax_amount = 0
    half_shipping_tax_amount = 0
    if TransactionType == "Sales":
        shipping_tax_amount = instance.shipping_tax_amount
        half_shipping_tax_amount = float(shipping_tax_amount) / 2
    if type_tx == "SGST":
        SGST_perc_list = []
        GST_final_list = []
        for i in Detail:
            if not i.SGSTPerc in SGST_perc_list and i.SGSTPerc > 0:
                SGST_perc_list.append(i.SGSTPerc)
                SGSTAmount = float(i.SGSTAmount) + float(half_shipping_tax_amount);
                GST_final_list.append({
                        "key": round(float(i.SGSTPerc),PriceRounding),
                        "val": float(SGSTAmount)
                    })
            else:
                for f in GST_final_list:
                    if round(float(f['key']),2) == round(float(i.SGSTPerc),2):
                        val_amt = f['val']
                        f['val'] = float(val_amt) + float(i.SGSTAmount)
    else:
        IGST_perc_list = []
        GST_final_list = []
        for i in Detail:
            if not i.IGSTPerc in IGST_perc_list and i.IGSTPerc > 0:
                IGST_perc_list.append(i.IGSTPerc)
                IGSTAmount = float(i.IGSTAmount) + float(half_shipping_tax_amount);
                GST_final_list.append({
                        "key": round(float(i.IGSTPerc),PriceRounding),
                        "val": float(IGSTAmount)
                    })
            else:
                for f in GST_final_list:
                    if round(float(f['key']),2) == round(float(i.IGSTPerc),2):
                        val_amt = f['val']
                        f['val'] = float(val_amt) + float(i.IGSTAmount)

    return GST_final_list




def SetBatchInSales(CompanyID, BranchID,Batch_salesPrice,Qty_batch,BatchCode,check_AllowUpdateBatchPriceInSales,UnitPriceListID,VoucherType):
    message = ""
    if table.Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
        batch_ins = table.Batch.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode)
        if VoucherType == "SI":
            StockOut = batch_ins.StockOut
            NewStock = float(
                StockOut) + float(Qty_batch)
            batch_ins.StockOut = NewStock
        if VoucherType == "SR":
            StockIn = batch_ins.StockIn
            NewStock = float(
                StockIn) + float(Qty_batch)
            batch_ins.StockIn = NewStock
        if VoucherType == "PR":
            StockOut = batch_ins.StockOut
            NewStock = float(
                StockOut) + float(Qty_batch)
            batch_ins.StockOut = NewStock
        if check_AllowUpdateBatchPriceInSales == "True" or check_AllowUpdateBatchPriceInSales == True and VoucherType == "SI":
            sales_price = get_batch_salesPrice(CompanyID, BranchID,UnitPriceListID,batch_ins.PriceListID,Batch_salesPrice)
        else:
            sales_price = batch_ins.SalesPrice
        batch_ins.SalesPrice = sales_price
        batch_ins.save()

    return message


def get_batch_salesPrice(CompanyID, BranchID,UnitPriceListID,BatchPriceListID,Batch_salesPrice):
    sales_price = Batch_salesPrice

    if not UnitPriceListID == BatchPriceListID:
        unit_multifactor = 1
        batch_multifactor = 1
        if table.PriceList.objects.filter(CompanyID=CompanyID,BranchID=BranchID,PriceListID=UnitPriceListID).exists():
            unit_priceList_ins = table.PriceList.objects.get(CompanyID=CompanyID,BranchID=BranchID,PriceListID=UnitPriceListID)
            unit_multifactor = unit_priceList_ins.MultiFactor

        if table.PriceList.objects.filter(CompanyID=CompanyID,BranchID=BranchID,PriceListID=BatchPriceListID).exists():
            batch_priceList_ins = table.PriceList.objects.get(CompanyID=CompanyID,BranchID=BranchID,PriceListID=BatchPriceListID)
            batch_multifactor = batch_priceList_ins.MultiFactor

        if float(batch_multifactor) < float(unit_multifactor):
            sales_price = float(Batch_salesPrice) / float(unit_multifactor)
        elif float(batch_multifactor) > float(unit_multifactor):
            sales_price = float(Batch_salesPrice) * float(batch_multifactor)

    return sales_price
