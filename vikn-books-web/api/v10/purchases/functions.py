import datetime
import random
import string
from decimal import Decimal

import xlwt
from django.db.models import Max
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from sqlalchemy import null
from xlwt import Alignment, Borders, Font, Pattern, Workbook, XFStyle, easyxf

from api.v4.ledgerPosting.functions import convertOrderdDict
from api.v10.products.functions import get_auto_AutoBatchCode
from api.v10.purchaseReturns.serializers import PurchaseReturnMasterRestSerializer
from api.v10.purchases.serializers import (
    PurchaseDetailsRestSerializer,
    PurchaseDetailsSerializer,
    PurchaseMasterForReturnSerializer,
    PurchaseMasterReportSerializer,
    PurchaseMasterRest1Serializer,
    PurchaseMasterRestSerializer,
    PurchaseMasterSerializer,
)
from brands import models as table
from brands.models import (
    AccountLedger,
    AccountLedger_Log,
    Batch,
    Brand,
    GeneralSettings,
    LedgerPosting,
    LedgerPosting_Log,
    OpeningStockMaster,
    Parties,
    PriceList,
    Product,
    ProductGroup,
    PurchaseDetails,
    PurchaseDetails_Log,
    PurchaseDetailsDummy,
    PurchaseMaster,
    PurchaseMaster_Log,
    PurchaseOrderMaster,
    PurchaseReturnDetails,
    PurchaseReturnMaster,
    State,
    StockPosting,
    StockPosting_Log,
    StockRate,
    StockTrans,
    Unit,
    UserTable,
    VoucherNoTable,
    Warehouse,
)
from main.functions import converted_float, guess_date


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
    PurchaseMasterID = 1

    if model.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        max_value = model.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID
        ).aggregate(Max("PurchaseMasterID"))

        if max_value:
            max_purchaseMasterId = max_value.get("PurchaseMasterID__max", 0)

            PurchaseMasterID = max_purchaseMasterId + 1

        else:
            PurchaseMasterID = 1

    return PurchaseMasterID


def get_auto_id(model, BranchID, CompanyID):
    PurchaseDetailsID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id = model.objects.filter(CompanyID=CompanyID).aggregate(
        Max("PurchaseDetailsID")
    )

    if model.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        max_value = model.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID
        ).aggregate(Max("PurchaseDetailsID"))

        if max_value:
            max_purchaseDetailsId = max_value.get("PurchaseDetailsID__max", 0)

            PurchaseDetailsID = max_purchaseDetailsId + 1

        else:
            PurchaseDetailsID = 1

    return PurchaseDetailsID


def get_auto_StockRateID(model, BranchID, CompanyID):
    StockRateID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id = model.objects.filter(CompanyID=CompanyID).aggregate(
        Max("StockRateID")
    )

    if model.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        max_value = model.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID
        ).aggregate(Max("StockRateID"))

        if max_value:
            max_stockRateId = max_value.get("StockRateID__max", 0)

            StockRateID = max_stockRateId + 1

        else:
            StockRateID = 1

    return StockRateID


def get_auto_StockTransID(model, BranchID, CompanyID):
    StockTransID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id = model.objects.filter(CompanyID=CompanyID).aggregate(
        Max("StockTransID")
    )

    if model.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        max_value = model.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID
        ).aggregate(Max("StockTransID"))

        if max_value:
            max_stockTransId = max_value.get("StockTransID__max", 0)

            StockTransID = max_stockTransId + 1

        else:
            StockTransID = 1

    return StockTransID


def purchase_taxgroup_excel_data(CompanyID, BranchID, FromDate, ToDate, PriceRounding):
    final_data = []
    is_ok = False
    count = 0
    # interstate b2b
    tax_types = [
        "GST Inter-state B2B",
        "GST Inter-state B2C",
        "GST Intra-state B2B",
        "GST Intra-state B2C",
        "GST Intra-state B2B Unregistered",
    ]
    for tx in tax_types:
        if PurchaseMaster.objects.filter(
            CompanyID=CompanyID,
            BranchID=BranchID,
            Date__gte=FromDate,
            Date__lte=ToDate,
            TaxType=tx,
        ).exists():
            purchase_instances = PurchaseMaster.objects.filter(
                CompanyID=CompanyID,
                BranchID=BranchID,
                Date__gte=FromDate,
                Date__lte=ToDate,
                TaxType=tx,
            )
            purchase_ids = purchase_instances.values_list("PurchaseMasterID", flat=True)

            purchase_details = PurchaseDetails.objects.filter(
                CompanyID=CompanyID,
                BranchID=BranchID,
                PurchaseMasterID__in=purchase_ids,
            )
            # purchase_details = PurchaseDetails.objects.filter(CompanyID=CompanyID,BranchID=BranchID,PurchaseMasterID__in=purchase_ids).exclude(IGSTPerc=0)
            tax_list = purchase_details.values_list("IGSTPerc", flat=True)
            tax_list = set(tax_list)
            print(purchase_details, "+++++++++++++++++++++++++++++++++")
            # count = 0
            for t in tax_list:
                gouprd_details = purchase_details.filter(IGSTPerc=t)
                if gouprd_details:
                    final_data.append(
                        {
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
                        }
                    )
                    total_Qty = 0
                    total_amount = 0
                    total_SGSTAmount = 0
                    total_CGSTAmount = 0
                    total_IGSTAmount = 0
                    total_sum_Total = 0
                    for g in gouprd_details:
                        PurchaseMasterID = g.PurchaseMasterID
                        Date = purchase_instances.get(
                            PurchaseMasterID=PurchaseMasterID
                        ).Date
                        InvoiceNo = purchase_instances.get(
                            PurchaseMasterID=PurchaseMasterID
                        ).RefferenceBillNo
                        LedgerID = purchase_instances.get(
                            PurchaseMasterID=PurchaseMasterID
                        ).LedgerID
                        ProductID = g.ProductID
                        party = ""
                        GSTN = ""
                        City = ""
                        State_id = ""
                        State_Code = ""
                        state_name = ""
                        if AccountLedger.objects.filter(
                            CompanyID=CompanyID,
                            LedgerID=LedgerID,
                            AccountGroupUnder__in=[10, 29],
                        ).exists():
                            parties = Parties.objects.get(
                                CompanyID=CompanyID,
                                BranchID=BranchID,
                                LedgerID=LedgerID,
                            )
                            party = parties.PartyName
                            GSTN = parties.GSTNumber
                            City = parties.City
                            State_id = parties.State
                            State_Code = parties.State_Code
                            if State_id:
                                if State.objects.filter(pk=State_id).exists():
                                    state_name = State.objects.get(pk=State_id).Name

                        product = Product.objects.get(
                            CompanyID=CompanyID, ProductID=ProductID
                        )
                        item_name = product.ProductName
                        HSN = product.HSNCode

                        Qty = g.Qty
                        UnitID = PriceList.objects.get(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            PriceListID=g.PriceListID,
                        ).UnitID
                        UnitName = Unit.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, UnitID=UnitID
                        ).UnitName
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

                        total_Qty += converted_float(Qty)
                        total_amount += converted_float(Amount)
                        total_SGSTAmount += converted_float(SGSTAmount)
                        total_CGSTAmount += converted_float(CGSTAmount)
                        total_IGSTAmount += converted_float(IGSTAmount)
                        total_sum_Total += converted_float(Total)

                        str_date = Date.strftime("%m/%d/%Y")
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
                            "Total": "%.2f" % round(Total, 2),
                        }

                        is_ok = True
                        final_data[count]["data"].append(data)

                    final_data[count]["total_Qty"] = total_Qty
                    final_data[count]["total_amount"] = total_amount
                    final_data[count]["total_SGSTAmount"] = total_SGSTAmount
                    final_data[count]["total_CGSTAmount"] = total_CGSTAmount
                    final_data[count]["total_IGSTAmount"] = total_IGSTAmount
                    final_data[count]["total_sum_Total"] = total_sum_Total

                    count += 1

        if PurchaseReturnMaster.objects.filter(
            CompanyID=CompanyID,
            BranchID=BranchID,
            VoucherDate__gte=FromDate,
            VoucherDate__lte=ToDate,
            TaxType=tx,
        ).exists():
            purchaseReturn_instances = PurchaseReturnMaster.objects.filter(
                CompanyID=CompanyID,
                BranchID=BranchID,
                VoucherDate__gte=FromDate,
                VoucherDate__lte=ToDate,
                TaxType=tx,
            )
            purchaseReturn_ids = purchaseReturn_instances.values_list(
                "PurchaseReturnMasterID", flat=True
            )

            purchaseReturn_details = PurchaseReturnDetails.objects.filter(
                CompanyID=CompanyID,
                BranchID=BranchID,
                PurchaseReturnMasterID__in=purchaseReturn_ids,
            )
            # purchaseReturn_details = PurchaseReturnDetails.objects.filter(CompanyID=CompanyID,BranchID=BranchID,PurchaseReturnMasterID__in=purchaseReturn_ids).exclude(IGSTPerc=0)
            tax_list = purchaseReturn_details.values_list("IGSTPerc", flat=True)
            tax_list = set(tax_list)
            print(purchaseReturn_details, "+++++++++++++++++++++++++++++++++")
            # count = 0
            for t in tax_list:
                gouprd_details = purchaseReturn_details.filter(IGSTPerc=t)
                if gouprd_details:
                    final_data.append(
                        {
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
                        }
                    )
                    total_Qty = 0
                    total_amount = 0
                    total_SGSTAmount = 0
                    total_CGSTAmount = 0
                    total_IGSTAmount = 0
                    total_sum_Total = 0
                    for g in gouprd_details:
                        PurchaseReturnMasterID = g.PurchaseReturnMasterID
                        VoucherDate = purchaseReturn_instances.get(
                            PurchaseReturnMasterID=PurchaseReturnMasterID
                        ).VoucherDate
                        InvoiceNo = purchaseReturn_instances.get(
                            PurchaseReturnMasterID=PurchaseReturnMasterID
                        ).RefferenceBillNo
                        LedgerID = purchaseReturn_instances.get(
                            PurchaseReturnMasterID=PurchaseReturnMasterID
                        ).LedgerID
                        ProductID = g.ProductID
                        party = ""
                        GSTN = ""
                        City = ""
                        State_id = ""
                        State_Code = ""
                        state_name = ""
                        if AccountLedger.objects.filter(
                            CompanyID=CompanyID,
                            LedgerID=LedgerID,
                            AccountGroupUnder__in=[10, 29],
                        ).exists():
                            parties = Parties.objects.get(
                                CompanyID=CompanyID,
                                BranchID=BranchID,
                                LedgerID=LedgerID,
                            )
                            party = parties.PartyName
                            GSTN = parties.GSTNumber
                            City = parties.City
                            State_id = parties.State
                            State_Code = parties.State_Code
                            if State_id:
                                if State.objects.filter(pk=State_id).exists():
                                    state_name = State.objects.get(pk=State_id).Name

                        product = Product.objects.get(
                            CompanyID=CompanyID, ProductID=ProductID
                        )
                        item_name = product.ProductName
                        HSN = product.HSNCode

                        Qty = g.Qty
                        UnitID = PriceList.objects.get(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            PriceListID=g.PriceListID,
                        ).UnitID
                        UnitName = Unit.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, UnitID=UnitID
                        ).UnitName
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

                        total_Qty += converted_float(Qty)
                        total_amount += converted_float(Amount)
                        total_SGSTAmount += converted_float(SGSTAmount)
                        total_CGSTAmount += converted_float(CGSTAmount)
                        total_IGSTAmount += converted_float(IGSTAmount)
                        total_sum_Total += converted_float(Total)

                        str_date = VoucherDate.strftime("%m/%d/%Y")
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
                            "Total": "%.2f" % round(Total, 2),
                        }

                        is_ok = True
                        final_data[count]["data"].append(data)

                    final_data[count]["total_Qty"] = total_Qty
                    final_data[count]["total_amount"] = total_amount
                    final_data[count]["total_SGSTAmount"] = total_SGSTAmount
                    final_data[count]["total_CGSTAmount"] = total_CGSTAmount
                    final_data[count]["total_IGSTAmount"] = total_IGSTAmount
                    final_data[count]["total_sum_Total"] = total_sum_Total

                    count += 1

    if is_ok == True:
        return final_data
    else:
        return []


def export_to_excel_purchase_taxgroup(wb, data, FromDate, ToDate):
    ws = wb.add_sheet("sheet1")
    # main header
    columns = [
        "SlNo",
        "Date",
        "Invoice Date",
        "Invoice No",
        "Party",
        "GSTIN / UIN",
        "City",
        "State",
        "State Code",
        "ItemName",
        "HSN",
        "Qty",
        "Unit",
        "Amount",
        "SGST(%)",
        "CGST(%)",
        "IGST(%)",
        "SGST",
        "CGST",
        "IGST",
        "Total",
    ]
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
            invoice_type = data[i]["type"]
        except:
            invoice_type = "Master"

        if invoice_type == "Master":
            invoice_head = "Purchase From "
        elif invoice_type == "Return":
            invoice_head = "Purchase Return From "

        ws.write(
            data_row,
            data_col,
            str(invoice_head)
            + str(data[i]["TaxType"])
            + str(" - ")
            + str(data[i]["TaxPerc"])
            + str("% Taxable"),
            sub_header_style,
        )
        data_row += 1
        ws.write(
            data_row,
            data_col,
            str("From " + str(FromDate) + str(" To ") + str(ToDate)),
            sub_header_style,
        )

        data_row += 1
        SlNo = 1

        total_Qty = data[i]["total_Qty"]
        total_amount = data[i]["total_amount"]
        total_SGSTAmount = data[i]["total_SGSTAmount"]
        total_CGSTAmount = data[i]["total_CGSTAmount"]
        total_IGSTAmount = data[i]["total_IGSTAmount"]
        total_sum_Total = data[i]["total_sum_Total"]
        for j in data[i]["data"]:
            total_row = SlNo + 3
            if data_row == 3:
                total_row += 1
            ws.write(data_row, 0, SlNo)
            ws.write(data_row, 1, j["Date"])
            ws.write(data_row, 2, j["InvoiceDate"])
            ws.write(data_row, 3, j["InvoiceNo"])
            ws.write(data_row, 4, j["party"])
            ws.write(data_row, 5, j["GSTN"])
            ws.write(data_row, 6, j["City"])
            ws.write(data_row, 7, j["State"])
            ws.write(data_row, 8, j["State_Code"])
            ws.write(data_row, 9, j["item_name"])
            ws.write(data_row, 10, j["HSN"])
            ws.write(data_row, 11, j["Qty"])
            ws.write(data_row, 12, j["UnitName"])
            ws.write(data_row, 13, j["Amount"])
            ws.write(data_row, 14, j["SGSTPerc"])
            ws.write(data_row, 15, j["CGSTPerc"])
            ws.write(data_row, 16, j["IGSTPerc"])
            ws.write(data_row, 17, j["SGSTAmount"])
            ws.write(data_row, 18, j["CGSTAmount"])
            ws.write(data_row, 19, j["IGSTAmount"])
            ws.write(data_row, 20, j["Total"])
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


# purchases gst report
def purchase_gst_excel_data(
    CompanyID, BranchID, FromDate, ToDate, PriceRounding, UserID
):
    Total_TaxableValue = 0
    Total_TotalQty = 0

    Total_TotalTaxableAmount = 0
    Total_TotalTax = 0
    Total_SGSTAmount = 0
    Total_CGSTAmount = 0
    Total_IGSTAmount = 0
    Total_KFCAmount = 0
    party_gstin = None
    Total_GrandTotal = 0

    print(UserID, "UserIDUserIDUserIDUserIDUserID")

    if UserID:
        UserID = UserTable.objects.get(id=UserID, Active=True).customer.user.pk
        # if PurchaseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID).exists():
        instances = PurchaseMaster.objects.filter(
            CompanyID=CompanyID,
            BranchID=BranchID,
            Date__gte=FromDate,
            Date__lte=ToDate,
            CreatedUserID=UserID,
        )
        return_instances = PurchaseReturnMaster.objects.filter(
            CompanyID=CompanyID,
            BranchID=BranchID,
            VoucherDate__gte=FromDate,
            VoucherDate__lte=ToDate,
            CreatedUserID=UserID,
        )
        final_array = []
        # =======
        for i in instances:
            LedgerID = i.LedgerID
            if AccountLedger.objects.filter(
                LedgerID=LedgerID, CompanyID=CompanyID
            ).exists():
                Particulars = AccountLedger.objects.get(
                    LedgerID=LedgerID, CompanyID=CompanyID
                )
                LedgerName = Particulars.LedgerName
                if Particulars.AccountGroupUnder == 29:
                    party_gstin = Parties.objects.get(
                        LedgerID=LedgerID,
                        BranchID=BranchID,
                        CompanyID=CompanyID,
                        PartyType="supplier",
                        PartyCode=Particulars.LedgerCode,
                    ).GSTNumber

            str_date = i.Date.strftime("%m/%d/%Y")
            print(str_date, ":**************************::::::::::")
            dic = {
                "Date": str_date,
                "VoucherNo": i.VoucherNo,
                "RefferenceBillNo": i.RefferenceBillNo,
                "VenderInvoiceDate": i.VenderInvoiceDate,
                "GrandTotal": i.GrandTotal,
                "VoucherType": "PI",
                "Particulars": LedgerName,
                "party_gstin": party_gstin,
                "TaxType": i.TaxType,
                "TotalTax": i.TotalTax,
                "SGSTAmount": i.SGSTAmount,
                "CGSTAmount": i.CGSTAmount,
                "IGSTAmount": i.IGSTAmount,
                "CESSAmount": 0,
                # "KFCAmount" : i.KFCAmount,
                "TotalTaxableAmount": i.TotalTaxableAmount,
            }
            if converted_float(i.TotalTax) > 0:
                final_array.append(dic)

        for i in return_instances:
            LedgerID = i.LedgerID
            if AccountLedger.objects.filter(
                LedgerID=LedgerID, CompanyID=CompanyID
            ).exists():
                Particulars = AccountLedger.objects.get(
                    LedgerID=LedgerID, CompanyID=CompanyID
                )
                LedgerName = Particulars.LedgerName
                if Particulars.AccountGroupUnder == 29:
                    party_gstin = Parties.objects.get(
                        LedgerID=LedgerID,
                        BranchID=BranchID,
                        CompanyID=CompanyID,
                        PartyType="supplier",
                        PartyCode=Particulars.LedgerCode,
                    ).GSTNumber
            # try:
            #     KFCAmount = int(i.KFCAmount)
            # except:
            #     KFCAmount = 0

            TotalTaxableAmount = converted_float(i.TotalTaxableAmount)
            if TotalTaxableAmount:
                TotalTaxableAmount = converted_float(i.TotalTaxableAmount)
            else:
                TotalTaxableAmount = 0

            str_date = i.VoucherDate.strftime("%m/%d/%Y")

            dic = {
                "Date": str_date,
                "VoucherNo": i.VoucherNo,
                "RefferenceBillNo": i.RefferenceBillNo,
                "VenderInvoiceDate": i.VenderInvoiceDate,
                "GrandTotal": i.GrandTotal,
                "VoucherType": "PR",
                "Particulars": LedgerName,
                "party_gstin": party_gstin,
                "TaxType": i.TaxType,
                "TotalTax": int(i.TotalTax * -1),
                "SGSTAmount": int(i.SGSTAmount * -1),
                "CGSTAmount": int(i.CGSTAmount * -1),
                "IGSTAmount": int(i.IGSTAmount * -1),
                "CESSAmount": 0,
                # "KFCAmount" : KFCAmount*-1,
                "TotalTaxableAmount": TotalTaxableAmount * -1,
            }
            if converted_float(i.TotalTax) > 0:
                final_array.append(dic)

        for i in final_array:
            Total_TotalTaxableAmount += converted_float(i["TotalTaxableAmount"])
            Total_TotalTax += converted_float(i["TotalTax"])

            Total_SGSTAmount += converted_float(i["SGSTAmount"])
            Total_CGSTAmount += converted_float(i["CGSTAmount"])
            Total_IGSTAmount += converted_float(i["IGSTAmount"])
            Total_GrandTotal += converted_float(i["GrandTotal"])
            # Total_KFCAmount += converted_float(i['KFCAmount'])
        response_data = {
            "StatusCode": 6000,
            "purchase_data": final_array,
            "Total_TaxableValue": Total_TaxableValue,
            "Total_TotalQty": Total_TotalQty,
            "Total_TotalTaxableAmount": Total_TotalTaxableAmount,
            "Total_TotalTax": Total_TotalTax,
            "Total_SGSTAmount": Total_SGSTAmount,
            "Total_CGSTAmount": Total_CGSTAmount,
            "Total_IGSTAmount": Total_IGSTAmount,
            "Total_KFCAmount": Total_KFCAmount,
            "Total_GrandTotal": Total_GrandTotal,
        }
        return response_data

    else:
        # if PurchaseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
        instances = PurchaseMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate
        )
        # ======
        return_instances = PurchaseReturnMaster.objects.filter(
            CompanyID=CompanyID,
            BranchID=BranchID,
            VoucherDate__gte=FromDate,
            VoucherDate__lte=ToDate,
        )

        final_array = []
        # =======
        for i in instances:
            LedgerID = i.LedgerID
            if AccountLedger.objects.filter(
                LedgerID=LedgerID, CompanyID=CompanyID
            ).exists():
                Particulars = AccountLedger.objects.get(
                    LedgerID=LedgerID, CompanyID=CompanyID
                )
                LedgerName = Particulars.LedgerName
                if Particulars.AccountGroupUnder == 29:
                    party_gstin = Parties.objects.get(
                        LedgerID=LedgerID,
                        BranchID=BranchID,
                        CompanyID=CompanyID,
                        PartyType="supplier",
                        PartyCode=Particulars.LedgerCode,
                    ).GSTNumber
            str_date = i.Date.strftime("%m/%d/%Y")
            str_invoice_date = i.VenderInvoiceDate.strftime("%m/%d/%Y")

            dic = {
                "Date": str_date,
                "VoucherNo": i.VoucherNo,
                "RefferenceBillNo": i.RefferenceBillNo,
                "VenderInvoiceDate": str_invoice_date,
                "GrandTotal": i.GrandTotal,
                "VoucherType": "PI",
                "Particulars": LedgerName,
                "party_gstin": party_gstin,
                "TaxType": i.TaxType,
                "TotalTax": i.TotalTax,
                "SGSTAmount": i.SGSTAmount,
                "CGSTAmount": i.CGSTAmount,
                "IGSTAmount": i.IGSTAmount,
                "CESSAmount": 0,
                # "KFCAmount" : i.KFCAmount,
                "TotalTaxableAmount": i.TotalTaxableAmount,
            }
            if converted_float(i.TotalTax) > 0:
                final_array.append(dic)

        for i in return_instances:
            LedgerID = i.LedgerID
            if AccountLedger.objects.filter(
                LedgerID=LedgerID, CompanyID=CompanyID
            ).exists():
                Particulars = AccountLedger.objects.get(
                    LedgerID=LedgerID, CompanyID=CompanyID
                )
                LedgerName = Particulars.LedgerName
                if Particulars.AccountGroupUnder == 29:
                    party_gstin = Parties.objects.get(
                        LedgerID=LedgerID,
                        BranchID=BranchID,
                        CompanyID=CompanyID,
                        PartyType="supplier",
                        PartyCode=Particulars.LedgerCode,
                    ).GSTNumber

            # try:
            #     KFCAmount = int(i.KFCAmount)
            # except:
            #     KFCAmount = 0

            TotalTaxableAmount = converted_float(i.TotalTaxableAmount)
            if TotalTaxableAmount:
                TotalTaxableAmount = converted_float(i.TotalTaxableAmount)
            else:
                TotalTaxableAmount = 0
            str_date = i.VoucherDate.strftime("%m/%d/%Y")
            str_invoice_date = i.VenderInvoiceDate.strftime("%m/%d/%Y")

            dic = {
                "Date": str_date,
                "VoucherNo": i.VoucherNo,
                "RefferenceBillNo": i.RefferenceBillNo,
                "VenderInvoiceDate": str_invoice_date,
                "GrandTotal": i.GrandTotal,
                "VoucherType": "PR",
                "Particulars": LedgerName,
                "party_gstin": party_gstin,
                "TaxType": i.TaxType,
                "TotalTax": int(i.TotalTax * -1),
                "SGSTAmount": int(i.SGSTAmount * -1),
                "CGSTAmount": int(i.CGSTAmount * -1),
                "IGSTAmount": int(i.IGSTAmount * -1),
                "CESSAmount": 0,
                # "KFCAmount" : KFCAmount*-1,
                "TotalTaxableAmount": TotalTaxableAmount * -1,
            }
            if converted_float(i.TotalTax) > 0:
                final_array.append(dic)

        for i in final_array:
            Total_TotalTaxableAmount += converted_float(i["TotalTaxableAmount"])
            Total_TotalTax += converted_float(i["TotalTax"])

            Total_SGSTAmount += converted_float(i["SGSTAmount"])
            Total_CGSTAmount += converted_float(i["CGSTAmount"])
            Total_IGSTAmount += converted_float(i["IGSTAmount"])
            Total_GrandTotal += converted_float(i["GrandTotal"])
            # Total_KFCAmount += converted_float(i['KFCAmount'])

        response_data = {
            "StatusCode": 6000,
            "purchase_data": final_array,
            "Total_TaxableValue": Total_TaxableValue,
            "Total_TotalQty": Total_TotalQty,
            "Total_TotalTaxableAmount": Total_TotalTaxableAmount,
            "Total_TotalTax": Total_TotalTax,
            "Total_SGSTAmount": Total_SGSTAmount,
            "Total_CGSTAmount": Total_CGSTAmount,
            "Total_IGSTAmount": Total_IGSTAmount,
            # "Total_KFCAmount": Total_KFCAmount,
            "Total_GrandTotal": Total_GrandTotal,
        }
        return response_data


def export_to_excel_purchase_gst(wb, data, FromDate, ToDate):
    ws = wb.add_sheet("Purchase GST Report")

    columns = [
        "Date",
        "Voucher No",
        "Refference Bill No",
        "Vender Invoice Date",
        "Particulars",
        "GSTIN/UIN",
        "Voucher Type",
        "Tax Type",
        "Taxable Amount",
        "SGST",
        "CGST",
        "IGST",
        "Cess",
        "Total Tax Amount",
        "Grand Total",
    ]
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
    total_values_style.font = font

    total_label_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True
    font.colour_index = 2
    total_label_style.font = font

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], sub_header_style)

    data_col = 0
    data_row = 1
    SlNo = 1

    print(data["purchase_data"], "oppppppppppppopopopo")
    Total_TotalTaxableAmount = data["Total_TotalTaxableAmount"]
    Total_SGSTAmount = data["Total_SGSTAmount"]
    Total_IGSTAmount = data["Total_IGSTAmount"]
    Total_CGSTAmount = data["Total_CGSTAmount"]

    Total_TotalTax = data["Total_TotalTax"]
    Total_GrandTotal = data["Total_GrandTotal"]

    for j in data["purchase_data"]:
        ws.write(data_row, 0, j["Date"])
        ws.write(data_row, 1, j["VoucherNo"])
        ws.write(data_row, 2, j["RefferenceBillNo"])
        ws.write(data_row, 3, j["VenderInvoiceDate"])
        ws.write(data_row, 4, j["Particulars"])
        ws.write(data_row, 5, j["party_gstin"])
        ws.write(data_row, 6, j["VoucherType"])
        ws.write(data_row, 7, j["TaxType"])
        ws.write(data_row, 8, j["TotalTaxableAmount"])
        ws.write(data_row, 9, j["SGSTAmount"])
        ws.write(data_row, 10, j["CGSTAmount"])
        ws.write(data_row, 11, j["IGSTAmount"])
        ws.write(data_row, 12, 0)
        ws.write(data_row, 13, j["TotalTax"])
        ws.write(data_row, 14, j["GrandTotal"])
        data_row += 1
    print(data_row, "&&&&&&&&&&&")
    ws.write(data_row, 7, "Total", total_label_style)
    ws.write(data_row, 8, Total_TotalTaxableAmount, total_values_style)
    ws.write(data_row, 9, Total_SGSTAmount, total_values_style)
    ws.write(data_row, 10, Total_CGSTAmount, total_values_style)
    ws.write(data_row, 11, Total_IGSTAmount, total_values_style)
    ws.write(data_row, 12, 0, total_values_style)
    ws.write(data_row, 13, Total_TotalTax, total_values_style)
    ws.write(data_row, 14, Total_GrandTotal, total_values_style)


def export_to_excel_purchase(wb, data, FromDate, ToDate, title, columns, columns_heads):
    ws = wb.add_sheet("Purchase Report")

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
    font.colour_index = 2
    total_label_style.font = font

    value_decimal_style = xlwt.XFStyle()
    value_decimal_style.num_format_str = "0.00"

    main_title = xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True
    main_title.font = font
    main_title.alignment = center

    ws.write_merge(0, 0, 0, 6, title, main_title)

    row_num = 1
    # for col_num in range(len(columns)):
    #     ws.write(row_num, col_num, columns[col_num], sub_header_style)

    table_column_num = 0
    for col_num in range(len(columns_heads["tableHead"])):
        is_active = columns_heads["tableHead"][col_num]["is_active"]
        label = columns_heads["tableHead"][col_num]["label"]
        if is_active:
            ws.write(row_num, table_column_num, label, sub_header_style)
            table_column_num += 1

    data_row = 2

    try:
        data_list = data["new_purchase_data"]
    except:
        data_list = []

    for j in data_list:

        # try:
        #     value = columns_heads[0]["tableHead"]['value']
        # except:
        #     value = ''

        # print(columns_heads[0]["tableHead"])

        try:
            VoucherNo = j["VoucherNo"]
        except:
            VoucherNo = "-"
        try:
            Date = j["VoucherDate"]
        except:
            Date = "-"
        try:
            RefferenceBillNo = j["RefferenceBillNo"]
        except:
            RefferenceBillNo = "-"
        try:
            RefferenceBillDate = j["RefferenceBillDate"]
        except:
            RefferenceBillDate = "-"
        try:
            LedgerName = j["LedgerName"]
        except:
            LedgerName = "-"

        try:
            TotalGrossAmt = j["TotalGrossAmt"]
        except:
            TotalGrossAmt = "-"
        try:
            TotalTax = j["TotalTax"]
        except:
            TotalTax = "-"
        try:
            BillDiscAmt = j["BillDiscAmt"]
        except:
            BillDiscAmt = "-"
        try:
            GrandTotal = j["GrandTotal"]
        except:
            GrandTotal = "-"

        table_column_num = 0
        for key in range(len(columns_heads["tableHead"])):
            try:
                val = j[columns_heads["tableHead"][key]["value"]]
            except:
                val = ""
            print(
                columns_heads["tableHead"][key]["is_active"],
                "#########################################################@@",
                columns_heads["tableHead"][key]["label"],
            )
            # ws.write(data_row, 0, VoucherNo)
            # ws.write(data_row, 1, Date)
            # ws.write(data_row, 2, RefferenceBillNo)
            # ws.write(data_row, 3, RefferenceBillDate)
            # ws.write(data_row, 4, LedgerName)
            # ws.write(data_row, 5, converted_float(TotalGrossAmt), value_decimal_style)
            # ws.write(data_row, 6, converted_float(TotalTax), value_decimal_style)
            # ws.write(data_row, 7, converted_float(BillDiscAmt), value_decimal_style)
            # ws.write(data_row, 8, converted_float(GrandTotal), value_decimal_style)
            if columns_heads["tableHead"][key]["is_active"]:
                try:
                    ws.write(
                        data_row, table_column_num, converted_float(val), value_decimal_style
                    )
                except:
                    ws.write(data_row, table_column_num, val, value_decimal_style)
                table_column_num += 1
        data_row += 1


def purchase_excel_data(CompanyID, BranchID, FromDate, ToDate, PriceRounding, ReffNo):
    purchase_data = []
    purchaseReturn_data = []
    Total_netAmt_purchase = 0
    Total_GrossAmt_purchase = 0
    Total_netAmt_purchaseRetn = 0
    Total_tax_purchase = 0
    Total_tax_purchaseRetn = 0
    Total_billDiscount_purchase = 0
    Total_billDiscount_purchaseRetn = 0
    Total_grandTotal_purchase = 0
    Total_grandTotal_purchaseRetn = 0

    PurchaseCode = 6001
    PurchaseReturnCode = 6001

    count_purchase = 0
    count_purchase_return = 0
    count_divided_purchase = 0
    count_divided_purchase_return = 0

    if ReffNo:
        if PurchaseMaster.objects.filter(
            CompanyID=CompanyID,
            BranchID=BranchID,
            Date__gte=FromDate,
            Date__lte=ToDate,
            RefferenceBillNo=ReffNo,
        ).exists():
            instances = PurchaseMaster.objects.filter(
                CompanyID=CompanyID,
                BranchID=BranchID,
                Date__gte=FromDate,
                Date__lte=ToDate,
                RefferenceBillNo=ReffNo,
            )

            serialized_purchase = PurchaseMasterRest1Serializer(
                instances,
                many=True,
                context={"CompanyID": CompanyID, "PriceRounding": PriceRounding},
            )
            purchase_data = serialized_purchase.data
            PurchaseCode = 6000

            for i_purchase in instances:
                Total_GrossAmt_purchase += i_purchase.TotalGrossAmt
                Total_netAmt_purchase += i_purchase.NetTotal
                Total_tax_purchase += i_purchase.TotalTax
                Total_billDiscount_purchase += i_purchase.BillDiscAmt
                Total_grandTotal_purchase += i_purchase.GrandTotal

    else:
        if PurchaseMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate
        ).exists():
            instances = PurchaseMaster.objects.filter(
                CompanyID=CompanyID,
                BranchID=BranchID,
                Date__gte=FromDate,
                Date__lte=ToDate,
            )

            serialized_purchase = PurchaseMasterRest1Serializer(
                instances,
                many=True,
                context={"CompanyID": CompanyID, "PriceRounding": PriceRounding},
            )
            purchase_data = serialized_purchase.data
            PurchaseCode = 6000

            for i_purchase in instances:
                Total_GrossAmt_purchase += i_purchase.TotalGrossAmt
                Total_netAmt_purchase += i_purchase.NetTotal
                Total_tax_purchase += i_purchase.TotalTax
                Total_billDiscount_purchase += i_purchase.BillDiscAmt
                Total_grandTotal_purchase += i_purchase.GrandTotal

    if purchase_data:
        PurchaseCode = 6000
    if purchase_data:
        # New Design function Start
        purchase_jsnDatas = convertOrderdDict(purchase_data)
        purchase_total = {
            "LedgerName": str(_("Total")),
            "TotalGrossAmt": Total_GrossAmt_purchase,
            "BillDiscAmt": Total_billDiscount_purchase,
            "TotalTax": Total_tax_purchase,
            "GrandTotal": Total_grandTotal_purchase,
        }

        purchase_jsnDatas.append(purchase_total)
        # New Design function End

        response_data = {
            "StatusCode": 6000,
            "purchase_data": purchase_data,
            "purchase_total": purchase_total,
            "new_purchase_data": purchase_jsnDatas,
        }
        return response_data
    else:
        response_data = {"StatusCode": 6001, "message": "Datas Not Found!"}

        return response_data


def export_to_excel_purchaseRetun(wb, data, FromDate, ToDate, title, columns):
    ws = wb.add_sheet("PurchaseReturn Report")

    # write column headers in sheet

    # xl sheet styles
    # header font

    center = Alignment()
    center.horz = Alignment.HORZ_CENTER

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
    font.colour_index = 2
    total_label_style.font = font

    value_decimal_style = xlwt.XFStyle()
    value_decimal_style.num_format_str = "0.00"

    main_title = xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True
    main_title.font = font
    main_title.alignment = center

    ws.write_merge(0, 0, 0, 6, title, main_title)

    row_num = 1
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], sub_header_style)

    data_row = 2
    SlNo = 1

    try:
        data_list = data["new_purchaseReturn_data"]
    except:
        data_list = []

    for j in data_list:
        print(data_row, "oppppppppppppopopopo")
        try:
            VoucherNo = j["VoucherNo"]
        except:
            VoucherNo = "-"
        try:
            Date = j["VoucherDate"]
        except:
            Date = "-"
        try:
            RefferenceBillNo = j["RefferenceBillNo"]
        except:
            RefferenceBillNo = "-"
        try:
            RefferenceBillDate = j["RefferenceBillDate"]
        except:
            RefferenceBillDate = "-"
        try:
            LedgerName = j["LedgerName"]
        except:
            LedgerName = "-"

        try:
            TotalGrossAmt = j["TotalGrossAmt"]
        except:
            TotalGrossAmt = "-"
        try:
            TotalTax = j["TotalTax"]
        except:
            TotalTax = "-"
        try:
            BillDiscAmt = j["BillDiscAmt"]
        except:
            BillDiscAmt = "-"
        try:
            GrandTotal = j["GrandTotal"]
        except:
            GrandTotal = "-"

        ws.write(data_row, 0, VoucherNo)
        ws.write(data_row, 1, Date)
        ws.write(data_row, 2, RefferenceBillNo)
        ws.write(data_row, 3, RefferenceBillDate)
        ws.write(data_row, 4, LedgerName)
        ws.write(data_row, 5, converted_float(TotalGrossAmt), value_decimal_style)
        ws.write(data_row, 6, converted_float(TotalTax), value_decimal_style)
        ws.write(data_row, 7, converted_float(BillDiscAmt), value_decimal_style)
        ws.write(data_row, 8, converted_float(GrandTotal), value_decimal_style)
        data_row += 1


def purchaseReturn_excel_data(
    CompanyID, BranchID, FromDate, ToDate, PriceRounding, ReffNo
):
    purchase_data = []
    purchaseReturn_data = []
    Total_netAmt_purchase = 0
    Total_GrossAmt_purchase = 0
    Total_netAmt_purchaseRetn = 0
    Total_tax_purchase = 0
    Total_tax_purchaseRetn = 0
    Total_billDiscount_purchase = 0
    Total_billDiscount_purchaseRetn = 0
    Total_grandTotal_purchase = 0
    Total_grandTotal_purchaseRetn = 0

    PurchaseCode = 6001
    PurchaseReturnCode = 6001

    count_purchase = 0
    count_purchase_return = 0
    count_divided_purchase = 0
    count_divided_purchase_return = 0

    if PurchaseReturnMaster.objects.filter(
        CompanyID=CompanyID,
        BranchID=BranchID,
        VoucherDate__gte=FromDate,
        VoucherDate__lte=ToDate,
    ).exists():
        instances_purchaseReturn = PurchaseReturnMaster.objects.filter(
            CompanyID=CompanyID,
            BranchID=BranchID,
            VoucherDate__gte=FromDate,
            VoucherDate__lte=ToDate,
        )
        count_purchase_return = instances_purchaseReturn.count()

        serialized_purchaseReturn = PurchaseReturnMasterRestSerializer(
            instances_purchaseReturn,
            many=True,
            context={"CompanyID": CompanyID, "PriceRounding": PriceRounding},
        )
        purchaseReturn_data = serialized_purchaseReturn.data
        PurchaseReturnCode = 6000

        for i_purchaseReturn in instances_purchaseReturn:
            Total_netAmt_purchaseRetn += i_purchaseReturn.TotalGrossAmt
            Total_tax_purchaseRetn += i_purchaseReturn.TotalTax
            Total_billDiscount_purchaseRetn += i_purchaseReturn.BillDiscAmt
            Total_grandTotal_purchaseRetn += i_purchaseReturn.GrandTotal

    if purchaseReturn_data:
        PurchaseReturnCode = 6000
    if purchaseReturn_data:

        purchaseReturn_jsnDatas = convertOrderdDict(purchaseReturn_data)

        purchaseReturn_total = {
            "LedgerName": str(_("Total")),
            "TotalGrossAmt": Total_netAmt_purchaseRetn,
            "BillDiscAmt": Total_billDiscount_purchaseRetn,
            "TotalTax": Total_tax_purchaseRetn,
            "GrandTotal": Total_grandTotal_purchaseRetn,
        }
        purchaseReturn_jsnDatas.append(purchaseReturn_total)

        response_data = {
            "StatusCode": 6000,
            "new_purchaseReturn_data": purchaseReturn_jsnDatas,
            "purchaseReturn_data": purchaseReturn_data,
            "purchasesReturn_total": purchaseReturn_total,
        }
        return response_data
    else:
        response_data = {"StatusCode": 6001, "message": "Datas Not Found!"}

        return response_data


# def SetBatch(CompanyID, BranchID, FromDate, ToDate, PriceRounding, ReffNo):
#     if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
#         if check_BatchCriteria == "PurchasePrice":
#             if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PriceListID=PriceListID, PurchasePrice=Batch_purchasePrice).exists():
#                 batch_ins = Batch.objects.filter(
#                     CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PriceListID=PriceListID, PurchasePrice=Batch_purchasePrice).last()
#                 StockIn = batch_ins.StockIn
#                 print(StockIn)
#                 BatchCode = batch_ins.BatchCode
#                 SalesPrice = batch_ins.SalesPrice
#                 NewStock = converted_float(
#                     StockIn) + converted_float(qty_batch)
#                 if ExpiryDate:
#                     batch_ins.ExpiryDate = ExpiryDate
#                 if ManufactureDate:
#                     batch_ins.ManufactureDate = ManufactureDate
#                 batch_ins.StockIn = NewStock
#                 batch_ins.save()
#             else:
#                 BatchCode = get_auto_AutoBatchCode(
#                     Batch, BranchID, CompanyID)
#                 Batch.objects.create(
#                     CompanyID=CompanyID,
#                     BranchID=BranchID,
#                     BatchCode=BatchCode,
#                     StockIn=qty_batch,
#                     PurchasePrice=Batch_purchasePrice,
#                     SalesPrice=SalesPrice,
#                     PriceListID=PriceListID,
#                     ProductID=ProductID,
#                     ManufactureDate=ManufactureDate,
#                     ExpiryDate=ExpiryDate,
#                     WareHouseID=WarehouseID,
#                     CreatedDate=today,
#                     UpdatedDate=today,
#                     CreatedUserID=CreatedUserID,
#                 )
#         elif check_BatchCriteria == "PurchasePriceAndExpiryDate":
#             if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PriceListID=PriceListID, PurchasePrice=Batch_purchasePrice, ExpiryDate=ExpiryDate).exists():
#                 batch_ins = Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID,
#                                                  PriceListID=PriceListID, PurchasePrice=Batch_purchasePrice, ExpiryDate=ExpiryDate).last()
#                 StockIn = batch_ins.StockIn
#                 BatchCode = batch_ins.BatchCode
#                 SalesPrice = batch_ins.SalesPrice
#                 NewStock = converted_float(
#                     StockIn) + converted_float(qty_batch)
#                 batch_ins.StockIn = NewStock
#                 batch_ins.save()
#             else:
#                 BatchCode = get_auto_AutoBatchCode(
#                     Batch, BranchID, CompanyID)
#                 Batch.objects.create(
#                     CompanyID=CompanyID,
#                     BranchID=BranchID,
#                     BatchCode=BatchCode,
#                     StockIn=qty_batch,
#                     PurchasePrice=Batch_purchasePrice,
#                     SalesPrice=SalesPrice,
#                     PriceListID=PriceListID,
#                     ProductID=ProductID,
#                     ManufactureDate=ManufactureDate,
#                     ExpiryDate=ExpiryDate,
#                     WareHouseID=WarehouseID,
#                     CreatedDate=today,
#                     UpdatedDate=today,
#                     CreatedUserID=CreatedUserID,
#                 )
#         # else:
#         #     if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=Batch_purchasePrice, SalesPrice=SalesPrice).exists():
#         #         batch_ins = Batch.objects.get(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=Batch_purchasePrice, SalesPrice=SalesPrice)
#         #         StockIn = batch_ins.StockIn
#         #         BatchCode = batch_ins.BatchCode
#         #         NewStock = converted_float(StockIn) + converted_float(qty_batch)
#         #         batch_ins.StockIn = NewStock
#         #         batch_ins.save()
#         #     else:
#         #         BatchCode = get_auto_AutoBatchCode(
#         #             Batch, BranchID, CompanyID)
#         #         Batch.objects.create(
#         #             CompanyID=CompanyID,
#         #             BranchID=BranchID,
#         #             BatchCode=BatchCode,
#         #             StockIn=qty_batch,
#         #             PurchasePrice=Batch_purchasePrice,
#         #             SalesPrice=SalesPrice,
#         #             PriceListID=PriceListID,
#         #             ProductID=ProductID,
#         #             WareHouseID=WarehouseID,
#         #             CreatedDate=today,
#         #             UpdatedDate=today,
#         #             CreatedUserID=CreatedUserID,
#         #         )

#     else:
#         if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PriceListID=PriceListID).exists():
#             batch_ins = Batch.objects.get(
#                 CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PriceListID=PriceListID)
#             StockIn = batch_ins.StockIn
#             BatchCode = batch_ins.BatchCode
#             SalesPrice = batch_ins.SalesPrice
#             NewStock = converted_float(
#                 StockIn) + converted_float(qty_batch)
#             batch_ins.StockIn = NewStock
#             batch_ins.save()
#         else:
#             BatchCode = get_auto_AutoBatchCode(
#                 Batch, BranchID, CompanyID)
#             Batch.objects.create(
#                 CompanyID=CompanyID,
#                 BranchID=BranchID,
#                 BatchCode=BatchCode,
#                 StockIn=qty_batch,
#                 PurchasePrice=Batch_purchasePrice,
#                 SalesPrice=SalesPrice,
#                 PriceListID=PriceListID,
#                 ProductID=ProductID,
#                 ManufactureDate=ManufactureDate,
#                 ExpiryDate=ExpiryDate,
#                 WareHouseID=WarehouseID,
#                 CreatedDate=today,
#                 UpdatedDate=today,
#                 CreatedUserID=CreatedUserID,
#             )

#     return response_data


def SetBatch(
    CompanyID,
    check_EnableProductBatchWise,
    check_BatchCriteria,
    BranchID,
    ProductID,
    PriceListID,
    SalesPrice,
    Batch_purchasePrice,
    ExpiryDate,
    ManufactureDate,
    qty_batch,
    WarehouseID,
    today,
    CreatedUserID,
    BatchCode,
    action,
    VoucherType,
):
    message = ""
    if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
        if CompanyID.business_type.Name == "Pharmacy":
            if action == "create":
                if table.Batch.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode
                ).exists():
                    if (
                        table.Batch.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode
                        )
                        .exclude(ProductID=ProductID)
                        .exists()
                    ):
                        message = "Batch Already exist with some other Product"
                    elif (
                        table.Batch.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode
                        )
                        .exclude(PriceListID=PriceListID)
                        .exists()
                    ):
                        message = "Batch Already exist with some other unit"
                    elif (
                        table.Batch.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode
                        )
                        .exclude(ManufactureDate=ManufactureDate)
                        .exists()
                    ):
                        message = "Batch Already exist with some other ManufactureDate"
                    elif (
                        table.Batch.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode
                        )
                        .exclude(ExpiryDate=ExpiryDate)
                        .exists()
                    ):
                        message = "Batch Already exist with some other ExpiryDate"
                    else:
                        if table.Batch.objects.filter(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            BatchCode=BatchCode,
                            PurchasePrice=Batch_purchasePrice,
                        ).exists():
                            batch_ins = table.Batch.objects.filter(
                                CompanyID=CompanyID,
                                BranchID=BranchID,
                                BatchCode=BatchCode,
                                PurchasePrice=Batch_purchasePrice,
                            ).first()
                            current_stock = batch_ins.StockIn
                            batch_ins.StockIn = converted_float(current_stock) + converted_float(qty_batch)
                            batch_ins.SalesPrice = SalesPrice
                            batch_ins.save()
                        else:
                            message = (
                                "Batch Already exist with some other Purchase Price"
                            )
                else:
                    # BatchCode = get_auto_AutoBatchCode(
                    #     table.Batch, BranchID, CompanyID)
                    table.Batch.objects.create(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        BatchCode=BatchCode,
                        StockIn=qty_batch,
                        PurchasePrice=Batch_purchasePrice,
                        SalesPrice=SalesPrice,
                        PriceListID=PriceListID,
                        ProductID=ProductID,
                        ManufactureDate=ManufactureDate,
                        ExpiryDate=ExpiryDate,
                        WareHouseID=WarehouseID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        VoucherType=VoucherType,
                    )
            else:
                if table.Batch.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode
                ).exists():
                    batch = table.Batch.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode
                    ).first()
                    if (
                        not table.StockPosting.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, BatchID=BatchCode
                        )
                        .exclude(VoucherType="PI")
                        .exists()
                    ):
                        current_stock = batch.StockIn
                        batch.StockIn = converted_float(current_stock) + converted_float(qty_batch)
                        batch.SalesPrice = SalesPrice
                        batch.PurchasePrice = Batch_purchasePrice
                        batch.ProductID = ProductID
                        batch.PriceListID = PriceListID
                        batch.ManufactureDate = ManufactureDate
                        batch.ExpiryDate = ExpiryDate
                        batch.WarehouseID = WarehouseID
                        batch.UpdatedDate = today
                        batch.save()
                    else:
                        try:
                            datetime.datetime.strptime(ExpiryDate, "%Y-%m-%d")
                        except:
                            if ExpiryDate:
                                ExpiryDate = guess_date(ExpiryDate)

                        try:
                            datetime.datetime.strptime(ManufactureDate, "%Y-%m-%d")
                        except:
                            if ManufactureDate:
                                ManufactureDate = guess_date(ManufactureDate)

                        if not ProductID == batch.ProductID:
                            message = "you can't change product,sales has been Already done with this Batch"
                        elif not PriceListID == batch.PriceListID:
                            message = "you can't change unit,sales has been Already done with this Batch"
                        elif not str(ManufactureDate) == str(batch.ManufactureDate):
                            message = "you can't change ManufactureDate,sales has been Already done with this Batch"
                        elif not str(ExpiryDate) == str(batch.ExpiryDate):
                            message = "you can't change ExpiryDate,sales has been Already done with this Batch"
                        elif not Batch_purchasePrice == batch.PurchasePrice:
                            message = "you can't change Unit Price,sales has been Already done with this Batch"
                        else:
                            current_stock = batch.StockIn
                            batch.StockIn = converted_float(current_stock) + converted_float(qty_batch)
                            batch.UpdatedDate = today
                            batch.save()
                else:
                    table.Batch.objects.create(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        BatchCode=BatchCode,
                        StockIn=qty_batch,
                        PurchasePrice=Batch_purchasePrice,
                        SalesPrice=SalesPrice,
                        PriceListID=PriceListID,
                        ProductID=ProductID,
                        ManufactureDate=ManufactureDate,
                        ExpiryDate=ExpiryDate,
                        WareHouseID=WarehouseID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        VoucherType=VoucherType,
                    )
        else:
            if check_BatchCriteria == "PurchasePrice":
                if table.Batch.objects.filter(
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    ProductID=ProductID,
                    PriceListID=PriceListID,
                    PurchasePrice=Batch_purchasePrice,
                ).exists():
                    batch_ins = table.Batch.objects.filter(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        ProductID=ProductID,
                        PriceListID=PriceListID,
                        PurchasePrice=Batch_purchasePrice,
                    ).last()
                    StockIn = batch_ins.StockIn
                    BatchCode = batch_ins.BatchCode
                    SalesPrice = batch_ins.SalesPrice
                    NewStock = converted_float(StockIn) + converted_float(qty_batch)
                    if ExpiryDate:
                        batch_ins.ExpiryDate = ExpiryDate
                    if ManufactureDate:
                        batch_ins.ManufactureDate = ManufactureDate
                    batch_ins.StockIn = NewStock
                    batch_ins.save()
                else:
                    BatchCode = get_auto_AutoBatchCode(table.Batch, BranchID, CompanyID)
                    table.Batch.objects.create(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        BatchCode=BatchCode,
                        StockIn=qty_batch,
                        PurchasePrice=Batch_purchasePrice,
                        SalesPrice=SalesPrice,
                        PriceListID=PriceListID,
                        ProductID=ProductID,
                        ManufactureDate=ManufactureDate,
                        ExpiryDate=ExpiryDate,
                        WareHouseID=WarehouseID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        VoucherType=VoucherType,
                    )
            elif check_BatchCriteria == "PurchasePriceAndExpiryDate":
                if table.Batch.objects.filter(
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    ProductID=ProductID,
                    PriceListID=PriceListID,
                    PurchasePrice=Batch_purchasePrice,
                    ExpiryDate=ExpiryDate,
                ).exists():
                    batch_ins = table.Batch.objects.filter(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        ProductID=ProductID,
                        PriceListID=PriceListID,
                        PurchasePrice=Batch_purchasePrice,
                        ExpiryDate=ExpiryDate,
                    ).last()
                    StockIn = batch_ins.StockIn
                    BatchCode = batch_ins.BatchCode
                    SalesPrice = batch_ins.SalesPrice
                    NewStock = converted_float(StockIn) + converted_float(qty_batch)
                    batch_ins.StockIn = NewStock
                    batch_ins.save()
                else:
                    BatchCode = get_auto_AutoBatchCode(table.Batch, BranchID, CompanyID)
                    table.Batch.objects.create(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        BatchCode=BatchCode,
                        StockIn=qty_batch,
                        PurchasePrice=Batch_purchasePrice,
                        SalesPrice=SalesPrice,
                        PriceListID=PriceListID,
                        ProductID=ProductID,
                        ManufactureDate=ManufactureDate,
                        ExpiryDate=ExpiryDate,
                        WareHouseID=WarehouseID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        VoucherType=VoucherType,
                    )

    return BatchCode, message
