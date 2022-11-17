import ast
import datetime
import json
import time
import timeit
from decimal import Decimal
from io import BytesIO, StringIO
from django.db import connection

import pandas as pd
import pdfkit
import yaml
from django.http import HttpResponse
from django.template.loader import get_template
from django.utils.translation import activate
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, renderer_classes,authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from api.v10.brands.serializers import ListSerializer
from api.v10.companySettings.serializers import CompanySettingsPrintRestSerializer
from api.v10.ledgerPosting.functions import DayBook_excel_data
from api.v10.reportQuerys.functions import (
    billwise_profit_report_data,
    billwise_report_data,
    opening_stock_report_data,
    product_summary_report_data,
    purchase_order_report_data,
    purchase_register_report_data,
    purchaseReturn_register_report_data,
    query_Cash_OR_Bank_Book_report_data,
    query_Expense_summary,
    query_closingTrialBalance_report_data,
    query_ledger_report_data,
    query_openingBalance_data,
    query_openingStockBalance_data,
    query_outStandingReport_report_data,
    query_payment_report_data,
    query_purchase_both_report_data,
    query_purchase_integrated_report_data,
    query_purchase_report_data,
    query_purchaseReturn_report_data,
    query_receipt_report_data,
    query_sales_both_report_data,
    query_sales_integrated_report_data,
    query_sales_report_data,
    query_salesReturn_report_data,
    query_salesSummary_report_data,
    query_stock_report_data,
    query_stockLedger_report_data,
    query_stockValue_report_data,
    query_trialBalance_report_data,
    query_updateLedgerBalance,
    quick_report_data,
    quick_report_pdf_excel,
    sales_order_report_data,
    sales_register_report_data,
    salesReturn_register_report_data,
    stock_transfer_report_data,
    supplierVsproduct_report_data,
)
from api.v10.settings.functions import get_country_time
from brands.models import (
    AccountGroup,
    AccountLedger,
    Branch,
    Brand,
    Category,
    CompanySettings,
    Country,
    Customer,
    Parties,
    Product,
    ProductCategory,
    ProductGroup,
    Route,
    UserTable,
    Warehouse,
)
from main.functions import get_GeneralSettings, get_company
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives, EmailMessage, send_mail
from django.contrib.auth.models import User, Group

@api_view(["GET"])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def download_report(request):
    whose_report = ""
    lang = request.GET.get("lang")
    download_type = request.GET.get("download_type")
    value = request.GET.get("value")
    if lang and download_type == "EXCEL":
        activate(lang)

    CompanyID = request.GET.get("CompanyID")
    BranchID = request.GET.get("BranchID")
    FromDate = request.GET.get("FromDate")
    ToDate = request.GET.get("ToDate")
    PriceRounding = request.GET.get("PriceRounding")
    UserID = request.GET.get("UserID")
    EmployeeID = request.GET.get("EmployeeID")

    invoice_type = request.GET.get("invoice_type")
    ReffNo = request.GET.get("ReffNo")
    ManualOpeningBalance = request.GET.get("ManualOpeningBalance")
    LedgerList = request.GET.getlist("LedgerList")

    VoucherType = request.GET.get("VoucherType")
    RouteLedgers = request.GET.get("RouteLedgers")
    if RouteLedgers:
        RouteLedgers = eval(RouteLedgers)

    LedgerID = request.GET.get("LedgerID")
    WareHouseID = request.GET.get("WarehouseID")
    WareHouseFrom = request.GET.get("WareHouseFrom")
    WareHouseTo = request.GET.get("WareHouseTo")

    PriceListID = request.GET.get("PriceListID")
    RouteID = request.GET.get("RouteID")
    CustomerID = request.GET.get("CustomerID")
    ProductFilter = request.GET.get("ProductFilter")
    StockFilter = request.GET.get("StockFilter")
    ProductID = request.GET.get("ProductID")
    CategoryID = request.GET.get("CategoryID")
    GroupID = request.GET.get("GroupID")
    ProductCode = request.GET.get("ProductCode")
    Barcode = request.GET.get("Barcode")
    BrandID = request.GET.get("BrandID")
    PartyID = request.GET.get("PartyID")
    filterValue = request.GET.get("filterValue")
    templateType = request.GET.get("templateType")

    is_manualOpening = request.GET.get("is_manualOpening")
    key = request.GET.get("key")
    ManualOpeningStock = request.GET.get("ManualOpeningStock")
    ManualClosingStock = request.GET.get("ManualClosingStock")

    CashLedgersList = request.GET.get("CashLedgers")
    is_fromDate = request.GET.get("is_fromDate")

    try:
        is_send_mail = request.GET.get("is_send_mail")
    except:
        is_send_mail = False
    # if CashLedgersList:
    #     CashLedgersList = eval(CashLedgersList)
    CashLedgersList = CashLedgersList.split(",")
    columns = request.GET.get("columns")
    columns_heads = []
    if columns:
        columns_heads = json.loads(columns)

    LedgerList = [x for x in LedgerList if x]
    for x in LedgerList:
        test_list = str(x).split(",")
        for i in range(0, len(test_list)):
            test_list[i] = int(test_list[i])
        LedgerList = test_list

    LedgerList = [x for x in LedgerList if x]
    CashLedgers = LedgerList
    # RouteLedgers = LedgerList

    try:
        value = int(request.GET.get("value"))
    except:
        value = 0

    try:
        PriceRounding = int(request.GET.get("PriceRounding"))
    except:
        PriceRounding = 2

    company_instance = CompanySettings.objects.get(id=CompanyID)
    country_instance = Country.objects.get(id=company_instance.Country.id)
    ShowProfitinSalesRegisterReport = False
    data = {}
    details = {}
    details1 = {}
    details2 = {}
    details3 = {}
    total = {}
    page_type = ""
    report_title = ""
    
    print("invoice_type>>>>>>>>>>>>>>>>>>>>>")
    print(invoice_type)

    # Sales Report
    if invoice_type == "sales":
        page_type = "master"
        df, details = query_sales_report_data(
            CompanyID, BranchID, FromDate, ToDate, PriceRounding, UserID, EmployeeID,CustomerID,filterValue
        )
        # Removing Id From Excel Sheet
        df = df.drop(["id"], axis=1)
    # Sales Return Report
    elif invoice_type == "sales_return":
        page_type = "return"
        df, details = query_salesReturn_report_data(
            CompanyID, BranchID, FromDate, ToDate, PriceRounding, UserID, EmployeeID,CustomerID,filterValue
        )
        # Removing Id From Excel Sheet
        df = df.drop(["id"], axis=1)
    # Sales Both Report
    elif invoice_type == "sales_both":
        page_type = "both"
        df, details = query_sales_both_report_data(
            CompanyID, BranchID, FromDate, ToDate, PriceRounding, UserID, EmployeeID,CustomerID,filterValue
        )
        # Removing Id From Excel Sheet
        df = df.drop(["id"], axis=1)
    # Sales Summary Report
    elif invoice_type == "sales_summary":
        page_type = "master"
        df,details = query_salesSummary_report_data(
            CompanyID,
            BranchID,
            FromDate,
            ToDate,
            PriceRounding,
            UserID,
            WareHouseID,
            LedgerID,
        )
        if AccountLedger.objects.filter(CompanyID=CompanyID,LedgerID=LedgerID).exists():
            whose_report = AccountLedger.objects.get(
                CompanyID=CompanyID,LedgerID=LedgerID
            ).LedgerName
        elif Warehouse.objects.filter(CompanyID=CompanyID,WarehouseID=WareHouseID).exists():
            whose_report = Warehouse.objects.get(
                CompanyID=CompanyID,WarehouseID=WareHouseID
            ).WarehouseName       
    # Purchase Report
    elif invoice_type == "purchase":
        print(ReffNo, "123456uaistrr%")
        page_type = "master"
        df,details = query_purchase_report_data(
            CompanyID, BranchID, FromDate, ToDate, PriceRounding,ReffNo, UserID, EmployeeID,CustomerID,filterValue
        )       
        df = df.drop(["id"], axis=1)
    # Purchase Return Report
    elif invoice_type == "purchase_return":
        page_type = "return"
        df,details = query_purchaseReturn_report_data(
            CompanyID, BranchID, FromDate, ToDate, PriceRounding,ReffNo, UserID, EmployeeID,CustomerID,filterValue
        )
        df = df.drop(["id"], axis=1)
   # Purchase Both Report
    elif invoice_type == "purchase_both":
        page_type = "both"
        df,details = query_purchase_both_report_data(
            CompanyID, BranchID, FromDate, ToDate, PriceRounding,ReffNo, UserID, EmployeeID,CustomerID,filterValue
        )       
        df = df.drop(["id"], axis=1)
    # Out Standing Report
    if invoice_type == "OutStanding":
        data = query_outStandingReport_report_data(
            CompanyID, BranchID, PriceRounding, RouteLedgers, ToDate, VoucherType
        )
        df = pd.DataFrame(data)
        print(df)
        df.columns = [str(_("LedgerID")),str(_("LedgerName")), str(_("Debit")), str(_("Credit"))]
        df.loc[str(_("Total"))] = (
            df[[str(_("Debit")), str(_("Credit"))]].sum().reindex(df.columns, fill_value="")
        )

        json_records = df.reset_index().to_json(orient="records")
        details = json.loads(json_records)
        if VoucherType == "null":
            VoucherType = "ALL"
    # Stock Report
    elif invoice_type == "stock_report":
        df, details = query_stock_report_data(
            CompanyID,
            BranchID,
            FromDate,
            ToDate,
            PriceRounding,
            ProductFilter,
            StockFilter,
            ProductID,
            CategoryID,
            GroupID,
            WareHouseID,
            Barcode,
            BrandID,
        )
        df.style.set_caption("Hello World")
        if Warehouse.objects.filter(
                CompanyID=CompanyID, WarehouseID=WareHouseID
            ).exists():
                whose_report = Warehouse.objects.get(
                    CompanyID=CompanyID, WarehouseID=WareHouseID
                ).WarehouseName
        elif ProductCategory.objects.filter(
                CompanyID=CompanyID, ProductCategoryID=CategoryID
            ).exists():
                whose_report = ProductCategory.objects.get(
                    CompanyID=CompanyID, ProductCategoryID=CategoryID
                ).CategoryName
        elif ProductGroup.objects.filter(
                CompanyID=CompanyID, ProductGroupID=GroupID
            ).exists():
                whose_report = ProductGroup.objects.get(
                    CompanyID=CompanyID, ProductGroupID=GroupID
                ).GroupName
        elif Brand.objects.filter(
                CompanyID=CompanyID, BrandID=BrandID
            ).exists():
                whose_report = Brand.objects.get(
                    CompanyID=CompanyID, BrandID=BrandID
                ).BrandName
    # Stock Ledger Report
    elif invoice_type == "stock_ledger_report":
        df, details = query_stockLedger_report_data(
            CompanyID, BranchID, FromDate, ToDate, PriceRounding, ProductID, WareHouseID
        )
    # Stock Value Report
    elif invoice_type == "stock_value_report":
        df, details = query_stockValue_report_data(
            CompanyID, BranchID, FromDate, ToDate, PriceRounding, ProductID, WareHouseID
        )
    # Ledger Report
    elif invoice_type == "ledger_report":
        if VoucherType == "ledger_wise":
            if AccountLedger.objects.filter(CompanyID=CompanyID,LedgerID=value).exists():
                whose_report = AccountLedger.objects.get(CompanyID=CompanyID,LedgerID=value).LedgerName
        elif VoucherType == "group_wise":
            if AccountGroup.objects.filter(
                CompanyID=CompanyID, AccountGroupID=value
            ).exists():
                whose_report = AccountGroup.objects.get(
                    CompanyID=CompanyID, AccountGroupID=value
                ).AccountGroupName
        df, details = query_ledger_report_data(
            CompanyID,
            BranchID,
            FromDate,
            ToDate,
            PriceRounding,
            VoucherType,
            int(value),
            ManualOpeningBalance,
            is_fromDate
        )
    # Trail Balance Report
    elif invoice_type == "trial_balance":
        df, details = query_closingTrialBalance_report_data(
            templateType,filterValue,CompanyID, UserID, PriceRounding, BranchID, ToDate, FromDate
        )
        print(df,"******************************************&")
        if templateType == "Closing Trial Balance":
            df = df.drop(['Debit','Credit'],axis=1)
            if templateType == "Closing Trial Balance":
                df = df.drop(['OpeningBalance','ClosingBalance'],axis=1)
                df.columns = [['Transactions'] * 4 + ['Opening Balance'] * 2 + ['Closing Balance'] * 2, df.columns]
                # df.columns = ['Transactions','ddd','ddd','dd'] + ['Opening Balance'] + ['Opening Balance'] + ['Opening Balance'] + ['Opening Balance'] + ['Closing Balance'], df.columns
        elif templateType == "Trial Balance":
            df = df.drop(['OpeningBalance','ClosingBalance','TotalDebit','TotalCredit','OpeningDebit','OpeningCredit','ClosingDebit','ClosingCredit','OpeningBalance','OpeningBalance','OpeningBalance','OpeningBalance','OpeningBalance','OpeningBalance'],axis=1)
        else:
            df = df.drop(['AccountGroupName','OpeningBalance','ClosingBalance','TotalDebit','TotalCredit','OpeningDebit','OpeningCredit','ClosingDebit','ClosingCredit','OpeningBalance','OpeningBalance','OpeningBalance','OpeningBalance','OpeningBalance','OpeningBalance'],axis=1)
    # Day Book
    elif invoice_type == "day_book":
        data = DayBook_excel_data(
            CompanyID, BranchID, ToDate, PriceRounding, VoucherType
        )
        if VoucherType == "1":
            details = data["summary_final"]
        elif VoucherType == "2":
            details = data["detailed_final"]
    # Cash Book
    elif invoice_type == "cash_book":
        df, details = query_Cash_OR_Bank_Book_report_data(
            9,
            CompanyID,
            BranchID,
            FromDate,
            ToDate,
            PriceRounding,
            VoucherType,
            RouteLedgers,
            ManualOpeningBalance,
        )
    # Bank Book
    elif invoice_type == "bank_book":
        df, details = query_Cash_OR_Bank_Book_report_data(
            8,
            CompanyID,
            BranchID,
            FromDate,
            ToDate,
            PriceRounding,
            VoucherType,
            RouteLedgers,
            ManualOpeningBalance,
        )
    # Receipt Report
    elif invoice_type == "receipt_report":
        df, details = query_receipt_report_data(
            CompanyID,
            BranchID,
            FromDate,
            ToDate,
            PriceRounding,
            RouteLedgers,
            VoucherType,
        )
    # Payment Report
    elif invoice_type == "payment_report":
        df, details = query_payment_report_data(
            CompanyID,
            BranchID,
            FromDate,
            ToDate,
            PriceRounding,
            RouteLedgers,
            VoucherType,
        )
    # Sales Integrated Report
    elif invoice_type == "sales_integrated_report":
        df, details = query_sales_integrated_report_data(
            CompanyID, BranchID, FromDate, ToDate, UserID
        )
    elif invoice_type == "purchase_integrated_report":
        df, details = query_purchase_integrated_report_data(
            CompanyID, BranchID, FromDate, ToDate, UserID
        )
    elif invoice_type == "billwise_profit_report":
        if not str(UserID) == "0" and UserTable.objects.filter(CompanyID=CompanyID, id=UserID, Active=True):
                whose_report = UserTable.objects.get(
                    CompanyID=CompanyID, id=UserID, Active=True
                ).customer.user.username
        if Parties.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PartyID=CustomerID).exists():
            whose_report = Parties.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, PartyID=CustomerID).first().PartyName
        if Route.objects.filter(CompanyID=CompanyID, BranchID=BranchID, RouteID=RouteID).exists():
            whose_report = Route.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, RouteID=RouteID).first().RouteName
        df, details = billwise_profit_report_data(
            CompanyID,
            BranchID,
            FromDate,
            ToDate,
            UserID,
            WareHouseID,
            CustomerID,
            RouteID,
        )
    elif invoice_type == "billwise_report":
        if Parties.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PartyID=CustomerID).exists():
            whose_report = Parties.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, PartyID=CustomerID).first().PartyName
        if Route.objects.filter(CompanyID=CompanyID, BranchID=BranchID, RouteID=RouteID).exists():
            whose_report = Route.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, RouteID=RouteID).first().RouteName
        df, details = billwise_report_data(
            CompanyID,
            BranchID,
            FromDate,
            ToDate,
            CustomerID,
            RouteID,
        )
        
    elif invoice_type == "supplier_vs_product_report":
        df, details = supplierVsproduct_report_data(
            CompanyID, BranchID, FromDate, ToDate, PartyID, ProductID, filterValue
        )
    elif invoice_type == "opening_stock_report":
        if WareHouseID:
            WareHouseID = WareHouseID.split(",")
        else:
            WareHouseID = []
        df, details = opening_stock_report_data(
            CompanyID, BranchID, FromDate, ToDate, PriceRounding, WareHouseID
        )
    elif invoice_type == "purchase_order_report":
        if filterValue:
            filterValue = filterValue.split(",")
        else:
            filterValue = []
        df, details = purchase_order_report_data(
            CompanyID, BranchID, FromDate, ToDate, filterValue
        )
    elif invoice_type == "sales_order_report":
        if filterValue:
            filterValue = filterValue.split(",")
        else:
            filterValue = []
        df, details = sales_order_report_data(
            CompanyID, BranchID, FromDate, ToDate, filterValue
        )
    elif invoice_type == "sales_register_report":
        ShowProfitinSalesRegisterReport = get_GeneralSettings(
            CompanyID, BranchID[0], "ShowProfitinSalesRegisterReport"
        )
        warehouse_list = []
        user_list = []
        ledger_list = []
        CompanyID_ins = get_company(CompanyID)
        BranchList = [1]
        if Branch.objects.filter(CompanyID=CompanyID_ins).exists():
            BranchList = Branch.objects.filter(CompanyID=CompanyID_ins).values_list(
                "BranchID", flat=True
            )
        if AccountLedger.objects.filter(CompanyID=CompanyID_ins).exists():
            ledger_list = AccountLedger.objects.filter(
                CompanyID=CompanyID_ins
            ).values_list("LedgerID", flat=True)
        if Warehouse.objects.filter(CompanyID=CompanyID_ins).exists():
            warehouse_list = Warehouse.objects.filter(
                CompanyID=CompanyID_ins
            ).values_list("WarehouseID", flat=True)
        if UserTable.objects.filter(CompanyID=CompanyID_ins, Active=True).exists():
            user_list = UserTable.objects.filter(CompanyID=CompanyID_ins, Active=True).values_list(
                "customer_id", flat=True
            )
            user_list = Customer.objects.filter(id__in=user_list).values_list(
                "user_id", flat=True
            )

        if int(BranchID) > 0:
            BranchList = []
            BranchList.append(int(BranchID))
        if int(LedgerID) > 0:
            ledger_list = []
            ledger_list.append(int(LedgerID))
        if int(WareHouseID) > 0:
            warehouse_list = []
            warehouse_list.append(int(WareHouseID))
        if int(UserID) > 0:
            user_list = []
            user_list.append(int(UserID))

        df, details = sales_register_report_data(
            CompanyID,
            BranchList,
            FromDate,
            ToDate,
            warehouse_list,
            user_list,
            ledger_list,
            ProductID,
            GroupID,
            CategoryID,
            ProductCode,
            Barcode,
        )
    elif invoice_type == "purchase_register_report":
        warehouse_list = []
        user_list = []
        ledger_list = []
        CompanyID_ins = get_company(CompanyID)
        BranchList = [1]
        if Branch.objects.filter(CompanyID=CompanyID_ins).exists():
            BranchList = Branch.objects.filter(CompanyID=CompanyID_ins).values_list(
                "BranchID", flat=True
            )
        if AccountLedger.objects.filter(CompanyID=CompanyID_ins).exists():
            ledger_list = AccountLedger.objects.filter(
                CompanyID=CompanyID_ins
            ).values_list("LedgerID", flat=True)
        if Warehouse.objects.filter(CompanyID=CompanyID_ins).exists():
            warehouse_list = Warehouse.objects.filter(
                CompanyID=CompanyID_ins
            ).values_list("WarehouseID", flat=True)
        if UserTable.objects.filter(CompanyID=CompanyID_ins, Active=True).exists():
            user_list = UserTable.objects.filter(CompanyID=CompanyID_ins, Active=True).values_list(
                "customer_id", flat=True
            )
            user_list = Customer.objects.filter(id__in=user_list).values_list(
                "user_id", flat=True
            )

        if int(BranchID) > 0:
            BranchList = []
            BranchList.append(int(BranchID))
        if int(LedgerID) > 0:
            ledger_list = []
            ledger_list.append(int(LedgerID))
        if int(WareHouseID) > 0:
            warehouse_list = []
            warehouse_list.append(int(WareHouseID))
        if int(UserID) > 0:
            user_list = []
            user_list.append(int(UserID))

        df, details = purchase_register_report_data(
            CompanyID,
            BranchList,
            FromDate,
            ToDate,
            warehouse_list,
            user_list,
            ledger_list,
            ProductID,
            GroupID,
            CategoryID,
            ProductCode,
            Barcode,
        )
    elif invoice_type == "salesReturn_register_report":
        warehouse_list = []
        user_list = []
        ledger_list = []
        CompanyID_ins = get_company(CompanyID)
        BranchList = [1]
        if Branch.objects.filter(CompanyID=CompanyID_ins).exists():
            BranchList = Branch.objects.filter(CompanyID=CompanyID_ins).values_list(
                "BranchID", flat=True
            )
        if AccountLedger.objects.filter(CompanyID=CompanyID_ins).exists():
            ledger_list = AccountLedger.objects.filter(
                CompanyID=CompanyID_ins
            ).values_list("LedgerID", flat=True)
        if Warehouse.objects.filter(CompanyID=CompanyID_ins).exists():
            warehouse_list = Warehouse.objects.filter(
                CompanyID=CompanyID_ins
            ).values_list("WarehouseID", flat=True)
        if UserTable.objects.filter(CompanyID=CompanyID_ins, Active=True).exists():
            user_list = UserTable.objects.filter(CompanyID=CompanyID_ins, Active=True).values_list(
                "customer_id", flat=True
            )
            user_list = Customer.objects.filter(id__in=user_list).values_list(
                "user_id", flat=True
            )

        if int(BranchID) > 0:
            BranchList = []
            BranchList.append(int(BranchID))
        if int(LedgerID) > 0:
            ledger_list = []
            ledger_list.append(int(LedgerID))
        if int(WareHouseID) > 0:
            warehouse_list = []
            warehouse_list.append(int(WareHouseID))
        if int(UserID) > 0:
            user_list = []
            user_list.append(int(UserID))

        df, details = salesReturn_register_report_data(
            CompanyID,
            BranchList,
            FromDate,
            ToDate,
            warehouse_list,
            user_list,
            ledger_list,
            ProductID,
            GroupID,
            CategoryID,
            ProductCode,
            Barcode,
        )
    elif invoice_type == "purchaseReturn_register_report":
        warehouse_list = []
        user_list = []
        ledger_list = []
        CompanyID_ins = get_company(CompanyID)
        BranchList = [1]
        if Branch.objects.filter(CompanyID=CompanyID_ins).exists():
            BranchList = Branch.objects.filter(CompanyID=CompanyID_ins).values_list(
                "BranchID", flat=True
            )
        if AccountLedger.objects.filter(CompanyID=CompanyID_ins).exists():
            ledger_list = AccountLedger.objects.filter(
                CompanyID=CompanyID_ins
            ).values_list("LedgerID", flat=True)
        if Warehouse.objects.filter(CompanyID=CompanyID_ins).exists():
            warehouse_list = Warehouse.objects.filter(
                CompanyID=CompanyID_ins
            ).values_list("WarehouseID", flat=True)
        if UserTable.objects.filter(CompanyID=CompanyID_ins, Active=True).exists():
            user_list = UserTable.objects.filter(CompanyID=CompanyID_ins, Active=True).values_list(
                "customer_id", flat=True
            )
            user_list = Customer.objects.filter(id__in=user_list).values_list(
                "user_id", flat=True
            )

        if int(BranchID) > 0:
            BranchList = []
            BranchList.append(int(BranchID))
        if int(LedgerID) > 0:
            ledger_list = []
            ledger_list.append(int(LedgerID))
        if int(WareHouseID) > 0:
            warehouse_list = []
            warehouse_list.append(int(WareHouseID))
        if int(UserID) > 0:
            user_list = []
            user_list.append(int(UserID))

        df, details = purchaseReturn_register_report_data(
            CompanyID,
            BranchList,
            FromDate,
            ToDate,
            warehouse_list,
            user_list,
            ledger_list,
            ProductID,
            GroupID,
            CategoryID,
            ProductCode,
            Barcode,
        )
    elif invoice_type == "stock_transfer_report":
        df, details = stock_transfer_report_data(
            CompanyID,
            BranchID,
            FromDate,
            ToDate,
            PriceRounding,
            int(UserID),
            int(WareHouseFrom),
            int(WareHouseTo),
            "ST",
        )
    elif invoice_type == "expense_summary":
        df, details = query_Expense_summary(CompanyID,RouteLedgers,FromDate,ToDate,PriceRounding)
    elif invoice_type == "quick_report":
        df, details1, details2, details3, = quick_report_pdf_excel(
            CompanyID,
            BranchID,
            FromDate,
            ToDate
        )

    elif invoice_type == "product_summary":
        df, details = product_summary_report_data(
            CompanyID,
            BranchID,
            FromDate,
            ToDate,
             ProductID,
              CategoryID,
              GroupID,
              BrandID,
              PriceListID,
              LedgerID
        )
    # For PDF
    if lang:
        activate(lang)

    if (
        invoice_type == "sales"
        or invoice_type == "sales_return"
        or invoice_type == "purchase"
        or invoice_type == "purchase_return"
        or invoice_type == "purchase_both"
        or invoice_type == "sales_both"
    ):
        
        if invoice_type == "sales":
                report_name = "SALES REPORT"
                report_title = str(_("SALES REPORT"))
        elif invoice_type == "sales_return":
                report_name = "RETURN REPORT"
                report_title = str(_("RETURN REPORT"))
        elif invoice_type == "sales_both":
                report_name = "BOTH REPORT"
                report_title = str(_("BOTH REPORT"))
        elif invoice_type == "purchase":
                report_name = "PURCHASE REPORT"
                report_title = str(_("PURCHASE REPORT"))
        elif invoice_type == "purchase_return":
                report_name = "PURCHASE RETURN REPORT"
                report_title = str(_("PURCHASE RETURN REPORT"))
        elif invoice_type == "purchase_both":
                report_name = "PURCHASE BOTH REPORT"
                report_title = str(_("PURCHASE BOTH REPORT"))
        template = get_template("reports/invoice_print.html")
    elif invoice_type == "sales_summary":
        report_name = "SALES SUMMARY REPORT"
        report_title = str(_("SALES SUMMARY REPORT"))
        template = get_template("reports/sales_summary_print.html")
    elif invoice_type == "OutStanding":
        report_name = "OUTSTANDING REPORT"
        report_title = str(_("OUTSTANDING REPORT"))
        template = get_template("reports/out_standing_print.html")
    elif invoice_type == "stock_report":
        report_name = "STOCK REPORT"
        report_title = str(_("STOCK REPORT"))
        template = get_template("reports/stock_report_print.html")
    elif invoice_type == "stock_ledger_report":
        report_name = "STOCK LEDGER REPORT"
        report_title = str(_("STOCK LEDGER REPORT"))
        template = get_template("reports/stock_ledger_report_print.html")
    elif invoice_type == "stock_value_report":
        report_name = "STOCK VALUE REPORT"
        report_title = str(_("STOCK VALUE REPORT"))
        template = get_template("reports/stock_value_report.html")
    elif invoice_type == "ledger_report":
        print(VoucherType, "<<<<<<<<<<<<<<<<<<VOUCHRTYPE>>>>>>>>>>>>>>>>>>>>>>>")
        invoice_type = VoucherType
        report_name = "LEDGER REPORT"
        report_title = str(_("LEDGER REPORT"))
        template = get_template("reports/ledger_report_print.html")
    elif invoice_type == "trial_balance":
        if templateType == "Trial Balance":
            template = get_template("reports/trail_balance_print1.html")
        elif templateType == "Closing Trial Balance":
            template = get_template("reports/trail_balance_print2.html")
        else:
            template = get_template("reports/trail_balance_print.html")
        report_name = "TRAIL BALANCE"
        report_title = str(_(templateType))
    elif invoice_type == "day_book":
        template = get_template("reports/day_book_print.html")
        report_name = "DAY BOOK"
        report_title = str(_("DAY BOOK"))
    elif invoice_type == "receipt_report":
        template = get_template("reports/receipt_report_print.html")
        report_name = "Receipt Report"
        report_title = str(_("Receipt Report"))
    elif invoice_type == "payment_report":
        template = get_template("reports/payment_report_print.html")
        report_name = "Payment Report"
        report_title = str(_("Payment Report"))
    elif invoice_type == "sales_integrated_report":
        template = get_template("reports/sales_integrated_print.html")
        report_name = "Sales Integrated Report"
        report_title = str(_("Sales Integrated Report"))
    elif invoice_type == "purchase_integrated_report":
        template = get_template("reports/purchase_integrated_print.html")
        report_name = "Purchase Integrated Report"
        report_title = str(_("Purchase Integrated Report"))
    elif invoice_type == "billwise_profit_report":
        template = get_template("reports/billwise_profit_print.html")
        report_name = "Billwise Profit Report"
        report_title = str(_("Billwise Profit Report"))
    elif invoice_type == "billwise_report":
        template = get_template("reports/billwise_print.html")
        report_name = "Billwise Report"
        report_title = str(_("Billwise Report"))
        templateType = report_title
    elif invoice_type == "supplier_vs_product_report":
        template = get_template("reports/supplierVsproduct_print.html")
        report_name = "Supplier Vs Product Report"
        report_title = str(_("Supplier Vs Product Report"))
        VoucherType = filterValue
    elif invoice_type == "opening_stock_report":
        template = get_template("reports/opening_stock_report_print.html")
        report_name = "Opening Stock Report"
        report_title = str(_("Opening Stock Report"))

    elif invoice_type == "cash_book":
        template = get_template("reports/cash_book_print.html")
        report_name = "Cash Book Report"
        report_title = str(_("CASH BOOK REPORT"))
    elif invoice_type == "bank_book":
        template = get_template("reports/cash_book_print.html")
        report_name = "Bank Book Report"
        report_title = str(_("BANK BOOK REPORT"))
    elif invoice_type == "stock_transfer_report":
        template = get_template("reports/stock_transfer_report_print.html")
        report_name = "Stock Transfer Report"
        report_title = str(_("Stock Transfer Report"))

    elif invoice_type == "purchase_order_report":
        template = get_template("reports/purchase_order_print.html")
        report_name = "Purchase Order Report"
        report_title = str(_("Purchase Order Report"))
    elif invoice_type == "sales_order_report":
        template = get_template("reports/sales_order_print.html")
        report_name = "Sales Order Report"
        report_title = str(_("Sales Order Report"))
    elif invoice_type == "sales_register_report":
        template = get_template("reports/sales_register_report_print.html")
        report_name = "Sales Register Report"
        report_title = str(_("Sales Register Report"))
    elif invoice_type == "purchase_register_report":
        template = get_template("reports/purchase_register_report_print.html")
        report_name = "Purchase Register Report"
        report_title = str(_("Purchase Register Report"))
    elif invoice_type == "salesReturn_register_report":
        template = get_template("reports/salesReturn_register_report_print.html")
        report_name = "Sales Return Register Report"
        report_title = str(_("Sales Return Register Report"))
    elif invoice_type == "purchaseReturn_register_report":
        template = get_template("reports/purchaseReturn_register_report_print.html")
        report_name = "Purchase Return Register Report"
        report_title = str(_("Purchase Return Register Report"))

    elif invoice_type == "expense_summary":
        template = get_template("reports/expense_summary_print.html")
        report_name = "Expense Summary Report"
        report_title = str(_("Expense Summary Report"))
    elif invoice_type == "quick_report":
        template = get_template("reports/quick_report_print.html")
        report_name = "Quick Report"
        report_title = str(_("Quick Report"))
        templateType = report_title
    elif invoice_type == "product_summary":
        template = get_template("reports/product_summary_print.html")
        report_name = "Product Summary Report"
        report_title = str(_("Product Summary Report"))

   
    if download_type == "PDF":
        today = datetime.datetime.now()
        current_time = get_country_time(
            today, country_instance.Country_Name
        )
        today = today.date()
        asof_date = today.strftime("%B %d, %Y")
        today = today.strftime("%d/%m/%y")
        # if lang:
        #     activate(lang)
        company_instance = CompanySettings.objects.get(id=CompanyID)
        serialized = CompanySettingsPrintRestSerializer(
            company_instance, many=False, context={"request": request}
        )
        data = {
            "country": country_instance,
            "page_type": page_type,
            "invoice_type": invoice_type,
            "VoucherType": VoucherType,
            "type": "pdf",
            "company": serialized.data,
            "details": details,
            "details1": details1,
            "details2": details2,
            "details3": details3,
            "total": total,
            "PriceRounding": int(PriceRounding),
            "FromDate": FromDate,
            "ToDate": ToDate,
            "report_title": report_title,
            "print_template": True,
            "columns_heads": columns_heads,
            "whose_report": whose_report,
            "ShowProfitinSalesRegisterReport": ShowProfitinSalesRegisterReport,
            "current_time": current_time,
            "today": today,
            "asof_date": asof_date
        }
        html = template.render(data)
        options = {
            "page-size": "Letter",
            "encoding": "UTF-8",
            "margin-top": "0.5in",
            "margin-right": "0.5in",
            "margin-bottom": "0.5in",
            "margin-left": "0.5in",
        }

        pdf = pdfkit.from_string(html, False, options)
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="{}.pdf"'.format(
            report_name
        )
    elif download_type == "EXCEL":
        with BytesIO() as b:
            with pd.ExcelWriter(b) as writer:
                # You can add multiple Dataframes to an excel file
                # Using the sheet_name attribute
                workbook = writer.book


               
                if VoucherType == 'product_summary_all':
                    df = df[0].drop([str(_("id"))], axis=1)
                    df1 = df[1].drop([str(_("id"))], axis=1)
                    worksheet1 = df.to_excel(writer, sheet_name="Sales", index=True)
                    worksheet2 = df1.to_excel(writer, sheet_name="Purchase", index=True)
                elif VoucherType == 'product_summary_sales':
                    df = df[0].drop([str(_("id"))], axis=1)
                    worksheet1 = df.to_excel(writer, sheet_name="Sales", index=True)
                elif VoucherType == 'product_summary_purchase':
                    df = df[1].drop([str(_("id"))], axis=1)
                    worksheet2 = df.to_excel(writer, sheet_name="Purchase", index=True)
                else:
                    print(invoice_type,"((((((((((((((((((*_D!))))))))))))))")
                    df = df.drop([str(_("id"))], axis=1)
                    worksheet1 = df.to_excel(writer, sheet_name=report_name, index=True)
                # worksheet2 = df.to_excel(writer, sheet_name="Closing Trial Balance", index=True)
                # workbook  = writer.book
                # worksheet_tb = writer.sheets['Trial Balance']
                # worksheet_ctb = writer.sheets['Closing Trial Balance']
                # text = 'Trial Balance'
                # text1 = 'Closing Trial Balance'
                # worksheet_tb.write(0, 0, text)
                # worksheet_ctb.write(0, 0, text1)

            response = HttpResponse(b.getvalue(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response["Content-Disposition"] = 'attachment; filename="{}.xlsx"'.format(
                report_name
            )
            # writer = pd.ExcelWriter('uvais111.xlsx', engine='xlsxwriter')
            # df.to_excel(writer, sheet_name='Sheet1', startrow = 1, index=False)
            # workbook  = writer.book
            # worksheet = writer.sheets['Sheet1']

            # text = 'sometitle'
            # worksheet.write(0, 0, text)

        
        # df.to_excel(response,index=False)
    return response


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def send_mail_reports(request):
    data = request.data
    token = data['token']
    UserID = data['UserID']
    user = User.objects.get(id=UserID)
    email = user.email
    username = user.username
    context = {
        'email': email,
        'site_name': 'viknbooks.com',
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'user': user,
        'token': token,
        'current_user': username,
        'username': username,
        'report_name': "Ledger Report",
    }

    email_html_message = render_to_string(
        'email/report_download.html', context)
    subject = "Download {title}".format(title="Ledger Report")
    print("send mailllllllllllllllllllllllll")
    print(user.email)
    msg = EmailMultiAlternatives(
        "Download Ledger Report",
        subject,
        "noreply@somehost.local",
        [user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()
    response_data = {
        "StatusCode": 6000,
    }
    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def export_company_details(request):
    dic = {}
    cursor = connection.cursor()
    cursor.execute('''
              SELECT               
                "id",
                "CreatedDate",
                "CompanyName",
                (SELECT COALESCE("username", '') FROM public."auth_user" AS C WHERE C."id" = "owner_id"   ) AS Ownername,
                (SELECT COALESCE("username", '') FROM public."auth_user" AS C WHERE C."id" = "CreatedUserID"   ) AS Createdusername,
                (SELECT COALESCE("email", '') FROM public."auth_user" AS C WHERE C."id" = "CreatedUserID"   ) AS useremail,
                (SELECT COALESCE("Phone", 0) FROM public."customer" AS C WHERE C."user_id" = "CreatedUserID"   fetch first 1 rows only) AS CustomerPhone,
                (SELECT COALESCE("Name", '') FROM public."state_state" AS C WHERE C."id" = "State_id"   ) AS State,
                (SELECT COALESCE("Country_Name", '') FROM public."country_country" AS C WHERE C."id" = "Country_id"   ) AS Country,

                "Mobile",
                "Phone",
                "Email",
                "Address1",
                "Address2",
                "Address3",
                "ExpiryDate",
                "NoOfUsers",
                "is_deleted"
                FROM public."companySettings_companySettings"     
                   
        ''', dic)
    response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    response["Content-Disposition"] = 'attachment; filename="{}.xlsx"'.format(
            "Companies"
        )
    data = cursor.fetchall()
    df = pd.DataFrame(data)
    df.columns = [
            'id',
            'CreatedDate',
            'CompanyName',
            'Ownername',
            'Createdusername',
            'useremail',
            'CustomerPhone',
            'State',
            'Country',
            'Mobile',
            'Phone',
            'Email',
            'Address1',
            'Address2',
            'Address3',
            'ExpiryDate',
            'NoOfUsers',
            'is_deleted',
            ]
    df['CreatedDate'] = df['CreatedDate'].dt.date
    # df['Date'] = pd.to_datetime(df['DateTime']).dt.date

    
    df.to_excel(response,index=False)
    return response

