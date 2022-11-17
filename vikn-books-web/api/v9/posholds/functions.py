import string
import random
from django.db import connection
from django.http import HttpResponse
from decimal import Decimal
from django.db.models import Max
from brands.models import POS_Printer, POS_User, ProductVariants
from random import randint
from brands import models as table
from django.contrib.auth.models import User
import re,sys, os
import pandas as pd
from django.utils.translation import ugettext_lazy as _
import json

def generate_serializer_errors(args):
    message = ""
    for key, values in args.items():
        error_message = ""
        for value in values:
            error_message += value + ","
        error_message = error_message[:-1]

        message += "%s : %s | " %(key,error_message)
    return message[:-3]


def get_auto_idMaster(model,BranchID):
    POSHoldMasterID = 1
    max_value = None
    POSHoldMasterID = None
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.all().aggregate(Max('POSHoldMasterID'))
    

    if model.objects.filter(BranchID=BranchID).exists():
        max_value =  model.objects.filter(BranchID=BranchID).aggregate(Max('POSHoldMasterID'))
        

    if max_value:
        max_posHoldMasterId = max_value.get('POSHoldMasterID__max', 0)
        
        POSHoldMasterID = max_posHoldMasterId + 1
        
    else:
        POSHoldMasterID = 1

    
    # if model.objects.filter(BrandID=BrandID).exists():
    #     BrandID = 1
            
    POSHoldMasterID
    return POSHoldMasterID





def get_auto_id(model,BranchID):
    POSHoldDetailsID = 1
    max_value = None
    POSHoldDetailsID = None
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.all().aggregate(Max('POSHoldDetailsID'))
    if model.objects.filter(BranchID=BranchID).exists():
        max_value =  model.objects.filter(BranchID=BranchID).aggregate(Max('POSHoldDetailsID'))
    if max_value:
        max_posHoldDetailsId = max_value.get('POSHoldDetailsID__max', 0)
        
        POSHoldDetailsID = max_posHoldDetailsId + 1
        
    else:
        POSHoldDetailsID = 1
    return POSHoldDetailsID


def get_pin_no(CompanyID,BranchID):
    range_start = 10**(6-1)
    range_end = (10**6)-1
    PinNo = randint(range_start, range_end)
    if POS_User.objects.filter(CompanyID=CompanyID,BranchID=BranchID,PinNo=PinNo).exists():
        get_pin_no(CompanyID,BranchID)
    return PinNo


def get_InvoiceNo(OldVoucherNo):
    InvoiceNo = 1
    if not OldVoucherNo.isdecimal():
        res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
        num = res.group(0)
        InvoiceNo = int(num)
    return InvoiceNo


def get_VoucherNoForPOS(CompanyID,BranchID,UserID,VoucherType):
    old_invoiceNo = 0
    seperator = ""
    PreFix = VoucherType
    user_count = table.UserTable.objects.filter(CompanyID=CompanyID).count()
    if user_count == 1:
        if table.VoucherNoGenerateTable.objects.filter(CompanyID=CompanyID,UserID=UserID,VoucherType=VoucherType).exists():
            voucher = table.VoucherNoGenerateTable.objects.filter(CompanyID=CompanyID,UserID=UserID,VoucherType=VoucherType).first()
            old_invoiceNo =  voucher.LastInvoiceNo
            PreFix = voucher.PreFix
            seperator = voucher.Seperater
    else:
        user_name = User.objects.get(id=UserID).username
        PreFix = user_name[0:3]
        if table.VoucherNoGenerateTable.objects.filter(CompanyID=CompanyID,UserID=UserID,VoucherType=VoucherType).exists():
            voucher = table.VoucherNoGenerateTable.objects.filter(CompanyID=CompanyID,UserID=UserID,VoucherType=VoucherType).first()
            old_invoiceNo =  voucher.LastInvoiceNo
            PreFix = voucher.PreFix
            seperator = voucher.Seperater
            
    new_invoiceNo = old_invoiceNo + 1
    new_VoucherNo = PreFix + str(seperator) + str(new_invoiceNo) 
    return new_VoucherNo




def get_TokenNo(CompanyID,BranchID):
    TokenNo = "001"
    types = ["Online","TakeAway","Car","Dining"]
    if table.SalesOrderMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,Type__in=types).exists():
        last_order = table.SalesOrderMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,Type__in=types).first()
        last_token = int(last_order.TokenNumber)

        TokenNo = "{0:03}".format(last_token + 1)
    return TokenNo



def get_KitchenID(model,BranchID):
    KitchenID = 1
    max_value = None
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.all().aggregate(Max('KitchenID'))
    if model.objects.filter(BranchID=BranchID).exists():
        max_value =  model.objects.filter(BranchID=BranchID).aggregate(Max('KitchenID'))
    if max_value:
        max_KitchenID = max_value.get('KitchenID__max', 0)
        KitchenID = max_KitchenID + 1
    return KitchenID


def get_auto_PrinterID(CompanyID, BranchID):
    PrinterID = 1
    max_value = None
    if POS_Printer.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value = POS_Printer.objects.filter(
            CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('PrinterID'))
    if max_value:
        max_PrinterID = max_value.get('PrinterID__max', 0)
        PrinterID = max_PrinterID + 1
    return PrinterID


def get_auto_VariantID(CompanyID, BranchID):
    VariantID = 1
    max_value = None
    if ProductVariants.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        max_value = ProductVariants.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID).aggregate(Max('VariantID'))
    if max_value:
        max_VariantID = max_value.get('VariantID__max', 0)
        VariantID = max_VariantID + 1
    return VariantID


def query_sales_report_rassassy_data(
    CompanyID, BranchID, FromDate, ToDate, filterVal, PriceRounding, ReportType
):
    dic = {"BranchID": BranchID, "CompanyID": CompanyID, "ToDate": ToDate,
           "FromDate": FromDate, "filterVal": filterVal, "PriceRounding": PriceRounding}
    cursor = connection.cursor()
    cursor.execute(
        """
            SELECT 
            S."id" AS id,          
            S."VoucherNo" AS VoucherNo,          
            S."Date",
            s."TokenNumber",
            S."CustomerName" AS CustomerName,
            S."GrandTotal" AS GrandTotal,
            (SELECT "TableName" from public."pos_table_pos_table" AS t WHERE S."Table_id" = t.id ) as TableName       

            FROM public."salesMasters_salesMaster" AS S    
            WHERE S."Date" BETWEEN %(FromDate)s AND %(ToDate)s AND S."CompanyID_id" = %(CompanyID)s AND S."BranchID" = %(BranchID)s         
            ORDER BY "SalesMasterID"
    """,
        dic,
    )
   
    
    data = cursor.fetchall()
    if cursor.rowcount == 0:
        data = [("", "", "", "NO DATA", "", 0,"")]

    df = pd.DataFrame(data)
    df.columns = [
        str(_("id")),
        str(_("VoucherNo")),
        str(_("Date")),
        str(_("TokenNumber")),
        str(_("CustomerName")),
        str(_("GrandTotal")),
        str(_("TableName")),
    ]
    # concert uuid to string
    convert_dict = {'id': str}
    df = df.astype(convert_dict)
    # adding decimal point
    df["GrandTotal"] = df["GrandTotal"].apply(lambda x: round(
        abs(x), PriceRounding))
    df["Date"] = df["Date"].astype(str)
    json_records = df.reset_index().to_json(orient="records")
    details = json.loads(json_records)
    return df, details


def query_dining_report_rassassy_data(
    CompanyID, BranchID, FromDate, ToDate, filterVal, PriceRounding, ReportType
):
    dic = {"BranchID": BranchID, "CompanyID": CompanyID, "ToDate": ToDate,
           "FromDate": FromDate, "filterVal": filterVal, "PriceRounding": PriceRounding}
    cursor = connection.cursor()
    
    if filterVal:
        cursor.execute(
            """
                SELECT 
                S."id" AS id,          
                S."VoucherNo" AS VoucherNo,          
                S."Date",
                s."TokenNumber",
                S."CustomerName" AS CustomerName,
                S."GrandTotal" AS GrandTotal,
                (SELECT "TableName" from public."pos_table_pos_table" AS t WHERE t."CompanyID_id" =  s."CompanyID_id" AND t."id" = s."Table_id" ) as TableName 

                FROM public."salesMasters_salesMaster" AS S
                WHERE S."Date" BETWEEN %(FromDate)s AND %(ToDate)s AND S."CompanyID_id" = %(CompanyID)s AND S."BranchID" = %(BranchID)s  AND S."Table_id" = %(filterVal)s AND S."Type" = 'Dining'
                ORDER BY "SalesMasterID"
            """,
            dic,
        )
    else:
        cursor.execute(
            """
                SELECT 
                S."id" AS id,          
                S."VoucherNo" AS VoucherNo,          
                S."Date",
                s."TokenNumber",
                S."CustomerName" AS CustomerName,
                S."GrandTotal" AS GrandTotal,
                (SELECT "TableName" from public."pos_table_pos_table" AS t WHERE t."CompanyID_id" =  s."CompanyID_id" AND s."Table_id" = t."id" ) as TableName 

                FROM public."salesMasters_salesMaster" AS S 
                WHERE S."Date" BETWEEN %(FromDate)s AND %(ToDate)s AND S."CompanyID_id" = %(CompanyID)s AND S."BranchID" = %(BranchID)s  AND S."Type" = 'Dining'
                ORDER BY "SalesMasterID"
            """,
            dic,
        )


    data = cursor.fetchall()
    if cursor.rowcount == 0:
        data = [("", "", "", "NO DATA", "", 0, "")]

    df = pd.DataFrame(data)
    df.columns = [
        str(_("id")),
        str(_("VoucherNo")),
        str(_("Date")),
        str(_("TokenNumber")),
        str(_("CustomerName")),
        str(_("GrandTotal")),
        str(_("TableName")),
    ]
    # concert uuid to string
    convert_dict = {'id': str}
    df = df.astype(convert_dict)
    # adding decimal point
    df["GrandTotal"] = df["GrandTotal"].apply(lambda x: round(
        abs(x), PriceRounding))
    df["Date"] = df["Date"].astype(str)
    json_records = df.reset_index().to_json(orient="records")
    details = json.loads(json_records)
    return df, details


def query_take_away_report_rassassy_data(
    CompanyID, BranchID, FromDate, ToDate, filterVal, PriceRounding, ReportType
):
    dic = {"BranchID": BranchID, "CompanyID": CompanyID, "ToDate": ToDate,
           "FromDate": FromDate, "filterVal": filterVal, "PriceRounding": PriceRounding, "ReportType": ReportType}
    cursor = connection.cursor()
    cursor.execute(
        """
            SELECT 
            S."id" AS id,          
            S."VoucherNo" AS VoucherNo,          
            S."Date",
            s."TokenNumber",
            S."CustomerName" AS CustomerName,
            S."GrandTotal" AS GrandTotal,  
            (SELECT "TableName" from public."pos_table_pos_table" AS t WHERE S."Table_id" = t.id ) as TableName 
                    
            FROM public."salesMasters_salesMaster" AS S    
            WHERE S."Date" BETWEEN %(FromDate)s AND %(ToDate)s AND S."CompanyID_id" = %(CompanyID)s AND S."BranchID" = %(BranchID)s  AND S."Type" = %(ReportType)s      
            ORDER BY "SalesMasterID"
    """,
        dic,
    )
    

    data = cursor.fetchall()
    if cursor.rowcount == 0:
        data = [("", "", "", "NO DATA", "", 0, "")]

    df = pd.DataFrame(data)
    df.columns = [
        str(_("id")),
        str(_("VoucherNo")),
        str(_("Date")),
        str(_("TokenNumber")),
        str(_("CustomerName")),
        str(_("GrandTotal")),
        str(_("TableName")),
    ]
    # concert uuid to string
    convert_dict = {'id': str}
    df = df.astype(convert_dict)
    # adding decimal point
    df["GrandTotal"] = df["GrandTotal"].apply(lambda x: round(
        abs(x), PriceRounding))
    df["Date"] = df["Date"].astype(str)
    json_records = df.reset_index().to_json(orient="records")
    details = json.loads(json_records)
    return df, details


def query_table_wise_report_rassassy_data(
    CompanyID, BranchID, FromDate, ToDate, filterVal, PriceRounding, ReportType
):
    dic = {"BranchID": BranchID, "CompanyID": CompanyID, "ToDate": ToDate,
           "FromDate": FromDate, "filterVal": filterVal, "PriceRounding": PriceRounding}
    cursor = connection.cursor()
    
    if filterVal:
        cursor.execute(
            """
                SELECT 
                S."id" AS id,          
                S."VoucherNo" AS VoucherNo,          
                S."Date",
                s."TokenNumber",
                S."CustomerName" AS CustomerName,
                S."GrandTotal" AS GrandTotal,
                (SELECT "TableName" from public."pos_table_pos_table" AS t WHERE S."Table_id" = t.id) as TableName 

                FROM public."salesMasters_salesMaster" AS S
                WHERE S."Date" BETWEEN %(FromDate)s AND %(ToDate)s AND S."CompanyID_id" = %(CompanyID)s AND S."BranchID" = %(BranchID)s  AND S."Table_id" = %(filterVal)s
                ORDER BY "SalesMasterID"
            """,
            dic,
        )
    else:
        cursor.execute(
            """
                SELECT 
                S."id" AS id,          
                S."VoucherNo" AS VoucherNo,          
                S."Date",
                s."TokenNumber",
                S."CustomerName" AS CustomerName,
                S."GrandTotal" AS GrandTotal,
                (SELECT "TableName" from public."pos_table_pos_table" AS t WHERE S."Table_id" = t.id ) as TableName 

                FROM public."salesMasters_salesMaster" AS S 
                WHERE S."Date" BETWEEN %(FromDate)s AND %(ToDate)s AND S."CompanyID_id" = %(CompanyID)s AND S."BranchID" = %(BranchID)s 
                ORDER BY "SalesMasterID"
            """,
            dic,
        )


    data = cursor.fetchall()
    if cursor.rowcount == 0:
        data = [("", "", "", "NO DATA", "", 0, "")]

    df = pd.DataFrame(data)
    df.columns = [
        str(_("id")),
        str(_("VoucherNo")),
        str(_("Date")),
        str(_("TokenNumber")),
        str(_("CustomerName")),
        str(_("GrandTotal")),
        str(_("TableName")),
    ]
    # concert uuid to string
    convert_dict = {'id': str}
    df = df.astype(convert_dict)
    # adding decimal point
    df["GrandTotal"] = df["GrandTotal"].apply(lambda x: round(
        abs(x), PriceRounding))
    df["Date"] = df["Date"].astype(str)
    json_records = df.reset_index().to_json(orient="records")
    details = json.loads(json_records)
    return df, details


def query_product_report_rassassy_data(
    CompanyID, BranchID, FromDate, ToDate, filterVal, PriceRounding, ReportType
):
    dic = {"BranchID": BranchID, "CompanyID": CompanyID, "ToDate": ToDate,
           "FromDate": FromDate, "filterVal": filterVal, "PriceRounding": PriceRounding}
    cursor = connection.cursor()
    if filterVal:
        cursor.execute(
            """
                    SELECT 
                    s."Date" AS date,  
                    s."ProductID" as ProductID,
                    (SELECT "ProductName" FROM public."products_product" AS p where p."CompanyID_id" = 'e837c6a7-288a-4199-8b61-cc7905e54451' and p."ProductID" = s."ProductID") as ProductName,
                    s."Rate" as  rate

                    FROM public."stockPosting_stockPosting" AS s
                    WHERE s."Date" BETWEEN %(FromDate)s AND %(ToDate)s AND s."CompanyID_id" = %(CompanyID)s AND s."BranchID" = '1' AND "ProductID" = %(filterVal)s
                    GROUP BY "date", "ProductID"  , "rate"     
                    Order by "Date"
            """,
            dic,
        )
    else:
        cursor.execute(
            """
                    SELECT 
                    s."Date" AS date,  
                    s."ProductID" as ProductID,
                    (SELECT "ProductName" FROM public."products_product" AS p where p."CompanyID_id" = 'e837c6a7-288a-4199-8b61-cc7905e54451' and p."ProductID" = s."ProductID") as ProductName,
                    s."Rate" as  rate

                    FROM public."stockPosting_stockPosting" AS s
                    WHERE s."Date" BETWEEN %(FromDate)s AND %(ToDate)s AND s."CompanyID_id" = %(CompanyID)s AND s."BranchID" = '1'
                    GROUP BY "date", "ProductID"  , "rate"     
                    Order by "Date"
            """,
            dic,
        )

    data = cursor.fetchall()
    if cursor.rowcount == 0:
        data = [("", "", "NO DATA",  0)]

    df = pd.DataFrame(data)
    df.columns = [
        str(_("date")),
        str(_("ProductID")),
        str(_("ProductName")),
        str(_("rate")),
    ]
    # concert uuid to string
    # convert_dict = {'id': str}
    # df = df.astype(convert_dict)
    # adding decimal point
    df["rate"] = df["rate"].apply(lambda x: round(
        abs(x), PriceRounding))
    df["date"] = df["date"].astype(str)
    json_records = df.reset_index().to_json(orient="records")
    details = json.loads(json_records)
    return df, details
