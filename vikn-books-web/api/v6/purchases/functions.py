import string
import random
from django.http import HttpResponse
from decimal import Decimal
from django.db.models import Max
from api.v6.purchases.serializers import PurchaseMasterSerializer, PurchaseMasterRestSerializer, PurchaseMasterRest1Serializer, PurchaseDetailsSerializer,\
    PurchaseDetailsRestSerializer, PurchaseMasterReportSerializer, PurchaseMasterForReturnSerializer
from brands.models import VoucherNoTable,State,PurchaseMaster, AccountLedger_Log,PurchaseMaster_Log, PurchaseDetails, PurchaseDetails_Log, StockPosting, LedgerPosting, StockPosting_Log,\
    LedgerPosting_Log, PurchaseDetailsDummy, StockRate, PriceList, StockTrans, ProductGroup, Brand, Unit, Warehouse, PurchaseReturnMaster, OpeningStockMaster,\
    Product, Batch, AccountLedger, UserTable, GeneralSettings, PurchaseOrderMaster, Parties
import xlwt


def generate_serializer_errors(args):
    message = ""
    for key, values in args.items():
        error_message = ""
        for value in values:
            error_message += value + ","
        error_message = error_message[:-1]

        message += "%s : %s | " %(key,error_message)
    return message[:-3]


def get_auto_idMaster(model,BranchID,CompanyID):
    PurchaseMasterID = 1
    
    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('PurchaseMasterID'))
        

        if max_value:
            max_purchaseMasterId = max_value.get('PurchaseMasterID__max', 0)
            
            PurchaseMasterID = max_purchaseMasterId + 1
            
        else:
            PurchaseMasterID = 1
     

    return PurchaseMasterID


def get_auto_id(model,BranchID,CompanyID):
    PurchaseDetailsID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('PurchaseDetailsID'))
    

    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('PurchaseDetailsID'))
        

        if max_value:
            max_purchaseDetailsId = max_value.get('PurchaseDetailsID__max', 0)
            
            PurchaseDetailsID = max_purchaseDetailsId + 1
            
        else:
            PurchaseDetailsID = 1

    return PurchaseDetailsID


def get_auto_StockRateID(model,BranchID,CompanyID):
    StockRateID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('StockRateID'))
    

    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('StockRateID'))
        

        if max_value:
            max_stockRateId = max_value.get('StockRateID__max', 0)
            
            StockRateID = max_stockRateId + 1
            
        else:
            StockRateID = 1

    return StockRateID


def get_auto_StockTransID(model,BranchID,CompanyID):
    StockTransID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('StockTransID'))
    

    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('StockTransID'))
        

        if max_value:
            max_stockTransId = max_value.get('StockTransID__max', 0)
            
            StockTransID = max_stockTransId + 1
            
        else:
            StockTransID = 1


    return StockTransID


def purchase_taxgroup_excel_data(CompanyID,BranchID,FromDate,ToDate,PriceRounding):
    final_data = []
    is_ok = False
    count = 0
    # interstate b2b
    tax_types = ["GST Inter-state B2B","GST Inter-state B2C","GST Intra-state B2B","GST Intra-state B2C","GST Intra-state B2B Unregistered"]
    for tx in tax_types:
        if PurchaseMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,Date__gte=FromDate,Date__lte=ToDate,TaxType=tx).exists():
            purchase_instances = PurchaseMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,Date__gte=FromDate,Date__lte=ToDate,TaxType=tx)
            purchase_ids = purchase_instances.values_list('PurchaseMasterID', flat=True)

            purchase_details = PurchaseDetails.objects.filter(CompanyID=CompanyID,BranchID=BranchID,PurchaseMasterID__in=purchase_ids)
            # purchase_details = PurchaseDetails.objects.filter(CompanyID=CompanyID,BranchID=BranchID,PurchaseMasterID__in=purchase_ids).exclude(IGSTPerc=0)
            tax_list = purchase_details.values_list('IGSTPerc', flat=True)
            tax_list = set(tax_list)
            print(purchase_details,"+++++++++++++++++++++++++++++++++")
            # count = 0
            for t in tax_list:
                gouprd_details = purchase_details.filter(IGSTPerc=t)
                if gouprd_details:
                    final_data.append({
                        "TaxType" : tx,
                        "TaxPerc" : t,
                        "total_Qty" : 0,
                        "total_amount" : 0,
                        "total_SGSTAmount" : 0,
                        "total_CGSTAmount" : 0,
                        "total_IGSTAmount" : 0,
                        "total_sum_Total" : 0,
                        "data" : [],
                        })
                    total_Qty = 0
                    total_amount = 0
                    total_SGSTAmount = 0
                    total_CGSTAmount = 0
                    total_IGSTAmount = 0
                    total_sum_Total = 0
                    for g in gouprd_details:
                        PurchaseMasterID = g.PurchaseMasterID
                        Date = purchase_instances.get(PurchaseMasterID=PurchaseMasterID).Date
                        InvoiceNo = purchase_instances.get(PurchaseMasterID=PurchaseMasterID).RefferenceBillNo
                        LedgerID = purchase_instances.get(PurchaseMasterID=PurchaseMasterID).LedgerID
                        ProductID = g.ProductID
                        party = ""
                        GSTN = ""
                        City = ""
                        State_id = ""
                        State_Code = ""
                        state_name = "" 
                        if AccountLedger.objects.filter(CompanyID=CompanyID,BranchID=BranchID,LedgerID=LedgerID,AccountGroupUnder__in=[10,29]).exists():
                            parties = Parties.objects.get(CompanyID=CompanyID,BranchID=BranchID,LedgerID=LedgerID)
                            party = parties.PartyName
                            GSTN = parties.GSTNumber
                            City = parties.City
                            State_id = parties.State
                            State_Code = parties.State_Code
                            if State_id:
                                if State.objects.filter(pk=State_id).exists():
                                    state_name = State.objects.get(pk=State_id).Name

                        product = Product.objects.get(CompanyID=CompanyID,BranchID=BranchID,ProductID=ProductID)
                        item_name = product.ProductName
                        HSN = product.HSNCode

                        Qty = g.Qty
                        UnitID = PriceList.objects.get(CompanyID=CompanyID,BranchID=BranchID,PriceListID=g.PriceListID).UnitID
                        UnitName = Unit.objects.get(CompanyID=CompanyID,BranchID=BranchID,UnitID=UnitID).UnitName
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
                            "Date" : str_date,
                            "InvoiceDate" : str_date,
                            "InvoiceNo" : InvoiceNo,
                            "party" : party,
                            "GSTN" : GSTN,
                            "City" : City,
                            "State" : state_name,
                            "State_Code" : State_Code,
                            "item_name" : item_name,
                            "HSN" : HSN,
                            "Qty" : Qty,
                            "UnitName" : UnitName,
                            "Amount" : Amount,
                            "SGSTPerc" : SGSTPerc,
                            "CGSTPerc" : CGSTPerc,
                            "IGSTPerc" : IGSTPerc,
                            "SGSTAmount" : SGSTAmount,
                            "CGSTAmount" : CGSTAmount,
                            "IGSTAmount" : IGSTAmount,                            
                            "Total" : '%.2f' % round(Total, 2),
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


def export_to_excel_purchase_taxgroup(wb,data,FromDate,ToDate):
    ws = wb.add_sheet("sheet1")
    # main header
    # ws.write(0, 0, "SlNo")
    # ws.write(0, 1, "Date")
    # ws.write(0, 2, "Invoice Date")
    # ws.write(0, 3, "Invoice No")
    # ws.write(0, 4, "Party")
    # ws.write(0, 5, "GSTIN / UIN")
    # ws.write(0, 6, "City")
    # ws.write(0, 7, "State")
    # ws.write(0, 8, "State Code")
    # ws.write(0, 9, "ItemName")
    # ws.write(0, 10, "HSN")
    # ws.write(0, 11, "Qty")
    # ws.write(0, 12, "Unit")
    # ws.write(0, 13, "Amount")
    # ws.write(0, 14, "SGST%")
    # ws.write(0, 15, "CGST%")
    # ws.write(0, 16, "IGST%")
    # ws.write(0, 17, "SGST")
    # ws.write(0, 18, "CGST")
    # ws.write(0, 19, "IGST")
    # ws.write(0, 20, "Total")



    columns = ['SlNo','Date','Invoice Date','Invoice No','Party','GSTIN / UIN','City','State','State Code','ItemName','HSN','Qty','Unit','Amount','SGST','CGST','IGST','SGST','CGST','IGST','Total']
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
        data_row+=1
        ws.write(data_row, data_col, str('Purchase From ')+str(data[i]['TaxType'])+str(" - ")+str(data[i]['TaxPerc'])+str("% Taxable"),sub_header_style)
        data_row+=1
        ws.write(data_row, data_col, str("From "+str(FromDate)+str(" To ")+str(ToDate)),sub_header_style)

        data_row+=1
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
                total_row+=1                
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
            data_row+=1
            SlNo+=1
        print(data_row,"&&&&&&&&&&&")
        ws.write(data_row, 9, "Total",total_values_style)
        ws.write(data_row, 10, "")
        ws.write(data_row, 11, total_Qty,total_values_style)
        ws.write(data_row, 12, "")
        ws.write(data_row, 13, total_amount,total_values_style)
        ws.write(data_row, 14, "")
        ws.write(data_row, 15, "")
        ws.write(data_row, 16, "")
        ws.write(data_row, 17, total_SGSTAmount,total_values_style)
        ws.write(data_row, 18, total_CGSTAmount,total_values_style)
        ws.write(data_row, 19, total_IGSTAmount,total_values_style)
        ws.write(data_row, 20, total_sum_Total,total_values_style)


# purchases gst report
def purchase_gst_excel_data(CompanyID,BranchID,FromDate,ToDate,PriceRounding,UserID):
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
        UserID = UserTable.objects.get(id=UserID).customer.user.pk
        # if PurchaseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID).exists():
        instances = PurchaseMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID)
        return_instances = PurchaseReturnMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate, CreatedUserID=UserID)
        final_array = []
        # =======
        for i in instances:
            LedgerID = i.LedgerID
            if AccountLedger.objects.filter(LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID).exists():
                Particulars = AccountLedger.objects.get(
                    LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID)
                LedgerName = Particulars.LedgerName
                if Particulars.AccountGroupUnder == 29:
                    party_gstin = Parties.objects.get(
                        LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID, PartyType="supplier", PartyCode=Particulars.LedgerCode).GSTNumber

            str_date = i.Date.strftime('%m/%d/%Y')
            print(str_date,':**************************::::::::::')
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
                "IGSTAmount": i.IGSTAmount,
                "CGSTAmount": i.CGSTAmount,
                "CESSAmount": 0,
                # "KFCAmount" : i.KFCAmount,
                "TotalTaxableAmount": i.TotalTaxableAmount,
            }
            if float(i.TotalTax) > 0:
                final_array.append(dic)

        for i in return_instances:
            LedgerID = i.LedgerID
            if AccountLedger.objects.filter(LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID).exists():
                Particulars = AccountLedger.objects.get(
                    LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID)
                LedgerName = Particulars.LedgerName
                if Particulars.AccountGroupUnder == 29:
                    party_gstin = Parties.objects.get(
                        LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID, PartyType="supplier", PartyCode=Particulars.LedgerCode).GSTNumber
            # try:
            #     KFCAmount = int(i.KFCAmount)
            # except:
            #     KFCAmount = 0

            TotalTaxableAmount = float(i.TotalTaxableAmount)
            if TotalTaxableAmount:
                TotalTaxableAmount = float(i.TotalTaxableAmount)
            else:
                TotalTaxableAmount = 0

            str_date = i.VoucherDate.strftime('%m/%d/%Y')

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
                "TotalTax": int(i.TotalTax*-1),
                "SGSTAmount": int(i.SGSTAmount*-1),
                "IGSTAmount": int(i.IGSTAmount*-1),
                "CGSTAmount": int(i.CGSTAmount*-1),
                "CESSAmount": 0,
                # "KFCAmount" : KFCAmount*-1,
                "TotalTaxableAmount": TotalTaxableAmount*-1,
            }
            if float(i.TotalTax) > 0:
                final_array.append(dic)

        for i in final_array:
            Total_TotalTaxableAmount += float(i['TotalTaxableAmount'])
            Total_TotalTax += float(i['TotalTax'])

            Total_SGSTAmount += float(i['SGSTAmount'])
            Total_CGSTAmount += float(i['CGSTAmount'])
            Total_IGSTAmount += float(i['IGSTAmount'])
            Total_GrandTotal += float(i['GrandTotal'])
            # Total_KFCAmount += float(i['KFCAmount'])
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
            "Total_GrandTotal" : Total_GrandTotal
        }
        return response_data


    else:
        # if PurchaseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
        instances = PurchaseMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)
        # ======
        return_instances = PurchaseReturnMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate)

        final_array = []
        # =======
        for i in instances:
            LedgerID = i.LedgerID
            if AccountLedger.objects.filter(LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID).exists():
                Particulars = AccountLedger.objects.get(
                    LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID)
                LedgerName = Particulars.LedgerName
                if Particulars.AccountGroupUnder == 29:
                    party_gstin = Parties.objects.get(
                        LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID, PartyType="supplier", PartyCode=Particulars.LedgerCode).GSTNumber
            str_date = i.Date.strftime('%m/%d/%Y')
            str_invoice_date = i.VenderInvoiceDate.strftime('%m/%d/%Y')

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
                "IGSTAmount": i.IGSTAmount,
                "CGSTAmount": i.CGSTAmount,
                "CESSAmount": 0,
                # "KFCAmount" : i.KFCAmount,
                "TotalTaxableAmount": i.TotalTaxableAmount,
            }
            if float(i.TotalTax) > 0:
                final_array.append(dic)

        for i in return_instances:
            LedgerID = i.LedgerID
            if AccountLedger.objects.filter(LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID).exists():
                Particulars = AccountLedger.objects.get(
                    LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID)
                LedgerName = Particulars.LedgerName
                if Particulars.AccountGroupUnder == 29:
                    party_gstin = Parties.objects.get(
                        LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID, PartyType="supplier", PartyCode=Particulars.LedgerCode).GSTNumber

            # try:
            #     KFCAmount = int(i.KFCAmount)
            # except:
            #     KFCAmount = 0

            TotalTaxableAmount = float(i.TotalTaxableAmount)
            if TotalTaxableAmount:
                TotalTaxableAmount = float(i.TotalTaxableAmount)
            else:
                TotalTaxableAmount = 0
            str_date = i.VoucherDate.strftime('%m/%d/%Y')
            str_invoice_date = i.VenderInvoiceDate.strftime('%m/%d/%Y')

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
                "TotalTax": int(i.TotalTax*-1),
                "SGSTAmount": int(i.SGSTAmount*-1),
                "IGSTAmount": int(i.IGSTAmount*-1),
                "CGSTAmount": int(i.CGSTAmount*-1),
                "CESSAmount": 0,
                # "KFCAmount" : KFCAmount*-1,
                "TotalTaxableAmount": TotalTaxableAmount*-1,
            }
            if float(i.TotalTax) > 0:
                final_array.append(dic)

        for i in final_array:
            Total_TotalTaxableAmount += float(i['TotalTaxableAmount'])
            Total_TotalTax += float(i['TotalTax'])

            Total_SGSTAmount += float(i['SGSTAmount'])
            Total_CGSTAmount += float(i['CGSTAmount'])
            Total_IGSTAmount += float(i['IGSTAmount'])
            Total_GrandTotal += float(i['GrandTotal'])
            # Total_KFCAmount += float(i['KFCAmount'])

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
            "Total_GrandTotal" : Total_GrandTotal
        }
        return response_data


def export_to_excel_purchase_gst(wb,data,FromDate,ToDate):
    ws = wb.add_sheet("Purchase GST Report")

    columns = ['Date','Voucher No','Refference Bill No','Vender Invoice Date','Particulars','GSTIN/UIN','Voucher Type','Tax Type','Taxable Amount','SGST','CGST','IGST','Cess','Total Tax Amount','Grand Total',]
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
        ws.write(row_num, col_num, columns[col_num],sub_header_style)
   

    data_col = 0
    data_row=1
    SlNo = 1


    print(data['purchase_data'],'oppppppppppppopopopo')
    Total_TotalTaxableAmount = data['Total_TotalTaxableAmount']
    Total_SGSTAmount = data['Total_SGSTAmount']
    Total_IGSTAmount = data['Total_IGSTAmount']
    Total_CGSTAmount = data['Total_CGSTAmount']

    Total_TotalTax = data['Total_TotalTax']
    Total_GrandTotal = data['Total_GrandTotal']

    for j in data['purchase_data']:             
        ws.write(data_row, 0, j['Date'])
        ws.write(data_row, 1, j['VoucherNo'])
        ws.write(data_row, 2, j['RefferenceBillNo'])
        ws.write(data_row, 3, j['VenderInvoiceDate'])
        ws.write(data_row, 4, j['Particulars'])
        ws.write(data_row, 5, j['party_gstin'])
        ws.write(data_row, 6, j['VoucherType'])
        ws.write(data_row, 7, j['TaxType'])
        ws.write(data_row, 8, j['TotalTaxableAmount'])
        ws.write(data_row, 9, j['SGSTAmount'])
        ws.write(data_row, 10, j['CGSTAmount'])
        ws.write(data_row, 11, j['IGSTAmount'])
        ws.write(data_row, 12, 0)
        ws.write(data_row, 13, j['TotalTax'])
        ws.write(data_row, 14, j['GrandTotal'])
        data_row+=1
    print(data_row,"&&&&&&&&&&&")
    ws.write(data_row, 7, "Total",total_label_style)
    ws.write(data_row, 8, Total_TotalTaxableAmount,total_values_style)
    ws.write(data_row, 9, Total_SGSTAmount,total_values_style)
    ws.write(data_row, 10, Total_IGSTAmount,total_values_style)
    ws.write(data_row, 11, Total_CGSTAmount,total_values_style)
    ws.write(data_row, 12, 0,total_values_style)
    ws.write(data_row, 13, Total_TotalTax,total_values_style)
    ws.write(data_row, 14, Total_GrandTotal,total_values_style)

