import imp
import random
import string
from ast import And, While
from decimal import Decimal

import pandas as pd
import json
from main.functions import converted_float, get_GeneralSettings, get_all_dates_bwn2dates
import xlwt
from django.contrib.auth.models import User
from django.db import connection
from django.db.models import Max
from django.http import HttpResponse
from django.utils.translation import activate
from django.utils.translation import ugettext_lazy as _
from sqlalchemy import between
from xlwt import Alignment, Borders, Font, Pattern, Workbook, XFStyle, easyxf
from brands.models import Parties, UserTable


def query_export_to_excel_sales(wb, data, FromDate, ToDate, title):
    ws2 = wb.create_sheet("Mysheet", 0)
    ws = wb.active
    ws.title = "New Title"
    ws.sheet_properties.tabColor = "1072BA"

    columns = [
        str(_("Voucher No")),
        str(_("Voucher Date")),
        str(_("Ledger Name")),
        str(_("Cash Sales")),
        str(_("Bank Sales")),
        str(_("Credit Sales")),
        str(_("Gross Amount")),
        str(_("Total Tax")),
        str(_("Bill Discount")),
        str(_("Grand Total")),
    ]

    ws["A1"] = title
    ch = "A"
    for col_num in range(len(columns)):
        ws[str(ch) + str(2)] = columns[col_num]
        ch = chr(ord(ch) + 1)

    data_row = 3

    try:
        data_list = data
    except:
        data_list = []

    tot_CashSales = 0
    tot_BankSales = 0
    tot_CreditSales = 0
    tot_TotalGrossAmt = 0
    tot_TotalTax = 0
    tot_BillDiscAmt = 0
    tot_GrandTotal = 0
    for j in data_list:
        try:
            VoucherNo = j[2]
        except:
            VoucherNo = "-"
        try:
            Date = j[3]
        except:
            Date = "-"
        try:
            LedgerName = j[4]
        except:
            LedgerName = "-"
        try:
            CashSales = j[13]
        except:
            CashSales = 0
        try:
            BankSales = j[14]
        except:
            BankSales = 0
        try:
            CreditSales = j[15]
        except:
            CreditSales = 0
        try:
            TotalGrossAmt = j[7]
        except:
            TotalGrossAmt = 0
        try:
            TotalTax = j[8]
        except:
            TotalTax = 0
        try:
            BillDiscAmt = j[9]
        except:
            BillDiscAmt = 0
        try:
            GrandTotal = j[10]
        except:
            GrandTotal = 0

        tot_CashSales += CashSales
        tot_BankSales += BankSales
        tot_CreditSales += CreditSales
        tot_TotalGrossAmt += TotalGrossAmt
        tot_TotalTax += TotalTax
        tot_BillDiscAmt += BillDiscAmt
        tot_GrandTotal += GrandTotal
        ws[str("A") + str(data_row)] = VoucherNo
        ws[str("B") + str(data_row)] = Date
        ws[str("C") + str(data_row)] = LedgerName
        ws[str("D") + str(data_row)] = CashSales
        ws[str("D") + str(data_row)].number_format = "0.00"
        ws[str("E") + str(data_row)] = BankSales
        ws[str("E") + str(data_row)].number_format = "0.00"
        ws[str("F") + str(data_row)] = CreditSales
        ws[str("F") + str(data_row)].number_format = "0.00"
        ws[str("G") + str(data_row)] = TotalGrossAmt
        ws[str("G") + str(data_row)].number_format = "0.00"
        ws[str("H") + str(data_row)] = TotalTax
        ws[str("H") + str(data_row)].number_format = "0.00"
        ws[str("I") + str(data_row)] = BillDiscAmt
        ws[str("I") + str(data_row)].number_format = "0.00"
        ws[str("J") + str(data_row)] = GrandTotal
        ws[str("J") + str(data_row)].number_format = "0.00"
        data_row += 1
    # ws[str('A')+str(data_row)] = "VoucherNo"
    # ws[str('B')+str(data_row)] = "Date"
    # ws[str('C')+str(data_row)] = "Total"
    # ws[str('D')+str(data_row)] = tot_CashSales
    # ws[str('D')+str(data_row)].number_format = '0.00'
    # ws[str('E')+str(data_row)] = tot_BankSales
    # ws[str('E')+str(data_row)].number_format = '0.00'
    # ws[str('F')+str(data_row)] = tot_CreditSales
    # ws[str('F')+str(data_row)].number_format = '0.00'
    # ws[str('G')+str(data_row)] = tot_TotalGrossAmt
    # ws[str('G')+str(data_row)].number_format = '0.00'
    # ws[str('H')+str(data_row)] = tot_TotalTax
    # ws[str('H')+str(data_row)].number_format = '0.00'
    # ws[str('I')+str(data_row)] = tot_BillDiscAmt
    # ws[str('I')+str(data_row)].number_format = '0.00'
    # ws[str('J')+str(data_row)] = tot_GrandTotal
    # ws[str('J')+str(data_row)].number_format = '0.00'
    # ===============================================================
    # ws = wb.add_sheet("Sales Report")

    # columns = [str(_('Voucher No')), str(_('Voucher Date')),str(_("Ledger Name")), str(_('Cash Sales')), str(_('Bank Sales')),
    #            str(_('Credit Sales')), str(_('Gross Amount')), str(_('Total Tax')), str(_('Bill Discount')), str(_('Grand Total')), ]
    # # write column headers in sheet

    # # xl sheet styles

    # center = Alignment()
    # center.horz = Alignment.HORZ_CENTER

    # # header font
    # font = xlwt.Font()
    # font.bold = True
    # font.height = 11 * 20

    # sub_header_style = xlwt.XFStyle()
    # sub_header_style.font = font

    # total_values_style = xlwt.XFStyle()
    # font = xlwt.Font()
    # font.bold = True
    # total_values_style.num_format_str = '0.00'
    # total_values_style.font = font

    # total_label_style = xlwt.XFStyle()
    # font = xlwt.Font()
    # font.bold = True
    # font.colour_index = 2
    # total_label_style.font = font

    # value_decimal_style = xlwt.XFStyle()
    # value_decimal_style.num_format_str = '0.00'

    # main_title = xlwt.XFStyle()
    # font = xlwt.Font()
    # font.bold = True
    # main_title.font = font
    # main_title.alignment = center

    # ws.write_merge(0, 0, 0, 3, title, main_title)

    # row_num = 1

    # for col_num in range(len(columns)):
    #     ws.write(row_num, col_num, columns[col_num], sub_header_style)

    # data_row = 2

    # try:
    #     data_list = data
    # except:
    #     data_list = []

    # for j in data_list:
    #     try:
    #         VoucherNo = j[2]
    #     except:
    #         VoucherNo = '-'
    #     try:
    #         Date = j[3]
    #     except:
    #         Date = '-'
    #     try:
    #         LedgerName = j[4]
    #     except:
    #         LedgerName = '-'
    #     try:
    #         CashSales = j[13]
    #     except:
    #         CashSales = 0
    #     try:
    #         BankSales = j[14]
    #     except:
    #         BankSales = 0
    #     try:
    #         CreditSales = j[15]
    #     except:
    #         CreditSales = 0
    #     try:
    #         TotalGrossAmt = j[7]
    #     except:
    #         TotalGrossAmt = 0
    #     try:
    #         TotalTax = j[8]
    #     except:
    #         TotalTax = 0
    #     try:
    #         BillDiscAmt = j[9]
    #     except:
    #         BillDiscAmt = 0
    #     try:
    #         GrandTotal = j[10]
    #     except:
    #         GrandTotal = 0

    #     ws.write(data_row, 0, VoucherNo)
    #     ws.write(data_row, 1, Date)
    #     if LedgerName == "Total":
    #         ws.write(data_row, 2, LedgerName, total_label_style)
    #     else:
    #         ws.write(data_row, 2, LedgerName)
    #     ws.write(data_row, 3, converted_float(CashSales), value_decimal_style)
    #     ws.write(data_row, 4, converted_float(BankSales), value_decimal_style)
    #     ws.write(data_row, 5, converted_float(CreditSales), value_decimal_style)
    #     ws.write(data_row, 6, converted_float(TotalGrossAmt), value_decimal_style)
    #     ws.write(data_row, 7, converted_float(TotalTax), value_decimal_style)
    #     ws.write(data_row, 8, converted_float(BillDiscAmt), value_decimal_style)
    #     ws.write(data_row, 9, converted_float(GrandTotal), value_decimal_style)
    #     data_row += 1


def query_sales_report_data(
    CompanyID, BranchID, FromDate, ToDate, PriceRounding, UserID, EmployeeID,CustomerID,filterValue
):
    dic = {"BranchID": BranchID,"CompanyID": CompanyID,"ToDate": ToDate,"FromDate": FromDate,"PriceRounding": PriceRounding,"UserID": UserID,"EmployeeID": EmployeeID,"CustomerID": CustomerID,"filterValue":filterValue}
    cursor = connection.cursor()
    
    cursor.execute(
        """
            SELECT * FROM(
            SELECT                                  

            S."id" AS id,          
            S."VoucherNo" AS VoucherNo,          
            S."Date",
            S."CreatedDate" AS CreatedDate,          
            AL."LedgerName" AS LedgerName,          
            S."CustomerName" AS Name,                  
            CASE WHEN  
            S."EmployeeID" >0  THEN(SELECT NULLIF("FirstName", '') FROM public.employees_employees WHERE "EmployeeID" = S."EmployeeID" AND "CompanyID_id" = S."CompanyID_id")      
            WHEN S."EmployeeID" =0 THEN ''
            END AS SalesMan,
            S."TotalGrossAmt" AS NetAmount,          
            S."TotalTax" AS TotalTax,          
            S."TotalDiscount" AS BillDiscount,
            S."GrandTotal" AS GrandTotal,          

            (select COALESCE (SUM("Debit"),0) from public."ledgerPostings_ledgerPosting" where "CompanyID_id" = S."CompanyID_id" AND "VoucherType"='SI'      
            AND "VoucherMasterID"=s."SalesMasterID"  
            AND "LedgerID" IN (Select "LedgerID" from public."accountLedger_accountLedger" where "CompanyID_id" = S."CompanyID_id" AND "AccountGroupUnder" IN (8,9))) AS Cash

            FROM public."salesMasters_salesMaster" AS S LEFT OUTER JOIN public."accountLedger_accountLedger" AS AL ON S."LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = S."CompanyID_id"     
            WHERE S."Status" != 'Cancelled' AND
            CASE WHEN %(CustomerID)s > 0 AND %(UserID)s > 0 AND %(EmployeeID)s > 0 THEN
            S."EmployeeID" = %(EmployeeID)s AND S."CreatedUserID" = %(UserID)s AND S."LedgerID" = %(CustomerID)s AND S."BranchID" = %(BranchID)s

            WHEN %(CustomerID)s > 0 AND %(UserID)s > 0 THEN
            S."CreatedUserID" = %(UserID)s AND S."LedgerID" = %(CustomerID)s AND S."BranchID" = %(BranchID)s

            WHEN %(CustomerID)s > 0 AND %(EmployeeID)s > 0 THEN
            S."EmployeeID" = %(EmployeeID)s AND S."LedgerID" = %(CustomerID)s AND S."BranchID" = %(BranchID)s

            WHEN %(UserID)s > 0 AND %(EmployeeID)s > 0 THEN
            S."EmployeeID" = %(EmployeeID)s AND S."CreatedUserID" = %(UserID)s AND S."BranchID" = %(BranchID)s
            
            WHEN %(CustomerID)s > 0 THEN 
            S."LedgerID" = %(CustomerID)s AND S."BranchID" = %(BranchID)s 
            WHEN %(EmployeeID)s > 0 THEN
            S."EmployeeID" = %(EmployeeID)s AND S."BranchID" = %(BranchID)s
            WHEN %(UserID)s > 0 THEN 
            S."CreatedUserID" = %(UserID)s AND S."BranchID" = %(BranchID)s 
            ELSE
            S."BranchID" = %(BranchID)s 
            END
            AND S."Date" BETWEEN %(FromDate)s AND %(ToDate)s AND S."CompanyID_id" = %(CompanyID)s         
            ORDER BY "SalesMasterID"
            )


            as t where 
            CASE WHEN %(filterValue)s = 'cash' THEN
            Cash>0 
            WHEN %(filterValue)s = 'credit' THEN
            Cash=0.00
            ELSE
            Cash > 0 or Cash=0
            END
     """,
        dic,
    )
    data = cursor.fetchall()
    if cursor.rowcount == 0:
        data = [("","", "","", "NO DATA", "", "", 0,0,0,0,0)]
   
    df = pd.DataFrame(data)
    df.columns = [
        str(_("id")),
        str(_("VoucherNo")),
        str(_("Date")),
        str(_("CreatedDate")),
        str(_("LedgerName")),
        str(_("CustomerName")),
        str(_("EmployeeName")),
        str(_("GrossAmount")),
        str(_("TotalTax")),
        str(_("BillDiscount")),
        str(_("GrandTotal")),
        str(_("Cash")),
    ]
    print(df)
    # concert uuid to string
    convert_dict = {'id': str}
    df = df.astype(convert_dict)
    # adding decimal point
    df["GrossAmount"] = df["GrossAmount"].apply(lambda x: round(
        abs(x), PriceRounding))
    df["TotalTax"] = df["TotalTax"].apply(lambda x: round(
        abs(x), PriceRounding))
    df["BillDiscount"] = df["BillDiscount"].apply(lambda x: round(
        abs(x), PriceRounding))
    df["GrandTotal"] = df["GrandTotal"].apply(lambda x: round(
        abs(x), PriceRounding))
    df["Date"] = df["Date"].astype(str)
    df["CreatedDate"] = df["CreatedDate"].astype(str)
    df.loc[str(_("Total"))] = (
        df[
            [
                str(_("GrossAmount")),
                str(_("TotalTax")),
                str(_("BillDiscount")),
                str(_("GrandTotal")),

            ]
        ]
        .sum()
        .reindex(df.columns, fill_value="")
    )
    df = df.drop(["Cash"], axis=1)
    df.at["Total", 'LedgerName'] = "Total"
    json_records = df.reset_index().to_json(orient="records")
    details = json.loads(json_records)

    return df,details

def query_sales_both_report_data(
    CompanyID, BranchID, FromDate, ToDate, PriceRounding, UserID, EmployeeID,CustomerID,filterValue
):
    dic = {"BranchID": BranchID,"CompanyID": CompanyID,"ToDate": ToDate,"FromDate": FromDate,"PriceRounding": PriceRounding,"UserID": UserID,"EmployeeID": EmployeeID,"CustomerID": CustomerID,"filterValue":filterValue}
    cursor = connection.cursor()
    
    cursor.execute(
        """
            SELECT * FROM(SELECT * FROM(

            SELECT             
                                 
            S."id" AS id,          
            S."VoucherNo" AS VoucherNo,          
            S."Date" AS Date,
            S."CreatedDate" AS CreatedDate,          
            AL."LedgerName" AS LedgerName,          
            S."CustomerName" AS Name,                  
            CASE WHEN  
            S."EmployeeID" >0  THEN(SELECT NULLIF("FirstName", '') FROM public.employees_employees WHERE "EmployeeID" = S."EmployeeID" AND "CompanyID_id" = S."CompanyID_id")      
            WHEN S."EmployeeID" =0 THEN ''
            END AS SalesMan,
            round(S."TotalGrossAmt",2) AS NetAmount,          
            round(S."TotalTax",2) AS TotalTax,          
            round(S."TotalDiscount",2) AS BillDiscount,
            round(S."GrandTotal",2) AS GrandTotal,
            (select COALESCE (SUM("Debit"),0) from public."ledgerPostings_ledgerPosting" where "CompanyID_id" = S."CompanyID_id" AND "VoucherType"='SI'      
            AND "VoucherMasterID"=s."SalesMasterID"  
            AND "LedgerID" IN (Select "LedgerID" from public."accountLedger_accountLedger" where "CompanyID_id" = S."CompanyID_id" AND "AccountGroupUnder" IN (8,9))) AS Cash


            FROM public."salesMasters_salesMaster" AS S LEFT OUTER JOIN public."accountLedger_accountLedger" AS AL ON S."LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = S."CompanyID_id"     
            WHERE S."Status" != 'Cancelled' AND
            CASE WHEN %(CustomerID)s > 0 AND %(UserID)s > 0 AND %(EmployeeID)s > 0 THEN
            S."EmployeeID" = %(EmployeeID)s AND S."CreatedUserID" = %(UserID)s AND S."LedgerID" = %(CustomerID)s AND S."BranchID" = %(BranchID)s

            WHEN %(CustomerID)s > 0 AND %(UserID)s > 0 THEN
            S."CreatedUserID" = %(UserID)s AND S."LedgerID" = %(CustomerID)s AND S."BranchID" = %(BranchID)s

            WHEN %(CustomerID)s > 0 AND %(EmployeeID)s > 0 THEN
            S."EmployeeID" = %(EmployeeID)s AND S."LedgerID" = %(CustomerID)s AND S."BranchID" = %(BranchID)s

            WHEN %(UserID)s > 0 AND %(EmployeeID)s > 0 THEN
            S."EmployeeID" = %(EmployeeID)s AND S."CreatedUserID" = %(UserID)s AND S."BranchID" = %(BranchID)s
            
            WHEN %(CustomerID)s > 0 THEN 
            S."LedgerID" = %(CustomerID)s AND S."BranchID" = %(BranchID)s 
            WHEN %(EmployeeID)s > 0 THEN
            S."EmployeeID" = %(EmployeeID)s AND S."BranchID" = %(BranchID)s
            WHEN %(UserID)s > 0 THEN 
            S."CreatedUserID" = %(UserID)s AND S."BranchID" = %(BranchID)s 
            ELSE
            S."BranchID" = %(BranchID)s 
            END
            AND S."Date" BETWEEN %(FromDate)s AND %(ToDate)s AND S."CompanyID_id" = %(CompanyID)s         

            
            UNION ALL

            SELECT   
            S."id" AS id,          
            S."VoucherNo" AS VoucherNo,          
            S."VoucherDate" AS Date,
            S."CreatedDate" AS CreatedDate,          
            AL."LedgerName" AS LedgerName,          
            S."CustomerName" AS Name,                  
            CASE WHEN  
            S."EmployeeID" >0  THEN(SELECT NULLIF("FirstName", '') FROM public.employees_employees WHERE "EmployeeID" = S."EmployeeID" AND "CompanyID_id" = S."CompanyID_id")      
            WHEN S."EmployeeID" =0 THEN ''
            END AS SalesMan,
            round(S."TotalGrossAmt" * -1,2) AS NetAmount,          
            round(S."TotalTax" * -1,2) AS TotalTax,          
            round(S."TotalDiscount" * -1,2) AS BillDiscount,
            round(S."GrandTotal" * -1,2) AS GrandTotal,
            (select COALESCE (SUM("Credit"),0) from public."ledgerPostings_ledgerPosting" where "CompanyID_id" = S."CompanyID_id" AND "VoucherType"='SR'      
            AND "VoucherMasterID"=s."SalesReturnMasterID"  
            AND "LedgerID" IN (Select "LedgerID" from public."accountLedger_accountLedger" where "CompanyID_id" = S."CompanyID_id" AND "AccountGroupUnder" IN (8,9))) AS Cash
  

            FROM public."salesReturnMasters_salesReturnMaster" AS S LEFT OUTER JOIN public."accountLedger_accountLedger" AS AL ON S."LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = S."CompanyID_id"     
            WHERE S."CompanyID_id" = %(CompanyID)s AND
            CASE WHEN %(CustomerID)s > 0 AND %(UserID)s > 0 AND %(EmployeeID)s > 0 THEN
            S."EmployeeID" = %(EmployeeID)s AND S."CreatedUserID" = %(UserID)s AND S."LedgerID" = %(CustomerID)s AND S."BranchID" = %(BranchID)s

            WHEN %(CustomerID)s > 0 AND %(UserID)s > 0 THEN
            S."CreatedUserID" = %(UserID)s AND S."LedgerID" = %(CustomerID)s AND S."BranchID" = %(BranchID)s

            WHEN %(CustomerID)s > 0 AND %(EmployeeID)s > 0 THEN
            S."EmployeeID" = %(EmployeeID)s AND S."LedgerID" = %(CustomerID)s AND S."BranchID" = %(BranchID)s

            WHEN %(UserID)s > 0 AND %(EmployeeID)s > 0 THEN
            S."EmployeeID" = %(EmployeeID)s AND S."CreatedUserID" = %(UserID)s AND S."BranchID" = %(BranchID)s
            
            WHEN %(CustomerID)s > 0 THEN 
            S."LedgerID" = %(CustomerID)s AND S."BranchID" = %(BranchID)s 
            WHEN %(EmployeeID)s > 0 THEN
            S."EmployeeID" = %(EmployeeID)s AND S."BranchID" = %(BranchID)s
            WHEN %(UserID)s > 0 THEN 
            S."CreatedUserID" = %(UserID)s AND S."BranchID" = %(BranchID)s 
            ELSE
            S."BranchID" = %(BranchID)s 
            END
            AND S."VoucherDate" BETWEEN %(FromDate)s AND %(ToDate)s         

            ) as temp order by Date)
            as t where 
            CASE WHEN %(filterValue)s = 'cash' THEN
            Cash>0 
            WHEN %(filterValue)s = 'credit' THEN
            Cash=0.00
            ELSE
            Cash > 0 or Cash=0
            END


     """,
        dic,
    )
    
    data = cursor.fetchall()
    if cursor.rowcount == 0:
        data = [("","", "","", "NO DATA", "", "", 0,0,0,0,0)]
   
    df = pd.DataFrame(data)
    df.columns = [
        str(_("id")),
        str(_("VoucherNo")),
        str(_("Date")),
        str(_("CreatedDate")),
        str(_("LedgerName")),
        str(_("CustomerName")),
        str(_("EmployeeName")),
        str(_("GrossAmount")),
        str(_("TotalTax")),
        str(_("BillDiscount")),
        str(_("GrandTotal")),
        str(_("Cash")),
        # str(_("CashSales")),
        # str(_("BankSales")),
        # str(_("CreditSales")),
    ]
    # concert uuid to string
    convert_dict = {'id': str}
    df = df.astype(convert_dict)

    df["Date"] = df["Date"].astype(str)
    df["CreatedDate"] = df["CreatedDate"].astype(str)
    df.loc[str(_("Total"))] = (
        df[
            [
                str(_("GrossAmount")),
                str(_("TotalTax")),
                str(_("BillDiscount")),
                str(_("GrandTotal")),
                # str(_("CashSales")),
                # str(_("BankSales")),
                # str(_("CreditSales")),
            ]
        ]
        .sum()
        .reindex(df.columns, fill_value="")
    )
    df = df.drop(["Cash"], axis=1)
    df.at["Total", 'LedgerName'] = "Total"

    json_records = df.reset_index().to_json(orient="records")
    details = json.loads(json_records)

    return df,details

def query_salesReturn_report_data(
    CompanyID, BranchID, FromDate, ToDate, PriceRounding, UserID, EmployeeID,CustomerID,filterValue
):
    dic = {"BranchID": BranchID,"CompanyID": CompanyID,"ToDate": ToDate,"FromDate": FromDate,"PriceRounding": PriceRounding,"UserID": UserID,"EmployeeID": EmployeeID,"CustomerID": CustomerID,"filterValue":filterValue}

    cursor = connection.cursor()
    cursor.execute(
    """
        SELECT * FROM(
        SELECT                                  

        S."id" AS id,          
        S."VoucherNo" AS VoucherNo,          
        S."VoucherDate" AS Date,
        S."CreatedDate" AS CreatedDate,
        AL."LedgerName" AS LedgerName,          
        S."CustomerName" AS Name,                  
        CASE WHEN  
        S."EmployeeID" >0  THEN(SELECT NULLIF("FirstName", '') FROM public.employees_employees WHERE "EmployeeID" = S."EmployeeID" AND "CompanyID_id" = S."CompanyID_id")      
        WHEN S."EmployeeID" =0 THEN ''
        END AS SalesMan,
        round(S."TotalGrossAmt",2) AS NetAmount,          
        round(S."TotalTax",2) AS TotalTax,          
        round(S."TotalDiscount",2) AS BillDiscount,
        round(S."GrandTotal",2) AS GrandTotal,          

        (select COALESCE (SUM("Credit"),0) from public."ledgerPostings_ledgerPosting" where "CompanyID_id" = S."CompanyID_id" AND "VoucherType"='SR'      
        AND "VoucherMasterID"=s."SalesReturnMasterID"  
        AND "LedgerID" IN (Select "LedgerID" from public."accountLedger_accountLedger" where "CompanyID_id" = S."CompanyID_id" AND "AccountGroupUnder" IN (8,9))) AS Cash



        FROM public."salesReturnMasters_salesReturnMaster" AS S LEFT OUTER JOIN public."accountLedger_accountLedger" AS AL ON S."LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = S."CompanyID_id"     
        WHERE S."CompanyID_id" = %(CompanyID)s AND
        CASE WHEN %(CustomerID)s > 0 AND %(UserID)s > 0 AND %(EmployeeID)s > 0 THEN
        S."EmployeeID" = %(EmployeeID)s AND S."CreatedUserID" = %(UserID)s AND S."LedgerID" = %(CustomerID)s AND S."BranchID" = %(BranchID)s

        WHEN %(CustomerID)s > 0 AND %(UserID)s > 0 THEN
        S."CreatedUserID" = %(UserID)s AND S."LedgerID" = %(CustomerID)s AND S."BranchID" = %(BranchID)s

        WHEN %(CustomerID)s > 0 AND %(EmployeeID)s > 0 THEN
        S."EmployeeID" = %(EmployeeID)s AND S."LedgerID" = %(CustomerID)s AND S."BranchID" = %(BranchID)s

        WHEN %(UserID)s > 0 AND %(EmployeeID)s > 0 THEN
        S."EmployeeID" = %(EmployeeID)s AND S."CreatedUserID" = %(UserID)s AND S."BranchID" = %(BranchID)s
        
        WHEN %(CustomerID)s > 0 THEN 
        S."LedgerID" = %(CustomerID)s AND S."BranchID" = %(BranchID)s 
        WHEN %(EmployeeID)s > 0 THEN
        S."EmployeeID" = %(EmployeeID)s AND S."BranchID" = %(BranchID)s
        WHEN %(UserID)s > 0 THEN 
        S."CreatedUserID" = %(UserID)s AND S."BranchID" = %(BranchID)s 
        ELSE
        S."BranchID" = %(BranchID)s 
        END
        AND S."VoucherDate" BETWEEN %(FromDate)s AND %(ToDate)s         
        ORDER BY "SalesReturnMasterID"
        )
        as t where 
        CASE WHEN %(filterValue)s = 'cash' THEN
        Cash>0 
        WHEN %(filterValue)s = 'credit' THEN
        Cash=0
        ELSE
        Cash > 0 or Cash=0
        END
    """,
    dic,
    )
    data = cursor.fetchall()
    if cursor.rowcount == 0:
        data = [("","", "","", "NO DATA", "", "", 0,0,0,0,0)]
    df = pd.DataFrame(data)
    print(df)
    df.columns = [
        str(_("id")),
        str(_("VoucherNo")),
        str(_("Date")),
        str(_("CreatedDate")),
        str(_("LedgerName")),
        str(_("CustomerName")),
        str(_("EmployeeName")),
        str(_("GrossAmount")),
        str(_("TotalTax")),
        str(_("BillDiscount")),
        str(_("GrandTotal")),
        str(_("Cash")),

    ]
    # concert uuid to string
    convert_dict = {'id': str}
    df = df.astype(convert_dict)
    df["Date"] = df["Date"].astype(str)
    df["CreatedDate"] = df["CreatedDate"].astype(str)
    df.loc[str(_("Total"))] = (
        df[
            [
                str(_("GrossAmount")),
                str(_("TotalTax")),
                str(_("BillDiscount")),
                str(_("GrandTotal")),
            ]
        ]
        .sum()
        .reindex(df.columns, fill_value="")
    )
    df = df.drop(["Cash"], axis=1)
    df.at["Total", 'LedgerName'] = "Total"

    json_records = df.reset_index().to_json(orient="records")
    details = json.loads(json_records)
    return df,details

def query_purchase_report_data(
    CompanyID, BranchID, FromDate, ToDate, PriceRounding,ReffNo, UserID, EmployeeID,CustomerID,filterValue
):

    cursor = connection.cursor()
    if ReffNo:
        ReffNo = ReffNo
    else:
        ReffNo = None

    dic = {"BranchID": BranchID,"CompanyID": CompanyID,"ToDate": ToDate,"FromDate": FromDate,"PriceRounding": PriceRounding,"UserID": UserID,"EmployeeID": EmployeeID,"CustomerID": CustomerID,"filterValue":filterValue,"ReffNo":ReffNo}
    print(UserID,EmployeeID,CustomerID,filterValue,ReffNo,"***********PURCHASE***********")

    cursor.execute(
        ''' SELECT * FROM (SELECT           
        P."id" as id ,           
        P."VoucherNo" as VoucherNo ,           
        P."Date",            
        P."RefferenceBillNo",          
        P."VenderInvoiceDate" AS ReferenceDate,          
        AL."LedgerName" AS LedgerName,  
        P."CustomerName" AS CustomerName,            
        round(P."NetTotal",2) AS NetAmount,  
        round(P."TotalGrossAmt",2) AS GrossAmount, 
        round(P."TotalTax",2) AS TotalTax,  
        round(P."TotalDiscount",2) AS BillDiscount,    
        round(P."GrandTotal",2) AS GrandTotal,
        (select COALESCE (SUM("Credit"),0) from public."ledgerPostings_ledgerPosting" where "CompanyID_id" = P."CompanyID_id" AND "VoucherType"='PI'      
        AND "VoucherMasterID"=P."PurchaseMasterID"  
        AND "LedgerID" IN (Select "LedgerID" from public."accountLedger_accountLedger" where "CompanyID_id" = P."CompanyID_id" AND "AccountGroupUnder" IN (8,9))) AS Cash


        FROM public."purchaseMasters_purchaseMaster" AS P  
        INNER JOIN public."accountLedger_accountLedger" AS AL ON P."LedgerID" = AL."LedgerID" AND P."CompanyID_id" = AL."CompanyID_id"
        INNER JOIN public.auth_user AS U ON P."CreatedUserID" = U."id"  
        WHERE P."IsActive" = 'true' AND  
        P."Date" BETWEEN %(FromDate)s AND %(ToDate)s AND P."CompanyID_id" = %(CompanyID)s AND

        CASE WHEN %(CustomerID)s > 0 AND %(UserID)s > 0 AND %(EmployeeID)s > 0 AND %(ReffNo)s is not null THEN
        P."EmployeeID" = %(EmployeeID)s AND P."CreatedUserID" = %(UserID)s AND P."LedgerID" = %(CustomerID)s AND P."RefferenceBillNo" = %(ReffNo)s AND P."BranchID" = %(BranchID)s

        WHEN %(CustomerID)s > 0 AND %(UserID)s > 0 AND %(ReffNo)s is not null THEN
        P."CreatedUserID" = %(UserID)s AND P."LedgerID" = %(CustomerID)s AND p."RefferenceBillNo" = %(ReffNo)s AND P."BranchID" = %(BranchID)s

        WHEN %(CustomerID)s > 0 AND %(EmployeeID)s > 0 AND %(ReffNo)s is not null THEN
        P."EmployeeID" = %(EmployeeID)s AND P."LedgerID" = %(CustomerID)s AND p."RefferenceBillNo" = %(ReffNo)s AND P."BranchID" = %(BranchID)s

        WHEN %(UserID)s > 0 AND %(EmployeeID)s > 0 AND %(ReffNo)s is not null THEN
        P."EmployeeID" = %(EmployeeID)s AND P."CreatedUserID" = %(UserID)s AND p."RefferenceBillNo" = %(ReffNo)s AND P."BranchID" = %(BranchID)s
        


        WHEN %(CustomerID)s > 0 AND %(UserID)s > 0 THEN
        P."CreatedUserID" = %(UserID)s AND P."LedgerID" = %(CustomerID)s AND P."BranchID" = %(BranchID)s

        WHEN %(CustomerID)s > 0 AND %(EmployeeID)s > 0 THEN
        P."EmployeeID" = %(EmployeeID)s AND P."LedgerID" = %(CustomerID)s AND P."BranchID" = %(BranchID)s

        WHEN %(UserID)s > 0 AND %(EmployeeID)s > 0 THEN
        P."EmployeeID" = %(EmployeeID)s AND P."CreatedUserID" = %(UserID)s AND P."BranchID" = %(BranchID)s

        WHEN %(CustomerID)s > 0 AND %(ReffNo)s is not null THEN 
        P."LedgerID" = %(CustomerID)s AND p."RefferenceBillNo" = %(ReffNo)s AND P."BranchID" = %(BranchID)s 
        WHEN %(EmployeeID)s > 0 AND %(ReffNo)s is not null THEN
        P."EmployeeID" = %(EmployeeID)s AND p."RefferenceBillNo" = %(ReffNo)s AND P."BranchID" = %(BranchID)s
        WHEN %(UserID)s > 0 AND %(ReffNo)s is not null THEN 
        P."CreatedUserID" = %(UserID)s AND P."RefferenceBillNo" = %(ReffNo)s AND P."BranchID" = %(BranchID)s 



        WHEN %(CustomerID)s > 0 THEN 
        P."LedgerID" = %(CustomerID)s AND P."BranchID" = %(BranchID)s 
        WHEN %(EmployeeID)s > 0 THEN
        P."EmployeeID" = %(EmployeeID)s AND P."BranchID" = %(BranchID)s
        WHEN %(UserID)s > 0 THEN 
        P."CreatedUserID" = %(UserID)s AND P."BranchID" = %(BranchID)s 
        WHEN %(ReffNo)s is not null THEN 
        p."RefferenceBillNo" = %(ReffNo)s AND P."BranchID" = %(BranchID)s 
        
        ELSE
        P."BranchID" = %(BranchID)s 
        END
        ORDER BY "PurchaseMasterID")
        as t where 
        CASE WHEN %(filterValue)s = 'cash' THEN
        Cash>0 
        WHEN %(filterValue)s = 'credit' THEN
        Cash=0.00
        ELSE
        Cash > 0 or Cash=0
        END
        ''',
        dic,
    )
    data = cursor.fetchall()
    # else:
    #     cursor.execute(
    #         '''SELECT  
                   
    #         P."VoucherNo" as VoucherNo ,           
    #         P."Date",            
    #         P."RefferenceBillNo",          
    #         P."VenderInvoiceDate" AS ReferenceDate,          
    #         AL."LedgerName" AS LedgerName,  
    #         P."CustomerName" AS CustomerName,            
    #         round(P."NetTotal",2) AS NetAmount,  
    #         round(P."TotalGrossAmt",2) AS GrossAmount, 
    #         round(P."TotalTax",2) AS TotalTax,  
    #         round(P."TotalDiscount",2) AS BillDiscount,    
    #         round(P."GrandTotal",2) AS GrandTotal 

    #         FROM public."purchaseMasters_purchaseMaster" AS P  
    #         INNER JOIN public."accountLedger_accountLedger" AS AL ON P."LedgerID" = AL."LedgerID" AND P."CompanyID_id" = AL."CompanyID_id"
    #         INNER JOIN public.auth_user AS U ON P."CreatedUserID" = U."id"  
    #         WHERE P."BranchID" = %(BranchID)s AND P."IsActive" = 'true' AND  
    #         P."Date" BETWEEN %(FromDate)s AND %(ToDate)s AND P."CompanyID_id" = %(CompanyID)s
    #         ORDER BY "PurchaseMasterID"''',
    #         dic,
    #     )
        # data = cursor.fetchall()
    if cursor.rowcount == 0:
        data = [("", "","", "NO DATA", "", "", 0,0,0,0,0,0,0)]

    df = pd.DataFrame(data)
    df.columns = [
        str(_("id")),
        str(_("VoucherNo")),
        str(_("Date")),
        str(_("ReferenceNo")),
        str(_("ReferenceDate")),
        str(_("LedgerName")),
        str(_("CustomerName")),
        str(_("NetAmount")),
        str(_("GrossAmount")),
        str(_("TotalTax")),
        str(_("BillDiscount")),
        str(_("GrandTotal")),
        str(_("Cash")),

    ]
    # concert uuid to string
    convert_dict = {'id': str}
    df = df.astype(convert_dict)

    df = df.drop(["Cash"], axis=1)
    df["Date"] = df["Date"].astype(str)
    df["ReferenceDate"] = df["ReferenceDate"].astype(str)
    df.loc[str(_("Total"))] = (
        df[
            [
                str(_("NetAmount")),
                str(_("GrossAmount")),
                str(_("TotalTax")),
                str(_("BillDiscount")),
                str(_("GrandTotal")),
            ]
        ]
        .sum()
        .reindex(df.columns, fill_value="")
    )
    json_records = df.reset_index().to_json(orient="records")
    details = json.loads(json_records)
    return df,details

def query_purchaseReturn_report_data(
    CompanyID, BranchID, FromDate, ToDate, PriceRounding,ReffNo, UserID, EmployeeID,CustomerID,filterValue
):
    cursor = connection.cursor()

    if ReffNo:
        ReffNo = ReffNo
    else:
        ReffNo = None

    dic = {"BranchID": BranchID,"CompanyID": CompanyID,"ToDate": ToDate,"FromDate": FromDate,"PriceRounding": int(PriceRounding),"UserID": UserID,"EmployeeID": EmployeeID,"CustomerID": CustomerID,"filterValue":filterValue,"ReffNo":ReffNo}
    print(UserID,EmployeeID,CustomerID,filterValue,type(ReffNo),"***********RETURN***********")
    cursor.execute(
        '''SELECT * FROM (SELECT  
        P."id" as id ,           
        P."VoucherNo" as VoucherNo ,           
        P."VoucherDate" AS Date,            
        P."RefferenceBillNo",          
        P."RefferenceBillDate" AS ReferenceDate,          
        AL."LedgerName" AS LedgerName,  
        P."CustomerName" AS CustomerName,            
        round(P."NetTotal",2) AS NetAmount,  
        round(P."TotalGrossAmt",2) AS GrossAmount, 
        round(P."TotalTax",2) AS TotalTax,  
        round(P."TotalDiscount",2) AS BillDiscount,    
        round(P."GrandTotal",2) AS GrandTotal,
        (select COALESCE (SUM("Credit"),0) from public."ledgerPostings_ledgerPosting" where "CompanyID_id" = P."CompanyID_id" AND "VoucherType"='PR'      
        AND "VoucherMasterID"=P."PurchaseReturnMasterID"  
        AND "LedgerID" IN (Select "LedgerID" from public."accountLedger_accountLedger" where "CompanyID_id" = P."CompanyID_id" AND "AccountGroupUnder" IN (8,9))) AS Cash


        FROM public."purchaseReturnMasters_purchaseReturnMaster" AS P  
        INNER JOIN public."accountLedger_accountLedger" AS AL ON P."LedgerID" = AL."LedgerID" AND P."CompanyID_id" = AL."CompanyID_id"
        INNER JOIN public.auth_user AS U ON P."CreatedUserID" = U."id"  
        WHERE P."IsActive" = 'true' AND  
        P."VoucherDate" BETWEEN %(FromDate)s AND %(ToDate)s AND P."CompanyID_id" = %(CompanyID)s AND

        CASE WHEN %(CustomerID)s > 0 AND %(UserID)s > 0 AND %(EmployeeID)s > 0 AND %(ReffNo)s is not null THEN
        P."EmployeeID" = %(EmployeeID)s AND P."CreatedUserID" = %(UserID)s AND P."LedgerID" = %(CustomerID)s AND P."RefferenceBillNo" = %(ReffNo)s AND P."BranchID" = %(BranchID)s

        WHEN %(CustomerID)s > 0 AND %(UserID)s > 0 AND %(ReffNo)s is not null THEN
        P."CreatedUserID" = %(UserID)s AND P."LedgerID" = %(CustomerID)s AND p."RefferenceBillNo" = %(ReffNo)s AND P."BranchID" = %(BranchID)s

        WHEN %(CustomerID)s > 0 AND %(EmployeeID)s > 0 AND %(ReffNo)s is not null THEN
        P."EmployeeID" = %(EmployeeID)s AND P."LedgerID" = %(CustomerID)s AND p."RefferenceBillNo" = %(ReffNo)s AND P."BranchID" = %(BranchID)s

        WHEN %(UserID)s > 0 AND %(EmployeeID)s > 0 AND %(ReffNo)s is not null THEN
        P."EmployeeID" = %(EmployeeID)s AND P."CreatedUserID" = %(UserID)s AND p."RefferenceBillNo" = %(ReffNo)s AND P."BranchID" = %(BranchID)s
        
        WHEN %(CustomerID)s > 0 AND %(UserID)s > 0 AND %(EmployeeID)s > 0 THEN
        P."EmployeeID" = %(EmployeeID)s AND P."CreatedUserID" = %(UserID)s AND P."LedgerID" = %(CustomerID)s AND P."BranchID" = %(BranchID)s


        WHEN %(CustomerID)s > 0 AND %(UserID)s > 0 THEN
        P."CreatedUserID" = %(UserID)s AND P."LedgerID" = %(CustomerID)s AND P."BranchID" = %(BranchID)s

        WHEN %(CustomerID)s > 0 AND %(EmployeeID)s > 0 THEN
        P."EmployeeID" = %(EmployeeID)s AND P."LedgerID" = %(CustomerID)s AND P."BranchID" = %(BranchID)s

        WHEN %(UserID)s > 0 AND %(EmployeeID)s > 0 THEN
        P."EmployeeID" = %(EmployeeID)s AND P."CreatedUserID" = %(UserID)s AND P."BranchID" = %(BranchID)s

        WHEN %(CustomerID)s > 0 AND %(ReffNo)s is not null THEN 
        P."LedgerID" = %(CustomerID)s AND p."RefferenceBillNo" = %(ReffNo)s AND P."BranchID" = %(BranchID)s 
        WHEN %(EmployeeID)s > 0 AND %(ReffNo)s is not null THEN
        P."EmployeeID" = %(EmployeeID)s AND p."RefferenceBillNo" = %(ReffNo)s AND P."BranchID" = %(BranchID)s
        WHEN %(UserID)s > 0 AND %(ReffNo)s is not null THEN 
        P."CreatedUserID" = %(UserID)s AND P."RefferenceBillNo" = %(ReffNo)s AND P."BranchID" = %(BranchID)s 



        WHEN %(CustomerID)s > 0 THEN 
        P."LedgerID" = %(CustomerID)s AND P."BranchID" = %(BranchID)s 
        WHEN %(EmployeeID)s > 0 THEN
        P."EmployeeID" = %(EmployeeID)s AND P."BranchID" = %(BranchID)s
        WHEN %(UserID)s > 0 THEN 
        P."CreatedUserID" = %(UserID)s AND P."BranchID" = %(BranchID)s 
        WHEN %(ReffNo)s is not null THEN 
        p."RefferenceBillNo" = %(ReffNo)s AND P."BranchID" = %(BranchID)s         
        ELSE
        P."BranchID" = %(BranchID)s 
        END

        ORDER BY "PurchaseReturnMasterID")
        as t where 
        CASE WHEN %(filterValue)s = 'cash' THEN
        Cash>0 
        WHEN %(filterValue)s = 'credit' THEN
        Cash=0.00
        ELSE
        Cash > 0 or Cash=0
        END
        ''',
        dic,
    )
    data = cursor.fetchall()
    # else:
    #     cursor.execute(
    #         '''SELECT  
    #         P."VoucherNo" as VoucherNo ,           
    #         P."VoucherDate" AS Date,            
    #         P."RefferenceBillNo",          
    #         P."RefferenceBillDate" AS ReferenceDate,          
    #         AL."LedgerName" AS LedgerName,  
    #         P."CustomerName" AS CustomerName,            
    #         round(P."NetTotal",2) AS NetAmount,  
    #         round(P."TotalGrossAmt",2) AS GrossAmount, 
    #         round(P."TotalTax",2) AS TotalTax,  
    #         round(P."TotalDiscount",2) AS BillDiscount,    
    #         round(P."GrandTotal",2) AS GrandTotal  
    #         FROM public."purchaseReturnMasters_purchaseReturnMaster" AS P  
    #         INNER JOIN public."accountLedger_accountLedger" AS AL ON P."LedgerID" = AL."LedgerID" AND P."CompanyID_id" = AL."CompanyID_id"
    #         INNER JOIN public.auth_user AS U ON P."CreatedUserID" = U."id"  
    #         WHERE P."BranchID" = %(BranchID)s AND P."IsActive" = 'true' AND  
    #         P."VoucherDate" BETWEEN %(FromDate)s AND %(ToDate)s AND P."CompanyID_id" = %(CompanyID)s
    #         ORDER BY "PurchaseReturnMasterID"''',
    #         dic,
    #     )
    #     data = cursor.fetchall()
    if cursor.rowcount == 0:
        data = [("", "","", "NO DATA", "", "", 0,0,0,0,0,0,0)]

    df = pd.DataFrame(data)
    df.columns = [
        str(_("id")),
        str(_("VoucherNo")),
        str(_("Date")),
        str(_("ReferenceNo")),
        str(_("ReferenceDate")),
        str(_("LedgerName")),
        str(_("CustomerName")),
        str(_("NetAmount")),
        str(_("GrossAmount")),
        str(_("TotalTax")),
        str(_("BillDiscount")),
        str(_("GrandTotal")),
        str(_("Cash")),
    ]
    # concert uuid to string
    convert_dict = {'id': str}
    df = df.astype(convert_dict)

    df = df.drop(["Cash"], axis=1)
    df["Date"] = df["Date"].astype(str)
    df["ReferenceDate"] = df["ReferenceDate"].astype(str)
    df.loc[str(_("Total"))] = (
        df[
            [
                str(_("NetAmount")),
                str(_("GrossAmount")),
                str(_("TotalTax")),
                str(_("BillDiscount")),
                str(_("GrandTotal")),
            ]
        ]
        .sum()
        .reindex(df.columns, fill_value="")
    )
    json_records = df.reset_index().to_json(orient="records")
    details = json.loads(json_records)
    return df,details

def query_purchase_both_report_data(
    CompanyID, BranchID, FromDate, ToDate, PriceRounding,ReffNo, UserID, EmployeeID,CustomerID,filterValue
):

    if ReffNo:
        ReffNo = ReffNo
    else:
        ReffNo = None

    dic = {"BranchID": BranchID,"CompanyID": CompanyID,"ToDate": ToDate,"FromDate": FromDate,"PriceRounding": PriceRounding,"UserID": UserID,"EmployeeID": EmployeeID,"CustomerID": CustomerID,"filterValue":filterValue,"ReffNo":ReffNo}

    cursor = connection.cursor()
    cursor.execute(
        '''
        SELECT * FROM (SELECT * FROM (SELECT           
        P."id" as id ,           
        P."VoucherNo" as VoucherNo ,           
        P."Date" AS Date,            
        P."RefferenceBillNo",          
        P."VenderInvoiceDate" AS ReferenceDate,          
        AL."LedgerName" AS LedgerName,  
        P."CustomerName" AS CustomerName,            
        round(P."NetTotal",2) AS NetAmount,  
        round(P."TotalGrossAmt",2) AS GrossAmount, 
        round(P."TotalTax",2) AS TotalTax,  
        round(P."TotalDiscount",2) AS BillDiscount,    
        round(P."GrandTotal",2) AS GrandTotal,
        (select COALESCE (SUM("Credit"),0) from public."ledgerPostings_ledgerPosting" where "CompanyID_id" = P."CompanyID_id" AND "VoucherType"='PI'      
        AND "VoucherMasterID"=P."PurchaseMasterID"  
        AND "LedgerID" IN (Select "LedgerID" from public."accountLedger_accountLedger" where "CompanyID_id" = P."CompanyID_id" AND "AccountGroupUnder" IN (8,9))) AS Cash


        FROM public."purchaseMasters_purchaseMaster" AS P  
        INNER JOIN public."accountLedger_accountLedger" AS AL ON P."LedgerID" = AL."LedgerID" AND P."CompanyID_id" = AL."CompanyID_id"
        INNER JOIN public.auth_user AS U ON P."CreatedUserID" = U."id"  
        WHERE P."IsActive" = 'true' AND  
        P."Date" BETWEEN %(FromDate)s AND %(ToDate)s AND P."CompanyID_id" = %(CompanyID)s AND

        CASE WHEN %(CustomerID)s > 0 AND %(UserID)s > 0 AND %(EmployeeID)s > 0 AND %(ReffNo)s is not null THEN
        P."EmployeeID" = %(EmployeeID)s AND P."CreatedUserID" = %(UserID)s AND P."LedgerID" = %(CustomerID)s AND P."RefferenceBillNo" = %(ReffNo)s AND P."BranchID" = %(BranchID)s

        WHEN %(CustomerID)s > 0 AND %(UserID)s > 0 AND %(ReffNo)s is not null THEN
        P."CreatedUserID" = %(UserID)s AND P."LedgerID" = %(CustomerID)s AND p."RefferenceBillNo" = %(ReffNo)s AND P."BranchID" = %(BranchID)s

        WHEN %(CustomerID)s > 0 AND %(EmployeeID)s > 0 AND %(ReffNo)s is not null THEN
        P."EmployeeID" = %(EmployeeID)s AND P."LedgerID" = %(CustomerID)s AND p."RefferenceBillNo" = %(ReffNo)s AND P."BranchID" = %(BranchID)s

        WHEN %(UserID)s > 0 AND %(EmployeeID)s > 0 AND %(ReffNo)s is not null THEN
        P."EmployeeID" = %(EmployeeID)s AND P."CreatedUserID" = %(UserID)s AND p."RefferenceBillNo" = %(ReffNo)s AND P."BranchID" = %(BranchID)s
        


        WHEN %(CustomerID)s > 0 AND %(UserID)s > 0 THEN
        P."CreatedUserID" = %(UserID)s AND P."LedgerID" = %(CustomerID)s AND P."BranchID" = %(BranchID)s

        WHEN %(CustomerID)s > 0 AND %(EmployeeID)s > 0 THEN
        P."EmployeeID" = %(EmployeeID)s AND P."LedgerID" = %(CustomerID)s AND P."BranchID" = %(BranchID)s

        WHEN %(UserID)s > 0 AND %(EmployeeID)s > 0 THEN
        P."EmployeeID" = %(EmployeeID)s AND P."CreatedUserID" = %(UserID)s AND P."BranchID" = %(BranchID)s

        WHEN %(CustomerID)s > 0 AND %(ReffNo)s is not null THEN 
        P."LedgerID" = %(CustomerID)s AND p."RefferenceBillNo" = %(ReffNo)s AND P."BranchID" = %(BranchID)s 
        WHEN %(EmployeeID)s > 0 AND %(ReffNo)s is not null THEN
        P."EmployeeID" = %(EmployeeID)s AND p."RefferenceBillNo" = %(ReffNo)s AND P."BranchID" = %(BranchID)s
        WHEN %(UserID)s > 0 AND %(ReffNo)s is not null THEN 
        P."CreatedUserID" = %(UserID)s AND P."RefferenceBillNo" = %(ReffNo)s AND P."BranchID" = %(BranchID)s 



        WHEN %(CustomerID)s > 0 THEN 
        P."LedgerID" = %(CustomerID)s AND P."BranchID" = %(BranchID)s 
        WHEN %(EmployeeID)s > 0 THEN
        P."EmployeeID" = %(EmployeeID)s AND P."BranchID" = %(BranchID)s
        WHEN %(UserID)s > 0 THEN 
        P."CreatedUserID" = %(UserID)s AND P."BranchID" = %(BranchID)s 
        WHEN %(ReffNo)s is not null THEN 
        p."RefferenceBillNo" = %(ReffNo)s AND P."BranchID" = %(BranchID)s 
        
        ELSE
        P."BranchID" = %(BranchID)s 
        END

        UNION ALL

        SELECT  
        P."id" as id ,           
        P."VoucherNo" as VoucherNo ,           
        P."VoucherDate" AS Date,            
        P."RefferenceBillNo",          
        P."RefferenceBillDate" AS ReferenceDate,          
        AL."LedgerName" AS LedgerName,  
        P."CustomerName" AS CustomerName,            
        round(P."NetTotal" * -1,2) AS NetAmount,  
        round(P."TotalGrossAmt" * -1,2) AS GrossAmount, 
        round(P."TotalTax" * -1,2) AS TotalTax,  
        round(P."TotalDiscount" * -1,2) AS BillDiscount,    
        round(P."GrandTotal" * -1,2) AS GrandTotal,
        (select COALESCE (SUM("Credit"),0) from public."ledgerPostings_ledgerPosting" where "CompanyID_id" = P."CompanyID_id" AND "VoucherType"='PR'      
        AND "VoucherMasterID"=P."PurchaseReturnMasterID"  
        AND "LedgerID" IN (Select "LedgerID" from public."accountLedger_accountLedger" where "CompanyID_id" = P."CompanyID_id" AND "AccountGroupUnder" IN (8,9))) AS Cash


        FROM public."purchaseReturnMasters_purchaseReturnMaster" AS P  
        INNER JOIN public."accountLedger_accountLedger" AS AL ON P."LedgerID" = AL."LedgerID" AND P."CompanyID_id" = AL."CompanyID_id"
        INNER JOIN public.auth_user AS U ON P."CreatedUserID" = U."id"  
        WHERE P."IsActive" = 'true' AND  
        P."VoucherDate" BETWEEN %(FromDate)s AND %(ToDate)s AND P."CompanyID_id" = %(CompanyID)s AND

        CASE WHEN %(CustomerID)s > 0 AND %(UserID)s > 0 AND %(EmployeeID)s > 0 AND %(ReffNo)s is not null THEN
        P."EmployeeID" = %(EmployeeID)s AND P."CreatedUserID" = %(UserID)s AND P."LedgerID" = %(CustomerID)s AND P."RefferenceBillNo" = %(ReffNo)s AND P."BranchID" = %(BranchID)s

        WHEN %(CustomerID)s > 0 AND %(UserID)s > 0 AND %(ReffNo)s is not null THEN
        P."CreatedUserID" = %(UserID)s AND P."LedgerID" = %(CustomerID)s AND p."RefferenceBillNo" = %(ReffNo)s AND P."BranchID" = %(BranchID)s

        WHEN %(CustomerID)s > 0 AND %(EmployeeID)s > 0 AND %(ReffNo)s is not null THEN
        P."EmployeeID" = %(EmployeeID)s AND P."LedgerID" = %(CustomerID)s AND p."RefferenceBillNo" = %(ReffNo)s AND P."BranchID" = %(BranchID)s

        WHEN %(UserID)s > 0 AND %(EmployeeID)s > 0 AND %(ReffNo)s is not null THEN
        P."EmployeeID" = %(EmployeeID)s AND P."CreatedUserID" = %(UserID)s AND p."RefferenceBillNo" = %(ReffNo)s AND P."BranchID" = %(BranchID)s
        
        WHEN %(CustomerID)s > 0 AND %(UserID)s > 0 AND %(EmployeeID)s > 0 THEN
        P."EmployeeID" = %(EmployeeID)s AND P."CreatedUserID" = %(UserID)s AND P."LedgerID" = %(CustomerID)s AND P."BranchID" = %(BranchID)s


        WHEN %(CustomerID)s > 0 AND %(UserID)s > 0 THEN
        P."CreatedUserID" = %(UserID)s AND P."LedgerID" = %(CustomerID)s AND P."BranchID" = %(BranchID)s

        WHEN %(CustomerID)s > 0 AND %(EmployeeID)s > 0 THEN
        P."EmployeeID" = %(EmployeeID)s AND P."LedgerID" = %(CustomerID)s AND P."BranchID" = %(BranchID)s

        WHEN %(UserID)s > 0 AND %(EmployeeID)s > 0 THEN
        P."EmployeeID" = %(EmployeeID)s AND P."CreatedUserID" = %(UserID)s AND P."BranchID" = %(BranchID)s

        WHEN %(CustomerID)s > 0 AND %(ReffNo)s is not null THEN 
        P."LedgerID" = %(CustomerID)s AND p."RefferenceBillNo" = %(ReffNo)s AND P."BranchID" = %(BranchID)s 
        WHEN %(EmployeeID)s > 0 AND %(ReffNo)s is not null THEN
        P."EmployeeID" = %(EmployeeID)s AND p."RefferenceBillNo" = %(ReffNo)s AND P."BranchID" = %(BranchID)s
        WHEN %(UserID)s > 0 AND %(ReffNo)s is not null THEN 
        P."CreatedUserID" = %(UserID)s AND P."RefferenceBillNo" = %(ReffNo)s AND P."BranchID" = %(BranchID)s 



        WHEN %(CustomerID)s > 0 THEN 
        P."LedgerID" = %(CustomerID)s AND P."BranchID" = %(BranchID)s 
        WHEN %(EmployeeID)s > 0 THEN
        P."EmployeeID" = %(EmployeeID)s AND P."BranchID" = %(BranchID)s
        WHEN %(UserID)s > 0 THEN 
        P."CreatedUserID" = %(UserID)s AND P."BranchID" = %(BranchID)s 
        WHEN %(ReffNo)s is not null THEN 
        p."RefferenceBillNo" = %(ReffNo)s AND P."BranchID" = %(BranchID)s         
        ELSE
        P."BranchID" = %(BranchID)s 
        END)
        as temp order by Date)
        as t where 
        CASE WHEN %(filterValue)s = 'cash' THEN
        Cash>0 
        WHEN %(filterValue)s = 'credit' THEN
        Cash=0.00
        ELSE
        Cash > 0 or Cash=0
        END

        ''',
        dic,
    )
    data = cursor.fetchall()
    if cursor.rowcount == 0:
        data = [("", "","", "NO DATA", "", "", 0,0,0,0,0,0,0)]
    

    df = pd.DataFrame(data)
    df.columns = [
        str(_("id")),
        str(_("VoucherNo")),
        str(_("Date")),
        str(_("ReferenceNo")),
        str(_("ReferenceDate")),
        str(_("LedgerName")),
        str(_("CustomerName")),
        str(_("NetAmount")),
        str(_("GrossAmount")),
        str(_("TotalTax")),
        str(_("BillDiscount")),
        str(_("GrandTotal")),
        str(_("Cash")),
    ]
    # concert uuid to string
    convert_dict = {'id': str}
    df = df.astype(convert_dict)

    df = df.drop(["Cash"], axis=1)
    df["Date"] = df["Date"].astype(str)
    df["ReferenceDate"] = df["ReferenceDate"].astype(str)
    df.loc[str(_("Total"))] = (
        df[
            [
                str(_("NetAmount")),
                str(_("GrossAmount")),
                str(_("TotalTax")),
                str(_("BillDiscount")),
                str(_("GrandTotal")),
            ]
        ]
        .sum()
        .reindex(df.columns, fill_value="")
    )
    json_records = df.reset_index().to_json(orient="records")
    details = json.loads(json_records)
    return df,details

def query_outStandingReport_report_data(
    CompanyID, BranchID, PriceRounding, RouteLedgers, ToDate, VoucherType
):

    cursor = connection.cursor()
    if RouteLedgers and VoucherType == "null":
        cursor.execute(
            """ select "LedgerName",round(Debit,2),round(Credit,2) FROM(  
        SELECT LP."LedgerID" , Al."LedgerName", AL."LedgerCode",  
        Case WHEN (SUM(LP."Debit") -SUM(LP."Credit") < 0 ) THEN SUM(LP."Credit") -SUM(LP."Debit") Else 0 end AS Credit ,    
        Case WHEN(SUM(LP."Debit") -SUM(LP."Credit") > 0 ) THEN SUM(LP."Debit") -SUM(LP."Credit") Else 0 end AS Debit  
        from public."ledgerPostings_ledgerPosting" AS LP  
        INNER JOIN public.parties_parties AS P ON LP."BranchID" = P."BranchID"  and lp."LedgerID" = P."LedgerID"
            AND P."CompanyID_id" = LP."CompanyID_id"
                INNER JOIN public."accountLedger_accountLedger" AS AL ON LP."LedgerID" = AL."LedgerID" 
                AND LP."CompanyID_id" = AL."CompanyID_id" 
            where LP."CompanyID_id" = %s
            AND AL."AccountGroupUnder" in (10, 29) AND LP."Date" <= %s  AND P."RouteID" in %s
        GROUP BY LP."LedgerID", Al."LedgerName",AL."LedgerCode")     
        AS Temp  
        """,
            [CompanyID, ToDate, RouteLedgers],
        )
    elif RouteLedgers and VoucherType == "creditors":
        cursor.execute(
            """ select "LedgerName",round(Debit,2),round(Credit,2) FROM(  
            SELECT Al."LedgerName",  
            Case WHEN (SUM(LP."Debit") -SUM(LP."Credit") < 0 ) THEN SUM(LP."Credit") -SUM(LP."Debit") Else 0 end AS Credit ,    
            Case WHEN(SUM(LP."Debit") -SUM(LP."Credit") > 0 ) THEN SUM(LP."Debit") -SUM(LP."Credit") Else 0 end AS Debit  
            from public."ledgerPostings_ledgerPosting" AS LP  
            INNER JOIN public.parties_parties AS P ON LP."BranchID" = P."BranchID"  and lp."LedgerID" = P."LedgerID"
                AND P."CompanyID_id" = LP."CompanyID_id"
                    INNER JOIN public."accountLedger_accountLedger" AS AL ON LP."LedgerID" = AL."LedgerID" 
                    AND LP."CompanyID_id" = AL."CompanyID_id" 
                where LP."Date" <= %s AND LP."CompanyID_id" = %s
                AND AL."AccountGroupUnder" in (10, 29)  AND P."RouteID" in %s 
            GROUP BY LP."LedgerID", Al."LedgerName",AL."LedgerCode"
            ) AS Temp  where Credit != 0  
            """,
            [ToDate, CompanyID, RouteLedgers],
        )
    elif RouteLedgers and VoucherType == "debitors":

        cursor.execute(
            """ select "LedgerName",round(Debit,2),round(Credit,2) FROM(  
            SELECT Al."LedgerName",  
            Case WHEN (SUM(LP."Debit") -SUM(LP."Credit") < 0 ) THEN SUM(LP."Credit") -SUM(LP."Debit") Else 0 end AS Credit ,    
            Case WHEN(SUM(LP."Debit") -SUM(LP."Credit") > 0 ) THEN SUM(LP."Debit") -SUM(LP."Credit") Else 0 end AS Debit  
            from public."ledgerPostings_ledgerPosting" AS LP  
            INNER JOIN public.parties_parties AS P ON LP."BranchID" = P."BranchID"  and lp."LedgerID" = P."LedgerID"
                AND P."CompanyID_id" = LP."CompanyID_id"
                    INNER JOIN public."accountLedger_accountLedger" AS AL ON LP."LedgerID" = AL."LedgerID" 
                    AND LP."CompanyID_id" = AL."CompanyID_id" 
                where LP."Date" <= %s AND LP."CompanyID_id" = %s
                AND AL."AccountGroupUnder" in (10, 29)  AND P."RouteID" in %s 
            GROUP BY LP."LedgerID", Al."LedgerName",AL."LedgerCode"
            ) AS Temp     where Debit != 0  
            """,
            [ToDate, CompanyID, RouteLedgers],
        )
    elif RouteLedgers and VoucherType == "zero_balance":

        cursor.execute(
            """ select "LedgerName",round(Debit,2),round(Credit,2) FROM(  
            SELECT Al."LedgerName",  
            Case WHEN (SUM(LP."Debit") -SUM(LP."Credit") < 0 ) THEN SUM(LP."Credit") -SUM(LP."Debit") Else 0 end AS Credit ,    
            Case WHEN(SUM(LP."Debit") -SUM(LP."Credit") > 0 ) THEN SUM(LP."Debit") -SUM(LP."Credit") Else 0 end AS Debit  
            from public."ledgerPostings_ledgerPosting" AS LP  
            INNER JOIN public.parties_parties AS P ON LP."BranchID" = P."BranchID"  and lp."LedgerID" = P."LedgerID"
                AND P."CompanyID_id" = LP."CompanyID_id"
                    INNER JOIN public."accountLedger_accountLedger" AS AL ON LP."LedgerID" = AL."LedgerID" 
                    AND LP."CompanyID_id" = AL."CompanyID_id" 
                where LP."Date" <= %s AND LP."CompanyID_id" = %s
                AND AL."AccountGroupUnder" in (10, 29)  AND P."RouteID" in %s 
            GROUP BY LP."LedgerID", Al."LedgerName",AL."LedgerCode"
            ) AS Temp     where Debit-Credit = 0  
            """,
            [ToDate, CompanyID, RouteLedgers],
        )
    elif VoucherType == "creditors":

        cursor.execute(
            """ select "LedgerName",round(Debit,2),round(Credit,2) FROM(  
            SELECT Al."LedgerName",  
            Case WHEN (SUM(LP."Debit") -SUM(LP."Credit") < 0 ) THEN SUM(LP."Credit") -SUM(LP."Debit") Else 0 end AS Credit ,    
            Case WHEN(SUM(LP."Debit") -SUM(LP."Credit") > 0 ) THEN SUM(LP."Debit") -SUM(LP."Credit") Else 0 end AS Debit  
            from public."ledgerPostings_ledgerPosting" AS LP  
            INNER JOIN public.parties_parties AS P ON LP."BranchID" = P."BranchID"  and lp."LedgerID" = P."LedgerID"
                AND P."CompanyID_id" = LP."CompanyID_id"
                    INNER JOIN public."accountLedger_accountLedger" AS AL ON LP."LedgerID" = AL."LedgerID" 
                    AND LP."CompanyID_id" = AL."CompanyID_id" 
                where LP."Date" <= %s AND LP."CompanyID_id" = %s
                AND AL."AccountGroupUnder" in (10, 29)
            GROUP BY LP."LedgerID", Al."LedgerName",AL."LedgerCode"
            ) AS Temp     where Credit != 0  
            """,
            [ToDate, CompanyID],
        )
    elif VoucherType == "debitors":

        cursor.execute(
            """ select "LedgerName",round(Debit,2),round(Credit,2) FROM(  
            SELECT Al."LedgerName",  
            Case WHEN (SUM(LP."Debit") -SUM(LP."Credit") < 0 ) THEN SUM(LP."Credit") -SUM(LP."Debit") Else 0 end AS Credit ,    
            Case WHEN(SUM(LP."Debit") -SUM(LP."Credit") > 0 ) THEN SUM(LP."Debit") -SUM(LP."Credit") Else 0 end AS Debit  
            from public."ledgerPostings_ledgerPosting" AS LP  
            INNER JOIN public.parties_parties AS P ON LP."BranchID" = P."BranchID"  and lp."LedgerID" = P."LedgerID"
                AND P."CompanyID_id" = LP."CompanyID_id"
                    INNER JOIN public."accountLedger_accountLedger" AS AL ON LP."LedgerID" = AL."LedgerID" 
                    AND LP."CompanyID_id" = AL."CompanyID_id" 
                where LP."Date" <= %s AND LP."CompanyID_id" = %s
                AND AL."AccountGroupUnder" in (10, 29)
            GROUP BY LP."LedgerID", Al."LedgerName",AL."LedgerCode"
            ) AS Temp     where Debit != 0  
            """,
            [ToDate, CompanyID],
        )
    elif VoucherType == "zero_balance":

        cursor.execute(
            """ select "LedgerName",round(Debit,2),round(Credit,2) FROM(  
            SELECT Al."LedgerName",  
            Case WHEN (SUM(LP."Debit") -SUM(LP."Credit") < 0 ) THEN SUM(LP."Credit") -SUM(LP."Debit") Else 0 end AS Credit ,    
            Case WHEN(SUM(LP."Debit") -SUM(LP."Credit") > 0 ) THEN SUM(LP."Debit") -SUM(LP."Credit") Else 0 end AS Debit  
            from public."ledgerPostings_ledgerPosting" AS LP  
            INNER JOIN public.parties_parties AS P ON LP."BranchID" = P."BranchID"  and lp."LedgerID" = P."LedgerID"
                AND P."CompanyID_id" = LP."CompanyID_id"
                    INNER JOIN public."accountLedger_accountLedger" AS AL ON LP."LedgerID" = AL."LedgerID" 
                    AND LP."CompanyID_id" = AL."CompanyID_id" 
                where LP."Date" <= %s AND LP."CompanyID_id" = %s
                AND AL."AccountGroupUnder" in (10, 29)
            GROUP BY LP."LedgerID", Al."LedgerName",AL."LedgerCode"
            ) AS Temp  where Debit-Credit = 0  
            """,
            [ToDate, CompanyID],
        )
    elif VoucherType == "null" or VoucherType == None:
        cursor.execute(
            """ select "LedgerName",round(Debit,2),round(Credit,2) FROM(  
            SELECT Al."LedgerName",
            Case WHEN (SUM(LP."Debit") -SUM(LP."Credit") < 0 ) THEN SUM(LP."Credit") -SUM(LP."Debit") Else 0 end AS Credit ,    
            Case WHEN(SUM(LP."Debit") -SUM(LP."Credit") > 0 ) THEN SUM(LP."Debit") -SUM(LP."Credit") Else 0 end AS Debit  
            from public."ledgerPostings_ledgerPosting" AS LP  
            INNER JOIN public.parties_parties AS P ON LP."BranchID" = P."BranchID"  and lp."LedgerID" = P."LedgerID"
                AND P."CompanyID_id" = LP."CompanyID_id"
                    INNER JOIN public."accountLedger_accountLedger" AS AL ON LP."LedgerID" = AL."LedgerID" 
                    AND LP."CompanyID_id" = AL."CompanyID_id" 
                where LP."Date" <= %s AND LP."CompanyID_id" = %s
                AND AL."AccountGroupUnder" in (10, 29)
            GROUP BY LP."LedgerID", Al."LedgerName",AL."LedgerCode"
            ) AS Temp  where Debit-Credit != 0  
            """,
            [ToDate, CompanyID],
        )
    data = cursor.fetchall()
    # df = pd.DataFrame(data)
    # df.columns = [
    #         str(_('LedgerName')), str(_('Debit')),str(_('Credit'))]
    # df.loc[str(_('Total'))] = df[['Debit','Credit']].sum().reindex(df.columns, fill_value='')
    # # df.at[len(df.index)-1,'LedgerName'] = "Total"
    # json_records = df.reset_index().to_json(orient ='records')
    # details = json.loads(json_records)
    return data


def query_salesSummary_report_data(
    CompanyID, BranchID, FromDate, ToDate, PriceRounding, UserID, WareHouseID, LedgerID
):
    cursor = connection.cursor()

    if not UserID=="0" and not UserID == 0:
        UserID = UserTable.objects.get(pk=UserID).customer.user.id
    dic = {
        "CompanyID": CompanyID,
        "BranchID": BranchID,
        "FromDate": FromDate,
        "ToDate": ToDate,
        "PriceRounding":PriceRounding,
        "UserID": UserID,
        "WareHouseID": WareHouseID,
        "LedgerID": LedgerID,
    }

    cursor.execute(
        """SELECT *,round(GrandTotal-CashSales-BankSales,2) AS CreditSales FROM(
    SELECT                                  
        
        S."VoucherNo" AS VoucherNo,          
        S."Date",
        AL."LedgerName" AS LedgerName,          
        CASE WHEN  
        S."EmployeeID" >0  THEN(SELECT NULLIF("FirstName", '') FROM public.employees_employees WHERE "EmployeeID" = S."EmployeeID" AND "CompanyID_id" = S."CompanyID_id")      
        WHEN S."EmployeeID" =0 THEN ''
        END AS SalesMan,
        round(S."TotalGrossAmt",2) AS NetAmount,          
        round(S."TotalTax",2) AS TotalTax,          
        round(S."TotalDiscount",2) AS BillDiscount,
        round(S."GrandTotal",2) AS GrandTotal,          

    round(
        (Select COALESCE(SUM("Debit" - "Credit"),0) FROM public."ledgerPostings_ledgerPosting" where "VoucherType"='SI'      
                AND "VoucherMasterID"=s."SalesMasterID" AND "BranchID" = S."BranchID"
        AND "CompanyID_id" = S."CompanyID_id"
        AND "LedgerID" IN       
            (Select "LedgerID" FROM public."accountLedger_accountLedger" where "AccountGroupUnder"=9 AND "CompanyID_id" = S."CompanyID_id")),2) AS CashSales,
    
    round(
    (Select COALESCE(SUM("Debit" - "Credit"),0) FROM public."ledgerPostings_ledgerPosting" where "VoucherType"='SI'      
                AND "VoucherMasterID"=s."SalesMasterID" AND "BranchID" = S."BranchID"
        AND "CompanyID_id" = S."CompanyID_id"
        AND "LedgerID" IN       
            (Select "LedgerID" FROM public."accountLedger_accountLedger" where "AccountGroupUnder"=8 AND "CompanyID_id" = S."CompanyID_id")),2) AS BankSales
                
        FROM public."salesMasters_salesMaster" AS S LEFT OUTER JOIN public."accountLedger_accountLedger" AS AL ON S."LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = S."CompanyID_id"     
        
        WHERE S."BranchID" = %(BranchID)s AND 
        
        CASE WHEN %(UserID)s > 0 AND %(WareHouseID)s > 0 AND %(LedgerID)s > 0 THEN
        S."Status" != 'Cancelled' AND S."CreatedUserID" = %(UserID)s AND S."WarehouseID" = %(WareHouseID)s AND S."LedgerID" = %(LedgerID)s
        WHEN %(UserID)s > 0 AND %(WareHouseID)s > 0 THEN
        S."Status" != 'Cancelled' AND S."CreatedUserID" = %(UserID)s AND S."WarehouseID" = %(WareHouseID)s 
        WHEN %(UserID)s > 0 AND %(LedgerID)s > 0 THEN
        S."Status" != 'Cancelled' AND S."CreatedUserID" = %(UserID)s AND S."LedgerID" = %(LedgerID)s 
        WHEN %(WareHouseID)s > 0 AND %(LedgerID)s > 0 THEN
        S."Status" != 'Cancelled' AND S."WarehouseID" = %(WareHouseID)s AND S."LedgerID" = %(LedgerID)s 

        WHEN %(UserID)s > 0 AND %(WareHouseID)s = 0 AND %(LedgerID)s = 0 THEN
        S."Status" != 'Cancelled' AND S."CreatedUserID" = %(UserID)s 
        WHEN %(UserID)s > 0 AND %(WareHouseID)s = 0 THEN
        S."Status" != 'Cancelled' AND S."CreatedUserID" = %(UserID)s 
        WHEN %(UserID)s > 0 AND %(LedgerID)s = 0 THEN
        S."Status" != 'Cancelled' AND S."CreatedUserID" = %(UserID)s 

        WHEN %(UserID)s > 0 THEN
        S."Status" != 'Cancelled' AND S."CreatedUserID" = %(UserID)s 
        WHEN %(WareHouseID)s > 0 THEN
        S."Status" != 'Cancelled' AND S."WarehouseID" = %(WareHouseID)s
        WHEN %(LedgerID)s > 0 THEN
        S."Status" != 'Cancelled' AND S."LedgerID" = %(LedgerID)s 
        ELSE
        S."Status" != 'Cancelled'
        END

        AND S."Date" BETWEEN %(FromDate)s AND %(ToDate)s AND S."CompanyID_id" = %(CompanyID)s         
        ORDER BY "SalesMasterID"
    ) as t """,
        dic,
    )
    data = cursor.fetchall()
  
    if cursor.rowcount == 0:
        data = [("", "", "NO DATA", "", "","","", 0, 0, 0, 0)]

    df = pd.DataFrame(data)
    df.columns = [
        str(_("VoucherNo")),
        str(_("VoucherDate")),
        str(_("LedgerName")),
        str(_("EmployeeName")),
        str(_("GrossAmount")),
        str(_("TotalTax")),
        str(_("BillDiscount")),
        str(_("GrandTotal")),
        str(_("CashSales")),
        str(_("BankSales")),
        str(_("CreditSales")),
    ]
    df["VoucherDate"] = df["VoucherDate"].astype(str)
    df.loc[str(_("Total"))] = (
        df[
            [
                str(_("GrossAmount")),
                str(_("TotalTax")),
                str(_("BillDiscount")),
                str(_("GrandTotal")),
                str(_("CashSales")),
                str(_("BankSales")),
                str(_("CreditSales")),
            ]
        ]
        .sum()
        .reindex(df.columns, fill_value="")
    )
    json_records = df.reset_index().to_json(orient="records")
    details = json.loads(json_records)
    return df,details


def query_stock_report_data(
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
):
    cursor = connection.cursor()
    dic = {
        "ProductID": ProductID,
        "BranchID": BranchID,
        "FromDate": FromDate,
        "ToDate": ToDate,
        "CompanyID": CompanyID,
        "StockFilter": StockFilter,
        "Barcode": Barcode,
        "CategoryID": CategoryID,
        "GroupID": GroupID,
        "WareHouseID": WareHouseID,
        "BrandID": BrandID,
        "PriceRounding":PriceRounding,
    }
    if ProductFilter == "1":
        cursor.execute(
            """SELECT * from (
            SELECT   
            P."StockReOrder" AS StockReOrder,
            P."StockMaximum" AS StockMaximum,
            P."StockMinimum" AS StockMinimum,
            P."ProductCode",
            PL."AutoBarcode" AS AutoBarcode,
            PL."Barcode" AS Barcode,
            P."ProductName",
        
            CASE WHEN %(ProductID)s > 0 AND %(WareHouseID)s > 0 THEN
            (SELECT NULLIF(round(SUM(SP."QtyIn"),2) - round(SUM(SP."QtyOut"),2),0)
            FROM public."stockPosting_stockPosting" AS SP WHERE SP."CompanyID_id" = P."CompanyID_id" AND SP."ProductID" = %(ProductID)s AND SP."WareHouseID" = %(WareHouseID)s AND SP."IsActive" = 'true' AND SP."BranchID" = '1' AND SP."Date" <= %(ToDate)s)  
            WHEN %(ProductID)s > 0 THEN
            (SELECT NULLIF(round(SUM(SP."QtyIn"),2) - round(SUM(SP."QtyOut"),2),0)
            FROM public."stockPosting_stockPosting" AS SP WHERE SP."CompanyID_id" = P."CompanyID_id" AND SP."ProductID" = %(ProductID)s AND SP."IsActive" = 'true' AND SP."BranchID" = '1' AND SP."Date" <= %(ToDate)s)  
            WHEN %(WareHouseID)s > 0 THEN
            (SELECT NULLIF(round(SUM(SP."QtyIn"),2) - round(SUM(SP."QtyOut"),2),0)
            FROM public."stockPosting_stockPosting" AS SP WHERE SP."CompanyID_id" = P."CompanyID_id" AND SP."ProductID" = P."ProductID" AND SP."WareHouseID" = %(WareHouseID)s AND SP."IsActive" = 'true' AND SP."BranchID" = '1' AND SP."Date" <= %(ToDate)s)  
            ELSE
            (SELECT NULLIF(round(SUM(SP."QtyIn"),2) - round(SUM(SP."QtyOut"),2),0)
            FROM public."stockPosting_stockPosting" AS SP WHERE SP."CompanyID_id" = P."CompanyID_id" AND SP."ProductID" = P."ProductID" AND SP."IsActive" = 'true' AND SP."BranchID" = '1' AND SP."Date" <= %(ToDate)s)  
            END AS CurrentStock,

            (SELECT NULLIF("UnitName", '') FROM public."units_unit" AS UN WHERE UN."CompanyID_id" = P."CompanyID_id" AND UN."UnitID" = PL."UnitID" AND PL."DefaultUnit" = 'true'  ) AS BaseUnitName,

            (SELECT coalesce(round("MultiFactor", '0'),%(PriceRounding)s) FROM public."pricelist_pricelist" AS UN WHERE UN."CompanyID_id" = P."CompanyID_id" AND UN."ProductID" = PL."ProductID" AND UN."UnitInReports" = 'true')AS StockInBaseUnit,
            


            (SELECT NULLIF("UnitName", '') FROM public."units_unit" AS UN INNER JOIN public.pricelist_pricelist as AA ON  AA."BranchID" = '1' AND 
            CASE WHEN %(ProductID)s > 0 THEN
            AA."ProductID" = %(ProductID)s AND AA."UnitInReports" = 'true' 
            ELSE
            AA."ProductID" = P."ProductID" AND AA."UnitInReports" = 'true' 
            END
            
            AND UN."UnitID" = AA."UnitID" AND
             AA."CompanyID_id" = P."CompanyID_id" WHERE UN."CompanyID_id" = P."CompanyID_id")
            AS UnitName,

            PG."GroupName",
            (SELECT NULLIF("CategoryName", '') FROM public."productcategory_productcategory" AS C WHERE C."CompanyID_id" = P."CompanyID_id" AND C."ProductCategoryID" = PG."CategoryID" )
            AS CategoryName,
            (SELECT NULLIF("BrandName", '') FROM public."brands_brand" AS B WHERE B."CompanyID_id" = P."CompanyID_id" AND B."BrandID" = P."BrandID" )
            AS BrandName,



            round(PL."PurchasePrice",%(PriceRounding)s),
            round(PL."SalesPrice",%(PriceRounding)s)
        
            FROM public.products_product as P  
            INNER JOIN public.pricelist_pricelist as PL ON P."ProductID" = PL."ProductID" AND P."BranchID" = '1' AND
            PL."DefaultUnit" = 'true' AND P."CompanyID_id" = PL."CompanyID_id"  
            INNER JOIN  public.productgroup_productgroup as PG on PG."ProductGroupID" = P."ProductGroupID" AND P."CompanyID_id" = PG."CompanyID_id"
            
            WHERE P."CompanyID_id" = %(CompanyID)s AND
            CASE WHEN %(ProductID)s > 0 THEN
            P."ProductID" = %(ProductID)s
            WHEN %(Barcode)s > 0 THEN
            PL."AutoBarcode" = %(Barcode)s
            WHEN %(CategoryID)s > 0 THEN
            P."ProductGroupID" IN(SELECT "ProductGroupID" FROM public."productgroup_productgroup" WHERE "CategoryID" = %(CategoryID)s AND "CompanyID_id" = %(CompanyID)s) AND P."ProductID" = PL."ProductID" 
            WHEN %(GroupID)s > 0 THEN
            P."ProductGroupID" = %(GroupID)s AND P."ProductID" = PL."ProductID"
            WHEN %(BrandID)s > 0 THEN
            P."BrandID" = %(BrandID)s AND P."ProductID" = PL."ProductID"
            ELSE
            P."ProductID" = PL."ProductID"
           
            END            
            ) as t where 
            CASE WHEN %(StockFilter)s = 1 THEN
            CurrentStock <> 0 or CurrentStock is null or CurrentStock = 0
            WHEN %(StockFilter)s = 2 THEN
            CurrentStock > 0 and CurrentStock is not null
            WHEN %(StockFilter)s = 3 THEN
            CurrentStock < 0 and CurrentStock is not null
            WHEN %(StockFilter)s = 4 THEN
            CurrentStock = 0 or CurrentStock is null
            WHEN %(StockFilter)s = 5 THEN
            CurrentStock < StockReOrder and CurrentStock is not null
            WHEN %(StockFilter)s = 6 THEN
            CurrentStock > StockMaximum and CurrentStock is not null
            WHEN %(StockFilter)s = 7 THEN
            CurrentStock < StockMinimum and CurrentStock is not null
            ELSE
            CurrentStock != 0 and CurrentStock is not null
            END


        """,
            dic,
        )
    elif ProductFilter == "2":
        cursor.execute(
            """SELECT * from (
            SELECT   
            P."ProductCode",
            PL."AutoBarcode" AS AutoBarcode,
            PL."Barcode" AS Barcode,
            P."ProductName",
        
            (SELECT NULLIF(round(SUM(SP."QtyIn"),2) - round(SUM(SP."QtyOut"),2),0)
            FROM public."stockPosting_stockPosting" AS SP WHERE SP."CompanyID_id" = P."CompanyID_id" AND SP."ProductID" = P."ProductID" AND SP."IsActive" = 'true' AND SP."BranchID" = '1' AND SP."Date" <= %(ToDate)s)  AS CurrentStock,
            
            (SELECT NULLIF("UnitName", '') FROM public."units_unit" AS UN WHERE UN."CompanyID_id" = P."CompanyID_id" AND UN."UnitID" = PL."UnitID" AND PL."DefaultUnit" = 'true'  ) AS BaseUnitName,


            (SELECT coalesce(round("MultiFactor", '0'),2) FROM public."pricelist_pricelist" AS UN WHERE UN."CompanyID_id" = P."CompanyID_id" AND UN."ProductID" = PL."ProductID" AND UN."UnitInReports" = 'true') AS MultiFactor,
            


            (SELECT NULLIF("UnitName", '') FROM public."units_unit" AS UN INNER JOIN public.pricelist_pricelist as AA ON  AA."BranchID" = '1' AND 
            AA."ProductID" = P."ProductID" AND AA."UnitInReports" = 'true' 
            AND UN."UnitID" = AA."UnitID" AND
             AA."CompanyID_id" = P."CompanyID_id" WHERE UN."CompanyID_id" = P."CompanyID_id")
            AS UnitName,



            PG."GroupName",
            (SELECT NULLIF("CategoryName", '') FROM public."productcategory_productcategory" AS C WHERE C."CompanyID_id" = P."CompanyID_id" AND C."ProductCategoryID" = PG."CategoryID" )
            AS CategoryName,
            (SELECT NULLIF("BrandName", '') FROM public."brands_brand" AS B WHERE B."CompanyID_id" = P."CompanyID_id" AND B."BrandID" = P."BrandID" )
            AS BrandName,


            round(PL."PurchasePrice",%(PriceRounding)s),
            round(PL."SalesPrice",%(PriceRounding)s)

            FROM public.products_product as P  
            INNER JOIN public.pricelist_pricelist as PL ON P."ProductID" = PL."ProductID" AND P."BranchID" = PL."BranchID" AND
            PL."DefaultUnit" = 'true' AND P."CompanyID_id" = PL."CompanyID_id"  
            INNER JOIN  public.productgroup_productgroup as PG on PG."ProductGroupID" = P."ProductGroupID" AND P."CompanyID_id" = PG."CompanyID_id"

            
            WHERE P."CompanyID_id" = %(CompanyID)s AND P."ProductID" = PL."ProductID"
            ) as t where CurrentStock != 0 and CurrentStock is not null
        """,
            dic,
        )

    data = cursor.fetchall()

    if cursor.rowcount == 0:
        data = [("", "", "NO DATA", "", "","","","", 0, 0, "", "", "", "", "", "")]

    df = pd.DataFrame(data)
    df = df.drop([0, 1, 2], axis=1)
    df.columns = [
        str(_("ProductCode")),
        str(_("Barcode")),
        str(_("M Barcode")),
        str(_("ProductName")),
        str(_("StockInBaseUnit")),
        str(_("BaseUnitName")),
        str(_("CurrentStock")),
        str(_("UnitName")),
        str(_("GroupName")),
        str(_("CategoryName")),
        str(_("BrandName")),
        str(_("PurchasePrice")),
        str(_("SalesPrice")),
    ]
    
    if df['CurrentStock'].eq(0).any():
        sum_column = 0
    else:
        sum_column = df["StockInBaseUnit"] / df["CurrentStock"]
    df["CurrentStock"] = sum_column
    df.loc[str(_("Total"))] = (
        df[["CurrentStock","StockInBaseUnit"]].sum().reindex(df.columns, fill_value="")
    )
    print(df["StockInBaseUnit"])
    json_records = df.reset_index().to_json(orient="records")
    details = json.loads(json_records)

    return df, details


def query_stockLedger_report_data(
    CompanyID, BranchID, FromDate, ToDate, PriceRounding, ProductID, WareHouseID
):
    ProductID, WareHouseID = int(ProductID), int(WareHouseID)
    cursor = connection.cursor()
    dic = {
        "ProductID": ProductID,
        "BranchID": BranchID,
        "FromDate": FromDate,
        "ToDate": ToDate,
        "CompanyID": CompanyID,
        "WareHouseID": WareHouseID,
    }
    if ProductID > 0 and WareHouseID > 0:
        cursor.execute(
            """
            SELECT CASE  
            WHEN "VoucherType" = 'SI' THEN 'Sales Invoice'  
            WHEN "VoucherType" = 'SR' THEN 'Sales Return'  
            WHEN "VoucherType" = 'PI' THEN 'Purchase Invoice'  
            WHEN "VoucherType" = 'PR' THEN 'Purchase Return'  
            WHEN "VoucherType" = 'OS' THEN 'Opening Stock'  
            WHEN "VoucherType" = 'WO' THEN 'Work Order'  
            WHEN "VoucherType" = 'ST' THEN 'Stock Transfer'  
            WHEN "VoucherType" = 'SA' THEN 'Stock Adjustment'  
            WHEN "VoucherType" = 'ES' THEN 'Excess Stock'  
            WHEN "VoucherType" = 'SS' THEN 'Shortage Stock'  
            WHEN "VoucherType" = 'DS' THEN 'Damage Stock'  
            WHEN "VoucherType" = 'US' THEN 'Used Stock'  
            END AS VoucherType,  
            CASE
			WHEN "VoucherType" = 'SI' THEN (SELECT "LedgerName" FROM public."accountLedger_accountLedger" WHERE "CompanyID_id" = S."CompanyID_id" AND "LedgerID" = (SELECT "LedgerID" FROM public."salesMasters_salesMaster" WHERE "BranchID" = '1' AND "SalesMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id"))  
            WHEN "VoucherType" = 'SR' THEN (SELECT "LedgerName" FROM public."accountLedger_accountLedger" WHERE "CompanyID_id" = S."CompanyID_id" AND "LedgerID" = (SELECT "LedgerID" FROM public."salesReturnMasters_salesReturnMaster" WHERE "BranchID" = '1' AND "SalesReturnMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id"))
            WHEN "VoucherType" = 'PI' THEN (SELECT "LedgerName" FROM public."accountLedger_accountLedger" WHERE "CompanyID_id" = S."CompanyID_id" AND "LedgerID" = (SELECT "LedgerID" FROM public."purchaseMasters_purchaseMaster" WHERE "BranchID" = '1' AND "PurchaseMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id"))
            WHEN "VoucherType" = 'PR' THEN (SELECT "LedgerName" FROM public."accountLedger_accountLedger" WHERE "CompanyID_id" = S."CompanyID_id" AND "LedgerID" = (SELECT "LedgerID" FROM public."purchaseReturnMasters_purchaseReturnMaster" WHERE "BranchID" = '1' AND "PurchaseReturnMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id"))
			ELSE '' END AS LedgerName,
            CASE  
            WHEN "VoucherType" = 'SI' THEN (SELECT "VoucherNo" FROM public."salesMasters_salesMaster" WHERE "BranchID" = '1' AND "SalesMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id" )  
            WHEN "VoucherType" = 'SR' THEN (SELECT "VoucherNo" FROM public."salesReturnMasters_salesReturnMaster" WHERE "BranchID" = '1' AND "SalesReturnMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id")  
            WHEN "VoucherType" = 'PI' THEN (SELECT "VoucherNo" FROM public."purchaseMasters_purchaseMaster" WHERE "BranchID" = '1' AND "PurchaseMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id")  
            WHEN "VoucherType" = 'PR' THEN (SELECT "VoucherNo" FROM public."purchaseReturnMasters_purchaseReturnMaster" WHERE "BranchID" = '1' AND "PurchaseReturnMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id")  
            WHEN "VoucherType" = 'OS' THEN (SELECT "VoucherNo" FROM public."openingStockMasters_openingStockMaster" WHERE "BranchID" = '1' AND "OpeningStockMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id")  
            WHEN "VoucherType" = 'WO' THEN (SELECT "VoucherNo" FROM public."WorkOrderMasters_WorkOrderMaster" WHERE "BranchID" = '1' AND "WorkOrderMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id")  
            WHEN "VoucherType" = 'ST' THEN (SELECT "VoucherNo" FROM public."stockTransferMaster_ID_stockTransferMaster_ID" WHERE "BranchID" = '1' AND "StockTransferMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id")  
            WHEN "VoucherType" = 'ES' THEN (SELECT "VoucherNo" FROM public."excessStockMaster_excessStockMaster" WHERE "BranchID" = '1' AND "ExcessStockMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id")  
            WHEN "VoucherType" = 'SS' THEN (SELECT "VoucherNo" FROM public."shortageStockMaster_shortageStockMaster" WHERE "BranchID" = '1' AND "ShortageStockMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id")  
            WHEN "VoucherType" = 'DS' THEN (SELECT "VoucherNo" FROM public."damageStockMaster_damageStockMaster" WHERE "BranchID" = '1' AND "DamageStockMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id")  
            WHEN "VoucherType" = 'US' THEN (SELECT "VoucherNo" FROM public."usedStockMaster_usedStockMaster" WHERE "BranchID" = '1' AND "UsedStockMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id" )  
            WHEN "VoucherType" = 'SA' THEN (SELECT "VoucherNo" FROM public."stock_management_master" WHERE "BranchID" = '1' AND "StockMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id" )  
            END AS VoucherNo,  
        "Date",W."WarehouseName",  
            round("QtyIn",2),round("QtyOut",2),  
            round((S."QtyIn"* S."Rate"),2) as QtyInRate,round((S."QtyOut"* S."Rate"),2) as QtyOutRate,  
            

            ---------START------------
            CASE 
			WHEN "VoucherType" = 'SI' THEN (SELECT "Qty" FROM public."salesDetails_salesDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "SalesDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'SR' THEN (SELECT "Qty" FROM public."salesReturnDetails_salesReturnDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "SalesReturnDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'PI' THEN (SELECT "Qty" FROM public."purchaseDetailses_purchaseDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "PurchaseDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'PR' THEN (SELECT "Qty" FROM public."purchaseReturnDetails_purchaseReturnDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "PurchaseReturnDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'OS' THEN (SELECT "Qty" FROM public."openingStockDetailss_openingStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "OpeningStockDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'WO' THEN (SELECT "Qty" FROM public."workOrderDetails_workOrderDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "WorkOrderDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'ST' THEN (SELECT "Qty" FROM public."stockTransferDetails_stockTransferDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "StockTransferDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'ES' THEN (SELECT "Stock" FROM public."excessStockDetails_excessStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "ExcessStockDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'SS' THEN (SELECT "Stock" FROM public."shortageStockDetails_shortageStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "ShortageStockDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'DS' THEN (SELECT "Stock" FROM public."damageStockDetails_damageStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "DamageStockDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'US' THEN (SELECT "Stock" FROM public."usedStockDetails_usedStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "UsedStockDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'SA' THEN (SELECT "Qty" FROM public."stock_management_details" WHERE "CompanyID_id" = S."CompanyID_id" AND "StockDetailsID" = S."VoucherDetailID")
			ELSE 0 END AS Qty,
            --------------------
			CASE 
            WHEN "VoucherType" = 'SI' THEN (SELECT "FreeQty" FROM public."salesDetails_salesDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "SalesDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'SR' THEN (SELECT "FreeQty" FROM public."salesReturnDetails_salesReturnDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "SalesReturnDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'PI' THEN (SELECT "FreeQty" FROM public."purchaseDetailses_purchaseDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "PurchaseDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'PR' THEN (SELECT "FreeQty" FROM public."purchaseReturnDetails_purchaseReturnDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "PurchaseReturnDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'OS' THEN (SELECT "FreeQty" FROM public."openingStockDetailss_openingStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "OpeningStockDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'WO' THEN (SELECT "FreeQty" FROM public."workOrderDetails_workOrderDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "WorkOrderDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'ST' THEN (SELECT "FreeQty" FROM public."stockTransferDetails_stockTransferDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "StockTransferDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'ES' THEN (SELECT "FreeQty" FROM public."excessStockDetails_excessStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "ExcessStockDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'SS' THEN (SELECT "FreeQty" FROM public."shortageStockDetails_shortageStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "ShortageStockDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'DS' THEN (SELECT "FreeQty" FROM public."damageStockDetails_damageStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "DamageStockDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'US' THEN (SELECT "FreeQty" FROM public."usedStockDetails_usedStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "UsedStockDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'SA' THEN (SELECT "FreeQty" FROM public."stock_management_details" WHERE "CompanyID_id" = S."CompanyID_id" AND "StockDetailsID" = S."VoucherDetailID")
			ELSE 0 END AS FreeQty,

            -----------------
			CASE 
			WHEN "VoucherType" = 'SI' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."salesDetails_salesDetail" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "SalesDetailsID" = S."VoucherDetailID"))
			WHEN "VoucherType" = 'SR' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."salesReturnDetails_salesReturnDetail" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "SalesReturnDetailsID" = S."VoucherDetailID"))
            WHEN "VoucherType" = 'PI' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."purchaseDetailses_purchaseDetails" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "PurchaseDetailsID" = S."VoucherDetailID"))
            WHEN "VoucherType" = 'PR' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."purchaseReturnDetails_purchaseReturnDetail" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "PurchaseReturnDetailsID" = S."VoucherDetailID"))
            WHEN "VoucherType" = 'OS' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."openingStockDetailss_openingStockDetails" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "OpeningStockDetailsID" = S."VoucherDetailID"))
            WHEN "VoucherType" = 'WO' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."workOrderDetails_workOrderDetail" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "WorkOrderDetailsID" = S."VoucherDetailID"))
            WHEN "VoucherType" = 'ST' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."stockTransferDetails_stockTransferDetails" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "StockTransferDetailsID" = S."VoucherDetailID"))
            WHEN "VoucherType" = 'ES' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."excessStockDetails_excessStockDetails" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "ExcessStockDetailsID" = S."VoucherDetailID"))
            WHEN "VoucherType" = 'SS' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."shortageStockDetails_shortageStockDetails" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "ShortageStockDetailsID" = S."VoucherDetailID"))
            WHEN "VoucherType" = 'DS' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."damageStockDetails_damageStockDetails" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "DamageStockDetailsID" = S."VoucherDetailID"))
            WHEN "VoucherType" = 'US' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."usedStockDetails_usedStockDetails" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "UsedStockDetailsID" = S."VoucherDetailID"))
            WHEN "VoucherType" = 'SA' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."stock_management_details" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "StockDetailsID" = S."VoucherDetailID"))
			ELSE '' END AS Unit,

            ----------------
			CASE 
			WHEN "VoucherType" = 'SI' THEN (SELECT "UnitPrice" FROM public."salesDetails_salesDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "SalesDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'SR' THEN (SELECT "UnitPrice" FROM public."salesReturnDetails_salesReturnDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "SalesReturnDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'PI' THEN (SELECT "UnitPrice" FROM public."purchaseDetailses_purchaseDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "PurchaseDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'PR' THEN (SELECT "UnitPrice" FROM public."purchaseReturnDetails_purchaseReturnDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "PurchaseReturnDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'OS' THEN (SELECT "Rate" FROM public."openingStockDetailss_openingStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "OpeningStockDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'WO' THEN (SELECT "UnitPrice" FROM public."workOrderDetails_workOrderDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "WorkOrderDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'ST' THEN (SELECT "Rate" FROM public."stockTransferDetails_stockTransferDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "StockTransferDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'ES' THEN (SELECT "UnitPrice" FROM public."excessStockDetails_excessStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "ExcessStockDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'SS' THEN (SELECT "UnitPrice" FROM public."shortageStockDetails_shortageStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "ShortageStockDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'DS' THEN (SELECT "UnitPrice" FROM public."damageStockDetails_damageStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "DamageStockDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'US' THEN (SELECT "UnitPrice" FROM public."usedStockDetails_usedStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "UsedStockDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'SA' THEN (SELECT "UnitPrice" FROM public."stock_management_details" WHERE "CompanyID_id" = S."CompanyID_id" AND "StockDetailsID" = S."VoucherDetailID")
			ELSE 0 END AS UnitPrice,
            --------END-----------


            U."username"  
            FROM public."stockPosting_stockPosting" AS S  
            INNER JOIN public.products_product AS P ON P."ProductID" = S."ProductID" AND P."CompanyID_id" = S."CompanyID_id"  
            INNER JOIN public.pricelist_pricelist AS PR ON PR."PriceListID" = S."PriceListID" AND PR."CompanyID_id" = S."CompanyID_id"  
            INNER JOIN public.warehouse_warehouse AS W ON W."WarehouseID" = S."WareHouseID" AND W."CompanyID_id" = S."CompanyID_id"  
            INNER JOIN public.auth_user AS U ON U."id" = S."CreatedUserID"  
            WHERE S."CompanyID_id" = %(CompanyID)s AND S."WareHouseID" = %(WareHouseID)s AND S."ProductID" = %(ProductID)s AND S."Date" BETWEEN %(FromDate)s AND %(ToDate)s  
            ORDER BY "Date"  
        """,
            dic,
        )
        data = cursor.fetchall()
        if cursor.rowcount == 0:
            data = [("", "", "NO DATA", "", 0, 0, 0, 0,0,"", "", "","","")]
            

    elif ProductID > 0:
        cursor.execute(
            """SELECT CASE  
            WHEN "VoucherType" = 'SI' THEN 'Sales Invoice'  
            WHEN "VoucherType" = 'SR' THEN 'Sales Return'  
            WHEN "VoucherType" = 'PI' THEN 'Purchase Invoice'  
            WHEN "VoucherType" = 'PR' THEN 'Purchase Return'  
            WHEN "VoucherType" = 'OS' THEN 'Opening Stock'  
            WHEN "VoucherType" = 'WO' THEN 'Work Order'  
            WHEN "VoucherType" = 'ST' THEN 'Stock Transfer'  
            WHEN "VoucherType" = 'ES' THEN 'Excess Stock'  
            WHEN "VoucherType" = 'SS' THEN 'Shortage Stock'  
            WHEN "VoucherType" = 'DS' THEN 'Damage Stock'  
            WHEN "VoucherType" = 'US' THEN 'Used Stock'  
            END AS VoucherType,  
            CASE
			WHEN "VoucherType" = 'SI' THEN (SELECT "LedgerName" FROM public."accountLedger_accountLedger" WHERE "CompanyID_id" = S."CompanyID_id" AND "LedgerID" = (SELECT "LedgerID" FROM public."salesMasters_salesMaster" WHERE "BranchID" = '1' AND "SalesMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id"))  
            WHEN "VoucherType" = 'SR' THEN (SELECT "LedgerName" FROM public."accountLedger_accountLedger" WHERE "CompanyID_id" = S."CompanyID_id" AND "LedgerID" = (SELECT "LedgerID" FROM public."salesReturnMasters_salesReturnMaster" WHERE "BranchID" = '1' AND "SalesReturnMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id"))
            WHEN "VoucherType" = 'PI' THEN (SELECT "LedgerName" FROM public."accountLedger_accountLedger" WHERE "CompanyID_id" = S."CompanyID_id" AND "LedgerID" = (SELECT "LedgerID" FROM public."purchaseMasters_purchaseMaster" WHERE "BranchID" = '1' AND "PurchaseMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id"))
            WHEN "VoucherType" = 'PR' THEN (SELECT "LedgerName" FROM public."accountLedger_accountLedger" WHERE "CompanyID_id" = S."CompanyID_id" AND "LedgerID" = (SELECT "LedgerID" FROM public."purchaseReturnMasters_purchaseReturnMaster" WHERE "BranchID" = '1' AND "PurchaseReturnMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id"))
			ELSE '' END AS LedgerName,
            CASE  
            WHEN "VoucherType" = 'SI' THEN (SELECT "VoucherNo" FROM public."salesMasters_salesMaster" WHERE "BranchID" = '1' AND "SalesMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id" )  
            WHEN "VoucherType" = 'SR' THEN (SELECT "VoucherNo" FROM public."salesReturnMasters_salesReturnMaster" WHERE "BranchID" = '1' AND "SalesReturnMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id")  
            WHEN "VoucherType" = 'PI' THEN (SELECT "VoucherNo" FROM public."purchaseMasters_purchaseMaster" WHERE "BranchID" = '1' AND "PurchaseMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id")  
            WHEN "VoucherType" = 'PR' THEN (SELECT "VoucherNo" FROM public."purchaseReturnMasters_purchaseReturnMaster" WHERE "BranchID" = '1' AND "PurchaseReturnMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id")  
            WHEN "VoucherType" = 'OS' THEN (SELECT "VoucherNo" FROM public."openingStockMasters_openingStockMaster" WHERE "BranchID" = '1' AND "OpeningStockMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id")  
            WHEN "VoucherType" = 'WO' THEN (SELECT "VoucherNo" FROM public."WorkOrderMasters_WorkOrderMaster" WHERE "BranchID" = '1' AND "WorkOrderMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id")  
            WHEN "VoucherType" = 'ST' THEN (SELECT "VoucherNo" FROM public."stockTransferMaster_ID_stockTransferMaster_ID" WHERE "BranchID" = '1' AND "StockTransferMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id")  
            WHEN "VoucherType" = 'ES' THEN (SELECT "VoucherNo" FROM public."excessStockMaster_excessStockMaster" WHERE "BranchID" = '1' AND "ExcessStockMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id")  
            WHEN "VoucherType" = 'SS' THEN (SELECT "VoucherNo" FROM public."shortageStockMaster_shortageStockMaster" WHERE "BranchID" = '1' AND "ShortageStockMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id")  
            WHEN "VoucherType" = 'DS' THEN (SELECT "VoucherNo" FROM public."damageStockMaster_damageStockMaster" WHERE "BranchID" = '1' AND "DamageStockMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id")  
            WHEN "VoucherType" = 'US' THEN (SELECT "VoucherNo" FROM public."usedStockMaster_usedStockMaster" WHERE "BranchID" = '1' AND "UsedStockMasterID"="VoucherMasterID" AND "CompanyID_id" = S."CompanyID_id" )  
            END AS VoucherNo,  
        "Date",W."WarehouseName",  
            round("QtyIn",2),round("QtyOut",2),  
            round((S."QtyIn"* S."Rate"),2) as QtyInRate,round((S."QtyOut"* S."Rate"),2) as QtyOutRate,  


            ---------START------------
            CASE 
			WHEN "VoucherType" = 'SI' THEN (SELECT "Qty" FROM public."salesDetails_salesDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "SalesDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'SR' THEN (SELECT "Qty" FROM public."salesReturnDetails_salesReturnDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "SalesReturnDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'PI' THEN (SELECT "Qty" FROM public."purchaseDetailses_purchaseDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "PurchaseDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'PR' THEN (SELECT "Qty" FROM public."purchaseReturnDetails_purchaseReturnDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "PurchaseReturnDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'OS' THEN (SELECT "Qty" FROM public."openingStockDetailss_openingStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "OpeningStockDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'WO' THEN (SELECT "Qty" FROM public."workOrderDetails_workOrderDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "WorkOrderDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'ST' THEN (SELECT "Qty" FROM public."stockTransferDetails_stockTransferDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "StockTransferDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'ES' THEN (SELECT "Stock" FROM public."excessStockDetails_excessStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "ExcessStockDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'SS' THEN (SELECT "Stock" FROM public."shortageStockDetails_shortageStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "ShortageStockDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'DS' THEN (SELECT "Stock" FROM public."damageStockDetails_damageStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "DamageStockDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'US' THEN (SELECT "Stock" FROM public."usedStockDetails_usedStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "UsedStockDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'SA' THEN (SELECT "Qty" FROM public."stock_management_details" WHERE "CompanyID_id" = S."CompanyID_id" AND "StockDetailsID" = S."VoucherDetailID")
			ELSE 0 END AS Qty,
            --------------------
			CASE 
            WHEN "VoucherType" = 'SI' THEN (SELECT "FreeQty" FROM public."salesDetails_salesDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "SalesDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'SR' THEN (SELECT "FreeQty" FROM public."salesReturnDetails_salesReturnDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "SalesReturnDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'PI' THEN (SELECT "FreeQty" FROM public."purchaseDetailses_purchaseDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "PurchaseDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'PR' THEN (SELECT "FreeQty" FROM public."purchaseReturnDetails_purchaseReturnDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "PurchaseReturnDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'OS' THEN (SELECT "FreeQty" FROM public."openingStockDetailss_openingStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "OpeningStockDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'WO' THEN (SELECT "FreeQty" FROM public."workOrderDetails_workOrderDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "WorkOrderDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'ST' THEN (SELECT "FreeQty" FROM public."stockTransferDetails_stockTransferDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "StockTransferDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'ES' THEN (SELECT "FreeQty" FROM public."excessStockDetails_excessStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "ExcessStockDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'SS' THEN (SELECT "FreeQty" FROM public."shortageStockDetails_shortageStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "ShortageStockDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'DS' THEN (SELECT "FreeQty" FROM public."damageStockDetails_damageStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "DamageStockDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'US' THEN (SELECT "FreeQty" FROM public."usedStockDetails_usedStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "UsedStockDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'SA' THEN (SELECT "FreeQty" FROM public."stock_management_details" WHERE "CompanyID_id" = S."CompanyID_id" AND "StockDetailsID" = S."VoucherDetailID")
			ELSE 0 END AS FreeQty,

            -----------------
			CASE 
			WHEN "VoucherType" = 'SI' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."salesDetails_salesDetail" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "SalesDetailsID" = S."VoucherDetailID"))
			WHEN "VoucherType" = 'SR' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."salesReturnDetails_salesReturnDetail" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "SalesReturnDetailsID" = S."VoucherDetailID"))
            WHEN "VoucherType" = 'PI' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."purchaseDetailses_purchaseDetails" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "PurchaseDetailsID" = S."VoucherDetailID"))
            WHEN "VoucherType" = 'PR' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."purchaseReturnDetails_purchaseReturnDetail" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "PurchaseReturnDetailsID" = S."VoucherDetailID"))
            WHEN "VoucherType" = 'OS' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."openingStockDetailss_openingStockDetails" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "OpeningStockDetailsID" = S."VoucherDetailID"))
            WHEN "VoucherType" = 'WO' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."workOrderDetails_workOrderDetail" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "WorkOrderDetailsID" = S."VoucherDetailID"))
            WHEN "VoucherType" = 'ST' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."stockTransferDetails_stockTransferDetails" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "StockTransferDetailsID" = S."VoucherDetailID"))
            WHEN "VoucherType" = 'ES' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."excessStockDetails_excessStockDetails" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "ExcessStockDetailsID" = S."VoucherDetailID"))
            WHEN "VoucherType" = 'SS' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."shortageStockDetails_shortageStockDetails" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "ShortageStockDetailsID" = S."VoucherDetailID"))
            WHEN "VoucherType" = 'DS' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."damageStockDetails_damageStockDetails" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "DamageStockDetailsID" = S."VoucherDetailID"))
            WHEN "VoucherType" = 'US' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."usedStockDetails_usedStockDetails" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "UsedStockDetailsID" = S."VoucherDetailID"))
            WHEN "VoucherType" = 'SA' THEN (SELECT "UnitName" FROM public.units_unit WHERE "CompanyID_id" = S."CompanyID_id" AND "UnitID" = (SELECT "UnitID" FROM public."stock_management_details" AS D 
			LEFT OUTER JOIN public.pricelist_pricelist AS PL ON PL."CompanyID_id" = D."CompanyID_id" AND D."PriceListID" = PL."PriceListID" WHERE D."CompanyID_id" = S."CompanyID_id" AND "StockDetailsID" = S."VoucherDetailID"))
			ELSE '' END AS Unit,

            ----------------
			CASE 
			WHEN "VoucherType" = 'SI' THEN (SELECT "UnitPrice" FROM public."salesDetails_salesDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "SalesDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'SR' THEN (SELECT "UnitPrice" FROM public."salesReturnDetails_salesReturnDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "SalesReturnDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'PI' THEN (SELECT "UnitPrice" FROM public."purchaseDetailses_purchaseDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "PurchaseDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'PR' THEN (SELECT "UnitPrice" FROM public."purchaseReturnDetails_purchaseReturnDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "PurchaseReturnDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'OS' THEN (SELECT "Rate" FROM public."openingStockDetailss_openingStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "OpeningStockDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'WO' THEN (SELECT "UnitPrice" FROM public."workOrderDetails_workOrderDetail" WHERE "CompanyID_id" = S."CompanyID_id" AND "WorkOrderDetailsID" = S."VoucherDetailID")
			WHEN "VoucherType" = 'ST' THEN (SELECT "Rate" FROM public."stockTransferDetails_stockTransferDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "StockTransferDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'ES' THEN (SELECT "UnitPrice" FROM public."excessStockDetails_excessStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "ExcessStockDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'SS' THEN (SELECT "UnitPrice" FROM public."shortageStockDetails_shortageStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "ShortageStockDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'DS' THEN (SELECT "UnitPrice" FROM public."damageStockDetails_damageStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "DamageStockDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'US' THEN (SELECT "UnitPrice" FROM public."usedStockDetails_usedStockDetails" WHERE "CompanyID_id" = S."CompanyID_id" AND "UsedStockDetailsID" = S."VoucherDetailID")
			-- WHEN "VoucherType" = 'SA' THEN (SELECT "UnitPrice" FROM public."stock_management_details" WHERE "CompanyID_id" = S."CompanyID_id" AND "StockDetailsID" = S."VoucherDetailID")
			ELSE 0 END AS UnitPrice,
            --------END-----------


            U."username"  
            FROM public."stockPosting_stockPosting" AS S  
            INNER JOIN public.products_product AS P ON P."ProductID" = S."ProductID" AND P."CompanyID_id" = S."CompanyID_id"  
            INNER JOIN public.pricelist_pricelist AS PR ON PR."PriceListID" = S."PriceListID" AND PR."CompanyID_id" = S."CompanyID_id"  
            INNER JOIN public.warehouse_warehouse AS W ON W."WarehouseID" = S."WareHouseID" AND W."CompanyID_id" = S."CompanyID_id"  
            INNER JOIN public.auth_user AS U ON U."id" = S."CreatedUserID"  
            WHERE S."CompanyID_id" = %(CompanyID)s AND S."ProductID" = %(ProductID)s AND S."Date" BETWEEN %(FromDate)s AND %(ToDate)s  
            ORDER BY "Date"  
        """,
            dic,
        )
        data = cursor.fetchall()
        if cursor.rowcount == 0:
            data = [("", "", "NO DATA", "", 0, 0, 0, 0,0,"", "", "","","")]

    else:
        data = [("", "", "Select A Product","", 0, 0, 0, 0,0,"","", "","","")]


    df = pd.DataFrame(data)
    # taiking Opening Stock Balance
    opening_stock_balance = query_openingStockBalance_data(
        CompanyID, BranchID, FromDate, ToDate, PriceRounding, ProductID, WareHouseID
    )
    op_balance_row = pd.DataFrame(opening_stock_balance, index=[0])

    # calculating qtyIn and qtyOut with opening stock balance
    stock = 0
    if op_balance_row.at[0, 7]:   
        stock = op_balance_row.at[0, 7]
    cal_stock = 0
    is_added = False
    stock_arr = [stock]
    for i in range(len(data)):
        if cal_stock == 0 and not is_added:
            is_added = True
            cal_stock = stock
        q_in = 0
        q_out = 0
        if data[i][5] != None:
            q_in = data[i][5]
        if data[i][6] != None:
            q_out = data[i][6]
        cal_stock = +q_in + cal_stock - q_out
        stock_arr.append(cal_stock)
    stock_arr.append(cal_stock)

    # adding Total in laast Row to data frame
    df.loc[str(_("Total"))] = df[[5,6]].sum().reindex(df.columns, fill_value="")

    # adding Opening Stock in first Row to data frame
    df = pd.concat([op_balance_row, df]).reset_index(drop=True)
    print(df)
    # adding Heading to frame
    df.columns = [
        str(_("VoucherType")),
        str(_("LedgerName")),
        str(_("VoucherNo")),
        str(_("Date")),
        # str(_("ProductName")),
        str(_("WareHouseName")),
        str(_("QtyIn")),
        str(_("QtyOut")),
        str(_("QuantyInRate")),
        str(_("QuantyOutRate")),

        str(_("Qty")),
        str(_("FreeQty")),
        str(_("UnitName")),
        str(_("UnitPrice")),

        str(_("UserName")),
    ]
    # convert date format(millisecond) to str in dataframe
    df["Date"] = df["Date"].astype(str)

    # inserting a calculated Stock column to dataframe
    df.insert(loc=7, column="Stock", value=stock_arr)
    # add top raw QuantyInRate to null
    df.at[0, "QuantyInRate"] = ""
    df.at[0, 'QtyOut'] = stock

    total_qty_out = df.at[len(df.index)-1, 'QtyOut'] 

    df.at[len(df.index)-1, 'QtyOut'] = stock+Decimal(total_qty_out)

    # rounding
    # df["UnitPrice"] = df["UnitPrice"].apply(lambda x: round(
    #     float(x), PriceRounding)) 
    # df["Qty"] = df["Qty"].apply(lambda x: round(
    #     float(x), PriceRounding)) 

    json_records = df.reset_index().to_json(orient="records")
    details = json.loads(json_records)
    return df, details


def query_openingStockBalance_data(
    CompanyID, BranchID, FromDate, ToDate, PriceRounding, ProductID, WareHouseID
):
    cursor = connection.cursor()
    dic = {
        "ProductID": ProductID,
        "BranchID": BranchID,
        "FromDate": FromDate,
        "ToDate": ToDate,
        "CompanyID": CompanyID,
        "WareHouseID": WareHouseID,
    }
    # cursor.execute('''select 'Opening Balance' AS VoucherType,'' AS VoucherNo,'' AS Date,'' AS ProductName,'' AS WarehouseName,'' AS UnitName,'' AS Username,'' AS QtyIn,'' AS QtyOut, NULLIF(round(SUM("QtyIn"),2)-round(SUM("QtyOut"),2),0) AS OPBalance,round(SUM("Rate")/(SUM("QtyIn")+SUM("QtyOut")),2) AS Rate FROM public."stockPosting_stockPosting" where "ProductID" = %(ProductID)s AND "Date" < %(FromDate)s AND "WareHouseID"='1'
    cursor.execute(
        """select 'Opening Stock','','','','','','0', NULLIF(round(SUM("QtyIn"),2)-round(SUM("QtyOut"),2),0) AS OPBalance,'' AS QtyIn,'' AS QtyOut,'' FROM public."stockPosting_stockPosting" where "CompanyID_id" = %(CompanyID)s AND "ProductID" = %(ProductID)s AND "Date" < %(FromDate)s AND "WareHouseID" = %(WareHouseID)s
    """,
        dic,
    )
    data = cursor.fetchall()

    return data


def query_openingBalance_data(
    CompanyID, BranchID, FromDate, ToDate, PriceRounding, value, ManualOpeningBalance
):

    cursor = connection.cursor()
    dic = {
        "BranchID": BranchID,
        "FromDate": FromDate,
        "ToDate": ToDate,
        "CompanyID": CompanyID,
        "value": value,
        "ManualOpeningBalance": ManualOpeningBalance,
    }
    # cursor.execute('''select 'Opening Balance' AS VoucherType,'' AS VoucherNo,'' AS Date,'' AS ProductName,'' AS WarehouseName,'' AS UnitName,'' AS Username,'' AS QtyIn,'' AS QtyOut, NULLIF(round(SUM("QtyIn"),2)-round(SUM("QtyOut"),2),0) AS OPBalance,round(SUM("Rate")/(SUM("QtyIn")+SUM("QtyOut")),2) AS Rate FROM public."stockPosting_stockPosting" where "ProductID" = %(ProductID)s AND "Date" < %(FromDate)s AND "WareHouseID"='1'
    if ManualOpeningBalance:
        data = [
            ("", "", "Opening Balance", "", "",
             "", "", Decimal(ManualOpeningBalance))
        ]
    else:
        cursor.execute(
            """
            SELECT '','','Opening Balance','','','','', COALESCE(SUM("Debit" - "Credit"),0) AS Balance   
            FROM "public"."ledgerPostings_ledgerPosting"  
            WHERE "CompanyID_id" = %(CompanyID)s AND "LedgerID" = %(value)s AND "Date"< %(FromDate)s
            """,
            dic,
        )
        data = cursor.fetchall()

    return data


def query_closingBalance_data(
    CompanyID, BranchID, FromDate, ToDate, PriceRounding, value, ManualClosingBalance
):
    cursor = connection.cursor()
    dic = {
        "BranchID": BranchID,
        "FromDate": FromDate,
        "ToDate": ToDate,
        "CompanyID": CompanyID,
        "value": value,
        "ManualClosingBalance": ManualClosingBalance,
    }
    # cursor.execute('''select 'Closing Balance' AS VoucherType,'' AS VoucherNo,'' AS Date,'' AS ProductName,'' AS WarehouseName,'' AS UnitName,'' AS Username,'' AS QtyIn,'' AS QtyOut, NULLIF(round(SUM("QtyIn"),2)-round(SUM("QtyOut"),2),0) AS OPBalance,round(SUM("Rate")/(SUM("QtyIn")+SUM("QtyOut")),2) AS Rate FROM public."stockPosting_stockPosting" where "ProductID" = %(ProductID)s AND "Date" < %(FromDate)s AND "WareHouseID"='1'
    if ManualClosingBalance:
        data = [
            ("", "", "Closing Balance", "", "",
             "", "", Decimal(ManualClosingBalance))
        ]
    else:
        cursor.execute(
            """
            SELECT '','','Closing Balance','','','','', COALESCE(SUM("Debit" - "Credit"),0) AS Balance   
            FROM "public"."ledgerPostings_ledgerPosting"  
            WHERE "CompanyID_id" = %(CompanyID)s AND "LedgerID" = %(value)s AND "Date"< %(ToDate)s
            """,
            dic,
        )
        data = cursor.fetchall()

    return data


def query_Cash_OR_Bank_book_openingBalance_data(value, CompanyID, BranchID, FromDate, ToDate, PriceRounding, VoucherType, RouteLedgers, ManualOpeningBalance):
    cursor = connection.cursor()
    dic = {'RouteLedgers': RouteLedgers, 'BranchID': BranchID, 'FromDate': FromDate,
           'ToDate': ToDate, 'CompanyID': CompanyID, 'ManualOpeningBalance': ManualOpeningBalance}
    # cursor.execute('''select 'Opening Balance' AS VoucherType,'' AS VoucherNo,'' AS Date,'' AS ProductName,'' AS WarehouseName,'' AS UnitName,'' AS Username,'' AS QtyIn,'' AS QtyOut, NULLIF(round(SUM("QtyIn"),2)-round(SUM("QtyOut"),2),0) AS OPBalance,round(SUM("Rate")/(SUM("QtyIn")+SUM("QtyOut")),2) AS Rate FROM public."stockPosting_stockPosting" where "ProductID" = %(ProductID)s AND "Date" < %(FromDate)s AND "WareHouseID"='1'
    if ManualOpeningBalance:
        data = [('', '', 'Opening Balance', '', '', '',
                 '', Decimal(ManualOpeningBalance))]
    elif VoucherType == 'all_ledger':
        cursor.execute('''
            SELECT '','','Opening Balance','','','','', COALESCE(SUM("Debit" - "Credit"),0) AS Balance   
            FROM "public"."ledgerPostings_ledgerPosting"  
            WHERE "BranchID" = %(BranchID)s AND "CompanyID_id" = %(CompanyID)s AND "LedgerID" IN (SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "CompanyID_id" = %(CompanyID)s AND "AccountGroupUnder" = '9' ) AND "Date"< %(FromDate)s
            ''', dic)
        data = cursor.fetchall()
    elif VoucherType == 'ledger_wise':
        cursor.execute('''
            SELECT '','','Opening Balance','','','','', COALESCE(SUM("Debit" - "Credit"),0) AS Balance   
            FROM "public"."ledgerPostings_ledgerPosting"  
            WHERE "BranchID" = %(BranchID)s AND "CompanyID_id" = %(CompanyID)s AND "LedgerID" IN %(RouteLedgers)s AND "Date"< %(FromDate)s
            ''', dic)
        data = cursor.fetchall()
    elif VoucherType == 'group_wise':
        cursor.execute('''
            SELECT '','','Opening Balance','','','','', COALESCE(SUM("Debit" - "Credit"),0) AS Balance   
            FROM "public"."ledgerPostings_ledgerPosting"  
            WHERE "BranchID" = %(BranchID)s AND "CompanyID_id" = %(CompanyID)s AND "LedgerID" IN (SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "CompanyID_id" = %(CompanyID)s AND "AccountGroupUnder" = %(value)s ) AND "Date"< %(FromDate)s
            ''', dic)
        data = cursor.fetchall()

    return data

# =====For Trail Balance====


def query_openingBalanceDifference_data(
    CompanyID, BranchID, FromDate, ToDate, PriceRounding, ManualOpeningBalance
):

    cursor = connection.cursor()
    dic = {
        "BranchID": BranchID,
        "FromDate": FromDate,
        "ToDate": ToDate,
        "CompanyID": CompanyID,
        "ManualOpeningBalance": ManualOpeningBalance,
    }
    if ManualOpeningBalance:
        data = [
            (
                "",
                "",
                "Opening Balance Difference",
                "",
                "",
                "",
                "",
                Decimal(ManualOpeningBalance),
            )
        ]
    else:
        cursor.execute(
            """
            SELECT NULLIF(SUM("Debit"),0) - NULLIF(SUM("Credit"),0) AS OpeningDifference               
            from public."ledgerPostings_ledgerPosting" WHERE "CompanyID_id" = %(CompanyID)s AND "VoucherType" = 'LOB' AND "BranchID" = '1' AND "Date" < %(ToDate)s
            """,
            dic,
        )
        data = cursor.fetchall()

    return data


def query_openingStockValue_data(CompanyID, BranchID, FromDate, ToDate, PriceRounding):
    cursor = connection.cursor()
    dic = {"BranchID": BranchID, "FromDate": FromDate,"ToDate": ToDate, "CompanyID": CompanyID}

    cursor.execute(
        """
        select SUM("GrandTotal") from public."openingStockMasters_openingStockMaster" where "CompanyID_id" = %(CompanyID)s AND "Date" < %(ToDate)s
    """,
        dic,
    )

    data = cursor.fetchall()
    if cursor.rowcount == 0:
        data = [(0)]

    return data

# ========END=======

def query_ledger_report_data(CompanyID, BranchID, FromDate, ToDate, PriceRounding, VoucherType, value, ManualOpeningBalance):
    cursor = connection.cursor()
    dic = {
        "value": value,
        "BranchID": BranchID,
        "FromDate": FromDate,
        "ToDate": ToDate,
        "CompanyID": CompanyID,
        "VoucherType": VoucherType,
    }
    if VoucherType == "all_ledger":
        # updating Ledger Balance
        query_updateLedgerBalance(CompanyID, BranchID)
        cursor.execute(
            """
            select "LedgerName",Balance FROM(  
              SELECT "LedgerName",round(coalesce("Balance", 0),2) AS Balance FROM public."accountLedger_accountLedger" WHERE "CompanyID_id" = %(CompanyID)s AND "BranchID" = '1'
            ) AS Temp  where Balance != 0 
            """,
            dic,
        )
        if cursor.rowcount == 0:
            data = [("No Data", "")]

        data = cursor.fetchall()

    elif VoucherType == "ledger_wise":
        cursor.execute(
            """
            SELECT   
            CASE 
            WHEN "VoucherType" = 'SI' THEN(SELECT "VoucherNo" FROM public."salesMasters_salesMaster" WHERE "BranchID" = L."BranchID" AND "SalesMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")   
            WHEN "VoucherType" = 'SR' THEN(SELECT "VoucherNo" FROM public."salesReturnMasters_salesReturnMaster" WHERE "BranchID" = L."BranchID" AND "SalesReturnMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")   
            WHEN "VoucherType" = 'PI' THEN(SELECT "VoucherNo" FROM public."purchaseMasters_purchaseMaster" WHERE "BranchID" = L."BranchID" AND "PurchaseMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")   
            WHEN "VoucherType" = 'PR' THEN(SELECT "VoucherNo" FROM public."purchaseReturnMasters_purchaseReturnMaster" WHERE "BranchID" = L."BranchID" AND "PurchaseReturnMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")   
            WHEN "VoucherType" = 'CR' THEN(SELECT "VoucherNo" FROM "public"."receiptMasters_receiptMaster" WHERE "BranchID" = L."BranchID" AND "ReceiptMasterID" = "VoucherMasterID" AND "VoucherType" = 'CR' AND "CompanyID_id" = L."CompanyID_id")   
            WHEN "VoucherType" = 'BR' THEN(SELECT "VoucherNo" FROM "public"."receiptMasters_receiptMaster" WHERE "BranchID" = L."BranchID" AND "ReceiptMasterID" = "VoucherMasterID" AND "VoucherType" = 'BR' AND "CompanyID_id" = L."CompanyID_id")   
            WHEN "VoucherType" = 'CP' THEN(SELECT "VoucherNo" FROM "public"."paymentMasters_paymentMaster" WHERE "BranchID" = L."BranchID" AND "PaymentMasterID" = "VoucherMasterID" AND "VoucherType" = 'CP' AND "CompanyID_id" = L."CompanyID_id")   
            WHEN "VoucherType" = 'BP' THEN(SELECT "VoucherNo" FROM "public"."paymentMasters_paymentMaster" WHERE "BranchID" = L."BranchID" AND "PaymentMasterID" = "VoucherMasterID" AND "VoucherType" = 'BP' AND "CompanyID_id" = L."CompanyID_id")   
            WHEN "VoucherType" = 'LOB' THEN cast( L."LedgerID" as varchar(50))
            WHEN "VoucherType" = 'OS' THEN(SELECT "VoucherNo" FROM public."openingStockMasters_openingStockMaster" WHERE "BranchID" = L."BranchID" AND "OpeningStockMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")   
            WHEN "VoucherType" = 'JL' THEN(SELECT "VoucherNo" FROM "public"."journalMaster_journalMaster" WHERE "BranchID" = L."BranchID" AND "JournalMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")   
            WHEN "VoucherType" = 'EX' THEN(SELECT "VoucherNo" FROM "public"."expenseMasters_expenseMaster" WHERE "BranchID" = L."BranchID" AND "ExpenseMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id") END AS VoucherNo,   

            CASE WHEN "VoucherType" = 'SI' THEN(SELECT "Notes" FROM public."salesMasters_salesMaster" WHERE "BranchID" = L."BranchID" AND "SalesMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")   
            WHEN "VoucherType" = 'SR' THEN(SELECT "Notes" FROM public."salesReturnMasters_salesReturnMaster" WHERE "BranchID" = L."BranchID" AND "SalesReturnMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")   
            WHEN "VoucherType" = 'PI' THEN(SELECT "Notes" FROM public."purchaseMasters_purchaseMaster" WHERE "BranchID" = L."BranchID" AND "PurchaseMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")   
            WHEN "VoucherType" = 'PR' THEN(SELECT "Notes" FROM public."purchaseReturnMasters_purchaseReturnMaster" WHERE "BranchID" = L."BranchID" AND "PurchaseReturnMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")

            WHEN "VoucherType" = 'CR' THEN (SELECT "Narration" FROM "public"."receiptDetailses_receiptDetails" AS A   
            INNER JOIN "public"."receiptMasters_receiptMaster" AS B ON A."ReceiptMasterID" = B."ReceiptMasterID" AND B."CompanyID_id" = A."CompanyID_id"  
            WHERE B."BranchID" = L."BranchID" AND A."ReceiptDetailID" = "VoucherDetailID" AND B."VoucherType" = 'CR'    
            AND A."LedgerID" = L."LedgerID" AND B."CompanyID_id" = L."CompanyID_id")   

            WHEN "VoucherType" = 'BR' THEN (SELECT "Narration" FROM "public"."receiptDetailses_receiptDetails" AS A 
                                            INNER JOIN "public"."receiptMasters_receiptMaster" AS B ON A."ReceiptMasterID" = B."ReceiptMasterID" AND A."CompanyID_id" = B."CompanyID_id"
                                            WHERE B."BranchID" = L."BranchID" AND A."ReceiptDetailID" = "VoucherDetailID" AND B."VoucherType" = 'BR'   
            AND A."LedgerID" = L."LedgerID"  AND A."CompanyID_id" = L."CompanyID_id")   

            WHEN "VoucherType" = 'CP' THEN (SELECT "Narration" FROM "public"."paymentDetails_paymentDetail" AS A 
                                            INNER JOIN "public"."paymentMasters_paymentMaster" AS B ON A."PaymentMasterID" = B."PaymentMasterID" AND B."CompanyID_id" = A."CompanyID_id"   
            WHERE B."BranchID" = L."BranchID" AND A."PaymentDetailsID" = "VoucherDetailID" AND B."VoucherType" = 'CP'   
            AND A."LedgerID" = L."LedgerID" AND A."CompanyID_id" = L."CompanyID_id")   

            WHEN "VoucherType" = 'BP' THEN (SELECT "Narration" FROM "public"."paymentDetails_paymentDetail" AS A INNER JOIN "public"."paymentMasters_paymentMaster" AS B ON A."PaymentMasterID" = B."PaymentMasterID"
            WHERE B."BranchID" = L."BranchID" AND A."PaymentDetailsID" = "VoucherDetailID" AND B."VoucherType" = 'BP' AND B."CompanyID_id" = A."CompanyID_id" 
            AND A."LedgerID" = L."LedgerID" AND A."CompanyID_id" = L."CompanyID_id")   

            WHEN "VoucherType" = 'LOB' THEN(SELECT "Notes" FROM public."accountLedger_accountLedger" WHERE "BranchID" = L."BranchID" AND "LedgerID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")   
            WHEN "VoucherType" = 'OS' THEN(SELECT "Notes" FROM "public"."openingStockMasters_openingStockMaster" WHERE "BranchID" = L."BranchID" AND "OpeningStockMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")   
            WHEN "VoucherType" = 'JL' THEN   
            (SELECT "Narration" FROM "public"."journalDetails_journalDetail" AS A 
            INNER JOIN "public"."journalMaster_journalMaster" AS B ON A."JournalMasterID" = B."JournalMasterID" AND B."CompanyID_id" = A."CompanyID_id"
            WHERE B."BranchID" = L."BranchID" AND A."JournalDetailsID" = "VoucherDetailID"   
            AND A."LedgerID" = L."LedgerID" AND A."CompanyID_id" =L."CompanyID_id")   

            WHEN "VoucherType" = 'EX' THEN   
            (SELECT "Notes" FROM "public"."expenseDetails_expenseDetail" AS A 
            INNER JOIN "public"."expenseMasters_expenseMaster" AS B ON A."ExpenseMasterID" = B."ExpenseMasterID" AND B."CompanyID_id" = A."CompanyID_id"    
            WHERE B."BranchID" = L."BranchID" AND A."ExpenseDetailsID" = "VoucherDetailID" AND B."CompanyID_id" = L."CompanyID_id" 
            AND A."Ledger_id" = LL.id )   
            END AS Narration,   
            L."Date" AS VoucherDate   
            , CASE WHEN "VoucherType" = 'SI' THEN 'Sales Invoice'   
            WHEN "VoucherType" = 'SR' THEN 'Sales Return'   
            WHEN "VoucherType" = 'PI' THEN 'Purchase Invoice'   
            WHEN "VoucherType" = 'PR' THEN 'Purchase Return'   
            WHEN "VoucherType" = 'CR' THEN 'Cash Receipt'   
            WHEN "VoucherType" = 'BR' THEN 'Bank Receipt'   
            WHEN "VoucherType" = 'CP' THEN 'Cash Payment'   
            WHEN "VoucherType" = 'BP' THEN 'Bank Payment'   
            WHEN "VoucherType" = 'LOB' THEN 'Ledger Opening Balance'   
            WHEN "VoucherType" = 'OS' THEN 'Opening Stock'   
            WHEN "VoucherType" = 'EX' THEN 'Expense'   
            WHEN "VoucherType" = 'JL' THEN 'Journal Entry'   
            END AS Particulars,

            (SELECT NULLIF("LedgerName", '') FROM public."accountLedger_accountLedger" AS RL WHERE RL."CompanyID_id" = L."CompanyID_id" AND RL."LedgerID" = L."RelatedLedgerID")
            AS LedgerName

            ,L."VoucherType"   
            ,round(L."Debit",2)   
            ,round(L."Credit",2)   

            FROM "public"."ledgerPostings_ledgerPosting" AS L   
            INNER JOIN public."accountLedger_accountLedger" AS LL ON L."LedgerID" = LL."LedgerID" AND L."CompanyID_id" = LL."CompanyID_id" 
            WHERE L."CompanyID_id" = %(CompanyID)s AND L."LedgerID" = %(value)s AND L."Date" between %(FromDate)s AND %(ToDate)s AND L."BranchID" = '1'  
            order by "Date"
        """,
            dic,
        )
        data = cursor.fetchall()
        # if ledger data is null show a default data
        if cursor.rowcount == 0:
            data = [("", "", "NO DATA FOR THIS LEDGER", "", "", "", 0, 0)]

    elif VoucherType == "group_wise":
        cursor.execute(
            """ 
            SELECT* FROM(   
            SELECT   
            A."LedgerName",   
            round(NULLIF(SUM(L."Debit"), 0),2 ) as Debit,   
            round(NULLIF(SUM(L."Credit"), 0),2) as Credit,   
            round(NULLIF(SUM(L."Debit"), 0) - NULLIF(SUM(L."Credit"), 0),2) AS Balance   
            FROM public."accountLedger_accountLedger" A   
            INNER JOIN "public"."ledgerPostings_ledgerPosting" AS L ON L."CompanyID_id" = A."CompanyID_id" AND L."LedgerID" = A."LedgerID" AND L."BranchID" = A."BranchID" AND L."Date" <= %(ToDate)s   
            WHERE A."CompanyID_id" = %(CompanyID)s AND A."BranchID" = %(BranchID)s AND A."AccountGroupUnder" = %(value)s GROUP BY L."LedgerID",A."LedgerName" ) AS TEMP WHERE Balance != 0 ORDER BY "LedgerName"   
                """,
            dic,
        )
        data = cursor.fetchall()
        if cursor.rowcount == 0:
            data = [("No Data", 0, 0, 0)]

    df = pd.DataFrame(data)
    if VoucherType == "all_ledger":
        df.columns = [str(_("LedgerName")), str(_("Balance"))]
    elif VoucherType == "group_wise":
        df.columns = [
            str(_("LedgerName")),
            str(_("Debit")),
            str(_("Credit")),
            str(_("Balance")),
        ]
    elif VoucherType == "ledger_wise":
        # taiking Opening Balance
        opening_stock_balance = query_openingBalance_data(
            CompanyID,
            BranchID,
            FromDate,
            ToDate,
            PriceRounding,
            value,
            ManualOpeningBalance,
        )
        op_balance_row = pd.DataFrame(opening_stock_balance, index=[0])
        # calculating Debit and Credit with opening balance

        balance = 0
        if op_balance_row.at[0, 7]:
            balance = round(op_balance_row.at[0, 7], PriceRounding)
        cal_balance = 0
        is_added = False
        balance_arr = [balance]
        for i in range(len(data)):
            if cal_balance == 0 and not is_added:
                is_added = True
                cal_balance = balance
            debit = 0
            credit = 0
            if data[i][6] != None:
                debit = data[i][6]
            if data[i][7] != None:
                credit = data[i][7]

            cal_balance = + debit + cal_balance - credit
            balance_arr.append(round(cal_balance, PriceRounding))
        balance_arr.append(round(cal_balance, PriceRounding))

        # adding Total to laast Row to data frame
        total_df = df[[6, 7]].sum().reindex(df.columns, fill_value="")
        df.loc[str(_("Total"))] = total_df
        # adding Opening Stock in first Row to data frame
        df = pd.concat([op_balance_row, df]).reset_index(drop=True)
        # adding Column Heading to Dataframe
        df.columns = [
            str(_("VoucherNo")),
            str(_("Narration")),
            str(_("Date")),
            str(_("Particulars")),
            str(_("LedgerName")),
            str(_("VoucherType")),
            str(_("Debit")),
            str(_("Credit")),
        ]
        # convert date format(millisecond) to str in dataframe
        df["Date"] = df["Date"].astype(str)
        # inserting a calculated Stock column to dataframe
        df.insert(loc=8, column="Balance", value=balance_arr)

        # add Credit/Debit to the first row of dataframe
        df.at[len(df.index)-1, 'Particulars'] = "Total"
        if balance > 0:
            df.at[0, "Debit"] = abs(balance)
            df.at[0, "Credit"] = "0"
            df.at[0, "Balance"] = abs(balance)
            # adding balance to TotalDebit
            df.at[len(df.index) - 1, "Debit"] = abs(balance) + \
                Decimal(total_df.at[6])
            df.at[len(df.index) - 1,
                  "Credit"] = Decimal(total_df.at[7]) + Decimal(0)

        if balance < 0:
            df.at[0, "Credit"] = abs(balance)
            df.at[0, "Debit"] = "0"
            df.at[0, "Balance"] = balance
            # adding balance to TotalCredit
            df.at[len(df.index) - 1,
                  "Debit"] = Decimal(total_df.at[6]) + Decimal(0)
            df.at[len(df.index) - 1, "Credit"] = abs(balance) + \
                Decimal(total_df.at[7])

    json_records = df.reset_index().to_json(orient="records")
    details = json.loads(json_records)
    return df, details


def query_updateLedgerBalance(CompanyID, BranchID):
    cursor = connection.cursor()
    dic = {"BranchID": BranchID, "CompanyID": CompanyID}
    cursor.execute(
        """
        UPDATE public."accountLedger_accountLedger" AS A SET "Balance" = (SELECT NULLIF(SUM("Debit" - "Credit") ,0) 
        FROM "public"."ledgerPostings_ledgerPosting" WHERE "LedgerID" = A."LedgerID" AND "CompanyID_id" = A."CompanyID_id") 
        WHERE "CompanyID_id" = %(CompanyID)s
    """,
        dic,
    )


def query_stockValue_report_data(
    CompanyID, BranchID, FromDate, ToDate, PriceRounding, ProductID, WareHouseID
):
    cursor = connection.cursor()
    dic = {
        "ProductID": int(ProductID),
        "BranchID": BranchID,
        "ToDate": ToDate,
        "CompanyID": CompanyID,
        "WareHouseID": int(WareHouseID),
        "PriceRounding": int(PriceRounding),
    }
    cursor.execute(
        """
    
        SELECT * from (
        SELECT "ProductCode","AutoBarcode","ProductName",
        
        CASE WHEN %(WareHouseID)s > 0 THEN
        (SELECT NULLIF("WarehouseName", '') FROM public."warehouse_warehouse" AS WH WHERE WH."CompanyID_id" = P."CompanyID_id" AND WH."WarehouseID" = %(WareHouseID)s)
        ELSE ''
        END AS WarehouseName

        ,round("PurchasePrice",%(PriceRounding)s),round("SalesPrice",%(PriceRounding)s),    
            
        CAST((SELECT NULLIF(SUM(SP."QtyIn" - SP."QtyOut"), 0) FROM public."stockPosting_stockPosting" AS SP       
        WHERE SP."CompanyID_id" = %(CompanyID)s AND 


        CASE WHEN %(WareHouseID)s > 0 THEN
        SP."ProductID" = P."ProductID" AND "WareHouseID" = %(WareHouseID)s
        ELSE
        SP."ProductID" = P."ProductID" 
        END        
        AND SP."IsActive" = 'true' AND SP."BranchID" = '1' AND "Date" <= %(ToDate)s) AS decimal(24, 2)) Stock,       
        -------Unit-------
        (SELECT NULLIF("UnitName", '') FROM public."units_unit" AS UN WHERE UN."CompanyID_id" = P."CompanyID_id" AND UN."UnitID" = PL."UnitID" AND PL."DefaultUnit" = 'true'  ) AS BaseUnitName,

        (SELECT coalesce(round("MultiFactor", '0'),%(PriceRounding)s) FROM public."pricelist_pricelist" AS UN WHERE UN."CompanyID_id" = P."CompanyID_id" AND UN."ProductID" = PL."ProductID" AND UN."UnitInReports" = 'true')AS StockInBaseUnit,
        

        (SELECT NULLIF("UnitName", '') FROM public."units_unit" AS UN INNER JOIN public.pricelist_pricelist as AA ON  AA."BranchID" = '1' AND 
        CASE WHEN %(ProductID)s > 0 THEN
        AA."ProductID" = %(ProductID)s AND AA."UnitInReports" = 'true' 
        ELSE
        AA."ProductID" = P."ProductID" AND AA."UnitInReports" = 'true' 
        END
        AND UN."UnitID" = AA."UnitID" AND
        AA."CompanyID_id" = P."CompanyID_id" WHERE UN."CompanyID_id" = P."CompanyID_id")
        AS UnitName,
        -----END----

        --- AVG ----        
            (SELECT CASE WHEN AvgRate <>0 THEN((AvgRate) / QtyIn) WHEN AvgRate = 0 THEN (SELECT 
            
            "PurchasePrice" FROM public.pricelist_pricelist AS PL WHERE PL."ProductID" = P."ProductID" AND PL."DefaultUnit" = 'true' AND "CompanyID_id" = '6601a605-41ec-459f-aff7-82340b2d3cc8') 

            
            ELSE 0 END AS AvgRates FROM(SELECT coalesce(SUM("Rate"* "QtyIn"),0) AS AvgRate,       
            coalesce(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "CompanyID_id" = %(CompanyID)s AND "VoucherType" in('PI', 'OS', 'ES') AND "ProductID" =       
            P."ProductID" AND "BranchID" = '1' AND "QtyIn" <> 0 AND "Date" <= %(ToDate)s ) AS Temp)   
            AS Cost     
            
        FROM public.products_product AS P       
        INNER JOIN public.pricelist_pricelist PL ON P."ProductID" = PL."ProductID" 
        AND P."BranchID" = PL."BranchID" AND PL."DefaultUnit" = 'true'   AND P."CompanyID_id" =PL."CompanyID_id"    
        WHERE P."CompanyID_id" = %(CompanyID)s AND 
        CASE WHEN %(ProductID)s > 0 THEN
        P."BranchID" = '1' AND P."ProductID" = %(ProductID)s
        ELSE
        P."BranchID" = '1'
        END

    ) as t where Stock != 0 and Stock is not null
    """,
        dic,
    )
    # if int(WareHouseID) > 0 and int(ProductID) > 0:
    #     cursor.execute(
    #         """
        
    #         SELECT * from (
    #         SELECT "ProductCode","AutoBarcode","ProductName",
            
    #         (SELECT NULLIF("WarehouseName", '') FROM public."warehouse_warehouse" AS WH WHERE WH."CompanyID_id" = P."CompanyID_id" AND WH."WarehouseID" = %(WareHouseID)s)
    #         AS WarehouseName, 

    #         round("PurchasePrice",%(PriceRounding)s),round("SalesPrice",%(PriceRounding)s),    
                
    #         CAST((SELECT NULLIF(SUM(SP."QtyIn" - SP."QtyOut"), 0) FROM public."stockPosting_stockPosting" AS SP       
    #         WHERE SP."CompanyID_id" = %(CompanyID)s AND SP."ProductID" = P."ProductID" AND SP."IsActive" = 'true' AND SP."BranchID" = '1' AND "Date" <= %(ToDate)s) AS decimal(24, 2)) Stock,       
    #         --- AVG ----       
            
    #         round((SELECT CASE WHEN AvgRate <> 0 THEN((AvgRate) / QtyIn)ELSE 0 END AS AvgRate FROM(SELECT NULLIF(SUM("Rate"* "QtyIn"),0) AS AvgRate,       
    #         NULLIF(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "CompanyID_id" = %(CompanyID)s AND "VoucherType" in('PI', 'OS', 'ES') AND "ProductID" =       
    #         P."ProductID" AND "BranchID" = '1' AND "WareHouseID" = %(WareHouseID)s AND "QtyIn" > 0 AND "Date" <= %(ToDate)s ) AS Temp),%(PriceRounding)s)       
    #         AS Cost       
                
    #         FROM public.products_product AS P       
    #         INNER JOIN public.pricelist_pricelist PL ON P."ProductID" = PL."ProductID" 
    #         AND P."BranchID" = PL."BranchID" AND PL."DefaultUnit" = 'true'   AND P."CompanyID_id" =PL."CompanyID_id"    
    #         WHERE P."CompanyID_id" = %(CompanyID)s AND P."BranchID" = '1' AND P."ProductID" = %(ProductID)s
    #     ) as t where Stock != 0 and Stock is not null
    #     """,
    #         dic,
    #     )
    # elif int(WareHouseID) == 0 and int(ProductID) == 0:
    #     cursor.execute(
    #         """
    #         SELECT * from (
    #         SELECT "ProductCode","AutoBarcode","ProductName",

    #         round("PurchasePrice",%(PriceRounding)s),round("SalesPrice",%(PriceRounding)s),    
                
    #         CAST((SELECT NULLIF(SUM(SP."QtyIn" - SP."QtyOut"), 0) FROM public."stockPosting_stockPosting" AS SP       
    #         WHERE SP."CompanyID_id" = %(CompanyID)s AND SP."ProductID" = P."ProductID" AND SP."IsActive" = 'true' AND SP."BranchID" = '1' AND "Date" <= %(ToDate)s) AS decimal(24, 2)) Stock,       
    #         --- AVG ----       
            
    #         (SELECT CASE WHEN AvgRate <> 0 THEN((AvgRate) / QtyIn)ELSE 0 END AS AvgRate FROM(SELECT NULLIF(SUM("Rate"* "QtyIn"),0) AS AvgRate,       
    #         NULLIF(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "CompanyID_id" = %(CompanyID)s AND "VoucherType" in('PI', 'OS', 'ES') AND "ProductID" =       
    #         P."ProductID" AND "BranchID" = '1' AND "QtyIn" > 0 AND "Date" <= %(ToDate)s ) AS Temp)       
    #         AS Cost       
                
    #         FROM public.products_product AS P       
    #         INNER JOIN public.pricelist_pricelist PL ON P."ProductID" = PL."ProductID" 
    #         AND P."BranchID" = PL."BranchID" AND PL."DefaultUnit" = 'true'   AND P."CompanyID_id" =PL."CompanyID_id"    
    #         WHERE P."CompanyID_id" = %(CompanyID)s AND P."BranchID" = '1'
    #     ) as t where Stock != 0 and Stock is not null
    #     """,
    #         dic,
    #     )

    # elif int(WareHouseID) > 0:
    # cursor.execute(
    #     """
    #     SELECT * from (
    #     SELECT "ProductCode","AutoBarcode","ProductName",
        
    #     (SELECT NULLIF("WarehouseName", '') FROM public."warehouse_warehouse" AS WH WHERE WH."CompanyID_id" = P."CompanyID_id" AND WH."WarehouseID" = %(WareHouseID)s)
    #     AS WarehouseName, 

    #     round("PurchasePrice",%(PriceRounding)s),round("SalesPrice",%(PriceRounding)s),    
            
    #     CAST((SELECT NULLIF(SUM(SP."QtyIn" - SP."QtyOut"), 0) FROM public."stockPosting_stockPosting" AS SP       
    #     WHERE SP."CompanyID_id" = %(CompanyID)s AND "WareHouseID" = %(WareHouseID)s AND SP."ProductID" = P."ProductID" AND SP."IsActive" = 'true' AND SP."BranchID" = '1' AND "Date" <= %(ToDate)s) AS decimal(24, 2)) Stock,       
    #     --- AVG ----       
        
    #     round((SELECT CASE WHEN AvgRate <> 0 THEN((AvgRate) / QtyIn)ELSE 0 END AS AvgRate FROM(SELECT NULLIF(SUM("Rate"* "QtyIn"),0) AS AvgRate,       
    #     NULLIF(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "CompanyID_id" = %(CompanyID)s AND "VoucherType" in('PI', 'OS', 'ES') AND "ProductID" =       
    #     P."ProductID" AND "BranchID" = '1' AND "QtyIn" > 0 AND "Date" <= %(ToDate)s ) AS Temp),%(PriceRounding)s)       
    #     AS Cost       
            
    #     FROM public.products_product AS P       
    #     INNER JOIN public.pricelist_pricelist PL ON P."ProductID" = PL."ProductID" 
    #     AND P."BranchID" = PL."BranchID" AND PL."DefaultUnit" = 'true'   AND P."CompanyID_id" =PL."CompanyID_id"    
    #     WHERE P."CompanyID_id" = %(CompanyID)s AND P."BranchID" = '1' 
    # ) as t where Stock != 0 and Stock is not null
    # """,
    #     dic,
    # )
    # elif int(ProductID) > 0:
    #     cursor.execute(
    #         """
    #         SELECT * from (
    #         SELECT "ProductCode","AutoBarcode","ProductName",round("PurchasePrice",%(PriceRounding)s),round("SalesPrice",%(PriceRounding)s),    
                
    #         CAST((SELECT NULLIF(SUM(SP."QtyIn" - SP."QtyOut"), 0) FROM public."stockPosting_stockPosting" AS SP       
    #         WHERE SP."CompanyID_id" = %(CompanyID)s AND SP."ProductID" = P."ProductID" AND SP."IsActive" = 'true' AND SP."BranchID" = '1' AND "Date" <= %(ToDate)s) AS decimal(24, 2)) Stock,       
    #         --- AVG ----       
            
    #         round((SELECT CASE WHEN AvgRate <> 0 THEN((AvgRate) / QtyIn)ELSE 0 END AS AvgRate FROM(SELECT NULLIF(SUM("Rate"* "QtyIn"),0) AS AvgRate,       
    #         NULLIF(SUM("QtyIn"), 0) AS QtyIn from public."stockPosting_stockPosting" where "CompanyID_id" = %(CompanyID)s AND "VoucherType" in('PI', 'OS', 'ES') AND "ProductID" =       
    #         P."ProductID" AND "BranchID" = '1' AND "QtyIn" > 0 AND "Date" <= %(ToDate)s ) AS Temp),%(PriceRounding)s)       
    #         AS Cost       
                
    #         FROM public.products_product AS P       
    #         INNER JOIN public.pricelist_pricelist PL ON P."ProductID" = PL."ProductID" 
    #         AND P."BranchID" = PL."BranchID" AND PL."DefaultUnit" = 'true'   AND P."CompanyID_id" =PL."CompanyID_id"    
    #         WHERE P."CompanyID_id" = %(CompanyID)s AND P."BranchID" = '1' AND P."ProductID" = %(ProductID)s
    #     ) as t where Stock != 0 and Stock is not null
    #     """,
    #         dic,
    #     )
    
    data = cursor.fetchall()

    if cursor.rowcount == 0:
        data = [("", "", "NO DATA", "", "","","","", 0, 0,0)]
   
    df = pd.DataFrame(data)
    # if int(WareHouseID) > 0:
    df.columns = [
        str(_("ProductCode")),
        str(_("Barcode")),
        str(_("ProductName")),
        str(_("WarehouseName")),
        str(_("PurchasePrice")),
        str(_("SalesPrice")),
        str(_("StockInBaseUnit")),
        str(_("BaseUnitName")),
        str(_("Stock")),
        str(_("UnitName")),
        str(_("Cost")),
    ]
    print(df)
    # else:
    #     df.columns = [
    #         str(_("ProductCode")),
    #         str(_("Barcode")),
    #         str(_("ProductName")),
    #         str(_("PurchasePrice")),
    #         str(_("SalesPrice")),
    #         str(_("Stock")),
    #         str(_("Cost")),
    #     ]

    if df['Stock'].eq(0).any():
        sum_column = 0
    else:
        sum_column = df["StockInBaseUnit"] / df["Stock"]
    df["Stock"] = sum_column

    tot_cost_column = df["StockInBaseUnit"] * df["Cost"]
    df["TotalCost"] = tot_cost_column
    df.loc[str(_("Total"))] = (
        df[["StockInBaseUnit", "Cost", "TotalCost"]].sum().reindex(
            df.columns, fill_value="")
    )
    # Round Folat Value
    df['Cost'] = df['Cost'].apply(lambda x: round(x, PriceRounding))
    df['TotalCost'] = df['TotalCost'].apply(lambda x: round(x, PriceRounding))

    json_records = df.reset_index().to_json(orient="records")
    details = json.loads(json_records)

    return df, details


def query_trialBalance_report_data(
    filterMethod,CompanyID, UserID, PriceRounding, BranchID, ToDate, FromDate
):
    exp_cursor = connection.cursor()
    # inc_cursor = connection.cursor()
    asset_liabilty_cursor = connection.cursor()
    dic = {
        "BranchID": BranchID,
        "ToDate": ToDate,
        "FromDate": FromDate,
        "CompanyID": CompanyID,
    }

    # cursor.execute(
    #     """
    #     SELECT * FROM               
    #     (              
    #     SELECT              
    #     --aL.LedgerName    
    #     aG."AccountGroupName"   
    #     ,(SELECT "LedgerName" FROM public."accountLedger_accountLedger"  WHERE     
    #     "LedgerID" = L."LedgerID" AND "BranchID" = 1 AND "CompanyID_id" = %(CompanyID)s) AS LedgerName     

    #     ,round(NULLIF(SUM("Debit" - "Credit"),0),2) AS Total              
    #     FROM public."ledgerPostings_ledgerPosting" AS L     
    #     iNNER jOIN public."accountLedger_accountLedger" AS AL ON l."LedgerID" =aL."LedgerID" AND al."CompanyID_id" = l."CompanyID_id"
    #     iNNER jOIN public.accountgroup_accountgroup AS AG on ag."AccountGroupID" =aL."AccountGroupUnder"   
    #     AND ag."CompanyID_id" = aL."CompanyID_id"
    #     WHERE l."BranchID" = 1 AND l."CompanyID_id" = %(CompanyID)s AND "Date" <= %(ToDate)s            
    #     Group BY l."LedgerID","LedgerName"    
    #     ,aG."AccountGroupName"   

    #     ) AS Temp              
    #     WHERE Total != 0 order by Temp.LedgerName 
    # """,
    #     dic,
    # )

    # <<<<<<<<<EXPENCE>>>>>>>>>>>
    exp_cursor.execute('''
            WITH RECURSIVE GroupInMainGroup42 AS (
            SELECT
            "AccountGroupID",
            "AccountGroupUnder",
            "AccountGroupName"
            FROM public.accountgroup_accountgroup
            WHERE
            "AccountGroupID" in (42,43,70,71) AND "CompanyID_id" = %(CompanyID)s
            UNION
            SELECT
            e."AccountGroupID",
            e."AccountGroupUnder",
            e."AccountGroupName"
            FROM
            public.accountgroup_accountgroup e
            INNER JOIN GroupInMainGroup42 s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = %(CompanyID)s
            )  
            SELECT *  
            FROM(  
            SELECT "AccountGroupName","LedgerName" ,  
            (SELECT ROUND(coalesce(SUM("Debit"), 0)- (coalesce(SUM("Credit"), 0)),2) 
            FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN %(FromDate)s AND %(ToDate)s )
            AND "BranchID" = %(BranchID)s AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
            AS Total FROM public."accountLedger_accountLedger" AL  
            INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
            WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup42) AND AL."BranchID" = %(BranchID)s
            AND AL."CompanyID_id" = %(CompanyID)s
            ) AS TEMP WHERE Total != 0;
            ''',dic)

    # <<<<<<<<<<INCOME>>>>>>>>>>
    # inc_cursor.execute('''
    #         WITH RECURSIVE GroupInMainGroup70 AS (
    #         SELECT
    #         "AccountGroupID",
    #         "AccountGroupUnder",
    #         "AccountGroupName"
    #         FROM public.accountgroup_accountgroup
    #         WHERE
    #         "AccountGroupID" in (70,71) AND "CompanyID_id" = %(CompanyID)s
    #         UNION
    #         SELECT
    #         e."AccountGroupID",
    #         e."AccountGroupUnder",
    #         e."AccountGroupName"
    #         FROM
    #         public.accountgroup_accountgroup e
    #         INNER JOIN GroupInMainGroup70 s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = %(CompanyID)s
    #         )       
    #         SELECT *
    #         FROM(  
    #         SELECT "AccountGroupName","LedgerName" ,  
    #         (SELECT ROUND(coalesce(SUM("Credit"), 0)- (coalesce(SUM("Debit"), 0)),2) 
    #         FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN %(FromDate)s AND %(ToDate)s )
    #         AND "BranchID" = %(BranchID)s AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
    #         AS Total FROM public."accountLedger_accountLedger" AL  
    #         INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
    #         WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup70) AND AL."BranchID" = %(BranchID)s
    #         AND AL."CompanyID_id" = %(CompanyID)s
    #         ) AS TEMP WHERE Total != 0;
    #     ''',dic)

    # <<<<<<<<ASSET&LIABILITY>>>>>>>>
    asset_liabilty_cursor.execute('''
        WITH RECURSIVE GroupInMainGroup AS (
        SELECT
        "AccountGroupID",
        "AccountGroupUnder",
        "AccountGroupName"
        FROM public.accountgroup_accountgroup
        WHERE
        "AccountGroupID" in (3,4) AND "CompanyID_id" = %(CompanyID)s
        UNION
        SELECT
        e."AccountGroupID",
        e."AccountGroupUnder",
        e."AccountGroupName"
        FROM
        public.accountgroup_accountgroup e
        INNER JOIN GroupInMainGroup s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = %(CompanyID)s
        )  
        SELECT *  
        FROM(  
        SELECT "AccountGroupName","LedgerName" ,  
        (SELECT ROUND(coalesce(SUM("Debit"), 0)- (coalesce(SUM("Credit"), 0)),2) 
        FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" <= %(ToDate)s )
        AND "BranchID" = %(BranchID)s AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
        AS Total FROM public."accountLedger_accountLedger" AL  
        INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
        WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup) AND AL."BranchID" = %(BranchID)s
        AND AL."CompanyID_id" = %(CompanyID)s
        ) AS TEMP WHERE Total != 0;
        ''',dic)

    data = []
    if exp_cursor.rowcount != 0:        
        data = exp_cursor.fetchall()
    # if inc_cursor.rowcount != 0:
    #     print("INCOME>>>>>>>>>>>>>>>>>>>")
    #     data += inc_cursor.fetchall()
    if asset_liabilty_cursor.rowcount != 0:
        print(type(exp_cursor.fetchall()),"ASSETLIABILTY>>>>>>>>>>>>>>>>>>>")
        data += asset_liabilty_cursor.fetchall()
    if exp_cursor.rowcount == 0 and asset_liabilty_cursor.rowcount == 0:
        data = [
            (
                "",
                "NO DATA",
                Decimal(0),
            )
        ]

    df = pd.DataFrame(data)
    
    df.columns = [str(_("AccountGroupName")), str(
        _("LedgerName")), str(_("Total"))]
    # ===============Taiking Opening Stock Value==================
    opening_stock = query_openingStockValue_data(
        CompanyID, BranchID, FromDate, ToDate, PriceRounding)
    op_stock_row = pd.DataFrame(opening_stock, index=[7])
    debit = 0
    credit = 0

    stock_value = 0
    TotalAvgValueOpening= 0 
    if op_stock_row.at[7, 0]:
        stock_value = round(op_stock_row.at[7, 0], PriceRounding)

    if filterMethod == "AVERAGE":
        opening = query_ProfitAndLoss_filter("AVG_OpeningStock",CompanyID,BranchID,FromDate,ToDate,"","")
        TotalAvgValueOpening = opening[0][0]
    elif filterMethod == "FIFO":
        opening = query_ProfitAndLoss_filter("FIFO_OpeningStock",CompanyID,BranchID,FromDate,ToDate,"","")
        TotalAvgValueOpening = opening[0][0]
    elif filterMethod == "LIFO":
        opening = query_ProfitAndLoss_filter("LIFO_OpeningStock",CompanyID,BranchID,FromDate,ToDate,"","")
        TotalAvgValueOpening = opening[0][0]
    # ===============END===============
    # SHIFT ROW TOP TO BOTTOM
    index_array = df.loc[df[str(
        _("LedgerName"))] == 'Suspense Account'].index.tolist()

    print(index_array)
    print("===============================.......................")
    if index_array:
        index = index_array[0]
        # reduce opening stock from Suspense Account
        df.loc[index, 'Total'] = df.loc[index, 'Total']-stock_value
        if df.loc[index, 'Total'] > 0:
            df.at[index, str(
        _("LedgerName"))] = 'Opening Blance Diffrence'
        elif df.loc[index, 'Total'] < 0:
            df.at[index, str(
        _("LedgerName"))] = 'Opening Blance Diffrence'
        elif df.loc[index, 'Total'] == 0:
            df.at[index, str(_("LedgerName"))] = 'Opening Blance Diffrence'



        idx = df.index.tolist()
        idx.pop(index)
        df = df.reindex(idx + [index])

    df[str(_("Debit"))] = df[str(_("Total"))].apply(
        lambda x: round(float(x), PriceRounding) if x >= 0 else 0)
    df[str(_("Credit"))] = df[str(_("Total"))].apply(lambda x: round(
        abs(float(x)), PriceRounding) if x <= 0 else 0)
    df = df.drop([str(_("Total"))], axis=1)
    # Adding To DataFrame Opening Stock Value
    if TotalAvgValueOpening > 0:
        print("TotalAvgValueOpening > 0>>>>>>>>*************>>>>>>>>>>>",TotalAvgValueOpening)
        debit = float(TotalAvgValueOpening)
        df.loc[len(df.index)] = ["", "Opening Stock Value", debit, credit]
    elif TotalAvgValueOpening < 0:
        print("TotalAvgValueOpening < 0>>>>>>>*************>>>>>>>>>>>>",TotalAvgValueOpening)
        credit = float(TotalAvgValueOpening)
        df.loc[len(df.index)] = ["", "Opening Stock Value", debit, credit]
    else:
        print("ELSEEEEEEEEEEEEEEEEEEEEEEEEEEUY>>*************>>>>>>>>>>>>>>>>>",TotalAvgValueOpening)

    print(df)
    tot_index = len(df.index)+1
    # adding Total in laast Row to data frame
    # df.loc[tot_index] = df[[str(_("Debit")), str(_("Credit"))]
    #                        ].sum().reindex(df.columns, fill_value='')
    Debit_total = df[str(_("Debit"))].sum()
    Credit_total = df[str(_("Credit"))].sum()
    # Debit_total = float(df.at[tot_index, str(_("Debit"))])
    # Credit_total = float(df.at[tot_index, str(_("Credit"))])
    debit = 0
    credit = 0
    diffrence = 0
    Difference_val = Debit_total - Credit_total

    # if Difference_val:
    if Debit_total > Credit_total:
        diffrence = Debit_total
        credit = Debit_total - Credit_total
        df.loc[tot_index] = ["", "Loss", debit, credit]
    elif Debit_total < Credit_total:
        diffrence = Credit_total
        debit = Credit_total - Debit_total
        df.loc[tot_index] = ["", "Profit", debit, credit]
    elif Debit_total == Credit_total:
        diffrence = Debit_total

    # df.loc[len(df.index)] = ["", "Profit and Loss account", debit, credit]
    df.loc[tot_index+1] = ["", "Total", diffrence, diffrence]
    
    # If Suspense Account is 0 Then Remove Suspence Account
    index_array = df.loc[df[str(
    _("AccountGroupName"))] == 'Suspense Accounts'].index.tolist()
    if index_array:
        if df.loc[index, 'Debit'] == 0 and df.loc[index, 'Credit'] == 0:
            df.drop([index], axis=0, inplace=True)
    # ==========END=========
    json_records = df.reset_index().to_json(orient="records")
    details = json.loads(json_records)

    return df, details


def query_Cash_OR_Bank_Book_report_data(value, CompanyID, BranchID, FromDate, ToDate, PriceRounding, VoucherType, RouteLedgers, ManualOpeningBalance):
    cursor = connection.cursor()
    dic = {'value': value, 'CompanyID': CompanyID, 'VoucherType': VoucherType,
           'RouteLedgers': RouteLedgers, 'BranchID': BranchID, 'FromDate': FromDate, 'ToDate': ToDate}
    if VoucherType == 'all_ledger':
        cursor.execute('''
        SELECT          
        CASE WHEN "VoucherType" ='SI' THEN (SELECT "VoucherNo" FROM public."salesMasters_salesMaster" WHERE "BranchID" = '1' AND "SalesMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")         
        WHEN "VoucherType" ='SR' THEN (SELECT "VoucherNo" FROM public."salesReturnMasters_salesReturnMaster" WHERE "BranchID" = '1' AND "SalesReturnMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")        
        WHEN "VoucherType" ='PI' THEN (SELECT "VoucherNo" FROM public."purchaseMasters_purchaseMaster" WHERE "BranchID" = '1' AND "PurchaseMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")        
        WHEN "VoucherType" ='PR' THEN (SELECT "VoucherNo" FROM public."purchaseReturnMasters_purchaseReturnMaster" WHERE "BranchID" = '1' AND "PurchaseReturnMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")        
        WHEN "VoucherType" ='CR' THEN (SELECT "VoucherNo" FROM public."receiptMasters_receiptMaster" WHERE "BranchID" = '1' AND "ReceiptMasterID" = "VoucherMasterID" AND "VoucherType"='CR' AND "CompanyID_id" = L."CompanyID_id")        
        WHEN "VoucherType" ='BR' THEN (SELECT "VoucherNo" FROM public."receiptMasters_receiptMaster" WHERE "BranchID" = '1' AND "ReceiptMasterID" = "VoucherMasterID" AND "VoucherType"='BR' AND "CompanyID_id" = L."CompanyID_id")        
        WHEN "VoucherType" ='CP' THEN (SELECT "VoucherNo" FROM public."paymentMasters_paymentMaster" WHERE "BranchID" = '1' AND "PaymentMasterID" = "VoucherMasterID" AND "VoucherType"='CP' AND "CompanyID_id" = L."CompanyID_id")        
        WHEN "VoucherType" ='BP' THEN (SELECT "VoucherNo" FROM public."paymentMasters_paymentMaster" WHERE "BranchID" = '1' AND "PaymentMasterID" = "VoucherMasterID" AND "VoucherType"='BP' AND "CompanyID_id" = L."CompanyID_id")        
        WHEN "VoucherType" ='LOB' THEN (SELECT "VoucherNo" FROM public."accountLedger_accountLedger" WHERE "BranchID" = '1' AND "LedgerID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")        
        WHEN "VoucherType" ='OS' THEN (SELECT "VoucherNo" FROM public."openingStockMasters_openingStockMaster" WHERE "BranchID" = '1' AND "OpeningStockMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")          
        WHEN "VoucherType" ='JL' THEN (SELECT "VoucherNo" FROM public."journalMaster_journalMaster" WHERE "BranchID" = '1' AND "JournalMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")   
        WHEN "VoucherType" ='EX' THEN (SELECT "VoucherNo" FROM public."expenseMasters_expenseMaster" WHERE "BranchID" = '1' AND "ExpenseMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")  
        ELSE ''  
        END AS "VoucherNo",        


            CASE WHEN "VoucherType" ='SI' THEN (SELECT "Notes" FROM public."salesMasters_salesMaster" WHERE "BranchID" = '1' AND "SalesMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")         
    WHEN "VoucherType" ='SR' THEN (SELECT "Notes" FROM public."salesReturnMasters_salesReturnMaster" WHERE "BranchID" = '1' AND "SalesReturnMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")        
    WHEN "VoucherType" ='PI' THEN (SELECT "Notes" FROM public."purchaseMasters_purchaseMaster" WHERE "BranchID" = '1' AND "PurchaseMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")        
    WHEN "VoucherType" ='PR' THEN (SELECT "Notes" FROM public."purchaseReturnMasters_purchaseReturnMaster" WHERE "BranchID" = '1' AND "PurchaseReturnMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")        
    WHEN "VoucherType" ='EX' THEN (SELECT "Notes" FROM public."expenseMasters_expenseMaster" WHERE "BranchID" = '1' AND "ExpenseMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")  
    WHEN "VoucherType" ='CR' THEN            

    (SELECT "Narration" FROM public."receiptDetailses_receiptDetails" AS A        
    INNER JOIN public."receiptMasters_receiptMaster" AS B ON A."ReceiptMasterID" = B."ReceiptMasterID" AND B."CompanyID_id" = L."CompanyID_id"         
    INNER JOIN public."ledgerPostings_ledgerPosting" AS C ON A."LedgerID" = C."LedgerID" AND C."CompanyID_id" = L."CompanyID_id"        
    WHERE B."BranchID" = '1' AND A."ReceiptDetailID" = "VoucherDetailID" AND B."VoucherType"='CR'        
    AND A."LedgerID"= L."LedgerID" AND  C."LedgerPostingID" = L."LedgerPostingID" AND A."CompanyID_id" = L."CompanyID_id")        

    WHEN "VoucherType" ='BR' THEN         

    (SELECT "Narration" FROM public."receiptDetailses_receiptDetails" AS A        
    INNER JOIN public."receiptMasters_receiptMaster" AS B ON A."ReceiptMasterID" = B."ReceiptMasterID" AND B."CompanyID_id" = L."CompanyID_id"         
    INNER JOIN public."ledgerPostings_ledgerPosting" AS C ON A."LedgerID" = C."LedgerID" AND C."CompanyID_id" = L."CompanyID_id"          
    WHERE B."BranchID" = '1' AND A."ReceiptDetailID" = "VoucherDetailID" AND B."VoucherType"='BR'        
    AND A."LedgerID"= L."LedgerID" AND  C."LedgerPostingID" = L."LedgerPostingID" AND A."CompanyID_id" = L."CompanyID_id")           

    WHEN "VoucherType" ='CP' THEN         

    (SELECT "Narration" FROM public."paymentDetails_paymentDetail" AS A        
    INNER JOIN public."paymentMasters_paymentMaster" AS B ON A."PaymentMasterID" = B."PaymentMasterID" AND B."CompanyID_id" = L."CompanyID_id"         
    INNER JOIN public."ledgerPostings_ledgerPosting" AS C ON A."LedgerID" = C."LedgerID" AND C."CompanyID_id" = L."CompanyID_id"        
    WHERE B."BranchID" = '1' AND A."PaymentDetailsID" = "VoucherDetailID" AND B."VoucherType"='CP'        
    AND A."LedgerID"= L."LedgerID" AND  C."LedgerPostingID" = L."LedgerPostingID" AND A."CompanyID_id" = L."CompanyID_id")        

    WHEN "VoucherType" ='BP' THEN         

    (SELECT "Narration" FROM public."paymentDetails_paymentDetail" AS A        
    INNER JOIN public."paymentMasters_paymentMaster" AS B ON A."PaymentMasterID" = B."PaymentMasterID" AND B."CompanyID_id" = L."CompanyID_id"         
    INNER JOIN public."ledgerPostings_ledgerPosting" AS C ON B."LedgerID" = B."LedgerID" AND C."CompanyID_id" = L."CompanyID_id"        
    WHERE B."BranchID" = '1' AND  A."PaymentDetailsID" = "VoucherDetailID" AND B."VoucherType"='BP'        
    AND A."LedgerID"= L."LedgerID" AND  C."LedgerPostingID" = L."LedgerPostingID" AND A."CompanyID_id" = C."CompanyID_id")         


    WHEN "VoucherType" ='LOB' THEN (SELECT "Notes" FROM public."accountLedger_accountLedger" WHERE "BranchID" = '1' AND "LedgerID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")        
    WHEN "VoucherType" ='OS' THEN (SELECT "Notes" FROM public."openingStockMasters_openingStockMaster" WHERE "BranchID" = '1' AND "OpeningStockMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")          

    WHEN "VoucherType" ='JL' THEN         

    (SELECT "Narration" FROM public."journalDetails_journalDetail" AS A        
    INNER JOIN public."journalMaster_journalMaster" AS B ON A."JournalMasterID" = B."JournalMasterID" AND A."CompanyID_id" = B."CompanyID_id"        
    INNER JOIN public."ledgerPostings_ledgerPosting" AS C ON A."LedgerID" = C."LedgerID"  AND A."CompanyID_id" = C."CompanyID_id"        
    WHERE B."BranchID" = '1' AND A."JournalDetailsID" = "VoucherDetailID"         
    AND A."LedgerID"= L."LedgerID" AND  C."LedgerPostingID" = L."LedgerPostingID" AND A."CompanyID_id" = C."CompanyID_id"   )        

    END AS "Narration"        

        ,L."Date" AS Date    
        ,CASE WHEN "VoucherType" ='SI' THEN 'Sales Invoice'        
        WHEN "VoucherType" ='SR' THEN 'Sales Return'        
        WHEN "VoucherType" ='PI' THEN 'Purchase Invoice'        
        WHEN "VoucherType" ='PR' THEN 'Purchase Return'        
        WHEN "VoucherType" ='CR' THEN 'Cash Receipt'        
        WHEN "VoucherType" ='BR' THEN 'Bank Receipt'        
        WHEN "VoucherType" ='CP' THEN 'Cash Payment'        
        WHEN "VoucherType" ='BP' THEN 'Bank Payment'        
        WHEN "VoucherType" ='LOB' THEN 'Ledger Opening Balance'        
        WHEN "VoucherType" ='OS' THEN 'Opening Stock'        
        WHEN "VoucherType" ='JL' THEN 'Journal Entry'    
        WHEN "VoucherType" ='EX' THEN 'Expense'   
        END AS Particulars        
        ,LL."LedgerName"         
        ,L."VoucherType"          
        ,round(L."Debit",2)        
        ,round(L."Credit",2)      
        FROM public."ledgerPostings_ledgerPosting" L        
        INNER JOIN public."accountLedger_accountLedger" AS LL ON L."LedgerID" = LL."LedgerID" AND L."CompanyID_id" = LL."CompanyID_id"        
        WHERE L."Date" between %(FromDate)s AND %(ToDate)s AND L."CompanyID_id" = %(CompanyID)s AND 
        
        L."LedgerID" IN (SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "CompanyID_id" = %(CompanyID)s AND "AccountGroupUnder" = %(value)s )  
        order by "Date" 
        ''', dic)
    else:
        cursor.execute('''
        SELECT          
        CASE WHEN "VoucherType" ='SI' THEN (SELECT "VoucherNo" FROM public."salesMasters_salesMaster" WHERE "BranchID" = '1' AND "SalesMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")         
        WHEN "VoucherType" ='SR' THEN (SELECT "VoucherNo" FROM public."salesReturnMasters_salesReturnMaster" WHERE "BranchID" = '1' AND "SalesReturnMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")        
        WHEN "VoucherType" ='PI' THEN (SELECT "VoucherNo" FROM public."purchaseMasters_purchaseMaster" WHERE "BranchID" = '1' AND "PurchaseMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")        
        WHEN "VoucherType" ='PR' THEN (SELECT "VoucherNo" FROM public."purchaseReturnMasters_purchaseReturnMaster" WHERE "BranchID" = '1' AND "PurchaseReturnMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")        
        WHEN "VoucherType" ='CR' THEN (SELECT "VoucherNo" FROM public."receiptMasters_receiptMaster" WHERE "BranchID" = '1' AND "ReceiptMasterID" = "VoucherMasterID" AND "VoucherType"='CR' AND "CompanyID_id" = L."CompanyID_id")        
        WHEN "VoucherType" ='BR' THEN (SELECT "VoucherNo" FROM public."receiptMasters_receiptMaster" WHERE "BranchID" = '1' AND "ReceiptMasterID" = "VoucherMasterID" AND "VoucherType"='BR' AND "CompanyID_id" = L."CompanyID_id")        
        WHEN "VoucherType" ='CP' THEN (SELECT "VoucherNo" FROM public."paymentMasters_paymentMaster" WHERE "BranchID" = '1' AND "PaymentMasterID" = "VoucherMasterID" AND "VoucherType"='CP' AND "CompanyID_id" = L."CompanyID_id")        
        WHEN "VoucherType" ='BP' THEN (SELECT "VoucherNo" FROM public."paymentMasters_paymentMaster" WHERE "BranchID" = '1' AND "PaymentMasterID" = "VoucherMasterID" AND "VoucherType"='BP' AND "CompanyID_id" = L."CompanyID_id")        
        WHEN "VoucherType" ='LOB' THEN (SELECT "VoucherNo" FROM public."accountLedger_accountLedger" WHERE "BranchID" = '1' AND "LedgerID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")        
        WHEN "VoucherType" ='OS' THEN (SELECT "VoucherNo" FROM public."openingStockMasters_openingStockMaster" WHERE "BranchID" = '1' AND "OpeningStockMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")          
        WHEN "VoucherType" ='JL' THEN (SELECT "VoucherNo" FROM public."journalMaster_journalMaster" WHERE "BranchID" = '1' AND "JournalMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")   
        WHEN "VoucherType" ='EX' THEN (SELECT "VoucherNo" FROM public."expenseMasters_expenseMaster" WHERE "BranchID" = '1' AND "ExpenseMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")  
        ELSE ''  
        END AS "VoucherNo",        


            CASE WHEN "VoucherType" ='SI' THEN (SELECT "Notes" FROM public."salesMasters_salesMaster" WHERE "BranchID" = '1' AND "SalesMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")         
    WHEN "VoucherType" ='SR' THEN (SELECT "Notes" FROM public."salesReturnMasters_salesReturnMaster" WHERE "BranchID" = '1' AND "SalesReturnMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")        
    WHEN "VoucherType" ='PI' THEN (SELECT "Notes" FROM public."purchaseMasters_purchaseMaster" WHERE "BranchID" = '1' AND "PurchaseMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")        
    WHEN "VoucherType" ='PR' THEN (SELECT "Notes" FROM public."purchaseReturnMasters_purchaseReturnMaster" WHERE "BranchID" = '1' AND "PurchaseReturnMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")        
    WHEN "VoucherType" ='EX' THEN (SELECT "Notes" FROM public."expenseMasters_expenseMaster" WHERE "BranchID" = '1' AND "ExpenseMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")  
    WHEN "VoucherType" ='CR' THEN            

    (SELECT "Narration" FROM public."receiptDetailses_receiptDetails" AS A        
    INNER JOIN public."receiptMasters_receiptMaster" AS B ON A."ReceiptMasterID" = B."ReceiptMasterID" AND B."CompanyID_id" = L."CompanyID_id"         
    INNER JOIN public."ledgerPostings_ledgerPosting" AS C ON A."LedgerID" = C."LedgerID" AND C."CompanyID_id" = L."CompanyID_id"        
    WHERE B."BranchID" = '1' AND A."ReceiptDetailID" = "VoucherDetailID" AND B."VoucherType"='CR'        
    AND A."LedgerID"= L."LedgerID" AND  C."LedgerPostingID" = L."LedgerPostingID" AND A."CompanyID_id" = L."CompanyID_id")        

    WHEN "VoucherType" ='BR' THEN         

    (SELECT "Narration" FROM public."receiptDetailses_receiptDetails" AS A        
    INNER JOIN public."receiptMasters_receiptMaster" AS B ON A."ReceiptMasterID" = B."ReceiptMasterID" AND B."CompanyID_id" = L."CompanyID_id"         
    INNER JOIN public."ledgerPostings_ledgerPosting" AS C ON A."LedgerID" = C."LedgerID" AND C."CompanyID_id" = L."CompanyID_id"          
    WHERE B."BranchID" = '1' AND A."ReceiptDetailID" = "VoucherDetailID" AND B."VoucherType"='BR'        
    AND A."LedgerID"= L."LedgerID" AND  C."LedgerPostingID" = L."LedgerPostingID" AND A."CompanyID_id" = L."CompanyID_id")           

    WHEN "VoucherType" ='CP' THEN         

    (SELECT "Narration" FROM public."paymentDetails_paymentDetail" AS A        
    INNER JOIN public."paymentMasters_paymentMaster" AS B ON A."PaymentMasterID" = B."PaymentMasterID" AND B."CompanyID_id" = L."CompanyID_id"         
    INNER JOIN public."ledgerPostings_ledgerPosting" AS C ON A."LedgerID" = C."LedgerID" AND C."CompanyID_id" = L."CompanyID_id"        
    WHERE B."BranchID" = '1' AND A."PaymentDetailsID" = "VoucherDetailID" AND B."VoucherType"='CP'        
    AND A."LedgerID"= L."LedgerID" AND  C."LedgerPostingID" = L."LedgerPostingID" AND A."CompanyID_id" = L."CompanyID_id")        

    WHEN "VoucherType" ='BP' THEN         

    (SELECT "Narration" FROM public."paymentDetails_paymentDetail" AS A        
    INNER JOIN public."paymentMasters_paymentMaster" AS B ON A."PaymentMasterID" = B."PaymentMasterID" AND B."CompanyID_id" = L."CompanyID_id"         
    INNER JOIN public."ledgerPostings_ledgerPosting" AS C ON B."LedgerID" = B."LedgerID" AND C."CompanyID_id" = L."CompanyID_id"        
    WHERE B."BranchID" = '1' AND  A."PaymentDetailsID" = "VoucherDetailID" AND B."VoucherType"='BP'        
    AND A."LedgerID"= L."LedgerID" AND  C."LedgerPostingID" = L."LedgerPostingID" AND A."CompanyID_id" = C."CompanyID_id")         


    WHEN "VoucherType" ='LOB' THEN (SELECT "Notes" FROM public."accountLedger_accountLedger" WHERE "BranchID" = '1' AND "LedgerID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")        
    WHEN "VoucherType" ='OS' THEN (SELECT "Notes" FROM public."openingStockMasters_openingStockMaster" WHERE "BranchID" = '1' AND "OpeningStockMasterID" = "VoucherMasterID" AND "CompanyID_id" = L."CompanyID_id")          

    WHEN "VoucherType" ='JL' THEN         

    (SELECT "Narration" FROM public."journalDetails_journalDetail" AS A        
    INNER JOIN public."journalMaster_journalMaster" AS B ON A."JournalMasterID" = B."JournalMasterID" AND A."CompanyID_id" = B."CompanyID_id"        
    INNER JOIN public."ledgerPostings_ledgerPosting" AS C ON A."LedgerID" = C."LedgerID"  AND A."CompanyID_id" = C."CompanyID_id"        
    WHERE B."BranchID" = '1' AND A."JournalDetailsID" = "VoucherDetailID"         
    AND A."LedgerID"= L."LedgerID" AND  C."LedgerPostingID" = L."LedgerPostingID" AND A."CompanyID_id" = C."CompanyID_id"   )        

    END AS "Narration"       

        ,L."Date" AS Date    
        ,CASE WHEN "VoucherType" ='SI' THEN 'Sales Invoice'        
        WHEN "VoucherType" ='SR' THEN 'Sales Return'        
        WHEN "VoucherType" ='PI' THEN 'Purchase Invoice'        
        WHEN "VoucherType" ='PR' THEN 'Purchase Return'        
        WHEN "VoucherType" ='CR' THEN 'Cash Receipt'        
        WHEN "VoucherType" ='BR' THEN 'Bank Receipt'        
        WHEN "VoucherType" ='CP' THEN 'Cash Payment'        
        WHEN "VoucherType" ='BP' THEN 'Bank Payment'        
        WHEN "VoucherType" ='LOB' THEN 'Ledger Opening Balance'        
        WHEN "VoucherType" ='OS' THEN 'Opening Stock'        
        WHEN "VoucherType" ='JL' THEN 'Journal Entry'    
        WHEN "VoucherType" ='EX' THEN 'Expense'   
        END AS Particulars        
        ,LL."LedgerName"         
        ,L."VoucherType"          
        ,round(L."Debit",2)        
        ,round(L."Credit",2)      
        FROM public."ledgerPostings_ledgerPosting" L        
        INNER JOIN public."accountLedger_accountLedger" AS LL ON L."LedgerID" = LL."LedgerID" AND L."CompanyID_id" = LL."CompanyID_id"        
        WHERE L."Date" between %(FromDate)s AND %(ToDate)s AND L."CompanyID_id" = %(CompanyID)s AND 
        L."LedgerID" IN %(RouteLedgers)s
       
        order by "Date" 
        ''',
                       dic
                       )

    data = cursor.fetchall()
    if cursor.rowcount == 0:
        data = [('', '', 'NO DATA', '', '', '', 0, 0)]

    df = pd.DataFrame(data)
    # taiking Opening Balance Balance
    opening_balance = query_Cash_OR_Bank_book_openingBalance_data(
        value, CompanyID, BranchID, FromDate, ToDate, PriceRounding, VoucherType, RouteLedgers, ManualOpeningBalance)
    op_balance_row = pd.DataFrame(opening_balance, index=[0])
    # calculating Debit and Credit with opening balance

    balance = 0
    if op_balance_row.at[0, 7]:
        balance = round(op_balance_row.at[0, 7], PriceRounding)
    cal_balance = 0
    is_added = False
    balance_arr = [balance]
    for i in range(len(data)):
        if cal_balance == 0 and not is_added:
            is_added = True
            cal_balance = balance

        debit = 0
        credit = 0
        if data[i][6] != None:
            debit = data[i][6]
        if data[i][7] != None:
            credit = data[i][7]
        cal_balance = + debit + cal_balance - credit
        balance_arr.append(round(cal_balance, PriceRounding))
    balance_arr.append(round(cal_balance, PriceRounding))

    # adding Total to laast Row to data frame
    total_df = df[[6, 7]].sum().reindex(df.columns, fill_value='')
    df.loc[str(_('Total'))] = total_df
    # adding Opening Stock in first Row to data frame
    df = pd.concat([op_balance_row, df]).reset_index(drop=True)
    # adding Column Heading to Dataframe
    df.columns = [str(_('VoucherNo')), str(_('Narration')), str(_('Date')), str(_('Particulars')), str(
        _('LedgerName')), str(_('VoucherType')), str(_('Receipts')), str(_('Payments'))]
    # convert date format(millisecond) to str in dataframe
    df['Date'] = df['Date'].astype(str)
    # inserting a calculated Stock column to dataframe
    df.insert(loc=8,
              column='Balance',
              value=balance_arr)

    # add Credit/Debit to the first row of dataframe
    df.at[len(df.index)-1, 'LedgerName'] = "Total"
    if balance > 0:
        df.at[0, 'Receipts'] = abs(balance)
        df.at[0, 'Payments'] = '0'
        df.at[0, 'Balance'] = abs(balance)
        # adding balance to TotalDebit
        df.at[len(df.index)-1, 'Receipts'] = abs(balance) + \
            Decimal(total_df.at[6])
        df.at[len(df.index)-1, 'Payments'] = Decimal(total_df.at[7])+Decimal(0)

    if balance < 0:
        df.at[0, 'Payments'] = abs(balance)
        df.at[0, 'Receipts'] = '0'
        df.at[0, 'Balance'] = balance
        # adding balance to TotalCredit
        df.at[len(df.index)-1, 'Receipts'] = Decimal(total_df.at[6])+Decimal(0)
        df.at[len(df.index)-1, 'Payments'] = abs(balance) + \
            Decimal(total_df.at[7])

    json_records = df.reset_index().to_json(orient='records')
    details = json.loads(json_records)
    return df, details


def query_receipt_report_data(CompanyID, BranchID, FromDate, ToDate, PriceRounding, CashLedgers, VoucherType):
    cursor = connection.cursor()
    VoucherTypes = ('CR', 'BR')
    if VoucherType == "CR":
        VoucherTypes = ('CR',)
    elif VoucherType == "BR":
        VoucherTypes = ('BR',)
    # CashLedgers = tuple(CashLedgers,"OOOOOOOOOOOOOOOIIIIIIUUUUYYYy")
    dic = { 'BranchID': BranchID, 'FromDate': FromDate, 'ToDate': ToDate,
           'CompanyID': CompanyID, "CashLedgers": CashLedgers, "VoucherType": VoucherTypes}
    print(CashLedgers,"************************")
    if CashLedgers == "0" or CashLedgers == 0:
        print(CashLedgers,VoucherTypes)
        cursor.execute('''
        select RM."VoucherNo",RM."Date",      
        AL."LedgerName",round(RD."Amount",2) as Amount,round(RD."Discount",2) as Discount,round(RD."NetAmount",2) as NetAmount,
        CASE WHEN
        RM."VoucherType" = 'CR'  THEN 'Cash Receipt'   
        WHEN RM."VoucherType" = 'BR' THEN 'Bank Receipt'      
        END AS VoucherType, 
        RD."Narration"      
        from  public."receiptMasters_receiptMaster" AS RM      
        INNER JOIN public."receiptDetailses_receiptDetails" AS RD ON RD."ReceiptMasterID" = RM."ReceiptMasterID"   AND RD."CompanyID_id" = RM."CompanyID_id"   
        INNER JOIN public."accountLedger_accountLedger" AS AL ON AL."LedgerID" = RD."LedgerID" AND AL."CompanyID_id" = RM."CompanyID_id"      
        WHERE RM."VoucherType" IN %(VoucherType)s  AND RM."Date" between %(FromDate)s AND %(ToDate)s  AND RM."CompanyID_id" = %(CompanyID)s     
        order by "Date" DESC
        ''', dic)
    else:
        cursor.execute('''
            select RM."VoucherNo",RM."Date",      
            AL."LedgerName",round(RD."Amount",2) as Amount,round(RD."Discount",2) as Discount,round(RD."NetAmount",2) as NetAmount,
            CASE WHEN
            RM."VoucherType" = 'CR'  THEN 'Cash Receipt'   
            WHEN RM."VoucherType" = 'BR' THEN 'Bank Receipt'      
            END AS VoucherType, 
            RD."Narration"      
            from  public."receiptMasters_receiptMaster" AS RM      
            INNER JOIN public."receiptDetailses_receiptDetails" AS RD ON RD."ReceiptMasterID" = RM."ReceiptMasterID"   AND RD."CompanyID_id" = RM."CompanyID_id"   
            INNER JOIN public."accountLedger_accountLedger" AS AL ON AL."LedgerID" = RD."LedgerID" AND AL."CompanyID_id" = RM."CompanyID_id"      
            WHERE RD."LedgerID" in %(CashLedgers)s  AND RM."VoucherType" IN %(VoucherType)s  AND RM."Date" between %(FromDate)s AND %(ToDate)s  AND RM."CompanyID_id" = %(CompanyID)s     
            order by "Date" DESC
            ''', dic)

    data = cursor.fetchall()
    if cursor.rowcount == 0:
        data = [('', '', 'NO DATA', '', '', 0, 0, '')]

    df = pd.DataFrame(data)
    # adding Total in laast Row to data frame
    df.loc[str(_('Total'))] = df[[3, 4, 5]].sum().reindex(
        df.columns, fill_value='')

    # adding Heading to frame
    df.columns = [
        str(('VoucherNo')), str(('Date')), str(('LedgerName')), str(('Amount')), str(('Discount')), str(('NetAmount')), str(('VoucherType')), str(('Narration'))]
    # convert date format(millisecond) to str in dataframe
    df['Date'] = df['Date'].astype(str)

    json_records = df.reset_index().to_json(orient='records')
    details = json.loads(json_records)
    return df, details


def query_payment_report_data(CompanyID, BranchID, FromDate, ToDate, PriceRounding, CashLedgers, VoucherType):
    cursor = connection.cursor()
    VoucherTypes = ('CP', 'BP')
    if VoucherType == "CP":
        VoucherTypes = ('CP',)
    elif VoucherType == "BP":
        VoucherTypes = ('BP',)
    # CashLedgers = tuple(CashLedgers)
    dic = {'BranchID': BranchID, 'FromDate': FromDate, 'ToDate': ToDate,
           'CompanyID': CompanyID, "CashLedgers": CashLedgers, "VoucherType": VoucherTypes}
    print(CashLedgers,"************************")
    
    if CashLedgers == "0" or CashLedgers == 0:
        cursor.execute('''
            select PM."VoucherNo", PM."Date",     
            AL."LedgerName", round(PD."Amount",2) as Amount, round(PD."Discount",2) as Discount, round(PD."NetAmount",2) as NetAmount,
            CASE WHEN
            PM."VoucherType" = 'CP'  THEN 'Cash Payment'   
            WHEN PM."VoucherType" = 'BP' THEN 'Bank Payment'      
            END AS VoucherType, 
            PD."Narration"           
            from public."paymentMasters_paymentMaster" AS PM      
            INNER JOIN public."paymentDetails_paymentDetail" AS PD ON PD."PaymentMasterID" = PM."PaymentMasterID"    AND PD."CompanyID_id" = PM."CompanyID_id"     
            INNER JOIN public."accountLedger_accountLedger" AS AL ON AL."LedgerID" = PD."LedgerID" AND AL."CompanyID_id" = PM."CompanyID_id"           
            WHERE PM."VoucherType" IN %(VoucherType)s  AND PM."Date" between %(FromDate)s AND %(ToDate)s  AND PM."CompanyID_id" = %(CompanyID)s          
            order by "Date" DESC  
            ''', dic)
    else:
        cursor.execute('''
        select PM."VoucherNo", PM."Date",     
        AL."LedgerName", round(PD."Amount",2) as Amount, round(PD."Discount",2) as Discount, round(PD."NetAmount",2) as NetAmount,
        CASE WHEN
        PM."VoucherType" = 'CP'  THEN 'Cash Payment'   
        WHEN PM."VoucherType" = 'BP' THEN 'Bank Payment'      
        END AS VoucherType, 
        PD."Narration"           
        from public."paymentMasters_paymentMaster" AS PM      
        INNER JOIN public."paymentDetails_paymentDetail" AS PD ON PD."PaymentMasterID" = PM."PaymentMasterID"    AND PD."CompanyID_id" = PM."CompanyID_id"     
        INNER JOIN public."accountLedger_accountLedger" AS AL ON AL."LedgerID" = PD."LedgerID" AND AL."CompanyID_id" = PM."CompanyID_id"           
        WHERE PD."LedgerID" in %(CashLedgers)s AND PM."VoucherType" IN %(VoucherType)s  AND PM."Date" between %(FromDate)s AND %(ToDate)s  AND PM."CompanyID_id" = %(CompanyID)s          
        order by "Date" DESC  
        ''', dic)

    data = cursor.fetchall()
    if cursor.rowcount == 0:
        data = [('', '', 'NO DATA', '', '', 0, 0, '')]

    df = pd.DataFrame(data)

    # adding Total in laast Row to data frame
    df.loc[str(_('Total'))] = df[[3, 4, 5]].sum().reindex(
        df.columns, fill_value='')

    # adding Heading to frame
    df.columns = [
        str(('VoucherNo')), str(('Date')), str(('LedgerName')), str(('Amount')), str(('Discount')), str(('NetAmount')), str(('VoucherType')), str(('Narration'))]
    # convert date format(millisecond) to str in dataframe
    df['Date'] = df['Date'].astype(str)

    json_records = df.reset_index().to_json(orient='records')
    details = json.loads(json_records)
    return df, details


def query_sales_integrated_report_data(CompanyID, BranchID, FromDate, ToDate, UserID):
    if not str(UserID) == "0" and UserTable.objects.filter(CompanyID=CompanyID, id=UserID):
        UserID = UserTable.objects.get(
            CompanyID=CompanyID, id=UserID
        ).customer.user.id
    cursor = connection.cursor()
    # DAILY_DATEs = ['2022-02-16','2022-02-12']
    DAILY_DATEs = get_all_dates_bwn2dates(FromDate, ToDate)
    data = []
    for DAILY_DATE in DAILY_DATEs:
        dic = {'DAILY_DATE': DAILY_DATE.date(), 'BranchID': BranchID, 'FromDate': FromDate,
               'ToDate': ToDate, 'CompanyID': CompanyID, 'UserID': UserID}
        if str(UserID) == "0":
            cursor.execute('''
                select %(DAILY_DATE)s as Date, 
                (select round(coalesce(SUM("Debit") - SUM("Credit"),0),2) from public."ledgerPostings_ledgerPosting" where "VoucherType" = 'SI'
                AND "LedgerID" IN(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" = '9'
                AND "CompanyID_id" = %(CompanyID)s) AND "CompanyID_id" = %(CompanyID)s AND "Date" = %(DAILY_DATE)s )AS CashSale  
                ,(select round(coalesce(SUM("Debit") - SUM("Credit"),0),2) from public."ledgerPostings_ledgerPosting" where "VoucherType" = 'SI' 
                AND "LedgerID" IN(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" IN('10', '29', '69')
                AND "CompanyID_id" = %(CompanyID)s)AND "CompanyID_id" = %(CompanyID)s AND "Date" = %(DAILY_DATE)s)AS CreditSale 
                ,(select round(coalesce(SUM("Debit") - SUM("Credit"),0),2) from public."ledgerPostings_ledgerPosting" where "VoucherType" = 'SI'
                AND "LedgerID" IN(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" = '8'
                AND "CompanyID_id" = %(CompanyID)s) AND "CompanyID_id" = %(CompanyID)s AND "Date" = %(DAILY_DATE)s)AS BankSale    
                ,(select round(coalesce(SUM("Credit") - SUM("Debit"),0),2) from public."ledgerPostings_ledgerPosting" where "VoucherType" = 'SR'
                AND "LedgerID" IN(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" = '9' 
                AND "CompanyID_id" = %(CompanyID)s)AND "CompanyID_id" = %(CompanyID)s AND "Date" = %(DAILY_DATE)s)AS CashReturn    
                ,(select round(coalesce(SUM("Credit") - SUM("Debit"),0),2) from public."ledgerPostings_ledgerPosting" where "VoucherType" = 'SR'
                AND "LedgerID" IN(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" IN('10', '29', '69') 
                AND "CompanyID_id" = %(CompanyID)s)AND "CompanyID_id" = %(CompanyID)s AND "Date" = %(DAILY_DATE)s 
                )AS DebitReturn
                ,(select round(coalesce(SUM("Credit") - SUM("Debit"),0),2) from public."ledgerPostings_ledgerPosting" where "VoucherType" = 'SR'
                AND "LedgerID" IN(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" = '8'
                AND "CompanyID_id" = %(CompanyID)s)AND "CompanyID_id" = %(CompanyID)s AND "Date" = %(DAILY_DATE)s)AS BankReturn 
                ''', dic)
        else:
            cursor.execute('''
                select %(DAILY_DATE)s as Date, 
                (select round(coalesce(SUM("Debit") - SUM("Credit"),0),2) from public."ledgerPostings_ledgerPosting" AS L inner 
                join public."salesMasters_salesMaster" as S on L."VoucherMasterID" = S."SalesMasterID"  AND L."CompanyID_id" = S."CompanyID_id" where "VoucherType" = 'SI' AND  L."LedgerID" IN    
                (SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" = '9' AND "CompanyID_id" = L."CompanyID_id") AND L."Date" = %(DAILY_DATE)s and  S."CreatedUserID" =  %(UserID)s   
                    AND L."CompanyID_id" = %(CompanyID)s) AS CashSale ,

                (select round(coalesce(SUM("Debit") - SUM("Credit"),0),2) from public."ledgerPostings_ledgerPosting" AS L inner    
                    join public."salesMasters_salesMaster" as S on L."VoucherMasterID" = S."SalesMasterID" AND L."CompanyID_id" = S."CompanyID_id" where "VoucherType" = 'SI'  
                AND L."LedgerID" IN(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" = '8' AND "CompanyID_id" = L."CompanyID_id") AND L."Date" = %(DAILY_DATE)s and S."CreatedUserID" =  %(UserID)s     
                    AND L."CompanyID_id" = %(CompanyID)s) AS BankSale  

                ,(select round(coalesce(SUM("Debit") - SUM("Credit"),0),2) from public."ledgerPostings_ledgerPosting" AS L inner    
                    join public."salesMasters_salesMaster" as S on L."VoucherMasterID" = s."SalesMasterID" AND L."CompanyID_id" = S."CompanyID_id" where "VoucherType" = 'SI'
                AND L."LedgerID" IN(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" IN('10', '29', '69') AND "CompanyID_id" = L."CompanyID_id") AND L."Date" = %(DAILY_DATE)s and S."CreatedUserID"  =  %(UserID)s      
                AND L."CompanyID_id" = %(CompanyID)s)AS CreditSale

                ,(select round(coalesce(SUM("Credit") - SUM("Debit"),0),2) from public."ledgerPostings_ledgerPosting" as L inner   
                join public."salesReturnMasters_salesReturnMaster" as S on L."VoucherMasterID" = S."SalesReturnMasterID" AND L."CompanyID_id" = S."CompanyID_id" where "VoucherType" = 'SR'  
                AND L."LedgerID" IN(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" = '9' AND "CompanyID_id" = L."CompanyID_id") AND "Date" = %(DAILY_DATE)s and S."CreatedUserID"  =  %(UserID)s    
                AND L."CompanyID_id" = %(CompanyID)s)AS CashReturn 

                ,(select round(coalesce(SUM("Credit") - SUM("Debit"),0),2) from public."ledgerPostings_ledgerPosting" as L inner    
                    join public."salesReturnMasters_salesReturnMaster" as S on L."VoucherMasterID" = S."SalesReturnMasterID" AND L."CompanyID_id" = S."CompanyID_id" where "VoucherType" = 'SR'  
                AND L."LedgerID" IN(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" = '8' AND "CompanyID_id" = L."CompanyID_id") AND "Date" = %(DAILY_DATE)s and S."CreatedUserID"  =  %(UserID)s    
                AND L."CompanyID_id" = %(CompanyID)s)AS BankReturn  

                ,(select round(coalesce(SUM("Credit") - SUM("Debit"),0),2) from public."ledgerPostings_ledgerPosting" as L inner    
                join public."salesReturnMasters_salesReturnMaster" as S on L."VoucherMasterID" = S."SalesReturnMasterID" AND L."CompanyID_id" = S."CompanyID_id" where "VoucherType" = 'SR'
                AND L."LedgerID" IN(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" IN('10', '29', '69') AND "CompanyID_id" = L."CompanyID_id") AND "Date" = %(DAILY_DATE)s and S."CreatedUserID"  =  %(UserID)s    
                AND L."CompanyID_id" = %(CompanyID)s)AS DebitReturn  

                ''', dic)
        data_set = cursor.fetchall()
        if data_set:
            if converted_float(data_set[0][1]) != converted_float(0) or converted_float(data_set[0][2]) != converted_float(0) or converted_float(data_set[0][3]) != converted_float(0) or converted_float(data_set[0][4]) != converted_float(0) or converted_float(data_set[0][5]) != converted_float(0) or converted_float(data_set[0][6]) != converted_float(0):
                data.append(data_set[0])

    if cursor.rowcount == 0:
        data = [('', 0, 0, 0, 0, 0, 0)]

    df = pd.DataFrame(data)
    # a_series = (df != 0).any(axis=1)
    # new_df = df.loc[a_series]
    df.loc[str(_('Total'))] = df[[1, 2, 3, 4, 5, 6]
                                 ].sum().reindex(df.columns, fill_value='')
    df.columns = [
        str(('Date')), str(('CashSales')), str(('CreditSales')), str(('BankSales')), str(('CashReturn')), str(('DebitReturn')), str(_('BankReturn'))]

    sum_column = df["CashSales"] + df["CreditSales"] + df["BankSales"]
    df["NetSales"] = sum_column
    df.insert(4, 'NetSales', df.pop("NetSales"))
    sum_returncolumn = df["CashReturn"] + df["DebitReturn"] + df["BankReturn"]
    df["NetReturn"] = sum_returncolumn
    df.insert(8, 'NetReturn', df.pop("NetReturn"))
    sum_actualcolumn = df["NetSales"] - df["NetReturn"]
    df["ActualSales"] = sum_actualcolumn

    if not str(UserID) == "0":
        user_name = ""
        if User.objects.filter(id=UserID).exists():
            user_name = User.objects.get(id=UserID).username

        df["User"] = user_name
        df.insert(1, 'User', df.pop("User"))
    # adding Total in laast Row to data frame

    # adding Heading to frame

    # convert date format(millisecond) to str in dataframe
    df['Date'] = df['Date'].astype(str)

    json_records = df.reset_index().to_json(orient='records')
    
    details = json.loads(json_records)
    return df, details


def query_purchase_integrated_report_data(CompanyID, BranchID, FromDate, ToDate, UserID):
    if not str(UserID) == "0" and UserTable.objects.filter(CompanyID=CompanyID, id=UserID):
        UserID = UserTable.objects.get(
            CompanyID=CompanyID, id=UserID
        ).customer.user.id
    cursor = connection.cursor()
    # DAILY_DATEs = ['2022-02-16','2022-02-12']
    DAILY_DATEs = get_all_dates_bwn2dates(FromDate, ToDate)
    data = []
    for DAILY_DATE in DAILY_DATEs:
        dic = {'DAILY_DATE': DAILY_DATE.date(), 'BranchID': BranchID, 'FromDate': FromDate,
               'ToDate': ToDate, 'CompanyID': CompanyID, 'UserID': UserID}
        if str(UserID) == "0":
            cursor.execute('''
                select %(DAILY_DATE)s as Date, 
                (select round(coalesce(SUM("Credit") - SUM("Debit"),0),2) from public."ledgerPostings_ledgerPosting" where "VoucherType" = 'PI'
                AND "LedgerID" IN(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" = '9'
                AND "CompanyID_id" = %(CompanyID)s) AND "CompanyID_id" = %(CompanyID)s AND "Date" = %(DAILY_DATE)s )AS CashPurchase  
                ,(select round(coalesce(SUM("Credit") - SUM("Debit"),0),2) from public."ledgerPostings_ledgerPosting" where "VoucherType" = 'PI' 
                AND "LedgerID" IN(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" IN('10', '29', '69')
                AND "CompanyID_id" = %(CompanyID)s)AND "CompanyID_id" = %(CompanyID)s AND "Date" = %(DAILY_DATE)s)AS CreditPurchase 
                ,(select round(coalesce(SUM("Credit") - SUM("Debit"),0),2) from public."ledgerPostings_ledgerPosting" where "VoucherType" = 'PI'
                AND "LedgerID" IN(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" = '8'
                AND "CompanyID_id" = %(CompanyID)s) AND "CompanyID_id" = %(CompanyID)s AND "Date" = %(DAILY_DATE)s)AS BankPurchase    
                ,(select round(coalesce(SUM("Debit") - SUM("Credit"),0),2) from public."ledgerPostings_ledgerPosting" where "VoucherType" = 'PR'
                AND "LedgerID" IN(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" = '9' 
                AND "CompanyID_id" = %(CompanyID)s)AND "CompanyID_id" = %(CompanyID)s AND "Date" = %(DAILY_DATE)s)AS CashReturn    
                ,(select round(coalesce(SUM("Debit") - SUM("Credit"),0),2) from public."ledgerPostings_ledgerPosting" where "VoucherType" = 'PR'
                AND "LedgerID" IN(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" IN('10', '29', '69') 
                AND "CompanyID_id" = %(CompanyID)s)AND "CompanyID_id" = %(CompanyID)s AND "Date" = %(DAILY_DATE)s 
                )AS DebitReturn
                ,(select round(coalesce(SUM("Debit") - SUM("Credit"),0),2) from public."ledgerPostings_ledgerPosting" where "VoucherType" = 'PR'
                AND "LedgerID" IN(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" = '8'
                AND "CompanyID_id" = %(CompanyID)s)AND "CompanyID_id" = %(CompanyID)s AND "Date" = %(DAILY_DATE)s)AS BankReturn 
                ''', dic)
        else:
            cursor.execute('''
                select %(DAILY_DATE)s as Date, 
                (select round(coalesce(SUM("Credit") - SUM("Debit"),0),2) from public."ledgerPostings_ledgerPosting" AS L inner 
                join public."purchaseMasters_purchaseMaster" as S on L."VoucherMasterID" = S."PurchaseMasterID"  AND L."CompanyID_id" = S."CompanyID_id" where "VoucherType" = 'PI' AND  L."LedgerID" IN    
                (SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" = '9' AND "CompanyID_id" = L."CompanyID_id") AND L."Date" = %(DAILY_DATE)s and  S."CreatedUserID" =  %(UserID)s   
                    AND L."CompanyID_id" = %(CompanyID)s) AS CashPurchase ,

                (select round(coalesce(SUM("Credit") - SUM("Debit"),0),2) from public."ledgerPostings_ledgerPosting" AS L inner    
                    join public."purchaseMasters_purchaseMaster" as S on L."VoucherMasterID" = S."PurchaseMasterID" AND L."CompanyID_id" = S."CompanyID_id" where "VoucherType" = 'PI'  
                AND L."LedgerID" IN(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" = '8' AND "CompanyID_id" = L."CompanyID_id") AND L."Date" = %(DAILY_DATE)s and S."CreatedUserID" =  %(UserID)s     
                    AND L."CompanyID_id" = %(CompanyID)s) AS BankPurchase  

                ,(select round(coalesce(SUM("Credit") - SUM("Debit"),0),2) from public."ledgerPostings_ledgerPosting" AS L inner    
                    join public."purchaseMasters_purchaseMaster" as S on L."VoucherMasterID" = s."PurchaseMasterID" AND L."CompanyID_id" = S."CompanyID_id" where "VoucherType" = 'PI'
                AND L."LedgerID" IN(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" IN('10', '29', '69') AND "CompanyID_id" = L."CompanyID_id") AND L."Date" = %(DAILY_DATE)s and S."CreatedUserID"  =  %(UserID)s      
                AND L."CompanyID_id" = %(CompanyID)s)AS CreditPurchase

                ,(select round(coalesce(SUM("Debit") - SUM("Credit"),0),2) from public."ledgerPostings_ledgerPosting" as L inner   
                join public."purchaseReturnMasters_purchaseReturnMaster" as S on L."VoucherMasterID" = S."PurchaseReturnMasterID" AND L."CompanyID_id" = S."CompanyID_id" where "VoucherType" = 'PR'  
                AND L."LedgerID" IN(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" = '9' AND "CompanyID_id" = L."CompanyID_id") AND "Date" = %(DAILY_DATE)s and S."CreatedUserID"  =  %(UserID)s    
                AND L."CompanyID_id" = %(CompanyID)s)AS CashReturn 

                ,(select round(coalesce(SUM("Debit") - SUM("Credit"),0),2) from public."ledgerPostings_ledgerPosting" as L inner    
                    join public."purchaseReturnMasters_purchaseReturnMaster" as S on L."VoucherMasterID" = S."PurchaseReturnMasterID" AND L."CompanyID_id" = S."CompanyID_id" where "VoucherType" = 'PR'  
                AND L."LedgerID" IN(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" = '8' AND "CompanyID_id" = L."CompanyID_id") AND "Date" = %(DAILY_DATE)s and S."CreatedUserID"  =  %(UserID)s    
                AND L."CompanyID_id" = %(CompanyID)s)AS BankReturn  

                ,(select round(coalesce(SUM("Debit") - SUM("Credit"),0),2) from public."ledgerPostings_ledgerPosting" as L inner    
                join public."purchaseReturnMasters_purchaseReturnMaster" as S on L."VoucherMasterID" = S."PurchaseReturnMasterID" AND L."CompanyID_id" = S."CompanyID_id" where "VoucherType" = 'PR'
                AND L."LedgerID" IN(SELECT "LedgerID" FROM public."accountLedger_accountLedger" WHERE "AccountGroupUnder" IN('10', '29', '69') AND "CompanyID_id" = L."CompanyID_id") AND "Date" = %(DAILY_DATE)s and S."CreatedUserID"  =  %(UserID)s    
                AND L."CompanyID_id" = %(CompanyID)s)AS DebitReturn  

                ''', dic)
        data_set = cursor.fetchall()
        if data_set:
            if converted_float(data_set[0][1]) != converted_float(0) or converted_float(data_set[0][2]) != converted_float(0) or converted_float(data_set[0][3]) != converted_float(0) or converted_float(data_set[0][4]) != converted_float(0) or converted_float(data_set[0][5]) != converted_float(0) or converted_float(data_set[0][6]) != converted_float(0):
                data.append(data_set[0])
        

    if not data:
        data = [('', 0, 0, 0, 0, 0, 0)]

    df = pd.DataFrame(data)
    # a_series = (df != 0).any(axis=1)
    # new_df = df.loc[a_series]
    
    # df.loc[str(_('Total'))] = df[[1, 2, 3, 4, 5, 6]
    #                              ].sum().reindex(df.columns, fill_value='')
    df.columns = [
        str(('Date')), str(('CashPurchases')), str(('CreditPurchases')), str(('BankPurchases')), str(('CashReturn')), str(('DebitReturn')), str(_('BankReturn'))]

    sum_column = df["CashPurchases"] + df["CreditPurchases"] + df["BankPurchases"]
    df["NetPurchases"] = sum_column
    df.insert(4, 'NetPurchases', df.pop("NetPurchases"))
    sum_returncolumn = df["CashReturn"] + df["DebitReturn"] + df["BankReturn"]
    df["NetReturn"] = sum_returncolumn
    df.insert(8, 'NetReturn', df.pop("NetReturn"))
    sum_actualcolumn = df["NetPurchases"] - df["NetReturn"]
    df["ActualPurchases"] = sum_actualcolumn

    if not str(UserID) == "0":
        user_name = ""
        if User.objects.filter(id=UserID).exists():
            user_name = User.objects.get(id=UserID).username

        df["User"] = user_name
        df.insert(1, 'User', df.pop("User"))
    df.loc[str(_('Total'))] = df[["CashPurchases", "CreditPurchases", "BankPurchases", "CashReturn", "DebitReturn", "BankReturn","NetPurchases","NetReturn","ActualPurchases"]
                                 ].sum().reindex(df.columns, fill_value='')
    # adding Total in laast Row to data frame

    # adding Heading to frame

    # convert date format(millisecond) to str in dataframe
    df['Date'] = df['Date'].astype(str)

    json_records = df.reset_index().to_json(orient='records')
    
    details = json.loads(json_records)
    return df, details


def billwise_profit_report_data(CompanyID, BranchID, FromDate, ToDate, UserID, WareHouseID, CustomerID, RouteID):
    if not str(UserID) == "0" and UserTable.objects.filter(CompanyID=CompanyID, id=UserID):
        UserID = UserTable.objects.get(
            CompanyID=CompanyID, id=UserID
        ).customer.user.id
    if Parties.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PartyID=CustomerID).exists():
        CustomerID = Parties.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, PartyID=CustomerID).first().LedgerID
    cursor = connection.cursor()
    dic = {'CompanyID': CompanyID, 'BranchID': BranchID, 'FromDate': FromDate, 'ToDate': ToDate,
           "UserID": UserID, "WareHouseID": WareHouseID, "CustomerID": CustomerID, "RouteID": RouteID}

    if not int(UserID) == 0 and not int(WareHouseID) == 0 and not int(CustomerID) == 0:
        cursor.execute('''
             SELECT               
            A."Date",          
            "VoucherNo",       
            round("TotalGrossAmt",2) as GrossAmount,          
            round(A."TotalTax",2) as TotalTax ,        
            round("NetTotal",2)   as NetAmount,         
            (SELECT round(sum("CostPerPrice"*"Qty"),2) FROM public."salesDetails_salesDetail" as D WHERE D."SalesMasterID"=A."SalesMasterID" AND D."BranchID" = A."BranchID" AND D."CompanyID_id" = A."CompanyID_id")  as NetCost         
                    
            FROM public."salesMasters_salesMaster" as A     
            INNER JOIN public."accountLedger_accountLedger" AS AL ON A."LedgerID"=AL."LedgerID" AND AL."CompanyID_id" = A."CompanyID_id"        
                where A."BranchID"=%(BranchID)s and   "Date" BETWEEN %(FromDate)s AND %(ToDate)s AND A."CompanyID_id" = %(CompanyID)s 
            AND A."CreatedUserID" = %(UserID)s           
            AND A."WarehouseID" = %(WareHouseID)s           
            AND A."LedgerID" = %(CustomerID)s
        ''', dic)
    elif not int(UserID) == 0 and not int(WareHouseID) == 0 and not int(RouteID) == 0:
        cursor.execute('''
              SELECT               
                A."Date",          
                "VoucherNo",       
                round("TotalGrossAmt",2) as GrossAmount,          
                round(A."TotalTax",2) as TotalTax ,        
                round("NetTotal",2)   as NetAmount,        
                (SELECT round(sum("CostPerPrice"*"Qty"),2) FROM public."salesDetails_salesDetail" as D WHERE D."SalesMasterID"=A."SalesMasterID" AND D."BranchID" = A."BranchID" AND D."CompanyID_id" = A."CompanyID_id")  as NetCost         
                        
                FROM public."salesMasters_salesMaster" as A     
                INNER JOIN public."accountLedger_accountLedger" AS AL ON A."LedgerID"=AL."LedgerID"   AND AL."CompanyID_id" = A."CompanyID_id"          
                    where A."BranchID"=%(BranchID)s and   "Date" BETWEEN %(FromDate)s AND %(ToDate)s  AND A."CompanyID_id" = %(CompanyID)s  
                AND A."CreatedUserID" =  %(UserID)s
                AND A."WarehouseID" = %(WareHouseID)s
                AND A."LedgerID" in (SELECT "LedgerID" from public."parties_parties" as p where p."CompanyID_id" = A."CompanyID_id"
                And p."BranchID" = A."BranchID" AND p."RouteID" = %(RouteID)s) 
        ''', dic)
    elif not int(UserID) == 0 and not int(WareHouseID) == 0:
        cursor.execute('''
             SELECT               
            A."Date",          
            "VoucherNo",       
            round("TotalGrossAmt",2) as GrossAmount,          
            round(A."TotalTax",2) as TotalTax ,        
            round("NetTotal",2)   as NetAmount,         
            (SELECT round(sum("CostPerPrice"*"Qty"),2) FROM public."salesDetails_salesDetail" as D WHERE D."SalesMasterID"=A."SalesMasterID" AND D."BranchID" = A."BranchID" AND D."CompanyID_id" = A."CompanyID_id")  as NetCost         
                    
            FROM public."salesMasters_salesMaster" as A     
            INNER JOIN public."accountLedger_accountLedger" AS AL ON A."LedgerID"=AL."LedgerID" AND AL."CompanyID_id" = A."CompanyID_id"        
                where A."BranchID"=%(BranchID)s and   "Date" BETWEEN %(FromDate)s AND %(ToDate)s AND A."CompanyID_id" = %(CompanyID)s 
            AND A."WarehouseID" = %(WareHouseID)s          
            AND A."CreatedUserID" = %(UserID)s 
        ''', dic)
    elif not int(UserID) == 0 and not int(RouteID) == 0:
        cursor.execute('''
            SELECT               
            A."Date",          
            "VoucherNo",       
            round("TotalGrossAmt",2) as GrossAmount,          
            round(A."TotalTax",2) as TotalTax ,        
            round("NetTotal",2)   as NetAmount,         
            (SELECT round(sum("CostPerPrice"*"Qty"),2) FROM public."salesDetails_salesDetail" as D WHERE D."SalesMasterID"=A."SalesMasterID" AND D."BranchID" = A."BranchID" AND D."CompanyID_id" = A."CompanyID_id")  as NetCost         
                    
            FROM public."salesMasters_salesMaster" as A     
            INNER JOIN public."accountLedger_accountLedger" AS AL ON A."LedgerID"=AL."LedgerID"   AND AL."CompanyID_id" = A."CompanyID_id"          
                where A."BranchID"=%(BranchID)s and   "Date" BETWEEN %(FromDate)s AND %(ToDate)s  AND A."CompanyID_id" = %(CompanyID)s  
            AND A."CreatedUserID" = %(UserID)s
            AND A."LedgerID" in (SELECT "LedgerID" from public."parties_parties" as p where p."CompanyID_id" = A."CompanyID_id"
            And p."BranchID" = A."BranchID" AND p."RouteID" = %(RouteID)s) 
        ''', dic)
    elif not int(UserID) == 0 and not int(CustomerID) == 0:
        cursor.execute('''
            SELECT               
            A."Date",          
            "VoucherNo",       
            round("TotalGrossAmt",2) as GrossAmount,          
            round(A."TotalTax",2) as TotalTax ,        
            round("NetTotal",2)   as NetAmount,          
            (SELECT round(sum("CostPerPrice"*"Qty"),2) FROM public."salesDetails_salesDetail" as D WHERE D."SalesMasterID"=A."SalesMasterID" AND D."BranchID" = A."BranchID" AND D."CompanyID_id" = A."CompanyID_id")  as NetCost         
                    
            FROM public."salesMasters_salesMaster" as A     
            INNER JOIN public."accountLedger_accountLedger" AS AL ON A."LedgerID"=AL."LedgerID"   AND AL."CompanyID_id" = A."CompanyID_id"          
                where A."BranchID"=%(BranchID)s and   "Date" BETWEEN %(FromDate)s AND %(ToDate)s  AND A."CompanyID_id" = %(CompanyID)s  
            AND A."CreatedUserID" = %(UserID)s
            AND A."LedgerID" = %(CustomerID)s   
        ''', dic)
    elif not int(WareHouseID) == 0 and not int(RouteID) == 0:
        cursor.execute('''
            SELECT               
            A."Date",          
            "VoucherNo",       
            round("TotalGrossAmt",2) as GrossAmount,          
            round(A."TotalTax",2) as TotalTax ,        
            round("NetTotal",2)   as NetAmount,         
            (SELECT round(sum("CostPerPrice"*"Qty"),2) FROM public."salesDetails_salesDetail" as D WHERE D."SalesMasterID"=A."SalesMasterID" AND D."BranchID" = A."BranchID" AND D."CompanyID_id" = A."CompanyID_id")  as NetCost         
                    
            FROM public."salesMasters_salesMaster" as A     
            INNER JOIN public."accountLedger_accountLedger" AS AL ON A."LedgerID"=AL."LedgerID"   AND AL."CompanyID_id" = A."CompanyID_id"          
                where A."BranchID"=%(BranchID)s and   "Date" BETWEEN  %(FromDate)s AND %(ToDate)s  AND A."CompanyID_id" = %(CompanyID)s  
            AND A."WarehouseID" = %(WareHouseID)s
            AND A."LedgerID" in (SELECT "LedgerID" from public."parties_parties" as p where p."CompanyID_id" = A."CompanyID_id"
            And p."BranchID" = A."BranchID" AND p."RouteID" = %(RouteID)s)
        ''', dic)
    elif not int(WareHouseID) == 0 and not int(CustomerID) == 0:
        cursor.execute('''
            SELECT               
            A."Date",          
            "VoucherNo",       
            round("TotalGrossAmt",2) as GrossAmount,          
            round(A."TotalTax",2) as TotalTax ,        
            round("NetTotal",2)   as NetAmount,          
            (SELECT round(sum("CostPerPrice"*"Qty"),2) FROM public."salesDetails_salesDetail" as D WHERE D."SalesMasterID"=A."SalesMasterID" AND D."BranchID" = A."BranchID" AND D."CompanyID_id" = A."CompanyID_id")  as NetCost         
                    
            FROM public."salesMasters_salesMaster" as A     
            INNER JOIN public."accountLedger_accountLedger" AS AL ON A."LedgerID"=AL."LedgerID" AND AL."CompanyID_id" = A."CompanyID_id"        
                where A."BranchID"=%(BranchID)s and   "Date" BETWEEN %(FromDate)s AND %(ToDate)s AND A."CompanyID_id" = %(CompanyID)s 
            AND A."WarehouseID" = %(WareHouseID)s          
            AND A."LedgerID" = %(CustomerID)s 
        ''', dic)
    elif not int(UserID) == 0:
        cursor.execute('''
            SELECT               
            A."Date",          
            "VoucherNo",       
            round("TotalGrossAmt",2) as GrossAmount,          
            round(A."TotalTax",2) as TotalTax ,        
            round("NetTotal",2)   as NetAmount,         
            (SELECT round(sum("CostPerPrice"*"Qty"),2) FROM public."salesDetails_salesDetail" as D WHERE D."SalesMasterID"=A."SalesMasterID" AND D."BranchID" = A."BranchID" AND D."CompanyID_id" = A."CompanyID_id")  as NetCost         
                    
            FROM public."salesMasters_salesMaster" as A     
            INNER JOIN public."accountLedger_accountLedger" AS AL ON A."LedgerID"=AL."LedgerID" AND AL."CompanyID_id" = A."CompanyID_id"         
                where A."BranchID"=%(BranchID)s and   "Date" BETWEEN %(FromDate)s AND %(ToDate)s AND A."CompanyID_id" =  %(CompanyID)s 

            AND A."CreatedUserID" = %(UserID)s 
        ''', dic)
    elif not int(WareHouseID) == 0:
        cursor.execute('''
            SELECT               
            A."Date",          
            "VoucherNo",       
            round("TotalGrossAmt",2) as GrossAmount,          
            round(A."TotalTax",2) as TotalTax ,        
            round("NetTotal",2)   as NetAmount,         
            (SELECT round(sum("CostPerPrice"*"Qty"),2) FROM public."salesDetails_salesDetail" as D WHERE D."SalesMasterID"=A."SalesMasterID" AND D."BranchID" = A."BranchID" AND D."CompanyID_id" = A."CompanyID_id")  as NetCost         
                    
            FROM public."salesMasters_salesMaster" as A     
            INNER JOIN public."accountLedger_accountLedger" AS AL ON A."LedgerID"=AL."LedgerID" AND AL."CompanyID_id" = A."CompanyID_id"        
                where A."BranchID"=%(BranchID)s and   "Date" BETWEEN %(FromDate)s AND %(ToDate)s AND A."CompanyID_id" = %(CompanyID)s  
            AND A."WarehouseID" =%(WareHouseID)s 
        ''', dic)
    elif not int(CustomerID) == 0:
        cursor.execute('''
            SELECT               
            A."Date",          
            "VoucherNo",       
            round("TotalGrossAmt",2) as GrossAmount,          
            round(A."TotalTax",2) as TotalTax ,        
            round("NetTotal",2)   as NetAmount,         
            (SELECT round(sum("CostPerPrice"*"Qty"),2) FROM public."salesDetails_salesDetail" as D WHERE D."SalesMasterID"=A."SalesMasterID" AND D."BranchID" = A."BranchID" AND D."CompanyID_id" = A."CompanyID_id")  as NetCost         
                    
            FROM public."salesMasters_salesMaster" as A     
            INNER JOIN public."accountLedger_accountLedger" AS AL ON A."LedgerID"=AL."LedgerID" AND AL."CompanyID_id" = A."CompanyID_id"         
                where A."BranchID"=%(BranchID)s and   "Date" BETWEEN %(FromDate)s AND %(ToDate)s AND A."CompanyID_id" = %(CompanyID)s    
            AND A."LedgerID" = %(CustomerID)s
        ''', dic)
    elif not int(RouteID) == 0:
        cursor.execute('''
            SELECT               
            A."Date",          
            "VoucherNo",       
            round("TotalGrossAmt",2) as GrossAmount,          
            round(A."TotalTax",2) as TotalTax ,        
            round("NetTotal",2)   as NetAmount,          
            (SELECT round(sum("CostPerPrice"*"Qty"),2) FROM public."salesDetails_salesDetail" as D WHERE D."SalesMasterID"=A."SalesMasterID" AND D."BranchID" = A."BranchID" AND D."CompanyID_id" = A."CompanyID_id")  as NetCost         
                    
            FROM public."salesMasters_salesMaster" as A     
            INNER JOIN public."accountLedger_accountLedger" AS AL ON A."LedgerID"=AL."LedgerID" AND AL."CompanyID_id" = A."CompanyID_id"         
                where A."BranchID"='1' and   "Date" BETWEEN %(FromDate)s AND %(ToDate)s AND A."CompanyID_id" = %(CompanyID)s    
            AND A."LedgerID" in (SELECT "LedgerID" from public."parties_parties" as p where p."CompanyID_id" = A."CompanyID_id"
            And p."BranchID" = A."BranchID" AND p."RouteID" = %(RouteID)s)  
        ''', dic)
    else:
        cursor.execute('''
            SELECT               
            A."Date",          
            "VoucherNo",       
            round("TotalGrossAmt",2) as GrossAmount,          
            round(A."TotalTax",2) as TotalTax ,        
            round("NetTotal",2)   as NetAmount,      
            (SELECT round(sum("CostPerPrice"*"Qty"),2) FROM public."salesDetails_salesDetail" as D WHERE D."SalesMasterID"=A."SalesMasterID" AND D."BranchID" = A."BranchID" AND D."CompanyID_id" = A."CompanyID_id")  as NetCost         
                    
            FROM public."salesMasters_salesMaster" as A     
            INNER JOIN public."accountLedger_accountLedger" AS AL ON A."LedgerID"=AL."LedgerID" AND AL."CompanyID_id" = A."CompanyID_id"         
                where A."BranchID"=%(BranchID)s and   "Date" BETWEEN %(FromDate)s AND %(ToDate)s AND A."CompanyID_id" = %(CompanyID)s
            ''', dic)

    data = cursor.fetchall()
    if cursor.rowcount == 0:
        data = [('', '', 0, 0, 0, 0)]

    df = pd.DataFrame(data)

    # adding Total in laast Row to data frame
    # adding Heading to frame
    df.columns = [
        str(('Date')), str(('InvoiceNo')), str(('GrossAmount')), str(('TotalTax')), str(('NetAmount')), str(('NetCost'))]

    profit_column = df["GrossAmount"] - df["NetCost"]
    df["Profit"] = profit_column
    df.insert(6, 'Profit', df.pop("Profit"))
    df.loc[str(_('Total'))] = df[['GrossAmount', 'TotalTax', 'Profit',
                                  'NetAmount', 'NetCost']].sum().reindex(df.columns, fill_value='')
    # convert date format(millisecond) to str in dataframe
    df['Date'] = df['Date'].astype(str)

    json_records = df.reset_index().to_json(orient='records')
    details = json.loads(json_records)
    return df, details


def supplierVsproduct_report_data(CompanyID, BranchID, FromDate, ToDate, PartyID, ProductID, filterValue):
    if Parties.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PartyID=PartyID).exists():
        PartyID = Parties.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, PartyID=PartyID).first().LedgerID
    cursor = connection.cursor()
    dic = {'CompanyID': CompanyID, 'BranchID': BranchID, 'FromDate': FromDate,
           'ToDate': ToDate, "PartyID": PartyID, "ProductID": ProductID, "filterValue": filterValue}

    if int(filterValue) == 1 and int(PartyID) > 0:
        cursor.execute('''
            SELECT  
            P."ProductName",
            (SELECT  round("UnitPrice",2) FROM public."purchaseDetailses_purchaseDetails"  WHERE "BranchID" = %(BranchID)s  
            AND "ProductID" = SP."ProductID" AND "CompanyID_id" = SP."CompanyID_id"    ORDER BY "PurchaseDetailsID" DESC LIMIT 1 ) AS LastPurchasePrice,
            
            (SELECT  coalesce(round("Qty",2),0)  FROM public."purchaseDetailses_purchaseDetails"  WHERE "BranchID" = %(BranchID)s  
            AND "ProductID" = SP."ProductID" AND "CompanyID_id" = SP."CompanyID_id"  ORDER BY "PurchaseDetailsID" DESC LIMIT 1 ) as LastPurchaseQty ,
            
            (SELECT coalesce(round(SUM("QtyOut"),2),0) FROM public."stockPosting_stockPosting" WHERE  
            "VoucherType" = 'SI' AND "BranchID" = %(BranchID)s  
            AND "Date" BETWEEN %(FromDate)s AND %(ToDate)s  AND "ProductID" = SP."ProductID" 
            AND "CompanyID_id" = SP."CompanyID_id" 
            ) AS TotalSales ,
            
            
            (SELECT coalesce(round(SUM("GrossAmount"),2),0) FROM public."salesDetails_salesDetail" as sd 
            INNER JOIN public."salesMasters_salesMaster" AS sm ON sm."SalesMasterID"=sd."SalesMasterID" AND sm."CompanyID_id" = sd."CompanyID_id" 
            AND   sm."Date" BETWEEN %(FromDate)s AND %(ToDate)s 
            WHERE  sd."BranchID" = %(BranchID)s   AND sd."ProductID" = SP."ProductID" 
            AND sd."CompanyID_id" = SP."CompanyID_id") AS TotalSalesAmount ,
            
                
            coalesce(round(SUM(SP."QtyIn"),2),0) AS TotalPurchase,  
            coalesce(round((SUM(SP."QtyIn") * SUM(SP."Rate")),2),0) AS TotalPurchaseAmount, 
            coalesce(round((SUM(SP."QtyIn") * SUM(SP."Rate") / (SUM(SP."QtyIn"))),2),0) AS AvgPurchaseRate, 
                 
                ( SELECT coalesce(round(SUM("QtyIn"),2),0) FROM public."stockPosting_stockPosting" WHERE  
            "VoucherType" = 'SR' AND "BranchID" = %(BranchID)s  
            AND "Date" BETWEEN %(FromDate)s AND %(ToDate)s  AND "ProductID" = SP."ProductID" 
            AND "CompanyID_id" = SP."CompanyID_id" 
            ) AS TotalSalesReturn,
            
            (SELECT coalesce(round(SUM("GrossAmount"),2),0) FROM public."salesReturnDetails_salesReturnDetail" as srd 
            INNER JOIN public."salesReturnMasters_salesReturnMaster" AS srm ON srm."SalesReturnMasterID"=srd."SalesReturnMasterID" AND srm."CompanyID_id" = srd."CompanyID_id" 
            AND   srm."VoucherDate" BETWEEN %(FromDate)s AND %(ToDate)s 
            WHERE  srd."BranchID" = %(BranchID)s   AND srd."ProductID" = SP."ProductID" 
            AND srd."CompanyID_id" = SP."CompanyID_id") AS TotalSalesReturnAmount, 
     

            ( SELECT coalesce(round(SUM("QtyOut"),2),0) FROM public."stockPosting_stockPosting" WHERE  
            "VoucherType" = 'PR' AND "BranchID" = %(BranchID)s  
            AND "Date" BETWEEN %(FromDate)s AND %(ToDate)s  AND "ProductID" = SP."ProductID" 
            AND "CompanyID_id" = SP."CompanyID_id" 
            ) AS TotalPurchaseReturn  
            
            ,( SELECT coalesce(round((SUM("QtyOut") * SUM("Rate")),2),0) FROM public."stockPosting_stockPosting" WHERE  
            "VoucherType" = 'PR' AND "BranchID" = %(BranchID)s  
            AND "Date" BETWEEN %(FromDate)s AND %(ToDate)s  AND "ProductID" = SP."ProductID"  
            AND "CompanyID_id" = SP."CompanyID_id"
            ) AS TotalPurchaseReturnAmount  
            
            ,( SELECT coalesce(round(SUM("Rate") / (SUM("QtyOut")),2),0) FROM public."stockPosting_stockPosting" WHERE  
            "VoucherType" = 'PR' AND "BranchID" = %(BranchID)s  
            AND "Date" BETWEEN %(FromDate)s AND %(ToDate)s  AND "ProductID" = SP."ProductID" 
            AND "CompanyID_id" = SP."CompanyID_id" 
            ) AS AvgPurchaseReturnRate  

            ,( SELECT coalesce(round(SUM("QtyIn") - SUM("QtyOut"),2),0) FROM public."stockPosting_stockPosting" WHERE  
            "BranchID" = %(BranchID)s 
            AND "ProductID" = SP."ProductID"  
            AND "CompanyID_id" = SP."CompanyID_id"
            ) AS CurrentStock ,

            (SELECT "UnitName" FROM public."units_unit" WHERE  
            "UnitID" = PL."UnitID" AND "BranchID" = %(BranchID)s AND "CompanyID_id" = SP."CompanyID_id") AS Unit 

            From public."stockPosting_stockPosting" AS SP  
            INNER JOIN public."products_product" AS P ON P."ProductID" = SP."ProductID" AND P."CompanyID_id" = SP."CompanyID_id" 
            INNER JOIN public."pricelist_pricelist" AS PL ON PL."PriceListID" = SP."PriceListID"  AND PL."CompanyID_id" = SP."CompanyID_id"
            INNER JOIN public."purchaseMasters_purchaseMaster" AS PM ON PM."PurchaseMasterID" = SP."VoucherMasterID"  AND PM."CompanyID_id" = SP."CompanyID_id"
            INNER JOIN public."accountLedger_accountLedger" AS AL ON PM."LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = SP."CompanyID_id" 
            WHERE AL."AccountGroupUnder" = '29' AND SP."VoucherType" = 'PI' AND SP."BranchID" = %(BranchID)s  AND PM."LedgerID" = %(PartyID)s  
            AND SP."Date" BETWEEN %(FromDate)s AND %(ToDate)s  AND SP."CompanyID_id" = %(CompanyID)s
            GROUP BY SP."ProductID",              
            P."ProductName",             
            PL."UnitID",        
            P."ProductCode",        
            PM."LedgerID",              
            AL."LedgerName"  ,       
            P."ProductID",      
            SP."Date",      
            SP."BranchID",  
            SP."CompanyID_id" 


        ''', dic)

    if int(filterValue) == 2 and int(ProductID) > 0:
        cursor.execute('''
            SELECT DISTINCT  
            AL."LedgerName" AS Supplier ,
            (SELECT  round("UnitPrice",2) FROM public."purchaseDetailses_purchaseDetails"  WHERE "BranchID" = %(BranchID)s  
            AND "ProductID" = SP."ProductID" AND "CompanyID_id" = SP."CompanyID_id"    ORDER BY "PurchaseDetailsID" DESC LIMIT 1 ) AS LastPurchasePrice, 
            (SELECT  coalesce(round("Qty",2),0)  FROM public."purchaseDetailses_purchaseDetails"  WHERE "BranchID" = %(BranchID)s  
            AND "ProductID" = SP."ProductID" AND "CompanyID_id" = SP."CompanyID_id"  ORDER BY "PurchaseDetailsID" DESC LIMIT 1 ) as LastPurchaseQty

            ,( SELECT coalesce(round(SUM("QtyOut"),2),0) FROM public."stockPosting_stockPosting" WHERE  
            "VoucherType" = 'SI' AND "BranchID" = %(BranchID)s  
            AND "Date" BETWEEN %(FromDate)s AND %(ToDate)s  AND "ProductID" = SP."ProductID" 
            AND "CompanyID_id" = SP."CompanyID_id"  
            ) AS TotalSales , 
            
            (SELECT coalesce(round(SUM("GrossAmount"),2),0) FROM public."salesDetails_salesDetail" as sd 
            INNER JOIN public."salesMasters_salesMaster" AS sm ON sm."SalesMasterID"=sd."SalesMasterID" AND sm."CompanyID_id" = sd."CompanyID_id" 
            AND   sm."Date" BETWEEN %(FromDate)s AND %(ToDate)s 
            WHERE  sd."BranchID" = %(BranchID)s   AND sd."ProductID" = SP."ProductID" 
            AND sd."CompanyID_id" = SP."CompanyID_id") AS TotalSalesAmount ,

                    
            (SELECT coalesce(round(SUM("QtyIn"),2),0) FROM public."stockPosting_stockPosting" WHERE  
            "VoucherType" = 'PI' AND "BranchID" = %(BranchID)s  
            AND "Date" BETWEEN %(FromDate)s AND %(ToDate)s  AND "ProductID" = SP."ProductID"
            AND "CompanyID_id" = SP."CompanyID_id" 
            ) AS TotalPurchase  
            
            ,(SELECT coalesce(round((SUM("QtyIn") * SUM("Rate")),2),0) FROM public."stockPosting_stockPosting" WHERE  
            "VoucherType" = 'PI' AND "BranchID" = %(BranchID)s  
            AND "Date" BETWEEN %(FromDate)s AND %(ToDate)s  AND "ProductID" = SP."ProductID"  
            AND "CompanyID_id" = SP."CompanyID_id" 
            ) AS TotalPurchaseAmount  
            
            ,(SELECT coalesce(round(SUM("Rate") / (SUM("QtyIn")),2),0) FROM public."stockPosting_stockPosting" WHERE  
            "VoucherType" = 'PI' AND "BranchID" = %(BranchID)s  
            AND "Date" BETWEEN %(FromDate)s AND %(ToDate)s  AND "ProductID" = SP."ProductID"  
            AND "CompanyID_id" = SP."CompanyID_id" 
            ) AS AvgPurchaseRate  
            
            

            
            ,( SELECT coalesce(round(SUM("QtyIn"),2),0) FROM public."stockPosting_stockPosting" WHERE  
            "VoucherType" = 'SR' AND "BranchID" = %(BranchID)s  
            AND "Date" BETWEEN %(FromDate)s AND %(ToDate)s  AND "ProductID" = SP."ProductID" 
            AND "CompanyID_id" = SP."CompanyID_id"  
            ) AS TotalSalesReturn  
            
            ,( SELECT coalesce(round((SUM("QtyIn") * SUM("Rate")),2),0) FROM public."stockPosting_stockPosting" WHERE  
            "VoucherType" = 'SR' AND "BranchID" = %(BranchID)s  
            AND "Date" BETWEEN %(FromDate)s AND %(ToDate)s  AND "ProductID" = SP."ProductID"  
            AND "CompanyID_id" = SP."CompanyID_id" 
            ) AS TotalSalesReturnAmount  
            
            
            ,( SELECT coalesce(round(SUM("QtyOut"),2),0) FROM public."stockPosting_stockPosting" WHERE  
            "VoucherType" = 'PR' AND "BranchID" = %(BranchID)s  
            AND "Date" BETWEEN %(FromDate)s AND %(ToDate)s  AND "ProductID" = SP."ProductID"
            AND "CompanyID_id" = SP."CompanyID_id"   
            ) AS TotalPurchaseReturn  
            
            ,( SELECT coalesce(round((SUM("QtyOut") * SUM("Rate")),2),0) FROM public."stockPosting_stockPosting" WHERE  
            "VoucherType" = 'PR' AND "BranchID" = %(BranchID)s  
            AND "Date" BETWEEN %(FromDate)s AND %(ToDate)s  AND "ProductID" = SP."ProductID" 
            AND "CompanyID_id" = SP."CompanyID_id"  
            ) AS TotalPurchaseReturnAmount  
            
            ,( SELECT coalesce(round(SUM("Rate") / (SUM("QtyOut")),2),0) FROM public."stockPosting_stockPosting" WHERE  
            "VoucherType" = 'PR' AND "BranchID" = %(BranchID)s  
            AND "Date" BETWEEN %(FromDate)s AND %(ToDate)s  AND "ProductID" = SP."ProductID" 
            AND "CompanyID_id" = SP."CompanyID_id"  
            ) AS AvgPurchaseReturnRate  
            
            ,( SELECT coalesce(round(SUM("QtyIn") - SUM("QtyOut"),2),0) FROM public."stockPosting_stockPosting" WHERE  
            "BranchID" = %(BranchID)s  
            AND "Date" BETWEEN %(FromDate)s AND %(ToDate)s  AND "ProductID" = SP."ProductID" 
            AND "CompanyID_id" = SP."CompanyID_id"  
            ) AS CurrentStock  ,

            (SELECT "UnitName" FROM public."units_unit" WHERE  
            "UnitID" = PL."UnitID" AND "BranchID" = %(BranchID)s AND "CompanyID_id" = SP."CompanyID_id") AS Unit
                
            
            
            
            
            From public."stockPosting_stockPosting" AS SP  
            INNER JOIN public."products_product" AS P ON P."ProductID" = SP."ProductID"   AND P."CompanyID_id" = SP."CompanyID_id" 
            INNER JOIN public."pricelist_pricelist" AS PL ON PL."PriceListID" = SP."PriceListID"   AND PL."CompanyID_id" = SP."CompanyID_id"
            INNER JOIN public."purchaseMasters_purchaseMaster" AS PM ON PM."PurchaseMasterID" = SP."VoucherMasterID"  AND PM."CompanyID_id" = SP."CompanyID_id"
            INNER JOIN public."accountLedger_accountLedger" AS AL ON PM."LedgerID" = AL."LedgerID"  AND AL."CompanyID_id" = SP."CompanyID_id" 
            
            
            WHERE AL."AccountGroupUnder" = '29'  AND SP."BranchID" = %(BranchID)s  AND SP."ProductID" = %(ProductID)s  
            AND SP."Date" BETWEEN %(FromDate)s AND %(ToDate)s  AND SP."CompanyID_id" = %(CompanyID)s

            ''', dic)
    data = cursor.fetchall()
    if cursor.rowcount == 0:
        data = [('', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "")]

    df = pd.DataFrame(data)
    # if filterValue == 1:
    heads = [
        str(_('ProductName')), str(_('LastPurchasePrice')), str(
            _('LastPurchaseQty')), str(_('TotalSales')), str(_('TotalSalesAmount')),
        str(_('TotalPurchase')), str(_('TotalPurchaseAmount')), str(
            _('AvgPurchaseRate')), str(_('TotalSalesReturn')), str(_('TotalSalesReturnAmount')),
        str(_('TotalPurchaseReturn')), str(_('TotalPurchaseReturnAmount')), str(_('AvgPurchaseReturnRate')), str(_('CurrentStock')), str(_('Unit'))]

    if int(filterValue) == 2:
        heads.pop(0)
        heads.insert(0, str(_('Supplier')))

    df.columns = heads
    df['TotalSalesAmount'] = df['TotalSalesAmount'].astype(float)
    df['TotalSales'] = df['TotalSales'].astype(float)
    avgSales_column = df["TotalSalesAmount"] / df["TotalSales"]

    df["AvgSalesRate"] = avgSales_column
    df.insert(5, 'AvgSalesRate', df.pop("AvgSalesRate"))

    df['TotalSalesReturnAmount'] = df['TotalSalesReturnAmount'].astype(float)
    df['TotalSalesReturn'] = df['TotalSalesReturn'].astype(float)
    avgSalesRetn_column = df["TotalSalesReturnAmount"] / df["TotalSalesReturn"]
    df["AvgSalesReturnRate"] = avgSalesRetn_column
    df.insert(11, 'AvgSalesReturnRate', df.pop("AvgSalesReturnRate"))
    df.loc[str(_('Total'))] = df[['LastPurchasePrice', 'LastPurchaseQty', 'TotalSales', 'TotalSalesAmount', 'AvgSalesRate', 'TotalPurchase', 'TotalPurchaseAmount', 'AvgPurchaseRate',
                                  'TotalSalesReturn', 'TotalSalesReturnAmount', 'AvgSalesReturnRate', 'TotalPurchaseReturn', 'TotalPurchaseReturnAmount', 'AvgPurchaseReturnRate', 'CurrentStock']].sum().reindex(df.columns, fill_value='')

    # convert date format(millisecond) to str in dataframe
    # df['Date']=df['Date'].astype(str)

    json_records = df.reset_index().to_json(orient='records')
    details = json.loads(json_records)
    return df, details


def opening_stock_report_data(CompanyID, BranchID, FromDate, ToDate, PriceRounding, WarehouseID):
    cursor = connection.cursor()
    WarehouseID = tuple(WarehouseID)
    dic = {'WarehouseID': WarehouseID, 'BranchID': BranchID,
           'FromDate': FromDate, 'ToDate': ToDate, 'CompanyID': CompanyID}
    if not len(WarehouseID) == 0:
        cursor.execute('''
            SELECT "VoucherNo",W."WarehouseName",OS."Notes",
            round("TotalQty",2),round("GrandTotal",2),U."username"  
            FROM public."openingStockMasters_openingStockMaster" AS OS  
            INNER JOIN public."warehouse_warehouse" AS W ON W."WarehouseID" = OS."WarehouseID"  AND 
            W."CompanyID_id" = OS."CompanyID_id"
            INNER JOIN public."auth_user" AS U ON U."id" = OS."CreatedUserID"  
            WHERE OS."BranchID" = %(BranchID)s AND "Date" BETWEEN %(FromDate)s AND %(ToDate)s  
            AND OS."WarehouseID" IN %(WarehouseID)s AND OS."CompanyID_id" = %(CompanyID)s  
            ''', dic)
    else:
        cursor.execute('''
            SELECT "VoucherNo",W."WarehouseName",OS."Notes",
            round("TotalQty",2),round("GrandTotal",2),U."username"  
            FROM public."openingStockMasters_openingStockMaster" AS OS  
            INNER JOIN public."warehouse_warehouse" AS W ON W."WarehouseID" = OS."WarehouseID" AND 
            W."CompanyID_id" = OS."CompanyID_id" 
            INNER JOIN public."auth_user" AS U ON U."id" = OS."CreatedUserID"  
            WHERE OS."BranchID" = %(BranchID)s AND "Date" BETWEEN %(FromDate)s AND %(ToDate)s 
            AND OS."CompanyID_id" = %(CompanyID)s 
            ''', dic)

    data = cursor.fetchall()
    if cursor.rowcount == 0:
        data = [('', '', '', 0, 0, '')]

    df = pd.DataFrame(data)

    # adding Total in laast Row to data frame
    df.loc[str(_('Total'))] = df[[3, 4]].sum().reindex(
        df.columns, fill_value='')

    # adding Heading to frame
    df.columns = [
        str(_('VoucherNo')), str(_('Warehouse')), str(_('Notes')), str(_('TotalQty')), str(_('GrandTotal')), str(_('User'))]
    # convert date format(millisecond) to str in dataframe

    json_records = df.reset_index().to_json(orient='records')
    details = json.loads(json_records)
    return df, details


def purchase_order_report_data(CompanyID, BranchID, FromDate, ToDate, ReportTypes):
    cursor = connection.cursor()
    ReportTypes = tuple(ReportTypes)

    dic = {'ReportTypes': ReportTypes, 'BranchID': BranchID,
           'FromDate': FromDate, 'ToDate': ToDate, 'CompanyID': CompanyID}
    if not len(ReportTypes) == 0:
        cursor.execute('''
            Select      
            P."VoucherNo" AS VoucherNo,      
            P."Date" AS VoucherDate,      
            AL."LedgerName" AS LedgerName,   
            (SELECT "LedgerName" FROM public."accountLedger_accountLedger" WHERE  
            "LedgerID" = P."LedgerID" AND "AccountGroupUnder" in ('10','29') AND "BranchID" = P."BranchID" AND "CompanyID_id" = P."CompanyID_id") AS SupplierName,   
            round(P."NetTotal",2) AS NetAmount,      
            round(P."TotalTax",2) AS TotalTax,        
            round(P."GrandTotal",2) AS GrandTotal ,
            case 
            when P."IsInvoiced" = 'N'then 'Pending'
            when  P."IsInvoiced" = 'I' then 'Invoiced'
            when P."IsInvoiced" = 'C' then 'Cancelled'
            end AS Status      
            FROM public."purchaseOrderMasters_purchaseOrderMaster" AS P       
            INNER JOIN public."accountLedger_accountLedger" AS AL ON P."LedgerID" = AL."LedgerID"
            AND AL."CompanyID_id" = P."CompanyID_id"      
            WHERE P."BranchID" = %(BranchID)s AND P."IsActive" = 'true' AND "IsInvoiced" in %(ReportTypes)s AND P."Date" BETWEEN %(FromDate)s AND %(ToDate)s  
            AND P."CompanyID_id" = %(CompanyID)s     
            ORDER BY "PurchaseOrderMasterID" 
            ''', dic)

        data = cursor.fetchall()
        if cursor.rowcount == 0:
            data = [('', '', '', '', 0, 0, 0, "")]
    else:
        data = [('', '', '', '', 0, 0, 0, "")]

    df = pd.DataFrame(data)

    # adding Total in laast Row to data frame
    df.loc[str(_('Total'))] = df[[4, 5, 6]].sum().reindex(
        df.columns, fill_value='')

    # adding Heading to frame
    df.columns = [
        str(_('VoucherNo')), str(_('VoucherDate')), str(_('LedgerName')), str(_('SupplierName')), str(_('NetAmount')), str(_('TotalTax')), str(_('GrandTotal')), str(_('Status'))]
    # convert date format(millisecond) to str in dataframe
    df['VoucherDate'] = df['VoucherDate'].astype(str)

    json_records = df.reset_index().to_json(orient='records')
    details = json.loads(json_records)
    return df, details


def sales_order_report_data(CompanyID, BranchID, FromDate, ToDate, ReportTypes):
    cursor = connection.cursor()
    ReportTypes = tuple(ReportTypes)

    dic = {'ReportTypes': ReportTypes, 'BranchID': BranchID,
           'FromDate': FromDate, 'ToDate': ToDate, 'CompanyID': CompanyID}
    if not len(ReportTypes) == 0:
        cursor.execute('''
            Select           
            S."VoucherNo" AS VoucherNo,      
            S."Date",
            AL."LedgerName" AS LedgerName,      
            (SELECT "LedgerName" FROM public."accountLedger_accountLedger" WHERE  
            "LedgerID" = S."LedgerID" AND "AccountGroupUnder" in ('10','29') AND "BranchID" = S."BranchID"
            AND "CompanyID_id" = S."CompanyID_id") AS CustomerName,     
            round(S."NetTotal",2) AS NetAmount,      
            round(S."TotalTax",2) AS TotalTax,      
            round(S."GrandTotal",2) AS GrandTotal,
            case 
            when S."IsInvoiced" = 'N'then 'Pending'
            when  S."IsInvoiced" = 'I' then 'Invoiced'
            when S."IsInvoiced" = 'C' then 'Cancelled'
            end AS Status     
            FROM public."salesOrderMasters_salesOrderMaster" AS S      
            INNER JOIN public."accountLedger_accountLedger" AS AL ON S."LedgerID" = AL."LedgerID"  
            AND AL."CompanyID_id" = S."CompanyID_id"     
            WHERE S."BranchID" = %(BranchID)s AND S."IsActive" = 'true' AND "IsInvoiced" in %(ReportTypes)s AND S."Date" BETWEEN %(FromDate)s AND %(ToDate)s
            AND S."CompanyID_id" = %(CompanyID)s      
            ORDER BY "SalesOrderMasterID" 
            ''', dic)

        data = cursor.fetchall()
        if cursor.rowcount == 0:
            data = [('', '', '', '', 0, 0, 0, "")]
    else:
        data = [('', '', '', '', 0, 0, 0, "")]

    df = pd.DataFrame(data)

    # adding Total in laast Row to data frame
    df.loc[str(_('Total'))] = df[[4, 5, 6]].sum().reindex(
        df.columns, fill_value='')

    # adding Heading to frame
    df.columns = [
        str(_('VoucherNo')), str(_('VoucherDate')), str(_('LedgerName')), str(_('CustomerName')), str(_('NetAmount')), str(_('TotalTax')), str(_('GrandTotal')), str(_('Status'))]
    # convert date format(millisecond) to str in dataframe
    df[str(_('VoucherDate'))] = df[str(_('VoucherDate'))].astype(str)

    json_records = df.reset_index().to_json(orient='records')
    details = json.loads(json_records)
    return df, details


def sales_register_report_data(CompanyID, BranchID, FromDate, ToDate, WarehouseID, UserID, LedgerID, ProductID, ProductGroupID, ProductCategoryID, ProductCode, Barcode):
    cursor = connection.cursor()
    WarehouseID = tuple(WarehouseID)
    UserID = tuple(UserID)
    LedgerID = tuple(LedgerID)
    BranchID = tuple(BranchID)
    dic = {'WarehouseID': WarehouseID, 'UserID': UserID, 'LedgerID': LedgerID, 'BranchID': BranchID,
           'ProductID': ProductID, 'ProductGroupID': ProductGroupID, 'ProductCategoryID': ProductCategoryID,
           'ProductCode': ProductCode, 'Barcode': Barcode, 'FromDate': FromDate, 'ToDate': ToDate, 'CompanyID': CompanyID}

    if int(ProductID) > 0:
        cursor.execute('''
            SELECT 
            "Date", "VoucherNo" as InvoiceNo,P."ProductCode", P."ProductName", PL."Barcode", round(SD."Qty",2),
            (SELECT NULLIF("UnitName", '') FROM public."units_unit" AS UN WHERE UN."CompanyID_id" = P."CompanyID_id" AND UN."UnitID" = PL."UnitID"  ) AS UnitName,

            round(SD."UnitPrice",2) as SalesPrice, round(SD."GrossAmount",2), round(SD."VATAmount",2), round(SD."NetAmount",2), round(SD."CostPerPrice",2) as Cost
            
            FROM public."salesMasters_salesMaster" AS S 
            INNER JOIN public."salesDetails_salesDetail" AS SD ON S."SalesMasterID" = SD."SalesMasterID" AND SD."CompanyID_id" = S."CompanyID_id" 
            INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID" AND P."CompanyID_id" = S."CompanyID_id" 
            INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = S."CompanyID_id" 
            INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = S."CompanyID_id" 
            INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = S."CompanyID_id"
            WHERE S."Date" BETWEEN %(FromDate)s AND %(ToDate)s AND SD."ProductID" = %(ProductID)s AND S."WarehouseID" in %(WarehouseID)s 
            AND S."CreatedUserID" in %(UserID)s AND S."LedgerID" in %(LedgerID)s AND S."CompanyID_id" = %(CompanyID)s 
            ''', dic)
    elif int(ProductGroupID) > 0:
        cursor.execute('''
            SELECT 
            "Date", "VoucherNo" as InvoiceNo,P."ProductCode", P."ProductName", PL."Barcode", round(SD."Qty",2),
            (SELECT NULLIF("UnitName", '') FROM public."units_unit" AS UN WHERE UN."CompanyID_id" = P."CompanyID_id" AND UN."UnitID" = PL."UnitID"  ) AS UnitName,

            round(SD."UnitPrice",2) as SalesPrice, round(SD."GrossAmount",2), round(SD."VATAmount",2), round(SD."NetAmount",2), round(SD."CostPerPrice",2) as Cost
            
            FROM public."salesMasters_salesMaster" AS S 
            INNER JOIN public."salesDetails_salesDetail" AS SD ON S."SalesMasterID" = SD."SalesMasterID" AND SD."CompanyID_id" = S."CompanyID_id" 
            INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID" AND P."CompanyID_id" = S."CompanyID_id" 
            INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = S."CompanyID_id"
            INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = S."CompanyID_id" 
            INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = S."CompanyID_id"
            WHERE S."Date" BETWEEN %(FromDate)s AND %(ToDate)s AND p."ProductGroupID" = %(ProductGroupID)s
            AND S."WarehouseID" in %(WarehouseID)s AND S."CreatedUserID" in %(UserID)s AND S."LedgerID" in %(LedgerID)s  AND S."CompanyID_id" = %(CompanyID)s 
            ''', dic)
    elif int(ProductCategoryID) > 0:
        cursor.execute('''
            SELECT 
            "Date", "VoucherNo" as InvoiceNo,P."ProductCode", P."ProductName", PL."Barcode", round(SD."Qty",2),
            (SELECT NULLIF("UnitName", '') FROM public."units_unit" AS UN WHERE UN."CompanyID_id" = P."CompanyID_id" AND UN."UnitID" = PL."UnitID"  ) AS UnitName,

            round(SD."UnitPrice",2) as SalesPrice, round(SD."GrossAmount",2), round(SD."VATAmount",2), round(SD."NetAmount",2), round(SD."CostPerPrice",2) as Cost
            
            FROM public."salesMasters_salesMaster" AS S 
            INNER JOIN public."salesDetails_salesDetail" AS SD ON S."SalesMasterID" = SD."SalesMasterID"  AND SD."CompanyID_id" = S."CompanyID_id" 
            INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID" AND P."CompanyID_id" = S."CompanyID_id" 
            INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = S."CompanyID_id"
            INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = S."CompanyID_id" 
            INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = S."CompanyID_id"
            WHERE S."Date" BETWEEN %(FromDate)s AND %(ToDate)s AND PG."CategoryID" = %(ProductCategoryID)s AND S."WarehouseID" in %(WarehouseID)s AND S."CreatedUserID" in %(UserID)s
            AND S."LedgerID" in %(LedgerID)s AND S."CompanyID_id" = %(CompanyID)s
            ''', dic)
    elif ProductCode:
        cursor.execute('''
            SELECT 
            "Date", "VoucherNo" as InvoiceNo,P."ProductCode", P."ProductName", PL."Barcode", round(SD."Qty",2),
            (SELECT NULLIF("UnitName", '') FROM public."units_unit" AS UN WHERE UN."CompanyID_id" = P."CompanyID_id" AND UN."UnitID" = PL."UnitID"  ) AS UnitName,

            round(SD."UnitPrice",2) as SalesPrice, round(SD."GrossAmount",2), round(SD."VATAmount",2), round(SD."NetAmount",2), round(SD."CostPerPrice",2) as Cost
            
            FROM public."salesMasters_salesMaster" AS S 
            INNER JOIN public."salesDetails_salesDetail" AS SD ON S."SalesMasterID" = SD."SalesMasterID" AND SD."CompanyID_id" = S."CompanyID_id" 
            INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID" AND P."CompanyID_id" = S."CompanyID_id" 
            INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = S."CompanyID_id" 
            INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = S."CompanyID_id" 
            INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = S."CompanyID_id"
            WHERE S."Date" BETWEEN %(FromDate)s AND %(ToDate)s AND P."ProductCode" = %(ProductCode)s AND S."WarehouseID" in %(WarehouseID)s 
            AND S."CreatedUserID" in %(UserID)s AND S."LedgerID" in %(LedgerID)s AND S."CompanyID_id" = %(CompanyID)s
            ''', dic)
    elif Barcode:
        cursor.execute('''
            SELECT 
            "Date", "VoucherNo" as InvoiceNo,P."ProductCode", P."ProductName", PL."Barcode", round(SD."Qty",2),
            (SELECT NULLIF("UnitName", '') FROM public."units_unit" AS UN WHERE UN."CompanyID_id" = P."CompanyID_id" AND UN."UnitID" = PL."UnitID"  ) AS UnitName,

            round(SD."UnitPrice",2) as SalesPrice, round(SD."GrossAmount",2), round(SD."VATAmount",2), round(SD."NetAmount",2), round(SD."CostPerPrice",2) as Cost
            
            FROM public."salesMasters_salesMaster" AS S 
            INNER JOIN public."salesDetails_salesDetail" AS SD ON S."SalesMasterID" = SD."SalesMasterID" AND SD."CompanyID_id" = S."CompanyID_id" 
            INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID" AND P."CompanyID_id" = S."CompanyID_id" 
            INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = S."CompanyID_id" 
            INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = S."CompanyID_id" 
            INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = S."CompanyID_id"
            WHERE S."Date" BETWEEN %(FromDate)s AND %(ToDate)s AND PL."Barcode" = %(Barcode)s AND S."WarehouseID" in %(WarehouseID)s 
            AND S."CreatedUserID" in %(UserID)s AND S."LedgerID" in %(LedgerID)s AND S."CompanyID_id" = %(CompanyID)s
            ''', dic)
    else:
        cursor.execute('''
            SELECT 
            "Date", "VoucherNo" as InvoiceNo,P."ProductCode", P."ProductName", PL."Barcode", round(SD."Qty",2),
            (SELECT NULLIF("UnitName", '') FROM public."units_unit" AS UN WHERE UN."CompanyID_id" = P."CompanyID_id" AND UN."UnitID" = PL."UnitID"  ) AS UnitName,

            round(SD."UnitPrice",2) as SalesPrice, round(SD."GrossAmount",2), round(SD."VATAmount",2), round(SD."NetAmount",2), round(SD."CostPerPrice",2) as Cost
            
            FROM public."salesMasters_salesMaster" AS S 
            INNER JOIN public."salesDetails_salesDetail" AS SD ON S."SalesMasterID" = SD."SalesMasterID" AND SD."CompanyID_id" = S."CompanyID_id" 
            INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID" AND P."CompanyID_id" = S."CompanyID_id" 
            INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = S."CompanyID_id" 
            INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = S."CompanyID_id" 
            INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = S."CompanyID_id"
            WHERE S."Date" BETWEEN %(FromDate)s AND %(ToDate)s AND S."WarehouseID" in %(WarehouseID)s 
            AND S."CreatedUserID" in %(UserID)s AND S."LedgerID" in %(LedgerID)s AND S."CompanyID_id" = %(CompanyID)s 
            ''', dic)

    data = cursor.fetchall()
    if cursor.rowcount == 0:
        data = [('', '', '', '', '', 0, 0, 0, 0, 0, 0, 0)]

    df = pd.DataFrame(data)
    ShowProfitinSalesRegisterReport = get_GeneralSettings(CompanyID,BranchID[0],"ShowProfitinSalesRegisterReport")
    df.columns = [
        str(('Date')), str(('InvoiceNo')), str(('ProductCode')), str(('ProductName')), str(('Barcode')), str(('Qty')),str(('UnitName')), str(('SalesPrice')), str(('GrossAmount')), str(('VATAmount')), str(('NetAmount')), str(('Cost'))]

    print(df)
    print(ShowProfitinSalesRegisterReport)
    if ShowProfitinSalesRegisterReport:
        profit_column = df["NetAmount"] - (df["Cost"] * df["Qty"])
        df["Profit"] = profit_column
        df.insert(11, 'Profit', df.pop("Profit"))
        df['Profit'] = df['Profit'].astype(float)
        df.loc[str(_('Total'))] = df[['Qty', 'SalesPrice', 'GrossAmount', 'VATAmount',
                                    'NetAmount', 'Cost', 'Profit']].sum().reindex(df.columns, fill_value='')
    else:       
        df.loc[str(_('Total'))] = df[['Qty', 'SalesPrice', 'GrossAmount', 'VATAmount',
                                    'NetAmount', 'Cost']].sum().reindex(df.columns, fill_value='')
    # convert date format(millisecond) to str in dataframe
    df['Date'] = df['Date'].astype(str)
    json_records = df.reset_index().to_json(orient='records')
    details = json.loads(json_records)
    return df, details


def purchase_register_report_data(CompanyID, BranchID, FromDate, ToDate, WarehouseID, UserID, LedgerID, ProductID, ProductGroupID, ProductCategoryID, ProductCode, Barcode):
    cursor = connection.cursor()
    WarehouseID = tuple(WarehouseID)
    UserID = tuple(UserID)
    LedgerID = tuple(LedgerID)
    BranchID = tuple(BranchID)
    dic = {'WarehouseID': WarehouseID, 'UserID': UserID, 'LedgerID': LedgerID, 'BranchID': BranchID,
           'ProductID': ProductID, 'ProductGroupID': ProductGroupID, 'ProductCategoryID': ProductCategoryID,
           'ProductCode': ProductCode, 'Barcode': Barcode, 'FromDate': FromDate, 'ToDate': ToDate, 'CompanyID': CompanyID}

    if int(ProductID) > 0:
        cursor.execute('''
            SELECT 
            "Date", "VoucherNo" as InvoiceNo,P."ProductCode", P."ProductName", PL."Barcode", round(PD."Qty",2),
            round(PD."UnitPrice",2) as UnitPrice, round(PD."GrossAmount",2), round(PD."VATAmount",2), round(PD."NetAmount",2), round(PD."CostPerItem",2) as Cost
            
            FROM public."purchaseMasters_purchaseMaster" AS PM 
            INNER JOIN public."purchaseDetailses_purchaseDetails" AS PD ON PM."PurchaseMasterID" = PD."PurchaseMasterID" AND PD."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."products_product" AS P ON PD."ProductID" = P."ProductID" AND P."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."pricelist_pricelist" AS PL ON PD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = PM."CompanyID_id"
            WHERE PM."Date" BETWEEN %(FromDate)s AND %(ToDate)s AND PD."ProductID" = %(ProductID)s AND PM."WarehouseID" in %(WarehouseID)s 
            AND PM."CreatedUserID" in %(UserID)s AND PM."LedgerID" in %(LedgerID)s AND PM."CompanyID_id" = %(CompanyID)s 
            ''', dic)
    elif int(ProductGroupID) > 0:
        cursor.execute('''
            SELECT 
            "Date", "VoucherNo" as InvoiceNo,P."ProductCode", P."ProductName", PL."Barcode", round(PD."Qty",2),
            round(PD."UnitPrice",2) as UnitPrice, round(PD."GrossAmount",2), round(PD."VATAmount",2), round(PD."NetAmount",2), round(PD."CostPerItem",2) as Cost
            
            FROM public."purchaseMasters_purchaseMaster" AS PM 
            INNER JOIN public."purchaseDetailses_purchaseDetails" AS PD ON PM."PurchaseMasterID" = PD."PurchaseMasterID" AND PD."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."products_product" AS P ON PD."ProductID" = P."ProductID" AND P."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."pricelist_pricelist" AS PL ON PD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = PM."CompanyID_id"
            INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = PM."CompanyID_id"
            WHERE PM."Date" BETWEEN %(FromDate)s AND %(ToDate)s AND p."ProductGroupID" = %(ProductGroupID)s
            AND PM."WarehouseID" in %(WarehouseID)s AND PM."CreatedUserID" in %(UserID)s AND PM."LedgerID" in %(LedgerID)s  AND PM."CompanyID_id" = %(CompanyID)s 
            ''', dic)
    elif int(ProductCategoryID) > 0:
        cursor.execute('''
            SELECT 
            "Date", "VoucherNo" as InvoiceNo,P."ProductCode", P."ProductName", PL."Barcode", round(PD."Qty",2),
            round(PD."UnitPrice",2) as UnitPrice, round(PD."GrossAmount",2), round(PD."VATAmount",2), round(PD."NetAmount",2), round(PD."CostPerItem",2) as Cost
            
            FROM public."purchaseMasters_purchaseMaster" AS PM 
            INNER JOIN public."purchaseDetailses_purchaseDetails" AS PD ON PM."PurchaseMasterID" = PD."PurchaseMasterID"  AND PD."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."products_product" AS P ON PD."ProductID" = P."ProductID" AND P."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."pricelist_pricelist" AS PL ON PD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = PM."CompanyID_id"
            INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = PM."CompanyID_id"
            WHERE PM."Date" BETWEEN %(FromDate)s AND %(ToDate)s AND PG."CategoryID" = %(ProductCategoryID)s AND PM."WarehouseID" in %(WarehouseID)s AND PM."CreatedUserID" in %(UserID)s
            AND PM."LedgerID" in %(LedgerID)s AND PM."CompanyID_id" = %(CompanyID)s
            ''', dic)
    elif ProductCode:
        cursor.execute('''
            SELECT 
            "Date", "VoucherNo" as InvoiceNo,P."ProductCode", P."ProductName", PL."Barcode", round(PD."Qty",2),
            round(PD."UnitPrice",2) as UnitPrice, round(PD."GrossAmount",2), round(PD."VATAmount",2), round(PD."NetAmount",2), round(PD."CostPerItem",2) as Cost
            
            FROM public."purchaseMasters_purchaseMaster" AS PM 
            INNER JOIN public."purchaseDetailses_purchaseDetails" AS PD ON PM."PurchaseMasterID" = PD."PurchaseMasterID" AND PD."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."products_product" AS P ON PD."ProductID" = P."ProductID" AND P."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."pricelist_pricelist" AS PL ON PD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = PM."CompanyID_id"
            WHERE PM."Date" BETWEEN %(FromDate)s AND %(ToDate)s AND P."ProductCode" = %(ProductCode)s AND PM."WarehouseID" in %(WarehouseID)s 
            AND PM."CreatedUserID" in %(UserID)s AND PM."LedgerID" in %(LedgerID)s AND PM."CompanyID_id" = %(CompanyID)s
            ''', dic)
    elif Barcode:
        cursor.execute('''
            SELECT 
            "Date", "VoucherNo" as InvoiceNo,P."ProductCode", P."ProductName", PL."Barcode", round(PD."Qty",2),
            round(PD."UnitPrice",2) as UnitPrice, round(PD."GrossAmount",2), round(PD."VATAmount",2), round(PD."NetAmount",2), round(PD."CostPerItem",2) as Cost
            
            FROM public."purchaseMasters_purchaseMaster" AS PM 
            INNER JOIN public."purchaseDetailses_purchaseDetails" AS PD ON PM."PurchaseMasterID" = PD."PurchaseMasterID" AND PD."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."products_product" AS P ON PD."ProductID" = P."ProductID" AND P."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."pricelist_pricelist" AS PL ON PD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = PM."CompanyID_id"
            WHERE PM."Date" BETWEEN %(FromDate)s AND %(ToDate)s AND PL."Barcode" = %(Barcode)s AND PM."WarehouseID" in %(WarehouseID)s 
            AND PM."CreatedUserID" in %(UserID)s AND PM."LedgerID" in %(LedgerID)s AND PM."CompanyID_id" = %(CompanyID)s
            ''', dic)
    else:
        cursor.execute('''
            SELECT 
            "Date", "VoucherNo" as InvoiceNo,P."ProductCode", P."ProductName", PL."Barcode", round(PD."Qty",2),
            round(PD."UnitPrice",2) as UnitPrice, round(PD."GrossAmount",2), round(PD."VATAmount",2), round(PD."NetAmount",2), round(PD."CostPerItem",2) as Cost
            
            FROM public."purchaseMasters_purchaseMaster" AS PM 
            INNER JOIN public."purchaseDetailses_purchaseDetails" AS PD ON PM."PurchaseMasterID" = PD."PurchaseMasterID" AND PD."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."products_product" AS P ON PD."ProductID" = P."ProductID" AND P."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."pricelist_pricelist" AS PL ON PD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = PM."CompanyID_id"
            WHERE PM."Date" BETWEEN %(FromDate)s AND %(ToDate)s AND PM."WarehouseID" in %(WarehouseID)s 
            AND PM."CreatedUserID" in %(UserID)s AND PM."LedgerID" in %(LedgerID)s AND PM."CompanyID_id" = %(CompanyID)s 
            ''', dic)

    data = cursor.fetchall()
    if cursor.rowcount == 0:
        data = [('', '', '', '', '', 0, 0, 0, 0, 0, 0)]

    df = pd.DataFrame(data)

    df.columns = [
        str(('Date')), str(('InvoiceNo')), str(('ProductCode')), str(('ProductName')), str(('Barcode')), str(('Qty')), str(('UnitPrice')), str(('GrossAmount')), str(('VATAmount')), str(('NetAmount')), str(('Cost'))]

    # profit_column = df["NetAmount"] - (df["Cost"] * df["Qty"])
    # df["Profit"] = profit_column
    # df.insert(11, 'Profit', df.pop("Profit"))
    # df['Profit'] = df['Profit'].astype(float)
    df.loc[str(_('Total'))] = df[['Qty', 'UnitPrice', 'GrossAmount', 'VATAmount',
                                  'NetAmount', 'Cost']].sum().reindex(df.columns, fill_value='')
    # convert date format(millisecond) to str in dataframe
    df['Date'] = df['Date'].astype(str)
    json_records = df.reset_index().to_json(orient='records')
    details = json.loads(json_records)
    return df, details


def salesReturn_register_report_data(CompanyID, BranchID, FromDate, ToDate, WarehouseID, UserID, LedgerID, ProductID, ProductGroupID, ProductCategoryID, ProductCode, Barcode):
    cursor = connection.cursor()
    WarehouseID = tuple(WarehouseID)
    UserID = tuple(UserID)
    LedgerID = tuple(LedgerID)
    BranchID = tuple(BranchID)
    dic = {'WarehouseID': WarehouseID, 'UserID': UserID, 'LedgerID': LedgerID, 'BranchID': BranchID,
           'ProductID': ProductID, 'ProductGroupID': ProductGroupID, 'ProductCategoryID': ProductCategoryID,
           'ProductCode': ProductCode, 'Barcode': Barcode, 'FromDate': FromDate, 'ToDate': ToDate, 'CompanyID': CompanyID}

    if int(ProductID) > 0:
        cursor.execute('''
            SELECT 
            "VoucherDate" as Date, "VoucherNo" as InvoiceNo,P."ProductCode", P."ProductName", PL."Barcode", round(SD."Qty",2),
            round(SD."UnitPrice",2) as SalesPrice, round(SD."GrossAmount",2), round(SD."VATAmount",2), round(SD."NetAmount",2), round(SD."CostPerPrice",2) as Cost
            
            FROM public."salesReturnMasters_salesReturnMaster" AS SR 
            INNER JOIN public."salesReturnDetails_salesReturnDetail" AS SD ON SR."SalesReturnMasterID" = SD."SalesReturnMasterID" AND SD."CompanyID_id" = SR."CompanyID_id" 
            INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID" AND P."CompanyID_id" = SR."CompanyID_id" 
            INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = SR."CompanyID_id" 
            INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = SR."CompanyID_id" 
            INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = SR."CompanyID_id"
            WHERE SR."VoucherDate" BETWEEN %(FromDate)s AND %(ToDate)s AND SD."ProductID" = %(ProductID)s AND SR."WarehouseID" in %(WarehouseID)s 
            AND SR."CreatedUserID" in %(UserID)s AND SR."LedgerID" in %(LedgerID)s AND SR."CompanyID_id" = %(CompanyID)s 
            ''', dic)
    elif int(ProductGroupID) > 0:
        cursor.execute('''
            SELECT 
            "VoucherDate" as Date, "VoucherNo" as InvoiceNo,P."ProductCode", P."ProductName", PL."Barcode", round(SD."Qty",2),
            round(SD."UnitPrice",2) as SalesPrice, round(SD."GrossAmount",2), round(SD."VATAmount",2), round(SD."NetAmount",2), round(SD."CostPerPrice",2) as Cost
            
            FROM public."salesReturnMasters_salesReturnMaster" AS SR 
            INNER JOIN public."salesReturnDetails_salesReturnDetail" AS SD ON SR."SalesReturnMasterID" = SD."SalesReturnMasterID" AND SD."CompanyID_id" = SR."CompanyID_id" 
            INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID" AND P."CompanyID_id" = SR."CompanyID_id" 
            INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = SR."CompanyID_id"
            INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = SR."CompanyID_id" 
            INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = SR."CompanyID_id"
            WHERE SR."VoucherDate" BETWEEN %(FromDate)s AND %(ToDate)s AND p."ProductGroupID" = %(ProductGroupID)s
            AND SR."WarehouseID" in %(WarehouseID)s AND SR."CreatedUserID" in %(UserID)s AND SR."LedgerID" in %(LedgerID)s  AND SR."CompanyID_id" = %(CompanyID)s 
            ''', dic)
    elif int(ProductCategoryID) > 0:
        cursor.execute('''
            SELECT 
            "VoucherDate" as Date, "VoucherNo" as InvoiceNo,P."ProductCode", P."ProductName", PL."Barcode", round(SD."Qty",2),
            round(SD."UnitPrice",2) as SalesPrice, round(SD."GrossAmount",2), round(SD."VATAmount",2), round(SD."NetAmount",2), round(SD."CostPerPrice",2) as Cost
            
            FROM public."salesReturnMasters_salesReturnMaster" AS SR 
            INNER JOIN public."salesReturnDetails_salesReturnDetail" AS SD ON SR."SalesReturnMasterID" = SD."SalesReturnMasterID"  AND SD."CompanyID_id" = SR."CompanyID_id" 
            INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID" AND P."CompanyID_id" = SR."CompanyID_id" 
            INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = SR."CompanyID_id"
            INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = SR."CompanyID_id" 
            INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = SR."CompanyID_id"
            WHERE SR."VoucherDate" BETWEEN %(FromDate)s AND %(ToDate)s AND PG."CategoryID" = %(ProductCategoryID)s AND SR."WarehouseID" in %(WarehouseID)s AND SR."CreatedUserID" in %(UserID)s
            AND SR."LedgerID" in %(LedgerID)s AND SR."CompanyID_id" = %(CompanyID)s
            ''', dic)
    elif ProductCode:
        cursor.execute('''
            SELECT 
            "VoucherDate" as Date, "VoucherNo" as InvoiceNo,P."ProductCode", P."ProductName", PL."Barcode", round(SD."Qty",2),
            round(SD."UnitPrice",2) as SalesPrice, round(SD."GrossAmount",2), round(SD."VATAmount",2), round(SD."NetAmount",2), round(SD."CostPerPrice",2) as Cost
            
            FROM public."salesReturnMasters_salesReturnMaster" AS SR 
            INNER JOIN public."salesReturnDetails_salesReturnDetail" AS SD ON SR."SalesReturnMasterID" = SD."SalesReturnMasterID" AND SD."CompanyID_id" = SR."CompanyID_id" 
            INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID" AND P."CompanyID_id" = SR."CompanyID_id" 
            INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = SR."CompanyID_id" 
            INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = SR."CompanyID_id" 
            INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = SR."CompanyID_id"
            WHERE SR."VoucherDate" BETWEEN %(FromDate)s AND %(ToDate)s AND P."ProductCode" = %(ProductCode)s AND SR."WarehouseID" in %(WarehouseID)s 
            AND SR."CreatedUserID" in %(UserID)s AND SR."LedgerID" in %(LedgerID)s AND SR."CompanyID_id" = %(CompanyID)s
            ''', dic)
    elif Barcode:
        cursor.execute('''
            SELECT 
            "VoucherDate" as Date, "VoucherNo" as InvoiceNo,P."ProductCode", P."ProductName", PL."Barcode", round(SD."Qty",2),
            round(SD."UnitPrice",2) as SalesPrice, round(SD."GrossAmount",2), round(SD."VATAmount",2), round(SD."NetAmount",2), round(SD."CostPerPrice",2) as Cost
            
            FROM public."salesReturnMasters_salesReturnMaster" AS SR 
            INNER JOIN public."salesReturnDetails_salesReturnDetail" AS SD ON SR."SalesReturnMasterID" = SD."SalesReturnMasterID" AND SD."CompanyID_id" = SR."CompanyID_id" 
            INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID" AND P."CompanyID_id" = SR."CompanyID_id" 
            INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = SR."CompanyID_id" 
            INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = SR."CompanyID_id" 
            INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = SR."CompanyID_id"
            WHERE SR."VoucherDate" BETWEEN %(FromDate)s AND %(ToDate)s AND PL."Barcode" = %(Barcode)s AND SR."WarehouseID" in %(WarehouseID)s 
            AND SR."CreatedUserID" in %(UserID)s AND SR."LedgerID" in %(LedgerID)s AND SR."CompanyID_id" = %(CompanyID)s
            ''', dic)
    else:
        cursor.execute('''
            SELECT 
            "VoucherDate" as Date, "VoucherNo" as InvoiceNo,P."ProductCode", P."ProductName", PL."Barcode", round(SD."Qty",2),
            round(SD."UnitPrice",2) as SalesPrice, round(SD."GrossAmount",2), round(SD."VATAmount",2), round(SD."NetAmount",2), round(SD."CostPerPrice",2) as Cost
            
            FROM public."salesReturnMasters_salesReturnMaster" AS SR 
            INNER JOIN public."salesReturnDetails_salesReturnDetail" AS SD ON SR."SalesReturnMasterID" = SD."SalesReturnMasterID" AND SD."CompanyID_id" = SR."CompanyID_id" 
            INNER JOIN public."products_product" AS P ON SD."ProductID" = P."ProductID" AND P."CompanyID_id" = SR."CompanyID_id" 
            INNER JOIN public."pricelist_pricelist" AS PL ON SD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = SR."CompanyID_id" 
            INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = SR."CompanyID_id" 
            INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = SR."CompanyID_id"
            WHERE SR."VoucherDate" BETWEEN %(FromDate)s AND %(ToDate)s AND SR."WarehouseID" in %(WarehouseID)s 
            AND SR."CreatedUserID" in %(UserID)s AND SR."LedgerID" in %(LedgerID)s AND SR."CompanyID_id" = %(CompanyID)s 
            ''', dic)

    data = cursor.fetchall()
    if cursor.rowcount == 0:
        data = [('', '', '', '', '', 0, 0, 0, 0, 0, 0)]

    df = pd.DataFrame(data)

    df.columns = [
        str(('Date')), str(('InvoiceNo')), str(('ProductCode')), str(('ProductName')), str(('Barcode')), str(('Qty')), str(('SalesPrice')), str(('GrossAmount')), str(('VATAmount')), str(('NetAmount')), str(('Cost'))]

    profit_column = df["NetAmount"] - (df["Cost"] * df["Qty"])
    df["Profit"] = profit_column
    df.insert(11, 'Profit', df.pop("Profit"))
    df['Profit'] = df['Profit'].astype(float)
    df.loc[str(_('Total'))] = df[['Qty', 'SalesPrice', 'GrossAmount', 'VATAmount',
                                  'NetAmount', 'Cost', 'Profit']].sum().reindex(df.columns, fill_value='')
    # convert date format(millisecond) to str in dataframe
    df['Date'] = df['Date'].astype(str)
    json_records = df.reset_index().to_json(orient='records')
    details = json.loads(json_records)
    return df, details


def purchaseReturn_register_report_data(CompanyID, BranchID, FromDate, ToDate, WarehouseID, UserID, LedgerID, ProductID, ProductGroupID, ProductCategoryID, ProductCode, Barcode):
    cursor = connection.cursor()
    WarehouseID = tuple(WarehouseID)
    UserID = tuple(UserID)
    LedgerID = tuple(LedgerID)
    BranchID = tuple(BranchID)
    dic = {'WarehouseID': WarehouseID, 'UserID': UserID, 'LedgerID': LedgerID, 'BranchID': BranchID,
           'ProductID': ProductID, 'ProductGroupID': ProductGroupID, 'ProductCategoryID': ProductCategoryID,
           'ProductCode': ProductCode, 'Barcode': Barcode, 'FromDate': FromDate, 'ToDate': ToDate, 'CompanyID': CompanyID}

    if int(ProductID) > 0:
        cursor.execute('''
            SELECT 
            "VoucherDate" as Date, "VoucherNo" as InvoiceNo,P."ProductCode", P."ProductName", PL."Barcode", round(PD."Qty",2),
            round(PD."UnitPrice",2) as UnitPrice, round(PD."GrossAmount",2), round(PD."VATAmount",2), round(PD."NetAmount",2), round(PD."CostPerPrice",2) as Cost
            
            FROM public."purchaseReturnMasters_purchaseReturnMaster" AS PM 
            INNER JOIN public."purchaseReturnDetails_purchaseReturnDetail" AS PD ON PM."PurchaseReturnMasterID" = PD."PurchaseReturnMasterID" AND PD."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."products_product" AS P ON PD."ProductID" = P."ProductID" AND P."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."pricelist_pricelist" AS PL ON PD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = PM."CompanyID_id"
            WHERE PM."VoucherDate" BETWEEN %(FromDate)s AND %(ToDate)s AND PD."ProductID" = %(ProductID)s AND PM."WarehouseID" in %(WarehouseID)s 
            AND PM."CreatedUserID" in %(UserID)s AND PM."LedgerID" in %(LedgerID)s AND PM."CompanyID_id" = %(CompanyID)s 
            ''', dic)
    elif int(ProductGroupID) > 0:
        cursor.execute('''
            SELECT 
            "VoucherDate" as Date, "VoucherNo" as InvoiceNo,P."ProductCode", P."ProductName", PL."Barcode", round(PD."Qty",2),
            round(PD."UnitPrice",2) as UnitPrice, round(PD."GrossAmount",2), round(PD."VATAmount",2), round(PD."NetAmount",2), round(PD."CostPerPrice",2) as Cost
            
            FROM public."purchaseReturnMasters_purchaseReturnMaster" AS PM 
            INNER JOIN public."purchaseReturnDetails_purchaseReturnDetail" AS PD ON PM."PurchaseReturnMasterID" = PD."PurchaseReturnMasterID" AND PD."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."products_product" AS P ON PD."ProductID" = P."ProductID" AND P."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."pricelist_pricelist" AS PL ON PD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = PM."CompanyID_id"
            INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = PM."CompanyID_id"
            WHERE PM."VoucherDate" BETWEEN %(FromDate)s AND %(ToDate)s AND p."ProductGroupID" = %(ProductGroupID)s
            AND PM."WarehouseID" in %(WarehouseID)s AND PM."CreatedUserID" in %(UserID)s AND PM."LedgerID" in %(LedgerID)s  AND PM."CompanyID_id" = %(CompanyID)s 
            ''', dic)
    elif int(ProductCategoryID) > 0:
        cursor.execute('''
            SELECT 
            "VoucherDate" as Date, "VoucherNo" as InvoiceNo,P."ProductCode", P."ProductName", PL."Barcode", round(PD."Qty",2),
            round(PD."UnitPrice",2) as UnitPrice, round(PD."GrossAmount",2), round(PD."VATAmount",2), round(PD."NetAmount",2), round(PD."CostPerPrice",2) as Cost
            
            FROM public."purchaseReturnMasters_purchaseReturnMaster" AS PM 
            INNER JOIN public."purchaseReturnDetails_purchaseReturnDetail" AS PD ON PM."PurchaseReturnMasterID" = PD."PurchaseReturnMasterID"  AND PD."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."products_product" AS P ON PD."ProductID" = P."ProductID" AND P."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."pricelist_pricelist" AS PL ON PD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = PM."CompanyID_id"
            INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = PM."CompanyID_id"
            WHERE PM."VoucherDate" BETWEEN %(FromDate)s AND %(ToDate)s AND PG."CategoryID" = %(ProductCategoryID)s AND PM."WarehouseID" in %(WarehouseID)s AND PM."CreatedUserID" in %(UserID)s
            AND PM."LedgerID" in %(LedgerID)s AND PM."CompanyID_id" = %(CompanyID)s
            ''', dic)
    elif ProductCode:
        cursor.execute('''
            SELECT 
            "VoucherDate" as Date, "VoucherNo" as InvoiceNo,P."ProductCode", P."ProductName", PL."Barcode", round(PD."Qty",2),
            round(PD."UnitPrice",2) as UnitPrice, round(PD."GrossAmount",2), round(PD."VATAmount",2), round(PD."NetAmount",2), round(PD."CostPerPrice",2) as Cost
            
            FROM public."purchaseReturnMasters_purchaseReturnMaster" AS PM 
            INNER JOIN public."purchaseReturnDetails_purchaseReturnDetail" AS PD ON PM."PurchaseReturnMasterID" = PD."PurchaseReturnMasterID" AND PD."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."products_product" AS P ON PD."ProductID" = P."ProductID" AND P."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."pricelist_pricelist" AS PL ON PD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = PM."CompanyID_id"
            WHERE PM."VoucherDate" BETWEEN %(FromDate)s AND %(ToDate)s AND P."ProductCode" = %(ProductCode)s AND PM."WarehouseID" in %(WarehouseID)s 
            AND PM."CreatedUserID" in %(UserID)s AND PM."LedgerID" in %(LedgerID)s AND PM."CompanyID_id" = %(CompanyID)s
            ''', dic)
    elif Barcode:
        cursor.execute('''
            SELECT 
            "VoucherDate" as Date, "VoucherNo" as InvoiceNo,P."ProductCode", P."ProductName", PL."Barcode", round(PD."Qty",2),
            round(PD."UnitPrice",2) as UnitPrice, round(PD."GrossAmount",2), round(PD."VATAmount",2), round(PD."NetAmount",2), round(PD."CostPerPrice",2) as Cost
            
            FROM public."purchaseReturnMasters_purchaseReturnMaster" AS PM 
            INNER JOIN public."purchaseReturnDetails_purchaseReturnDetail" AS PD ON PM."PurchaseReturnMasterID" = PD."PurchaseReturnMasterID" AND PD."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."products_product" AS P ON PD."ProductID" = P."ProductID" AND P."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."pricelist_pricelist" AS PL ON PD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = PM."CompanyID_id"
            WHERE PM."VoucherDate" BETWEEN %(FromDate)s AND %(ToDate)s AND PL."Barcode" = %(Barcode)s AND PM."WarehouseID" in %(WarehouseID)s 
            AND PM."CreatedUserID" in %(UserID)s AND PM."LedgerID" in %(LedgerID)s AND PM."CompanyID_id" = %(CompanyID)s
            ''', dic)
    else:
        cursor.execute('''
            SELECT 
            "VoucherDate" as Date, "VoucherNo" as InvoiceNo,P."ProductCode", P."ProductName", PL."Barcode", round(PD."Qty",2),
            round(PD."UnitPrice",2) as UnitPrice, round(PD."GrossAmount",2), round(PD."VATAmount",2), round(PD."NetAmount",2), round(PD."CostPerPrice",2) as Cost
            
            FROM public."purchaseReturnMasters_purchaseReturnMaster" AS PM 
            INNER JOIN public."purchaseReturnDetails_purchaseReturnDetail" AS PD ON PM."PurchaseReturnMasterID" = PD."PurchaseReturnMasterID" AND PD."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."products_product" AS P ON PD."ProductID" = P."ProductID" AND P."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."pricelist_pricelist" AS PL ON PD."PriceListID" = PL."PriceListID" AND PL."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."productgroup_productgroup" AS PG ON p."ProductGroupID" = PG."ProductGroupID" AND PG."CompanyID_id" = PM."CompanyID_id" 
            INNER JOIN public."productcategory_productcategory" AS PC ON PG."CategoryID" = PC."ProductCategoryID" AND PC."CompanyID_id" = PM."CompanyID_id"
            WHERE PM."VoucherDate" BETWEEN %(FromDate)s AND %(ToDate)s AND PM."WarehouseID" in %(WarehouseID)s 
            AND PM."CreatedUserID" in %(UserID)s AND PM."LedgerID" in %(LedgerID)s AND PM."CompanyID_id" = %(CompanyID)s 
            ''', dic)

    data = cursor.fetchall()
    if cursor.rowcount == 0:
        data = [('', '', '', '', '', 0, 0, 0, 0, 0, 0)]

    df = pd.DataFrame(data)

    df.columns = [
        str(('Date')), str(('InvoiceNo')), str(('ProductCode')), str(('ProductName')), str(('Barcode')), str(('Qty')), str(('UnitPrice')), str(('GrossAmount')), str(('VATAmount')), str(('NetAmount')), str(('Cost'))]

    # profit_column = df["NetAmount"] - (df["Cost"] * df["Qty"])
    # df["Profit"] = profit_column
    # df.insert(11, 'Profit', df.pop("Profit"))
    # df['Profit'] = df['Profit'].astype(float)
    df.loc[str(_('Total'))] = df[['Qty', 'UnitPrice', 'GrossAmount', 'VATAmount',
                                  'NetAmount', 'Cost']].sum().reindex(df.columns, fill_value='')
    # convert date format(millisecond) to str in dataframe
    df['Date'] = df['Date'].astype(str)
    json_records = df.reset_index().to_json(orient='records')
    details = json.loads(json_records)
    return df, details


def stock_transfer_report_data(CompanyID,BranchID,FromDate,ToDate,PriceRounding,UserID,WarehouseFromID,WarehouseToID,VoucherType):
    cursor = connection.cursor()
    dic = {'UserID':UserID,'WarehouseFromID': WarehouseFromID,'WarehouseToID': WarehouseToID, 'BranchID': BranchID, 'FromDate': FromDate,'ToDate':ToDate,'CompanyID':CompanyID,'VoucherType':VoucherType}
    cursor.execute('''
        SELECT 
        "VoucherNo"  
        ,"Date"  
        ,UC."username" AS User
        ,WF."WarehouseName" AS WarehouseFrom  
        , WT."WarehouseName" AS WarehouseTo
        , "TotalQty"  
        , "GrandTotal"  
        FROM public."stockTransferMaster_ID_stockTransferMaster_ID" AS S  
        INNER JOIN public."warehouse_warehouse" WT ON WT."BranchID" = S."BranchID" AND WT."WarehouseID" = S."WarehouseToID" AND WT."CompanyID_id" = S."CompanyID_id"  
        INNER JOIN public."warehouse_warehouse" WF ON WF."BranchID" = S."BranchID" AND WF."WarehouseID" = S."WarehouseFromID" AND WF."CompanyID_id" = S."CompanyID_id"  
        INNER JOIN public."auth_user" UC ON UC."id" = S."CreatedUserID"  
        INNER JOIN public."auth_user" UU ON UU."id" = S."CreatedUserID"  
        WHERE        
        S."CompanyID_id" = %(CompanyID)s AND S."Date" BETWEEN %(FromDate)s AND %(ToDate)s AND "VoucherType" = %(VoucherType)s AND
        CASE WHEN %(UserID)s > 0 AND %(WarehouseFromID)s > 0 AND %(WarehouseToID)s > 0 THEN
        S."CreatedUserID" = %(UserID)s AND "WarehouseFromID" = %(WarehouseFromID)s AND "WarehouseToID" = %(WarehouseToID)s AND S."BranchID" = %(BranchID)s
        
        WHEN %(UserID)s > 0 AND %(WarehouseFromID)s = 0 AND %(WarehouseToID)s = 0 THEN
        S."CreatedUserID" = %(UserID)s AND S."BranchID" = %(BranchID)s
        WHEN %(UserID)s = 0 AND %(WarehouseFromID)s > 0 AND %(WarehouseToID)s = 0 THEN
        "WarehouseFromID" = %(WarehouseFromID)s AND S."BranchID" = %(BranchID)s
        WHEN %(UserID)s = 0 AND %(WarehouseFromID)s = 0 AND %(WarehouseToID)s > 0 THEN
        "WarehouseToID" = %(WarehouseToID)s AND S."BranchID" = %(BranchID)s

        WHEN %(UserID)s = 0 AND %(WarehouseFromID)s > 0 AND %(WarehouseToID)s > 0 THEN
        "WarehouseFromID" = %(WarehouseFromID)s AND "WarehouseToID" = %(WarehouseToID)s AND S."BranchID" = %(BranchID)s
        WHEN %(UserID)s > 0 AND %(WarehouseFromID)s = 0 AND %(WarehouseToID)s > 0 THEN
        S."CreatedUserID" = %(UserID)s AND "WarehouseToID" = %(WarehouseToID)s AND S."BranchID" = %(BranchID)s
        WHEN %(UserID)s > 0 AND %(WarehouseFromID)s > 0 AND %(WarehouseToID)s = 0 THEN
        "WarehouseFromID" = %(WarehouseFromID)s AND S."CreatedUserID" = %(UserID)s AND S."BranchID" = %(BranchID)s

        ELSE
        S."BranchID" = %(BranchID)s
        END
            ''',dic)
  
   

    data = cursor.fetchall()
    if cursor.rowcount == 0:
        data = [('', '', '', '', '', 0, 0)]

    df = pd.DataFrame(data)

    # adding Total in laast Row to data frame
    df.loc[str(_('Total'))] = df[[5, 6]].sum().reindex(
        df.columns, fill_value='')

    # adding Heading to frame
    df.columns = [
        str(_('VoucherNo')), str(_('Date')), str(_('User')), str(_('WarehouseFrom')), str(_('WarehouseTo')), str(_('TotalQty')), str(_('GrandTotal'))]
    # convert date format(millisecond) to str in dataframe
    df['Date'] = df['Date'].astype(str)
    json_records = df.reset_index().to_json(orient='records')
    details = json.loads(json_records)
    return df,details


def query_ProfitAndLoss_filter(filterValue,CompanyID,BranchID,FromDate,ToDate,ManualOpeningStock,ManualClosingStock):
    cursor = connection.cursor()
    dic = {'BranchID': BranchID, 'FromDate': FromDate,'ToDate':ToDate,'CompanyID':CompanyID,'ManualOpeningStock':ManualOpeningStock,'ManualClosingStock':ManualClosingStock}
    # ===========================CONSOLIDATED==============================
    if filterValue == 'AVG_OpeningStock':
        if ManualOpeningStock:
            data = [[(int(ManualOpeningStock))]]

        else:
            cursor.execute('''
                select AverageValueOfAllProductBeforeDate(%(ToDate)s,%(FromDate)s,%(CompanyID)s,%(BranchID)s)

                ''',dic)
            data = cursor.fetchall()
        
    elif filterValue == 'AVG_ClosingStock':
        if ManualClosingStock:
            ManualClosingStock = int(ManualClosingStock)
            data = [[(int(ManualClosingStock))]]
        else:
            cursor.execute('''
                select AverageValueOfAllProduct(%(ToDate)s,%(CompanyID)s,%(BranchID)s)
            
                ''',dic)
            data = cursor.fetchall()
    elif filterValue == 'FIFO_OpeningStock':
        if ManualOpeningStock:
            data = [[(int(ManualOpeningStock))]]
        else:
            cursor.execute('''
                SELECT SUM(FIFOValueOfAProductBeforeDate(%(FromDate)s,P."ProductID",%(CompanyID)s)) FROM public.products_product AS P 
                WHERE "CompanyID_id"=%(CompanyID)s AND "InventoryType" = 'StockItem'
                ''',dic)
            data = cursor.fetchall()

    elif filterValue == 'FIFO_ClosingStock':
        if ManualClosingStock:
            data = [[(int(ManualClosingStock))]]
        else:
            cursor.execute('''
                SELECT SUM(FIFOValueOfAProduct(%(ToDate)s,P."ProductID",%(CompanyID)s)) FROM public.products_product AS P 
                WHERE "CompanyID_id"=%(CompanyID)s AND "InventoryType" = 'StockItem'
                ''',dic)
            data = cursor.fetchall()
    elif filterValue == 'LIFO_OpeningStock':
        if ManualOpeningStock:
            data = [[(int(ManualOpeningStock))]]
        else:
            cursor.execute('''
                SELECT SUM(LIFOValueOfAProductBeforeDate(%(FromDate)s,P."ProductID",%(CompanyID)s)) FROM public.products_product AS P 
                WHERE "CompanyID_id"=%(CompanyID)s AND "InventoryType" = 'StockItem'
                ''',dic)
            data = cursor.fetchall()
    elif filterValue == 'LIFO_ClosingStock':
        if ManualClosingStock:
            data = [[(int(ManualClosingStock))]]
        else:
            cursor.execute('''
                SELECT SUM(LIFOValueOfAProduct(%(ToDate)s,P."ProductID",%(CompanyID)s)) FROM public.products_product AS P 
                WHERE "CompanyID_id"=%(CompanyID)s AND "InventoryType" = 'StockItem'
                ''',dic)
            data = cursor.fetchall()
   
    
    return data


def query_ProfitAndLoss_Consolidated_data(key,CompanyID,BranchID,FromDate,ToDate,PriceRounding,VoucherType,ManualOpeningStock,ManualClosingStock):
    cursor = connection.cursor()
    dic = {'PriceRounding':PriceRounding,'BranchID': BranchID, 'FromDate': FromDate,'ToDate':ToDate,'CompanyID':CompanyID,'ManualOpeningStock':ManualOpeningStock,'ManualClosingStock':ManualClosingStock}
    # ===========================CONSOLIDATED==============================
    if VoucherType == 'direct_expence':
        cursor.execute('''
            WITH RECURSIVE GroupInMainGroup42 AS (
            SELECT
            "AccountGroupID",
            "AccountGroupUnder",
            "AccountGroupName"
            FROM public.accountgroup_accountgroup
            WHERE
            "AccountGroupID"= 42 AND "CompanyID_id" = %(CompanyID)s
            UNION
            SELECT
            e."AccountGroupID",
            e."AccountGroupUnder",
            e."AccountGroupName"
            FROM
            public.accountgroup_accountgroup e
            INNER JOIN GroupInMainGroup42 s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = %(CompanyID)s
            )  
            SELECT "AccountGroupID", "AccountGroupName", SUM(Total) AS Total  
            FROM(  
            SELECT "AccountGroupID","AccountGroupName","LedgerID","LedgerName" ,  
            (SELECT ROUND(coalesce(SUM("Debit"), 0)- (coalesce(SUM("Credit"), 0)),2) 
            FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN %(FromDate)s AND %(ToDate)s )
            AND "BranchID" = %(BranchID)s AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
            AS Total FROM public."accountLedger_accountLedger" AL  
            INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
            WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup42) AND AL."BranchID" = %(BranchID)s
            AND AL."CompanyID_id" = %(CompanyID)s
            ) AS TEMP WHERE Total != 0 GROUP BY "AccountGroupID", "AccountGroupName";
            ''',dic)
    elif VoucherType == 'indirect_expence':
        cursor.execute('''
            WITH RECURSIVE GroupInMainGroup43 AS (
            SELECT
            "AccountGroupID",
            "AccountGroupUnder",
            "AccountGroupName"
            FROM public.accountgroup_accountgroup
            WHERE
            "AccountGroupID"= 43 AND "CompanyID_id" = %(CompanyID)s
            UNION
            SELECT
            e."AccountGroupID",
            e."AccountGroupUnder",
            e."AccountGroupName"
            FROM
            public.accountgroup_accountgroup e
            INNER JOIN GroupInMainGroup43 s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = %(CompanyID)s
            )       
            SELECT "AccountGroupID", "AccountGroupName", SUM(Total) AS Total  
            FROM(  
            SELECT "AccountGroupID","AccountGroupName","LedgerID","LedgerName" ,  
            (SELECT ROUND(coalesce(SUM("Debit"), 0)- (coalesce(SUM("Credit"), 0)),2) 
            FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN %(FromDate)s AND %(ToDate)s )
            AND "BranchID" = %(BranchID)s AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
            AS Total FROM public."accountLedger_accountLedger" AL  
            INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
            WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup43) AND AL."BranchID" = %(BranchID)s
            AND AL."CompanyID_id" = %(CompanyID)s
            ) AS TEMP WHERE Total != 0 GROUP BY "AccountGroupID", "AccountGroupName";
        ''',dic)
    elif VoucherType == 'direct_income':
        cursor.execute('''
            WITH RECURSIVE GroupInMainGroup70 AS (
            SELECT
            "AccountGroupID",
            "AccountGroupUnder",
            "AccountGroupName"
            FROM public.accountgroup_accountgroup
            WHERE
            "AccountGroupID"= 70 AND "CompanyID_id" = %(CompanyID)s
            UNION
            SELECT
            e."AccountGroupID",
            e."AccountGroupUnder",
            e."AccountGroupName"
            FROM
            public.accountgroup_accountgroup e
            INNER JOIN GroupInMainGroup70 s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = %(CompanyID)s
            )       
            SELECT "AccountGroupID", "AccountGroupName", SUM(Total) AS Total  
            FROM(  
            SELECT "AccountGroupID","AccountGroupName","LedgerID","LedgerName" ,  
            (SELECT ROUND(coalesce(SUM("Credit"), 0)- (coalesce(SUM("Debit"), 0)),2) 
            FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN %(FromDate)s AND %(ToDate)s )
            AND "BranchID" = %(BranchID)s AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
            AS Total FROM public."accountLedger_accountLedger" AL  
            INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
            WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup70) AND AL."BranchID" = %(BranchID)s
            AND AL."CompanyID_id" = %(CompanyID)s
            ) AS TEMP WHERE Total != 0 GROUP BY "AccountGroupID", "AccountGroupName";
        ''',dic)
    elif VoucherType == 'indirect_income':
        cursor.execute('''
            WITH RECURSIVE GroupInMainGroup71 AS (
            SELECT
            "AccountGroupID",
            "AccountGroupUnder",
            "AccountGroupName"
            FROM public.accountgroup_accountgroup
            WHERE
            "AccountGroupID"= 71 AND "CompanyID_id" = %(CompanyID)s
            UNION
            SELECT
            e."AccountGroupID",
            e."AccountGroupUnder",
            e."AccountGroupName"
            FROM
            public.accountgroup_accountgroup e
            INNER JOIN GroupInMainGroup71 s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = %(CompanyID)s
            )       
            SELECT "AccountGroupID", "AccountGroupName", SUM(Total) AS Total  
            FROM(  
            SELECT "AccountGroupID","AccountGroupName","LedgerID","LedgerName" ,  
            (SELECT ROUND(coalesce(SUM("Credit"), 0)- (coalesce(SUM("Debit"), 0)),2) 
            FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN %(FromDate)s AND %(ToDate)s )
            AND "BranchID" = %(BranchID)s AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
            AS Total FROM public."accountLedger_accountLedger" AL  
            INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
            WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup71) AND AL."BranchID" = %(BranchID)s
            AND AL."CompanyID_id" = %(CompanyID)s
            ) AS TEMP WHERE Total != 0 GROUP BY "AccountGroupID", "AccountGroupName";
        ''',dic)

    data = cursor.fetchall()
    if cursor.rowcount == 0:
        data = [('','',0)]
    
    return data


def query_ProfitAndLoss_Detailed_data(key,CompanyID,BranchID,FromDate,ToDate,PriceRounding,VoucherType,ManualOpeningStock,ManualClosingStock):
    cursor = connection.cursor()
    dic = {'PriceRounding':PriceRounding,'BranchID': BranchID, 'FromDate': FromDate,'ToDate':ToDate,'CompanyID':CompanyID,'ManualOpeningStock':ManualOpeningStock,'ManualClosingStock':ManualClosingStock}
    # ===========================CONSOLIDATED==============================
    if VoucherType == 'direct_expence':
        cursor.execute('''
            WITH RECURSIVE GroupInMainGroup42 AS (
            SELECT
            "AccountGroupID",
            "AccountGroupUnder",
            "AccountGroupName"
            FROM public.accountgroup_accountgroup
            WHERE
            "AccountGroupID"= 42 AND "CompanyID_id" = %(CompanyID)s
            UNION
            SELECT
            e."AccountGroupID",
            e."AccountGroupUnder",
            e."AccountGroupName"
            FROM
            public.accountgroup_accountgroup e
            INNER JOIN GroupInMainGroup42 s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = %(CompanyID)s
            )  
            SELECT *  
            FROM(  
            SELECT "AccountGroupID","AccountGroupName","LedgerName" ,  
            (SELECT ROUND(coalesce(SUM("Debit"), 0)- (coalesce(SUM("Credit"), 0)),2) 
            FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN %(FromDate)s AND %(ToDate)s )
            AND "BranchID" = %(BranchID)s AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
            AS Total FROM public."accountLedger_accountLedger" AL  
            INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
            WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup42) AND AL."BranchID" = %(BranchID)s
            AND AL."CompanyID_id" = %(CompanyID)s
            ) AS TEMP WHERE Total != 0;
            ''',dic)
    elif VoucherType == 'indirect_expence':
        cursor.execute('''
            WITH RECURSIVE GroupInMainGroup43 AS (
            SELECT
            "AccountGroupID",
            "AccountGroupUnder",
            "AccountGroupName"
            FROM public.accountgroup_accountgroup
            WHERE
            "AccountGroupID"= 43 AND "CompanyID_id" = %(CompanyID)s
            UNION
            SELECT
            e."AccountGroupID",
            e."AccountGroupUnder",
            e."AccountGroupName"
            FROM
            public.accountgroup_accountgroup e
            INNER JOIN GroupInMainGroup43 s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = %(CompanyID)s
            )       
            SELECT *
            FROM(  
            SELECT "AccountGroupID","AccountGroupName","LedgerName" ,  
            (SELECT ROUND(coalesce(SUM("Debit"), 0)- (coalesce(SUM("Credit"), 0)),2) 
            FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN %(FromDate)s AND %(ToDate)s )
            AND "BranchID" = %(BranchID)s AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
            AS Total FROM public."accountLedger_accountLedger" AL  
            INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
            WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup43) AND AL."BranchID" = %(BranchID)s
            AND AL."CompanyID_id" = %(CompanyID)s
            ) AS TEMP WHERE Total != 0;

        ''',dic)
    elif VoucherType == 'direct_income':
        cursor.execute('''
            WITH RECURSIVE GroupInMainGroup70 AS (
            SELECT
            "AccountGroupID",
            "AccountGroupUnder",
            "AccountGroupName"
            FROM public.accountgroup_accountgroup
            WHERE
            "AccountGroupID"= 70 AND "CompanyID_id" = %(CompanyID)s
            UNION
            SELECT
            e."AccountGroupID",
            e."AccountGroupUnder",
            e."AccountGroupName"
            FROM
            public.accountgroup_accountgroup e
            INNER JOIN GroupInMainGroup70 s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = %(CompanyID)s
            )       
            SELECT *
            FROM(  
            SELECT "AccountGroupID","AccountGroupName","LedgerName" ,  
            (SELECT ROUND(coalesce(SUM("Credit"), 0)- (coalesce(SUM("Debit"), 0)),2) 
            FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN %(FromDate)s AND %(ToDate)s )
            AND "BranchID" = %(BranchID)s AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
            AS Total FROM public."accountLedger_accountLedger" AL  
            INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
            WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup70) AND AL."BranchID" = %(BranchID)s
            AND AL."CompanyID_id" = %(CompanyID)s
            ) AS TEMP WHERE Total != 0;
        ''',dic)
    elif VoucherType == 'indirect_income':
        cursor.execute('''
            WITH RECURSIVE GroupInMainGroup71 AS (
            SELECT
            "AccountGroupID",
            "AccountGroupUnder",
            "AccountGroupName"
            FROM public.accountgroup_accountgroup
            WHERE
            "AccountGroupID"= 71 AND "CompanyID_id" = %(CompanyID)s
            UNION
            SELECT
            e."AccountGroupID",
            e."AccountGroupUnder",
            e."AccountGroupName"
            FROM
            public.accountgroup_accountgroup e
            INNER JOIN GroupInMainGroup71 s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = %(CompanyID)s
            )       
            SELECT *
            FROM(  
            SELECT "AccountGroupID","AccountGroupName","LedgerName" ,  
            (SELECT ROUND(coalesce(SUM("Credit"), 0)- (coalesce(SUM("Debit"), 0)),2) 
            FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN %(FromDate)s AND %(ToDate)s )
            AND "BranchID" = %(BranchID)s AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
            AS Total FROM public."accountLedger_accountLedger" AL  
            INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
            WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup71) AND AL."BranchID" = '1'
            AND AL."CompanyID_id" = %(CompanyID)s
            ) AS TEMP WHERE Total != 0;

        ''',dic)

    data = cursor.fetchall()
    if cursor.rowcount == 0:
        data = [('','','',0)]
    
    return data


def query_BalanceSheet_Consolidated_data(key,CompanyID,BranchID,FromDate,ToDate,PriceRounding,VoucherType):
    cursor = connection.cursor()
    GroupID = ""
    if VoucherType == 'Assets':
        GroupID = 3
    elif VoucherType == "Liabilities":
        GroupID = 4
    dic = {'GroupID':GroupID,'PriceRounding':PriceRounding,'BranchID': BranchID, 'FromDate': FromDate,'ToDate':ToDate,'CompanyID':CompanyID}
    # ===========================CONSOLIDATED==============================
    if VoucherType == 'Assets':
        cursor.execute('''
            WITH RECURSIVE GroupInMainGroup AS (
            SELECT
            "AccountGroupID",
            "AccountGroupUnder",
            "AccountGroupName"
            FROM public.accountgroup_accountgroup
            WHERE
            "AccountGroupID"= 3 AND "CompanyID_id" = %(CompanyID)s
            UNION
            SELECT
            e."AccountGroupID",
            e."AccountGroupUnder",
            e."AccountGroupName"
            FROM
            public.accountgroup_accountgroup e
            INNER JOIN GroupInMainGroup s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = %(CompanyID)s
            )  
            SELECT "AccountGroupID", "AccountGroupName", SUM(Total) AS Total  
            FROM(  
            SELECT "AccountGroupID","AccountGroupName","LedgerID","LedgerName" ,  
            (SELECT ROUND(coalesce(SUM("Debit"), 0)- (coalesce(SUM("Credit"), 0)),2) 
            FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN %(FromDate)s AND %(ToDate)s )
            AND "BranchID" = %(BranchID)s AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
            AS Total FROM public."accountLedger_accountLedger" AL  
            INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
            WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup) AND AL."BranchID" = %(BranchID)s
            AND AL."CompanyID_id" = %(CompanyID)s
            ) AS TEMP WHERE Total != 0 GROUP BY "AccountGroupID", "AccountGroupName";
            ''',dic)
    elif VoucherType == "Liabilities":
        cursor.execute('''
            WITH RECURSIVE GroupInMainGroup AS (
            SELECT
            "AccountGroupID",
            "AccountGroupUnder",
            "AccountGroupName"
            FROM public.accountgroup_accountgroup
            WHERE
            "AccountGroupID"= 4 AND "CompanyID_id" = %(CompanyID)s
            UNION
            SELECT
            e."AccountGroupID",
            e."AccountGroupUnder",
            e."AccountGroupName"
            FROM
            public.accountgroup_accountgroup e
            INNER JOIN GroupInMainGroup s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = %(CompanyID)s
            )  
            SELECT "AccountGroupID", "AccountGroupName", SUM(Total) AS Total  
            FROM(  
            SELECT "AccountGroupID","AccountGroupName","LedgerID","LedgerName" ,  
            (SELECT ROUND(coalesce(SUM("Credit"), 0)- (coalesce(SUM("Debit"), 0)),2) 
            FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN %(FromDate)s AND %(ToDate)s )
            AND "BranchID" = %(BranchID)s AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
            AS Total FROM public."accountLedger_accountLedger" AL  
            INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
            WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup) AND AL."BranchID" = %(BranchID)s
            AND AL."CompanyID_id" = %(CompanyID)s
            ) AS TEMP WHERE Total != 0 GROUP BY "AccountGroupID", "AccountGroupName";
            ''',dic)
   
    data = cursor.fetchall()
    if cursor.rowcount == 0:
        data = [('','',0)]
    
    return data


def query_BalanceSheet_Detailed_data(key,CompanyID,BranchID,FromDate,ToDate,PriceRounding,VoucherType):
    cursor = connection.cursor()
    GroupID = ""
    dic = {'GroupID':GroupID,'PriceRounding':PriceRounding,'BranchID': BranchID, 'FromDate': FromDate,'ToDate':ToDate,'CompanyID':CompanyID}
    if VoucherType == 'Assets':
        cursor.execute('''
            WITH RECURSIVE GroupInMainGroup AS (
            SELECT
            "AccountGroupID",
            "AccountGroupUnder",
            "AccountGroupName"
            FROM public.accountgroup_accountgroup
            WHERE
            "AccountGroupID"= '3' AND "CompanyID_id" = %(CompanyID)s
            UNION
            SELECT
            e."AccountGroupID",
            e."AccountGroupUnder",
            e."AccountGroupName"
            FROM
            public.accountgroup_accountgroup e
            INNER JOIN GroupInMainGroup s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = %(CompanyID)s
            )  
            SELECT *  
            FROM(  
            SELECT "AccountGroupID","AccountGroupName","LedgerName" ,  
            (SELECT ROUND(coalesce(SUM("Debit"), 0)- (coalesce(SUM("Credit"), 0)),2) 
            FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN %(FromDate)s AND %(ToDate)s )
            AND "BranchID" = %(BranchID)s AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
            AS Total FROM public."accountLedger_accountLedger" AL  
            INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
            WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup) AND AL."BranchID" = %(BranchID)s
            AND AL."CompanyID_id" = %(CompanyID)s
            ) AS TEMP WHERE Total != 0;
        ''',dic)
    elif VoucherType == "Liabilities":
        cursor.execute('''
            WITH RECURSIVE GroupInMainGroup AS (
            SELECT
            "AccountGroupID",
            "AccountGroupUnder",
            "AccountGroupName"
            FROM public.accountgroup_accountgroup
            WHERE
            "AccountGroupID"= '4' AND "CompanyID_id" = %(CompanyID)s
            UNION
            SELECT
            e."AccountGroupID",
            e."AccountGroupUnder",
            e."AccountGroupName"
            FROM
            public.accountgroup_accountgroup e
            INNER JOIN GroupInMainGroup s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = %(CompanyID)s
            )  
            SELECT *  
            FROM(  
            SELECT "AccountGroupID","AccountGroupName","LedgerName" ,  
            (SELECT ROUND(coalesce(SUM("Credit"), 0)- (coalesce(SUM("Debit"), 0)),2) 
            FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN %(FromDate)s AND %(ToDate)s )
            AND "BranchID" = %(BranchID)s AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
            AS Total FROM public."accountLedger_accountLedger" AL  
            INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
            WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup) AND AL."BranchID" = %(BranchID)s
            AND AL."CompanyID_id" = %(CompanyID)s
            ) AS TEMP WHERE Total != 0;
        ''',dic)
    # ===========================CONSOLIDATED==============================
    

    data = cursor.fetchall()
    if cursor.rowcount == 0:
        data = [('','','',0)]

    
    return data


def FREEZ_query_BalanceSheet_NetLoss_or_NetProfit(ToDate,FromDate,BranchID,CompanyID,OpeningStock,ClosingStock):
    cursor = connection.cursor()
  
    dic = {'ClosingStock':ClosingStock,'OpeningStock':OpeningStock,'BranchID': BranchID, 'FromDate': FromDate,'ToDate':ToDate,'CompanyID':CompanyID}
    # ===========================BALANCE SHEET NETLOSS/NETPROFIT==============================
    # (ToDate Date,FromDate Date, BranchID bigint, CompanyID uuid,OPENINGSTOCK numeric,CLOSINGSTOCK numeric
    cursor.execute('''
       SELECT Profit(%(ToDate)s,%(FromDate)s,%(BranchID)s,%(CompanyID)s,%(OpeningStock)s,%(ClosingStock)s)
        ''',dic)

    data = cursor.fetchall()
    if cursor.rowcount == 0:
        data = [(0)]

    
    return data


def query_BalanceSheet_NetLoss_or_NetProfit(ToDate,FromDate,BranchID,CompanyID,OPENINGSTOCK,CLOSINGSTOCK):
  
    dic = {'BranchID': BranchID, 'FromDate': FromDate,'ToDate':ToDate,'CompanyID':CompanyID}
    # ===========================BALANCE SHEET NETLOSS/NETPROFIT==============================
    # ===============DIRECTEXPENCES================
    direct_expence_cursor = connection.cursor()
    direct_expence_cursor.execute('''
        WITH RECURSIVE GroupInMainGroup42 AS (
        SELECT
        "AccountGroupID",
        "AccountGroupUnder",
        "AccountGroupName"
        FROM public.accountgroup_accountgroup
        WHERE
        "AccountGroupID"= 42 AND "CompanyID_id" = %(CompanyID)s
        UNION
        SELECT
        e."AccountGroupID",
        e."AccountGroupUnder",
        e."AccountGroupName"
        FROM
        public.accountgroup_accountgroup e
        INNER JOIN GroupInMainGroup42 s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = %(CompanyID)s
        )  
        SELECT SUM(Total) as DIRECTEXPENCES 
        FROM(  
        SELECT   
        (SELECT ROUND(coalesce(SUM("Debit"), 0)- (coalesce(SUM("Credit"), 0)),2) 
        FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN %(FromDate)s AND %(ToDate)s )
        AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
        AS Total FROM public."accountLedger_accountLedger" AL  
        INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
        WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup42) AND AL."BranchID" = '1'
        AND AL."CompanyID_id" = %(CompanyID)s
        ) AS TEMP;
    ''',dic)

    direct_expence_data = direct_expence_cursor.fetchall()
    if direct_expence_cursor.rowcount == 0:
        direct_expence_data = [(0)]

    # ===============DIRECTINCOME================
    direct_income_cursor = connection.cursor()
    direct_income_cursor.execute('''
        WITH RECURSIVE GroupInMainGroup70 AS (
        SELECT
        "AccountGroupID",
        "AccountGroupUnder",
        "AccountGroupName"
        FROM public.accountgroup_accountgroup
        WHERE
            "AccountGroupID"= 70 AND "CompanyID_id" = %(CompanyID)s
        UNION
        SELECT
            e."AccountGroupID",
            e."AccountGroupUnder",
            e."AccountGroupName"
        FROM
            public.accountgroup_accountgroup e
        INNER JOIN GroupInMainGroup70 s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = %(CompanyID)s
        )  
        SELECT SUM(Total) as DIRECTINCOME 
        FROM(  
        SELECT 
        (SELECT ROUND(coalesce(SUM("Credit"), 0)- (coalesce(SUM("Debit"), 0)),2) 
        FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN %(FromDate)s AND %(ToDate)s )
        AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
        AS Total FROM public."accountLedger_accountLedger" AL  
        INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
        WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup70) AND AL."BranchID" = '1'
        AND AL."CompanyID_id" = %(CompanyID)s
        ) AS TEMP ;
    ''',dic)

    direct_income_data = direct_income_cursor.fetchall()
    if direct_income_cursor.rowcount == 0:
        direct_income_data = [(0)]

    # ===============INDIRECTEXPENCES================
    indirect_expence_cursor = connection.cursor()
    indirect_expence_cursor.execute('''
        WITH RECURSIVE GroupInMainGroup43 AS (
        SELECT
        "AccountGroupID",
        "AccountGroupUnder",
        "AccountGroupName"
        FROM public.accountgroup_accountgroup
        WHERE
        "AccountGroupID"= 43 AND "CompanyID_id" = %(CompanyID)s
        UNION
        SELECT
        e."AccountGroupID",
        e."AccountGroupUnder",
        e."AccountGroupName"
        FROM
        public.accountgroup_accountgroup e
        INNER JOIN GroupInMainGroup43 s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = %(CompanyID)s
        )  
        SELECT SUM(Total) as INDIRECTEXPENCES 
        FROM(  
        SELECT 
        (SELECT ROUND(coalesce(SUM("Debit"), 0)- (coalesce(SUM("Credit"), 0)),2) 
        FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN %(FromDate)s AND %(ToDate)s )
        AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
        AS Total FROM public."accountLedger_accountLedger" AL  
        INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
        WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup43) AND AL."BranchID" = '1'
        AND AL."CompanyID_id" = %(CompanyID)s
        ) AS TEMP ;
    ''',dic)

    indirect_expence_data = indirect_expence_cursor.fetchall()
    if indirect_expence_cursor.rowcount == 0:
        indirect_expence_data = [(0)]
    
     # ===============INDIRECTINCOME================
    indirect_income_cursor = connection.cursor()
    indirect_income_cursor.execute('''
        WITH RECURSIVE GroupInMainGroup71 AS (
        SELECT
        "AccountGroupID",
        "AccountGroupUnder",
        "AccountGroupName"
        FROM public.accountgroup_accountgroup
        WHERE
            "AccountGroupID"= 71 AND "CompanyID_id" = %(CompanyID)s
        UNION
        SELECT
            e."AccountGroupID",
            e."AccountGroupUnder",
            e."AccountGroupName"
        FROM
            public.accountgroup_accountgroup e
        INNER JOIN GroupInMainGroup71 s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = %(CompanyID)s
        )  
        SELECT SUM(Total) as INDIRECTINCOME 
        FROM(  
        SELECT 
        (SELECT ROUND(coalesce(SUM("Credit"), 0)- (coalesce(SUM("Debit"), 0)),2) 
        FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN %(FromDate)s AND %(ToDate)s )
        AND "BranchID" = '1' AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
        AS Total FROM public."accountLedger_accountLedger" AL  
        INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
        WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup71) AND AL."BranchID" = '1'
        AND AL."CompanyID_id" = %(CompanyID)s
        ) AS TEMP;
    ''',dic)

    indirect_income_data = indirect_income_cursor.fetchall()
    if indirect_income_cursor.rowcount == 0:
        indirect_income_data = [(0)]

    DIRECTEXPENCES = direct_expence_data[0][0]
    INDIRECTEXPENCES = indirect_expence_data[0][0]
    DIRECTINCOME = direct_income_data[0][0]
    INDIRECTINCOME = indirect_income_data[0][0]
    GrossLoss = 0
    GrossProfit = 0

    DIRECTEXPENCES = DIRECTEXPENCES + OPENINGSTOCK
    DIRECTINCOME = DIRECTINCOME + CLOSINGSTOCK

    if DIRECTEXPENCES > DIRECTINCOME:  
        GrossLoss = DIRECTEXPENCES - DIRECTINCOME
        DIRECTINCOME = GrossProfit + DIRECTINCOME
    elif DIRECTEXPENCES < DIRECTINCOME:
        GrossProfit = DIRECTINCOME - DIRECTEXPENCES
        DIRECTEXPENCES = GrossProfit + DIRECTEXPENCES
    INDIRECTEXPENCES = GrossLoss + INDIRECTEXPENCES
    INDIRECTINCOME = GrossProfit + INDIRECTINCOME
    
    if INDIRECTEXPENCES <= INDIRECTINCOME:
        NetProfit =  INDIRECTINCOME - INDIRECTEXPENCES
        return NetProfit
    elif INDIRECTEXPENCES > INDIRECTINCOME:  
        NetLoss = INDIRECTEXPENCES - INDIRECTINCOME
        return NetLoss * -1


def query_Expense_summary(CompanyID,BranchIDs,FromDate,ToDate,PriceRounding):
    cursor = connection.cursor()
    dic = {'PriceRounding':PriceRounding,'BranchIDs': BranchIDs, 'FromDate': FromDate,'ToDate':ToDate,'CompanyID':CompanyID}
    if BranchIDs:
        cursor.execute('''
                WITH RECURSIVE GroupInMainGroup43 AS (
                SELECT
                "AccountGroupID",
                "AccountGroupUnder",
                "AccountGroupName"
                FROM public.accountgroup_accountgroup
                WHERE
                "AccountGroupID"= 43 AND "CompanyID_id" = %(CompanyID)s
                UNION
                SELECT
                e."AccountGroupID",
                e."AccountGroupUnder",
                e."AccountGroupName"
                FROM
                public.accountgroup_accountgroup e
                INNER JOIN GroupInMainGroup43 s ON s."AccountGroupID" = e."AccountGroupUnder" AND e."CompanyID_id" = %(CompanyID)s
                )       
                SELECT *
                FROM(  
                SELECT "LedgerName" ,  
                (SELECT ROUND(coalesce(SUM("Debit"), 0)- (coalesce(SUM("Credit"), 0)),2) 
                FROM public."ledgerPostings_ledgerPosting" WHERE ("Date" BETWEEN %(FromDate)s AND %(ToDate)s )
                AND "BranchID" IN %(BranchIDs)s AND "LedgerID" = AL."LedgerID" AND AL."CompanyID_id" = "CompanyID_id")--GROUP BY LedgerID       
                AS Total FROM public."accountLedger_accountLedger" AL  
                INNER JOIN public."accountgroup_accountgroup" AS A ON AL."AccountGroupUnder" = A."AccountGroupID" AND AL."CompanyID_id" = A."CompanyID_id" 
                WHERE AL."AccountGroupUnder" IN (SELECT "AccountGroupID" FROM GroupInMainGroup43) AND AL."BranchID" = '1'
                AND AL."CompanyID_id" = %(CompanyID)s
                ) AS TEMP WHERE Total != 0;

            ''',dic)

        data = cursor.fetchall()
    else:
        data = [('Please Select a Branch',0)]

    if cursor.rowcount == 0:
        data = [('No Data',0)]
    
    df = pd.DataFrame(data)

    # adding Total in laast Row to data frame
    df.loc[len(df.index)] = df[[1]].sum().reindex(
        df.columns, fill_value='')

    # adding Heading to frame
    df.columns = [
        str(_('LedgerName')), str(_('Amount'))]
        
    df.at[len(df.index)-1, 'LedgerName'] = "Total"


    # convert date format(millisecond) to str in dataframe
    json_records = df.reset_index().to_json(orient='records')
    details = json.loads(json_records)
    return df,details


