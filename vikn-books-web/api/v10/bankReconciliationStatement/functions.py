import random
import string
from decimal import Decimal

import pandas as pd
import xlwt
from django.db.models import Max, Prefetch, Q, Sum
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from xlwt import Alignment, Borders, Font, Pattern, Workbook, XFStyle, easyxf

from api.v10.bankReconciliationStatement import serializers
from api.v10.reportQuerys.functions import (
    query_closingBalance_data,
    query_openingBalance_data,
)
from brands import models


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
    autoid = 1
    if model.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        current_id = (
            model.objects.filter(CompanyID=CompanyID, BranchID=BranchID)
            .order_by("BankReconciliationMasterID")
            .last()
            .BankReconciliationMasterID
        )
        autoid = int(current_id) + 1
    return autoid


def get_auto_idDetail(model, BranchID, CompanyID):
    autoid = 1
    if model.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        current_id = (
            model.objects.filter(CompanyID=CompanyID, BranchID=BranchID)
            .order_by("BankReconciliationDetailsID")
            .last()
            .BankReconciliationDetailsID
        )
        autoid = int(current_id) + 1
    return autoid


def get_timezone(request):
    if "set_user_timezone" in request.session:
        user_time_zone = request.session["set_user_timezone"]
    else:
        user_time_zone = "Asia/Riyadh"
    return user_time_zone


def bank_reconslation_date(
    CompanyID, LedgerID, BranchID, FromDate, ToDate, PriceRounding
):
    print(CompanyID, LedgerID, BranchID, FromDate, ToDate, PriceRounding)
    if models.LedgerPosting.objects.filter(
        CompanyID=CompanyID,
        BranchID=BranchID,
        LedgerID=LedgerID,
        VoucherType__in=["BR", "BP", "SI", "SR", "PI", "PR", "CP", "CR"],
        Date__lte=ToDate,
    ).exists():
        instance = models.LedgerPosting.objects.filter(
            CompanyID=CompanyID,
            BranchID=BranchID,
            LedgerID=LedgerID,
            VoucherType__in=["BR", "BP", "SI", "SR", "PI", "PR", "CP", "CR"],
            Date__gte=FromDate,
            Date__lte=ToDate,
        )
        unmatched_instance = instance.filter(IsReconciliated=False)
        matched_instance = instance.filter(IsReconciliated=True)
        total_matched_values = 0
        total_unmatched_values = 0
        print(unmatched_instance, "unmatched_instance")
        print(matched_instance, "matched_instance")
        if matched_instance:
            # Matched Transactions
            total_matched_debit = matched_instance.aggregate(Sum("Debit"))
            total_matched_credit = matched_instance.aggregate(Sum("Credit"))
            if total_matched_debit:
                total_matched_debit = total_matched_debit["Debit__sum"]
            if total_matched_credit:
                total_matched_credit = total_matched_credit["Credit__sum"]
            total_matched_values = total_matched_debit - total_matched_credit
        matched_serialized = serializers.BankReconciliationReportSerializer(
            matched_instance, many=True, context={"CompanyID": CompanyID}
        )
        if unmatched_instance:
            # UnMatched Transactions
            total_unmatched_debit = unmatched_instance.aggregate(Sum("Debit"))
            total_unmatched_credit = unmatched_instance.aggregate(Sum("Credit"))
            if total_unmatched_debit:
                total_unmatched_debit = total_unmatched_debit["Debit__sum"]
            if total_unmatched_credit:
                total_unmatched_credit = total_unmatched_credit["Credit__sum"]
            total_unmatched_values = total_unmatched_debit - total_unmatched_credit
        unmatched_serialized = serializers.BankReconciliationReportSerializer(
            unmatched_instance, many=True, context={"CompanyID": CompanyID}
        )
        # OpeningBalance===========
        opening_stock_balance = query_openingBalance_data(
            CompanyID,
            BranchID,
            FromDate,
            ToDate,
            PriceRounding,
            LedgerID,
            "",
        )
        op_balance_row = pd.DataFrame(opening_stock_balance, index=[0])
        # calculating Debit and Credit with opening balance
        op_balance = 0
        if op_balance_row.at[0, 7]:
            op_balance = round(op_balance_row.at[0, 7], PriceRounding)
        # closingBalance===========
        closing_balance = query_closingBalance_data(
            CompanyID,
            BranchID,
            FromDate,
            ToDate,
            PriceRounding,
            LedgerID,
            "",
        )
        clos_balance_row = pd.DataFrame(closing_balance, index=[0])
        # calculating Debit and Credit with closing balance
        clos_balance = 0
        if clos_balance_row.at[0, 7]:
            clos_balance = round(clos_balance_row.at[0, 7], PriceRounding)
        # Reconsiliation status summary
        reconsiliation_status_summary = {
            "OpeningBalance": op_balance,
            "ClosingBalance": clos_balance,
            "total_value_of_matched_transactions_for_this_period": total_matched_values,
            "total_value_of_unmatched_statements": total_unmatched_values,
            "total_value_of_unmatched_statements_in_viknbooks": 0,
        }
        response_data = {
            "StatusCode": 6000,
            "reconsiliation_status_summary": reconsiliation_status_summary,
            "matched_transactions": matched_serialized.data,
            "unmatched_transactions": unmatched_serialized.data,
        }

        return response_data
    else:
        response_data = {"StatusCode": 6001, "message": "datas not found!"}
        return response_data


def export_to_excel_bank_reconslation(wb, data, FromDate, ToDate, title, columns, Type):
    ws = wb.add_sheet("Reconciliation Report")

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
    total_values_style.num_format_str = "0.00"
    total_values_style.font = font

    total_label_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True
    font.colour_index = 10
    total_label_style.font = font

    value_decimal_style = xlwt.XFStyle()
    value_decimal_style.num_format_str = "0.00"

    main_title = xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True
    main_title.font = font
    main_title.alignment = center

    ws.write_merge(0, 0, 0, 3, title, main_title)

    print(data)
    print(
        "(((((((((((((((((((((((((**********BankReconslation*******)))))))))))))))))))))))))"
    )
    try:
        reconsiliation_status_summary = data["reconsiliation_status_summary"]
    except:
        reconsiliation_status_summary = []

    try:
        matched_transactions = data["matched_transactions"]
    except:
        matched_transactions = []

    try:
        unmatched_transactions = data["unmatched_transactions"]
    except:
        unmatched_transactions = []
    if Type == 2:
        details = matched_transactions
    elif Type == 3:
        details = unmatched_transactions
    if Type == 2 or Type == 3:
        row_num = 1
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], sub_header_style)

        data_row = 2
        for j in details:

            try:
                Date = j["Date"]
            except:
                Date = "-"
            try:
                TransactionType = j["TransactionType"]
            except:
                TransactionType = "-"
            try:
                Reference = j["Reference"]
            except:
                Reference = "-"
            try:
                RelativeLedgerName = j["RelativeLedgerName"]
            except:
                RelativeLedgerName = "-"
            try:
                Debit = j["Debit"]
            except:
                Debit = 0
            try:
                Credit = j["Credit"]
            except:
                Credit = 0

            ws.write(data_row, 0, Date)
            ws.write(data_row, 1, Reference)

            ws.write(data_row, 2, TransactionType)

            ws.write(data_row, 3, RelativeLedgerName, value_decimal_style)
            ws.write(data_row, 4, float(Debit), value_decimal_style)
            ws.write(data_row, 5, float(Credit), value_decimal_style)
            data_row += 1
    else:
        try:
            OpeningBalance = reconsiliation_status_summary["OpeningBalance"]
        except:
            OpeningBalance = "-"
        try:
            ClosingBalance = reconsiliation_status_summary["ClosingBalance"]
        except:
            ClosingBalance = "-"
        try:
            total_value_of_matched = reconsiliation_status_summary[
                "total_value_of_matched_transactions_for_this_period"
            ]
        except:
            total_value_of_matched = "-"
        try:
            total_value_of_unmatched = reconsiliation_status_summary[
                "total_value_of_unmatched_statements"
            ]
        except:
            total_value_of_unmatched = "-"
        ws.write_merge(1, 1, 0, 3, "Opening Balance")
        ws.write_merge(2, 2, 0, 3, "Closing Balance")
        ws.write_merge(
            3, 3, 0, 3, "Total value of matched transactions for this period"
        )
        ws.write_merge(
            4, 4, 0, 3, "Total Value of Unmatched statements as on 17/08/2021"
        )

        ws.write(1, 4, OpeningBalance)
        ws.write(2, 4, ClosingBalance)
        ws.write(3, 4, total_value_of_matched)
        ws.write(4, 4, total_value_of_unmatched)
