from rest_framework import serializers
from brands.models import Settings, PrintSettings, BarcodeSettings, Language


class SettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Settings
        fields = ('id','BranchID','PriceList','GroupName','SettingsType','SettingsValue','CreatedDate','CreatedUserID')


class SettingsRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Settings
        fields = ('id','SettingsID','BranchID','Action','PriceList','GroupName','SettingsType','SettingsValue',
        	'CreatedDate','CreatedUserID')


class PrintSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = PrintSettings
        fields = ('id','template','IsDefaultThermalPrinter','PageSize','IsCompanyLogo','IsCompanyName','IsDescription','IsAddress','IsMobile','IsEmail','IsTaxNo','IsCRNo','IsCurrentBalance','SalesInvoiceTrName','SalesOrderTrName','SalesReturnTrName','PurchaseInvoiceTrName','PurchaseOrderTrName','PurchaseReturnTrName','CashRecieptTrName','BankRecieptTrName','CashPaymentTrName','BankPaymentTrName','IsInclusiveTaxUnitPrice','IsInclusiveTaxNetAmount','IsFlavour','IsShowDescription','IsTotalQuantity','IsTaxDetails','IsReceivedAmount','SalesInvoiceFooter','SalesReturnFooter','SalesOrderFooter','PurchaseInvoiceFooter','PurchaseOrderFooter','PurchaseReturnFooter','CashRecieptFooter','BankRecieptFooter','CashPaymentFooter','BankPaymentFooter','Action','CompanyID','BranchID','CreatedDate','UpdatedDate','CreatedUserID','UpdatedUserID',)


# class PrintRestSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PrintSettings
#         fields = ('template','IsDefaultThermalPrinter','PageSize','IsCompanyLogo','IsCompanyName','IsDescription','IsAddress','IsMobile','IsEmail','IsTaxNo','IsCRNo','IsCurrentBalance','SalesInvoiceTrName','SalesOrderTrName','SalesReturnTrName','PurchaseInvoiceTrName','PurchaseOrderTrName','PurchaseReturnTrName','CashRecieptTrName','BankRecieptTrName','CashPaymentTrName','BankPaymentTrName','IsInclusiveTaxUnitPrice','IsInclusiveTaxNetAmount','IsFlavour','IsShowDescription','IsTotalQuantity','IsTaxDetails','IsReceivedAmount','SalesInvoiceFooter','SalesReturnFooter','SalesOrderFooter','PurchaseInvoiceFooter','PurchaseOrderFooter','PurchaseReturnFooter','CashRecieptFooter','BankRecieptFooter','CashPaymentFooter','BankPaymentFooter',)

class BarcodeSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = BarcodeSettings
        fields = ('id','One','Two','Three','Four','Five','Six','Seven','Eight','Nine','Zero','Dot','size','template','Description','IsCompanyName','IsProductName','IsPrice','IsCurrencyName','IsPriceCode','IsDescription','IsReceivedAmount','Action','CompanyID','BranchID','CreatedDate','UpdatedDate','CreatedUserID','UpdatedUserID','Is_MRP')


class LanguageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Language
        fields = ('CreatedUserID','language',)