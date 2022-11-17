import string
from django.contrib.auth.models import User
from main.functions import converted_float, get_company
from api.v9.products.functions import get_auto_id, get_auto_priceListid, get_ProductCode, get_auto_AutoBarcode, get_auto_BatchNo, get_auto_AutoBatchCode
from django.utils.crypto import get_random_string
from celery_progress.backend import ProgressRecorder
from celery import shared_task
from brands import models
import datetime
import xlrd


# @shared_task
# def create_random_user_accounts(total):
#     for i in range(total):
#         username = 'user_{}'.format(
#             get_random_string(10, string.ascii_letters))
#         email = '{}@example.com'.format(username)
#         password = get_random_string(50)
#         models.User.objects.create_user(
#             username=username, email=email, password=password)
#     return '{} random users created with success!'.format(total)


@shared_task(bind=True)
def import_product_task(self, input_excel, CompanyID, CreatedUserID, BranchID, Type):
    progress_recorder = ProgressRecorder(self)
    today = datetime.datetime.now()
    CompanyID = get_company(CompanyID)
    book = xlrd.open_workbook(input_excel)
    sheet = book.sheet_by_index(0)
    total = sheet.nrows
    dict_list = []
    keys = [str(sheet.cell(0, col_index).value)
            for col_index in range(sheet.ncols)]
    for row_index in range(1, sheet.nrows):
        d = {keys[col_index]: str(sheet.cell(row_index, col_index).value)
             for col_index in range(sheet.ncols)}
        dict_list.append(d)

    def is_number_tryexcept(item):
        """ Returns True is string is a number. """
        try:
            converted_float(item)
            return item
        except ValueError:
            item = 0
            return item

    def is_number_or_is_string(item):
        """ Returns True is string is a number. """
        try:
            item = int(converted_float(item))
            return item
        except ValueError:
            item = str(item)
            return item
    count = 0
    message = '{} products created successfully!'
    str_count = ""

    product_list = []
    product_list_log = []
    price_list = []
    price_list_log = []
    from api.v9.products.functions import get_auto_id
    ProductID = get_auto_id(models.Product, BranchID, CompanyID)
    PriceListID = get_auto_priceListid(models.PriceList, BranchID, CompanyID)
    AutoBarcode = get_auto_AutoBarcode(models.PriceList, BranchID, CompanyID)
    for item in dict_list:
        # count += 1

        ProductName = item['ProductName']
        Description = item['Description']
        PurchasePrice = item['PurchasePrice']
        PurchasePrice = is_number_tryexcept(PurchasePrice)
        if PurchasePrice == 0 or PurchasePrice == "" or PurchasePrice == "0":
            PurchasePrice = 0
        else:
            PurchasePrice = float(PurchasePrice)

        SalesPrice = item['SalesPrice']

        try:
            SalesPrice1 = item['SalesPrice1']
            if SalesPrice1 == "":
                SalesPrice1 = 0
        except:
            SalesPrice1 = 0
        try:
            SalesPrice2 = item['SalesPrice2']
            if SalesPrice2 == "":
                SalesPrice2 = 0
        except:
            SalesPrice2 = 0
        try:
            SalesPrice3 = item['SalesPrice3']
            if SalesPrice3 == "":
                SalesPrice3 = 0
        except:
            SalesPrice3 = 0

        SalesPrice = is_number_tryexcept(SalesPrice)
        SalesPrice1 = is_number_tryexcept(SalesPrice1)
        SalesPrice2 = is_number_tryexcept(SalesPrice2)
        SalesPrice3 = is_number_tryexcept(SalesPrice3)

        GroupName = item['GroupName']
        UnitName = item['Unit']
        BrandName = item['BrandName']
        try:
            ProductCode = item['ProductCode']
            # ProductCode = is_number_or_is_string(ProductCode)
        except:
            ProductCode = ""

        try:
            VAT = item['VAT']
        except:
            VAT = 0

        StockMinimum = item['StockMinimum']
        if StockMinimum == "":
            StockMinimum = 0
        StockReOrder = item['StockReOrder']
        if StockReOrder == "":
            StockReOrder = 0
        StockMaximum = item['StockMaximum']
        if StockMaximum == "":
            StockMaximum = 0
        Barcode = item['Barcode']
        try:
            MultiFactor = item['MultiFactor']
        except:
            MultiFactor = 1

        Barcode = is_number_or_is_string(Barcode)
        print(Barcode)
        if StockMaximum == "":
            StockMaximum = 0

        Action = "A"
        
        if not models.TaxCategory.objects.filter(CompanyID=CompanyID, BranchID=BranchID, TaxName=VAT).exists():
            from api.v9.taxCategories.functions import get_auto_id
            TaxType = 1
            TaxID = get_auto_id(models.TaxCategory, BranchID, CompanyID)
            VatID = models.TaxCategory.objects.create(
                TaxID=TaxID,
                BranchID=BranchID,
                TaxName=VAT,
                TaxType=TaxType,
                PurchaseTax=VAT,
                SalesTax=VAT,
                Inclusive=False,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID
            )

            models.TaxCategory_Log.objects.create(
                BranchID=BranchID,
                TransactionID=TaxID,
                TaxName=VAT,
                TaxType=TaxType,
                PurchaseTax=VAT,
                SalesTax=VAT,
                Inclusive=False,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID
            )
        else:
            instances = models.TaxCategory.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, TaxName=VAT)

            VatID = models.TaxCategory.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, TaxName=VAT).first()

        if not models.Brand.objects.filter(BranchID=BranchID, CompanyID=CompanyID, BrandName=BrandName).exists():
            from api.v9.brands.functions import get_auto_id
            BrandID = get_auto_id(models.Brand, BranchID, CompanyID)
            Brand_id = models.Brand.objects.create(
                BrandID=BrandID,
                BranchID=BranchID,
                BrandName=BrandName,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
                CompanyID=CompanyID
            )

            models.Brand_Log.objects.create(
                BranchID=BranchID,
                TransactionID=BrandID,
                BrandName=BrandName,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
                CompanyID=CompanyID
            )
        else:
            Brand_id = models.Brand.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, BrandName=BrandName)

        if not models.ProductGroup.objects.filter(CompanyID=CompanyID, BranchID=BranchID, GroupName=GroupName).exists():
            from api.v9.productGroups.functions import get_auto_id
            ProductGroupID = get_auto_id(
                models.ProductGroup, BranchID, CompanyID)
            ProductGroup_id = models.ProductGroup.objects.create(
                ProductGroupID=ProductGroupID,
                BranchID=BranchID,
                GroupName=GroupName,
                CategoryID=1,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )

            models.ProductGroup_Log.objects.create(
                BranchID=BranchID,
                TransactionID=ProductGroupID,
                GroupName=GroupName,
                CategoryID=1,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )
        else:
            ProductGroup_id = models.ProductGroup.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, GroupName=GroupName)

        if not models.Unit.objects.filter(CompanyID=CompanyID, BranchID=BranchID, UnitName=UnitName).exists():
            from api.v9.units.functions import get_auto_id
            UnitID = get_auto_id(models.Unit, BranchID, CompanyID)
            Unit_id = models.Unit.objects.create(
                UnitID=UnitID,
                BranchID=BranchID,
                UnitName=UnitName,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
                CompanyID=CompanyID
            )

            models.Unit_Log.objects.create(
                BranchID=BranchID,
                TransactionID=UnitID,
                UnitName=UnitName,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
                CompanyID=CompanyID
            )
        else:
            Unit_id = models.Unit.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, UnitName=UnitName)
        if not models.Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductCode=str(ProductCode)).exists() and ProductCode:
            product_list.append({
                "ProductID":int(ProductID)+count,
                "ProductCode":ProductCode,
                "ProductName":ProductName,
                "DisplayName":ProductName,
                "Description":Description,
                "ProductGroupID":ProductGroup_id.ProductGroupID,
                "BrandID":Brand_id.BrandID,
                "VatID":VatID.TaxID,
                "StockMinimum":StockMinimum,
                "StockReOrder":StockReOrder,
                "StockMaximum":StockMaximum,
                "CreatedDate":today,
                "UpdatedDate":today,
                "CreatedUserID":CreatedUserID,
                "Action":Action,
            })
            product_list_log.append({
                "TransactionID": int(ProductID)+count,
                "ProductCode": ProductCode,
                "ProductName": ProductName,
                "DisplayName": ProductName,
                "Description": Description,
                "ProductGroupID": ProductGroup_id.ProductGroupID,
                "BrandID": Brand_id.BrandID,
                "VatID": VatID.TaxID,
                "StockMinimum": StockMinimum,
                "StockReOrder": StockReOrder,
                "StockMaximum": StockMaximum,
                "CreatedDate": today,
                "UpdatedDate": today,
                "CreatedUserID": CreatedUserID,
                "Action": Action,
            })

            price_list.append({
                "PriceListID": PriceListID+count,
                "UnitID": Unit_id.UnitID,
                "SalesPrice": SalesPrice,
                "SalesPrice1": SalesPrice1,
                "SalesPrice2": SalesPrice2,
                "SalesPrice3": SalesPrice3,
                "PurchasePrice": PurchasePrice,
                "Barcode": Barcode,
                "CreatedDate": today,
                "UpdatedDate": today,
                "MRP": SalesPrice,
                "Action": Action,
                "CreatedUserID": CreatedUserID,
                "DefaultUnit": True,
                "MultiFactor": 1,
                "AutoBarcode": AutoBarcode+count,
            })
            print("SalesPrice")
            print(type(SalesPrice))            
            print("SalesPrice1")
            print(type(SalesPrice1))            
            print("SalesPrice2")
            print(type(SalesPrice2))            
            print("SalesPrice3")
            print(type(SalesPrice3))            
            print("PurchasePrice")
            print(type(PurchasePrice))            
            price_list_log.append({
                "TransactionID": PriceListID+count,
                "UnitID": Unit_id.UnitID,
                "SalesPrice": SalesPrice,
                "SalesPrice1": SalesPrice1,
                "SalesPrice2": SalesPrice2,
                "SalesPrice3": SalesPrice3,
                "PurchasePrice": PurchasePrice,
                "Barcode": Barcode,
                "CreatedDate": today,
                "UpdatedDate": today,
                "MRP": SalesPrice,
                "Action": Action,
                "CreatedUserID": CreatedUserID,
                "DefaultUnit": True,
                "MultiFactor": 1,
                "AutoBarcode": AutoBarcode+count,
            })
            count+=1
        else:
            str_count += str(count+1)+str(",")
            message = 'ProductCode is exists in Sheet line number:' + \
                str(str_count)
            print(total, str_count)
        
        progress_recorder.set_progress(
            int(count), int(total), description="hello world")

    bulk_product = models.Product.objects.bulk_create([
        models.Product(
        **{key:value for key, value in i.items()},
        BranchID=BranchID,
        CompanyID=CompanyID,
        )
        for i in product_list
    ])
    bulk_product_log = models.Product_Log.objects.bulk_create([
        models.Product_Log(
        **{key:value for key, value in i.items()},
        BranchID=BranchID,
        CompanyID=CompanyID,
        )
        for i in product_list_log
    ])

    bulk_price_list = models.PriceList.objects.bulk_create([
        models.PriceList(
        **{key:value for key, value in i.items()},
        product=j,
        ProductID=j.ProductID,
        BranchID=BranchID,
        CompanyID=CompanyID,
        )
        for (i,j) in zip(price_list,bulk_product)
    ])
    bulk_price_list_log = models.PriceList_Log.objects.bulk_create([
        models.PriceList_Log(
        **{key:value for key, value in i.items()},
        ProductID=j.ProductID,
        BranchID=BranchID,
        CompanyID=CompanyID,
        )
        for (i,j) in zip(price_list_log,bulk_product)
    ])
    return message.format(total)


@shared_task(bind=True)
def import_multyUnit_task(self, input_excel, CompanyID, CreatedUserID, BranchID, Type):
    progress_recorder = ProgressRecorder(self)
    today = datetime.datetime.now()
    CompanyID = get_company(CompanyID)
    book = xlrd.open_workbook(input_excel)
    sheet = book.sheet_by_index(0)
    total = sheet.nrows
    dict_list = []
    keys = [str(sheet.cell(0, col_index).value)
            for col_index in range(sheet.ncols)]
    for row_index in range(1, sheet.nrows):
        d = {keys[col_index]: str(sheet.cell(row_index, col_index).value)
             for col_index in range(sheet.ncols)}
        dict_list.append(d)

    def is_number_tryexcept(item):
        """ Returns True is string is a number. """
        try:
            converted_float(item)
            return item
        except ValueError:
            item = 0
            return item

    def is_number_or_is_string(item):
        """ Returns True is string is a number. """
        try:
            item = int(converted_float(item))
            return item
        except ValueError:
            item = str(item)
            return item

    count = 0
    message = '{} Multy Unit Added Successfully!'
    str_count = ""
    for item in dict_list:
        count += 1

        PurchasePrice = item['PurchasePrice']
        PurchasePrice = is_number_tryexcept(PurchasePrice)
        SalesPrice = item['SalesPrice']

        SalesPrice = is_number_tryexcept(SalesPrice)

        try:
            ProductCode = item['ProductCode']
            # ProductCode = is_number_or_is_string(ProductCode)
        except:
            pass
        UnitName = item['Unit']

        Barcode = item['Barcode']
        try:
            MultiFactor = item['MultiFactor']
        except:
            MultiFactor = 1

        Barcode = is_number_or_is_string(Barcode)
        print(Barcode)

        Action = "A"

        if not models.Unit.objects.filter(CompanyID=CompanyID, BranchID=BranchID, UnitName=UnitName).exists():
            from api.v9.units.functions import get_auto_id
            UnitID = get_auto_id(models.Unit, BranchID, CompanyID)
            Unit_id = models.Unit.objects.create(
                UnitID=UnitID,
                BranchID=BranchID,
                UnitName=UnitName,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
                CompanyID=CompanyID
            )

            models.Unit_Log.objects.create(
                BranchID=BranchID,
                TransactionID=UnitID,
                UnitName=UnitName,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
                CompanyID=CompanyID
            )
        else:
            Unit_id = models.Unit.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, UnitName=UnitName)

        from api.v9.products.functions import get_auto_id
        ProductID = get_auto_id(models.Product, BranchID, CompanyID)

        print(Type, "THACHANKAIITOJD")
        is_barcode_exists = False
        if Barcode:
            if models.PriceList.objects.filter(CompanyID=CompanyID, Barcode=Barcode).exists():
                is_barcode_exists = True
        if not is_barcode_exists:
            if models.Product.objects.filter(CompanyID=CompanyID, ProductCode=str(ProductCode)).exists():
                instance = models.Product.objects.get(
                    CompanyID=CompanyID, ProductCode=str(ProductCode))
                PriceListID = get_auto_priceListid(
                    models.PriceList, BranchID, CompanyID)
                AutoBarcode = get_auto_AutoBarcode(
                    models.PriceList, BranchID, CompanyID)

                models.PriceList.objects.create(
                    PriceListID=PriceListID,
                    BranchID=BranchID,
                    ProductID=instance.ProductID,
                    product=instance,
                    UnitID=Unit_id.UnitID,
                    SalesPrice=SalesPrice,
                    PurchasePrice=PurchasePrice,
                    Barcode=Barcode,
                    CreatedDate=today,
                    UpdatedDate=today,
                    MRP=SalesPrice,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                    DefaultUnit=False,
                    MultiFactor=MultiFactor,
                    AutoBarcode=AutoBarcode
                )

                models.PriceList_Log.objects.create(
                    TransactionID=PriceListID,
                    BranchID=BranchID,
                    ProductID=instance.ProductID,
                    UnitID=Unit_id.UnitID,
                    SalesPrice=SalesPrice,
                    PurchasePrice=PurchasePrice,
                    Barcode=Barcode,
                    CreatedDate=today,
                    UpdatedDate=today,
                    MRP=SalesPrice,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                    DefaultUnit=False,
                    MultiFactor=MultiFactor,
                    AutoBarcode=AutoBarcode
                )

        else:
            str_count += str(count+1)+str(",")
            message = 'Barcode is exists in Sheet line number:' + \
                str(str_count)
            print(total, str_count)

        progress_recorder.set_progress(
            int(count), int(total), description="hello world")

    return message.format(total)
