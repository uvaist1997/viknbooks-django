import string
from django.contrib.auth.models import User
from main.functions import get_company
from api.v3.products.functions import get_auto_id, get_auto_priceListid, get_ProductCode, get_auto_AutoBarcode, get_auto_BatchNo, get_auto_AutoBatchCode
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
def import_product_task(self, input_excel, CompanyID, CreatedUserID, BranchID):
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
            float(item)
            return item
        except ValueError:
            item = 0
            return item

    def is_number_or_is_string(item):
        """ Returns True is string is a number. """
        try:
            item = int(float(item))
            return item
        except ValueError:
            item = str(item)
            return item

    count = 0
    for item in dict_list:
        count += 1
        print(count)

        ProductName = item['ProductName']
        Description = item['Description']
        PurchasePrice = item['PurchasePrice']
        PurchasePrice = is_number_tryexcept(PurchasePrice)
        SalesPrice = item['SalesPrice']
        SalesPrice = is_number_tryexcept(SalesPrice)
        GroupName = item['GroupName']
        UnitName = item['Unit']
        BrandName = item['BrandName']
        try:
            ProductCode = item['ProductCode']
            ProductCode = is_number_or_is_string(ProductCode)
        except:
            pass
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
        Barcode = is_number_or_is_string(Barcode)
        if StockMaximum == "":
            StockMaximum = 0

        Action = "A"

        if not models.TaxCategory.objects.filter(CompanyID=CompanyID, BranchID=BranchID, TaxName=VAT).exists():
            from api.v3.taxCategories.functions import get_auto_id
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
            VatID = models.TaxCategory.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, TaxName=VAT)

        if not models.Brand.objects.filter(BranchID=BranchID, CompanyID=CompanyID, BrandName=BrandName).exists():
            from api.v3.brands.functions import get_auto_id
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
            from api.v3.productGroups.functions import get_auto_id
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
            from api.v3.units.functions import get_auto_id
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

        from api.v3.products.functions import get_auto_id
        ProductID = get_auto_id(models.Product, BranchID, CompanyID)
        # if ProductCode:
        #     ProductCode = ProductCode
        # else:
        #     ProductCode = get_ProductCode(Product, BranchID,CompanyID)
        is_nameExist = False
        ProductNameLow = ProductName.lower()
        products = models.Product.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID)
        for product in products:
            product_name = product.ProductName

            productName = product_name.lower()

            if ProductNameLow == productName:
                is_nameExist = True

        if not is_nameExist:
            instance = models.Product.objects.create(
                ProductID=ProductID,
                BranchID=BranchID,
                ProductCode=ProductCode,
                ProductName=ProductName,
                DisplayName=ProductName,
                Description=Description,
                ProductGroupID=ProductGroup_id.ProductGroupID,
                BrandID=Brand_id.BrandID,
                VatID=VatID.TaxID,
                StockMinimum=StockMinimum,
                StockReOrder=StockReOrder,
                StockMaximum=StockMaximum,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
                CompanyID=CompanyID,
            )

            models.Product_Log.objects.create(
                TransactionID=ProductID,
                BranchID=BranchID,
                ProductCode=ProductCode,
                ProductName=ProductName,
                DisplayName=ProductName,
                Description=Description,
                ProductGroupID=ProductGroup_id.ProductGroupID,
                BrandID=Brand_id.BrandID,
                VatID=VatID.TaxID,
                StockMinimum=StockMinimum,
                StockReOrder=StockReOrder,
                StockMaximum=StockMaximum,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
                CompanyID=CompanyID,
            )

            PriceListID = get_auto_priceListid(
                models.PriceList, BranchID, CompanyID)
            AutoBarcode = get_auto_AutoBarcode(
                models.PriceList, BranchID, CompanyID)

            models.PriceList.objects.create(
                PriceListID=PriceListID,
                BranchID=BranchID,
                ProductID=ProductID,
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
                DefaultUnit=True,
                MultiFactor=1,
                AutoBarcode=AutoBarcode
            )

            models.PriceList_Log.objects.create(
                TransactionID=PriceListID,
                BranchID=BranchID,
                ProductID=ProductID,
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
                DefaultUnit=True,
                MultiFactor=1,
                AutoBarcode=AutoBarcode
            )
        progress_recorder.set_progress(
            int(count), int(total), description="hello world")

    return '{} products created successfully!'.format(total)
