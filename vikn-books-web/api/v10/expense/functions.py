import string
import random
from django.http import HttpResponse
from decimal import Decimal
from django.db.models import Max
import xlwt
from xlwt import Workbook, XFStyle, Borders, Pattern, Font, easyxf, Alignment
from brands.models import ExpenseMaster,ExpenseDetails, Parties,TaxCategory
from django.utils.translation import gettext_lazy as _

from main.functions import converted_float

def generate_serializer_errors(args):
    message = ""
    for key, values in args.items():
        error_message = ""
        for value in values:
            error_message += value + ","
        error_message = error_message[:-1]

        message += "%s : %s | " %(key,error_message)
    return message[:-3]


def get_masterID(model,BranchID,CompanyID):
    ExpenseMasterID = 1
    latest_auto_id =  model.objects.all().aggregate(Max('ExpenseMasterID'))
    if model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).exists():
        max_value =  model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).aggregate(Max('ExpenseMasterID'))
        if max_value:
            max_ExpenseMasterID = max_value.get('ExpenseMasterID__max', 0)
            ExpenseMasterID = max_ExpenseMasterID + 1
        else:
            ExpenseMasterID = 1
    return ExpenseMasterID


def get_detailID(model,BranchID,CompanyID):
    ExpenseDetailsID = 1
    latest_auto_id =  model.objects.all().aggregate(Max('ExpenseDetailsID'))
    if model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).exists():
        max_value =  model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).aggregate(Max('ExpenseDetailsID'))
        if max_value:
            max_ExpenseDetailsID = max_value.get('ExpenseDetailsID__max', 0)
            ExpenseDetailsID = max_ExpenseDetailsID + 1
        else:
            ExpenseDetailsID = 1
    return ExpenseDetailsID



def expence_excel_data(CompanyID,BranchID,FromDate,ToDate,PriceRounding,CashLedgers,):
    LedgerList = CashLedgers 
    if ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
        instances = ExpenseMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)

        final_data = []
        new_final_data = []
        tot_IGSTAmount = 0
        tot_SGSTAmount = 0
        tot_CGSTAmount = 0
        tot_Discount = 0
        tot_Amount = 0
        tot_NetAmount = 0
        for i in instances:
            ExpenseMasterID = i.ExpenseMasterID
            Particulars = i.Supplier.LedgerName
            LedgerID = i.Supplier.LedgerID
            TaxNumber = ""
            if Parties.objects.filter(CompanyID_id=CompanyID, BranchID=BranchID).exists():
                party_instance = Parties.objects.get(CompanyID=CompanyID, BranchID=BranchID,LedgerID=LedgerID)
                if party_instance.CompanyID.Country.Country_Name == "India":
                    TaxNumber = party_instance.GSTNumber
                else:
                    TaxNumber = party_instance.VATNumber

            if ExpenseDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).exists():
                if LedgerList:
                    detail_ins = ExpenseDetails.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID, Ledger__LedgerID__in=LedgerList)
                else:
                    detail_ins = ExpenseDetails.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID)
                for l in detail_ins:
                    TaxType = "-"
                    if TaxCategory.objects.filter(CompanyID=CompanyID,TaxID=l.TaxID).exists():
                        TaxType = TaxCategory.objects.get(CompanyID=CompanyID,TaxID=l.TaxID).TaxName
                    LedgerName = l.Ledger.LedgerName
                    
                    
                    
                    virtual_dictionary = {"VoucherNo": i.VoucherNo, "Date": i.Date, "LedgerName": LedgerName, "TaxNumber": TaxNumber,
                                            "VATAmount": l.VATAmount,"IGSTAmount": l.IGSTAmount,"SGSTAmount": l.SGSTAmount,"CGSTAmount": l.CGSTAmount,"TaxType": TaxType,"Particulars": Particulars,"Amount": l.Amount, "Discount": l.DiscountAmount, "NetAmount": l.NetTotal}
                    tot_Discount += l.DiscountAmount
                    tot_Amount += l.Amount
                    tot_NetAmount += l.NetTotal
                    tot_IGSTAmount += l.IGSTAmount
                    tot_SGSTAmount += l.SGSTAmount
                    tot_CGSTAmount += l.CGSTAmount
                    final_data.append(virtual_dictionary)
                    new_final_data.append(virtual_dictionary)

        # append Total new New array
        tot_dictionary = {"VoucherNo": "Total", "Date": "", "LedgerName": "",
                            "TaxType": "","TaxNumber": "", "IGSTAmount": tot_IGSTAmount,"SGSTAmount": tot_SGSTAmount,"CGSTAmount": tot_CGSTAmount,"Amount": tot_Amount, "Discount": tot_Discount, "NetAmount": tot_NetAmount, "Narration": ""}
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
                "message": "Expense details not found!"
            }
            return response_data
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Expense details not found!"
        }
        return response_data


def export_to_excel_expence(wb, data, FromDate, ToDate, title,columns):
    ws = wb.add_sheet("Expence Report")

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
        data_list = data
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
            Particulars = j['Particulars']
        except:
            Particulars = '-'
        try:
            TaxNumber = j['TaxNumber']
        except:
            TaxNumber = '-'
        try:
            VATAmount = j['VATAmount']
        except:
            VATAmount = 0
        try:
            IGSTAmount = j['IGSTAmount']
        except:
            IGSTAmount = 0
        try:
            SGSTAmount = j['SGSTAmount']
        except:
            SGSTAmount = 0
        try:
            CGSTAmount = j['CGSTAmount']
        except:
            CGSTAmount = 0
        try:
            Amount = j['Amount']
        except:
            Amount = 0
        try:
            Discount = j['Discount']
        except:
            Discount = 0
        try:
            NetAmount = j['NetAmount']
        except:
            NetAmount = 0

        ws.write(data_row, 0, VoucherNo)
        ws.write(data_row, 1, Date)
        if LedgerName == "Total":
            ws.write(data_row, 2, LedgerName, total_label_style)
        else:
            ws.write(data_row, 2, LedgerName)

        ws.write(data_row, 3, Particulars, value_decimal_style)
        ws.write(data_row, 4, TaxNumber, value_decimal_style)
        ws.write(data_row, 5, converted_float(VATAmount), value_decimal_style)
        ws.write(data_row, 6, converted_float(IGSTAmount), value_decimal_style)
        ws.write(data_row, 7, converted_float(SGSTAmount), value_decimal_style)
        ws.write(data_row, 8, converted_float(CGSTAmount), value_decimal_style)
        ws.write(data_row, 9, converted_float(Amount), value_decimal_style)
        ws.write(data_row, 10, converted_float(Discount), value_decimal_style)
        ws.write(data_row, 11, converted_float(NetAmount), value_decimal_style)
        data_row += 1

