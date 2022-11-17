@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def upload_product(request):
    today = datetime.datetime.now()

    data = request.data
    serializer = UploadSerializer(data=request.data)
    if serializer.is_valid():
        CompanyID = data['CompanyID']
        CreatedUserID = data['CreatedUserID']
        input_excel = data['file']
        CompanyID = get_company(CompanyID)
        BranchID = 1
        book = xlrd.open_workbook(file_contents=input_excel.read())
        sheet = book.sheet_by_index(0)

        dict_list = []
        keys = [str(sheet.cell(0, col_index).value)
                for col_index in range(sheet.ncols)]
        for row_index in range(1, sheet.nrows):
            d = {keys[col_index]: str(sheet.cell(row_index, col_index).value)
                 for col_index in range(sheet.ncols)}
            dict_list.append(d)

        is_ok = True
        message = ''
        row_count = 2

        sheet_counter = 1

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

            if not TaxCategory.objects.filter(CompanyID=CompanyID, BranchID=BranchID, TaxName=VAT).exists():
                from api.v5.taxCategories.functions import get_auto_id
                TaxType = 1
                TaxID = get_auto_id(TaxCategory, BranchID, CompanyID)
                VatID = TaxCategory.objects.create(
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

                TaxCategory_Log.objects.create(
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
                VatID = TaxCategory.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, TaxName=VAT)

            if not Brand.objects.filter(BranchID=BranchID, CompanyID=CompanyID, BrandName=BrandName).exists():
                from api.v5.brands.functions import get_auto_id
                BrandID = get_auto_id(Brand, BranchID, CompanyID)
                Brand_id = Brand.objects.create(
                    BrandID=BrandID,
                    BranchID=BranchID,
                    BrandName=BrandName,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    Action=Action,
                    CompanyID=CompanyID
                )

                Brand_Log.objects.create(
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
                Brand_id = Brand.objects.get(
                    BranchID=BranchID, CompanyID=CompanyID, BrandName=BrandName)

            if not ProductGroup.objects.filter(CompanyID=CompanyID, BranchID=BranchID, GroupName=GroupName).exists():
                from api.v5.productGroups.functions import get_auto_id
                ProductGroupID = get_auto_id(ProductGroup, BranchID, CompanyID)
                ProductGroup_id = ProductGroup.objects.create(
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

                ProductGroup_Log.objects.create(
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
                ProductGroup_id = ProductGroup.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, GroupName=GroupName)

            if not Unit.objects.filter(CompanyID=CompanyID, BranchID=BranchID, UnitName=UnitName).exists():
                from api.v5.units.functions import get_auto_id
                UnitID = get_auto_id(Unit, BranchID, CompanyID)
                Unit_id = Unit.objects.create(
                    UnitID=UnitID,
                    BranchID=BranchID,
                    UnitName=UnitName,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    Action=Action,
                    CompanyID=CompanyID
                )

                Unit_Log.objects.create(
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
                Unit_id = Unit.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, UnitName=UnitName)

            from api.v5.products.functions import get_auto_id
            ProductID = get_auto_id(Product, BranchID, CompanyID)
            # if ProductCode:
            #     ProductCode = ProductCode
            # else:
            #     ProductCode = get_ProductCode(Product, BranchID,CompanyID)
            is_nameExist = False
            ProductNameLow = ProductName.lower()
            products = Product.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
            for product in products:
                product_name = product.ProductName

                productName = product_name.lower()

                if ProductNameLow == productName:
                    is_nameExist = True

            if not is_nameExist:
                instance = Product.objects.create(
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

                Product_Log.objects.create(
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
                    PriceList, BranchID, CompanyID)
                AutoBarcode = get_auto_AutoBarcode(
                    PriceList, BranchID, CompanyID)

                PriceList.objects.create(
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

                PriceList_Log.objects.create(
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

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product',
                     'Uploaded', 'Product Uploaded successfully.', 'Product Uploaded successfully.')
        response_data = {
            "StatusCode": 6000,
            "message": "Product Uploaded Successfully!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serializer._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)
