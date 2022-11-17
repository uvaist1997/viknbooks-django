@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
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
                from api.v10.taxCategories.functions import get_auto_id
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
                from api.v10.brands.functions import get_auto_id
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
                from api.v10.productGroups.functions import get_auto_id
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
                from api.v10.units.functions import get_auto_id
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

            from api.v10.products.functions import get_auto_id
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


# Uvais
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def products_search_web(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    product_name = data['product_name']
    length = data['length']

    try:
        type = data['type']
    except:
        type = "any"

    try:
        Date = data['Date']
    except:
        Date = ""

    try:
        WarehouseID = data['WarehouseID']
    except:
        WarehouseID = 1

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        check_EnableProductBatchWise = False
        check_AllowNegativeStockSales = False
        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="AllowNegativeStockSales").exists():
            check_AllowNegativeStockSales = GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="AllowNegativeStockSales").SettingsValue
        if type == "Sales":
            if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Active=True, IsSales=True).exists():
                if length < 3:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, Active=True, ProductName__icontains=product_name, IsSales=True)[:10]
                else:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, Active=True, ProductName__icontains=product_name, IsSales=True)

                product_ids = []
                for p in instances:
                    Stock = 0
                    ProductID = p.ProductID
                    is_Service = p.is_Service
                    check_EnableProductBatchWise = False
                    if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
                        check_EnableProductBatchWise = GeneralSettings.objects.get(
                            CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
                    if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID).exists():
                            Batch_ins = Batch.objects.filter(
                                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID)
                            total_stockIN = 0
                            total_stockOUT = 0
                            for b in Batch_ins:
                                batch_pricelistID = b.PriceListID
                                batch_MultiFactor = PriceList.objects.get(
                                    CompanyID=CompanyID, PriceListID=batch_pricelistID).MultiFactor
                                total_stockIN += (converted_float(b.StockIn) /
                                                  converted_float(batch_MultiFactor))
                                total_stockOUT += (converted_float(b.StockOut) /
                                                   converted_float(batch_MultiFactor))

                            Stock = converted_float(total_stockIN) - \
                                converted_float(total_stockOUT)
                        elif StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID):
                            stock_ins = StockPosting.objects.filter(
                                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID)
                            total_stockIN = 0
                            total_stockOUT = 0
                            for s in stock_ins:
                                total_stockIN += converted_float(s.QtyIn)
                                total_stockOUT += converted_float(s.QtyOut)

                            Stock = converted_float(total_stockIN) - \
                                converted_float(total_stockOUT)
                    else:
                        if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID):
                            stock_ins = StockPosting.objects.filter(
                                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID)
                            total_stockIN = 0
                            total_stockOUT = 0
                            for s in stock_ins:
                                total_stockIN += converted_float(s.QtyIn)
                                total_stockOUT += converted_float(s.QtyOut)

                            Stock = converted_float(total_stockIN) - \
                                converted_float(total_stockOUT)
                    if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="ShowNegativeBatchInSales").exists():
                            check_ShowNegativeBatchInSales = GeneralSettings.objects.get(
                                CompanyID=CompanyID, SettingsType="ShowNegativeBatchInSales").SettingsValue
                            if check_ShowNegativeBatchInSales == "False" or check_ShowNegativeBatchInSales == False:
                                if Stock > 0:
                                    product_ids.append(ProductID)
                            else:
                                product_ids.append(ProductID)
                    # else:
                    if check_AllowNegativeStockSales == "False" or check_AllowNegativeStockSales == False:

                        if Stock > 0 or is_Service == True:
                            product_ids.append(ProductID)
                        # else:
                        #     product_ids.append(ProductID)
                    else:
                        product_ids.append(ProductID)

                # if check_AllowNegativeStockSales == "True" or check_AllowNegativeStockSales == True and check_EnableProductBatchWise == "False" or check_EnableProductBatchWise == False:
                #     instances12 = Product.objects.filter(
                #         CompanyID=CompanyID, BranchID=BranchID)
                #     for i in instances12:
                #         product_ids.append(i.ProductID)

                if product_ids:
                    if length < 3:
                        instances = Product.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, ProductID__in=product_ids)
                        for i in instances:
                            print(i.ProductName, 'ProductName1')
                    # elif:
                    #     instances = StockPosting.objects.filter(
                    #         CompanyID=CompanyID, BranchID=BranchID, ProductID__in=product_ids)
                    else:
                        instances = instances.filter(ProductID__in=product_ids)
                        for i in instances:
                            print(i.ProductName, 'ProductName2')
                    serialized = ProductSearchSerializer(instances, many=True, context={
                        "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding, "WarehouseID": WarehouseID})

                    # request , company, log_type, user, source, action, message, description
                    # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product', 'List', 'Product List Viewed successfully.', 'Product List Viewed successfully.')
                    response_data = {
                        "StatusCode": 6000,
                        "data": serialized.data
                    }

                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Product Not Found with Stock!!"
                    }

                    return Response(response_data, status=status.HTTP_200_OK)
            else:
                # request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Product',
                             'List', 'Product List Viewed Failed.', 'Product Not Found in this Branch!')
                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Not Found in this Branch!!"
                }

                return Response(response_data, status=status.HTTP_200_OK)
        elif type == "Purchase":

            if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Active=True, IsPurchase=True).exists():
                if length < 3:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, Active=True, ProductName__icontains=product_name, IsPurchase=True)[:10]

                else:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, Active=True, ProductName__icontains=product_name, IsPurchase=True)
                serialized = ProductSearchSerializer(instances, many=True, context={
                    "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding, "WarehouseID": WarehouseID})
                # if page_number and items_per_page:

                #     product_object = Product.objects.filter(
                #         CompanyID=CompanyID, BranchID=BranchID, Active=True)

                # request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product', 'List', 'Product List Viewed successfully.', 'Product List Viewed successfully.')
                response_data = {
                    "StatusCode": 6000,
                    "data": serialized.data
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Product',
                             'List', 'Product List Viewed Failed.', 'Product Not Found in this Branch!')
                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Not Found in this Branch!!"
                }

                return Response(response_data, status=status.HTTP_200_OK)
        elif type == "WorkOrder":
            if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, is_Service=False).exists():
                if length < 3:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductName__icontains=product_name, is_Service=False)[:10]
                else:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductName__icontains=product_name, is_Service=False)
                serialized = ProductSearchSerializer(instances, many=True, context={
                    "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding, "WarehouseID": WarehouseID})

                # request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product', 'List', 'Product List Viewed successfully.', 'Product List Viewed successfully.')
                response_data = {
                    "StatusCode": 6000,
                    "data": serialized.data
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                # request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Product',
                             'List', 'Product List Viewed Failed.', 'Product Not Found in this Branch!')
                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Not Found in this Branch!!"
                }

                return Response(response_data, status=status.HTTP_200_OK)
        else:

            if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, is_Service=False).exists():
                if length < 3:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductName__icontains=product_name, is_Service=False)[:10]
                else:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductName__icontains=product_name, is_Service=False)
                serialized = ProductSearchSerializer(instances, many=True, context={
                    "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding, "WarehouseID": WarehouseID, "type": type, "Date": Date})

                # request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product', 'List', 'Product List Viewed successfully.', 'Product List Viewed successfully.')
                response_data = {
                    "StatusCode": 6000,
                    "data": serialized.data
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                # request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Product',
                             'List', 'Product List Viewed Failed.', 'Product Not Found in this Branch!')
                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Not Found in this Branch!!"
                }

                return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@shared_task(bind=True)
def laast_import_product_task(self, input_excel, CompanyID, CreatedUserID, BranchID, Type):
    progress_recorder = ProgressRecorder(self)
    today = datetime.datetime.now()
    CompanyID = get_company(CompanyID)
    book = xlrd.open_workbook(input_excel)
    sheet = book.sheet_by_index(0)
    total = sheet.nrows
    dict_list = []
    print(Type, "THACHANKAIITOJD")
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
    for item in dict_list:
        count += 1

        ProductName = item['ProductName']
        Description = item['Description']
        PurchasePrice = item['PurchasePrice']
        PurchasePrice = is_number_tryexcept(PurchasePrice)
        SalesPrice = item['SalesPrice']

        try:
            SalesPrice1 = item['SalesPrice1']
        except:
            SalesPrice1 = 0
        try:
            SalesPrice2 = item['SalesPrice2']
        except:
            SalesPrice2 = 0
        try:
            SalesPrice3 = item['SalesPrice3']
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
            from api.v10.taxCategories.functions import get_auto_id
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
            from api.v10.brands.functions import get_auto_id
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
            from api.v10.productGroups.functions import get_auto_id
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
            from api.v10.units.functions import get_auto_id
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

        from api.v10.products.functions import get_auto_id
        ProductID = get_auto_id(models.Product, BranchID, CompanyID)
        # if ProductCode:
        #     ProductCode = ProductCode
        # else:
        #     ProductCode = get_ProductCode(Product, BranchID,CompanyID)
        # is_nameExist = False
        # ProductNameLow = ProductName.lower()
        # products = models.Product.objects.filter(
        #     CompanyID=CompanyID, BranchID=BranchID)
        # for product in products:
        #     product_name = product.ProductName

        #     productName = product_name.lower()

        #     if ProductNameLow == productName:
        #         is_nameExist = True

        if not models.Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductCode=str(ProductCode)).exists():
            # if not models.Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductName__iexact=ProductName).exists():
            # print(str(ProductCode)+str("***")+str(ProductName), "####")
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
                SalesPrice1=SalesPrice1,
                SalesPrice2=SalesPrice2,
                SalesPrice3=SalesPrice3,
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
                SalesPrice1=SalesPrice1,
                SalesPrice2=SalesPrice2,
                SalesPrice3=SalesPrice3,
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
        else:
            # instance = models.Product.objects.get(
            #     CompanyID=CompanyID, BranchID=BranchID, ProductCode=str(ProductCode))
            # PriceListID = get_auto_priceListid(
            #     models.PriceList, BranchID, CompanyID)
            # AutoBarcode = get_auto_AutoBarcode(
            #     models.PriceList, BranchID, CompanyID)

            # models.PriceList.objects.create(
            #     PriceListID=PriceListID,
            #     BranchID=BranchID,
            #     ProductID=instance.ProductID,
            #     product=instance,
            #     UnitID=Unit_id.UnitID,
            #     SalesPrice=SalesPrice,
            #     PurchasePrice=PurchasePrice,
            #     Barcode=Barcode,
            #     CreatedDate=today,
            #     UpdatedDate=today,
            #     MRP=SalesPrice,
            #     Action=Action,
            #     CreatedUserID=CreatedUserID,
            #     CompanyID=CompanyID,
            #     DefaultUnit=False,
            #     MultiFactor=MultiFactor,
            #     AutoBarcode=AutoBarcode
            # )

            # models.PriceList_Log.objects.create(
            #     TransactionID=PriceListID,
            #     BranchID=BranchID,
            #     ProductID=instance.ProductID,
            #     UnitID=Unit_id.UnitID,
            #     SalesPrice=SalesPrice,
            #     PurchasePrice=PurchasePrice,
            #     Barcode=Barcode,
            #     CreatedDate=today,
            #     UpdatedDate=today,
            #     MRP=SalesPrice,
            #     Action=Action,
            #     CreatedUserID=CreatedUserID,
            #     CompanyID=CompanyID,
            #     DefaultUnit=False,
            #     MultiFactor=MultiFactor,
            #     AutoBarcode=AutoBarcode
            # )

            # else:
            str_count += str(count+1)+str(",")
            message = 'ProductCode is exists in Sheet line number:' + \
                str(str_count)
            print(total, str_count)
        progress_recorder.set_progress(
            int(count), int(total), description="hello world")

    return message.format(total)
