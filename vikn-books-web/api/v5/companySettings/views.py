from brands.models import CompanySettings, CompanySettings_Log, Designation, Department, AccountLedger, TransactionTypes, Warehouse, UserType, AccountGroup, Bank, Branch, Brand, Flavours, Color, GeneralSettings, MasterType, PriceCategory, ProductCategory, ProductGroup, Route, TaxCategory, TaxType, Country, Unit, FinancialYear, FinancialYear_Log, Unit, State, BusinessType, UserTable, Customer, User_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v5.companySettings.serializers import CompanySettingsRestSerializer, CompanySettingsInitialSerializer, FinancialYearSerializer
from api.v5.companySettings.functions import generate_serializer_errors
from rest_framework import status
from api.v5.companySettings.serializers import CompanySettingsSerializer
from administrations.functions import get_auto_id_financial_year
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from main.functions import get_company, activity_log
from api.v5.settings.functions import create_or_update_user_type_settings, get_user_type_settings
import datetime
import json
import os
from django.contrib.auth import authenticate
from api.v5.general.functions import isValidMasterCardNo
from api.v5.settings.functions import create_or_update_user_type_settings


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_companySettings_initial(request):
    data = request.data
    owner = data['owner']
    CreatedUserID = data['CreatedUserID']
    UpdatedUserID = data['UpdatedUserID']
    CompanyLogo = data['CompanyLogo']
    is_registeredVat = data['is_registeredVat']
    if CompanyLogo == "null":
        CompanyLogo = None

    today = datetime.datetime.now()
    serialized = CompanySettingsInitialSerializer(data=request.data)
    serialized1 = FinancialYearSerializer(data=request.data)

    if serialized.is_valid() and serialized1.is_valid():
        GSTNumber = serialized.data['GSTNumber']

        is_Gstn_validate = True
        if GSTNumber:
            if is_registeredVat:
                is_Gstn_validate = False
                print("KAYAR?YYYYYYYYYYYYYYYYYYYYYYYYYYYYY")
                is_Gstn_validate = isValidMasterCardNo(GSTNumber)
        print(is_Gstn_validate, GSTNumber)
        if is_Gstn_validate:
            # GSTNumber = serialized.data['GSTNumber']
            CompanyName = serialized.data['CompanyName']
            VATNumber = serialized.data['VATNumber']
            State_pk = serialized.data['State']
            States = State.objects.get(pk=State_pk)
            business_type_pk = serialized.data['business_type']
            business_types = BusinessType.objects.get(pk=business_type_pk)
            countries = serialized.data['Country']
            is_vat = serialized.data['is_vat']
            is_gst = serialized.data['is_gst']

            FromDate = serialized1.data['FromDate']
            FromDate = datetime.datetime.strptime(FromDate, '%Y-%m-%d')
            ToDate = serialized1.data['ToDate']
            ToDate = datetime.datetime.strptime(ToDate, '%Y-%m-%d')
            date = datetime.datetime.now().date()
            today_date = datetime.datetime.strptime(str(date), '%Y-%m-%d')
            ExpiryDate = today_date + datetime.timedelta(days=7)

            owner = get_object_or_404(User.objects.filter(pk=owner))
            Action = 'A'
            countries = Country.objects.get(pk=countries)

            if CompanySettings.objects.filter(is_deleted=False, owner=owner, CompanyName__iexact=CompanyName).exists():
                response_data = {
                    "StatusCode": 6001,
                    "message": f"{CompanyName} already exists."
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:

                company = CompanySettings.objects.create(
                    owner=owner,
                    CompanyName=CompanyName,
                    CompanyLogo=CompanyLogo,
                    State=States,
                    Country=countries,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    GSTNumber=GSTNumber,
                    VATNumber=VATNumber,
                    business_type=business_types,
                    UpdatedUserID=UpdatedUserID,
                    ExpiryDate=ExpiryDate,
                    is_vat=is_vat,
                    is_gst=is_gst,
                )

                CompanySettings_Log.objects.create(
                    owner=owner,
                    TransactionID=company.id,
                    CompanyName=CompanyName,
                    CompanyLogo=company.CompanyLogo,
                    State=States,
                    Country=countries,
                    CreatedDate=today,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    VATNumber=VATNumber,
                    GSTNumber=GSTNumber,
                    UpdatedUserID=UpdatedUserID,
                    business_type=business_types,
                    UpdatedDate=today,
                    ExpiryDate=ExpiryDate,
                    is_vat=is_vat,
                    is_gst=is_gst,
                )

                customer = Customer.objects.get(user=owner)
                user_table = UserTable.objects.create(
                    CompanyID=company,
                    Sales_Account=85,
                    Sales_Return_Account=86,
                    Purchase_Account=69,
                    Purchase_Return_Account=70,
                    Cash_Account=1,
                    Bank_Account=92,
                    CreatedUserID=CreatedUserID,
                    customer=customer,
                    CreatedDate=today,
                    UpdatedDate=today,
                    JoinedDate=today,
                    is_owner=True,
                    Action='A',
                )

                User_Log.objects.create(
                    TransactionID=user_table.id,
                    CompanyID=company,
                    Sales_Account=85,
                    Sales_Return_Account=86,
                    Purchase_Account=69,
                    Purchase_Return_Account=70,
                    Cash_Account=1,
                    Bank_Account=92,
                    CreatedUserID=CreatedUserID,
                    customer=customer,
                    CreatedDate=today,
                    UpdatedDate=today,
                    JoinedDate=today,
                    is_owner=True,
                    Action='A',
                )

            CompanyID = company.id
            CompanyID = get_company(CompanyID)
            auto_id = get_auto_id_financial_year(FinancialYear, CompanyID)

            financial_year = FinancialYear.objects.create(
                Action='A',
                CreatedUserID=CreatedUserID,
                FinancialYearID=auto_id,
                FromDate=FromDate,
                ToDate=ToDate,
                CreatedDate=today,
                UpdatedDate=today,
                IsClosed=False,
                CompanyID=CompanyID,
            )
            FinancialYear_Log.objects.create(
                TransactionID=financial_year.FinancialYearID,
                Action=financial_year.Action,
                FromDate=FromDate,
                ToDate=ToDate,
                CreatedDate=financial_year.CreatedDate,
                UpdatedDate=financial_year.UpdatedDate,
                CreatedUserID=financial_year.CreatedUserID,
                IsClosed=False,
                CompanyID=CompanyID,
            )

            # ================creating defult Designation starts here================
            THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(
                THIS_FOLDER, 'company_fixtures/designations.json')

            # path = 'main/fixtures/account_groups.json'
            with open(path, 'r+') as json_file:
                json_data = json_file.read()
                dic = json.loads(json_data)
                # name = dic[0]['fields']['GroupName']
                CompanyID = company.id
                CompanyID = get_company(CompanyID)
                for i in dic:
                    if i['model'] == "brands.Designation":
                        DesignationID = i['fields']['DesignationID']
                        BranchID = i['fields']['BranchID']
                        DesignationName = i['fields']['DesignationName']
                        ShortName = i['fields']['ShortName']
                        DesignationUnder = i['fields']['DesignationUnder']
                        Notes = i['fields']['Notes']
                        CreatedUserID = i['fields']['CreatedUserID']
                        CreatedDate = i['fields']['CreatedDate']
                        UpdatedDate = i['fields']['UpdatedDate']
                        Action = i['fields']['Action']
                        Designation.objects.create(
                            CompanyID=CompanyID,
                            DesignationID=DesignationID,
                            BranchID=BranchID,
                            DesignationName=DesignationName,
                            ShortName=ShortName,
                            DesignationUnder=DesignationUnder,
                            Notes=Notes,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            Action=Action,
                        )
            # ================creating defult Designation ends here================

            # ================creating defult Department starts here================
            THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(
                THIS_FOLDER, 'company_fixtures/departments.json')

            # path = 'main/fixtures/account_groups.json'
            with open(path, 'r+') as json_file:
                json_data = json_file.read()
                dic = json.loads(json_data)
                # name = dic[0]['fields']['GroupName']
                CompanyID = company.id
                CompanyID = get_company(CompanyID)
                for i in dic:
                    if i['model'] == "brands.Department":
                        DepartmentID = i['fields']['DepartmentID']
                        BranchID = i['fields']['BranchID']
                        DepartmentName = i['fields']['DepartmentName']
                        Notes = i['fields']['Notes']
                        CreatedUserID = i['fields']['CreatedUserID']
                        CreatedDate = i['fields']['CreatedDate']
                        UpdatedDate = i['fields']['UpdatedDate']
                        Action = i['fields']['Action']
                        Department.objects.create(
                            CompanyID=CompanyID,
                            DepartmentID=DepartmentID,
                            BranchID=BranchID,
                            DepartmentName=DepartmentName,
                            Notes=Notes,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=CreatedDate,
                            UpdatedDate=UpdatedDate,
                            Action=Action,
                        )
            # ================creating defult Department ends here================

            # ================creating defult Account Ledger starts here================
            THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(
                THIS_FOLDER, 'company_fixtures/account_ledgers.json')

            # path = 'main/fixtures/account_groups.json'
            with open(path, 'r+') as json_file:
                json_data = json_file.read()
                dic = json.loads(json_data)
                # name = dic[0]['fields']['GroupName']
                CompanyID = company.id
                CompanyID = get_company(CompanyID)
                for i in dic:
                    if i['model'] == "brands.AccountLedger":
                        LedgerID = i['fields']['LedgerID']
                        BranchID = i['fields']['BranchID']
                        LedgerName = i['fields']['LedgerName']
                        LedgerCode = i['fields']['LedgerCode']
                        AccountGroupUnder = i['fields']['AccountGroupUnder']
                        OpeningBalance = i['fields']['OpeningBalance']
                        CrOrDr = i['fields']['CrOrDr']
                        Notes = i['fields']['Notes']
                        IsActive = i['fields']['IsActive']
                        IsDefault = i['fields']['IsDefault']
                        CreatedUserID = i['fields']['CreatedUserID']
                        CreatedDate = i['fields']['CreatedDate']
                        UpdatedDate = i['fields']['UpdatedDate']
                        Action = i['fields']['Action']
                        AccountLedger.objects.create(
                            CompanyID=CompanyID,
                            LedgerID=LedgerID,
                            BranchID=BranchID,
                            LedgerName=LedgerName,
                            LedgerCode=LedgerCode,
                            AccountGroupUnder=AccountGroupUnder,
                            OpeningBalance=OpeningBalance,
                            CrOrDr=CrOrDr,
                            Notes=Notes,
                            IsActive=IsActive,
                            IsDefault=IsDefault,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=CreatedDate,
                            UpdatedDate=UpdatedDate,
                            Action=Action,
                        )
            # ================creating defult Account Ledger ends here================

            # ================creating defult Transaction Types starts here================
            THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(
                THIS_FOLDER, 'company_fixtures/transaction_types.json')

            # path = 'main/fixtures/account_groups.json'
            with open(path, 'r+') as json_file:
                json_data = json_file.read()
                dic = json.loads(json_data)
                # name = dic[0]['fields']['GroupName']
                CompanyID = company.id
                CompanyID = get_company(CompanyID)
                for i in dic:
                    if i['model'] == "brands.TransactionTypes":
                        TransactionTypesID = i['fields']['TransactionTypesID']
                        BranchID = i['fields']['BranchID']
                        Action = i['fields']['Action']
                        MasterTypeID = i['fields']['MasterTypeID']
                        Name = i['fields']['Name']
                        Notes = i['fields']['Notes']
                        CreatedDate = i['fields']['CreatedDate']
                        UpdatedDate = i['fields']['UpdatedDate']
                        CreatedUserID = i['fields']['CreatedUserID']
                        IsDefault = i['fields']['IsDefault']
                        TransactionTypes.objects.create(
                            CompanyID=CompanyID,
                            TransactionTypesID=TransactionTypesID,
                            BranchID=BranchID,
                            Action=Action,
                            MasterTypeID=MasterTypeID,
                            Name=Name,
                            Notes=Notes,
                            CreatedDate=CreatedDate,
                            UpdatedDate=UpdatedDate,
                            CreatedUserID=CreatedUserID,
                            IsDefault=IsDefault,
                        )
            # ================creating defult Transaction Types ends here================

            # ================creating defult Warehouse starts here================
            THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(
                THIS_FOLDER, 'company_fixtures/warehouses.json')

            # path = 'main/fixtures/account_groups.json'
            with open(path, 'r+') as json_file:
                json_data = json_file.read()
                dic = json.loads(json_data)
                # name = dic[0]['fields']['GroupName']
                CompanyID = company.id
                CompanyID = get_company(CompanyID)
                for i in dic:
                    if i['model'] == "brands.Warehouse":
                        WarehouseID = i['fields']['WarehouseID']
                        BranchID = i['fields']['BranchID']
                        WarehouseName = i['fields']['WarehouseName']
                        Notes = i['fields']['Notes']
                        CreatedUserID = i['fields']['CreatedUserID']
                        CreatedDate = i['fields']['CreatedDate']
                        UpdatedDate = i['fields']['UpdatedDate']
                        Action = i['fields']['Action']
                        Warehouse.objects.create(
                            CompanyID=CompanyID,
                            WarehouseID=WarehouseID,
                            BranchID=BranchID,
                            WarehouseName=WarehouseName,
                            Notes=Notes,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=CreatedDate,
                            UpdatedDate=UpdatedDate,
                            Action=Action,
                        )
                # ================creating defult Warehouse ends here================

            # ================creating defult UserType starts here================
            THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(
                THIS_FOLDER, 'company_fixtures/user_types.json')

            # path = 'main/fixtures/account_groups.json'
            with open(path, 'r+') as json_file:
                json_data = json_file.read()
                dic = json.loads(json_data)
                # name = dic[0]['fields']['GroupName']
                CompanyID = company.id
                CompanyID = get_company(CompanyID)
                for i in dic:
                    if i['model'] == "brands.UserType":
                        ID = i['fields']['ID']
                        UserTypeName = i['fields']['UserTypeName']
                        BranchID = i['fields']['BranchID']
                        Notes = i['fields']['Notes']
                        CreatedUserID = i['fields']['CreatedUserID']
                        CreatedDate = i['fields']['CreatedDate']
                        UpdatedDate = i['fields']['UpdatedDate']
                        Action = i['fields']['Action']
                        IsActive = i['fields']['IsActive']
                        UserType.objects.create(
                            CompanyID=CompanyID,
                            ID=ID,
                            UserTypeName=UserTypeName,
                            BranchID=BranchID,
                            Notes=Notes,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=CreatedDate,
                            UpdatedDate=UpdatedDate,
                            Action=Action,
                            IsActive=IsActive,
                        )
            usertype_instance = UserType.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, UserTypeName="Admin")
            user_table_instance = UserTable.objects.get(CompanyID=CompanyID)
            user_table_instance.UserType = usertype_instance
            user_table_instance.save()
            # ================creating defult UserType ends here================

            # ================creating defult UserTypeSettings starts here================

            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Masters", "AccountGroupView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Masters", "AccountGroupSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Masters", "AccountGroupEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Masters", "AccountGroupDelete", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Masters", "AccountLedgerView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Masters", "AccountLedgerSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Masters", "AccountLedgerEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Masters", "AccountLedgerDelete", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Masters", "BankView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Masters", "BankSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Masters", "BankEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Masters", "BankDelete", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Masters", "CustomerView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Masters", "CustomerSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Masters", "CustomerEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Masters", "CustomerDelete", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Masters", "SupplierView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Masters", "SupplierSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Masters", "SupplierEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Masters", "SupplierDelete", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Masters", "TransactionTypeView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Masters", "TransactionTypeSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Masters", "TransactionTypeEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Masters", "TransactionTypeDelete", True, usertype_instance)

            # Accounts => Transactions
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Transactions", "BankPaymentDelete", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Transactions", "BankPaymentEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Transactions", "BankPaymentSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Transactions", "BankPaymentView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Transactions", "BankReceiptDelete", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Transactions", "BankReceiptEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Transactions", "BankReceiptSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Transactions", "BankReceiptView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Transactions", "CashPaymentDelete", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Transactions", "CashPaymentEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Transactions", "CashPaymentSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Transactions", "CashPaymentView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Transactions", "CashReceiptDelete", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Transactions", "CashReceiptEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Transactions", "CashReceiptSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Transactions", "CashReceiptView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Transactions", "JournalEntryDelete", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Transactions", "JournalEntryEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Transactions", "JournalEntrySave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Transactions", "JournalEntryView", True, usertype_instance)

            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Transactions", "CashPaymentDiscountLimit", 0, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Transactions", "CashReceiptDiscountLimit", 0, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Transactions", "BankPaymentLimit", 0, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Transactions", "BankReceiptLimit", 0, usertype_instance)
            # Accounts => Reports
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Reports", "LedgerReportView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Reports", "LedgerReportPrint", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Reports", "LedgerReportExport", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Reports", "TrialBalanceView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Reports", "TrialBalancePrint", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Reports", "TrialBalanceExport", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Reports", "ProfitAndLossView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Reports", "ProfitAndLossPrint", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Reports", "ProfitAndLossExport", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Reports", "BalanceSheetView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Reports", "BalanceSheetPrint", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Reports", "BalanceSheetExport", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Reports", "DailyReportView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Reports", "DailyReportPrint", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Reports", "DailyReportExport", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Reports", "CashBookView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Reports", "CashBookPrint", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Reports", "CashBookExport", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Reports", "VATReportView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Reports", "VATReportPrint", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Accounts_Reports", "VATReportExport", True, usertype_instance)

            # Inventory => Masters
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "ProductGroupView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "ProductGroupSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "ProductGroupEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "ProductGroupDelete", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "BrandsView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "BrandsSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "BrandsEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "BrandsDelete", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "TaxCategoriesView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "TaxCategoriesSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "TaxCategoriesEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "TaxCategoriesDelete", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "PriceCategoriesView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "PriceCategoriesSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "PriceCategoriesEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "PriceCategoriesDelete", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "WarehouseView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "WarehouseSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "WarehouseEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "WarehouseDelete", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "ProductCategoriesView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "ProductCategoriesSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "ProductCategoriesEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "ProductCategoriesDelete", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "ProductsView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "ProductsSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "ProductsEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "ProductsDelete", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "RoutesView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "RoutesSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "RoutesEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "RoutesDelete", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "UnitsView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "UnitsSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "UnitsEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Masters", "UnitsDelete", True, usertype_instance)

            # Inventory => Transaction
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "PurchaseInvoicesView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "PurchaseInvoicesSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "PurchaseInvoicesEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "PurchaseInvoicesDelete", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "WorkOrdersView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "WorkOrdersSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "WorkOrdersEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "WorkOrdersDelete", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "PurchaseReturnsView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "PurchaseReturnsSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "PurchaseReturnsEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "PurchaseReturnsDelete", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "SaleInvoicesView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "SaleInvoicesSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "SaleInvoicesEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "SaleInvoicesDelete", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "SaleReturnsView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "SaleReturnsSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "SaleReturnsEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "SaleReturnsDelete", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "OpeningStockView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "OpeningStockSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "OpeningStockEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "OpeningStockDelete", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "StockTransferView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "StockTransferSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "StockTransferEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "StockTransferDelete", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "ExcessStocksView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "ExcessStocksSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "ExcessStocksEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "ExcessStocksDelete", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "ShortageStocksView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "ShortageStocksSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "ShortageStocksEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "ShortageStocksDelete", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "DamageStocksView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "DamageStocksSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "DamageStocksEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "DamageStocksDelete", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "UsedStocksView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "UsedStocksSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "UsedStocksEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "UsedStocksDelete", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "StockAdjustmentsView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "StockAdjustmentsSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "StockAdjustmentsEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "StockAdjustmentsDelete", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "SalesOrderView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "SalesOrderSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "SalesOrderEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "SalesOrderDelete", True, usertype_instance)

            # =====
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "SalesEstimateView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "SalesEstimateSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "SalesEstimateEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "SalesEstimateDelete", True, usertype_instance)
            # =====

            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "PurchaseInvoicesDiscountLimit", 0, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "PurchaseReturnsDiscountLimit", 0, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "SaleInvoicesDiscountLimit", 0, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Transactions", "SaleReturnsDiscountLimit", 0, usertype_instance)
            # Inventory => Reports
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Reports", "StockReportView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Reports", "StockReportPrint", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Reports", "StockReportExport", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Reports", "StockValueReportView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Reports", "StockValueReportPrint", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Reports", "StockValueReportExport", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Reports", "PurchaseReportView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Reports", "PurchaseReportPrint", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Reports", "PurchaseReportExport", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Reports", "SalesReportView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Reports", "SalesReportPrint", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Reports", "SalesReportExport", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Reports", "SalesIntegratedReportView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Reports", "SalesIntegratedReportPrint", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Reports", "SalesIntegratedReportExport", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Reports", "SalesRegisterReportView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Reports", "SalesRegisterReportPrint", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Reports", "SalesRegisterReportExport", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Reports", "BillWiseReportView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Reports", "BillWiseReportPrint", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Reports", "BillWiseReportExport", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Reports", "ExcessStockReportView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Reports", "ExcessStockReportPrint", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Reports", "ExcessStockReportExport", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Reports", "DamageStockReportView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Reports", "DamageStockReportPrint", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Reports", "DamageStockReportExport", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Reports", "UsedStockReportView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Reports", "UsedStockReportPrint", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Reports", "UsedStockReportExport", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Reports", "BatchWiseReportView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Reports", "BatchWiseReportPrint", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Inventory_Reports", "BatchWiseReportExport", True, usertype_instance)
            # Payroll => Masters
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Payroll_Masters", "DepartmentsView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Payroll_Masters", "DepartmentsSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Payroll_Masters", "DepartmentsEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Payroll_Masters", "DepartmentsDelete", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Payroll_Masters", "DesignationsView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Payroll_Masters", "DesignationsSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Payroll_Masters", "DesignationsEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Payroll_Masters", "DesignationsDelete", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Payroll_Masters", "EmployeeView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Payroll_Masters", "EmployeeSave", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Payroll_Masters", "EmployeeEdit", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Payroll_Masters", "EmployeeDelete", True, usertype_instance)

            # Settings
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Settings", "PrinterView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Settings", "BarcodeView", True, usertype_instance)
            create_or_update_user_type_settings(
                owner.id, CompanyID,
                BranchID, "Settings", "PrintBarcodeView", True, usertype_instance)

            # ================creating defult UserTypeSettings ends here================

            # ================creating defult Account Groups starts here================
            THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(
                THIS_FOLDER, 'company_fixtures/account_groups.json')

            # path = 'main/fixtures/account_groups.json'
            with open(path, 'r+') as json_file:
                json_data = json_file.read()
                dic = json.loads(json_data)
                # name = dic[0]['fields']['GroupName']
                CompanyID = company.id
                CompanyID = get_company(CompanyID)
                for i in dic:
                    if i['model'] == "brands.AccountGroup":
                        AccountGroupID = i['fields']['AccountGroupID']
                        AccountGroupName = i['fields']['AccountGroupName']
                        GroupCode = i['fields']['GroupCode']
                        AccountGroupUnder = i['fields']['AccountGroupUnder']
                        Notes = i['fields']['Notes']
                        CreatedUserID = i['fields']['CreatedUserID']
                        CreatedDate = i['fields']['CreatedDate']
                        UpdatedDate = i['fields']['UpdatedDate']
                        IsActive = i['fields']['IsActive']
                        IsDefault = i['fields']['IsDefault']
                        Action = i['fields']['Action']
                        AccountGroup.objects.create(
                            CompanyID=CompanyID,
                            AccountGroupID=AccountGroupID,
                            AccountGroupName=AccountGroupName,
                            GroupCode=GroupCode,
                            AccountGroupUnder=AccountGroupUnder,
                            Notes=Notes,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=CreatedDate,
                            UpdatedDate=UpdatedDate,
                            IsActive=IsActive,
                            IsDefault=IsDefault,
                            Action=Action,
                        )
            # ================creating default Account Groups ends here================

            # ================creating default Banks starts here================
            THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(THIS_FOLDER, 'company_fixtures/banks.json')

            # path = 'main/fixtures/banks.json'
            with open(path, 'r+') as json_file:
                json_data = json_file.read()
                dic = json.loads(json_data)
                # name = dic[0]['fields']['GroupName']
                CompanyID = company.id
                CompanyID = get_company(CompanyID)
                for i in dic:
                    if i['model'] == "brands.Bank":
                        BankID = i['fields']['BankID']
                        BranchID = i['fields']['BranchID']
                        Name = i['fields']['Name']
                        LedgerName = i['fields']['LedgerName']
                        LedgerCode = i['fields']['LedgerCode']
                        AccountNumber = i['fields']['AccountNumber']
                        OpeningBalance = i['fields']['OpeningBalance']
                        Notes = i['fields']['Notes']
                        CreatedUserID = i['fields']['CreatedUserID']
                        CreatedDate = i['fields']['CreatedDate']
                        Bank.objects.create(
                            CompanyID=CompanyID,
                            BankID=BankID,
                            BranchID=BranchID,
                            Name=Name,
                            LedgerName=LedgerName,
                            LedgerCode=LedgerCode,
                            AccountNumber=AccountNumber,
                            OpeningBalance=OpeningBalance,
                            Notes=Notes,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=CreatedDate,
                        )
            # ================creating defult Banks ends here================

            # ================creating defult branches starts here================
            THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(THIS_FOLDER, 'company_fixtures/branches.json')

            # path = 'main/fixtures/banks.json'
            with open(path, 'r+') as json_file:
                json_data = json_file.read()
                dic = json.loads(json_data)
                # name = dic[0]['fields']['GroupName']
                CompanyID = company.id
                CompanyID = get_company(CompanyID)
                for i in dic:
                    if i['model'] == "brands.Branch":
                        BranchID = i['fields']['BranchID']
                        BranchName = i['fields']['BranchName']
                        BranchLocation = i['fields']['BranchLocation']
                        CreatedUserID = i['fields']['CreatedUserID']
                        CreatedDate = i['fields']['CreatedDate']
                        Action = i['fields']['Action']
                        Branch.objects.create(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            BranchName=BranchName,
                            BranchLocation=BranchLocation,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=CreatedDate,
                            Action=Action,
                        )
            # ================creating defult branches ends here================

            # ================creating defult brands starts here================
            THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(THIS_FOLDER, 'company_fixtures/brands.json')

            # path = 'main/fixtures/banks.json'
            with open(path, 'r+') as json_file:
                json_data = json_file.read()
                dic = json.loads(json_data)
                # name = dic[0]['fields']['GroupName']
                CompanyID = company.id
                CompanyID = get_company(CompanyID)
                for i in dic:
                    if i['model'] == "brands.Brand":
                        BrandID = i['fields']['BrandID']
                        BranchID = i['fields']['BranchID']
                        BrandName = i['fields']['BrandName']
                        Notes = i['fields']['Notes']
                        CreatedUserID = i['fields']['CreatedUserID']
                        CreatedDate = i['fields']['CreatedDate']
                        Action = i['fields']['Action']
                        Brand.objects.create(
                            CompanyID=CompanyID,
                            BrandID=BrandID,
                            BranchID=BranchID,
                            BrandName=BrandName,
                            Notes=Notes,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=CreatedDate,
                            Action=Action,
                        )
            # ================creating defult brands ends here================

            # ================creating defult Color starts here================
            THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(THIS_FOLDER, 'company_fixtures/colors.json')

            # path = 'main/fixtures/colors.json'
            with open(path, 'r+') as json_file:
                json_data = json_file.read()
                dic = json.loads(json_data)
                # name = dic[0]['fields']['GroupName']
                CompanyID = company.id
                CompanyID = get_company(CompanyID)
                for i in dic:
                    if i['model'] == "brands.Color":
                        ColorID = i['fields']['ColorID']
                        ColorName = i['fields']['ColorName']
                        ColorValue = i['fields']['ColorValue']
                        Action = i['fields']['Action']

                        Color.objects.create(
                            CompanyID=CompanyID,
                            ColorID=ColorID,
                            ColorName=ColorName,
                            ColorValue=ColorValue,
                            Action=Action,
                        )
            # ================creating defult Color ends here================

            # ================creating defult Flavours starts here================
            THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(THIS_FOLDER, 'company_fixtures/flavours.json')

            # path = 'main/fixtures/flavours.json'
            with open(path, 'r+') as json_file:
                json_data = json_file.read()
                dic = json.loads(json_data)
                # name = dic[0]['fields']['GroupName']
                CompanyID = company.id
                CompanyID = get_company(CompanyID)
                for i in dic:
                    if i['model'] == "brands.Flavours":
                        FlavourID = i['fields']['FlavourID']
                        BranchID = i['fields']['BranchID']
                        FlavourName = i['fields']['FlavourName']
                        BgColor = i['fields']['BgColor']
                        IsActive = i['fields']['IsActive']
                        Action = i['fields']['Action']
                        Flavours.objects.create(
                            CompanyID=CompanyID,
                            FlavourID=FlavourID,
                            BranchID=BranchID,
                            FlavourName=FlavourName,
                            BgColor=BgColor,
                            IsActive=IsActive,
                            Action=Action,
                        )

            # ================creating defult Flavours ends here================

            # ================creating defult General Settings starts here================
            THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(
                THIS_FOLDER, 'company_fixtures/general_settings.json')

            # path = 'main/fixtures/general_settings.json'
            with open(path, 'r+') as json_file:
                json_data = json_file.read()
                dic = json.loads(json_data)
                # name = dic[0]['fields']['GroupName']
                CompanyID = company.id
                CompanyID = get_company(CompanyID)
                for i in dic:
                    if i['model'] == "brands.GeneralSettings":
                        GeneralSettingsID = i['fields']['GeneralSettingsID']
                        BranchID = i['fields']['BranchID']
                        GroupName = i['fields']['GroupName']
                        SettingsType = i['fields']['SettingsType']
                        SettingsValue = i['fields']['SettingsValue']
                        Action = i['fields']['Action']
                        CreatedDate = i['fields']['CreatedDate']
                        UpdatedDate = i['fields']['UpdatedDate']
                        CreatedUserID = i['fields']['CreatedUserID']

                        GeneralSettings.objects.create(
                            CompanyID=CompanyID,
                            GeneralSettingsID=GeneralSettingsID,
                            BranchID=BranchID,
                            GroupName=GroupName,
                            SettingsType=SettingsType,
                            SettingsValue=SettingsValue,
                            Action=Action,
                            CreatedDate=CreatedDate,
                            UpdatedDate=UpdatedDate,
                            CreatedUserID=CreatedUserID,
                        )

            if GSTNumber:
                GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="GST").update(
                    SettingsValue="true", UpdatedDate=today, CreatedUserID=CreatedUserID, Action="A")
            # ================creating defult General Settings ends here================

            # ================creating defult Master Type starts here================
            THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(
                THIS_FOLDER, 'company_fixtures/master_types.json')

            # path = 'main/fixtures/master_types.json'
            with open(path, 'r+') as json_file:
                json_data = json_file.read()
                dic = json.loads(json_data)
                # name = dic[0]['fields']['GroupName']
                CompanyID = company.id
                CompanyID = get_company(CompanyID)
                for i in dic:
                    if i['model'] == "brands.MasterType":
                        MasterTypeID = i['fields']['MasterTypeID']
                        BranchID = i['fields']['BranchID']
                        Name = i['fields']['Name']
                        Description = i['fields']['Description']
                        CreatedUserID = i['fields']['CreatedUserID']
                        IsDefault = i['fields']['IsDefault']

                        MasterType.objects.create(
                            CompanyID=CompanyID,
                            MasterTypeID=MasterTypeID,
                            BranchID=BranchID,
                            Name=Name,
                            Description=Description,
                            CreatedUserID=CreatedUserID,
                            IsDefault=IsDefault,
                        )
            # ================creating defult Master Type ends here================

            # ================creating defult Price Category starts here================
            THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(
                THIS_FOLDER, 'company_fixtures/price_category.json')

            # path = 'main/fixtures/price_category.json'
            with open(path, 'r+') as json_file:
                json_data = json_file.read()
                dic = json.loads(json_data)
                # name = dic[0]['fields']['GroupName']
                CompanyID = company.id
                CompanyID = get_company(CompanyID)
                for i in dic:
                    if i['model'] == "brands.PriceCategory":
                        PriceCategoryID = i['fields']['PriceCategoryID']
                        BranchID = i['fields']['BranchID']
                        PriceCategoryName = i['fields']['PriceCategoryName']
                        ColumnName = i['fields']['ColumnName']
                        IsActive = i['fields']['IsActive']
                        Notes = i['fields']['Notes']
                        CreatedUserID = i['fields']['CreatedUserID']
                        CreatedDate = i['fields']['CreatedDate']
                        Action = i['fields']['Action']

                        PriceCategory.objects.create(
                            CompanyID=CompanyID,
                            PriceCategoryID=PriceCategoryID,
                            BranchID=BranchID,
                            PriceCategoryName=PriceCategoryName,
                            ColumnName=ColumnName,
                            IsActive=IsActive,
                            Notes=Notes,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=CreatedDate,
                            Action=Action,
                        )
            # ================creating defult Price Category ends here================

            # ================creating defult Price Category starts here================
            THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(
                THIS_FOLDER, 'company_fixtures/product_category.json')

            # path = 'main/fixtures/price_category.json'
            with open(path, 'r+') as json_file:
                json_data = json_file.read()
                dic = json.loads(json_data)
                # name = dic[0]['fields']['GroupName']
                CompanyID = company.id
                CompanyID = get_company(CompanyID)
                for i in dic:
                    if i['model'] == "brands.PriceCategory":
                        PriceCategoryID = i['fields']['PriceCategoryID']
                        BranchID = i['fields']['BranchID']
                        PriceCategoryName = i['fields']['PriceCategoryName']
                        ColumnName = i['fields']['ColumnName']
                        IsActive = i['fields']['IsActive']
                        Notes = i['fields']['Notes']
                        CreatedUserID = i['fields']['CreatedUserID']
                        CreatedDate = i['fields']['CreatedDate']
                        Action = i['fields']['Action']

                        PriceCategory.objects.create(
                            CompanyID=CompanyID,
                            PriceCategoryID=PriceCategoryID,
                            BranchID=BranchID,
                            PriceCategoryName=PriceCategoryName,
                            ColumnName=ColumnName,
                            IsActive=IsActive,
                            Notes=Notes,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=CreatedDate,
                            Action=Action,
                        )
            # ================creating defult Price Category ends here================

            # ================creating defult Price Category starts here================
            THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(
                THIS_FOLDER, 'company_fixtures/product_category.json')

            # path = 'main/fixtures/product_category.json'
            with open(path, 'r+') as json_file:
                json_data = json_file.read()
                dic = json.loads(json_data)
                # name = dic[0]['fields']['GroupName']
                CompanyID = company.id
                CompanyID = get_company(CompanyID)
                for i in dic:
                    if i['model'] == "brands.ProductCategory":
                        ProductCategoryID = i['fields']['ProductCategoryID']
                        BranchID = i['fields']['BranchID']
                        CategoryName = i['fields']['CategoryName']
                        Notes = i['fields']['Notes']
                        CreatedUserID = i['fields']['CreatedUserID']
                        CreatedDate = i['fields']['CreatedDate']
                        Action = i['fields']['Action']

                        ProductCategory.objects.create(
                            CompanyID=CompanyID,
                            ProductCategoryID=ProductCategoryID,
                            BranchID=BranchID,
                            CategoryName=CategoryName,
                            Notes=Notes,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=CreatedDate,
                            Action=Action,
                        )
            # ================creating defult Price Category ends here================

            # ================creating defult Product Group starts here================
            THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(
                THIS_FOLDER, 'company_fixtures/product_group.json')

            # path = 'main/fixtures/product_group.json'
            with open(path, 'r+') as json_file:
                json_data = json_file.read()
                dic = json.loads(json_data)
                # name = dic[0]['fields']['GroupName']
                CompanyID = company.id
                CompanyID = get_company(CompanyID)
                for i in dic:
                    if i['model'] == "brands.ProductGroup":
                        ProductGroupID = i['fields']['ProductGroupID']
                        BranchID = i['fields']['BranchID']
                        GroupName = i['fields']['GroupName']
                        CategoryID = i['fields']['CategoryID']
                        Notes = i['fields']['Notes']
                        CreatedUserID = i['fields']['CreatedUserID']
                        CreatedDate = i['fields']['CreatedDate']
                        Action = i['fields']['Action']

                        ProductGroup.objects.create(
                            CompanyID=CompanyID,
                            ProductGroupID=ProductGroupID,
                            BranchID=BranchID,
                            GroupName=GroupName,
                            CategoryID=CategoryID,
                            Notes=Notes,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=CreatedDate,
                            Action=Action,
                        )
            # ================creating defult Product Group ends here================

            # ================creating defult Route starts here================
            THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(THIS_FOLDER, 'company_fixtures/routes.json')

            # path = 'main/fixtures/routes.json'
            with open(path, 'r+') as json_file:
                json_data = json_file.read()
                dic = json.loads(json_data)
                # name = dic[0]['fields']['GroupName']
                CompanyID = company.id
                CompanyID = get_company(CompanyID)
                for i in dic:
                    if i['model'] == "brands.Route":
                        RouteID = i['fields']['RouteID']
                        BranchID = i['fields']['BranchID']
                        RouteName = i['fields']['RouteName']
                        Notes = i['fields']['Notes']
                        CreatedUserID = i['fields']['CreatedUserID']
                        CreatedDate = i['fields']['CreatedDate']
                        Action = i['fields']['Action']

                        Route.objects.create(
                            CompanyID=CompanyID,
                            RouteID=RouteID,
                            BranchID=BranchID,
                            RouteName=RouteName,
                            Notes=Notes,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=CreatedDate,
                            Action=Action,
                        )
            # ================creating defult Route ends here================

            # ================creating defult TaxCategory starts here================
            THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(
                THIS_FOLDER, 'company_fixtures/tax_categories.json')

            # path = 'main/fixtures/tax_categories.json'
            with open(path, 'r+') as json_file:
                json_data = json_file.read()
                dic = json.loads(json_data)
                # name = dic[0]['fields']['GroupName']
                CompanyID = company.id
                CompanyID = get_company(CompanyID)
                for i in dic:
                    if i['model'] == "brands.TaxCategory":
                        TaxID = i['fields']['TaxID']
                        BranchID = i['fields']['BranchID']
                        TaxName = i['fields']['TaxName']
                        TaxTypes = i['fields']['TaxType']
                        PurchaseTax = i['fields']['PurchaseTax']
                        SalesTax = i['fields']['SalesTax']
                        Inclusive = i['fields']['Inclusive']
                        CreatedUserID = i['fields']['CreatedUserID']
                        CreatedDate = i['fields']['CreatedDate']
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
                            CreatedDate=CreatedDate,
                            Action=Action,
                        )
            # ================creating defult TaxCategory ends here================

            # ================creating defult TaxType starts here================
            THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(THIS_FOLDER, 'company_fixtures/tax_types.json')

            # path = 'main/fixtures/tax_types.json'
            with open(path, 'r+') as json_file:
                json_data = json_file.read()
                dic = json.loads(json_data)
                # name = dic[0]['fields']['GroupName']
                CompanyID = company.id
                CompanyID = get_company(CompanyID)
                for i in dic:
                    if i['model'] == "brands.TaxType":
                        TaxTypeID = i['fields']['TaxTypeID']
                        BranchID = i['fields']['BranchID']
                        TaxTypeName = i['fields']['TaxTypeName']
                        Active = i['fields']['Active']

                        TaxType.objects.create(
                            CompanyID=CompanyID,
                            TaxTypeID=TaxTypeID,
                            BranchID=BranchID,
                            TaxTypeName=TaxTypeName,
                            Active=Active,
                        )
            # ================creating defult TaxType ends here================

            # # ================creating defult Countries starts here================
            # THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
            # path = os.path.join(THIS_FOLDER, 'company_fixtures/countries.json')

            # # path = 'main/fixtures/countries.json'
            # with open(path,'r+') as json_file:
            #     json_data = json_file.read()
            #     dic = json.loads(json_data)
            #     # name = dic[0]['fields']['GroupName']
            #     CompanyID = company.id
            #     CompanyID = get_company(CompanyID)
            #     for i in dic:
            #         if i['model']== "brands.Country":
            #             CountryID = i['fields']['CountryID']
            #             CountryCode = i['fields']['CountryCode']
            #             Currency_Name = i['fields']['Currency_Name']
            #             Currency_Description = i['fields']['Currency_Description']
            #             Change = i['fields']['Change']
            #             Symbol = i['fields']['Symbol']
            #             FractionalUnits = i['fields']['FractionalUnits']
            #             CurrencySymbolUnicode = i['fields']['CurrencySymbolUnicode']
            #             Country_Name = i['fields']['Country_Name']
            #             Country_Description = i['fields']['Country_Description']
            #             ISD_Code = i['fields']['ISD_Code']

            #             Country.objects.create(
            #                 CompanyID = CompanyID,
            #                 CountryID = CountryID,
            #                 CountryCode = CountryCode,
            #                 Currency_Name = Currency_Name,
            #                 Currency_Description = Currency_Description,
            #                 Change = Change,
            #                 Symbol = Symbol,
            #                 FractionalUnits = FractionalUnits,
            #                 CurrencySymbolUnicode = CurrencySymbolUnicode,
            #                 Country_Name = Country_Name,
            #                 Country_Description = Country_Description,
            #                 ISD_Code = ISD_Code,
            #             )
            # # ================creating defult Countries ends here================

            # ================creating defult Unit starts here================
            THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(THIS_FOLDER, 'company_fixtures/unit.json')

            # path = 'main/fixtures/banks.json'
            with open(path, 'r+') as json_file:
                json_data = json_file.read()
                dic = json.loads(json_data)
                # name = dic[0]['fields']['GroupName']
                CompanyID = company.id
                CompanyID = get_company(CompanyID)
                for i in dic:
                    if i['model'] == "brands.Unit":
                        UnitID = i['fields']['UnitID']
                        BranchID = i['fields']['BranchID']
                        UnitName = i['fields']['UnitName']
                        Notes = i['fields']['Notes']
                        CreatedUserID = i['fields']['CreatedUserID']
                        CreatedDate = i['fields']['CreatedDate']
                        Unit.objects.create(
                            CompanyID=CompanyID,
                            UnitID=UnitID,
                            BranchID=BranchID,
                            UnitName=UnitName,
                            Notes=Notes,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=CreatedDate,
                        )
            # ================creating defult Unit ends here================

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "id": company.id
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            response_data = {
                "StatusCode": 6001,
                "message": "Invalid GSTNumber!!!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_companySettings(request):
    data = request.data
    owner = data['owner']
    CreatedUserID = data['CreatedUserID']
    UpdatedUserID = data['UpdatedUserID']
    CompanyLogo = data['CompanyLogo']
    if CompanyLogo:
        CompanyLogo = CompanyLogo
    else:
        CompanyLogo = None

    today = datetime.datetime.now()
    serialized = CompanySettingsSerializer(data=request.data)

    if serialized.is_valid():
        CompanyName = serialized.data['CompanyName']

        owner = get_object_or_404(User.objects.filter(id=owner))
        Address1 = serialized.data['Address1']
        Address2 = serialized.data['Address2']
        Address3 = serialized.data['Address3']
        City = serialized.data['City']
        State = serialized.data['State']
        countries = serialized.data['Country']
        # countries = get_object_or_404(Country.objects.filter(id=countries))
        PostalCode = serialized.data['PostalCode']
        Phone = serialized.data['Phone']
        Mobile = serialized.data['Mobile']
        Email = serialized.data['Email']
        Website = serialized.data['Website']
        Currency = serialized.data['Currency']
        FractionalUnit = serialized.data['FractionalUnit']
        VATNumber = serialized.data['VATNumber']
        GSTNumber = serialized.data['GSTNumber']
        Tax1 = serialized.data['Tax1']
        Tax2 = serialized.data['Tax2']
        Tax3 = serialized.data['Tax3']
        Action = 'A'

        company = CompanySettings.objects.create(
            owner=owner,
            CompanyName=CompanyName,
            CompanyLogo=CompanyLogo,
            Address1=Address1,
            Address2=Address2,
            Address3=Address3,
            City=City,
            State=State,
            Country=countries,
            PostalCode=PostalCode,
            Phone=Phone,
            Mobile=Mobile,
            Email=Email,
            Website=Website,
            Currency=Currency,
            FractionalUnit=FractionalUnit,
            VATNumber=VATNumber,
            GSTNumber=GSTNumber,
            Tax1=Tax1,
            Tax2=Tax2,
            Tax3=Tax3,
            Action=Action,
            CreatedUserID=CreatedUserID,
            UpdatedUserID=UpdatedUserID,
        )

        CompanySettings_Log.objects.create(
            owner=owner,
            TransactionID=company.id,
            CompanyName=CompanyName,
            CompanyLogo=CompanyLogo,
            Address1=Address1,
            Address2=Address2,
            Address3=Address3,
            City=City,
            State=State,
            Country=countries,
            PostalCode=PostalCode,
            Phone=Phone,
            Mobile=Mobile,
            Email=Email,
            Website=Website,
            Currency=Currency,
            FractionalUnit=FractionalUnit,
            VATNumber=VATNumber,
            GSTNumber=GSTNumber,
            Tax1=Tax1,
            Tax2=Tax2,
            Tax3=Tax3,
            CreatedDate=today,
            Action=Action,
            CreatedUserID=CreatedUserID,
            UpdatedUserID=UpdatedUserID,
            UpdatedDate=today
        )

        # ================creating defult Designation starts here================
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(THIS_FOLDER, 'company_fixtures/designations.json')

        # path = 'main/fixtures/account_groups.json'
        with open(path, 'r+') as json_file:
            json_data = json_file.read()
            dic = json.loads(json_data)
            # name = dic[0]['fields']['GroupName']
            CompanyID = company.id
            CompanyID = get_company(CompanyID)
            for i in dic:
                if i['model'] == "brands.Designation":
                    DesignationID = i['fields']['DesignationID']
                    BranchID = i['fields']['BranchID']
                    DesignationName = i['fields']['DesignationName']
                    ShortName = i['fields']['ShortName']
                    DesignationUnder = i['fields']['DesignationUnder']
                    Notes = i['fields']['Notes']
                    CreatedUserID = i['fields']['CreatedUserID']
                    CreatedDate = i['fields']['CreatedDate']
                    UpdatedDate = i['fields']['UpdatedDate']
                    Action = i['fields']['Action']
                    Designation.objects.create(
                        CompanyID=CompanyID,
                        DesignationID=DesignationID,
                        BranchID=BranchID,
                        DesignationName=DesignationName,
                        ShortName=ShortName,
                        DesignationUnder=DesignationUnder,
                        Notes=Notes,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        Action=Action,
                    )
        # ================creating defult Designation ends here================

        # ================creating defult Department starts here================
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(THIS_FOLDER, 'company_fixtures/departments.json')

        # path = 'main/fixtures/account_groups.json'
        with open(path, 'r+') as json_file:
            json_data = json_file.read()
            dic = json.loads(json_data)
            # name = dic[0]['fields']['GroupName']
            CompanyID = company.id
            CompanyID = get_company(CompanyID)
            for i in dic:
                if i['model'] == "brands.Department":
                    DepartmentID = i['fields']['DepartmentID']
                    BranchID = i['fields']['BranchID']
                    DepartmentName = i['fields']['DepartmentName']
                    Notes = i['fields']['Notes']
                    CreatedUserID = i['fields']['CreatedUserID']
                    CreatedDate = i['fields']['CreatedDate']
                    UpdatedDate = i['fields']['UpdatedDate']
                    Action = i['fields']['Action']
                    Department.objects.create(
                        CompanyID=CompanyID,
                        DepartmentID=DepartmentID,
                        BranchID=BranchID,
                        DepartmentName=DepartmentName,
                        Notes=Notes,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        Action=Action,
                    )
        # ================creating defult Department ends here================

        # ================creating defult Account Ledger starts here================
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(
            THIS_FOLDER, 'company_fixtures/account_ledgers.json')

        # path = 'main/fixtures/account_groups.json'
        with open(path, 'r+') as json_file:
            json_data = json_file.read()
            dic = json.loads(json_data)
            # name = dic[0]['fields']['GroupName']
            CompanyID = company.id
            CompanyID = get_company(CompanyID)
            for i in dic:
                if i['model'] == "brands.AccountLedger":
                    LedgerID = i['fields']['LedgerID']
                    BranchID = i['fields']['BranchID']
                    LedgerName = i['fields']['LedgerName']
                    LedgerCode = i['fields']['LedgerCode']
                    AccountGroupUnder = i['fields']['AccountGroupUnder']
                    OpeningBalance = i['fields']['OpeningBalance']
                    CrOrDr = i['fields']['CrOrDr']
                    Notes = i['fields']['Notes']
                    IsActive = i['fields']['IsActive']
                    IsDefault = i['fields']['IsDefault']
                    CreatedUserID = i['fields']['CreatedUserID']
                    CreatedDate = i['fields']['CreatedDate']
                    UpdatedDate = i['fields']['UpdatedDate']
                    Action = i['fields']['Action']
                    AccountLedger.objects.create(
                        CompanyID=CompanyID,
                        LedgerID=LedgerID,
                        BranchID=BranchID,
                        LedgerName=LedgerName,
                        LedgerCode=LedgerCode,
                        AccountGroupUnder=AccountGroupUnder,
                        OpeningBalance=OpeningBalance,
                        CrOrDr=CrOrDr,
                        Notes=Notes,
                        IsActive=IsActive,
                        IsDefault=IsDefault,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        Action=Action,
                    )
        # ================creating defult Account Ledger ends here================

        # ================creating defult Transaction Types starts here================
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(
            THIS_FOLDER, 'company_fixtures/transaction_types.json')

        # path = 'main/fixtures/account_groups.json'
        with open(path, 'r+') as json_file:
            json_data = json_file.read()
            dic = json.loads(json_data)
            # name = dic[0]['fields']['GroupName']
            CompanyID = company.id
            CompanyID = get_company(CompanyID)
            for i in dic:
                if i['model'] == "brands.TransactionTypes":
                    TransactionTypesID = i['fields']['TransactionTypesID']
                    BranchID = i['fields']['BranchID']
                    Action = i['fields']['Action']
                    MasterTypeID = i['fields']['MasterTypeID']
                    Name = i['fields']['Name']
                    Notes = i['fields']['Notes']
                    CreatedDate = i['fields']['CreatedDate']
                    UpdatedDate = i['fields']['UpdatedDate']
                    CreatedUserID = i['fields']['CreatedUserID']
                    IsDefault = i['fields']['IsDefault']
                    TransactionTypes.objects.create(
                        CompanyID=CompanyID,
                        TransactionTypesID=TransactionTypesID,
                        BranchID=BranchID,
                        Action=Action,
                        MasterTypeID=MasterTypeID,
                        Name=Name,
                        Notes=Notes,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CreatedUserID=CreatedUserID,
                        IsDefault=IsDefault,
                    )
        # ================creating defult Transaction Types ends here================

        # ================creating defult Warehouse starts here================
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(THIS_FOLDER, 'company_fixtures/warehouses.json')

        # path = 'main/fixtures/account_groups.json'
        with open(path, 'r+') as json_file:
            json_data = json_file.read()
            dic = json.loads(json_data)
            # name = dic[0]['fields']['GroupName']
            CompanyID = company.id
            CompanyID = get_company(CompanyID)
            for i in dic:
                if i['model'] == "brands.Warehouse":
                    WarehouseID = i['fields']['WarehouseID']
                    BranchID = i['fields']['BranchID']
                    WarehouseName = i['fields']['WarehouseName']
                    Notes = i['fields']['Notes']
                    CreatedUserID = i['fields']['CreatedUserID']
                    CreatedDate = i['fields']['CreatedDate']
                    UpdatedDate = i['fields']['UpdatedDate']
                    Action = i['fields']['Action']
                    Warehouse.objects.create(
                        CompanyID=CompanyID,
                        WarehouseID=WarehouseID,
                        BranchID=BranchID,
                        WarehouseName=WarehouseName,
                        Notes=Notes,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        Action=Action,
                    )
            # ================creating defult Warehouse ends here================

        # ================creating defult UserType starts here================
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(THIS_FOLDER, 'company_fixtures/user_types.json')

        # path = 'main/fixtures/account_groups.json'
        with open(path, 'r+') as json_file:
            json_data = json_file.read()
            dic = json.loads(json_data)
            # name = dic[0]['fields']['GroupName']
            CompanyID = company.id
            CompanyID = get_company(CompanyID)
            for i in dic:
                if i['model'] == "brands.UserType":
                    ID = i['fields']['ID']
                    UserTypeName = i['fields']['UserTypeName']
                    BranchID = i['fields']['BranchID']
                    Notes = i['fields']['Notes']
                    CreatedUserID = i['fields']['CreatedUserID']
                    CreatedDate = i['fields']['CreatedDate']
                    UpdatedDate = i['fields']['UpdatedDate']
                    Action = i['fields']['Action']
                    IsActive = i['fields']['IsActive']
                    UserType.objects.create(
                        CompanyID=CompanyID,
                        ID=ID,
                        UserTypeName=UserTypeName,
                        BranchID=BranchID,
                        Notes=Notes,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        Action=Action,
                        IsActive=IsActive,
                    )
        # ================creating defult UserType ends here================

        # ================creating defult Account Groups starts here================
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(
            THIS_FOLDER, 'company_fixtures/account_groups.json')

        # path = 'main/fixtures/account_groups.json'
        with open(path, 'r+') as json_file:
            json_data = json_file.read()
            dic = json.loads(json_data)
            # name = dic[0]['fields']['GroupName']
            CompanyID = company.id
            CompanyID = get_company(CompanyID)
            for i in dic:
                if i['model'] == "brands.AccountGroup":
                    AccountGroupID = i['fields']['AccountGroupID']
                    AccountGroupName = i['fields']['AccountGroupName']
                    GroupCode = i['fields']['GroupCode']
                    AccountGroupUnder = i['fields']['AccountGroupUnder']
                    Notes = i['fields']['Notes']
                    CreatedUserID = i['fields']['CreatedUserID']
                    CreatedDate = i['fields']['CreatedDate']
                    UpdatedDate = i['fields']['UpdatedDate']
                    IsActive = i['fields']['IsActive']
                    IsDefault = i['fields']['IsDefault']
                    Action = i['fields']['Action']
                    AccountGroup.objects.create(
                        CompanyID=CompanyID,
                        AccountGroupID=AccountGroupID,
                        AccountGroupName=AccountGroupName,
                        GroupCode=GroupCode,
                        AccountGroupUnder=AccountGroupUnder,
                        Notes=Notes,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        IsActive=IsActive,
                        IsDefault=IsDefault,
                        Action=Action,
                    )
        # ================creating defult Account Groups ends here================

        # ================creating defult Banks starts here================
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(THIS_FOLDER, 'company_fixtures/banks.json')

        # path = 'main/fixtures/banks.json'
        with open(path, 'r+') as json_file:
            json_data = json_file.read()
            dic = json.loads(json_data)
            # name = dic[0]['fields']['GroupName']
            CompanyID = company.id
            CompanyID = get_company(CompanyID)
            for i in dic:
                if i['model'] == "brands.Bank":
                    BankID = i['fields']['BankID']
                    BranchID = i['fields']['BranchID']
                    Name = i['fields']['Name']
                    LedgerName = i['fields']['LedgerName']
                    LedgerCode = i['fields']['LedgerCode']
                    AccountNumber = i['fields']['AccountNumber']
                    OpeningBalance = i['fields']['OpeningBalance']
                    Notes = i['fields']['Notes']
                    CreatedUserID = i['fields']['CreatedUserID']
                    CreatedDate = i['fields']['CreatedDate']
                    Bank.objects.create(
                        CompanyID=CompanyID,
                        BankID=BankID,
                        BranchID=BranchID,
                        Name=Name,
                        LedgerName=LedgerName,
                        LedgerCode=LedgerCode,
                        AccountNumber=AccountNumber,
                        OpeningBalance=OpeningBalance,
                        Notes=Notes,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                    )
        # ================creating defult Banks ends here================

        # ================creating defult branches starts here================
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(THIS_FOLDER, 'company_fixtures/branches.json')

        # path = 'main/fixtures/banks.json'
        with open(path, 'r+') as json_file:
            json_data = json_file.read()
            dic = json.loads(json_data)
            # name = dic[0]['fields']['GroupName']
            CompanyID = company.id
            CompanyID = get_company(CompanyID)
            for i in dic:
                if i['model'] == "brands.Branch":
                    BranchID = i['fields']['BranchID']
                    BranchName = i['fields']['BranchName']
                    BranchLocation = i['fields']['BranchLocation']
                    CreatedUserID = i['fields']['CreatedUserID']
                    CreatedDate = i['fields']['CreatedDate']
                    Action = i['fields']['Action']
                    Branch.objects.create(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        BranchName=BranchName,
                        BranchLocation=BranchLocation,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        Action=Action,
                    )
        # ================creating defult branches ends here================

        # ================creating defult brands starts here================
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(THIS_FOLDER, 'company_fixtures/brands.json')

        # path = 'main/fixtures/banks.json'
        with open(path, 'r+') as json_file:
            json_data = json_file.read()
            dic = json.loads(json_data)
            # name = dic[0]['fields']['GroupName']
            CompanyID = company.id
            CompanyID = get_company(CompanyID)
            for i in dic:
                if i['model'] == "brands.Brand":
                    BrandID = i['fields']['BrandID']
                    BranchID = i['fields']['BranchID']
                    BrandName = i['fields']['BrandName']
                    Notes = i['fields']['Notes']
                    CreatedUserID = i['fields']['CreatedUserID']
                    CreatedDate = i['fields']['CreatedDate']
                    Action = i['fields']['Action']
                    Brand.objects.create(
                        CompanyID=CompanyID,
                        BrandID=BrandID,
                        BranchID=BranchID,
                        BrandName=BrandName,
                        Notes=Notes,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        Action=Action,
                    )
        # ================creating defult brands ends here================

        # ================creating defult Color starts here================
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(THIS_FOLDER, 'company_fixtures/colors.json')

        # path = 'main/fixtures/colors.json'
        with open(path, 'r+') as json_file:
            json_data = json_file.read()
            dic = json.loads(json_data)
            # name = dic[0]['fields']['GroupName']
            CompanyID = company.id
            CompanyID = get_company(CompanyID)
            for i in dic:
                if i['model'] == "brands.Color":
                    ColorID = i['fields']['ColorID']
                    ColorName = i['fields']['ColorName']
                    ColorValue = i['fields']['ColorValue']
                    Action = i['fields']['Action']

                    Color.objects.create(
                        CompanyID=CompanyID,
                        ColorID=ColorID,
                        ColorName=ColorName,
                        ColorValue=ColorValue,
                        Action=Action,
                    )
        # ================creating defult Color ends here================

        # ================creating defult Flavours starts here================
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(THIS_FOLDER, 'company_fixtures/flavours.json')

        # path = 'main/fixtures/flavours.json'
        with open(path, 'r+') as json_file:
            json_data = json_file.read()
            dic = json.loads(json_data)
            # name = dic[0]['fields']['GroupName']
            CompanyID = company.id
            CompanyID = get_company(CompanyID)
            for i in dic:
                if i['model'] == "brands.Flavours":
                    FlavourID = i['fields']['FlavourID']
                    BranchID = i['fields']['BranchID']
                    FlavourName = i['fields']['FlavourName']
                    BgColor = i['fields']['BgColor']
                    IsActive = i['fields']['IsActive']
                    Action = i['fields']['Action']
                    Flavours.objects.create(
                        CompanyID=CompanyID,
                        FlavourID=FlavourID,
                        BranchID=BranchID,
                        FlavourName=FlavourName,
                        BgColor=BgColor,
                        IsActive=IsActive,
                        Action=Action,
                    )

        # ================creating defult Flavours ends here================

        # ================creating defult General Settings starts here================
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(
            THIS_FOLDER, 'company_fixtures/general_settings.json')

        # path = 'main/fixtures/general_settings.json'
        with open(path, 'r+') as json_file:
            json_data = json_file.read()
            dic = json.loads(json_data)
            # name = dic[0]['fields']['GroupName']
            CompanyID = company.id
            CompanyID = get_company(CompanyID)
            for i in dic:
                if i['model'] == "brands.GeneralSettings":
                    GeneralSettingsID = i['fields']['GeneralSettingsID']
                    BranchID = i['fields']['BranchID']
                    GroupName = i['fields']['GroupName']
                    SettingsType = i['fields']['SettingsType']
                    SettingsValue = i['fields']['SettingsValue']
                    Action = i['fields']['Action']
                    CreatedDate = i['fields']['CreatedDate']
                    UpdatedDate = i['fields']['UpdatedDate']
                    CreatedUserID = i['fields']['CreatedUserID']

                    GeneralSettings.objects.create(
                        CompanyID=CompanyID,
                        GeneralSettingsID=GeneralSettingsID,
                        BranchID=BranchID,
                        GroupName=GroupName,
                        SettingsType=SettingsType,
                        SettingsValue=SettingsValue,
                        Action=Action,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CreatedUserID=CreatedUserID,
                    )
        # ================creating defult General Settings ends here================

        # ================creating defult Master Type starts here================
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(THIS_FOLDER, 'company_fixtures/master_types.json')

        # path = 'main/fixtures/master_types.json'
        with open(path, 'r+') as json_file:
            json_data = json_file.read()
            dic = json.loads(json_data)
            # name = dic[0]['fields']['GroupName']
            CompanyID = company.id
            CompanyID = get_company(CompanyID)
            for i in dic:
                if i['model'] == "brands.MasterType":
                    MasterTypeID = i['fields']['MasterTypeID']
                    BranchID = i['fields']['BranchID']
                    Name = i['fields']['Name']
                    Description = i['fields']['Description']
                    CreatedUserID = i['fields']['CreatedUserID']
                    IsDefault = i['fields']['IsDefault']

                    MasterType.objects.create(
                        CompanyID=CompanyID,
                        MasterTypeID=MasterTypeID,
                        BranchID=BranchID,
                        Name=Name,
                        Description=Description,
                        CreatedUserID=CreatedUserID,
                        IsDefault=IsDefault,
                    )
        # ================creating defult Master Type ends here================

        # ================creating defult Price Category starts here================
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(
            THIS_FOLDER, 'company_fixtures/price_category.json')

        # path = 'main/fixtures/price_category.json'
        with open(path, 'r+') as json_file:
            json_data = json_file.read()
            dic = json.loads(json_data)
            # name = dic[0]['fields']['GroupName']
            CompanyID = company.id
            CompanyID = get_company(CompanyID)
            for i in dic:
                if i['model'] == "brands.PriceCategory":
                    PriceCategoryID = i['fields']['PriceCategoryID']
                    BranchID = i['fields']['BranchID']
                    PriceCategoryName = i['fields']['PriceCategoryName']
                    ColumnName = i['fields']['ColumnName']
                    IsActive = i['fields']['IsActive']
                    Notes = i['fields']['Notes']
                    CreatedUserID = i['fields']['CreatedUserID']
                    CreatedDate = i['fields']['CreatedDate']
                    Action = i['fields']['Action']

                    PriceCategory.objects.create(
                        CompanyID=CompanyID,
                        PriceCategoryID=PriceCategoryID,
                        BranchID=BranchID,
                        PriceCategoryName=PriceCategoryName,
                        ColumnName=ColumnName,
                        IsActive=IsActive,
                        Notes=Notes,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        Action=Action,
                    )
        # ================creating defult Price Category ends here================

        # ================creating defult Price Category starts here================
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(
            THIS_FOLDER, 'company_fixtures/product_category.json')

        # path = 'main/fixtures/product_category.json'
        with open(path, 'r+') as json_file:
            json_data = json_file.read()
            dic = json.loads(json_data)
            # name = dic[0]['fields']['GroupName']
            CompanyID = company.id
            CompanyID = get_company(CompanyID)
            for i in dic:
                if i['model'] == "brands.ProductCategory":
                    ProductCategoryID = i['fields']['ProductCategoryID']
                    BranchID = i['fields']['BranchID']
                    CategoryName = i['fields']['CategoryName']
                    Notes = i['fields']['Notes']
                    CreatedUserID = i['fields']['CreatedUserID']
                    CreatedDate = i['fields']['CreatedDate']
                    Action = i['fields']['Action']

                    ProductCategory.objects.create(
                        CompanyID=CompanyID,
                        ProductCategoryID=ProductCategoryID,
                        BranchID=BranchID,
                        CategoryName=CategoryName,
                        Notes=Notes,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        Action=Action,
                    )
        # ================creating defult Price Category ends here================

        # ================creating defult Product Group starts here================
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(THIS_FOLDER, 'company_fixtures/product_group.json')

        # path = 'main/fixtures/product_group.json'
        with open(path, 'r+') as json_file:
            json_data = json_file.read()
            dic = json.loads(json_data)
            # name = dic[0]['fields']['GroupName']
            CompanyID = company.id
            CompanyID = get_company(CompanyID)
            for i in dic:
                if i['model'] == "brands.ProductGroup":
                    ProductGroupID = i['fields']['ProductGroupID']
                    BranchID = i['fields']['BranchID']
                    GroupName = i['fields']['GroupName']
                    CategoryID = i['fields']['CategoryID']
                    Notes = i['fields']['Notes']
                    CreatedUserID = i['fields']['CreatedUserID']
                    CreatedDate = i['fields']['CreatedDate']
                    Action = i['fields']['Action']

                    ProductGroup.objects.create(
                        CompanyID=CompanyID,
                        ProductGroupID=ProductGroupID,
                        BranchID=BranchID,
                        GroupName=GroupName,
                        CategoryID=CategoryID,
                        Notes=Notes,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        Action=Action,
                    )
        # ================creating defult Product Group ends here================

        # ================creating defult Route starts here================
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(THIS_FOLDER, 'company_fixtures/routes.json')

        # path = 'main/fixtures/routes.json'
        with open(path, 'r+') as json_file:
            json_data = json_file.read()
            dic = json.loads(json_data)
            # name = dic[0]['fields']['GroupName']
            CompanyID = company.id
            CompanyID = get_company(CompanyID)
            for i in dic:
                if i['model'] == "brands.Route":
                    RouteID = i['fields']['RouteID']
                    BranchID = i['fields']['BranchID']
                    RouteName = i['fields']['RouteName']
                    Notes = i['fields']['Notes']
                    CreatedUserID = i['fields']['CreatedUserID']
                    CreatedDate = i['fields']['CreatedDate']
                    Action = i['fields']['Action']

                    Route.objects.create(
                        CompanyID=CompanyID,
                        RouteID=RouteID,
                        BranchID=BranchID,
                        RouteName=RouteName,
                        Notes=Notes,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        Action=Action,
                    )
        # ================creating defult Route ends here================

        # ================creating defult TaxCategory starts here================
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(
            THIS_FOLDER, 'company_fixtures/tax_categories.json')

        # path = 'main/fixtures/tax_categories.json'
        with open(path, 'r+') as json_file:
            json_data = json_file.read()
            dic = json.loads(json_data)
            # name = dic[0]['fields']['GroupName']
            CompanyID = company.id
            CompanyID = get_company(CompanyID)
            for i in dic:
                if i['model'] == "brands.TaxCategory":
                    TaxID = i['fields']['TaxID']
                    BranchID = i['fields']['BranchID']
                    TaxName = i['fields']['TaxName']
                    TaxTypes = i['fields']['TaxType']
                    PurchaseTax = i['fields']['PurchaseTax']
                    SalesTax = i['fields']['SalesTax']
                    Inclusive = i['fields']['Inclusive']
                    CreatedUserID = i['fields']['CreatedUserID']
                    CreatedDate = i['fields']['CreatedDate']
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
                        CreatedDate=CreatedDate,
                        Action=Action,
                    )
        # ================creating defult TaxCategory ends here================

        # ================creating defult TaxType starts here================
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(THIS_FOLDER, 'company_fixtures/tax_types.json')

        # path = 'main/fixtures/tax_types.json'
        with open(path, 'r+') as json_file:
            json_data = json_file.read()
            dic = json.loads(json_data)
            # name = dic[0]['fields']['GroupName']
            CompanyID = company.id
            CompanyID = get_company(CompanyID)
            for i in dic:
                if i['model'] == "brands.TaxType":
                    TaxTypeID = i['fields']['TaxTypeID']
                    BranchID = i['fields']['BranchID']
                    TaxTypeName = i['fields']['TaxTypeName']
                    Active = i['fields']['Active']

                    TaxType.objects.create(
                        CompanyID=CompanyID,
                        TaxTypeID=TaxTypeID,
                        BranchID=BranchID,
                        TaxTypeName=TaxTypeName,
                        Active=Active,
                    )
        # ================creating defult TaxType ends here================

        # # ================creating defult Countries starts here================
        # THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        # path = os.path.join(THIS_FOLDER, 'company_fixtures/countries.json')

        # # path = 'main/fixtures/countries.json'
        # with open(path,'r+') as json_file:
        #     json_data = json_file.read()
        #     dic = json.loads(json_data)
        #     # name = dic[0]['fields']['GroupName']
        #     CompanyID = company.id
        #     CompanyID = get_company(CompanyID)
        #     for i in dic:
        #         if i['model']== "brands.Country":
        #             CountryID = i['fields']['CountryID']
        #             CountryCode = i['fields']['CountryCode']
        #             Currency_Name = i['fields']['Currency_Name']
        #             Currency_Description = i['fields']['Currency_Description']
        #             Change = i['fields']['Change']
        #             Symbol = i['fields']['Symbol']
        #             FractionalUnits = i['fields']['FractionalUnits']
        #             CurrencySymbolUnicode = i['fields']['CurrencySymbolUnicode']
        #             Country_Name = i['fields']['Country_Name']
        #             Country_Description = i['fields']['Country_Description']
        #             ISD_Code = i['fields']['ISD_Code']

        #             Country.objects.create(
        #                 CompanyID = CompanyID,
        #                 CountryID = CountryID,
        #                 CountryCode = CountryCode,
        #                 Currency_Name = Currency_Name,
        #                 Currency_Description = Currency_Description,
        #                 Change = Change,
        #                 Symbol = Symbol,
        #                 FractionalUnits = FractionalUnits,
        #                 CurrencySymbolUnicode = CurrencySymbolUnicode,
        #                 Country_Name = Country_Name,
        #                 Country_Description = Country_Description,
        #                 ISD_Code = ISD_Code,
        #             )
        # # ================creating defult Countries ends here================

        # ================creating defult Unit starts here================
        THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(THIS_FOLDER, 'company_fixtures/unit.json')

        # path = 'main/fixtures/banks.json'
        with open(path, 'r+') as json_file:
            json_data = json_file.read()
            dic = json.loads(json_data)
            # name = dic[0]['fields']['GroupName']
            CompanyID = company.id
            CompanyID = get_company(CompanyID)
            for i in dic:
                if i['model'] == "brands.Unit":
                    UnitID = i['fields']['UnitID']
                    BranchID = i['fields']['BranchID']
                    UnitName = i['fields']['UnitName']
                    Notes = i['fields']['Notes']
                    CreatedUserID = i['fields']['CreatedUserID']
                    CreatedDate = i['fields']['CreatedDate']
                    Unit.objects.create(
                        CompanyID=CompanyID,
                        UnitID=UnitID,
                        BranchID=BranchID,
                        UnitName=UnitName,
                        Notes=Notes,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                    )
        # ================creating defult Unit ends here================
        # ================creating defult User type settings starts here================
        User = request.user.id
        # arguments order :- User, GroupName, SettingsType, SettingsValue
        # Accounts => Masters
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "AccountGroupView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "AccountGroupSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "AccountGroupEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "AccountGroupDelete", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "AccountLedgerView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "AccountLedgerSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "AccountLedgerEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "AccountLedgerDelete", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "BankView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "BankSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "BankEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "BankDelete", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "CustomerView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "CustomerSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "CustomerEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "CustomerDelete", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "SupplierView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "SupplierSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "SupplierEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "SupplierDelete", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "TransactionTypeView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "TransactionTypeSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "TransactionTypeEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "TransactionTypeDelete", True)

        # Accounts => Transactions
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "BankPaymentDelete", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "BankPaymentEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "BankPaymentSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "BankPaymentView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "BankReceiptDelete", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "BankReceiptEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "BankReceiptSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "BankReceiptView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "CashPaymentDelete", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "CashPaymentEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "CashPaymentSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "CashPaymentView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "CashReceiptDelete", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "CashReceiptEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "CashReceiptSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "CashReceiptView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "JournalEntryDelete", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "JournalEntryEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "JournalEntrySave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "JournalEntryView", True)
        # Accounts => Reports
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "LedgerReportView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "LedgerReportPrint", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "LedgerReportExport", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "TrialBalanceView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "TrialBalancePrint", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "TrialBalanceExport", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "ProfitAndLossView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "ProfitAndLossPrint", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "ProfitAndLossExport", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "BalanceSheetView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "BalanceSheetPrint", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "BalanceSheetExport", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "DailyReportView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "DailyReportPrint", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "DailyReportExport", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "CashBookView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "CashBookPrint", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "CashBookExport", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "VATReportView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "VATReportPrint", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "VATReportExport", True)

        # Inventory => Masters
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductGroupView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductGroupSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductGroupEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductGroupDelete", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "BrandsView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "BrandsSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "BrandsEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "BrandsDelete", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "TaxCategoriesView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "TaxCategoriesSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "TaxCategoriesEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "TaxCategoriesDelete", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "PriceCategoriesView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "PriceCategoriesSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "PriceCategoriesEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "PriceCategoriesDelete", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "WarehouseView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "WarehouseSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "WarehouseEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "WarehouseDelete", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductCategoriesView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductCategoriesSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductCategoriesEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductCategoriesDelete", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductsView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductsSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductsEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductsDelete", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "RoutesView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "RoutesSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "RoutesEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "RoutesDelete", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "UnitsView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "UnitsSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "UnitsEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "UnitsDelete", True)

        # Inventory => Transaction
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "PurchaseInvoicesView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "PurchaseInvoicesSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "PurchaseInvoicesEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "PurchaseInvoicesDelete", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "WorkOrdersView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "WorkOrdersSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "WorkOrdersEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "WorkOrdersDelete", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "PurchaseReturnsView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "PurchaseReturnsSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "PurchaseReturnsEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "PurchaseReturnsDelete", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SaleInvoicesView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SaleInvoicesSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SaleInvoicesEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SaleInvoicesDelete", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SaleReturnsView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SaleReturnsSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SaleReturnsEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SaleReturnsDelete", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "OpeningStockView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "OpeningStockSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "OpeningStockEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "OpeningStockDelete", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "StockTransferView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "StockTransferSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "StockTransferEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "StockTransferDelete", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "ExcessStocksView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "ExcessStocksSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "ExcessStocksEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "ExcessStocksDelete", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "ShortageStocksView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "ShortageStocksSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "ShortageStocksEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "ShortageStocksDelete", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "DamageStocksView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "DamageStocksSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "DamageStocksEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "DamageStocksDelete", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "UsedStocksView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "UsedStocksSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "UsedStocksEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "UsedStocksDelete", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "StockAdjustmentsView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "StockAdjustmentsSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "StockAdjustmentsEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "StockAdjustmentsDelete", True)
        # Inventory => Reports
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "StockReportView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "StockReportPrint", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "StockReportExport", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "StockValueReportView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "StockValueReportPrint", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "StockValueReportExport", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "PurchaseReportView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "PurchaseReportPrint", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "PurchaseReportExport", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "SalesReportView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "SalesReportPrint", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "SalesReportExport", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "SalesIntegratedReportView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "SalesIntegratedReportPrint", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "SalesIntegratedReportExport", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "SalesRegisterReportView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "SalesRegisterReportPrint", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "SalesRegisterReportExport", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "BillWiseReportView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "BillWiseReportPrint", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "BillWiseReportExport", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "ExcessStockReportView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "ExcessStockReportPrint", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "ExcessStockReportExport", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "DamageStockReportView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "DamageStockReportPrint", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "DamageStockReportExport", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "UsedStockReportView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "UsedStockReportPrint", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "UsedStockReportExport", True)
        # Payroll => Masters
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "DepartmentsView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "DepartmentsSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "DepartmentsEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "DepartmentsDelete", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "DesignationsView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "DesignationsSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "DesignationsEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "DesignationsDelete", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "EmployeeView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "EmployeeSave", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "EmployeeEdit", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "EmployeeDelete", True)

        # Settings
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Settings", "PrinterView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Settings", "BarcodeView", True)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Settings", "PrintBarcodeView", True)
        # ================creating defult Unit ends here================

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data,
            "id": company.id
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def edit_companySettings(request):
    data = request.data
    CompanyID = data['CompanyID']
    Email = data['Email']
    # CompanyID = get_company(CompanyID)
    # CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    serialized = CompanySettingsSerializer(data=request.data)
    instance = CompanySettings.objects.get(id=CompanyID)
    CompanyLogo = data['CompanyLogo']
    business_type = data['business_type']
    if CompanyLogo == "":
        CompanyLogo = instance.CompanyLogo

    if BusinessType.objects.filter(pk=business_type).exists():
        print(business_type, "JOOOOuvaisOOOOOOIIIIIIIIII")
        business_type = BusinessType.objects.get(pk=business_type)
    else:
        business_type = instance.business_type
        print(business_type, "NULLLLLLLLLLLLLLL")

    # if business_type == "" or 'null':
    #     business_type = instance.business_type

    # CompanySettingsID = instance.CompanySettingsID

    if serialized.is_valid():
        GSTNumber = serialized.data['GSTNumber']
        try:
            CountryName = data['CountryName']
        except:
            CountryName = ""

        is_Gstn_validate = True
        if GSTNumber:
            if CountryName == "India":
                is_Gstn_validate = False
                print("KAYAR?YYYYYYYYYYYYYYYYYYYYYYYYYYYYY")
                is_Gstn_validate = isValidMasterCardNo(GSTNumber)
        print(is_Gstn_validate, GSTNumber)
        if is_Gstn_validate:

            CompanyName = serialized.data['CompanyName']
            Address1 = serialized.data['Address1']
            Address2 = serialized.data['Address2']
            Address3 = serialized.data['Address3']
            City = serialized.data['City']
            state = serialized.data['State']
            if state == "" or 'null':
                state = instance.State
            else:
                state = State.objects.get(pk=state)
            CountryID = serialized.data['Country']
            Countries = Country.objects.get(id=CountryID)
            PostalCode = serialized.data['PostalCode']
            Phone = serialized.data['Phone']
            # if Phone == 'null':
            #     Phone = None
            # else:
            #     Phone = instance.Phone

            Mobile = serialized.data['Mobile']
            # Email = serialized.data['Email']
            Website = serialized.data['Website']
            # Currency = serialized.data['Currency']
            # FractionalUnit = serialized.data['FractionalUnit']
            VATNumber = serialized.data['VATNumber']
            # GSTNumber = serialized.data['GSTNumber']
            CRNumber = serialized.data['CRNumber']
            CINNumber = serialized.data['CINNumber']
            Description = serialized.data['Description']
            Tax1 = serialized.data['Tax1']
            Tax2 = serialized.data['Tax2']
            Tax3 = serialized.data['Tax3']
            is_vat = serialized.data['is_vat']
            is_gst = serialized.data['is_gst']

            if CRNumber == 'null' or '':
                CRNumber = None
            if CINNumber == 'null' or '':
                CINNumber = None

            if Tax1 == 'null':
                Tax1 = None

            if Tax2 == 'null':
                Tax2 = None

            if Tax3 == 'null':
                Tax3 = None

            Action = 'M'

            instance.CompanyName = CompanyName
            instance.CompanyLogo = CompanyLogo
            instance.Address1 = Address1
            instance.Address2 = Address2
            instance.Address3 = Address3
            instance.City = City
            instance.State = state
            instance.Country = Countries
            instance.PostalCode = PostalCode
            instance.Phone = Phone
            instance.Mobile = Mobile
            instance.Email = Email
            instance.Website = Website
            # instance.Currency = Currency
            # instance.FractionalUnit = FractionalUnit
            instance.VATNumber = VATNumber
            instance.GSTNumber = GSTNumber
            instance.Tax1 = Tax1
            instance.Tax2 = Tax2
            instance.Tax3 = Tax3

            instance.business_type = business_type
            instance.Action = Action
            instance.CRNumber = CRNumber
            instance.CINNumber = CINNumber
            instance.Description = Description
            instance.is_vat = is_vat
            instance.is_gst = is_gst
            # instance.CreatedUserID = CreatedUserID
            instance.save()

            CompanySettings_Log.objects.create(
                TransactionID=CompanyID,
                CompanyName=CompanyName,
                CompanyLogo=instance.CompanyLogo,
                Address1=Address1,
                Address2=Address2,
                Address3=Address3,
                City=City,
                State=state,
                Country=Countries,
                PostalCode=PostalCode,
                Phone=Phone,
                Mobile=Mobile,
                Email=Email,
                Website=Website,
                # Currency=Currency,
                # FractionalUnit=FractionalUnit,
                VATNumber=VATNumber,
                GSTNumber=GSTNumber,
                Tax1=Tax1,
                Tax2=Tax2,
                Tax3=Tax3,
                CreatedDate=today,
                Action=Action,
                CreatedUserID=instance.CreatedUserID,
                business_type=business_type,
                owner=instance.owner,
                CRNumber=CRNumber,
                CINNumber=CINNumber,
                Description=Description,
                is_vat=is_vat,
                is_gst=is_gst,
            )
            # data = {"CompanySettingsID" : CompanySettingsID}
            data = serialized.data
            response_data = {
                "StatusCode": 6000,
                "data": data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            response_data = {
                "StatusCode": 6001,
                "message": "Invalid GSTNumber!!!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def companySettings(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    instance = None

    if CompanySettings.objects.filter(pk=CompanyID.id).exists():
        instance = CompanySettings.objects.get(pk=CompanyID.id)
        serialized = CompanySettingsRestSerializer(
            instance, context={"request": request})
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "CompanySettings Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_companySettings(request, pk):
    data = request.data
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = get_company(pk)

    CompanyName = instance.CompanyName
    CompanyLogo = instance.CompanyLogo
    Address1 = instance.Address1
    Address2 = instance.Address2
    Address3 = instance.Address3
    City = instance.City
    State = instance.State
    PostalCode = instance.PostalCode
    Phone = instance.Phone
    Mobile = instance.Mobile
    Email = instance.Email
    Website = instance.Website
    # Currency = instance.Currency
    # FractionalUnit = instance.FractionalUnit
    VATNumber = instance.VATNumber
    GSTNumber = instance.GSTNumber
    Tax1 = instance.Tax1
    Tax2 = instance.Tax2
    Tax3 = instance.Tax3
    owner = instance.owner
    Action = "D"
    instance.is_deleted = True
    instance.save()

    if UserTable.objects.filter(CompanyID=instance).exists():
        instances = UserTable.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    CompanySettings_Log.objects.create(
        CompanyName=CompanyName,
        CompanyLogo=CompanyLogo,
        Address1=Address1,
        Address2=Address2,
        Address3=Address3,
        City=City,
        State=State,
        PostalCode=PostalCode,
        Phone=Phone,
        Mobile=Mobile,
        Email=Email,
        Website=Website,
        # Currency = Currency,
        # FractionalUnit = FractionalUnit,
        VATNumber=VATNumber,
        GSTNumber=GSTNumber,
        Tax1=Tax1,
        Tax2=Tax2,
        Tax3=Tax3,
        owner=owner,
        Action=Action,
        is_deleted=True
    )

    response_data = {
        "StatusCode": 6000,
        "message": "CompanySettings Deleted Successfully!"
    }
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_companyPermanantly(request, pk):
    from brands import models
    data = request.data
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = get_company(pk)

    CompanyName = instance.CompanyName
    CompanyLogo = instance.CompanyLogo
    Address1 = instance.Address1
    Address2 = instance.Address2
    Address3 = instance.Address3
    City = instance.City
    State = instance.State
    PostalCode = instance.PostalCode
    Phone = instance.Phone
    Mobile = instance.Mobile
    Email = instance.Email
    Website = instance.Website
    # Currency = instance.Currency
    # FractionalUnit = instance.FractionalUnit
    VATNumber = instance.VATNumber
    GSTNumber = instance.GSTNumber
    Tax1 = instance.Tax1
    Tax2 = instance.Tax2
    Tax3 = instance.Tax3
    owner = instance.owner
    Action = "D"
    instance.is_deleted = True
    instance.delete()

    if models.UserType.objects.filter(CompanyID=instance).exists():
        instances = models.UserType.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.UserTypeLog.objects.filter(CompanyID=instance).exists():
        instances = models.UserTypeLog.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.UserTable.objects.filter(CompanyID=instance).exists():
        instances = models.UserTable.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.User_Log.objects.filter(CompanyID=instance).exists():
        instances = models.User_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.Brand.objects.filter(CompanyID=instance).exists():
        instances = models.Brand.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.Brand_Log.objects.filter(CompanyID=instance).exists():
        instances = models.Brand_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.Route.objects.filter(CompanyID=instance).exists():
        instances = models.Route.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.Route_Log.objects.filter(CompanyID=instance).exists():
        instances = models.Route_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.TaxType.objects.filter(CompanyID=instance).exists():
        instances = models.TaxType.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.TaxCategory.objects.filter(CompanyID=instance).exists():
        instances = models.TaxCategory.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.TaxCategory_Log.objects.filter(CompanyID=instance).exists():
        instances = models.TaxCategory_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.ProductCategory.objects.filter(CompanyID=instance).exists():
        instances = models.ProductCategory.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.ProductCategory_Log.objects.filter(CompanyID=instance).exists():
        instances = models.ProductCategory_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.ProductGroup.objects.filter(CompanyID=instance).exists():
        instances = models.ProductGroup.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.ProductGroup_Log.objects.filter(CompanyID=instance).exists():
        instances = models.ProductGroup_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.Warehouse.objects.filter(CompanyID=instance).exists():
        instances = models.Warehouse.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.Warehouse_Log.objects.filter(CompanyID=instance).exists():
        instances = models.Warehouse_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PriceCategory.objects.filter(CompanyID=instance).exists():
        instances = models.PriceCategory.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PriceCategory_Log.objects.filter(CompanyID=instance).exists():
        instances = models.PriceCategory_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.AccountGroup.objects.filter(CompanyID=instance).exists():
        instances = models.AccountGroup.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.AccountGroup_Log.objects.filter(CompanyID=instance).exists():
        instances = models.AccountGroup_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.AccountLedger.objects.filter(CompanyID=instance).exists():
        instances = models.AccountLedger.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.AccountLedger_Log.objects.filter(CompanyID=instance).exists():
        instances = models.AccountLedger_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.Branch.objects.filter(CompanyID=instance).exists():
        instances = models.Branch.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.Branch_Log.objects.filter(CompanyID=instance).exists():
        instances = models.Branch_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.Parties.objects.filter(CompanyID=instance).exists():
        instances = models.Parties.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.Parties_Log.objects.filter(CompanyID=instance).exists():
        instances = models.Parties_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.Product.objects.filter(CompanyID=instance).exists():
        instances = models.Product.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.Product_Log.objects.filter(CompanyID=instance).exists():
        instances = models.Product_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PriceList.objects.filter(CompanyID=instance).exists():
        instances = models.PriceList.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PriceList_Log.objects.filter(CompanyID=instance).exists():
        instances = models.PriceList_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.MasterType.objects.filter(CompanyID=instance).exists():
        instances = models.MasterType.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.MasterType_Log.objects.filter(CompanyID=instance).exists():
        instances = models.MasterType_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.TransactionTypes.objects.filter(CompanyID=instance).exists():
        instances = models.TransactionTypes.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.TransactionTypes_Log.objects.filter(CompanyID=instance).exists():
        instances = models.TransactionTypes_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.Color.objects.filter(CompanyID=instance).exists():
        instances = models.Color.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.Color_Log.objects.filter(CompanyID=instance).exists():
        instances = models.Color_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.GeneralSettings.objects.filter(CompanyID=instance).exists():
        instances = models.GeneralSettings.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.GeneralSettings_Log.objects.filter(CompanyID=instance).exists():
        instances = models.GeneralSettings_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.DamageStockDetails.objects.filter(CompanyID=instance).exists():
        instances = models.DamageStockDetails.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.DamageStockDetails_Log.objects.filter(CompanyID=instance).exists():
        instances = models.DamageStockDetails_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.DamageStockMaster.objects.filter(CompanyID=instance).exists():
        instances = models.DamageStockMaster.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.DamageStockMaster_Log.objects.filter(CompanyID=instance).exists():
        instances = models.DamageStockMaster_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.Designation.objects.filter(CompanyID=instance).exists():
        instances = models.Designation.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.Designation_Log.objects.filter(CompanyID=instance).exists():
        instances = models.Designation_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.Department.objects.filter(CompanyID=instance).exists():
        instances = models.Department.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.Department_Log.objects.filter(CompanyID=instance).exists():
        instances = models.Department_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.Employee.objects.filter(CompanyID=instance).exists():
        instances = models.Employee.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.Employee_Log.objects.filter(CompanyID=instance).exists():
        instances = models.Employee_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.FinancialYear.objects.filter(CompanyID=instance).exists():
        instances = models.FinancialYear.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.FinancialYear_Log.objects.filter(CompanyID=instance).exists():
        instances = models.FinancialYear_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.Flavours.objects.filter(CompanyID=instance).exists():
        instances = models.Flavours.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.Flavours_Log.objects.filter(CompanyID=instance).exists():
        instances = models.Flavours_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.JournalDetails.objects.filter(CompanyID=instance).exists():
        instances = models.JournalDetails.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.JournalDetails_Log.objects.filter(CompanyID=instance).exists():
        instances = models.JournalDetails_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.JournalMaster.objects.filter(CompanyID=instance).exists():
        instances = models.JournalMaster.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.JournalMaster_Log.objects.filter(CompanyID=instance).exists():
        instances = models.JournalMaster_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.Kitchen.objects.filter(CompanyID=instance).exists():
        instances = models.Kitchen.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.Kitchen_Log.objects.filter(CompanyID=instance).exists():
        instances = models.Kitchen_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.LedgerPosting.objects.filter(CompanyID=instance).exists():
        instances = models.LedgerPosting.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.LedgerPosting_Log.objects.filter(CompanyID=instance).exists():
        instances = models.LedgerPosting_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.OpeningStockDetails.objects.filter(CompanyID=instance).exists():
        instances = models.OpeningStockDetails.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.OpeningStockDetails_Log.objects.filter(CompanyID=instance).exists():
        instances = models.OpeningStockDetails_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.OpeningStockMaster.objects.filter(CompanyID=instance).exists():
        instances = models.OpeningStockMaster.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.OpeningStockMaster_Log.objects.filter(CompanyID=instance).exists():
        instances = models.OpeningStockMaster_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PaymentDetails.objects.filter(CompanyID=instance).exists():
        instances = models.PaymentDetails.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PaymentDetails_Log.objects.filter(CompanyID=instance).exists():
        instances = models.PaymentDetails_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PaymentMaster.objects.filter(CompanyID=instance).exists():
        instances = models.PaymentMaster.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PaymentMaster_Log.objects.filter(CompanyID=instance).exists():
        instances = models.PaymentMaster_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.POSHoldDetails.objects.filter(CompanyID=instance).exists():
        instances = models.POSHoldDetails.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.POSHoldDetails_Log.objects.filter(CompanyID=instance).exists():
        instances = models.POSHoldDetails_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.POSHoldMaster.objects.filter(CompanyID=instance).exists():
        instances = models.POSHoldMaster.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.POSHoldMaster_Log.objects.filter(CompanyID=instance).exists():
        instances = models.POSHoldMaster_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PurchaseDetails.objects.filter(CompanyID=instance).exists():
        instances = models.PurchaseDetails.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PurchaseDetails_Log.objects.filter(CompanyID=instance).exists():
        instances = models.PurchaseDetails_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PurchaseMaster.objects.filter(CompanyID=instance).exists():
        instances = models.PurchaseMaster.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PurchaseMaster_Log.objects.filter(CompanyID=instance).exists():
        instances = models.PurchaseMaster_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PurchaseOrderDetails.objects.filter(CompanyID=instance).exists():
        instances = models.PurchaseOrderDetails.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PurchaseOrderDetails_Log.objects.filter(CompanyID=instance).exists():
        instances = models.PurchaseOrderDetails_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PurchaseOrderMaster.objects.filter(CompanyID=instance).exists():
        instances = models.PurchaseOrderMaster.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PurchaseOrderMaster_Log.objects.filter(CompanyID=instance).exists():
        instances = models.PurchaseOrderMaster_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PurchaseReturnDetails.objects.filter(CompanyID=instance).exists():
        instances = models.PurchaseReturnDetails.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PurchaseReturnDetails_Log.objects.filter(CompanyID=instance).exists():
        instances = models.PurchaseReturnDetails_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PurchaseReturnMaster.objects.filter(CompanyID=instance).exists():
        instances = models.PurchaseReturnMaster.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PurchaseReturnMaster_Log.objects.filter(CompanyID=instance).exists():
        instances = models.PurchaseReturnMaster_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.ReceiptDetails.objects.filter(CompanyID=instance).exists():
        instances = models.ReceiptDetails.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.ReceiptDetails_Log.objects.filter(CompanyID=instance).exists():
        instances = models.ReceiptDetails_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.ReceiptMaster.objects.filter(CompanyID=instance).exists():
        instances = models.ReceiptMaster.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.ReceiptMaster_Log.objects.filter(CompanyID=instance).exists():
        instances = models.ReceiptMaster_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.SalesDetails.objects.filter(CompanyID=instance).exists():
        instances = models.SalesDetails.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.SalesDetails_Log.objects.filter(CompanyID=instance).exists():
        instances = models.SalesDetails_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.SalesMaster.objects.filter(CompanyID=instance).exists():
        instances = models.SalesMaster.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.SalesMaster_Log.objects.filter(CompanyID=instance).exists():
        instances = models.SalesMaster_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.SalesOrderDetails.objects.filter(CompanyID=instance).exists():
        instances = models.SalesOrderDetails.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.SalesOrderDetails_Log.objects.filter(CompanyID=instance).exists():
        instances = models.SalesOrderDetails_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.SalesOrderMaster.objects.filter(CompanyID=instance).exists():
        instances = models.SalesOrderMaster.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.SalesOrderMaster_Log.objects.filter(CompanyID=instance).exists():
        instances = models.SalesOrderMaster_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.SalesReturnDetails.objects.filter(CompanyID=instance).exists():
        instances = models.SalesReturnDetails.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.SalesReturnDetails_Log.objects.filter(CompanyID=instance).exists():
        instances = models.SalesReturnDetails_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.SalesReturnMaster.objects.filter(CompanyID=instance).exists():
        instances = models.SalesReturnMaster.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.SalesReturnMaster_Log.objects.filter(CompanyID=instance).exists():
        instances = models.SalesReturnMaster_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.Settings.objects.filter(CompanyID=instance).exists():
        instances = models.Settings.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.Settings_Log.objects.filter(CompanyID=instance).exists():
        instances = models.Settings_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.StockAdjustmentDetails.objects.filter(CompanyID=instance).exists():
        instances = models.StockAdjustmentDetails.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.StockAdjustmentDetails_Log.objects.filter(CompanyID=instance).exists():
        instances = models.StockAdjustmentDetails_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.StockAdjustmentMaster.objects.filter(CompanyID=instance).exists():
        instances = models.StockAdjustmentMaster.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.StockAdjustmentMaster_Log.objects.filter(CompanyID=instance).exists():
        instances = models.StockAdjustmentMaster_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.StockReceiptDetails.objects.filter(CompanyID=instance).exists():
        instances = models.StockReceiptDetails.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.StockReceiptDetails_Log.objects.filter(CompanyID=instance).exists():
        instances = models.StockReceiptDetails_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.StockReceiptMaster_ID.objects.filter(CompanyID=instance).exists():
        instances = models.StockReceiptMaster_ID.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.StockReceiptMasterID_Log.objects.filter(CompanyID=instance).exists():
        instances = models.StockReceiptMasterID_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.StockTransferDetails.objects.filter(CompanyID=instance).exists():
        instances = models.StockTransferDetails.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.StockTransferDetails_Log.objects.filter(CompanyID=instance).exists():
        instances = models.StockTransferDetails_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.StockTransferMaster_ID.objects.filter(CompanyID=instance).exists():
        instances = models.StockTransferMaster_ID.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.StockTransferMasterID_Log.objects.filter(CompanyID=instance).exists():
        instances = models.StockTransferMasterID_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.StockPosting.objects.filter(CompanyID=instance).exists():
        instances = models.StockPosting.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.StockPosting_Log.objects.filter(CompanyID=instance).exists():
        instances = models.StockPosting_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.StockRate.objects.filter(CompanyID=instance).exists():
        instances = models.StockRate.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.StockTrans.objects.filter(CompanyID=instance).exists():
        instances = models.StockTrans.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.Bank.objects.filter(CompanyID=instance).exists():
        instances = models.Bank.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.Bank_Log.objects.filter(CompanyID=instance).exists():
        instances = models.Bank_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.Unit.objects.filter(CompanyID=instance).exists():
        instances = models.Unit.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.Unit_Log.objects.filter(CompanyID=instance).exists():
        instances = models.Unit_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.UserTable.objects.filter(CompanyID=instance).exists():
        instances = models.UserTable.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    CompanySettings_Log.objects.create(
        CompanyName=CompanyName,
        CompanyLogo=CompanyLogo,
        Address1=Address1,
        Address2=Address2,
        Address3=Address3,
        City=City,
        State=State,
        PostalCode=PostalCode,
        Phone=Phone,
        Mobile=Mobile,
        Email=Email,
        Website=Website,
        # Currency = Currency,
        # FractionalUnit = FractionalUnit,
        VATNumber=VATNumber,
        GSTNumber=GSTNumber,
        Tax1=Tax1,
        Tax2=Tax2,
        Tax3=Tax3,
        owner=owner,
        Action=Action,
        is_deleted=True
    )

    response_data = {
        "StatusCode": 6000,
        "message": "CompanySettings Deleted Successfully!"
    }
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def check_company_delete(request):
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
                "message": "CompanySettings Deleted Successfully!"
            }
            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6001,
                "title": "Failed",
                "message": "organization can delete only the owner of organization"
            }
            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "user credential is wrong!"
        }
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_companyTransactions(request, pk):
    from brands import models
    data = request.data
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = get_company(pk)

    if models.DamageStockDetails.objects.filter(CompanyID=instance).exists():
        instances = models.DamageStockDetails.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.DamageStockDetails_Log.objects.filter(CompanyID=instance).exists():
        instances = models.DamageStockDetails_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.DamageStockMaster.objects.filter(CompanyID=instance).exists():
        instances = models.DamageStockMaster.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.DamageStockMaster_Log.objects.filter(CompanyID=instance).exists():
        instances = models.DamageStockMaster_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.JournalDetails.objects.filter(CompanyID=instance).exists():
        instances = models.JournalDetails.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.JournalDetails_Log.objects.filter(CompanyID=instance).exists():
        instances = models.JournalDetails_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.JournalMaster.objects.filter(CompanyID=instance).exists():
        instances = models.JournalMaster.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.JournalMaster_Log.objects.filter(CompanyID=instance).exists():
        instances = models.JournalMaster_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.LedgerPosting.objects.filter(CompanyID=instance).exists():
        instances = models.LedgerPosting.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.LedgerPosting_Log.objects.filter(CompanyID=instance).exists():
        instances = models.LedgerPosting_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.OpeningStockDetails.objects.filter(CompanyID=instance).exists():
        instances = models.OpeningStockDetails.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.OpeningStockDetails_Log.objects.filter(CompanyID=instance).exists():
        instances = models.OpeningStockDetails_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.OpeningStockMaster.objects.filter(CompanyID=instance).exists():
        instances = models.OpeningStockMaster.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.OpeningStockMaster_Log.objects.filter(CompanyID=instance).exists():
        instances = models.OpeningStockMaster_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PaymentDetails.objects.filter(CompanyID=instance).exists():
        instances = models.PaymentDetails.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PaymentDetails_Log.objects.filter(CompanyID=instance).exists():
        instances = models.PaymentDetails_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PaymentMaster.objects.filter(CompanyID=instance).exists():
        instances = models.PaymentMaster.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PaymentMaster_Log.objects.filter(CompanyID=instance).exists():
        instances = models.PaymentMaster_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.POSHoldDetails.objects.filter(CompanyID=instance).exists():
        instances = models.POSHoldDetails.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.POSHoldDetails_Log.objects.filter(CompanyID=instance).exists():
        instances = models.POSHoldDetails_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.POSHoldMaster.objects.filter(CompanyID=instance).exists():
        instances = models.POSHoldMaster.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.POSHoldMaster_Log.objects.filter(CompanyID=instance).exists():
        instances = models.POSHoldMaster_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PurchaseDetails.objects.filter(CompanyID=instance).exists():
        instances = models.PurchaseDetails.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PurchaseDetails_Log.objects.filter(CompanyID=instance).exists():
        instances = models.PurchaseDetails_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PurchaseMaster.objects.filter(CompanyID=instance).exists():
        instances = models.PurchaseMaster.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PurchaseMaster_Log.objects.filter(CompanyID=instance).exists():
        instances = models.PurchaseMaster_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PurchaseOrderDetails.objects.filter(CompanyID=instance).exists():
        instances = models.PurchaseOrderDetails.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PurchaseOrderDetails_Log.objects.filter(CompanyID=instance).exists():
        instances = models.PurchaseOrderDetails_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PurchaseOrderMaster.objects.filter(CompanyID=instance).exists():
        instances = models.PurchaseOrderMaster.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PurchaseOrderMaster_Log.objects.filter(CompanyID=instance).exists():
        instances = models.PurchaseOrderMaster_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PurchaseReturnDetails.objects.filter(CompanyID=instance).exists():
        instances = models.PurchaseReturnDetails.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PurchaseReturnDetails_Log.objects.filter(CompanyID=instance).exists():
        instances = models.PurchaseReturnDetails_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PurchaseReturnMaster.objects.filter(CompanyID=instance).exists():
        instances = models.PurchaseReturnMaster.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.PurchaseReturnMaster_Log.objects.filter(CompanyID=instance).exists():
        instances = models.PurchaseReturnMaster_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.ReceiptDetails.objects.filter(CompanyID=instance).exists():
        instances = models.ReceiptDetails.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.ReceiptDetails_Log.objects.filter(CompanyID=instance).exists():
        instances = models.ReceiptDetails_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.ReceiptMaster.objects.filter(CompanyID=instance).exists():
        instances = models.ReceiptMaster.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.ReceiptMaster_Log.objects.filter(CompanyID=instance).exists():
        instances = models.ReceiptMaster_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.SalesDetails.objects.filter(CompanyID=instance).exists():
        instances = models.SalesDetails.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.SalesDetails_Log.objects.filter(CompanyID=instance).exists():
        instances = models.SalesDetails_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.SalesMaster.objects.filter(CompanyID=instance).exists():
        instances = models.SalesMaster.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.SalesMaster_Log.objects.filter(CompanyID=instance).exists():
        instances = models.SalesMaster_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.SalesOrderDetails.objects.filter(CompanyID=instance).exists():
        instances = models.SalesOrderDetails.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.SalesOrderDetails_Log.objects.filter(CompanyID=instance).exists():
        instances = models.SalesOrderDetails_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.SalesOrderMaster.objects.filter(CompanyID=instance).exists():
        instances = models.SalesOrderMaster.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.SalesOrderMaster_Log.objects.filter(CompanyID=instance).exists():
        instances = models.SalesOrderMaster_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.SalesReturnDetails.objects.filter(CompanyID=instance).exists():
        instances = models.SalesReturnDetails.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.SalesReturnDetails_Log.objects.filter(CompanyID=instance).exists():
        instances = models.SalesReturnDetails_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.SalesReturnMaster.objects.filter(CompanyID=instance).exists():
        instances = models.SalesReturnMaster.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.SalesReturnMaster_Log.objects.filter(CompanyID=instance).exists():
        instances = models.SalesReturnMaster_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.StockAdjustmentDetails.objects.filter(CompanyID=instance).exists():
        instances = models.StockAdjustmentDetails.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.StockAdjustmentDetails_Log.objects.filter(CompanyID=instance).exists():
        instances = models.StockAdjustmentDetails_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.StockAdjustmentMaster.objects.filter(CompanyID=instance).exists():
        instances = models.StockAdjustmentMaster.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.StockAdjustmentMaster_Log.objects.filter(CompanyID=instance).exists():
        instances = models.StockAdjustmentMaster_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.StockReceiptDetails.objects.filter(CompanyID=instance).exists():
        instances = models.StockReceiptDetails.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.StockReceiptDetails_Log.objects.filter(CompanyID=instance).exists():
        instances = models.StockReceiptDetails_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.StockReceiptMaster_ID.objects.filter(CompanyID=instance).exists():
        instances = models.StockReceiptMaster_ID.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.StockReceiptMasterID_Log.objects.filter(CompanyID=instance).exists():
        instances = models.StockReceiptMasterID_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.StockTransferDetails.objects.filter(CompanyID=instance).exists():
        instances = models.StockTransferDetails.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.StockTransferDetails_Log.objects.filter(CompanyID=instance).exists():
        instances = models.StockTransferDetails_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.StockTransferMaster_ID.objects.filter(CompanyID=instance).exists():
        instances = models.StockTransferMaster_ID.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.StockTransferMasterID_Log.objects.filter(CompanyID=instance).exists():
        instances = models.StockTransferMasterID_Log.objects.filter(
            CompanyID=instance)
        for i in instances:
            i.delete()

    if models.StockPosting.objects.filter(CompanyID=instance).exists():
        instances = models.StockPosting.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.StockPosting_Log.objects.filter(CompanyID=instance).exists():
        instances = models.StockPosting_Log.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.StockRate.objects.filter(CompanyID=instance).exists():
        instances = models.StockRate.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    if models.StockTrans.objects.filter(CompanyID=instance).exists():
        instances = models.StockTrans.objects.filter(CompanyID=instance)
        for i in instances:
            i.delete()

    print("======================-----------------====================")

    response_data = {
        "StatusCode": 6000,
        "message": "Company Transactions Deleted Successfully!"
    }
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def get_company_count(request):
    data = request.data
    UserID = data['UserID']

    if CompanySettings.objects.filter(CreatedUserID=UserID).exists():
        count = CompanySettings.objects.filter(CreatedUserID=UserID).count()

        response_data = {
            "StatusCode": 6000,
            "count": count
        }
        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001
        }
        return Response(response_data, status=status.HTTP_200_OK)
