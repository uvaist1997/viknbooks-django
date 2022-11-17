from rest_framework import serializers
from brands.models import Settings, PrintSettings, BarcodeSettings, Language, UserType


class SettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Settings
        fields = ('id', 'BranchID', 'PriceList', 'Group',
                  'SettingsType', 'SettingsValue', 'CreatedDate', 'CreatedUserID')


class SettingsRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Settings
        fields = ('id', 'SettingsID', 'BranchID', 'Action', 'PriceList', 'GroupName', 'SettingsType', 'SettingsValue',
                  'CreatedDate', 'CreatedUserID')


class PrintSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = PrintSettings
        fields = ('id', 'template', 'IsDefaultThermalPrinter', 'PageSize', 'IsCompanyLogo', 'IsCompanyName', 'IsDescription', 'IsAddress', 'IsMobile', 'IsEmail', 'IsTaxNo', 'IsCRNo', 'IsCurrentBalance', 'SalesInvoiceTrName', 'SalesOrderTrName', 'SalesReturnTrName', 'PurchaseInvoiceTrName', 'PurchaseOrderTrName', 'PurchaseReturnTrName', 'CashRecieptTrName', 'BankRecieptTrName', 'CashPaymentTrName', 'BankPaymentTrName', 'IsInclusiveTaxUnitPrice',
                  'IsInclusiveTaxNetAmount', 'IsFlavour', 'IsShowDescription', 'IsTotalQuantity', 'IsTaxDetails', 'IsReceivedAmount', 'SalesInvoiceFooter', 'SalesReturnFooter', 'SalesOrderFooter', 'PurchaseInvoiceFooter', 'PurchaseOrderFooter', 'PurchaseReturnFooter', 'CashRecieptFooter', 'BankRecieptFooter', 'CashPaymentFooter', 'BankPaymentFooter', 'TermsAndConditionsSales', 'TermsAndConditionsPurchase', 'TermsAndConditionsSaleEstimate', 'Action', 'CompanyID', 'BranchID', 'CreatedDate', 'UpdatedDate', 'CreatedUserID', 'UpdatedUserID', "HeadFontSize", "BodyFontSize", "ContentFontSize", "FooterFontSize", "IsHSNCode", "IsProductCode")


# class PrintRestSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PrintSettings
#         fields = ('template','IsDefaultThermalPrinter','PageSize','IsCompanyLogo','IsCompanyName','IsDescription','IsAddress','IsMobile','IsEmail','IsTaxNo','IsCRNo','IsCurrentBalance','SalesInvoiceTrName','SalesOrderTrName','SalesReturnTrName','PurchaseInvoiceTrName','PurchaseOrderTrName','PurchaseReturnTrName','CashRecieptTrName','BankRecieptTrName','CashPaymentTrName','BankPaymentTrName','IsInclusiveTaxUnitPrice','IsInclusiveTaxNetAmount','IsFlavour','IsShowDescription','IsTotalQuantity','IsTaxDetails','IsReceivedAmount','SalesInvoiceFooter','SalesReturnFooter','SalesOrderFooter','PurchaseInvoiceFooter','PurchaseOrderFooter','PurchaseReturnFooter','CashRecieptFooter','BankRecieptFooter','CashPaymentFooter','BankPaymentFooter',)

class BarcodeSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = BarcodeSettings
        fields = ('id', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Zero', 'Dot', 'size', 'template', 'Description', 'IsCompanyName', 'IsProductName', 'IsPrice',
                  'IsCurrencyName', 'IsPriceCode', 'IsDescription', 'IsReceivedAmount', 'Action', 'CompanyID', 'BranchID', 'CreatedDate', 'UpdatedDate', 'CreatedUserID', 'UpdatedUserID', 'Is_MRP')


class LanguageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Language
        fields = ('CreatedUserID', 'language',)


class UserTypeSettingsSerializer(serializers.Serializer):
    UserType = serializers.CharField(max_length=250)
    # Accounts => Masters
    AccountGroupDelete = serializers.BooleanField()
    AccountGroupEdit = serializers.BooleanField()
    AccountGroupSave = serializers.BooleanField()
    AccountGroupView = serializers.BooleanField()
    AccountLedgerDelete = serializers.BooleanField()
    AccountLedgerEdit = serializers.BooleanField()
    AccountLedgerSave = serializers.BooleanField()
    AccountLedgerView = serializers.BooleanField()
    BankDelete = serializers.BooleanField()
    BankEdit = serializers.BooleanField()
    BankSave = serializers.BooleanField()
    BankView = serializers.BooleanField()
    CustomerDelete = serializers.BooleanField()
    CustomerEdit = serializers.BooleanField()
    CustomerSave = serializers.BooleanField()
    CustomerView = serializers.BooleanField()
    SupplierDelete = serializers.BooleanField()
    SupplierEdit = serializers.BooleanField()
    SupplierSave = serializers.BooleanField()
    SupplierView = serializers.BooleanField()
    TransactionTypeDelete = serializers.BooleanField()
    TransactionTypeEdit = serializers.BooleanField()
    TransactionTypeSave = serializers.BooleanField()
    TransactionTypeView = serializers.BooleanField()

    # Accounts => Transactions
    BankPaymentDelete = serializers.BooleanField()
    BankPaymentEdit = serializers.BooleanField()
    BankPaymentSave = serializers.BooleanField()
    BankPaymentView = serializers.BooleanField()
    BankReceiptDelete = serializers.BooleanField()
    BankReceiptEdit = serializers.BooleanField()
    BankReceiptSave = serializers.BooleanField()
    BankReceiptView = serializers.BooleanField()
    CashPaymentDelete = serializers.BooleanField()
    CashPaymentEdit = serializers.BooleanField()
    CashPaymentSave = serializers.BooleanField()
    CashPaymentView = serializers.BooleanField()
    CashReceiptDelete = serializers.BooleanField()
    CashReceiptEdit = serializers.BooleanField()
    CashReceiptSave = serializers.BooleanField()
    CashReceiptView = serializers.BooleanField()
    JournalEntryDelete = serializers.BooleanField()
    JournalEntryEdit = serializers.BooleanField()
    JournalEntrySave = serializers.BooleanField()
    JournalEntryView = serializers.BooleanField()
    CashPaymentDiscountLimit = serializers.CharField(max_length=250)
    CashReceiptDiscountLimit = serializers.CharField(max_length=250)
    BankPaymentLimit = serializers.CharField(max_length=250)
    BankReceiptLimit = serializers.CharField(max_length=250)

    # Accounts => Reports
    LedgerReportView = serializers.BooleanField()
    LedgerReportPrint = serializers.BooleanField()
    LedgerReportExport = serializers.BooleanField()
    TrialBalanceView = serializers.BooleanField()
    TrialBalancePrint = serializers.BooleanField()
    TrialBalanceExport = serializers.BooleanField()
    ProfitAndLossView = serializers.BooleanField()
    ProfitAndLossPrint = serializers.BooleanField()
    ProfitAndLossExport = serializers.BooleanField()
    BalanceSheetView = serializers.BooleanField()
    BalanceSheetPrint = serializers.BooleanField()
    BalanceSheetExport = serializers.BooleanField()
    DailyReportView = serializers.BooleanField()
    DailyReportPrint = serializers.BooleanField()
    DailyReportExport = serializers.BooleanField()
    CashBookView = serializers.BooleanField()
    CashBookPrint = serializers.BooleanField()
    CashBookExport = serializers.BooleanField()
    VATReportView = serializers.BooleanField()
    VATReportPrint = serializers.BooleanField()
    VATReportExport = serializers.BooleanField()

    # Accounts => Masters
    ProductGroupView = serializers.BooleanField()
    ProductGroupSave = serializers.BooleanField()
    ProductGroupEdit = serializers.BooleanField()
    ProductGroupDelete = serializers.BooleanField()
    BrandsView = serializers.BooleanField()
    BrandsSave = serializers.BooleanField()
    BrandsEdit = serializers.BooleanField()
    BrandsDelete = serializers.BooleanField()
    TaxCategoriesView = serializers.BooleanField()
    TaxCategoriesSave = serializers.BooleanField()
    TaxCategoriesEdit = serializers.BooleanField()
    TaxCategoriesDelete = serializers.BooleanField()
    PriceCategoriesView = serializers.BooleanField()
    PriceCategoriesSave = serializers.BooleanField()
    PriceCategoriesEdit = serializers.BooleanField()
    PriceCategoriesDelete = serializers.BooleanField()
    WarehouseView = serializers.BooleanField()
    WarehouseSave = serializers.BooleanField()
    WarehouseEdit = serializers.BooleanField()
    WarehouseDelete = serializers.BooleanField()
    ProductCategoriesView = serializers.BooleanField()
    ProductCategoriesSave = serializers.BooleanField()
    ProductCategoriesEdit = serializers.BooleanField()
    ProductCategoriesDelete = serializers.BooleanField()
    ProductsView = serializers.BooleanField()
    ProductsSave = serializers.BooleanField()
    ProductsEdit = serializers.BooleanField()
    ProductsDelete = serializers.BooleanField()
    RoutesView = serializers.BooleanField()
    RoutesSave = serializers.BooleanField()
    RoutesEdit = serializers.BooleanField()
    RoutesDelete = serializers.BooleanField()
    UnitsView = serializers.BooleanField()
    UnitsSave = serializers.BooleanField()
    UnitsEdit = serializers.BooleanField()
    UnitsDelete = serializers.BooleanField()
    # Accounts => Transactions

    PurchaseInvoicesView = serializers.BooleanField()
    PurchaseInvoicesSave = serializers.BooleanField()
    PurchaseInvoicesEdit = serializers.BooleanField()
    PurchaseInvoicesDelete = serializers.BooleanField()
    WorkOrdersView = serializers.BooleanField()
    WorkOrdersSave = serializers.BooleanField()
    WorkOrdersEdit = serializers.BooleanField()
    WorkOrdersDelete = serializers.BooleanField()
    PurchaseReturnsView = serializers.BooleanField()
    PurchaseReturnsSave = serializers.BooleanField()
    PurchaseReturnsEdit = serializers.BooleanField()
    PurchaseReturnsDelete = serializers.BooleanField()
    SaleInvoicesView = serializers.BooleanField()
    SaleInvoicesSave = serializers.BooleanField()
    SaleInvoicesEdit = serializers.BooleanField()
    SaleInvoicesDelete = serializers.BooleanField()
    SaleReturnsView = serializers.BooleanField()
    SaleReturnsSave = serializers.BooleanField()
    SaleReturnsEdit = serializers.BooleanField()
    SaleReturnsDelete = serializers.BooleanField()
    OpeningStockView = serializers.BooleanField()
    OpeningStockSave = serializers.BooleanField()
    OpeningStockEdit = serializers.BooleanField()
    OpeningStockDelete = serializers.BooleanField()
    StockTransferView = serializers.BooleanField()
    StockTransferSave = serializers.BooleanField()
    StockTransferEdit = serializers.BooleanField()
    StockTransferDelete = serializers.BooleanField()
    ExcessStocksView = serializers.BooleanField()
    ExcessStocksSave = serializers.BooleanField()
    ExcessStocksEdit = serializers.BooleanField()
    ExcessStocksDelete = serializers.BooleanField()
    ShortageStocksView = serializers.BooleanField()
    ShortageStocksSave = serializers.BooleanField()
    ShortageStocksEdit = serializers.BooleanField()
    ShortageStocksDelete = serializers.BooleanField()
    DamageStocksView = serializers.BooleanField()
    DamageStocksSave = serializers.BooleanField()
    DamageStocksEdit = serializers.BooleanField()
    DamageStocksDelete = serializers.BooleanField()
    UsedStocksView = serializers.BooleanField()
    UsedStocksSave = serializers.BooleanField()
    UsedStocksEdit = serializers.BooleanField()
    UsedStocksDelete = serializers.BooleanField()
    StockAdjustmentsView = serializers.BooleanField()
    StockAdjustmentsSave = serializers.BooleanField()
    StockAdjustmentsEdit = serializers.BooleanField()
    StockAdjustmentsDelete = serializers.BooleanField()
    SalesOrderView = serializers.BooleanField()
    SalesOrderSave = serializers.BooleanField()
    SalesOrderEdit = serializers.BooleanField()
    SalesOrderDelete = serializers.BooleanField()
    # -------------------------------------------
    SalesEstimateView = serializers.BooleanField()
    SalesEstimateSave = serializers.BooleanField()
    SalesEstimateEdit = serializers.BooleanField()
    SalesEstimateDelete = serializers.BooleanField()
    # -------------------------------------------
    PurchaseInvoicesDiscountLimit = serializers.CharField(max_length=250)
    PurchaseReturnsDiscountLimit = serializers.CharField(max_length=250)
    SaleInvoicesDiscountLimit = serializers.CharField(max_length=250)
    SaleReturnsDiscountLimit = serializers.CharField(max_length=250)

    # Inventory => Reports
    StockReportView = serializers.BooleanField()
    StockReportPrint = serializers.BooleanField()
    StockReportExport = serializers.BooleanField()
    StockValueReportView = serializers.BooleanField()
    StockValueReportPrint = serializers.BooleanField()
    StockValueReportExport = serializers.BooleanField()
    PurchaseReportView = serializers.BooleanField()
    PurchaseReportPrint = serializers.BooleanField()
    PurchaseReportExport = serializers.BooleanField()
    SalesReportView = serializers.BooleanField()
    SalesReportPrint = serializers.BooleanField()
    SalesReportExport = serializers.BooleanField()
    SalesIntegratedReportView = serializers.BooleanField()
    SalesIntegratedReportPrint = serializers.BooleanField()
    SalesIntegratedReportExport = serializers.BooleanField()
    SalesRegisterReportView = serializers.BooleanField()
    SalesRegisterReportPrint = serializers.BooleanField()
    SalesRegisterReportExport = serializers.BooleanField()
    BillWiseReportView = serializers.BooleanField()
    BillWiseReportPrint = serializers.BooleanField()
    BillWiseReportExport = serializers.BooleanField()
    ExcessStockReportView = serializers.BooleanField()
    ExcessStockReportPrint = serializers.BooleanField()
    ExcessStockReportExport = serializers.BooleanField()
    DamageStockReportView = serializers.BooleanField()
    DamageStockReportPrint = serializers.BooleanField()
    DamageStockReportExport = serializers.BooleanField()
    UsedStockReportView = serializers.BooleanField()
    UsedStockReportPrint = serializers.BooleanField()
    UsedStockReportExport = serializers.BooleanField()
    BatchWiseReportView = serializers.BooleanField()
    BatchWiseReportPrint = serializers.BooleanField()
    BatchWiseReportExport = serializers.BooleanField()

    # Payroll => Masters
    DepartmentsView = serializers.BooleanField()
    DepartmentsSave = serializers.BooleanField()
    DepartmentsEdit = serializers.BooleanField()
    DepartmentsDelete = serializers.BooleanField()
    DesignationsView = serializers.BooleanField()
    DesignationsSave = serializers.BooleanField()
    DesignationsEdit = serializers.BooleanField()
    DesignationsDelete = serializers.BooleanField()
    EmployeeView = serializers.BooleanField()
    EmployeeSave = serializers.BooleanField()
    EmployeeEdit = serializers.BooleanField()
    EmployeeDelete = serializers.BooleanField()

    # Settings
    PrinterView = serializers.BooleanField()
    BarcodeView = serializers.BooleanField()
    PrintBarcodeView = serializers.BooleanField()


# class GeneralSettingsListSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = GeneralSettings
#         fields = ('SettingsType')
