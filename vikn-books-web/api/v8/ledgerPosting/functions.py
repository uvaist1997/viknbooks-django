import string
import random
from django.http import HttpResponse
from decimal import Decimal
from django.db.models import Max
from json import loads, dumps
import xlwt
from django.db.models import Sum
from django.db.models import F
from itertools import chain, groupby
from operator import itemgetter
from xlwt import Workbook, XFStyle, Borders, Pattern, Font, easyxf, Alignment
from api.v8.salesReturns.serializers import SalesReturnMasterRestSerializer, SalesReturnMasterReportSerializer
from brands.models import LedgerPosting, LedgerPosting_Log, AccountLedger, AccountGroup, StockRate, StockPosting, Product, FinancialYear, PriceList,\
    CompanySettings, Parties, PaymentMaster, ReceiptMaster, SalesMaster, PurchaseMaster, SalesReturnMaster, PurchaseReturnMaster, SalesMaster_Log,\
    PurchaseMaster_Log, SalesReturnMaster_Log, PurchaseReturnMaster_Log, PaymentMaster_Log, ReceiptMaster_Log
from api.v8.ledgerPosting.serializers import LedgerPostingSerializer, LedgerPostingRestSerializer, ListSerializerforTrialBalance,\
    TrialBalanceSerializer, ListSerializerforLedgerReport, LedgerReportAllSerializer, LedgerReportGroupSerializer, ListSerializerforProfitAndLoss, ProfitAndLossSerializer,\
    BalanceSheetSerializer, LedgerReportLedgerWiseSerializer, StockReportSerializer, LedgerReportSerializer
from api.v8.companySettings.serializers import CompanySettingsRestSerializer
import itertools


def generate_serializer_errors(args):
    message = ""
    for key, values in args.items():
        error_message = ""
        for value in values:
            error_message += value + ","
        error_message = error_message[:-1]

        message += "%s : %s | " % (key, error_message)
    return message[:-3]


def get_auto_id(model, BranchID, DataBase):
    LedgerPostingID = 1
    max_value = None
    LedgerPostingID = None
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id = model.objects.filter(
        CompanyID=CompanyID).aggregate(Max('LedgerPostingID'))

    if model.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        max_value = model.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID).aggregate(Max('LedgerPostingID'))

        if max_value:
            max_ledgerPostingId = max_value.get('LedgerPostingID__max', 0)

            LedgerPostingID = max_ledgerPostingId + 1

        else:
            LedgerPostingID = 1

    return LedgerPostingID


def convertOrderdDict(input_ordered_dict):
    return loads(dumps(input_ordered_dict))


def get_VoucherName(VoucherType):
    if VoucherType == 'SI':
        VoucherName = 'Sales Invoice'
    elif VoucherType == 'SR':
        VoucherName = 'Sales Return'
    elif VoucherType == 'SO':
        VoucherName = 'Sales Order'
    elif VoucherType == 'PI':
        VoucherName = 'Purchase Invoice'
    elif VoucherType == 'PR':
        VoucherName = 'Purchase Return'
    elif VoucherType == 'PO':
        VoucherName = 'Purchase Order'
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

    return VoucherName


def ledgerReport_excel_data(CompanyID, CreatedUserID, PriceRounding, BranchID, FromDate, ToDate, ID, value, ManualOpeningBalance):
    try:
        ManualOpeningBalance = ManualOpeningBalance
    except:
        ManualOpeningBalance = ""

    print(ManualOpeningBalance)

    if LedgerPosting.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():

        test_arr = []
        print('=====', ID, "><-------------------------------------------><")
        if ID == 0:
            print('=====', ID, "><00000000><")
            instances = LedgerPosting.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID, Date__lte=ToDate).order_by('Date', 'LedgerPostingID')
            ledger_ids = instances.values_list('LedgerID')
            for ledger_id in ledger_ids:
                if ledger_id[0] not in test_arr:
                    test_arr.append(ledger_id[0])

            account_ledger = AccountLedger.objects.filter(
                CompanyID=CompanyID, LedgerID__in=test_arr)
            serialized = LedgerReportAllSerializer(account_ledger, many=True, context={
                                                   "CompanyID": CompanyID, "PriceRounding": PriceRounding})

            orderdDict = serialized.data
            jsnDatas = convertOrderdDict(orderdDict)

            for i in jsnDatas:
                Debit = i['Debit']
                Credit = i['Credit']

                Balance = float(Debit) - float(Credit)

                i['Balance'] = round(Balance, PriceRounding)
            if jsnDatas:
                response_data = {
                    "StatusCode": 6000,
                    "data": jsnDatas,
                }
                return response_data
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "No Datas with this Ledger during this date!"
                }
                return response_data
        elif ID == 1:
            print('=====', ID, "><111111111111111><")

            instances = LedgerPosting.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID).order_by('Date', 'LedgerPostingID')
            virtual_array = []
            last_data = []
            ob_array = []
            Balance = 0
            if ManualOpeningBalance:
                Balance = ManualOpeningBalance
            OpeningBalance = 0
            if instances.filter(CompanyID=CompanyID, LedgerID=value).exists():
                if ManualOpeningBalance:
                    instances = instances.filter(
                        CompanyID=CompanyID, LedgerID=value, Date__gte=FromDate, Date__lte=ToDate).order_by('Date', 'LedgerPostingID')
                else:
                    instances = instances.filter(
                        CompanyID=CompanyID, LedgerID=value).order_by('Date', 'LedgerPostingID')

                serialized = LedgerReportLedgerWiseSerializer(instances, many=True, context={
                                                              "CompanyID": CompanyID, "PriceRounding": PriceRounding})

                orderdDict = serialized.data
                jsnDatas = convertOrderdDict(orderdDict)

                for i in jsnDatas:
                    Unq_id = i['Unq_id']
                    Debit = i['Debit']
                    Credit = i['Credit']
                    LedgerID = i['LedgerID']
                    LedgerName = i['LedgerName']
                    RelatedLedgerName = i['RelatedLedgerName']
                    VoucherType = i['VoucherType']
                    VoucherNo = i['VoucherNo']
                    Date = i['Date']
                    Balance = (float(Balance) + float(Debit)) - \
                        float(Credit)

                    i['Balance'] = round(Balance, PriceRounding)
                    Debit = float(Debit)
                    Credit = float(Credit)

                    virtual_dictionary = {"Unq_id": Unq_id, "Debit": round(Debit, PriceRounding), "Credit": round(Credit, PriceRounding), "LedgerID": LedgerID, "LedgerName": LedgerName,
                                          "RelatedLedgerName": RelatedLedgerName, "VoucherType": VoucherType, "VoucherNo": VoucherNo, "Date": Date, "Balance": round(Balance, PriceRounding)}

                    virtual_array.append(virtual_dictionary)

                for i in virtual_array:
                    date = i["Date"]
                    if FromDate > date:
                        ob_array.append(i)
                    if FromDate <= date and ToDate >= date:
                        last_data.append(i)

                if ManualOpeningBalance:
                    OpeningBalance = ManualOpeningBalance
                else:
                    if ob_array:
                        last_dict = ob_array[-1]
                        OpeningBalance = last_dict['Balance']

                # if last_data:
                TotalDebit = 0
                TotalCredit = 0
                TotalBalance = 0
                for data in last_data:
                    TotalDebit += data['Debit']
                    TotalCredit += data['Credit']
                    # TotalBalance += data['Balance']

                Opening_type = ""
                if float(OpeningBalance) > 0:
                    Opening_type = "Dr"
                    TotalDebit = float(TotalDebit) + float(OpeningBalance)
                elif float(OpeningBalance) < 0:
                    Opening_type = "Cr"
                    TotalCredit = float(TotalCredit) + \
                        float(OpeningBalance)
                TotalBalance = float(TotalDebit) - float(TotalCredit)
                total = {
                    "Opening_date": FromDate,
                    "Opening_type": Opening_type,
                    "OpeningBalance": OpeningBalance,
                    "TotalDebit": round(TotalDebit, PriceRounding),
                    "TotalCredit": round(TotalCredit, PriceRounding),
                    "TotalBalance": round(TotalBalance, PriceRounding),
                }
                response_data = {
                    "StatusCode": 6000,
                    "data": last_data,
                    "total": total,
                    "OpeningBalance": OpeningBalance,
                    "TotalDebit": round(TotalDebit, PriceRounding),
                    "TotalCredit": round(TotalCredit, PriceRounding),
                    "TotalBalance": round(TotalBalance, PriceRounding),
                }
                return response_data
                # else:
                #     response_data = {
                #         "StatusCode": 6001,
                #         "message": "No Datas with this Ledger during this date!"
                #     }
                #     return response_data
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "No Datas with this Ledger!"
                }
                return response_data
        elif ID == 2:

            instances = LedgerPosting.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID).order_by('Date', 'LedgerPostingID')
            virtual_array = []
            last_data = []
            ob_array = []
            Balance = 0
            OpeningBalance = 0
            # instances = instances.filter(
            #     CompanyID=CompanyID, Date__gte=FromDate, Date__lte=ToDate).order_by('Date')
            serialized = LedgerReportGroupSerializer(instances, many=True, context={
                                                     'value': value, "CompanyID": CompanyID, "PriceRounding": PriceRounding})

            orderdDict = serialized.data
            jsnDatas = convertOrderdDict(orderdDict)

            filtered_array = []

            for i in jsnDatas:
                Debit = i['Debit']
                Credit = i['Credit']
                LedgerName = i['LedgerName']
                LedgerID = i['LedgerID']
                GroupUnder = i['GroupUnder']
                Date = i['Date']

                # Balance = (float(Balance) + float(Debit)) - float(Credit)

                i['Balance'] = round(Balance, PriceRounding)
                Debit = float(Debit)
                Credit = float(Credit)

                if GroupUnder == True:
                    Balance = (float(Balance) + float(Debit)) - \
                        float(Credit)
                    filtered_dictionary = {"LedgerID": LedgerID, "LedgerName": LedgerName, "Debit": round(Debit, PriceRounding), "Credit": round(Credit, PriceRounding),
                                           "Balance": round(Balance, PriceRounding), "Date": Date, "GroupUnder": GroupUnder, }

                    filtered_array.append(filtered_dictionary)
            for i in filtered_array:
                date = i["Date"]
                if FromDate > date:
                    ob_array.append(i)
                if FromDate <= date and ToDate >= date:
                    last_data.append(i)

            if ob_array:
                last_dict = ob_array[-1]
                OpeningBalance = last_dict['Balance']

            # if last_data:
            TotalDebit = 0
            TotalCredit = 0
            TotalBalance = 0
            for data in last_data:
                TotalDebit += data['Debit']
                TotalCredit += data['Credit']
                # TotalBalance += data['Balance']
            Opening_type = ""
            if float(OpeningBalance) > 0:
                Opening_type = "Dr"
                TotalDebit = float(TotalDebit) + float(OpeningBalance)
            elif float(OpeningBalance) < 0:
                Opening_type = "Cr"
                TotalCredit = float(TotalCredit) + \
                    float(OpeningBalance)
            TotalBalance = float(TotalDebit) - float(TotalCredit)
            total = {
                "Opening_type": Opening_type,
                "Opening_date": FromDate,
                "OpeningBalance": OpeningBalance,
                "TotalDebit": round(TotalDebit, PriceRounding),
                "TotalCredit": round(TotalCredit, PriceRounding),
                "TotalBalance": round(TotalBalance, PriceRounding),
            }

            response_data = {
                "StatusCode": 6000,
                "data": last_data,
                "total": total,
                "OpeningBalance": OpeningBalance,
                "TotalDebit": round(TotalDebit, PriceRounding),
                "TotalCredit": round(TotalCredit, PriceRounding),
                "TotalBalance": round(TotalBalance, PriceRounding),
            }
            return response_data
            # else:
            #     response_data = {
            #         "StatusCode": 6001,
            #         "message": "No Datas under this group!"
            #     }
            #     return response_data
    else:
        print("No Datas in this Branch!")
        response_data = {
            "StatusCode": 6001,
            "message": "No Datas in this Branch!"
        }
    return response_data
    # else:
    #     return []
    # FromDate = serialized1.data['FromDate']
    # ToDate = serialized1.data['ToDate']
    # value = serialized1.data['value']
    # print(value, "KAYARUNNUND................!1")
    # ID = serialized1.data['ID']
    # if not FromDate and not ToDate:
    #     response_data = {
    #         "StatusCode": 6001,
    #         "message": "please Select Dates!"
    #     }
    #     return response_data
    # if not value:

    #     if ID == 1:
    #         response_data = {
    #             "StatusCode": 6001,
    #             "message": "please Select Ledger!"
    #         }
    #         return response_data
    #     elif ID == 2:
    #         response_data = {
    #             "StatusCode": 6001,
    #             "message": "please Select Group!"
    #         }
    #         return response_data
    # else:
    #     response_data = {
    #         "StatusCode": 6001,
    #     }
    #     return response_data


def export_to_excel_ledgerReport(wb, data, ID, FromDate):
    ws = wb.add_sheet("Ledger Report")
    print(data, "*************************************8")
    # write column headers in sheet

    # xl sheet styles
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
    font.colour_index = 2
    total_label_style.font = font

    value_decimal_style = xlwt.XFStyle()
    value_decimal_style.num_format_str = '0.00'

    # ********************
    try:
        TotalBalance = data['TotalBalance']
    except:
        TotalBalance = ""
    try:
        TotalCredit = data['TotalCredit']
    except:
        TotalCredit = ""
    try:
        TotalDebit = data['TotalDebit']
    except:
        TotalDebit = ""
    try:
        OpeningBalance = data['OpeningBalance']
    except:
        OpeningBalance = 0

    print(type(OpeningBalance), 'oppppppppppppopopopo')
    d_OpeningBalance = 0
    c_OpeningBalance = 0
    if OpeningBalance > 0:
        d_OpeningBalance = OpeningBalance
    else:
        c_OpeningBalance = OpeningBalance
    # ********************
    if data["StatusCode"] == 6000:
        if ID == 0:
            columns = ['SlNo', 'LedgerName', 'Debit', 'Credit', 'Balance']
            row_num = 0
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], sub_header_style)

            data_col = 0
            data_row = 1
            SlNo = 0

            print(data['data'], 'oppppppppppppopopopo')

            for j in data['data']:
                LedgerName = j['LedgerName']
                Debit = j['Debit']
                Credit = j['Credit']
                Balance = j['Balance']
                SlNo += 1

                ws.write(data_row, 0, SlNo)
                ws.write(data_row, 1, LedgerName)
                ws.write(data_row, 2, Debit)
                ws.write(data_row, 3, Credit)
                ws.write(data_row, 4, Balance)
                data_row += 1
        elif ID == 1:
            columns = ['SlNo', 'Voucher No', 'Date', 'Voucher Type',
                       'Particulars', 'Debit', 'Credit', 'Balance']
            row_num = 0
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], sub_header_style)

            data_col = 0
            data_row = 1
            SlNo = 0

            # Opening Balance
            ws.write(data_row, 0, "--")
            ws.write(data_row, 1, "--")
            ws.write(data_row, 2, FromDate)
            ws.write(data_row, 3, "OpeningBalance")
            ws.write(data_row, 4, "")
            ws.write(data_row, 5, d_OpeningBalance, value_decimal_style)
            ws.write(data_row, 6, c_OpeningBalance, value_decimal_style)
            ws.write(data_row, 7, OpeningBalance, value_decimal_style)
            data_row += 1
            for j in data['data']:
                RelatedLedgerName = j['RelatedLedgerName']
                VoucherType = j['VoucherType']
                VoucherType = j['VoucherType']
                VoucherNo = j['VoucherNo']
                Date = j['Date']

                LedgerName = j['LedgerName']
                Debit = j['Debit']
                Credit = j['Credit']
                Balance = j['Balance']

                SlNo += 1

                ws.write(data_row, 0, SlNo)
                ws.write(data_row, 1, VoucherNo)
                ws.write(data_row, 2, Date)
                ws.write(data_row, 3, VoucherType)
                ws.write(data_row, 4, RelatedLedgerName)
                ws.write(data_row, 5, Debit, value_decimal_style)
                ws.write(data_row, 6, Credit, value_decimal_style)
                ws.write(data_row, 7, Balance, value_decimal_style)
                data_row += 1
            ws.write(data_row, 3, "Total", total_label_style)
            ws.write(data_row, 5, TotalDebit, total_values_style)
            ws.write(data_row, 6, TotalCredit, total_values_style)
            ws.write(data_row, 7, TotalBalance, total_values_style)
        elif ID == 2:
            columns = ['SlNo', 'Ledger Name', 'Debit', 'Credit', 'Balance']
            row_num = 0
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], sub_header_style)

            data_col = 0
            data_row = 1
            SlNo = 0

            # Opening Balance
            ws.write(data_row, 0, "--")
            ws.write(data_row, 1, "OpeningBalance")
            ws.write(data_row, 2, d_OpeningBalance, value_decimal_style)
            ws.write(data_row, 3, c_OpeningBalance, value_decimal_style)
            ws.write(data_row, 4, OpeningBalance, value_decimal_style)
            data_row += 1
            for j in data['data']:
                LedgerName = j['LedgerName']
                Debit = j['Debit']
                Credit = j['Credit']
                Balance = j['Balance']
                SlNo += 1

                ws.write(data_row, 0, SlNo)
                ws.write(data_row, 1, LedgerName)
                ws.write(data_row, 2, Debit)
                ws.write(data_row, 3, Credit)
                ws.write(data_row, 4, Balance)
                data_row += 1
            print(data_row, "&&&&&&&&&&&")
            ws.write(data_row, 1, "Total", total_label_style)
            ws.write(data_row, 2, TotalDebit, total_values_style)
            ws.write(data_row, 3, TotalCredit, total_values_style)
            ws.write(data_row, 4, TotalBalance, total_values_style)

    else:
        pass


def trialBalance_excel_data(CompanyID, CreatedUserID, PriceRounding, BranchID, ToDate, request):
    company_instance = CompanySettings.objects.get(pk=CompanyID)
    company_serialized = CompanySettingsRestSerializer(
        company_instance, context={"request": request})
    if LedgerPosting.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
        TotalDebit = 0
        TotalCredit = 0
        TotalDebitForLOB = 0
        TotalCreditForLOB = 0
        DifferenceForLOB = 0
        test_arr = []

        instances = LedgerPosting.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID, Date__lte=ToDate)

        ledger_ids = instances.values_list('LedgerID')
        for ledger_id in ledger_ids:
            if ledger_id[0] not in test_arr:
                test_arr.append(ledger_id[0])
        for instance in instances:
            TotalDebit += instance.Debit
            TotalCredit += instance.Credit

        if instances:
            account_ledger = AccountLedger.objects.filter(
                CompanyID=CompanyID, LedgerID__in=test_arr)
            serialized = TrialBalanceSerializer(account_ledger, many=True, context={
                                                "CompanyID": CompanyID, "PriceRounding": PriceRounding})

            orderdDict = serialized.data
            jsnDatas = convertOrderdDict(orderdDict)
            new_jsnDatas = convertOrderdDict(orderdDict)

            # TotalAvgValueOpening = 0
            # FromDate = FinancialYear.objects.get(
            #     CompanyID=CompanyID, IsClosed=False).FromDate
            # # opening stock till financial year
            # if StockPosting.objects.filter(Date__lt=FromDate, CompanyID=CompanyID).exists():
            #     stock_instance_CS = StockPosting.objects.filter(
            #         Date__lte=FromDate, CompanyID=CompanyID)
            #     QtyInTot = 0
            #     QtyOutTot = 0
            #     for si in stock_instance_CS:

            #         QtyInTot += (float(si.QtyIn) * float(si.Rate))
            #         QtyOutTot += (float(si.QtyOut) * float(si.Rate))

            #     TotalAvgValueOpening = float(QtyInTot) - float(QtyOutTot)

            # # opening stock after financial year
            # if StockPosting.objects.filter(Date__gte=FromDate, Date__lte=ToDate, CompanyID=CompanyID, VoucherType="OS").exists():
            #     stock_instance_CS = StockPosting.objects.filter(
            #         Date__lte=ToDate, CompanyID=CompanyID, VoucherType="OS")
            #     QtyInTot = 0
            #     QtyOutTot = 0
            #     for si in stock_instance_CS:

            #         QtyInTot += (float(si.QtyIn) * float(si.Rate))
            #         QtyOutTot += (float(si.QtyOut) * float(si.Rate))

            #     TotalAvgValueOpening += (float(QtyInTot) -
            #                              float(QtyOutTot))

            TotalAvgValueOpening = 0

            if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, InventoryType="StockItem").exists():
                product_instances_CS = Product.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, InventoryType="StockItem")

                for pi in product_instances_CS:
                    ProductID = pi.ProductID

                    if StockPosting.objects.filter(ProductID=ProductID, Date__lte=ToDate, CompanyID=CompanyID, VoucherType="OS").exists():
                        stock_instance_CS = StockPosting.objects.filter(
                            ProductID=ProductID, Date__lte=ToDate, CompanyID=CompanyID, VoucherType="OS")
                        QtyInRate = 0
                        QtyOutTot = 0
                        QtyInTot = 0
                        for si in stock_instance_CS:
                            QtyInRate += (float(si.QtyIn) * float(si.Rate))
                            QtyInTot += float(si.QtyIn)
                            QtyOutTot += float(si.QtyOut)

                        stock = float(QtyInTot) - float(QtyOutTot)

                        AvgRate = 0
                        if QtyInTot > 0:
                            AvgRate = float(QtyInRate) / float(QtyInTot)

                        TotalAvgValueOpening += float(stock) * \
                            float(AvgRate)

            if TotalAvgValueOpening > 0:
                OpeningStock = {
                    "LedgerName": "OpeningStock",
                    "LedgerID": "-",
                    "Debit": TotalAvgValueOpening,
                    "Credit": 0,
                    "VoucherType": "-",
                }
                jsnDatas.append(OpeningStock)
                new_jsnDatas.append(OpeningStock)
            elif TotalAvgValueOpening < 0:
                OpeningStock = {
                    "LedgerName": "OpeningStock",
                    "LedgerID": "-",
                    "Debit": 0,
                    "Credit": TotalAvgValueOpening,
                    "VoucherType": "-",
                }
                jsnDatas.append(OpeningStock)
                new_jsnDatas.append(OpeningStock)

            for i in jsnDatas:
                LedgerName = i['LedgerName']
                LedgerID = i['LedgerID']
                Debit = i['Debit']
                Credit = i['Credit']
                VoucherType = i['VoucherType']

                # if VoucherType == 'LOB':
                #     TotalDebitForLOB += Debit
                #     TotalCreditForLOB += Credit

                TotalDebitForLOB += Debit
                TotalCreditForLOB += Credit

            is_DebitGreater = False
            is_CreditGreater = False
            Total = 0

            if TotalDebitForLOB > TotalCreditForLOB:
                Total = TotalDebitForLOB
                is_DebitGreater = True
                difference = float(TotalDebitForLOB) - \
                    float(TotalCreditForLOB)

            elif TotalDebitForLOB < TotalCreditForLOB:
                Total = TotalCreditForLOB
                is_CreditGreater = True
                difference = float(TotalCreditForLOB) - \
                    float(TotalDebitForLOB)
            else:
                difference = 0
                Total = TotalDebitForLOB

            # Total = 0
            # if TotalDebit > TotalCredit:
            #     Total = float(Total) + float(TotalDebit)
            # elif TotalDebit < TotalCredit:
            #     Total = float(Total) + float(TotalCredit)
            # else:
            #     Total = float(Total) + float(TotalDebit)

            # New style Page function Start
            deb = ""
            crd = ""
            if difference > 0:
                deb = difference
                crd = ""
            elif difference < 0:
                deb = ""
                crd = difference
            if not difference == 0:
                dic = {
                    "LedgerName": "Opening Balance Difference",
                    "LedgerID": "-",
                    "Debit": deb,
                    "Credit": crd,
                    "VoucherType": "-",
                }
                new_jsnDatas.append(dic)
            # Adding Total to new_jsnDatas array
            dic = {
                "LedgerName": "Total",
                "LedgerID": "-",
                "Debit": Total,
                "Credit": Total,
                "VoucherType": "-",
            }
            new_jsnDatas.append(dic)
            # New style Page function End

            response_data = {
                "StatusCode": 6000,
                "data": jsnDatas,
                "new_data": new_jsnDatas,
                "TotalDebit": TotalDebit,
                "TotalCredit": TotalCredit,
                "Total": Total,
                "TotalDebitForLOB": TotalDebitForLOB,
                "TotalCreditForLOB": TotalCreditForLOB,
                "difference": difference,
                "is_DebitGreater": is_DebitGreater,
                "is_CreditGreater": is_CreditGreater,
                "OpeningStock": TotalAvgValueOpening,
                "company_data": company_serialized.data
            }
            return response_data
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Account Ledger Not Found Till this date!"
            }

            return response_data

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Account Ledger Not Found in this BranchID!"
        }

        return response_data


def export_to_excel_trialBalance(wb, data):
    ws = wb.add_sheet("TrialBalance Report")
    print(data, "*************************************8")
    # write column headers in sheet

    # xl sheet styles
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
    font.colour_index = 2
    total_label_style.font = font

    value_decimal_style = xlwt.XFStyle()
    value_decimal_style.num_format_str = '0.00'

    data_col = 0
    data_row = 1
    SlNo = 0

    columns = ['SlNo', 'Ledger Name', 'Debit', 'Credit']
    row_num = 0
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], sub_header_style)

    data_col = 0
    data_row = 1
    SlNo = 0

    # ********************
    Total = data['Total']
    TotalCredit = data['TotalCredit']
    TotalDebit = data['TotalDebit']
    difference = data['difference']
    # ********************
    o_Debit = 0
    o_Credit = 0
    try:
        data_list = data['data']
    except:
        data_list = []

    for j in data_list:
        LedgerName = j['LedgerName']
        Debit = j['Debit']
        Credit = j['Credit']

        o_Debit += Debit
        o_Credit += Credit
        SlNo += 1

        ws.write(data_row, 0, SlNo)
        ws.write(data_row, 1, LedgerName)
        ws.write(data_row, 2, Debit)
        ws.write(data_row, 3, Credit)
        data_row += 1

    # Opening Balance Difference
    if o_Debit > o_Credit:
        o_Credit = difference
        o_Debit = 0
    else:
        o_Credit = 0
        o_Debit = difference

    ws.write(data_row, 0, SlNo+1)
    ws.write(data_row, 1, "Opening Balance Difference")
    ws.write(data_row, 2, o_Debit, total_values_style)
    ws.write(data_row, 3, o_Credit, total_values_style)
    data_row += 1
    # ===========
    ws.write(data_row, 0, "", total_values_style)
    ws.write(data_row, 1, "Total", total_label_style)
    ws.write(data_row, 2, Total, total_values_style)
    ws.write(data_row, 3, Total, total_values_style)


def profitAndLoss_excel_data(key, CompanyID, CreatedUserID, PriceRounding, BranchID, ToDate, FromDate, request, ManualOpeningStock, ManualClosingStock):
    try:
        ManualOpeningStock = ManualOpeningStock
    except:
        ManualOpeningStock = ""

    try:
        ManualClosingStock = ManualClosingStock
    except:
        ManualClosingStock = ""

    if LedgerPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():

        TotalCoast = 0
        TotalDirectExpense = 0
        TotalDirectIncome = 0
        TotalIndirectExpense = 0
        TotalInDirectIncome = 0
        test_arr = []
        instances = LedgerPosting.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)
        ledger_ids = instances.values_list('LedgerID')
        for ledger_id in ledger_ids:
            if ledger_id[0] not in test_arr:
                test_arr.append(ledger_id[0])

        account_ledger = AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID__in=test_arr)
        serialized = ProfitAndLossSerializer(
            account_ledger, many=True, context={"CompanyID": CompanyID, "FromDate": FromDate, "ToDate": ToDate})

        orderdDict = serialized.data
        jsnDatas = convertOrderdDict(orderdDict)

        Direct_Expenses_Array = []
        Indirect_Expenses_Array = []
        Direct_Income_Array = []
        Indirect_Income_Array = []

        dirExArr = []

        name_exist_dirExp = {}
        name_exist_detailed_dirExp = {}
        dic_exGrp_dirExp = {}
        final_direct_expence_arr = []

        name_exist_indirExp = {}
        name_exist_detailed_indirExp = {}
        dic_exGrp_indirExp = {}
        final_indirect_expence_arr = []

        name_exist_dirInc = {}
        name_exist_detailed_dirInc = {}
        dic_exGrp_dirInc = {}
        final_direct_income_arr = []

        name_exist_indirInc = {}
        name_exist_detailed_indirInc = {}
        dic_exGrp_indirInc = {}
        final_indirect_income_arr = []

        TotalAvgValueOpening = 0
        if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, InventoryType="StockItem").exists():
            product_instances_OS = Product.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, InventoryType="StockItem")
            voucherTypes = ["PI", "OS", "ES"]
            product_ids = product_instances_OS.values_list('ProductID')
            # for pi in product_instances_OS:
            #     ProductID = pi.ProductID
            # # opening stock before financial year

            if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, InventoryType="StockItem").exists():
                product_instances_CS = Product.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, InventoryType="StockItem")

                # for pi in product_instances_CS:
                #     ProductID = pi.ProductID
                product_ids = product_instances_CS.values_list('ProductID')
                # new start
                if StockPosting.objects.filter(ProductID__in=product_ids, BranchID=BranchID, Date__lt=FromDate, CompanyID=CompanyID, VoucherType__in=voucherTypes).exists():
                    stock_instances_new = StockPosting.objects.filter(
                        ProductID__in=product_ids, BranchID=BranchID, Date__lt=FromDate, CompanyID=CompanyID, VoucherType__in=voucherTypes, QtyIn__gt=0)

                    qurried_instances = stock_instances_new.values('ProductID').annotate(
                        sum_in_rate=Sum(F('QtyIn') * F('Rate')) / Sum('QtyIn')).order_by('ProductID')
                    TotalQty_new = StockPosting.objects.filter(BranchID=BranchID, Date__lt=FromDate, CompanyID=CompanyID).values(
                        'ProductID').annotate(sum_in_rate=Sum('QtyIn') - Sum('QtyOut')).order_by('ProductID')
                    result_list = sorted(
                        chain(qurried_instances, TotalQty_new), key=itemgetter('ProductID'))

                    names = [i.get('ProductID') for i in result_list]
                    points = [i.get('sum_in_rate') for i in result_list]
                    # pprint(points)

                    content_list = {}
                    for (name, score) in zip(names, points):
                        if name in content_list.keys():
                            # if the value is already in list, add current score to the sum
                            content_list[name] *= score
                        else:
                            # if the value is not yet in list, create an entry
                            content_list[name] = score

                    values = content_list.values()
                    TotalAvgValueOpening = sum(values)

            if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, InventoryType="StockItem").exists():
                product_instances_CS = Product.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, InventoryType="StockItem")

                # for pi in product_instances_CS:
                #     ProductID = pi.ProductID
                product_ids = product_instances_CS.values_list('ProductID')
                # new start
                if StockPosting.objects.filter(ProductID__in=product_ids, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, CompanyID=CompanyID, VoucherType="OS").exists():
                    stock_instances_new = StockPosting.objects.filter(
                        ProductID__in=product_ids, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, CompanyID=CompanyID, VoucherType="OS", QtyIn__gt=0)

                    print(stock_instances_new)
                    qurried_instances = stock_instances_new.values('ProductID').annotate(
                        sum_in_rate=Sum(F('QtyIn') * F('Rate')) / Sum('QtyIn')).order_by('ProductID')
                    TotalQty_new = StockPosting.objects.filter(BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, CompanyID=CompanyID).values(
                        'ProductID').annotate(sum_in_rate=Sum('QtyIn') - Sum('QtyOut')).order_by('ProductID')
                    result_list = sorted(
                        chain(qurried_instances, TotalQty_new), key=itemgetter('ProductID'))

                    names = [i.get('ProductID') for i in result_list]
                    points = [i.get('sum_in_rate') for i in result_list]
                    # pprint(points)

                    content_list = {}
                    for (name, score) in zip(names, points):
                        if name in content_list.keys():
                            # if the value is already in list, add current score to the sum
                            content_list[name] *= score
                        else:
                            # if the value is not yet in list, create an entry
                            content_list[name] = score

                    values = content_list.values()
                    TotalAvgValueOpening += sum(values)

        if ManualOpeningStock:
            TotalAvgValueOpening = float(ManualOpeningStock)
        name_exist_dirExp['Opening Stock'] = {
            # 'GroupName' : "Opening Stock",
            'Balance': float(TotalAvgValueOpening)
        }

        # opening stock end
        # closing stock start
        TotalAvgValueClosing = 0

        if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, InventoryType="StockItem").exists():
            product_instances_CS = Product.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, InventoryType="StockItem")

            # for pi in product_instances_CS:
            #     ProductID = pi.ProductID
            product_ids = product_instances_CS.values_list('ProductID')
            # new start
            if StockPosting.objects.filter(ProductID__in=product_ids, BranchID=BranchID, Date__lte=ToDate, CompanyID=CompanyID, VoucherType__in=voucherTypes).exists():
                stock_instances_new = StockPosting.objects.filter(
                    ProductID__in=product_ids, BranchID=BranchID, Date__lte=ToDate, CompanyID=CompanyID, VoucherType__in=voucherTypes, QtyIn__gt=0)

                qurried_instances = stock_instances_new.values('ProductID').annotate(
                    sum_in_rate=Sum(F('QtyIn') * F('Rate')) / Sum('QtyIn')).order_by('ProductID')
                TotalQty_new = StockPosting.objects.filter(BranchID=BranchID, Date__lte=ToDate, CompanyID=CompanyID).values(
                    'ProductID').annotate(sum_in_rate=Sum('QtyIn') - Sum('QtyOut')).order_by('ProductID')
                result_list = sorted(
                    chain(qurried_instances, TotalQty_new), key=itemgetter('ProductID'))

                names = [i.get('ProductID') for i in result_list]
                points = [i.get('sum_in_rate') for i in result_list]
                # pprint(points)

                content_list = {}
                for (name, score) in zip(names, points):
                    if name in content_list.keys():
                        # if the value is already in list, add current score to the sum
                        content_list[name] *= score
                    else:
                        # if the value is not yet in list, create an entry
                        content_list[name] = score

                values = content_list.values()
                TotalAvgValueClosing = sum(values)

        if ManualClosingStock:
            TotalAvgValueClosing = float(ManualClosingStock)
        # closing stock data for consolidated ends here
        test_dicT = {}

        for i in jsnDatas:
            LedgerName = i['LedgerName']
            LedgerID = i['LedgerID']
            GroupUnder = i['GroupUnder']
            Balance = i['Balance']
            if GroupUnder == 'Direct Expenses':
                Group_Under = AccountLedger.objects.get(
                    BranchID=BranchID, LedgerID=LedgerID, CompanyID=CompanyID).AccountGroupUnder
                Group_name = AccountGroup.objects.get(
                    AccountGroupID=Group_Under, CompanyID=CompanyID).AccountGroupName

                ledgerpost_ins = LedgerPosting.objects.filter(
                    LedgerID=LedgerID, Date__range=(FromDate, ToDate), CompanyID=CompanyID)

                # for consolidated start
                dir_exp_Tot_Credit = 0
                dir_exp_Tot_Debit = 0
                for lpi in ledgerpost_ins:
                    dir_exp_Tot_Debit = + float(lpi.Debit)
                    dir_exp_Tot_Credit = + float(lpi.Credit)
                    dir_exp_balance = float(
                        dir_exp_Tot_Debit) - float(dir_exp_Tot_Credit)

                    dic_exGrp_dirExp = {"GroupName": str(
                        Group_name), "Balance": float(dir_exp_balance)}

                if not Group_name in name_exist_dirExp:
                    # name_exist.append(Group_name)
                    dic_exGrp_dirExp = {
                        "Balance": float(Balance)
                    }
                    name_exist_dirExp[Group_name] = dic_exGrp_dirExp
                else:
                    b = name_exist_dirExp[Group_name]["Balance"]
                    name_exist_dirExp[Group_name]["Balance"] = b + \
                        float(Balance)

                # consolidated end
                # detailed start
                TotalDirectExpense += Balance
                Direct_Expenses_dictionary = {"LedgerID": LedgerID, "LedgerName": LedgerName,
                                              "Balance": Balance, "GroupUnder": GroupUnder, }

                if not Group_name in name_exist_detailed_dirExp:
                    name_exist_detailed_dirExp[Group_name] = []
                name_exist_detailed_dirExp[Group_name].append(
                    Direct_Expenses_dictionary)

                # dic = {
                #     "group_name" : Group_name,
                #     "ledgers" : Direct_Expenses_dictionary
                # }
                # if not Group_name in test_dicT:
                #     test_dicT[Group_name] = []
                # name_exist_detailed_dirExp[Group_name].append(Direct_Expenses_dictionary)
            elif GroupUnder == 'Indirect Expenses':

                Group_Under = AccountLedger.objects.get(
                    BranchID=BranchID, LedgerID=LedgerID, CompanyID=CompanyID).AccountGroupUnder
                Group_name = AccountGroup.objects.get(
                    AccountGroupID=Group_Under, CompanyID=CompanyID).AccountGroupName

                ledgerpost_ins = LedgerPosting.objects.filter(
                    LedgerID=LedgerID, Date__range=(FromDate, ToDate), CompanyID=CompanyID)

                # for consolidated start
                indir_exp_Tot_Credit = 0
                indir_exp_Tot_Debit = 0
                for lpi in ledgerpost_ins:
                    indir_exp_Tot_Debit = + lpi.Debit
                    dir_exp_Tot_Credit = + lpi.Credit
                    dir_exp_balance = indir_exp_Tot_Debit - indir_exp_Tot_Credit

                    dic_exGrp_indirExp = {"GroupName": str(
                        Group_name), "Balance": float(dir_exp_balance)}

                if not Group_name in name_exist_indirExp:
                    # name_exist.append(Group_name)
                    dic_exGrp_indirExp = {
                        "Balance": float(Balance),
                    }
                    name_exist_indirExp[Group_name] = dic_exGrp_indirExp
                else:
                    b = name_exist_indirExp[Group_name]["Balance"]
                    name_exist_indirExp[Group_name]["Balance"] = b + \
                        float(Balance)

                # consolidated end
                # detailed start
                TotalIndirectExpense += Balance
                Indirect_Expenses_dictionary = {"LedgerID": LedgerID, "LedgerName": LedgerName,
                                                "Balance": Balance, "GroupUnder": GroupUnder, }

                if not Group_name in name_exist_detailed_indirExp:
                    name_exist_detailed_indirExp[Group_name] = []
                name_exist_detailed_indirExp[Group_name].append(
                    Indirect_Expenses_dictionary)

            elif GroupUnder == 'Direct Income':
                if LedgerID == 86:
                    Balance = -(Balance)
                if LedgerID == 85:
                    Balance = abs(Balance)
                if LedgerID == 83:
                    Balance = abs(Balance)

                Group_Under = AccountLedger.objects.get(
                    BranchID=BranchID, LedgerID=LedgerID, CompanyID=CompanyID).AccountGroupUnder
                Group_name = AccountGroup.objects.get(
                    AccountGroupID=Group_Under, CompanyID=CompanyID).AccountGroupName

                ledgerpost_ins = LedgerPosting.objects.filter(
                    LedgerID=LedgerID, Date__range=(FromDate, ToDate), CompanyID=CompanyID)

                # for consolidated start
                dir_inc_Tot_Credit = 0
                dir_inc_Tot_Debit = 0
                for lpi in ledgerpost_ins:

                    dir_inc_Tot_Debit = + lpi.Debit
                    dir_inc_Tot_Credit = + lpi.Credit

                    dir_inc_balance = dir_inc_Tot_Debit - dir_inc_Tot_Credit

                    dir_inc_balance = dir_inc_balance

                    dic_exGrp_dirInc = {"GroupName": str(
                        Group_name), "Balance": float(dir_inc_balance)}
                if not Group_name in name_exist_dirInc:
                    # name_exist.append(Group_name)
                    dic_exGrp_dirInc = {
                        "Balance": float(Balance),
                    }
                    name_exist_dirInc[Group_name] = dic_exGrp_dirInc
                else:
                    b = name_exist_dirInc[Group_name]["Balance"]
                    name_exist_dirInc[Group_name]["Balance"] = b + \
                        float(Balance)

                name_exist_dirInc['Closing Stock'] = {
                    # 'GroupName' : "Closing Stock",
                    'Balance': TotalAvgValueClosing
                }

                # consolidated end
                # detailed start
                TotalDirectIncome += Balance

                Direct_Income_dictionary = {"LedgerID": LedgerID, "LedgerName": LedgerName,
                                            "Balance": Balance, "GroupUnder": GroupUnder, }

                if not Group_name in name_exist_detailed_dirInc:
                    name_exist_detailed_dirInc[Group_name] = []
                name_exist_detailed_dirInc[Group_name].append(
                    Direct_Income_dictionary)

                # TotalDirectIncome += Balance
                # Direct_Income_dictionary = {"LedgerID" : LedgerID,"LedgerName" : LedgerName,
                #                                 "Balance" : Balance,"GroupUnder" : GroupUnder, }

                # Direct_Income_Array.append(Direct_Income_dictionary)

            elif GroupUnder == 'Indirect Income':

                Group_Under = AccountLedger.objects.get(
                    BranchID=BranchID, LedgerID=LedgerID, CompanyID=CompanyID).AccountGroupUnder
                Group_name = AccountGroup.objects.get(
                    AccountGroupID=Group_Under, CompanyID=CompanyID).AccountGroupName

                ledgerpost_ins = LedgerPosting.objects.filter(
                    LedgerID=LedgerID, Date__range=(FromDate, ToDate), CompanyID=CompanyID)

                # for consolidated start
                indir_inc_Tot_Credit = 0
                indir_inc_Tot_Debit = 0
                for lpi in ledgerpost_ins:
                    indir_inc_Tot_Debit = + lpi.Debit
                    indir_inc_Tot_Credit = + lpi.Credit
                    indir_inc_balance = indir_inc_Tot_Debit - indir_inc_Tot_Credit

                    dic_exGrp_indirInc = {"GroupName": str(
                        Group_name), "Balance": float(abs(indir_inc_balance))}

                if not Group_name in name_exist_indirInc:
                    dic_exGrp_indirInc = {
                        "Balance": float(Balance),
                    }
                    name_exist_indirInc[Group_name] = dic_exGrp_indirInc
                else:
                    b = name_exist_indirInc[Group_name]["Balance"]
                    name_exist_indirInc[Group_name]["Balance"] = b + \
                        float(Balance)

                TotalInDirectIncome += abs(Balance)
                Indirect_Income_dictionary = {"LedgerID": LedgerID, "LedgerName": LedgerName,
                                              "Balance": abs(Balance), "GroupUnder": GroupUnder, }

                if not Group_name in name_exist_detailed_indirInc:
                    name_exist_detailed_indirInc[Group_name] = []
                name_exist_detailed_indirInc[Group_name].append(
                    Indirect_Income_dictionary)

        final_direct_expence_arr.append(name_exist_dirExp)

        final_direct_income_arr.append(name_exist_dirInc)

        # final_direct_income_arr.append(closing_stock_dic_dirInc)

        final_indirect_expence_arr.append(name_exist_indirExp)

        final_indirect_income_arr.append(name_exist_indirInc)

        Direct_Expenses_Array.append(name_exist_detailed_dirExp)
        Indirect_Expenses_Array.append(name_exist_detailed_indirExp)
        Direct_Income_Array.append(name_exist_detailed_dirInc)
        Indirect_Income_Array.append(name_exist_detailed_indirInc)

        if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
            stock_instances = StockRate.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)
            for stock_instance in stock_instances:
                TotalCoast += stock_instance.Cost

        is_DirectexpenseGreater = False
        is_IndirectexpenseGreater = False
        is_DirectincomeGreater = False
        is_IndirectincomeGreater = False

        TotalDirectIncome = float(
            TotalDirectIncome) + float(TotalAvgValueClosing)
        # TotalDirectIncomeWithStock = float(TotalCoast) + float(TotalDirectIncome)
        TotalDirectExpense = float(
            TotalDirectExpense) + float(TotalAvgValueOpening)

        if TotalDirectIncome > TotalDirectExpense:
            is_DirectincomeGreater = True
            TotalDirect = TotalDirectIncome
            Direct_difference = float(
                TotalDirectIncome) - float(TotalDirectExpense)
        elif TotalDirectExpense > TotalDirectIncome:
            is_DirectexpenseGreater = True
            TotalDirect = TotalDirectExpense
            Direct_difference = float(
                TotalDirectExpense) - float(TotalDirectIncome)
        else:
            TotalDirect = TotalDirectExpense
            Direct_difference = 0

        if is_DirectincomeGreater == True:
            TotalInDirectIncome = TotalInDirectIncome + Direct_difference

        if is_DirectexpenseGreater == True:
            TotalIndirectExpense = TotalIndirectExpense + Direct_difference

        if TotalIndirectExpense > TotalInDirectIncome:
            is_IndirectexpenseGreater = True
            TotalIndirect = TotalIndirectExpense
            Indirectdifference = float(
                TotalIndirectExpense) - float(TotalInDirectIncome)
        elif TotalIndirectExpense < TotalInDirectIncome:

            is_IndirectincomeGreater = True
            TotalIndirect = TotalInDirectIncome
            Indirectdifference = float(
                TotalInDirectIncome) - float(TotalIndirectExpense)
        else:
            Indirectdifference = 0
            TotalIndirect = TotalIndirectExpense

        # direct expense final array starts here
        DirExPCons = []
        for i in final_direct_expence_arr[0]:

            myDic = {
                'GroupName': i,
                'Balance': float(round(final_direct_expence_arr[0][i]['Balance'], PriceRounding))
            }
            DirExPCons.append(myDic)

        DirIncCons = []
        if final_direct_income_arr[0]:
            for i in final_direct_income_arr[0]:

                if i == "Closing Stock":
                    myDic = {
                        'GroupName': i,
                        'Balance': float(round(final_direct_income_arr[0][i]['Balance'], PriceRounding))
                    }
                    DirIncCons.append(myDic)
                else:
                    myDic = {
                        'GroupName': i,
                        'Balance': float(round(final_direct_income_arr[0][i]['Balance'], PriceRounding))
                    }
                    DirIncCons.append(myDic)
        else:
            myDic = {
                'GroupName': "Closing Stock",
                'Balance': float(round(TotalAvgValueClosing, PriceRounding))
            }
            DirIncCons.append(myDic)

        inDirIncCons = []
        inDirExpCons = []
        for i in final_indirect_income_arr[0]:
            myDic = {
                'GroupName': i,
                'Balance': float(round(abs(final_indirect_income_arr[0][i]['Balance']), PriceRounding))
            }
            inDirIncCons.append(myDic)

        for i in final_indirect_expence_arr[0]:
            myDic = {
                'GroupName': i,
                'Balance': float(round(final_indirect_expence_arr[0][i]['Balance'], PriceRounding))
            }
            inDirExpCons.append(myDic)

        profitAndLoss_final_data = profitAndLoss_balancing(key, DirExPCons, DirIncCons, inDirExpCons, inDirIncCons, is_DirectincomeGreater, is_DirectexpenseGreater, is_IndirectexpenseGreater, is_IndirectincomeGreater, Indirectdifference, Direct_difference, TotalDirect, TotalIndirect, Direct_Expenses_Array, Indirect_Expenses_Array, Direct_Income_Array, Indirect_Income_Array, TotalAvgValueOpening, TotalAvgValueClosing
                                                           )

        response_data = {
            "StatusCode": 6000,
            "DirectExpensesData": Direct_Expenses_Array,
            "InDirectExpensesData": Indirect_Expenses_Array,
            "DirectIncomeData": Direct_Income_Array,
            "IndirectIncomeData": Indirect_Income_Array,
            "TotalCoast": TotalCoast,
            "TotalDirect": TotalDirect,
            "TotalIndirect": TotalIndirect,
            "DirectIncomeGreater": is_DirectincomeGreater,
            "DirectExpenseGreater": is_DirectexpenseGreater,
            "IndirectExpenseGreater": is_IndirectexpenseGreater,
            "IndirectIncomeGreater": is_IndirectincomeGreater,
            "Direct_difference": Direct_difference,
            "Indirectdifference": Indirectdifference,
            "DirExPCons": DirExPCons,
            "inDirIncCons": inDirIncCons,
            "DirIncCons": DirIncCons,
            "inDirExpCons": inDirExpCons,
            "OpeningStock": TotalAvgValueOpening,
            "ClosingStock": TotalAvgValueClosing,
            "profitAndLoss_final_data": profitAndLoss_final_data,
        }
        return response_data
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "No Datas During this Time Periods!"
        }
        return response_data


def export_to_excel_profitAndLoss_123(wb, data, key):
    ws = wb.add_sheet("ProfitAndLoss Report")
    # xl sheet styles
    font = xlwt.Font()
    font.bold = True
    # font.height = 11 * 20

    main_header_style = xlwt.XFStyle()
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    main_header_style.alignment = center
    main_header_style.font = font

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

    total_label_style = xlwt.XFStyle()
    # font = xlwt.Font()
    # font.bold = True
    font.colour_index = 2
    total_label_style.font = font

    value_decimal_style = xlwt.XFStyle()
    value_decimal_style.num_format_str = '0.00'

    data_col = 0
    data_row = 0
    SlNo = 0

    # **********Gross Profit/Gross Loss && Net Profit/Net Loss**************
    Indirectdifference = data['Indirectdifference']
    Direct_difference = data['Direct_difference']
    # ************************

    # <<<<<<<<<<<<<<<<<<<CONSOLIDATED START HEARE>>>>>>>>>>>>>>>>>>>>>>>>>>
    if key == 1:
        # ---------Expence------------------
        ws.write(data_row, data_col, "Expense", main_header_style)
        data_row += 1
        ws.write(data_row, data_col, "Group Name", main_header_style)
        data_col += 1
        ws.write(data_row, data_col, "Amount", main_header_style)
        data_row += 1
        # ==========Direct Expence==========
        for i in data['DirExPCons']:
            GroupName = i['GroupName']
            Balance = i['Balance']
            ws.write(data_row, 0, GroupName)
            ws.write(data_row, 1, Balance)
            data_row += 1
        # Gross Profit
        if data['DirectIncomeGreater']:
            ws.write(data_row, 0, 'Gross Profit')
            ws.write(data_row, 1, Direct_difference)
            data_row += 1
        else:
            ws.write(data_row, 0, '')
            ws.write(data_row, 1, '')
            data_row += 1

        # *****END******
        ws.write(data_row, 0, 'Total', total_label_style)
        ws.write(data_row, 1, data['TotalDirect'])
        data_row += 1
        # Gross Loss
        if data['DirectExpenseGreater']:
            ws.write(data_row, 0, 'Gross Loss')
            ws.write(data_row, 1, Direct_difference)
            data_row += 1
        else:
            ws.write(data_row, 0, '')
            ws.write(data_row, 1, '')
            data_row += 1
        # ==========InDirect Expence==========
        for i in data['inDirExpCons']:
            GroupName = i['GroupName']
            Balance = i['Balance']
            ws.write(data_row, 0, GroupName)
            ws.write(data_row, 1, Balance)
            data_row += 1
        # Net Profit
        if data['IndirectIncomeGreater']:
            ws.write(data_row, 0, 'Net Profit')
            ws.write(data_row, 1, Indirectdifference)
            data_row += 1
        else:
            ws.write(data_row, 0, '')
            ws.write(data_row, 1, '')
            data_row += 1
        # *****END******
        ws.write(data_row, 0, 'Total', total_label_style)
        ws.write(data_row, 1, data['TotalIndirect'])

        data_col = 2
        data_row = 0

        # ---------Income------------------
        ws.write(data_row, data_col, "Income", main_header_style)
        data_row += 1
        ws.write(data_row, data_col, "Group Name", main_header_style)
        data_col += 1
        ws.write(data_row, data_col, "Amount", main_header_style)
        data_row += 1
        # ==========Direct Income==========
        for i in data['DirIncCons']:
            GroupName = i['GroupName']
            Balance = i['Balance']
            ws.write(data_row, 2, GroupName)
            ws.write(data_row, 3, Balance)
            data_row += 1
        # Gross Loss
        if data['DirectExpenseGreater']:
            ws.write(data_row, 2, 'Gross Profit')
            ws.write(data_row, 3, Direct_difference)
            data_row += 1
        else:
            ws.write(data_row, 2, '')
            ws.write(data_row, 3, '')
            data_row += 1
        # *****END******
        ws.write(data_row, 2, 'Total', total_label_style)
        ws.write(data_row, 3, data['TotalDirect'])
        data_row += 1
        # Gross Profit
        if data['DirectIncomeGreater']:
            ws.write(data_row, 2, 'Gross Profit')
            ws.write(data_row, 3, Direct_difference)
            data_row += 1
        else:
            ws.write(data_row, 2, '')
            ws.write(data_row, 3, '')
            data_row += 1
        # ==========InDirect Income==========
        for i in data['inDirIncCons']:
            GroupName = i['GroupName']
            Balance = i['Balance']
            ws.write(data_row, 2, GroupName)
            ws.write(data_row, 3, Balance)
            data_row += 1
        # Net Loss
        if data['IndirectExpenseGreater']:
            ws.write(data_row, 2, 'Net Loss')
            ws.write(data_row, 3, Indirectdifference)
            data_row += 1
        else:
            ws.write(data_row, 2, '')
            ws.write(data_row, 3, '')
            data_row += 1
        # *****END******
        ws.write(data_row, 2, 'Total', total_label_style)
        ws.write(data_row, 3, data['TotalIndirect'])
    # <<<<<<<<<<<<<<<<<<<DETAILED START HEARE>>>>>>>>>>>>>>>>>>>>>>>>>>
    elif key == 2:
        # # ==========Direct Expence==========
        ws.write(data_row, data_col, "Expense", main_header_style)
        data_row += 1
        ws.write(data_row, data_col, "Group Name", main_header_style)
        data_col += 1
        ws.write(data_row, data_col, "Ledger Name", main_header_style)
        data_col += 1
        ws.write(data_row, data_col, "Amount", main_header_style)
        data_row += 1

        # OpeningStock
        ws.write(data_row, 0, 'OpeningStock')
        ws.write(data_row, 1, "")
        ws.write(data_row, 2, data['OpeningStock'])

        data_row += 1
        for i in data['DirectExpensesData'][0]:
            GroupName = i

            ws.write(data_row, 0, GroupName)
            for detail in data['DirectExpensesData'][0][i]:
                ws.write(data_row, 1, detail['LedgerName'])
                ws.write(data_row, 2, detail['Balance'])
                data_row += 1
        # Gross Profit
        if data['DirectIncomeGreater']:
            ws.write(data_row, 0, 'Gross Profit')
            ws.write(data_row, 1, '')
            ws.write(data_row, 2, Direct_difference)
            data_row += 1
        else:
            ws.write(data_row, 0, '')
            ws.write(data_row, 1, '')
            ws.write(data_row, 2, '')
            data_row += 1

        # *****END******
        ws.write(data_row, 0, 'Total', total_label_style)
        ws.write(data_row, 1, '')
        ws.write(data_row, 2, data['TotalDirect'])
        data_row += 1
        # Gross Loss
        if data['DirectExpenseGreater']:
            ws.write(data_row, 0, 'Gross Profit')
            ws.write(data_row, 1, '')
            ws.write(data_row, 2, Direct_difference)
            data_row += 1
        else:
            ws.write(data_row, 0, '')
            ws.write(data_row, 1, '')
            ws.write(data_row, 2, '')
            data_row += 1

        # ==========InDirect Expence==========
        for i in data['InDirectExpensesData'][0]:
            GroupName = i

            ws.write(data_row, 0, GroupName)
            for detail in data['InDirectExpensesData'][0][i]:
                ws.write(data_row, 1, detail['LedgerName'])
                ws.write(data_row, 2, detail['Balance'])
                data_row += 1
        # Net Profit
        if data['IndirectIncomeGreater']:
            ws.write(data_row, 0, 'Net Profit')
            ws.write(data_row, 1, '')
            ws.write(data_row, 2, Indirectdifference)
            data_row += 1
        else:
            ws.write(data_row, 0, '')
            ws.write(data_row, 1, '')
            ws.write(data_row, 2, '')
            data_row += 1

        # *****END******
        ws.write(data_row, 0, 'Total', total_label_style)
        ws.write(data_row, 1, '')
        ws.write(data_row, 2, data['TotalIndirect'])
        data_row += 1

        # ==========Direct Income==========
        data_col = 3
        data_row = 0
        ws.write(data_row, data_col, "Income", main_header_style)
        data_row += 1
        ws.write(data_row, data_col, "Group Name", main_header_style)
        data_col += 1
        ws.write(data_row, data_col, "Ledger Name", main_header_style)
        data_col += 1
        ws.write(data_row, data_col, "Amount", main_header_style)
        data_row += 1

        for i in data['DirectIncomeData'][0]:
            GroupName = i

            ws.write(data_row, 3, GroupName)
            for detail in data['DirectIncomeData'][0][i]:
                ws.write(data_row, 4, detail['LedgerName'])
                ws.write(data_row, 5, detail['Balance'])
                data_row += 1
        # ClosingStock
        ws.write(data_row, 3, 'ClosingStock')
        ws.write(data_row, 4, "")
        ws.write(data_row, 5, data['ClosingStock'])
        data_row += 1
        # Gross Profit
        if data['DirectExpenseGreater']:
            ws.write(data_row, 3, 'Gross Profit')
            ws.write(data_row, 4, '')
            ws.write(data_row, 5, Direct_difference)
            data_row += 1
        else:
            ws.write(data_row, 3, '')
            ws.write(data_row, 4, '')
            ws.write(data_row, 5, '')
            data_row += 1

        # *****END******
        ws.write(data_row, 3, 'Total', total_label_style)
        ws.write(data_row, 4, '')
        ws.write(data_row, 5, data['TotalDirect'])
        data_row += 1
        # Gross Loss
        if data['DirectIncomeGreater']:
            ws.write(data_row, 3, 'Gross Profit')
            ws.write(data_row, 4, '')
            ws.write(data_row, 5, Direct_difference)
            data_row += 1
        else:
            ws.write(data_row, 3, '')
            ws.write(data_row, 4, '')
            ws.write(data_row, 5, '')
            data_row += 1

        # ==========InDirect Income==========
        for i in data['IndirectIncomeData'][0]:
            GroupName = i

            ws.write(data_row, 3, GroupName)
            for detail in data['IndirectIncomeData'][0][i]:
                ws.write(data_row, 4, detail['LedgerName'])
                ws.write(data_row, 5, detail['Balance'])
                data_row += 1
        # Net Profit
        if data['IndirectExpenseGreater']:
            ws.write(data_row, 3, 'Net Profit')
            ws.write(data_row, 4, '')
            ws.write(data_row, 5, Indirectdifference)
            data_row += 1
        else:
            ws.write(data_row, 3, '')
            ws.write(data_row, 4, '')
            ws.write(data_row, 5, '')
            data_row += 1

        # *****END******
        ws.write(data_row, 3, 'Total', total_label_style)
        ws.write(data_row, 4, '')
        ws.write(data_row, 5, data['TotalIndirect'])
        data_row += 1


def balanceSheet_excel_data(CompanyID, CreatedUserID, PriceRounding, BranchID, ToDate, FromDate, request):
    if LedgerPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():

        TotalCoast = 0
        TotalAssets = 0
        TotalLiabilitis = 0
        test_arr = []
        instances = LedgerPosting.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)
        ledger_ids = instances.values_list('LedgerID')
        for ledger_id in ledger_ids:
            if ledger_id[0] not in test_arr:
                test_arr.append(ledger_id[0])
        if instances:
            account_ledger = AccountLedger.objects.filter(
                CompanyID=CompanyID, LedgerID__in=test_arr)
            serialized = BalanceSheetSerializer(
                account_ledger, many=True, context={"CompanyID": CompanyID, "FromDate": FromDate, "ToDate": ToDate})

            orderdDict = serialized.data
            jsnDatas = convertOrderdDict(orderdDict)

            Assets_Array = []
            Liabilitis_Array = []

            name_exist_liabilities = {}
            name_exist_detailed_liabilities = {}
            dic_exGrp_liabilities = {}
            final_liabilities_arr = []

            name_exist_asset = {}
            name_exist_detailed_asset = {}
            dic_exGrp_asset = {}
            final_asset_arr = []

            for i in jsnDatas:
                LedgerName = i['LedgerName']
                LedgerID = i['LedgerID']
                GroupUnder = i['GroupUnder']
                Balance = i['Balance']

                if GroupUnder == 'Assets':
                    Group_Under = AccountLedger.objects.get(
                        BranchID=BranchID, LedgerID=LedgerID, CompanyID=CompanyID).AccountGroupUnder
                    Group_name = AccountGroup.objects.get(
                        AccountGroupID=Group_Under, CompanyID=CompanyID).AccountGroupName

                    ledgerpost_ins = LedgerPosting.objects.filter(
                        LedgerID=LedgerID, Date__gte=FromDate, Date__lte=ToDate, CompanyID=CompanyID)

                    # for consolidated start
                    asset_Tot_Credit = 0
                    asset_Tot_Debit = 0
                    for lpi in ledgerpost_ins:
                        asset_Tot_Debit = + float(lpi.Debit)
                        asset_Tot_Credit = + float(lpi.Credit)
                        asset_balance = float(
                            asset_Tot_Debit) - float(asset_Tot_Credit)

                        dic_exGrp_asset = {"GroupName": str(
                            Group_name), "Balance": float(asset_balance)}

                    if not Group_name in name_exist_asset:
                        # name_exist.append(Group_name)
                        dic_exGrp_asset = {
                            "Balance": float(Balance)
                        }
                        name_exist_asset[Group_name] = dic_exGrp_asset
                    else:
                        b = name_exist_asset[Group_name]["Balance"]
                        name_exist_asset[Group_name]["Balance"] = b + \
                            float(Balance)

                    TotalAssets += Balance
                    Assets_dictionary = {"LedgerID": LedgerID, "LedgerName": LedgerName,
                                         "Balance": Balance, "GroupUnder": GroupUnder, }

                    # Assets_Array.append(Assets_dictionary)

                    if not Group_name in name_exist_detailed_asset:
                        name_exist_detailed_asset[Group_name] = []
                    name_exist_detailed_asset[Group_name].append(
                        Assets_dictionary)

                elif GroupUnder == 'Liabilitis':

                    Group_Under = AccountLedger.objects.get(
                        BranchID=BranchID, LedgerID=LedgerID, CompanyID=CompanyID).AccountGroupUnder
                    Group_name = AccountGroup.objects.get(
                        AccountGroupID=Group_Under, CompanyID=CompanyID).AccountGroupName

                    ledgerpost_ins = LedgerPosting.objects.filter(
                        LedgerID=LedgerID, Date__gte=FromDate, Date__lte=ToDate, CompanyID=CompanyID)

                    # for consolidated start
                    liabilites_Tot_Credit = 0
                    liabilites_Tot_Debit = 0
                    for lpi in ledgerpost_ins:
                        liabilites_Tot_Debit = + float(lpi.Debit)
                        liabilites_Tot_Credit = + float(lpi.Credit)
                    liablities_balance = float(
                        liabilites_Tot_Credit) - float(liabilites_Tot_Debit)

                    dic_exGrp_liabilities = {"GroupName": str(
                        Group_name), "Balance": float(liablities_balance)}

                    if float(Balance) <= 0:
                        Balance = abs(Balance)
                    else:
                        Balance = float(Balance) * -1

                    print(Balance)

                    if not Group_name in name_exist_liabilities:
                        # name_exist.append(Group_name)
                        dic_exGrp_liabilities = {
                            "Balance": float(Balance)
                        }
                        name_exist_liabilities[Group_name] = dic_exGrp_liabilities
                    else:
                        b = name_exist_liabilities[Group_name]["Balance"]
                        name_exist_liabilities[Group_name]["Balance"] = b + \
                            float(Balance)

                    TotalLiabilitis += Balance
                    Liabilitis_dictionary = {"LedgerID": LedgerID, "LedgerName": LedgerName,
                                             "Balance": Balance, "GroupUnder": GroupUnder, }

                    # Liabilitis_Array.append(Liabilitis_dictionary)

                    if not Group_name in name_exist_detailed_liabilities:
                        name_exist_detailed_liabilities[Group_name] = []
                    name_exist_detailed_liabilities[Group_name].append(
                        Liabilitis_dictionary)

            final_liabilities_arr.append(name_exist_liabilities)
            final_asset_arr.append(name_exist_asset)

            Liabilitis_Array.append(name_exist_detailed_liabilities)
            Assets_Array.append(name_exist_detailed_asset)

            if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
                stock_instances = StockRate.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)
                for stock_instance in stock_instances:
                    TotalCoast += stock_instance.Cost

        LiablityPCons = []
        for i in final_liabilities_arr[0]:
            myDic = {
                'GroupName': i,
                'Balance': float(final_liabilities_arr[0][i]['Balance'])
            }
            LiablityPCons.append(myDic)

        AssetCons = []
        for i in final_asset_arr[0]:
            myDic = {
                'GroupName': i,
                'Balance': float(final_asset_arr[0][i]['Balance'])
            }
            AssetCons.append(myDic)

        # opening balance difference

        total_debit_LoB = 0
        total_credit_LoB = 0
        ledger_instances_LoB = LedgerPosting.objects.filter(
            CompanyID=CompanyID, VoucherType='LOB', BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)
        for ledger_instance in ledger_instances_LoB:
            total_debit_LoB += ledger_instance.Debit
            total_credit_LoB += ledger_instance.Credit

        openingBalance_differece = 0
        if (total_debit_LoB > total_credit_LoB):
            openingBalance_differece = total_debit_LoB - total_credit_LoB
        elif(total_credit_LoB > total_debit_LoB):
            openingBalance_differece = total_credit_LoB - total_debit_LoB

        response_data = {
            "StatusCode": 6000,
            "AssetsData": Assets_Array,
            "LiabilitisData": Liabilitis_Array,
            "TotalAssets": TotalAssets,
            "TotalLiabilitis": TotalLiabilitis,
            "TotalCoast": TotalCoast,
            "AssetCons": AssetCons,
            "LiablityPCons": LiablityPCons,
            "openingBalance_difference": openingBalance_differece
        }
        return response_data
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "No Datas During this Time Periods!"
        }
        return response_data


def export_to_excel_balanceSheet(wb, data, profit_loss_data):
    ws = wb.add_sheet("ProfitAndLoss Report")
    print(profit_loss_data, "*************************************8")
    # xl sheet styles
    font = xlwt.Font()
    font.bold = True
    # font.height = 11 * 20

    main_header_style = xlwt.XFStyle()
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    main_header_style.alignment = center
    main_header_style.font = font

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

    total_label_style = xlwt.XFStyle()
    # font = xlwt.Font()
    # font.bold = True
    font.colour_index = 2
    total_label_style.font = font

    value_decimal_style = xlwt.XFStyle()
    value_decimal_style.num_format_str = '0.00'

    data_col = 0
    data_row = 0
    SlNo = 0

    IndirectExpenseGreater = profit_loss_data['IndirectExpenseGreater']
    IndirectIncomeGreater = profit_loss_data['IndirectIncomeGreater']
    if IndirectExpenseGreater:
        pass
    if IndirectIncomeGreater:
        pass
    # <<<<<<<<<<<<<<<<<<<CONSOLIDATED START HEARE>>>>>>>>>>>>>>>>>>>>>>>>>>
    # ---------Liabilities------------------
    ws.write(data_row, data_col, "Liabilities", main_header_style)
    data_row += 1
    ws.write(data_row, data_col, "Group Name", main_header_style)
    data_col += 1
    ws.write(data_row, data_col, "Amount", main_header_style)
    data_row += 1
    for i in data['LiablityPCons']:
        GroupName = i['GroupName']
        Balance = i['Balance']
        print(i)
        ws.write(data_row, 0, GroupName)
        ws.write(data_row, 1, Balance)
        data_row += 1
    # Net Profit
    if profit_loss_data['IndirectIncomeGreater']:
        ws.write(data_row, 0, 'Net Profit')
        ws.write(data_row, 1, profit_loss_data['Indirectdifference'])
        data_row += 1
    else:
        ws.write(data_row, 0, '')
        ws.write(data_row, 1, '')
        data_row += 1
    # *****Total Liabilities******
    ws.write(data_row, 0, 'Total', total_label_style)
    ws.write(data_row, 1, data['TotalLiabilitis'])
    # data_row+=1

    data_col = 2
    data_row = 0

    # ---------Assets------------------
    ws.write(data_row, data_col, "Assets", main_header_style)
    data_row += 1
    ws.write(data_row, data_col, "Group Name", main_header_style)
    data_col += 1
    ws.write(data_row, data_col, "Amount", main_header_style)
    data_row += 1
    # ==========Direct Assets==========
    for i in data['AssetCons']:
        GroupName = i['GroupName']
        Balance = i['Balance']
        print(i)
        ws.write(data_row, 2, GroupName)
        ws.write(data_row, 3, Balance)
        data_row += 1
    # *****Closing Stock******
    ws.write(data_row, 2, 'Closing Stock')
    ws.write(data_row, 3, profit_loss_data['ClosingStock'])
    # Net Loss
    if profit_loss_data['IndirectExpenseGreater']:
        data_row += 1
        ws.write(data_row, 2, 'Net Loss')
        ws.write(data_row, 3, profit_loss_data['Indirectdifference'])
    else:
        data_row += 1
        ws.write(data_row, 2, '')
        ws.write(data_row, 3, '')
    # *****Total Assets******
    data_row += 1
    ws.write(data_row, 2, 'Total', total_label_style)
    ws.write(data_row, 3, data['TotalAssets'])


def export_to_excel_profitAndLoss(wb, data, key):
    ws = wb.add_sheet("ProfitAndLoss Report")
    # xl sheet styles
    font = xlwt.Font()
    font.bold = True
    # font.height = 11 * 20

    main_header_style = xlwt.XFStyle()
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    main_header_style.alignment = center
    main_header_style.font = font

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

    total_label_style = xlwt.XFStyle()
    # font = xlwt.Font()
    # font.bold = True
    font.colour_index = 2
    total_label_style.font = font

    value_decimal_style = xlwt.XFStyle()
    value_decimal_style.num_format_str = '0.00'

    data_col = 0
    data_row = 0
    SlNo = 0

    # **********Gross Profit/Gross Loss && Net Profit/Net Loss**************
    Indirectdifference = data['Indirectdifference']
    Direct_difference = data['Direct_difference']
    # ************************

    # <<<<<<<<<<<<<<<<<<<CONSOLIDATED START HEARE>>>>>>>>>>>>>>>>>>>>>>>>>>
    if key == 1:
        # ---------Expence------------------
        ws.write(data_row, data_col, "Expense", main_header_style)
        data_row += 1
        ws.write(data_row, data_col, "Group Name", main_header_style)
        data_col += 1
        ws.write(data_row, data_col, "Amount", main_header_style)
        data_row += 1
        # ==========Direct Expence==========
        for i in data['profitAndLoss_final_data']:
            expence = i['expence']
            ws.write(data_row, 0, expence['name'])
            ws.write(data_row, 1, expence['balance'])
            data_row += 1
        # ---------Income------------------
        data_col = 2
        data_row = 0
        ws.write(data_row, data_col, "Income", main_header_style)
        data_row += 1
        ws.write(data_row, data_col, "Group Name", main_header_style)
        data_col += 1
        ws.write(data_row, data_col, "Amount", main_header_style)
        data_row += 1
        # ==========Direct Expence==========
        for i in data['profitAndLoss_final_data']:
            expence = i['income']
            ws.write(data_row, 2, expence['name'])
            ws.write(data_row, 3, expence['balance'])
            data_row += 1

    # <<<<<<<<<<<<<<<<<<<DETAILED START HEARE>>>>>>>>>>>>>>>>>>>>>>>>>>
    if key == 2:
        # # ==========Direct Expence==========
        ws.write(data_row, data_col, "Expense", main_header_style)
        data_row += 1
        ws.write(data_row, data_col, "Group Name", main_header_style)
        data_col += 1
        ws.write(data_row, data_col, "Ledger Name", main_header_style)
        data_col += 1
        ws.write(data_row, data_col, "Amount", main_header_style)
        data_row += 1
        # ==========Direct Expence==========
        for i in data['profitAndLoss_final_data']:
            expence = i['expence']
            ws.write(data_row, 0, expence['group_name'])
            ws.write(data_row, 1, expence['ledger_name'])
            ws.write(data_row, 2, expence['balance'])
            data_row += 1

        # # ==========Direct Income==========
        data_col = 3
        data_row = 0
        ws.write(data_row, data_col, "Income", main_header_style)
        data_row += 1
        ws.write(data_row, data_col, "Group Name", main_header_style)
        data_col += 1
        ws.write(data_row, data_col, "Ledger Name", main_header_style)
        data_col += 1
        ws.write(data_row, data_col, "Amount", main_header_style)
        data_row += 1
        # ==========Direct Income==========
        for i in data['profitAndLoss_final_data']:
            income = i['income']
            ws.write(data_row, 3, income['group_name'])
            ws.write(data_row, 4, income['ledger_name'])
            ws.write(data_row, 5, income['balance'])
            data_row += 1


def profitAndLoss_balancing(key, DirExPCons, DirIncCons, inDirExpCons, inDirIncCons, DirectIncomeGreater, DirectExpenseGreater, IndirectExpenseGreater, IndirectIncomeGreater, Indirectdifference, Direct_difference, TotalDirect, TotalIndirect, DirectExpensesData, InDirectExpensesData, DirectIncomeData, IndirectIncomeData, OpeningStock, ClosingStock):

    profitAndLoss_final_data = []

    if key == 1:
        # =========================================================
        if len(DirExPCons) >= len(DirIncCons):
            loop_count = len(DirExPCons)
        else:
            loop_count = len(DirIncCons)
        for i in range(loop_count):
            try:
                exp_name = DirExPCons[i]['GroupName']
            except:
                exp_name = "-"

            try:
                exp_balance = DirExPCons[i]['Balance']
            except:
                exp_balance = "-"

            try:
                inc_name = DirIncCons[i]['GroupName']
            except:
                inc_name = "-"

            try:
                inc_balance = DirIncCons[i]['Balance']
            except:
                inc_balance = "-"

            dic = {"expence": {'name': exp_name, 'balance': exp_balance},
                   "income": {"name": inc_name, "balance": inc_balance}}
            profitAndLoss_final_data.append(dic)
        # Gross Profit
        if DirectIncomeGreater:
            dic = {"expence": {'name': 'Gross Profit', 'balance': Direct_difference}, "income": {
                "name": "-", "balance": "-"}}
            profitAndLoss_final_data.append(dic)
        # Gross Loss
        elif DirectExpenseGreater:
            dic = {"expence": {'name': "-", 'balance': "-"},
                   "income": {"name": "Gross Loss", "balance": Direct_difference}}
            profitAndLoss_final_data.append(dic)

        # Total Direct
        dic = {"expence": {'name': 'Total', 'balance': TotalDirect},
               "income": {"name": "Total", "balance": TotalDirect}}
        profitAndLoss_final_data.append(dic)
        # ==========================
        if len(inDirExpCons) >= len(inDirIncCons):
            loop_count = len(inDirExpCons)
        else:
            loop_count = len(inDirIncCons)
        for i in range(loop_count):
            try:
                exp_name = inDirExpCons[i]['GroupName']
            except:
                exp_name = "-"

            try:
                exp_balance = inDirExpCons[i]['Balance']
            except:
                exp_balance = "-"

            try:
                inc_name = inDirIncCons[i]['GroupName']
            except:
                inc_name = "-"

            try:
                inc_balance = inDirIncCons[i]['Balance']
            except:
                inc_balance = "-"

            dic = {"expence": {'name': exp_name, 'balance': exp_balance},
                   "income": {"name": inc_name, "balance": inc_balance}}
            profitAndLoss_final_data.append(dic)
        print(DirectIncomeGreater)
        print(DirectExpenseGreater)

        # Net Profit
        if IndirectIncomeGreater:
            dic = {"expence": {'name': 'Net Profit', 'balance': Indirectdifference}, "income": {
                "name": "-", "balance": "-"}}
            profitAndLoss_final_data.append(dic)
        # Net Loss
        elif IndirectExpenseGreater:
            dic = {"expence": {'name': "-", 'balance': "-"},
                   "income": {"name": "Net Loss", "balance": Indirectdifference}}
            profitAndLoss_final_data.append(dic)

        # Total Direct
        dic = {"expence": {'name': 'Total', 'balance': TotalIndirect},
               "income": {"name": "Total", "balance": TotalIndirect}}
        profitAndLoss_final_data.append(dic)

        return profitAndLoss_final_data
    if key == 2:
        # empty_dic = {"-":[{"-":"-","-":"-","-":"-"}]}
        print(len(DirectExpensesData[0]), 'DirectExpensesData')
        print(len(DirectIncomeData[0]), 'DirectIncomeData')
        print(len(InDirectExpensesData[0]), 'InDirectExpensesData')
        print(len(IndirectIncomeData[0]), 'IndirectIncomeData')
        empty_dic = {"LedgerID": "-", "LedgerName": "-",
                     "Balance": "-", "GroupUnder": "-", }
        if len(DirectExpensesData[0]) >= len(DirectIncomeData[0]):
            loop_count1 = len(DirectIncomeData[0])
            loop_count = len(DirectExpensesData[0]) - loop_count1
            for mt in range(loop_count):
                DirectIncomeData[0][mt] = [mt]
                DirectIncomeData[0][mt].append(empty_dic)
        else:
            loop_count1 = len(DirectExpensesData[0])
            loop_count = len(DirectIncomeData[0]) - loop_count1
            for mt in range(loop_count):
                DirectExpensesData[0][mt] = [mt]
                DirectExpensesData[0][mt].append(empty_dic)

        if len(InDirectExpensesData[0]) >= len(IndirectIncomeData[0]):
            loop_count1 = len(IndirectIncomeData[0])
            loop_count = len(InDirectExpensesData[0]) - loop_count1
            for mt in range(loop_count):
                IndirectIncomeData[0][mt] = [mt]
                IndirectIncomeData[0][mt].append(empty_dic)
        else:
            loop_count1 = len(InDirectExpensesData[0])
            loop_count = len(IndirectIncomeData[0]) - loop_count1
            for mt in range(loop_count):
                InDirectExpensesData[0][mt] = [mt]
                InDirectExpensesData[0][mt].append(empty_dic)

        print(DirectExpensesData[0], DirectIncomeData[0])
        print(InDirectExpensesData[0], IndirectIncomeData[0])
        # ^^^^^^^^^^^^^^^^
        # Direct Start heare=======================
        # OpeningStock
        dic = {"expence": {'group_name': "OpeningStock", 'ledger_name': "-", 'balance': OpeningStock},
               "income": {"group_name": "-", 'ledger_name': "-", "balance": "-"}}
        profitAndLoss_final_data.append(dic)

        for (exp, inc) in itertools.zip_longest(DirectExpensesData[0], DirectIncomeData[0], fillvalue=""):
            try:
                exp_grp_name = exp
            except:
                exp_grp_name = "-"
            try:
                inc_grp_name = inc
            except:
                inc_grp_name = "-"
            if type(exp_grp_name) == int:
                exp_grp_name = "-"
            if type(inc_grp_name) == int:
                inc_grp_name = "-"
            print(type(exp_grp_name))
            print(type(inc_grp_name))
            dic = {"expence": {'group_name': exp_grp_name, 'ledger_name': "-", 'balance': "-"},
                   "income": {'group_name': inc_grp_name, 'ledger_name': "-", 'balance': "-"}}
            profitAndLoss_final_data.append(dic)
            for (exp_detail, inc_detail) in itertools.zip_longest(DirectExpensesData[0][exp], DirectIncomeData[0][inc], fillvalue=""):
                try:
                    exp_name = exp_detail['LedgerName']
                except:
                    exp_name = "-"
                try:
                    exp_balance = exp_detail['Balance']
                except:
                    exp_balance = "-"
                try:
                    inc_name = inc_detail['LedgerName']
                except:
                    inc_name = "-"
                try:
                    inc_balance = inc_detail['Balance']
                except:
                    inc_balance = "-"

                is_remove_empty = False
                if exp_name == "-" and inc_name == "-" and exp_balance == "-" and inc_balance == "-":
                    is_remove_empty = True
                dic = {"expence": {'group_name': "", 'ledger_name': exp_name, 'balance': exp_balance}, "income": {
                    'group_name': "-", 'ledger_name': inc_name, 'balance': inc_balance}}
                if not is_remove_empty:
                    profitAndLoss_final_data.append(dic)

        # ClosingStock
        dic = {"expence": {'group_name': "-", 'ledger_name': "-", 'balance': "-"},
               "income": {"group_name": "ClosingStock", 'ledger_name': "-", "balance": ClosingStock}}
        profitAndLoss_final_data.append(dic)
        # Gross Profit
        if DirectIncomeGreater:
            dic = {"expence": {'group_name': "Gross Profit", 'ledger_name': "-", 'balance': Direct_difference},
                   "income": {"group_name": "-", 'ledger_name': "-", "balance": "-"}}
            profitAndLoss_final_data.append(dic)
        # Gross Loss
        if DirectExpenseGreater:
            dic = {"expence": {'group_name': "-", 'ledger_name': "-", 'balance': "-"}, "income": {
                "group_name": "Gross Loss", 'ledger_name': "-", "balance": Direct_difference}}
            profitAndLoss_final_data.append(dic)
        # Total
        dic = {"expence": {'group_name': "Total", 'ledger_name': "-", 'balance': TotalDirect},
               "income": {"group_name": "Total", 'ledger_name': "-", "balance": TotalDirect}}
        profitAndLoss_final_data.append(dic)
        # ^^^^^^^^^^^^^^^

        # Indirect Start heare========================================
        # Gross Profit
        if DirectExpenseGreater:
            dic = {"expence": {'group_name': "Gross Loss", 'ledger_name': "-", 'balance': Direct_difference},
                   "income": {"group_name": "-", 'ledger_name': "-", "balance": "-"}}
            profitAndLoss_final_data.append(dic)
        # Gross Loss
        if DirectIncomeGreater:
            dic = {"expence": {'group_name': "-", 'ledger_name': "-", 'balance': "-"}, "income": {
                "group_name": "Gross Profit", 'ledger_name': "-", "balance": Direct_difference}}
            profitAndLoss_final_data.append(dic)

        for (exp, inc) in itertools.zip_longest(InDirectExpensesData[0], IndirectIncomeData[0], fillvalue=""):
            try:
                exp_grp_name = exp
            except:
                exp_grp_name = "-"
            try:
                inc_grp_name = inc
            except:
                inc_grp_name = "-"
            if type(exp_grp_name) == int:
                exp_grp_name = "-"
            if type(inc_grp_name) == int:
                inc_grp_name = "-"
            print(type(exp_grp_name))
            print(type(inc_grp_name))

            dic = {"expence": {'group_name': exp_grp_name, 'ledger_name': "-", 'balance': "-"},
                   "income": {'group_name': inc_grp_name, 'ledger_name': "-", 'balance': "-"}}
            profitAndLoss_final_data.append(dic)
            for (exp_detail, inc_detail) in itertools.zip_longest(InDirectExpensesData[0][exp], IndirectIncomeData[0][inc], fillvalue=""):
                try:
                    exp_name = exp_detail['LedgerName']
                except:
                    exp_name = "-"
                try:
                    exp_balance = exp_detail['Balance']
                except:
                    exp_balance = "-"
                try:
                    inc_name = inc_detail['LedgerName']
                except:
                    inc_name = "-"
                try:
                    inc_balance = inc_detail['Balance']
                except:
                    inc_balance = "-"

                is_remove_empty = False
                if exp_name == "-" and inc_name == "-" and exp_balance == "-" and inc_balance == "-":
                    is_remove_empty = True
                if not is_remove_empty:
                    dic = {"expence": {'group_name': "", 'ledger_name': exp_name, 'balance': exp_balance}, "income": {
                        'group_name': "-", 'ledger_name': inc_name, 'balance': inc_balance}}
                    profitAndLoss_final_data.append(dic)

        # Net Profit
        if IndirectIncomeGreater:
            dic = {"expence": {'group_name': "Net Profit", 'ledger_name': "-", 'balance': Indirectdifference},
                   "income": {'group_name': "-", 'ledger_name': "-", 'balance': "-"}}
            profitAndLoss_final_data.append(dic)
        # Net Loss
        elif IndirectExpenseGreater:
            dic = {"expence": {'group_name': "-", 'ledger_name': "-", 'balance': '-'},
                   "income": {'group_name': "Net Loss", 'ledger_name': "-", 'balance': Indirectdifference}}
            profitAndLoss_final_data.append(dic)

        # Total InDirect
        dic = {"expence": {'group_name': "Total", 'ledger_name': "-", 'balance': TotalIndirect},
               "income": {'group_name': "Total", 'ledger_name': "-", 'balance': TotalIndirect}}
        profitAndLoss_final_data.append(dic)

        return profitAndLoss_final_data


def balanceSheet_balancing(profit_loss_data, Assets_Array, Liabilitis_Array, TotalAssets, TotalLiabilitis, TotalCoast, AssetCons, LiablityPCons, openingBalance_differece):
    balanceSheet_final_CONSOLIDATED_data = []
    balanceSheet_final_DETAILED_data = []
    tot_assets = float(0)
    tot_liablity = float(0)
    # **************BALANCE SHEET CONSOLIDATE******************
    for (lib, ass) in itertools.zip_longest(LiablityPCons, AssetCons, fillvalue=""):
        try:
            lib_grp_name = lib['GroupName']
        except:
            lib_grp_name = "-"
        try:
            ass_grp_name = ass['GroupName']
        except:
            ass_grp_name = "-"
        try:
            lib_balance = lib['Balance']
            tot_liablity += float(lib_balance)
        except:
            lib_balance = "-"
        try:
            ass_balance = ass['Balance']
            tot_assets += float(ass_balance)
        except:
            ass_balance = "-"
        dic = {
            "liabilities": {'group_name': lib_grp_name, 'balance': lib_balance},
            "assets": {'group_name': ass_grp_name, 'balance': ass_balance}
        }
        balanceSheet_final_CONSOLIDATED_data.append(dic)
    # *****Closing Stock******
    dic = {
        "liabilities": {'group_name': "-", 'balance': "-"},
        "assets": {'group_name': "Closing Stock", 'balance': profit_loss_data['ClosingStock']}
    }
    tot_assets += float(profit_loss_data['ClosingStock'])
    balanceSheet_final_CONSOLIDATED_data.append(dic)
    # ******Net Profit*******

    if profit_loss_data['IndirectIncomeGreater']:
        dic = {
            "liabilities": {'group_name': 'Net Profit', 'balance': profit_loss_data['Indirectdifference']},
            "assets": {'group_name': '-', 'balance': '-'}
        }
        tot_liablity += float(profit_loss_data['Indirectdifference'])

        balanceSheet_final_CONSOLIDATED_data.append(dic)
    # ******Net Loss*******
    if profit_loss_data['IndirectExpenseGreater']:
        dic = {
            "liabilities": {'group_name': '-', 'balance': '-'},
            "assets": {'group_name': 'Net Loss', 'balance': profit_loss_data['Indirectdifference']}
        }
        tot_assets += float(profit_loss_data['Indirectdifference'])

        balanceSheet_final_CONSOLIDATED_data.append(dic)

    # *******Deffrence START*******
    defference = 0
    Total = 0
    if tot_liablity > tot_assets:
        Total = tot_liablity
        defference = float(tot_liablity)-float(tot_assets)
        dic = {
            "liabilities": {'group_name': '-', 'balance': '-'},
            "assets": {'group_name': 'Balance Difference', 'balance': defference}
        }
        balanceSheet_final_CONSOLIDATED_data.append(dic)
    elif tot_assets > tot_liablity:
        Total = tot_assets
        defference = float(tot_assets)-float(tot_liablity)
        dic = {
            "liabilities": {'group_name': 'Balance Difference', 'balance': defference},
            "assets": {'group_name': '-', 'balance': '-'},
        }
        balanceSheet_final_CONSOLIDATED_data.append(dic)
    elif tot_assets == tot_liablity:
        Total = tot_assets
        defference = float(tot_assets)-float(tot_liablity)
    # *******Deffrence END*******

    # ******* Total ******
    dic = {
        "liabilities": {'group_name': 'Total', 'balance': Total},
        "assets": {'group_name': 'Total', 'balance': Total}
    }
    balanceSheet_final_CONSOLIDATED_data.append(dic)

    # **************BALANCE SHEET DETAILED******************
    empty_dic = {"LedgerID": "-", "LedgerName": "-",
                 "Balance": "-", "GroupUnder": "-", }
    if len(Liabilitis_Array[0]) >= len(Assets_Array[0]):
        loop_count1 = len(Assets_Array[0])
        loop_count = len(Liabilitis_Array[0]) - loop_count1
        for mt in range(loop_count):
            Assets_Array[0][mt] = [mt]
            Assets_Array[0][mt].append(empty_dic)
    else:
        loop_count1 = len(Liabilitis_Array[0])
        loop_count = len(Assets_Array[0]) - loop_count1
        for mt in range(loop_count):
            Liabilitis_Array[0][mt] = [mt]
            Liabilitis_Array[0][mt].append(empty_dic)
    for (lib, ass) in itertools.zip_longest(Liabilitis_Array[0], Assets_Array[0], fillvalue=""):
        print(Liabilitis_Array[0][lib], Assets_Array[0][ass])
        try:
            lib_grp_name = lib
        except:
            lib_grp_name = "-"
        try:
            ass_grp_name = ass
        except:
            ass_grp_name = "-"
        if type(lib_grp_name) == int:
            lib_grp_name = "-"
        if type(ass_grp_name) == int:
            ass_grp_name = "-"
        dic = {
            "liabilities": {'group_name': lib_grp_name, 'ledger_name': "-", 'balance': "-"},
            "assets": {'group_name': ass_grp_name, 'ledger_name': "-", 'balance': "-"}
        }
        balanceSheet_final_DETAILED_data.append(dic)
        for (lib_detail, ass_detail) in itertools.zip_longest(Liabilitis_Array[0][lib], Assets_Array[0][ass], fillvalue=""):
            print(lib_detail, ass_detail)
            try:
                lib_name = lib_detail['LedgerName']
            except:
                lib_name = "-"
            try:
                lib_balance = lib_detail['Balance']
            except:
                lib_balance = "-"
            try:
                ass_name = ass_detail['LedgerName']
            except:
                ass_name = "-"
            try:
                ass_balance = ass_detail['Balance']
            except:
                ass_balance = "-"
            dic = {
                "liabilities": {'group_name': '-', 'ledger_name': lib_name, 'balance': lib_balance},
                "assets": {'group_name': '-', 'ledger_name': ass_name, 'balance': ass_balance}
            }
            print(type(lib_balance), lib_balance, 'UVAIS')
            print(type(ass_balance), ass_balance, 'THAMEEEM')
            if lib_balance == 0 or ass_balance == 0:
                print("ZEROOOOOOO UVIASS")
            balanceSheet_final_DETAILED_data.append(dic)
    # *****Closing Stock******
    dic = {
        "liabilities": {'group_name': '-', 'ledger_name': '-', 'balance': '-'},
        "assets": {'group_name': 'Closing Stock', 'ledger_name': '-', 'balance': profit_loss_data['ClosingStock']}
    }
    balanceSheet_final_DETAILED_data.append(dic)
    # *****Net Profit******
    if profit_loss_data['IndirectIncomeGreater']:
        dic = {
            "liabilities": {'group_name': 'Net Profit', 'ledger_name': '-', 'balance': profit_loss_data['Indirectdifference']},
            "assets": {'group_name': '-', 'ledger_name': '-', 'balance': '-'}
        }
        balanceSheet_final_DETAILED_data.append(dic)
    # *****Net Loss******
    if profit_loss_data['IndirectExpenseGreater']:
        dic = {
            "liabilities": {'group_name': '-', 'ledger_name': '-', 'balance': '-'},
            "assets": {'group_name': 'Net Loss', 'ledger_name': '-', 'balance': profit_loss_data['Indirectdifference']},
        }
        balanceSheet_final_DETAILED_data.append(dic)
    # *******Deffrence START*******
    if tot_liablity > tot_assets:
        dic = {
            "liabilities": {'group_name': '-', 'ledger_name': '-', 'balance': '-'},
            "assets": {'group_name': 'Balance Difference', 'ledger_name': '-', 'balance': defference}
        }
        balanceSheet_final_DETAILED_data.append(dic)
    elif tot_assets > tot_liablity:

        dic = {
            "liabilities": {'group_name': 'Balance Difference', 'ledger_name': '-', 'balance': defference},
            "assets": {'group_name': '-', 'ledger_name': '-', 'balance': '-'},
        }
        balanceSheet_final_DETAILED_data.append(dic)
    # *******Deffrence END*******

    # ******* Total ******
    dic = {
        "liabilities": {'group_name': 'Total', 'ledger_name': '-', 'balance': Total},
        "assets": {'group_name': 'Total', 'ledger_name': '-', 'balance': Total}
    }
    balanceSheet_final_DETAILED_data.append(dic)
    return [balanceSheet_final_CONSOLIDATED_data, balanceSheet_final_DETAILED_data]


def DayBook_excel_data(CompanyID, BranchID, Date, PriceRounding, Type):
    if LedgerPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date=Date).exists():
        ledger_instances = LedgerPosting.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Date=Date)
        voucher_types = ledger_instances.values_list('VoucherType')
        test_arr = []

        summary_final_all = []
        summary_final_modi = []
        summary_final_Delt = []
        detailed_final = []
        for voucherType in voucher_types:
            if voucherType[0] not in test_arr:
                test_arr.append(voucherType[0])

        for ta in test_arr:
            ledger_voucher_group_instances = ledger_instances.filter(
                VoucherType=ta)
            ledger_voucher_instances_modi = ledger_instances.filter(
                VoucherType=ta, Action='M')
            ledger_voucher_instances_Delt = LedgerPosting_Log.objects.filter(
                VoucherType=ta, Action='D', CompanyID=CompanyID, BranchID=BranchID, Date=Date)
            # count1 = ledger_voucher_group_instances.count()
            list_byID = ledger_voucher_group_instances.values_list(
                'VoucherMasterID', flat=True)
            not_dupli_list_byID = []
            [not_dupli_list_byID.append(
                x) for x in list_byID if x not in not_dupli_list_byID]
            count = len(not_dupli_list_byID)

            list_byID_modi = ledger_voucher_instances_modi.values_list(
                'VoucherMasterID', flat=True)
            not_dupli_list_byID_modi = []
            [not_dupli_list_byID_modi.append(
                x) for x in list_byID_modi if x not in not_dupli_list_byID_modi]
            count_modi = len(not_dupli_list_byID_modi)

            list_byID_delt = ledger_voucher_instances_Delt.values_list(
                'VoucherMasterID', flat=True)
            not_dupli_list_byID_delt = []
            [not_dupli_list_byID_delt.append(
                x) for x in list_byID_delt if x not in not_dupli_list_byID_delt]
            count_delt = len(not_dupli_list_byID_delt)
            print("not_dupli_list_byID_delt=======================")
            print(ta)
            print(not_dupli_list_byID_delt)
            vouch_list = []
            if ta == "SI":
                sales_instances = SalesMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, SalesMasterID__in=not_dupli_list_byID)
                sales_instances_modif = SalesMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, SalesMasterID__in=not_dupli_list_byID_modi)
                sales_instances_delt = SalesMaster_Log.objects.filter(
                    CompanyID=CompanyID, Action="D", BranchID=BranchID, TransactionID__in=not_dupli_list_byID_delt)
                summary_count = sales_instances.count()
                summary_count_modif = sales_instances_modif.count()
                summary_count_delt = sales_instances_delt.count()
                sales_grand_total = sales_instances.aggregate(
                    Sum('GrandTotal'))
                grand_total = sales_grand_total['GrandTotal__sum']
                sales_grand_total_modif = sales_instances_modif.aggregate(
                    Sum('GrandTotal'))
                grand_total_modif = sales_grand_total_modif['GrandTotal__sum']
                sales_grand_total_delt = sales_instances_delt.aggregate(
                    Sum('GrandTotal'))
                grand_total_delt = sales_grand_total_delt['GrandTotal__sum']
                vouch_list.append(ta)
            elif ta == "PI":
                purchase_instances = PurchaseMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, PurchaseMasterID__in=not_dupli_list_byID)
                purchase_instances_modif = PurchaseMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, PurchaseMasterID__in=not_dupli_list_byID_modi)
                purchase_instances_delt = PurchaseMaster_Log.objects.filter(
                    CompanyID=CompanyID, Action="D", BranchID=BranchID, TransactionID__in=not_dupli_list_byID_delt)
                summary_count = purchase_instances.count()
                summary_count_modif = purchase_instances_modif.count()
                summary_count_delt = purchase_instances_delt.count()
                purchase_grand_total = purchase_instances.aggregate(
                    Sum('GrandTotal'))
                grand_total = purchase_grand_total['GrandTotal__sum']
                purchase_grand_total_modif = purchase_instances_modif.aggregate(
                    Sum('GrandTotal'))
                grand_total_modif = purchase_grand_total_modif['GrandTotal__sum']
                purchase_grand_total_delt = purchase_instances_delt.aggregate(
                    Sum('GrandTotal'))
                grand_total_delt = purchase_grand_total_delt['GrandTotal__sum']
                vouch_list.append(ta)
            elif ta == "SR":
                sales_return_instances = SalesReturnMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, SalesReturnMasterID__in=not_dupli_list_byID)
                sales_return_instances_modif = SalesReturnMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, SalesReturnMasterID__in=not_dupli_list_byID_modi)
                sales_return_instances_delt = SalesReturnMaster_Log.objects.filter(
                    CompanyID=CompanyID, Action="D", BranchID=BranchID, TransactionID__in=not_dupli_list_byID_delt)
                summary_count = sales_return_instances.count()
                summary_count_modif = sales_return_instances_modif.count()
                summary_count_delt = sales_return_instances_delt.count()
                sales_return_grand_total = sales_return_instances.aggregate(
                    Sum('GrandTotal'))
                grand_total = sales_return_grand_total['GrandTotal__sum']
                sales_return_grand_total_modif = sales_return_instances_modif.aggregate(
                    Sum('GrandTotal'))
                grand_total_modif = sales_return_grand_total_modif['GrandTotal__sum']
                sales_return_grand_total_delt = sales_return_instances_delt.aggregate(
                    Sum('GrandTotal'))
                grand_total_delt = sales_return_grand_total_delt['GrandTotal__sum']
                vouch_list.append(ta)
            elif ta == "PR":
                purchase_return_instances = PurchaseReturnMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, PurchaseReturnMasterID__in=not_dupli_list_byID)
                purchase_return_instances_modif = PurchaseReturnMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, PurchaseReturnMasterID__in=not_dupli_list_byID_modi)
                purchase_return_instances_delt = PurchaseReturnMaster_Log.objects.filter(
                    CompanyID=CompanyID, Action="D", BranchID=BranchID, TransactionID__in=not_dupli_list_byID_delt)
                summary_count = purchase_return_instances.count()
                summary_count_modif = purchase_return_instances_modif.count()
                summary_count_delt = purchase_return_instances_delt.count()
                purchase_return_grand_total = purchase_return_instances.aggregate(
                    Sum('GrandTotal'))
                grand_total = purchase_return_grand_total['GrandTotal__sum']
                purchase_return_grand_total_modif = purchase_return_instances_modif.aggregate(
                    Sum('GrandTotal'))
                grand_total_modif = purchase_return_grand_total_modif['GrandTotal__sum']
                purchase_return_grand_total_delt = purchase_return_instances_delt.aggregate(
                    Sum('GrandTotal'))
                grand_total_delt = purchase_return_grand_total_delt['GrandTotal__sum']
                vouch_list.append(ta)
            elif ta == "CP" or ta == "BP":
                payment_instances = PaymentMaster.objects.filter(
                    CompanyID=CompanyID, VoucherType=ta, BranchID=BranchID, PaymentMasterID__in=not_dupli_list_byID)
                payment_instances_modif = PaymentMaster.objects.filter(
                    CompanyID=CompanyID, VoucherType=ta, BranchID=BranchID, PaymentMasterID__in=not_dupli_list_byID_modi)
                payment_instances_delt = PaymentMaster_Log.objects.filter(
                    CompanyID=CompanyID, VoucherType=ta, Action="D", BranchID=BranchID, TransactionID__in=not_dupli_list_byID_delt)
                summary_count = payment_instances.count()
                summary_count_modif = payment_instances_modif.count()
                summary_count_delt = payment_instances_delt.count()
                payment_grand_total = payment_instances.aggregate(
                    Sum('TotalAmount'))
                grand_total = payment_grand_total['TotalAmount__sum']
                payment_grand_total_modif = payment_instances_modif.aggregate(
                    Sum('TotalAmount'))
                grand_total_modif = payment_grand_total_modif['TotalAmount__sum']
                payment_grand_total_delt = payment_instances_delt.aggregate(
                    Sum('TotalAmount'))
                grand_total_delt = payment_grand_total_delt['TotalAmount__sum']
                vouch_list.append(ta)
            elif ta == "CR" or ta == "BR":
                receipt_instances = ReceiptMaster.objects.filter(
                    CompanyID=CompanyID, VoucherType=ta, BranchID=BranchID, ReceiptMasterID__in=not_dupli_list_byID)
                receipt_instances_modif = ReceiptMaster.objects.filter(
                    CompanyID=CompanyID, VoucherType=ta, BranchID=BranchID, ReceiptMasterID__in=not_dupli_list_byID_modi)
                receipt_instances_delt = ReceiptMaster_Log.objects.filter(
                    CompanyID=CompanyID, VoucherType=ta, Action="D", BranchID=BranchID, TransactionID__in=not_dupli_list_byID_delt)
                summary_count = receipt_instances.count()
                summary_count_modif = receipt_instances_modif.count()
                summary_count_delt = receipt_instances_delt.count()
                receipt_grand_total = receipt_instances.aggregate(
                    Sum('TotalAmount'))
                grand_total = receipt_grand_total['TotalAmount__sum']
                receipt_grand_total_modif = receipt_instances_modif.aggregate(
                    Sum('TotalAmount'))
                grand_total_modif = receipt_grand_total_modif['TotalAmount__sum']
                receipt_grand_total_delt = receipt_instances_delt.aggregate(
                    Sum('TotalAmount'))
                grand_total_delt = receipt_grand_total_delt['TotalAmount__sum']
                vouch_list.append(ta)

            VoucherName = get_VoucherName(ta)
            if summary_count > 0 and ta in vouch_list:
                summary_dic = {
                    'particular': VoucherName,
                    'trans_count': summary_count,
                    'Amount': grand_total
                }
                summary_final_all.append(summary_dic)

            if summary_count_modif > 0 and ta in vouch_list:
                summary_dic_modi = {
                    'particular': VoucherName,
                    'trans_count': summary_count_modif,
                    'Amount': grand_total_modif
                }
                summary_final_modi.append(summary_dic_modi)

            if summary_count_delt > 0 and ta in vouch_list:
                summary_dic_dlt = {
                    'particular': VoucherName,
                    'trans_count': summary_count_delt,
                    'Amount': grand_total_delt
                }
                summary_final_Delt.append(summary_dic_dlt)

            # list_byID_modi = ledger_voucher_instances_modi.values_list(
            #             'VoucherMasterID', flat=True)
            # not_dupli_list_byID_modi = []
            # [not_dupli_list_byID_modi.append(x) for x in list_byID_modi if x not in not_dupli_list_byID_modi]
            # count_modi = len(not_dupli_list_byID_modi)

            # count_modi = ledger_voucher_instances_modi.count()
            # list_byID_delt = ledger_voucher_instances_Delt.values_list(
            #             'VoucherMasterID', flat=True)
            # not_dupli_list_byID_delt = []
            # [not_dupli_list_byID_delt.append(x) for x in list_byID_delt if x not in not_dupli_list_byID_delt]
            # count_delt = len(not_dupli_list_byID_delt)

            # count_delt = ledger_voucher_instances_Delt.count()
            # Amount = 0
            # Amount_modi = 0
            # Amount_delt = 0
            # VoucherName = get_VoucherName(ta)
            # if count > 0:
            #     total_debit_daybk = ledger_voucher_group_instances.aggregate(Sum('Debit'))
            #     total_debit_daybk = total_debit_daybk['Debit__sum']
            #     total_credit = ledger_voucher_group_instances.aggregate(Sum('Credit'))
            #     total_credit = total_credit['Credit__sum']
            #     Amount = float(total_debit_daybk) - float(total_credit)
            #     # for lgp in ledger_voucher_group_instances:
            #     #     Amount += lgp.Debit
            #     summary_dic = {
            #         'particular': VoucherName,
            #         'trans_count': count,
            #         'Amount': total_debit_daybk
            #     }
            #     summary_final_all.append(summary_dic)

            # if count_modi > 0:
            #     total_debit_daybk_modi = ledger_voucher_instances_modi.aggregate(Sum('Debit'))
            #     total_debit_daybk_modi = total_debit_daybk_modi['Debit__sum']
            #     total_credit_modi = ledger_voucher_instances_modi.aggregate(Sum('Credit'))
            #     total_credit_modi = total_credit_modi['Credit__sum']
            #     Amount_modi = float(total_debit_daybk_modi) - float(total_credit_modi)
            #     # for lmd in ledger_voucher_instances_modi:
            #     #     Amount_modi += lmd.Debit
            #     summary_dic_modi = {
            #         'particular': VoucherName,
            #         'trans_count': count_modi,
            #         'Amount': total_debit_daybk_modi
            #     }
            #     summary_final_modi.append(summary_dic_modi)

            # if count_delt > 0:
            #     total_debit_daybk_delt = ledger_voucher_instances_Delt.aggregate(Sum('Debit'))
            #     total_debit_daybk_delt = total_debit_daybk_delt['Debit__sum']
            #     total_credit_modi_delt = ledger_voucher_instances_Delt.aggregate(Sum('Credit'))
            #     total_credit_modi_delt = total_credit_modi_delt['Credit__sum']
            #     Amount_delt = float(total_debit_daybk_delt) - float(total_credit_modi_delt)
            #     # for ldt in ledger_voucher_instances_Delt:
            #     #     Amount_delt += ldt.Debit
            #     summary_dic_dlt = {
            #         'particular': VoucherName,
            #         'trans_count': count_delt,
            #         'Amount': total_debit_daybk_delt
            #     }
            #     summary_final_Delt.append(summary_dic_dlt)

            # summary end here

            ledger_ids = ledger_voucher_group_instances.values_list('LedgerID')
            test_arr_ledger = []
            for ledger_id in ledger_ids:
                if ledger_id[0] not in test_arr_ledger:
                    test_arr_ledger.append(ledger_id[0])

            account_ledger_insts = AccountLedger.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID__in=test_arr_ledger)

            for al in account_ledger_insts:
                LedgerName = al.LedgerName
                ledgers_byId = ledger_instances.filter(
                    LedgerID=al.LedgerID, VoucherType=ta)

                # detail_count = ledgers_byId.count()
                list_byID_detail = ledgers_byId.values_list(
                    'VoucherMasterID', flat=True)
                not_dupli_list_byID_detail = []
                [not_dupli_list_byID_detail.append(
                    x) for x in list_byID_detail if x not in not_dupli_list_byID_detail]
                detail_count = len(not_dupli_list_byID_detail)

                detail_amt = 0
                total_debit_daybk_ = ledgers_byId.aggregate(Sum('Debit'))
                total_debit_daybk_ = total_debit_daybk_['Debit__sum']
                total_credit_modi_ = ledgers_byId.aggregate(Sum('Credit'))
                total_credit_modi_ = total_credit_modi_['Credit__sum']
                detail_amt = float(total_debit_daybk_) - \
                    float(total_credit_modi_)
                # for ldgs in ledgers_byId:
                #     detail_amt += ldgs.Debit
                detaild_dic = {
                    'particular': VoucherName,
                    'LedgerName': LedgerName,
                    'LedgerID': al.LedgerID,
                    'trans_count': detail_count,
                    'Amount': detail_amt
                }
                detailed_final.append(detaild_dic)
             # New Design Function Start
            summary_final = []
            toatl__label_dic = {
                'particular': "Total Active Transactions",
                'trans_count': "",
                'Amount': ""
            }
            modified__label_dic = {
                'particular': "Modified Transactions",
                'trans_count': "",
                'Amount': ""
            }
            deleted__label_dic = {
                'particular': "Deleted Transactions",
                'trans_count': "",
                'Amount': ""
            }
            if summary_final_all:
                summary_final.append(toatl__label_dic)
                for i in summary_final_all:
                    summary_final.append(i)
            if summary_final_modi:
                summary_final.append(modified__label_dic)
                for i in summary_final_modi:
                    summary_final.append(i)
            if summary_final_Delt:
                summary_final.append(deleted__label_dic)
                for i in summary_final_Delt:
                    summary_final.append(i)

            # New Design Function End
        response_data = {
            "StatusCode": 6000,
            "summary_final_all": summary_final_all,
            "summary_final_modi": summary_final_modi,
            "summary_final_Delt": summary_final_Delt,
            "detailed_final": detailed_final,
            "summary_final": summary_final,
        }
        return response_data

    elif LedgerPosting_Log.objects.filter(Action='D', CompanyID=CompanyID, BranchID=BranchID, Date=Date).exists():
        ledgerLog_instances = LedgerPosting_Log.objects.filter(
            Action='D', CompanyID=CompanyID, BranchID=BranchID, Date=Date)
        voucher_types = ledgerLog_instances.values_list('VoucherType')
        test_arr = []
        summary_final_Delt = []
        for voucherType in voucher_types:
            if voucherType[0] not in test_arr:
                test_arr.append(voucherType[0])

        for ta in test_arr:
            ledger_voucher_instances_Delt = ledgerLog_instances.filter(
                VoucherType=ta)
            # count_delt = ledger_voucher_instances_Delt.count()
            list_byID_delt = ledger_voucher_instances_Delt.values_list(
                'VoucherMasterID', flat=True)
            not_dupli_list_byID_delt = []
            [not_dupli_list_byID_delt.append(
                x) for x in list_byID_delt if x not in not_dupli_list_byID_delt]

            vouch_list = []
            if ta == "SI":
                sales_instances_delt = SalesMaster_Log.objects.filter(
                    CompanyID=CompanyID, Action="D", BranchID=BranchID, TransactionID__in=not_dupli_list_byID_delt)
                summary_count_delt = sales_instances_delt.count()
                sales_grand_total_delt = sales_instances_delt.aggregate(
                    Sum('GrandTotal'))
                grand_total_delt = sales_grand_total_delt['GrandTotal__sum']
                vouch_list.append(ta)
            elif ta == "PI":
                purchase_instances_delt = PurchaseMaster_Log.objects.filter(
                    CompanyID=CompanyID, Action="D", BranchID=BranchID, TransactionID__in=not_dupli_list_byID_delt)
                summary_count_delt = purchase_instances_delt.count()
                purchase_grand_total_delt = purchase_instances_delt.aggregate(
                    Sum('GrandTotal'))
                grand_total_delt = purchase_grand_total_delt['GrandTotal__sum']
                vouch_list.append(ta)
            elif ta == "SR":
                sales_return_instances_delt = SalesReturnMaster_Log.objects.filter(
                    CompanyID=CompanyID, Action="D", BranchID=BranchID, TransactionID__in=not_dupli_list_byID_delt)
                summary_count_delt = sales_return_instances_delt.count()
                sales_return_grand_total_delt = sales_return_instances_delt.aggregate(
                    Sum('GrandTotal'))
                grand_total_delt = sales_return_grand_total_delt['GrandTotal__sum']
                vouch_list.append(ta)
            elif ta == "PR":
                purchase_return_instances_delt = PurchaseReturnMaster_Log.objects.filter(
                    CompanyID=CompanyID, Action="D", BranchID=BranchID, TransactionID__in=not_dupli_list_byID_delt)
                summary_count_delt = purchase_return_instances_delt.count()
                purchase_return_grand_total_delt = purchase_return_instances_delt.aggregate(
                    Sum('GrandTotal'))
                grand_total_delt = purchase_return_grand_total_delt['GrandTotal__sum']
                vouch_list.append(ta)
            elif ta == "CP" or ta == "BP":
                payment_instances_delt = PaymentMaster_Log.objects.filter(
                    CompanyID=CompanyID, VoucherType=ta, Action="D", BranchID=BranchID, TransactionID__in=not_dupli_list_byID_delt)
                summary_count_delt = payment_instances_delt.count()
                payment_grand_total_delt = payment_instances_delt.aggregate(
                    Sum('TotalAmount'))
                grand_total_delt = payment_grand_total_delt['TotalAmount__sum']
                vouch_list.append(ta)
            elif ta == "CR" or ta == "BR":
                receipt_instances_delt = ReceiptMaster_Log.objects.filter(
                    CompanyID=CompanyID, VoucherType=ta, Action="D", BranchID=BranchID, TransactionID__in=not_dupli_list_byID_delt)
                summary_count_delt = receipt_instances_delt.count()
                receipt_grand_total_delt = receipt_instances_delt.aggregate(
                    Sum('TotalAmount'))
                grand_total_delt = receipt_grand_total_delt['TotalAmount__sum']
                vouch_list.append(ta)

            VoucherName = get_VoucherName(ta)

            if summary_count_delt > 0 and ta in vouch_list:
                summary_dic_dlt = {
                    'particular': VoucherName,
                    'trans_count': summary_count_delt,
                    'Amount': grand_total_delt
                }
                summary_final_Delt.append(summary_dic_dlt)

            # count_delt = len(not_dupli_list_byID_delt)
            # Amount_delt = 0
            # VoucherName = get_VoucherName(ta)

            # if count_delt > 0:
            #     total_debit_daybk_delt = ledger_voucher_instances_Delt.aggregate(Sum('Debit'))
            #     total_credit_modi_delt = ledger_voucher_instances_Delt.aggregate(Sum('Credit'))
            #     Amount_delt = float(total_debit_daybk_delt) - float(total_credit_modi_delt)
            #     # for ldt in ledger_voucher_instances_Delt:
            #     #     Amount_delt += ldt.Debit
            #     summary_dic_dlt = {
            #         'particular': VoucherName,
            #         'trans_count': count_delt,
            #         'Amount': Amount_delt
            #     }
            #     summary_final_Delt.append(summary_dic_dlt)
        response_data = {
            "StatusCode": 6000,
            "summary_final_all": [],
            "summary_final_modi": [],
            "summary_final_Delt": summary_final_Delt,
            "detailed_final": []
        }
        return response_data

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "No Datas on this day!"
        }
        return response_data


def export_to_excel_DayBook(wb, data, Type, title):
    ws = wb.add_sheet("DayBook Report")
    # xl sheet styles

    # column value alighn center
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER

    label_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True
    font.colour_index = 2
    label_style.font = font

    header_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True
    header_style.font = font

    main_title = xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True
    main_title.font = font
    main_title.alignment = center

    value_decimal_style = xlwt.XFStyle()
    value_decimal_style.num_format_str = '0.00'

    data_col = 0
    data_row = 2
    SlNo = 0

    if Type == '1':
        ws.write_merge(0, 0, 0, 2, title, main_title)
        # ==========Day book Summary==========
        columns = ['Particular', 'Trans Count', 'Amount']
        row_num = 1
        # HEADING
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], header_style)

        # Contents
        for i in data['summary_final']:
            try:
                particular = i['particular']
            except:
                particular = '-'
            try:
                trans_count = i['trans_count']
            except:
                trans_count = '-'
            try:
                amt = i['Amount']
                Amount = float(amt)
            except:
                Amount = '-'
            if particular == 'Total Active Transactions' or particular == 'Modified Transactions' or particular == 'Deleted Transactions':
                ws.write(data_row, 0, particular, label_style)
            else:
                ws.write(data_row, 0, particular)
            ws.write(data_row, 1, trans_count)
            ws.write(data_row, 3, Amount, value_decimal_style)
            data_row += 1
    else:
        ws.write_merge(0, 0, 0, 3, title, main_title)
        # ==========Day book Detail==========
        columns = ['Particular', 'Ledger Name', 'Trans Count', 'Amount']
        row_num = 1
        # HEADING
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], header_style)

        for i in data['detailed_final']:
            try:
                particular = i['particular']
            except:
                particular = '-'
            try:
                LedgerName = i['LedgerName']
            except:
                LedgerName = '-'
            try:
                trans_count = i['trans_count']
            except:
                trans_count = '-'
            try:
                amt = i['Amount']
                Amount = float(amt)
            except:
                Amount = '-'

            ws.write(data_row, 0, particular)
            ws.write(data_row, 1, LedgerName)
            ws.write(data_row, 2, trans_count)
            ws.write(data_row, 3, Amount, value_decimal_style)
            data_row += 1


def outStandingReport_excel_data(CompanyID, BranchID, PriceRounding, RouteLedgers, ToDate, Type):
    ledger_id_list = []
    if Parties.objects.filter(CompanyID=CompanyID, BranchID=BranchID, RouteID__in=RouteLedgers).exists():
        party_ins = Parties.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, RouteID__in=RouteLedgers)
        for i in party_ins:
            ledger_id_list.append(i.LedgerID)
    else:
        party_ins = Parties.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID)
        for i in party_ins:
            ledger_id_list.append(i.LedgerID)

    test_arr = []
    final_arr = []
    new_final_arr = []
    if LedgerPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerID__in=ledger_id_list, Date__lte=ToDate).exists():
        ledger_instances = LedgerPosting.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID__in=ledger_id_list, Date__lte=ToDate)

        ledger_ids = ledger_instances.values_list('LedgerID')
        for ledger_id in ledger_ids:
            if ledger_id[0] not in test_arr:
                test_arr.append(ledger_id[0])

        account_ledgers = AccountLedger.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID__in=test_arr)
        serialized = LedgerReportSerializer(account_ledgers, many=True, context={
            "CompanyID": CompanyID, "PriceRounding": PriceRounding})
        jsnDatas = convertOrderdDict(serialized.data)
        tot_Debit = 0
        tot_Credit = 0
        for i in jsnDatas:
            if Type == "null":
                print(Type, "UUUUUUUUUUUu", type(Type))
                tot_Debit += i['Debit']
                tot_Credit += i['Credit']
                final_arr.append(i)
                new_final_arr.append(i)

            elif Type == "creditors":
                if i['Debit'] == 0 and i['Credit'] > 0:
                    final_arr.append(i)
                    new_final_arr.append(i)

                    tot_Debit += i['Debit']
                    tot_Credit += i['Credit']
            elif Type == "debitors":
                if i['Debit'] > 0 and i['Credit'] == 0:
                    final_arr.append(i)
                    new_final_arr.append(i)

                    tot_Debit += i['Debit']
                    tot_Credit += i['Credit']
            elif Type == "zero_balance":
                if i['Debit'] == 0 and i['Credit'] == 0:
                    final_arr.append(i)
                    new_final_arr.append(i)

                    tot_Debit += i['Debit']
                    tot_Credit += i['Credit']
        total_dic = {
            "LedgerName": "Total",
            "Debit": tot_Debit,
            "Credit": tot_Credit,
        }
        final_arr.append(total_dic)

        response_data = {
            "StatusCode": 6000,
            "data": final_arr,
            "new_data": new_final_arr,
            "total": total_dic,
        }
        return response_data

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "No Datas During This Time!"
        }
        return response_data


def export_to_excel_outStandingReport(wb, data, title, Type):
    ws = wb.add_sheet("OutStanding Report")
    print(Type, "*************************************8")
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

    ws.write_merge(0, 0, 0, 2, title, main_title)

    columns = ['SlNo', 'Ledger Name', 'Debit', 'Credit']
    row_num = 1
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], sub_header_style)

    data_col = 0
    data_row = 2
    SlNo = 0

    for j in data['data']:

        LedgerName = j['LedgerName']
        Debit = j['Debit']
        Credit = j['Credit']

        SlNo += 1

        ws.write(data_row, 0, SlNo)
        if LedgerName == "Total":
            ws.write(data_row, 1, LedgerName, total_label_style)
        else:
            ws.write(data_row, 1, LedgerName)

        ws.write(data_row, 2, Debit, value_decimal_style)
        ws.write(data_row, 3, Credit, value_decimal_style)
        data_row += 1
