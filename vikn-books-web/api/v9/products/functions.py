import string
import random
from django.http import HttpResponse
from decimal import Decimal
from django.db.models import Max, Sum
import re
from rest_framework import status
from rest_framework.response import Response
from api.v9.priceLists.serializers import PriceListRestSerializer
from api.v9.products.serializers import MultyUnitExcelSerializer, ProductRestSerializer, ProductsExcelSerializer,Batch_ListSerializer
from brands.models import BranchSettings, PriceList, Product, StockPosting,Batch
from main.functions import activity_log, converted_float, get_BranchSettings, get_company
import xlwt
from xlwt import Workbook, XFStyle, Borders, Pattern, Font, easyxf, Alignment
from django.utils.translation import gettext_lazy as _
from django.db import connection
import pandas as pd
import json


def generate_serializer_errors(args):
    message = ""
    for key, values in args.items():
        error_message = ""
        for value in values:
            error_message += value + ","
        error_message = error_message[:-1]

        message += "%s : %s | " % (key, error_message)
    return message[:-3]


def generate_priceList_serializer_errors(args):
    message = ""
    for key, values in args.items():
        error_message = ""
        for value in values:
            error_message += value + ","
        error_message = error_message[:-1]

        message += "%s : %s | " % (key, error_message)
    return message[:-3]


def get_auto_id(model, BranchID, CompanyID):
    ProductID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id = model.objects.filter(
        CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('ProductID'))
    max_value = 0
    if model.objects.filter(CompanyID=CompanyID).exists():
        max_value = model.objects.filter(
            CompanyID=CompanyID).aggregate(Max('ProductID'))
    if max_value:
        max_productId = max_value.get('ProductID__max', 0)
        ProductID = max_productId + 1

    else:
        ProductID = 1

    # if model.objects.filter(CompanyID=CompanyID,BrandID=BrandID).exists():
    #     BrandID = 1

    return ProductID


def get_auto_priceListid(model, BranchID, CompanyID):
    PriceListID = 1
    max_value = None
    PriceListID = None
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id = model.objects.filter(
        CompanyID=CompanyID).aggregate(Max('PriceListID'))

    if model.objects.filter(CompanyID=CompanyID).exists():
        max_value = model.objects.filter(
            CompanyID=CompanyID).aggregate(Max('PriceListID'))

    if max_value:
        max_priceListId = max_value.get('PriceListID__max', 0)

        PriceListID = max_priceListId + 1

    else:
        PriceListID = 1

    # if model.objects.filter(CompanyID=CompanyID,BrandID=BrandID).exists():
    #     BrandID = 1

    return PriceListID


def get_auto_ProductBarcode(model, BranchID, CompanyID):

    AutoBarcode = 1
    if model.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        latest_AutoBarcode = model.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID).order_by("ProductBarcodeID").last()

        AutoBarcode = latest_AutoBarcode.ProductBarcodeID

        AutoBarcode = AutoBarcode + 1

    return AutoBarcode


def get_ProductCode(model, BranchID, CompanyID):
    ProductCode = "PC1000"
    if model.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        latest_ProductCode = model.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID).order_by("ProductID").last()
        ProductCode = latest_ProductCode.ProductCode
        # temp = re.compile("([a-zA-Z]+)([0-9]+)")
        # res = temp.match(ProductCode).groups()
        # code, number = res
        # number = int(number) + 1
        # ProductCode = str(code) + str(number)
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
                ProductCodeNumber = re.findall(r'\d+', ProductCode)[-1]
                rest = ProductCode.split(ProductCodeNumber)[0]
                ProductCode = str(int(ProductCodeNumber) +
                                    1).zfill(len(ProductCodeNumber))
                ProductCode = str(rest) + str(ProductCode)
        else:
            code = str(float(ProductCode) + 1)
            code = code.rstrip('0').rstrip('.') if '.' in code else code
            ProductCode = code.zfill(len(ProductCode))
    return ProductCode


def get_auto_AutoBarcode(model, BranchID, CompanyID):
    AutoBarcode = 70000
    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        latest_AutoBarcode = model.objects.filter(
            CompanyID=CompanyID).order_by("PriceListID").last()
        AutoBarcode = latest_AutoBarcode.AutoBarcode
        AutoBarcode = AutoBarcode + 1

    return AutoBarcode


def get_auto_AutoBatchCode(model, BranchID, CompanyID):
    BatchCode = 500000
    if model.objects.filter(CompanyID=CompanyID).exists():
        latest_BatchCode = model.objects.filter(
            CompanyID=CompanyID).order_by("BatchCode").last()
        BatchCode = latest_BatchCode.BatchCode
        BatchCode = int(BatchCode) + 1
    return BatchCode


def get_auto_BatchNo(model, BranchID, CompanyID):

    BatchNo = 5000
    if model.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        latest_BatchNo = model.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID).order_by("BatchNo").last()

        BatchNo = latest_BatchNo.BatchNo

        BatchNo = BatchNo + 1

    return BatchNo


# def update_stock(CompanyID,BranchID,ProductID,Qty,value):
#     Stock = 0
#     pro_ins = Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID).first()
#     current_stock = pro_ins.Stock
#     if value == "IN":
#         Stock = converted_float(current_stock) + converted_float(Qty)
#     elif value == "OUT":
#         Stock = converted_float(current_stock) - converted_float(Qty)

#     pro_ins.Stock = Stock
#     pro_ins.save()
#     return Stock


def update_stock(CompanyID, BranchID, ProductID):
    check_productsForAllBranches = False
    if BranchSettings.objects.filter(CompanyID=CompanyID, SettingsType="productsForAllBranches").exists():
        check_productsForAllBranches = BranchSettings.objects.get(
            CompanyID=CompanyID, SettingsType="productsForAllBranches").SettingsValue
    if check_productsForAllBranches == True or check_productsForAllBranches == "True":
        stock_postings = StockPosting.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID)
        pro_ins = Product.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID).first()

    else:
        stock_postings = StockPosting.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
        pro_ins = Product.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID).first()

    Product_Stock = 0
    if stock_postings.exists():
        stock_instances = stock_postings
        TotalQtyIn = stock_instances.aggregate(Sum('QtyIn'))
        TotalQtyIn = TotalQtyIn['QtyIn__sum']
        TotalQtyOut = stock_instances.aggregate(Sum('QtyOut'))
        TotalQtyOut = TotalQtyOut['QtyOut__sum']
        Product_Stock = converted_float(TotalQtyIn) - converted_float(TotalQtyOut)

    pro_ins.Stock = Product_Stock
    pro_ins.save()
    return Product_Stock


def get_stock(CompanyID, BranchID, ProductID, VoucherType, VoucherMasterID):
    Invoice_Stock = 0
    if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType, VoucherMasterID=VoucherMasterID, ProductID=ProductID).exists():
        stock_instances = StockPosting.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType, VoucherMasterID=VoucherMasterID, ProductID=ProductID)
        TotalQtyIn = stock_instances.aggregate(Sum('QtyIn'))
        TotalQtyIn = TotalQtyIn['QtyIn__sum']
        TotalQtyOut = stock_instances.aggregate(Sum('QtyOut'))
        TotalQtyOut = TotalQtyOut['QtyOut__sum']
        Invoice_Stock = converted_float(TotalQtyIn) - converted_float(TotalQtyOut)
    return abs(Invoice_Stock)


def get_Allproducts(CompanyID, CreatedUserID, PriceRounding, BranchID, request):

    CompanyID = get_company(CompanyID)
    if get_BranchSettings(CompanyID, "productsForAllBranches"):
        product_instance = Product.objects.filter(
            CompanyID=CompanyID, Active=True)
    else:
        product_instance = Product.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Active=True)

    if product_instance.exists():
        print("UVAIS............................................>>>>>>.")
        serialized = ProductsExcelSerializer(product_instance, many=True, context={
            "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding})

        # request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product',
                     'List', 'Product List Viewed successfully.', 'Product List Viewed successfully.')
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }

        return response_data
    else:
        # request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Product',
                     'List', 'Product List Viewed Failed.', 'Product Not Found in this Branch!')
        response_data = {
            "StatusCode": 6001,
            "message": "Product Not Found in this Branch!!"
        }

        return response_data

def query_Allproducts_toExcel(CompanyID, CreatedUserID, PriceRounding, BranchID, request):

    cursor = connection.cursor()
    dic = {
        "BranchID": BranchID,
        "CreatedUserID": CreatedUserID,
        "PriceRounding": PriceRounding,
        "CompanyID": CompanyID,
        "request": request,
    }
    if get_BranchSettings(CompanyID, "productsForAllBranches"):
        cursor.execute(
            """
            SELECT   P."ProductCode",P."ProductName",P."Description",PL."PurchasePrice",PL."SalesPrice",PL."SalesPrice1",PL."SalesPrice2",PL."SalesPrice3",
            (SELECT NULLIF("GroupName", '') FROM public."productgroup_productgroup" AS PG WHERE PG."CompanyID_id" = P."CompanyID_id" AND PG."ProductGroupID" = P."ProductGroupID"  ) AS PurchasePrice,
            (SELECT NULLIF("UnitName", '') FROM public."units_unit" AS UN WHERE UN."CompanyID_id" = P."CompanyID_id" AND UN."UnitID" = PL."UnitID" AND PL."DefaultUnit" = 'true'  ) AS UnitName,
            (SELECT NULLIF("BrandName", '') FROM public."brands_brand" AS BR WHERE BR."CompanyID_id" = P."CompanyID_id" AND BR."BrandID" = P."BrandID"  ) AS BrandName,
            P."VatID",
            P."StockMinimum",
            P."StockReOrder",
            P."StockMaximum",
            PL."Barcode",
            PL."AutoBarcode"

            FROM public.products_product AS P       
            INNER JOIN public.pricelist_pricelist PL ON P."ProductID" = PL."ProductID" 
            AND P."BranchID" = PL."BranchID" AND PL."DefaultUnit" = 'true'   AND P."CompanyID_id" =PL."CompanyID_id"    
            WHERE P."CompanyID_id" = %(CompanyID)s AND P."Active" = 'true'

            """,
            dic,)
    else:
        cursor.execute(
            """
            SELECT   P."ProductCode",P."ProductName",P."Description",PL."PurchasePrice",PL."SalesPrice",PL."SalesPrice1",PL."SalesPrice2",PL."SalesPrice3",
            (SELECT NULLIF("GroupName", '') FROM public."productgroup_productgroup" AS PG WHERE PG."CompanyID_id" = P."CompanyID_id" AND PG."ProductGroupID" = P."ProductGroupID"  ) AS PurchasePrice,
            (SELECT NULLIF("UnitName", '') FROM public."units_unit" AS UN WHERE UN."CompanyID_id" = P."CompanyID_id" AND UN."UnitID" = PL."UnitID" AND PL."DefaultUnit" = 'true'  ) AS UnitName,
            (SELECT NULLIF("BrandName", '') FROM public."brands_brand" AS BR WHERE BR."CompanyID_id" = P."CompanyID_id" AND BR."BrandID" = P."BrandID"  ) AS BrandName,
            P."VatID",
            P."StockMinimum",
            P."StockReOrder",
            P."StockMaximum",
            PL."Barcode",
            PL."AutoBarcode"

            FROM public.products_product AS P       
            INNER JOIN public.pricelist_pricelist PL ON P."ProductID" = PL."ProductID" 
            AND P."BranchID" = PL."BranchID" AND PL."DefaultUnit" = 'true'   AND P."CompanyID_id" =PL."CompanyID_id"    
            WHERE P."CompanyID_id" = %(CompanyID)s AND P."Active" = 'true' AND
            P."BranchID" = %(BranchID)s 
            """,
            dic,
        )
    data = cursor.fetchall()
    df = pd.DataFrame(data)
    df.columns = [
        "ProductCode",
        "ProductName",
        "Description",
        "PurchasePrice",
        "SalesPrice",
        "SalesPrice1",
        "SalesPrice2",
        "SalesPrice3",
        "GroupName",
        "Unit",
        "BrandName",
        "VAT",
        "StockMinimum",
        "StockReOrder",
        "StockMaximum",
        "Barcode",
        "AutoBarcode",
    ]
    json_records = df.reset_index().to_json(orient="records")
    details = json.loads(json_records)
    return df, details



def get_AllmultyUnits(CompanyID, CreatedUserID, PriceRounding, BranchID, request):
    CompanyID = get_company(CompanyID)
    if get_BranchSettings(CompanyID, "productsForAllBranches"):
        product_instance = Product.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Active=True)
    else:
        product_instance = Product.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Active=True)

    if product_instance.exists():
        instances = product_instance

        product_ids = instances.values_list('ProductID', flat=True)
        price_list = PriceList.objects.filter(
            CompanyID=CompanyID, ProductID__in=product_ids, DefaultUnit=False)

        serialized = MultyUnitExcelSerializer(price_list, many=True, context={
            "CompanyID": CompanyID, "PriceRounding": PriceRounding})

        # request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product',
                     'List', 'Product List Viewed successfully.', 'Product List Viewed successfully.')
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }

        return response_data
    else:
        # request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Product',
                     'List', 'Product List Viewed Failed.', 'Product Not Found in this Branch!')
        response_data = {
            "StatusCode": 6001,
            "message": "Product Not Found in this Branch!!"
        }

        return response_data


def batch_excel_data(CompanyID,BranchID,FromDate,ToDate,PriceRounding,ProductGroupID,ProductID,BatchCode):
    is_ok = True
    message = ""
    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, CreatedDate__date__gte=FromDate, CreatedDate__date__lte=ToDate).exists():
        batch_ins = Batch.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, CreatedDate__date__gte=FromDate, CreatedDate__date__lte=ToDate)
        product_ids = batch_ins.values_list('ProductID', flat=True)
        if ProductGroupID:
            if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID__in=product_ids, ProductGroupID=ProductGroupID).exists():
                product_ids = Product.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID__in=product_ids, ProductGroupID=ProductGroupID).values_list('ProductID', flat=True)
                batch_ins = batch_ins.filter(ProductID__in=product_ids)
            else:
                is_ok = False
                message = "No Batch found under this Product Group"
        elif ProductID:
            if batch_ins.filter(ProductID=ProductID).exists():
                batch_ins = batch_ins.filter(ProductID=ProductID)
            else:
                is_ok = False
                message = "No Batch found with this Product"
        elif BatchCode:
            if batch_ins.filter(BatchCode=BatchCode).exists():
                batch_ins = batch_ins.filter(BatchCode=BatchCode)
            else:
                is_ok = False
                message = "No Batch found with this Batch Code"

        count = len(batch_ins)
       
        serialized = Batch_ListSerializer(batch_ins, many=True, context={
         "CompanyID": CompanyID, "PriceRounding": PriceRounding})
        if is_ok:
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "total_count": count
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "message": message
            }
        return response_data
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Batch Not Found During this dates"
        }

        return response_data



def export_to_excel_batch(wb, data, FromDate, ToDate, title,columns):
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
            BatchCode = j['BatchCode']
        except:
            BatchCode = '-'
        try:
            Date = j['Date']
        except:
            Date = '-'
        try:
            ProductName = j['ProductName']
        except:
            ProductName = '-'
        try:
            ProductGroupName = j['ProductGroupName']
        except:
            ProductGroupName = '-'
        try:
            ManufactureDate = j['ManufactureDate']
        except:
            ManufactureDate = '-'
        try:
            ExpiryDate = j['ExpiryDate']
        except:
            ExpiryDate = '-'
        try:
            PurchasePrice = j['PurchasePrice']
        except:
            PurchasePrice = 0
        try:
            SalesPrice = j['SalesPrice']
        except:
            SalesPrice = 0
        try:
            Stock = j['Stock']
        except:
            Stock = 0


        ws.write(data_row, 0, BatchCode)
        ws.write(data_row, 1, Date)
        if ProductName == "Total":
            ws.write(data_row, 2, ProductName, total_label_style)
        else:
            ws.write(data_row, 2, ProductName)

        ws.write(data_row, 3, ProductGroupName, value_decimal_style)
        ws.write(data_row, 4, ManufactureDate, value_decimal_style)
        ws.write(data_row, 5, ExpiryDate, value_decimal_style)
        ws.write(data_row, 6, converted_float(PurchasePrice), value_decimal_style)
        ws.write(data_row, 7, converted_float(SalesPrice), value_decimal_style)
        ws.write(data_row, 8, converted_float(Stock), value_decimal_style)
        # ws.write(data_row, 9, converted_float(Discount), value_decimal_style)
        # ws.write(data_row, 10, converted_float(NetAmount), value_decimal_style)
        data_row += 1



# def query_product_search(CompanyID,PriceRounding,product_name,length,type,Date,WarehouseID,BranchList,check_EnableProductBatchWise,check_AllowNegativeStockSales):
#     cursor = connection.cursor()
#     dic = {'CompanyID':CompanyID,'PriceRounding': PriceRounding, 'product_name': product_name,'length':length,'type':type,'Date':Date,
#            'WarehouseID': WarehouseID,'BranchList':BranchList,'check_EnableProductBatchWise':check_EnableProductBatchWise,'check_AllowNegativeStockSales':check_AllowNegativeStockSales}
#     if type == "Sales":
#         cursor.execute('''
#            SELECT
#             P."ProductID", P."ProductCode",  
#             P."ProductName",  
#             coalesce(PL."PurchasePrice",0) AS PurchasePrice,  
#             coalesce(PL."SalesPrice",0) AS SalesPrice,  
#             (SELECT "UnitName" FROM public."units_unit" WHERE  
#             "UnitID" = PL."UnitID" AND "BranchID" in %(BranchList)s AND "CompanyID_id" = P."CompanyID_id") AS UnitName
#             FROM "products_product" as P  
#             INNER JOIN "pricelist_pricelist" as PL ON P."ProductID" = PL."ProductID"  
#             AND P."CompanyID_id" = PL."CompanyID_id"  
#             Where PL."DefaultUnit" = 'true' AND "IsSales" = 'TRUE'  
#             AND P."ProductName" LIKE '%' %(product_name)s '%'  AND P."CompanyID_id" = '878acf1f-6090-47f6-ab00-2b0f61cbcce6'
#             ORDER BY P."ProductName" limit 20
#             ''',dic)
#     data = cursor.fetchall()
#     df = pd.DataFrame(data)
#     heads = [                
#             str(_('ProductID')),str(_('ProductCode')),str(_('ProductName')),str(_('PurchasePrice')),str(_('SalesPrice')),
#             str(_('UnitName'))]
#     df.columns = heads
#     json_records = df.reset_index().to_json(orient ='records')
#     details = json.loads(json_records)
#     print(">>>>>>>>>>>>>>>>>>>>>>>>>>detailssssss")
#     print(details)
    
#     return data


