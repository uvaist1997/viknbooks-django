import json
import os
import sys
from django.contrib.auth import authenticate
from api.v10.accountLedgers.functions import get_LedgerCode
from brands.models import Route, AccountLedger, Branch, Branch_Log, BranchSettings, Brand, CompanySettings, Country, GeneralSettings, ProductCategory, ProductGroup, State, TaxCategory, Unit, Warehouse
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes,authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from api.v10.branchs.serializers import BranchSerializer, BranchRestSerializer, BranchSettingsSerializer
from api.v10.branchs.functions import create_ledger_instance, create_or_update_branch_settings, generate_serializer_errors, get_branch_settings, get_ledger_instance, get_pk_ledger_instance
from rest_framework import status
from api.v10.branchs.functions import get_auto_id
import datetime
from api.v10.warehouses.functions import get_auto_id as wareHouse_auto_id
from main.functions import get_company, activity_log, delete_model_datas
from brands import models as table
from django.db import transaction, IntegrityError
from api.v10.taxCategories.functions import get_auto_id as tax_auto_id
from api.v10.units.functions import get_auto_id as unit_auto_id
from api.v10.productGroups.functions import get_auto_id as productGroup_auto_id
from api.v10.productCategories.functions import get_auto_id as productCategory_auto_id
from api.v10.brands.functions import get_auto_id as brand_auto_id
from api.v10.routes.functions import get_auto_id as route_auto_id


@api_view(['POST'])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def create_branch(request):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            CreatedUserID = data['CreatedUserID']
            try:
                NoOfBrances = data['NoOfBrances']
            except:
                NoOfBrances = data['NoOfBrances']

            today = datetime.datetime.now()
            serialized = BranchSerializer(data=request.data)
            if serialized.is_valid():

                BranchName = serialized.data['BranchName']
                DisplayName = serialized.data['DisplayName']
                regional_office_pk = serialized.data['regional_office']
                Phone = serialized.data['Phone']
                Email = serialized.data['Email']
                Building = serialized.data['Building']
                PostalCode = serialized.data['PostalCode']
                City = serialized.data['City']
                state_pk = serialized.data['state']
                country_pk = serialized.data['country']
                GSTNumber = serialized.data['GSTNumber']
                VATNumber = serialized.data['VATNumber']
                is_gst = serialized.data['is_gst']
                is_vat = serialized.data['is_vat']
                is_regional_office = serialized.data['is_regional_office']

                if not Branch.objects.filter(CompanyID=CompanyID, BranchName__iexact=BranchName):
                    branch_len = Branch.objects.filter(
                        CompanyID=CompanyID).count()
                    print(NoOfBrances)
                    print(branch_len)
                    if not NoOfBrances <= branch_len:
                        if state_pk:
                            state = State.objects.get(pk=state_pk)

                        if country_pk:
                            country = Country.objects.get(pk=country_pk)

                        regional_office = None
                        if regional_office_pk:
                            regional_office = Branch.objects.get(
                                pk=regional_office_pk)

                        Action = "A"

                        BranchID = get_auto_id(Branch, CompanyID)

                        branch_instance = Branch.objects.create(
                            BranchID=BranchID,
                            BranchName=BranchName,
                            DisplayName=DisplayName,
                            regional_office=regional_office,
                            Phone=Phone,
                            Email=Email,
                            Building=Building,
                            PostalCode=PostalCode,
                            City=City,
                            state=state,
                            country=country,
                            GSTNumber=GSTNumber,
                            VATNumber=VATNumber,
                            is_gst=is_gst,
                            is_vat=is_vat,
                            is_regional_office=is_regional_office,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )
                        Branch_Log.objects.create(
                            TransactionID=BranchID,
                            BranchName=BranchName,
                            DisplayName=DisplayName,
                            regional_office=regional_office,
                            Phone=Phone,
                            Email=Email,
                            Building=Building,
                            City=City,
                            state=state,
                            country=country,
                            GSTNumber=GSTNumber,
                            VATNumber=VATNumber,
                            is_gst=is_gst,
                            is_vat=is_vat,
                            is_regional_office=is_regional_office,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        # ================creating Ledgers for branches starts here================
                        integrated_gst_on_sales_ins = get_ledger_instance(
                            7, 1, CompanyID)
                        branch_instance.integrated_gst_on_sales = integrated_gst_on_sales_ins

                        central_gst_on_sales_ins = get_ledger_instance(
                            3, 1, CompanyID)
                        branch_instance.central_gst_on_sales = central_gst_on_sales_ins

                        state_gst_on_sales_ins = get_ledger_instance(
                            10, 1, CompanyID)
                        branch_instance.state_gst_on_sales = state_gst_on_sales_ins

                        central_gst_on_expense_ins = get_ledger_instance(
                            35, 1, CompanyID)
                        branch_instance.central_gst_on_expense = central_gst_on_expense_ins

                        central_gst_on_purchase_ins = get_ledger_instance(
                            36, 1, CompanyID)
                        branch_instance.central_gst_on_purchase = central_gst_on_purchase_ins

                        state_gst_on_purchase_ins = get_ledger_instance(
                            42, 1, CompanyID)
                        branch_instance.state_gst_on_purchase = state_gst_on_purchase_ins

                        integrated_gst_on_purchase_ins = get_ledger_instance(
                            39, 1, CompanyID)
                        branch_instance.integrated_gst_on_purchase = integrated_gst_on_purchase_ins

                        state_gst_on_payment_ins = get_ledger_instance(
                            41, 1, CompanyID)
                        branch_instance.state_gst_on_payment = state_gst_on_payment_ins

                        vat_on_sales_ins = get_ledger_instance(
                            55, 1, CompanyID)
                        branch_instance.vat_on_sales = vat_on_sales_ins

                        vat_on_purchase_ins = get_ledger_instance(
                            56, 1, CompanyID)
                        branch_instance.vat_on_purchase = vat_on_purchase_ins

                        vat_on_expense_ins = get_ledger_instance(
                            24, 1, CompanyID)
                        branch_instance.vat_on_expense = vat_on_expense_ins

                        round_off_sales_ins = get_ledger_instance(
                            78, 1, CompanyID)
                        branch_instance.round_off_sales = round_off_sales_ins

                        discount_on_sales_ins = get_ledger_instance(
                            74, 1, CompanyID)
                        branch_instance.discount_on_sales = discount_on_sales_ins

                        discount_on_purchase_ins = get_ledger_instance(
                            83, 1, CompanyID)
                        branch_instance.discount_on_purchase = discount_on_purchase_ins

                        discount_on_payment_ins = get_ledger_instance(
                            82, 1, CompanyID)
                        branch_instance.discount_on_payment = discount_on_payment_ins

                        discount_on_receipt_ins = get_ledger_instance(
                            72, 1, CompanyID)
                        branch_instance.discount_on_receipt = discount_on_receipt_ins

                        discount_on_loyalty_ins = get_ledger_instance(
                            73, 1, CompanyID)
                        branch_instance.discount_on_loyalty = discount_on_loyalty_ins

                        round_off_purchase_ins = get_ledger_instance(
                            77, 1, CompanyID)
                        branch_instance.round_off_purchase = round_off_purchase_ins
                        branch_instance.save()

                        # ================creating defult General Settings starts here================
                        THIS_FOLDER = os.path.dirname(
                            os.path.abspath(__file__))
                        path = os.path.join(
                            THIS_FOLDER, '../companySettings/company_fixtures/general_settings.json')

                        # path = 'main/fixtures/general_settings.json'
                        with open(path, 'r+') as json_file:
                            json_data = json_file.read()
                            dic = json.loads(json_data)
                            # name = dic[0]['fields']['GroupName']
                            for i in dic:
                                if i['model'] == "brands.GeneralSettings":
                                    GeneralSettingsID = i['fields']['GeneralSettingsID']
                                    GroupName = i['fields']['GroupName']
                                    SettingsType = i['fields']['SettingsType']
                                    SettingsValue = i['fields']['SettingsValue']
                                    Action = i['fields']['Action']

                                    GeneralSettings.objects.create(
                                        CompanyID=CompanyID,
                                        GeneralSettingsID=GeneralSettingsID,
                                        BranchID=BranchID,
                                        GroupName=GroupName,
                                        SettingsType=SettingsType,
                                        SettingsValue=SettingsValue,
                                        Action=Action,
                                        CreatedDate=today,
                                        UpdatedDate=today,
                                        CreatedUserID=CreatedUserID,
                                    )

                        if is_gst:
                            GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="GST").update(
                                SettingsValue="true", UpdatedDate=today, CreatedUserID=CreatedUserID, Action="A")
                            GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="VAT").update(
                                SettingsValue="false", UpdatedDate=today, CreatedUserID=CreatedUserID, Action="A")
                        else:
                            GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="VAT").update(
                                SettingsValue="true", UpdatedDate=today, CreatedUserID=CreatedUserID, Action="A")
                            GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="GST").update(
                                SettingsValue="false", UpdatedDate=today, CreatedUserID=CreatedUserID, Action="A")

                        # ================creating defult TaxCategory starts here================
                        warehouse_id = wareHouse_auto_id(
                            Warehouse, BranchID, CompanyID)
                        Warehouse.objects.create(
                            CompanyID=CompanyID,
                            WarehouseID=warehouse_id,
                            BranchID=BranchID,
                            WarehouseName='Primary Warehouse',
                            Notes="Default Note",
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            Action="A",
                        )
                        check_productsForAllBranches = False
                        if BranchSettings.objects.filter(CompanyID=CompanyID, SettingsType="productsForAllBranches").exists():
                            check_productsForAllBranches = BranchSettings.objects.get(
                                CompanyID=CompanyID, SettingsType="productsForAllBranches").SettingsValue

                        if check_productsForAllBranches == False or check_productsForAllBranches == "False":
                            THIS_FOLDER = os.path.dirname(
                                os.path.abspath(__file__))
                            path = os.path.join(
                                THIS_FOLDER, '../companySettings/company_fixtures/tax_categories.json')

                            # path = 'main/fixtures/tax_categories.json'
                            with open(path, 'r+') as json_file:
                                json_data = json_file.read()
                                dic = json.loads(json_data)
                                for i in dic:
                                    if i['model'] == "brands.TaxCategory":
                                        TaxID = tax_auto_id(
                                            table.TaxCategory, BranchID, CompanyID)
                                        # TaxID = i['fields']['TaxID']
                                        TaxName = i['fields']['TaxName']
                                        TaxTypes = i['fields']['TaxType']
                                        PurchaseTax = i['fields']['PurchaseTax']
                                        SalesTax = i['fields']['SalesTax']
                                        Inclusive = i['fields']['Inclusive']
                                        Action = i['fields']['Action']

                                        TaxCategory.objects.create(
                                            CompanyID=CompanyID,
                                            TaxID=TaxID,
                                            BranchID=BranchID,
                                            TaxName=TaxName,
                                            TaxType=TaxTypes,
                                            PurchaseTax=PurchaseTax,
                                            SalesTax=SalesTax,
                                            Inclusive=Inclusive,
                                            CreatedUserID=CreatedUserID,
                                            CreatedDate=today,
                                            Action=Action,
                                        )
                            # ================creating defult TaxCategory ends here================
                            # ================creating defult Unit starts here================
                            THIS_FOLDER = os.path.dirname(
                                os.path.abspath(__file__))
                            path = os.path.join(
                                THIS_FOLDER, '../companySettings/company_fixtures/unit.json')

                            # path = 'main/fixtures/banks.json'
                            with open(path, 'r+') as json_file:
                                json_data = json_file.read()
                                dic = json.loads(json_data)
                                # name = dic[0]['fields']['GroupName']
                                # CompanyID = get_company(CompanyID)
                                for i in dic:
                                    if i['model'] == "brands.Unit":
                                        UnitID = unit_auto_id(
                                            Unit, BranchID, CompanyID)
                                        UnitName = i['fields']['UnitName']
                                        Notes = i['fields']['Notes']
                                        Unit.objects.create(
                                            CompanyID=CompanyID,
                                            UnitID=UnitID,
                                            BranchID=BranchID,
                                            UnitName=UnitName,
                                            Notes=Notes,
                                            CreatedUserID=CreatedUserID,
                                            CreatedDate=today,
                                        )
                            # ================creating defult Unit ends here================
                            # ================creating defult Product Group starts here================
                            THIS_FOLDER = os.path.dirname(
                                os.path.abspath(__file__))
                            path = os.path.join(
                                THIS_FOLDER, '../companySettings/company_fixtures/product_group.json')

                            # path = 'main/fixtures/product_group.json'
                            with open(path, 'r+') as json_file:
                                json_data = json_file.read()
                                dic = json.loads(json_data)
                                # name = dic[0]['fields']['GroupName']
                                # CompanyID = get_company(CompanyID)
                                for i in dic:
                                    if i['model'] == "brands.ProductGroup":
                                        # ProductGroupID = i['fields']['ProductGroupID']
                                        ProductGroupID = productGroup_auto_id(
                                            ProductGroup, BranchID, CompanyID)
                                        GroupName = i['fields']['GroupName']
                                        CategoryID = i['fields']['CategoryID']
                                        Notes = i['fields']['Notes']
                                        Action = i['fields']['Action']

                                        ProductGroup.objects.create(
                                            CompanyID=CompanyID,
                                            ProductGroupID=ProductGroupID,
                                            BranchID=BranchID,
                                            GroupName=GroupName,
                                            CategoryID=CategoryID,
                                            Notes=Notes,
                                            CreatedUserID=CreatedUserID,
                                            CreatedDate=today,
                                            Action=Action,
                                        )
                                    # ================creating defult Product Group ends here================
                                        # ================creating defult Price Category starts here================
                            THIS_FOLDER = os.path.dirname(
                                os.path.abspath(__file__))
                            path = os.path.join(
                                THIS_FOLDER, '../companySettings/company_fixtures/product_category.json')

                            # path = 'main/fixtures/product_category.json'
                            with open(path, 'r+') as json_file:
                                json_data = json_file.read()
                                dic = json.loads(json_data)
                                # name = dic[0]['fields']['GroupName']
                                # CompanyID = get_company(CompanyID)
                                for i in dic:
                                    if i['model'] == "brands.ProductCategory":
                                        # ProductCategoryID = i['fields']['ProductCategoryID']
                                        ProductCategoryID = productCategory_auto_id(
                                            ProductCategory, BranchID, CompanyID)
                                        CategoryName = i['fields']['CategoryName']
                                        Notes = i['fields']['Notes']
                                        CreatedUserID = i['fields']['CreatedUserID']
                                        Action = i['fields']['Action']

                                        ProductCategory.objects.create(
                                            CompanyID=CompanyID,
                                            ProductCategoryID=ProductCategoryID,
                                            BranchID=BranchID,
                                            CategoryName=CategoryName,
                                            Notes=Notes,
                                            CreatedUserID=CreatedUserID,
                                            CreatedDate=today,
                                            Action=Action,
                                        )
                            BrandID = brand_auto_id(Brand, BranchID, CompanyID)
                            Brand.objects.create(
                                CompanyID=CompanyID,
                                BrandID=BrandID,
                                BranchID=BranchID,
                                BrandName='Primary Brand',
                                Notes="Default Note",
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                Action="A",
                            )

                            RouteID = route_auto_id(Route, BranchID, CompanyID)
                            Route.objects.create(
                                RouteID=RouteID,
                                BranchID=BranchID,
                                RouteName="Primary Route",
                                Notes=Notes,
                                Action="A",
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )
                            # ================creating defult Price Category ends here================

                        # ================creating defult General Settings ends here================

                        data = {"BranchID": BranchID}
                        data.update(serialized.data)
                        response_data = {
                            "StatusCode": 6000,
                            "data": data
                        }

                        return Response(response_data, status=status.HTTP_200_OK)
                    else:
                        response_data = {
                            "StatusCode": 6001,
                            "message": "You can't add more branches!Your Limit got Over.please Contact Admin"
                        }

                        return Response(response_data, status=status.HTTP_200_OK)
                else:
                    activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Warehouse',
                                 'Create', 'Branch created Failed.', 'WareHouse Name Already Exist')
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Branch name already exists."
                    }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Branch', 'Create',
                             'Branch created failed.', generate_serializer_errors(serialized._errors))
                response_data = {
                    "StatusCode": 6001,
                    "message": generate_serializer_errors(serialized._errors)
                }

                return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("======================exception test")
        print(exc_type, fname, exc_tb.tb_lineno)
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        message = "some error occured..please try again"
        response_data = {
            "StatusCode": 6001,
            "message": message,
            "err_descrb": err_descrb
        }

        # transaction.rollback()
        # transaction.set_rollback(True)
        # transaction.set_rollback(False)
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Branch',
                     'Create', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def edit_branch(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = BranchSerializer(data=request.data)
    instance = None
    if Branch.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = Branch.objects.get(pk=pk, CompanyID=CompanyID)

    if instance:
        BranchID = instance.BranchID
        CreatedUserID = instance.CreatedUserID

        Action = "M"

        vat_on_sales = get_pk_ledger_instance(data['vat_on_sales'], CompanyID)
        vat_on_purchase = get_pk_ledger_instance(
            data['vat_on_purchase'], CompanyID)
        vat_on_expense = get_pk_ledger_instance(
            data['vat_on_expense'], CompanyID)
        central_gst_on_sales = get_pk_ledger_instance(
            data['central_gst_on_sales'], CompanyID)
        state_gst_on_sales = get_pk_ledger_instance(
            data['state_gst_on_sales'], CompanyID)
        integrated_gst_on_sales = get_pk_ledger_instance(
            data['integrated_gst_on_sales'], CompanyID)
        central_gst_on_expense = get_pk_ledger_instance(
            data['central_gst_on_expense'], CompanyID)
        central_gst_on_purchase = get_pk_ledger_instance(
            data['central_gst_on_purchase'], CompanyID)
        state_gst_on_purchase = get_pk_ledger_instance(
            data['state_gst_on_purchase'], CompanyID)
        integrated_gst_on_purchase = get_pk_ledger_instance(
            data['integrated_gst_on_purchase'], CompanyID)
        state_gst_on_payment = get_pk_ledger_instance(
            data['state_gst_on_payment'], CompanyID)
        round_off_sales = get_pk_ledger_instance(
            data['round_off_sales'], CompanyID)
        discount_on_sales = get_pk_ledger_instance(
            data['discount_on_sales'], CompanyID)
        discount_on_purchase = get_pk_ledger_instance(
            data['discount_on_purchase'], CompanyID)
        discount_on_payment = get_pk_ledger_instance(
            data['discount_on_payment'], CompanyID)
        discount_on_receipt = get_pk_ledger_instance(
            data['discount_on_receipt'], CompanyID)
        discount_on_loyalty = get_pk_ledger_instance(
            data['discount_on_loyalty'], CompanyID)
        round_off_purchase = get_pk_ledger_instance(
            data['round_off_purchase'], CompanyID)

        if serialized.is_valid():
            BranchName = serialized.data['BranchName']
            DisplayName = serialized.data['DisplayName']
            regional_office_pk = serialized.data['regional_office']
            Phone = serialized.data['Phone']
            Email = serialized.data['Email']
            Building = serialized.data['Building']
            PostalCode = serialized.data['PostalCode']
            City = serialized.data['City']
            state_pk = serialized.data['state']
            country_pk = serialized.data['country']
            GSTNumber = serialized.data['GSTNumber']
            VATNumber = serialized.data['VATNumber']
            is_gst = serialized.data['is_gst']
            is_vat = serialized.data['is_vat']
            is_regional_office = serialized.data['is_regional_office']

            RegionalOffice = get_pk_ledger_instance(
                regional_office_pk, CompanyID)

            if state_pk:
                state = State.objects.get(pk=state_pk)
            print(state)
            if country_pk:
                country = Country.objects.get(pk=country_pk)

            # serialized.update(instance, serialized.data)
            Branch_Log.objects.create(
                TransactionID=BranchID,
                BranchName=BranchName,
                DisplayName=DisplayName,
                regional_office=RegionalOffice,
                Phone=Phone,
                Email=Email,
                Building=Building,
                PostalCode=PostalCode,
                City=City,
                state=state,
                country=country,
                GSTNumber=GSTNumber,
                VATNumber=VATNumber,
                is_gst=is_gst,
                is_vat=is_vat,
                is_regional_office=is_regional_office,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,

                vat_on_sales=vat_on_sales,
                vat_on_purchase=vat_on_purchase,
                vat_on_expense=vat_on_expense,
                central_gst_on_sales=central_gst_on_sales,
                state_gst_on_sales=state_gst_on_sales,
                integrated_gst_on_sales=integrated_gst_on_sales,
                central_gst_on_expense=central_gst_on_expense,
                central_gst_on_purchase=central_gst_on_purchase,
                state_gst_on_purchase=state_gst_on_purchase,
                integrated_gst_on_purchase=integrated_gst_on_purchase,
                state_gst_on_payment=state_gst_on_payment,
                round_off_sales=round_off_sales,
                discount_on_sales=discount_on_sales,
                discount_on_purchase=discount_on_purchase,
                discount_on_payment=discount_on_payment,
                discount_on_receipt=discount_on_receipt,
                discount_on_loyalty=discount_on_loyalty,
                round_off_purchase=round_off_purchase,
            )
            instance.Action = Action
            instance.CreatedUserID = CreatedUserID
            instance.UpdatedDate = today

            instance.BranchName = BranchName
            instance.DisplayName = DisplayName
            instance.regional_office = RegionalOffice
            instance.Phone = Phone
            instance.Email = Email
            instance.Building = Building
            instance.PostalCode = PostalCode
            instance.City = City
            instance.GSTNumber = GSTNumber
            instance.VATNumber = VATNumber
            instance.is_gst = is_gst
            instance.is_vat = is_vat
            instance.is_regional_office = is_regional_office
            instance.state = state

            instance.vat_on_sales = get_pk_ledger_instance(
                data['vat_on_sales'], CompanyID)
            instance.vat_on_purchase = get_pk_ledger_instance(
                data['vat_on_purchase'], CompanyID)
            instance.vat_on_expense = get_pk_ledger_instance(
                data['vat_on_expense'], CompanyID)
            instance.central_gst_on_sales = get_pk_ledger_instance(
                data['central_gst_on_sales'], CompanyID)
            instance.state_gst_on_sales = get_pk_ledger_instance(
                data['state_gst_on_sales'], CompanyID)
            instance.integrated_gst_on_sales = get_pk_ledger_instance(
                data['integrated_gst_on_sales'], CompanyID)
            instance.central_gst_on_expense = get_pk_ledger_instance(
                data['central_gst_on_expense'], CompanyID)
            instance.central_gst_on_purchase = get_pk_ledger_instance(
                data['central_gst_on_purchase'], CompanyID)
            instance.state_gst_on_purchase = get_pk_ledger_instance(
                data['state_gst_on_purchase'], CompanyID)
            instance.integrated_gst_on_purchase = get_pk_ledger_instance(
                data['integrated_gst_on_purchase'], CompanyID)
            instance.state_gst_on_payment = get_pk_ledger_instance(
                data['state_gst_on_payment'], CompanyID)
            instance.round_off_sales = get_pk_ledger_instance(
                data['round_off_sales'], CompanyID)
            instance.discount_on_sales = get_pk_ledger_instance(
                data['discount_on_sales'], CompanyID)
            instance.discount_on_purchase = get_pk_ledger_instance(
                data['discount_on_purchase'], CompanyID)
            instance.discount_on_payment = get_pk_ledger_instance(
                data['discount_on_payment'], CompanyID)
            instance.discount_on_receipt = get_pk_ledger_instance(
                data['discount_on_receipt'], CompanyID)
            instance.discount_on_loyalty = get_pk_ledger_instance(
                data['discount_on_loyalty'], CompanyID)
            instance.round_off_purchase = get_pk_ledger_instance(
                data['round_off_purchase'], CompanyID)

            instance.save()
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Branch', 'Edit',
                         'Branch Updated failed.', generate_serializer_errors(serialized._errors))
            response_data = {
                "StatusCode": 6001,
                "message": generate_serializer_errors(serialized._errors)
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID,
                     'Branch', 'Edit', 'Branch Updated failed.', "Branch Not Found!")
        response_data = {
            "StatusCode": 6001,
            "message": "Branch Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def regional_office_branchs(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instances = Branch.objects.filter(
        CompanyID=CompanyID, is_regional_office=True)
    serialized = BranchRestSerializer(instances, many=True)
    #request , company, log_type, user, source, action, message, description

    response_data = {
        "StatusCode": 6000,
        "data": serialized.data
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def branchs(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instances = Branch.objects.filter(CompanyID=CompanyID)
    serialized = BranchRestSerializer(instances, many=True)
    #request , company, log_type, user, source, action, message, description
    activity_log(request._request, CompanyID, 'Information', CreatedUserID,
                 'Branch', 'List VIew', 'Branch List Viewed.', "Branch List Viewed.")
    response_data = {
        "StatusCode": 6000,
        "data": serialized.data
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def branch(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instance = None
    if Branch.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = Branch.objects.get(pk=pk, CompanyID=CompanyID)
        serialized = BranchRestSerializer(instance)
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Branch',
                     'VIew', 'Branch Single Page Viewed.', 'Branch Single Page Viewed.')
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Branch',
                     'VIew', 'Branch Single Page Viewed Failed.', 'Branch Not Found!')
        response_data = {
            "StatusCode": 6001,
            "message": "Branch Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def delete_branch(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    try:
        selecte_ids = data['selecte_ids']
    except:
        selecte_ids = []

    today = datetime.datetime.now()
    if selecte_ids:
        if Branch.objects.filter(CompanyID=CompanyID, pk__in=selecte_ids).exists():
            instances = Branch.objects.filter(pk__in=selecte_ids)
    else:
        if Branch.objects.filter(CompanyID=CompanyID, pk=pk).exists():
            instances = Branch.objects.filter(pk=pk)

    if instances:
        for instance in instances:

            state = State.objects.get(pk=instance.state.pk)
            country = Country.objects.get(pk=instance.country.pk)
            BranchID = instance.BranchID
            BranchName = instance.BranchName
            DisplayName = instance.DisplayName
            regional_office = None
            if instance.regional_office:
                regional_office = Branch.objects.get(
                    pk=instance.regional_office.pk)
                # regional_office = instance.regional_office,
            phone = instance.Phone
            Email = instance.Email
            Building = instance.Building
            City = instance.City
            GSTNumber = instance.GSTNumber
            VATNumber = instance.VATNumber
            is_gst = instance.is_gst
            is_vat = instance.is_vat
            is_regional_office = instance.is_regional_office
            Action = "D"

            delete_GeneralSettings = delete_model_datas(
                table.GeneralSettings, CompanyID, BranchID, "branch_wise")
            delete_Brand = delete_model_datas(
                table.Brand, CompanyID, BranchID, "branch_wise")
            delete_BrandLog = delete_model_datas(
                table.Brand_Log, CompanyID, BranchID, "branch_wise")
            delete_Route = delete_model_datas(
                table.Route, CompanyID, BranchID, "branch_wise")
            delete_RouteLog = delete_model_datas(
                table.Route_Log, CompanyID, BranchID, "branch_wise")
            delete_TaxCategory = delete_model_datas(
                table.TaxCategory, CompanyID, BranchID, "branch_wise")
            delete_TaxCategory_Log = delete_model_datas(
                table.TaxCategory_Log, CompanyID, BranchID, "branch_wise")
            delete_ProductCategory = delete_model_datas(
                table.ProductCategory, CompanyID, BranchID, "branch_wise")
            delete_ProductCategory_Log = delete_model_datas(
                table.ProductCategory_Log, CompanyID, BranchID, "branch_wise")
            delete_ProductGroup = delete_model_datas(
                table.ProductGroup, CompanyID, BranchID, "branch_wise")
            delete_ProductGroup_Log = delete_model_datas(
                table.ProductGroup_Log, CompanyID, BranchID, "branch_wise")
            delete_Warehouse = delete_model_datas(
                table.Warehouse, CompanyID, BranchID, "branch_wise")
            delete_Warehouse_Log = delete_model_datas(
                table.Warehouse_Log, CompanyID, BranchID, "branch_wise")
            delete_AccountLedger = delete_model_datas(
                table.AccountLedger, CompanyID, BranchID, "branch_wise")
            delete_AccountLedger_Log = delete_model_datas(
                table.AccountLedger_Log, CompanyID, BranchID, "branch_wise")
            delete_Parties = delete_model_datas(
                table.Parties, CompanyID, BranchID, "branch_wise")
            delete_Product = delete_model_datas(
                table.Product, CompanyID, BranchID, "branch_wise")
            delete_Product_Log = delete_model_datas(
                table.Product_Log, CompanyID, BranchID, "branch_wise")
            delete_PriceList = delete_model_datas(
                table.PriceList, CompanyID, BranchID, "branch_wise")
            delete_PriceList_Log = delete_model_datas(
                table.PriceList_Log, CompanyID, BranchID, "branch_wise")
            delete_DamageStockDetails = delete_model_datas(
                table.DamageStockDetails, CompanyID, BranchID, "branch_wise")
            delete_DamageStockDetails_Log = delete_model_datas(
                table.DamageStockDetails_Log, CompanyID, BranchID, "branch_wise")
            delete_DamageStockMaster = delete_model_datas(
                table.DamageStockMaster, CompanyID, BranchID, "branch_wise")
            delete_DamageStockMaster_Log = delete_model_datas(
                table.DamageStockMaster_Log, CompanyID, BranchID, "branch_wise")
            delete_Designation = delete_model_datas(
                table.Designation, CompanyID, BranchID, "branch_wise")
            delete_Designation_Log = delete_model_datas(
                table.Designation_Log, CompanyID, BranchID, "branch_wise")
            delete_Department = delete_model_datas(
                table.Department, CompanyID, BranchID, "branch_wise")
            delete_Department_Log = delete_model_datas(
                table.Department_Log, CompanyID, BranchID, "branch_wise")
            delete_Flavours = delete_model_datas(
                table.Flavours, CompanyID, BranchID, "branch_wise")
            delete_JournalDetails = delete_model_datas(
                table.JournalDetails, CompanyID, BranchID, "branch_wise")
            delete_JournalDetails_Log = delete_model_datas(
                table.JournalDetails_Log, CompanyID, BranchID, "branch_wise")
            delete_JournalMaster = delete_model_datas(
                table.JournalMaster, CompanyID, BranchID, "branch_wise")
            delete_JournalMaster_Log = delete_model_datas(
                table.JournalMaster_Log, CompanyID, BranchID, "branch_wise")
            delete_Kitchen = delete_model_datas(
                table.Kitchen, CompanyID, BranchID, "branch_wise")
            delete_Kitchen_Log = delete_model_datas(
                table.Kitchen_Log, CompanyID, BranchID, "branch_wise")
            delete_LedgerPosting = delete_model_datas(
                table.LedgerPosting, CompanyID, BranchID, "branch_wise")
            delete_LedgerPosting_Log = delete_model_datas(
                table.LedgerPosting_Log, CompanyID, BranchID, "branch_wise")
            delete_OpeningStockDetails = delete_model_datas(
                table.OpeningStockDetails, CompanyID, BranchID, "branch_wise")
            delete_OpeningStockDetails_Log = delete_model_datas(
                table.OpeningStockDetails_Log, CompanyID, BranchID, "branch_wise")
            delete_OpeningStockMaster = delete_model_datas(
                table.OpeningStockMaster, CompanyID, BranchID, "branch_wise")
            delete_OpeningStockMaster_Log = delete_model_datas(
                table.OpeningStockMaster_Log, CompanyID, BranchID, "branch_wise")
            delete_PaymentDetails = delete_model_datas(
                table.PaymentDetails, CompanyID, BranchID, "branch_wise")
            delete_PaymentDetails_Log = delete_model_datas(
                table.PaymentDetails_Log, CompanyID, BranchID, "branch_wise")
            delete_PaymentMaster = delete_model_datas(
                table.PaymentMaster, CompanyID, BranchID, "branch_wise")
            delete_PaymentMaster_Log = delete_model_datas(
                table.PaymentMaster_Log, CompanyID, BranchID, "branch_wise")
            delete_POSHoldDetails = delete_model_datas(
                table.POSHoldDetails, CompanyID, BranchID, "branch_wise")
            delete_POSHoldDetails_Log = delete_model_datas(
                table.POSHoldDetails_Log, CompanyID, BranchID, "branch_wise")
            delete_POSHoldMaster = delete_model_datas(
                table.POSHoldMaster, CompanyID, BranchID, "branch_wise")
            delete_POSHoldMaster_Log = delete_model_datas(
                table.POSHoldMaster_Log, CompanyID, BranchID, "branch_wise")
            delete_PurchaseDetails = delete_model_datas(
                table.PurchaseDetails, CompanyID, BranchID, "branch_wise")
            delete_PurchaseDetails_Log = delete_model_datas(
                table.PurchaseDetails_Log, CompanyID, BranchID, "branch_wise")
            delete_PurchaseMaster = delete_model_datas(
                table.PurchaseMaster, CompanyID, BranchID, "branch_wise")
            delete_PurchaseMaster_Log = delete_model_datas(
                table.PurchaseMaster_Log, CompanyID, BranchID, "branch_wise")
            delete_PurchaseOrderDetails = delete_model_datas(
                table.PurchaseOrderDetails, CompanyID, BranchID, "branch_wise")
            delete_PurchaseOrderDetails_Log = delete_model_datas(
                table.PurchaseOrderDetails_Log, CompanyID, BranchID, "branch_wise")
            delete_PurchaseOrderMaster = delete_model_datas(
                table.PurchaseOrderMaster, CompanyID, BranchID, "branch_wise")
            delete_PurchaseOrderMaster_Log = delete_model_datas(
                table.PurchaseOrderMaster_Log, CompanyID, BranchID, "branch_wise")
            delete_PurchaseReturnDetails = delete_model_datas(
                table.PurchaseReturnDetails, CompanyID, BranchID, "branch_wise")
            delete_PurchaseReturnDetails_Log = delete_model_datas(
                table.PurchaseReturnDetails_Log, CompanyID, BranchID, "branch_wise")
            delete_PurchaseReturnMaster = delete_model_datas(
                table.PurchaseReturnMaster, CompanyID, BranchID, "branch_wise")
            delete_PurchaseReturnMaster_Log = delete_model_datas(
                table.PurchaseReturnMaster_Log, CompanyID, BranchID, "branch_wise")
            delete_ReceiptDetails = delete_model_datas(
                table.ReceiptDetails, CompanyID, BranchID, "branch_wise")
            delete_ReceiptDetails_Log = delete_model_datas(
                table.ReceiptDetails_Log, CompanyID, BranchID, "branch_wise")
            delete_ReceiptMaster = delete_model_datas(
                table.ReceiptMaster, CompanyID, BranchID, "branch_wise")
            delete_ReceiptMaster_Log = delete_model_datas(
                table.ReceiptMaster_Log, CompanyID, BranchID, "branch_wise")
            delete_SalesDetails = delete_model_datas(
                table.SalesDetails, CompanyID, BranchID, "branch_wise")
            delete_SalesDetails_Log = delete_model_datas(
                table.SalesDetails_Log, CompanyID, BranchID, "branch_wise")
            delete_SalesMaster = delete_model_datas(
                table.SalesMaster, CompanyID, BranchID, "branch_wise")
            delete_SalesMaster_Log = delete_model_datas(
                table.SalesMaster_Log, CompanyID, BranchID, "branch_wise")
            delete_SalesOrderDetails = delete_model_datas(
                table.SalesOrderDetails, CompanyID, BranchID, "branch_wise")
            delete_SalesOrderDetails_Log = delete_model_datas(
                table.SalesOrderDetails_Log, CompanyID, BranchID, "branch_wise")
            delete_SalesOrderMaster = delete_model_datas(
                table.SalesOrderMaster, CompanyID, BranchID, "branch_wise")
            delete_SalesOrderMaster_Log = delete_model_datas(
                table.SalesOrderMaster_Log, CompanyID, BranchID, "branch_wise")
            delete_SalesReturnDetails = delete_model_datas(
                table.SalesReturnDetails, CompanyID, BranchID, "branch_wise")
            delete_SalesReturnDetails_Log = delete_model_datas(
                table.SalesReturnDetails_Log, CompanyID, BranchID, "branch_wise")
            delete_SalesReturnMaster = delete_model_datas(
                table.SalesReturnMaster, CompanyID, BranchID, "branch_wise")
            delete_SalesReturnMaster_Log = delete_model_datas(
                table.SalesReturnMaster_Log, CompanyID, BranchID, "branch_wise")
            delete_Settings = delete_model_datas(
                table.Settings, CompanyID, BranchID, "branch_wise")
            delete_Settings_Log = delete_model_datas(
                table.Settings_Log, CompanyID, BranchID, "branch_wise")
            delete_StockAdjustmentDetails = delete_model_datas(
                table.StockAdjustmentDetails, CompanyID, BranchID, "branch_wise")
            delete_StockAdjustmentDetails_Log = delete_model_datas(
                table.StockAdjustmentDetails_Log, CompanyID, BranchID, "branch_wise")
            delete_StockAdjustmentMaster = delete_model_datas(
                table.StockAdjustmentMaster, CompanyID, BranchID, "branch_wise")
            delete_StockAdjustmentMaster_Log = delete_model_datas(
                table.StockAdjustmentMaster_Log, CompanyID, BranchID, "branch_wise")
            delete_StockReceiptDetails = delete_model_datas(
                table.StockReceiptDetails, CompanyID, BranchID, "branch_wise")
            delete_StockReceiptDetails_Log = delete_model_datas(
                table.StockReceiptDetails_Log, CompanyID, BranchID, "branch_wise")
            delete_StockReceiptMaster_ID = delete_model_datas(
                table.StockReceiptMaster_ID, CompanyID, BranchID, "branch_wise")
            delete_StockReceiptMasterID_Log = delete_model_datas(
                table.StockReceiptMasterID_Log, CompanyID, BranchID, "branch_wise")
            delete_StockTransferDetails = delete_model_datas(
                table.StockTransferDetails, CompanyID, BranchID, "branch_wise")
            delete_StockTransferDetails_Log = delete_model_datas(
                table.StockTransferDetails_Log, CompanyID, BranchID, "branch_wise")
            delete_StockTransferMaster_ID = delete_model_datas(
                table.StockTransferMaster_ID, CompanyID, BranchID, "branch_wise")
            delete_StockTransferMasterID_Log = delete_model_datas(
                table.StockTransferMasterID_Log, CompanyID, BranchID, "branch_wise")
            delete_StockPosting = delete_model_datas(
                table.StockPosting, CompanyID, BranchID, "branch_wise")
            delete_StockPosting_Log = delete_model_datas(
                table.StockPosting_Log, CompanyID, BranchID, "branch_wise")
            delete_StockRate = delete_model_datas(
                table.StockRate, CompanyID, BranchID, "branch_wise")
            delete_StockTrans = delete_model_datas(
                table.StockTrans, CompanyID, BranchID, "branch_wise")
            delete_Bank = delete_model_datas(
                table.Bank, CompanyID, BranchID, "branch_wise")
            delete_Bank_Log = delete_model_datas(
                table.Bank_Log, CompanyID, BranchID, "branch_wise")
            delete_Unit = delete_model_datas(
                table.Unit, CompanyID, BranchID, "branch_wise")
            delete_Unit_Log = delete_model_datas(
                table.Unit_Log, CompanyID, BranchID, "branch_wise")
            delete_UserTable = delete_model_datas(
                table.UserTable, CompanyID, BranchID, "branch_wise")

            instance.delete()

            Branch_Log.objects.create(
                TransactionID=BranchID,
                BranchName=BranchName,
                DisplayName=DisplayName,
                regional_office=regional_office,
                Phone=phone,
                Email=Email,
                Building=Building,
                City=City,
                state=state,
                country=country,
                GSTNumber=GSTNumber,
                VATNumber=VATNumber,
                is_gst=is_gst,
                is_vat=is_vat,
                is_regional_office=is_regional_office,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Branch',
                         'Deleted', "Branch Deleted Successfully!", "Branch Deleted Successfully!")
            response_data = {
                "StatusCode": 6000,
                "message": "Branch Deleted Successfully!"
            }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID,
                     'Branch', 'Delete', 'Branch Deleted Failed.', 'Branch Not Found!')
        response_data = {
            "StatusCode": 6001,
            "message": "Branch Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def create_branch_settings(request):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    data = request.data
    serialized = BranchSettingsSerializer(data=request.data)

    # if serialized.is_valid():
    if data:
        SettingsType = data['SettingsType']
        SettingsValue = data['SettingsValue']
        # productsForAllBranches = data['productsForAllBranches']
        User = request.user.id
        create_or_update_branch_settings(
            CompanyID, SettingsType, SettingsValue, User)
        # create_or_update_branch_settings(
        #     CompanyID, "customersForAllBranches", customersForAllBranches, User)
        # create_or_update_branch_settings(
        #     CompanyID, "productsForAllBranches", productsForAllBranches, User)
        response_data = {
            "StatusCode": 6000,
        }
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
            # "message": "data is not exists"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def branch_settings_list(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    if BranchSettings.objects.filter(CompanyID=CompanyID).exists():
        instances = BranchSettings.objects.filter(
            CompanyID=CompanyID)

        suppliersForAllBranches = get_branch_settings(
            CompanyID, "suppliersForAllBranches")
        customersForAllBranches = get_branch_settings(
            CompanyID, "customersForAllBranches")
        productsForAllBranches = get_branch_settings(
            CompanyID, "productsForAllBranches")
        EnableBranch = get_branch_settings(
            CompanyID, "EnableBranch")

        dic = {
            "suppliersForAllBranches": suppliersForAllBranches,
            "customersForAllBranches": customersForAllBranches,
            "productsForAllBranches": productsForAllBranches,
            "EnableBranch": EnableBranch,
        }
        response_data = {
            "StatusCode": 6000,
            "data": dic,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Settings not found"
        }
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def check_branch_delete(request):
    data = request.data
    CompanyID = data['CompanyID']
    username = data['username']
    password = data['password']

    user = authenticate(username=username, password=password)
    if user is not None:
        userID = CompanySettings.objects.get(id=CompanyID).CreatedUserID
        if userID == user.id:
            response_data = {
                "StatusCode": 6000,
                "message": "Branch Deleted Successfully!"
            }
            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6001,
                "title": "Failed",
                "message": "Branch can delete only the owner of organization"
            }
            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "user credential is wrong!"
        }
        return Response(response_data, status=status.HTTP_200_OK)
