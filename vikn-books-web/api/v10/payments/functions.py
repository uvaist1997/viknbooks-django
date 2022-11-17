import string
import random
from django.http import HttpResponse
from decimal import Decimal
from django.db.models import Max
from api.v10.receipts.functions import get_voucher_type
from brands.models import AccountLedger, PaymentDetails, PaymentMaster
import xlwt
from xlwt import Workbook, XFStyle, Borders, Pattern, Font, easyxf, Alignment


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
    PaymentMasterID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id = model.objects.filter(
        CompanyID=CompanyID).aggregate(Max('PaymentMasterID'))

    if model.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        max_value = model.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID).aggregate(Max('PaymentMasterID'))

        if max_value:
            max_paymentMasterId = max_value.get('PaymentMasterID__max', 0)

            PaymentMasterID = max_paymentMasterId + 1

        else:
            PaymentMasterID = 1

    return PaymentMasterID


def get_auto_id(model, BranchID, CompanyID):
    PaymentDetailsID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id = model.objects.filter(
        CompanyID=CompanyID).aggregate(Max('PaymentDetailsID'))

    if model.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        max_value = model.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID).aggregate(Max('PaymentDetailsID'))

        if max_value:
            max_paymentDetailsId = max_value.get('PaymentDetailsID__max', 0)

            PaymentDetailsID = max_paymentDetailsId + 1

        else:
            PaymentDetailsID = 1

    return PaymentDetailsID


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


def paymentReport_excel_data(CompanyID, BranchID, PriceRounding, VoucherType, LedgerList, FromDate, ToDate):
    if PaymentMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType, Date__gte=FromDate, Date__lte=ToDate).exists():
        instances = PaymentMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType, Date__gte=FromDate, Date__lte=ToDate)
        final_data = []
        new_final_data = []
        tot_Discount = 0
        tot_Amount = 0
        tot_NetAmount = 0
        for i in instances:
            PaymentMasterID = i.PaymentMasterID
            if PaymentDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID).exists():
                if PaymentDetails.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID, LedgerID__in=LedgerList).exists():
                    detail_ins = PaymentDetails.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID, LedgerID__in=LedgerList)
                else:
                    detail_ins = PaymentDetails.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID)
                for l in detail_ins:
                    LedgerName = AccountLedger.objects.get(
                        CompanyID=CompanyID, BranchID=BranchID, LedgerID=l.LedgerID).LedgerName
                    voucher_type = get_voucher_type(i.VoucherType)
                    virtual_dictionary = {"VoucherNo": i.VoucherNo, "Date": i.Date, "LedgerName": LedgerName,
                                          "VoucherType": voucher_type, "Amount": l.Amount, "Discount": l.Discount, "NetAmount": l.NetAmount, "Narration": l.Narration}
                    tot_Discount += l.Discount
                    tot_Amount += l.Amount
                    tot_NetAmount += l.NetAmount
                    final_data.append(virtual_dictionary)
                    new_final_data.append(virtual_dictionary)

        # append Total new New array
        tot_dictionary = {"VoucherNo": "Total", "Date": "", "LedgerName": "",
                          "VoucherType": "", "Amount": tot_Amount, "Discount": tot_Discount, "NetAmount": tot_NetAmount, "Narration": ""}
        new_final_data.append(tot_dictionary)
        if final_data and new_final_data:
            response_data = {
                "StatusCode": 6000,
                "data": final_data,
                "new_data": new_final_data,
                "total": tot_dictionary,
            }
            return response_data
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Receipt details not found!"
            }
            return response_data

    elif PaymentMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists() and VoucherType == "All":
        instances = PaymentMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)

        final_data = []
        new_final_data = []
        tot_Discount = 0
        tot_Amount = 0
        tot_NetAmount = 0
        for i in instances:
            PaymentMasterID = i.PaymentMasterID
            if PaymentDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID).exists():
                if LedgerList:
                    detail_ins = PaymentDetails.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID, LedgerID__in=LedgerList)
                else:
                    detail_ins = PaymentDetails.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID)
                for l in detail_ins:
                    LedgerName = AccountLedger.objects.get(
                        CompanyID=CompanyID, BranchID=BranchID, LedgerID=l.LedgerID).LedgerName
                    voucher_type = get_voucher_type(i.VoucherType)
                    virtual_dictionary = {"VoucherNo": i.VoucherNo, "Date": i.Date, "LedgerName": LedgerName,
                                          "VoucherType": voucher_type, "Amount": l.Amount, "Discount": l.Discount, "NetAmount": l.NetAmount, "Narration": l.Narration}
                    tot_Discount += l.Discount
                    tot_Amount += l.Amount
                    tot_NetAmount += l.NetAmount
                    final_data.append(virtual_dictionary)
                    new_final_data.append(virtual_dictionary)

        # append Total new New array
        tot_dictionary = {"VoucherNo": "Total", "Date": "", "LedgerName": "",
                          "VoucherType": "", "Amount": tot_Amount, "Discount": tot_Discount, "NetAmount": tot_NetAmount, "Narration": ""}
        new_final_data.append(tot_dictionary)
        if final_data and new_final_data:
            response_data = {
                "StatusCode": 6000,
                "data": final_data,
                "new_data": new_final_data,
                "total": tot_dictionary,
            }
            return response_data
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Receipt details not found!"
            }
            return response_data
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Receipt details not found!"
        }
        return response_data


def export_to_excel_paymentReport(wb, data, title):
    ws = wb.add_sheet("Payment Report")
    print(data, "*************************************8")
    # write column headers in sheet

    # xl sheet styles
    # column value alighn center
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    # header font
    font = xlwt.Font()
    font.bold = True
    # font.height = 11 * 20

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

    main_title = xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True
    main_title.font = font
    main_title.alignment = center

    value_decimal_style = xlwt.XFStyle()
    value_decimal_style.num_format_str = '0.00'

    data_col = 0
    data_row = 1
    SlNo = 0

    ws.write_merge(0, 0, 0, 8, title, main_title)

    columns = ['SlNo', 'Voucher No', 'Date', 'Ledger Name', 'Voucher Type',
               'Amount', 'Discount', 'Net Amount', 'Narration']
    row_num = 1
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], sub_header_style)

    data_col = 0
    data_row = 2
    SlNo = 0

    for j in data['new_data']:
        VoucherNo = j['VoucherNo']
        Date = j['Date']
        LedgerName = j['LedgerName']
        VoucherType = j['VoucherType']
        Amount = j['Amount']
        Discount = j['Discount']
        NetAmount = j['NetAmount']
        Narration = j['Narration']
        try:
            Date = Date.strftime("%m/%d/%Y")
        except:
            Date = ""

        print(type(Date), Date, 'DateDateDateDate')
        SlNo += 1

        ws.write(data_row, 0, SlNo)
        if VoucherNo == "Total":
            ws.write(data_row, 1, VoucherNo, total_label_style)
        else:
            ws.write(data_row, 1, VoucherNo)
        ws.write(data_row, 2, Date)
        ws.write(data_row, 3, LedgerName)
        ws.write(data_row, 4, VoucherType)
        ws.write(data_row, 5, Amount, value_decimal_style)
        ws.write(data_row, 6, Discount, value_decimal_style)
        ws.write(data_row, 7, NetAmount, value_decimal_style)
        ws.write(data_row, 8, Narration)
        data_row += 1
