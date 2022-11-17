import ast
import datetime
import json
import time
from io import BytesIO

import pdfkit
import xlwt
from django import template
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.utils.translation import activate
from django.utils.translation import ugettext_lazy as _
from num2words import num2words
from PyPDF2 import PdfFileReader, PdfFileWriter
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, renderer_classes,authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication

# from brands.models import Settings, Settings_Log, PrintSettings, BarcodeSettings, Language
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from api.v10.bankReconciliationStatement.functions import (
    bank_reconslation_date,
    export_to_excel_bank_reconslation,
)
from api.v10.brands.serializers import ListSerializer
from api.v10.companySettings.serializers import CompanySettingsPrintRestSerializer
from api.v10.expense.functions import expence_excel_data, export_to_excel_expence
from api.v10.expense.serializers import ExpenseMasterSerializer
from api.v10.journals.serializers import JournalMasterRestSerializer
from api.v10.ledgerPosting.functions import (
    balanceSheet_excel_data,
    bank_book_report_data,
    cash_book_report_data,
    export_to_excel_balanceSheet,
    export_to_excel_balanceSingleSideSheet,
    export_to_excel_bankBook,
    export_to_excel_cashBook,
    export_to_excel_profitAndLoss,
    export_to_excel_trialBalance,
    ledgerReport_excel_data,
    outStandingReport_excel_data,
    profitAndLoss_excel_data,
    trialBalance_excel_data,
)
from api.v10.payments.functions import paymentReport_excel_data
from api.v10.payments.serializers import PaymentMasterRestSerializer
from api.v10.products.functions import batch_excel_data, export_to_excel_batch
from api.v10.purchaseOrders.serializers import PurchaseOrderMasterRestSerializer
from api.v10.purchaseReturns.serializers import PurchaseReturnMasterRestSerializer
from api.v10.purchases.functions import (
    export_to_excel_purchaseRetun,
    purchase_excel_data,
    purchaseReturn_excel_data,
)
from api.v10.purchases.serializers import PurchaseMasterRestSerializer
from api.v10.receipts.functions import receiptReport_excel_data
from api.v10.receipts.serializers import ReceiptMasterRestSerializer
from api.v10.sales.functions import (
    billWise_profit_report_data,
    export_to_excel_billWise,
    export_to_excel_Stock,
    sales_excel_data,
    salesReturn_excel_data,
    stock_report_data,
    taxSummary_excel_data,
)
from api.v10.sales.serializers import SalesMasterRestSerializer
from api.v10.salesEstimates.serializers import SalesEstimateMasterRestSerializer
from api.v10.salesOrders.serializers import SalesOrderMasterRestSerializer
from api.v10.salesReturns.serializers import SalesReturnMasterRestSerializer
from api.v10.settings import serializers
from api.v10.settings.functions import (
    convert_to_base64,
    create_or_update_user_type_settings,
    export_to_excel,
    generate_serializer_errors,
    get_auto_id,
    get_country_time,
    get_user_type_settings,
)
from api.v10.stockTransfers.serializers import StockTransferMaster_IDRestSerializer
from api.v10.workOrder.serializers import WorkOrderSerializer
from brands import models
from main.functions import converted_float, get_GeneralSettings, get_company


@api_view(["POST"])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def create_settings(request):
    today = datetime.datetime.now()
    serialized = serializers.SettingsSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data["BranchID"]
        PriceList = serialized.data["PriceList"]
        GroupName = serialized.data["GroupName"]
        SettingsType = serialized.data["SettingsType"]
        SettingsValue = serialized.data["SettingsValue"]
        CreatedUserID = serialized.data["CreatedUserID"]

        Action = "A"

        SettingsID = get_auto_id(Settings, BranchID)

        models.Settings.objects.create(
            SettingsID=SettingsID,
            BranchID=BranchID,
            PriceList=PriceList,
            GroupName=GroupName,
            SettingsType=SettingsType,
            SettingsValue=SettingsValue,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
        )

        models.Settings_Log.objects.create(
            TransactionID=SettingsID,
            BranchID=BranchID,
            PriceList=PriceList,
            GroupName=GroupName,
            SettingsType=SettingsType,
            SettingsValue=SettingsValue,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
        )

        data = {"SettingsID": SettingsID}
        data.update(serialized.data)
        response_data = {"StatusCode": 6000, "data": data}

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors),
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def edit_settings(request, pk):
    today = datetime.datetime.now()
    serialized = serializers.SettingsSerializer(data=request.data)
    instance = None
    if models.Settings.objects.filter(pk=pk).exists():
        instance = models.Settings.objects.get(pk=pk)

        SettingsID = instance.SettingsID
        BranchID = instance.BranchID
        CreatedUserID = instance.CreatedUserID

    if instance:
        if serialized.is_valid():
            PriceList = serialized.data["PriceList"]
            GroupName = serialized.data["GroupName"]
            SettingsType = serialized.data["SettingsType"]
            SettingsValue = serialized.data["SettingsValue"]

            Action = "M"

            instance.PriceList = PriceList
            instance.GroupName = GroupName
            instance.SettingsType = SettingsType
            instance.SettingsValue = SettingsValue
            instance.Action = Action
            instance.save()
            models.Settings_Log.objects.create(
                TransactionID=SettingsID,
                BranchID=BranchID,
                PriceList=PriceList,
                GroupName=GroupName,
                SettingsType=SettingsType,
                SettingsValue=SettingsValue,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
            )

            data = {"SettingsID": SettingsID}
            data.update(serialized.data)
            response_data = {"StatusCode": 6000, "data": data}

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6001,
                "message": generate_serializer_errors(serialized._errors),
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {"StatusCode": 6001, "message": "Settings Not Found!"}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def list_settings(request):
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data["BranchID"]

        if models.Settings.objects.filter(BranchID=BranchID).exists():

            instances = models.Settings.objects.filter(BranchID=BranchID)

            serialized = serializers.SettingsRestSerializer(instances, many=True)

            response_data = {"StatusCode": 6000, "data": serialized.data}

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Settings Not Found in this BranchID!",
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def document_settings(request, pk):
    instance = None
    if models.Settings.objects.filter(pk=pk).exists():
        instance = models.Settings.objects.get(pk=pk)
    if instance:
        serialized = serializers.SettingsRestSerializer(instance)
        response_data = {"StatusCode": 6000, "data": serialized.data}
    else:
        response_data = {"StatusCode": 6001, "message": "Settings Not Found!"}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def delete_settings(request, pk):
    today = datetime.datetime.now()
    instance = None
    if models.Settings.objects.filter(pk=pk).exists():
        instance = models.Settings.objects.get(pk=pk)
    if instance:

        SettingsID = instance.SettingsID
        BranchID = instance.BranchID
        PriceList = instance.PriceList
        GroupName = instance.GroupName
        SettingsType = instance.SettingsType
        SettingsValue = instance.SettingsValue
        CreatedUserID = instance.CreatedUserID
        Action = "D"

        instance.delete()

        models.Settings_Log.objects.create(
            TransactionID=SettingsID,
            BranchID=BranchID,
            PriceList=PriceList,
            GroupName=GroupName,
            SettingsType=SettingsType,
            SettingsValue=SettingsValue,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
        )
        response_data = {
            "StatusCode": 6000,
            "message": "Settings Deleted Successfully!",
        }
    else:
        response_data = {"StatusCode": 6001, "message": "Settings Not Found!"}

    return Response(response_data, status=status.HTTP_200_OK)


# @api_view(['POST'])
# @permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
# @renderer_classes((JSONRenderer,))
# def print_settings(request):
#     today = datetime.datetime.now()
#     serialized = serializers.PrintSettingsSerializer(data=request.data)
#     if serialized.is_valid():
#         data = request.data
#         CompanyID = data['CompanyID']
#         CompanyID = get_company(CompanyID)
#         CreatedUserID = data['CreatedUserID']
#         BranchID = data['BranchID']

#         template = serialized.data['template']
#         IsDefaultThermalPrinter = serialized.data['IsDefaultThermalPrinter']
#         PageSize = serialized.data['PageSize']
#         IsCompanyLogo = serialized.data['IsCompanyLogo']
#         IsCompanyName = serialized.data['IsCompanyName']
#         IsDescription = serialized.data['IsDescription']
#         IsAddress = serialized.data['IsAddress']
#         IsMobile = serialized.data['IsMobile']
#         IsEmail = serialized.data['IsEmail']
#         IsTaxNo = serialized.data['IsTaxNo']
#         IsCRNo = serialized.data['IsCRNo']
#         IsCurrentBalance = serialized.data['IsCurrentBalance']
#         SalesInvoiceTrName = serialized.data['SalesInvoiceTrName']
#         SalesOrderTrName = serialized.data['SalesOrderTrName']
#         SalesReturnTrName = serialized.data['SalesReturnTrName']
#         PurchaseInvoiceTrName = serialized.data['PurchaseInvoiceTrName']
#         PurchaseOrderTrName = serialized.data['PurchaseOrderTrName']
#         PurchaseReturnTrName = serialized.data['PurchaseReturnTrName']
#         CashRecieptTrName = serialized.data['CashRecieptTrName']
#         BankRecieptTrName = serialized.data['BankRecieptTrName']
#         CashPaymentTrName = serialized.data['CashPaymentTrName']
#         BankPaymentTrName = serialized.data['BankPaymentTrName']
#         IsInclusiveTaxUnitPrice = serialized.data['IsInclusiveTaxUnitPrice']
#         IsInclusiveTaxNetAmount = serialized.data['IsInclusiveTaxNetAmount']
#         IsFlavour = serialized.data['IsFlavour']
#         IsShowDescription = serialized.data['IsShowDescription']
#         IsTotalQuantity = serialized.data['IsTotalQuantity']
#         IsTaxDetails = serialized.data['IsTaxDetails']
#         IsHSNCode = serialized.data['IsHSNCode']
#         IsProductCode = serialized.data['IsProductCode']

#         IsReceivedAmount = serialized.data['IsReceivedAmount']
#         # print Bank Details START
#         IsBankDetails = serialized.data['IsBankDetails']
#         BankNameFooter = serialized.data['BankNameFooter']
#         AccountNumberFooter = serialized.data['AccountNumberFooter']
#         BranchIFCFooter = serialized.data['BranchIFCFooter']
#         # print Bank Details END
#         SalesInvoiceFooter = serialized.data['SalesInvoiceFooter']
#         SalesReturnFooter = serialized.data['SalesReturnFooter']
#         SalesOrderFooter = serialized.data['SalesOrderFooter']
#         PurchaseInvoiceFooter = serialized.data['PurchaseInvoiceFooter']
#         PurchaseOrderFooter = serialized.data['PurchaseOrderFooter']
#         PurchaseReturnFooter = serialized.data['PurchaseReturnFooter']
#         CashRecieptFooter = serialized.data['CashRecieptFooter']
#         BankRecieptFooter = serialized.data['BankRecieptFooter']
#         CashPaymentFooter = serialized.data['CashPaymentFooter']
#         BankPaymentFooter = serialized.data['BankPaymentFooter']
#         TermsAndConditionsSales = serialized.data['TermsAndConditionsSales']
#         TermsAndConditionsPurchase = serialized.data['TermsAndConditionsPurchase']
#         TermsAndConditionsSaleEstimate = serialized.data['TermsAndConditionsSaleEstimate']
#         HeadFontSize = serialized.data['HeadFontSize']
#         BodyFontSize = serialized.data['BodyFontSize']
#         ContentFontSize = serialized.data['ContentFontSize']
#         FooterFontSize = serialized.data['FooterFontSize']
#         Action = "A"
#         print_settings_id = None
#         if models.PrintSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
#             print_settings_id = models.PrintSettings.objects.get(
#                 CompanyID=CompanyID, BranchID=BranchID).pk
#             models.PrintSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID).update(
#                 template=template,
#                 IsDefaultThermalPrinter=IsDefaultThermalPrinter,
#                 PageSize=PageSize,
#                 IsCompanyLogo=IsCompanyLogo,
#                 IsCompanyName=IsCompanyName,
#                 IsDescription=IsDescription,
#                 IsAddress=IsAddress,
#                 IsMobile=IsMobile,
#                 IsEmail=IsEmail,
#                 IsTaxNo=IsTaxNo,
#                 IsCRNo=IsCRNo,
#                 IsCurrentBalance=IsCurrentBalance,
#                 SalesInvoiceTrName=SalesInvoiceTrName,
#                 SalesOrderTrName=SalesOrderTrName,
#                 SalesReturnTrName=SalesReturnTrName,
#                 PurchaseInvoiceTrName=PurchaseInvoiceTrName,
#                 PurchaseOrderTrName=PurchaseOrderTrName,
#                 PurchaseReturnTrName=PurchaseReturnTrName,
#                 CashRecieptTrName=CashRecieptTrName,
#                 BankRecieptTrName=BankRecieptTrName,
#                 CashPaymentTrName=CashPaymentTrName,
#                 BankPaymentTrName=BankPaymentTrName,
#                 IsInclusiveTaxUnitPrice=IsInclusiveTaxUnitPrice,
#                 IsInclusiveTaxNetAmount=IsInclusiveTaxNetAmount,
#                 IsFlavour=IsFlavour,
#                 IsShowDescription=IsShowDescription,
#                 IsTotalQuantity=IsTotalQuantity,
#                 IsTaxDetails=IsTaxDetails,
#                 IsHSNCode=IsHSNCode,
#                 IsProductCode=IsProductCode,
#                 IsReceivedAmount=IsReceivedAmount,
#                 # print Bank Details START
#                 IsBankDetails=IsBankDetails,
#                 BankNameFooter=BankNameFooter,
#                 AccountNumberFooter=AccountNumberFooter,
#                 BranchIFCFooter=BranchIFCFooter,
#                 # print Bank Details END
#                 SalesInvoiceFooter=SalesInvoiceFooter,
#                 SalesReturnFooter=SalesReturnFooter,
#                 SalesOrderFooter=SalesOrderFooter,
#                 PurchaseInvoiceFooter=PurchaseInvoiceFooter,
#                 PurchaseOrderFooter=PurchaseOrderFooter,
#                 PurchaseReturnFooter=PurchaseReturnFooter,
#                 CashRecieptFooter=CashRecieptFooter,
#                 BankRecieptFooter=BankRecieptFooter,
#                 CashPaymentFooter=CashPaymentFooter,
#                 BankPaymentFooter=BankPaymentFooter,
#                 TermsAndConditionsSales=TermsAndConditionsSales,
#                 TermsAndConditionsPurchase=TermsAndConditionsPurchase,
#                 TermsAndConditionsSaleEstimate=TermsAndConditionsSaleEstimate,
#                 Action=Action,
#                 BranchID=BranchID,
#                 CreatedUserID=CreatedUserID,
#                 CreatedDate=today,
#                 CompanyID=CompanyID,
#                 HeadFontSize=HeadFontSize,
#                 BodyFontSize=BodyFontSize,
#                 ContentFontSize=ContentFontSize,
#                 FooterFontSize=FooterFontSize,
#             )
#         else:
#             models.PrintSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID).create(
#                 template=template,
#                 IsDefaultThermalPrinter=IsDefaultThermalPrinter,
#                 PageSize=PageSize,
#                 IsCompanyLogo=IsCompanyLogo,
#                 IsCompanyName=IsCompanyName,
#                 IsDescription=IsDescription,
#                 IsAddress=IsAddress,
#                 IsMobile=IsMobile,
#                 IsEmail=IsEmail,
#                 IsTaxNo=IsTaxNo,
#                 IsCRNo=IsCRNo,
#                 IsCurrentBalance=IsCurrentBalance,
#                 SalesInvoiceTrName=SalesInvoiceTrName,
#                 SalesOrderTrName=SalesOrderTrName,
#                 SalesReturnTrName=SalesReturnTrName,
#                 PurchaseInvoiceTrName=PurchaseInvoiceTrName,
#                 PurchaseOrderTrName=PurchaseOrderTrName,
#                 PurchaseReturnTrName=PurchaseReturnTrName,
#                 CashRecieptTrName=CashRecieptTrName,
#                 BankRecieptTrName=BankRecieptTrName,
#                 CashPaymentTrName=CashPaymentTrName,
#                 BankPaymentTrName=BankPaymentTrName,
#                 IsInclusiveTaxUnitPrice=IsInclusiveTaxUnitPrice,
#                 IsInclusiveTaxNetAmount=IsInclusiveTaxNetAmount,
#                 IsFlavour=IsFlavour,
#                 IsShowDescription=IsShowDescription,
#                 IsTotalQuantity=IsTotalQuantity,
#                 IsTaxDetails=IsTaxDetails,
#                 IsHSNCode=IsHSNCode,
#                 IsProductCode=IsProductCode,
#                 IsReceivedAmount=IsReceivedAmount,
#                  # print Bank Details START
#                 IsBankDetails=IsBankDetails,
#                 BankNameFooter=BankNameFooter,
#                 AccountNumberFooter=AccountNumberFooter,
#                 BranchIFCFooter=BranchIFCFooter,
#                 # print Bank Details END
#                 SalesInvoiceFooter=SalesInvoiceFooter,
#                 SalesReturnFooter=SalesReturnFooter,
#                 SalesOrderFooter=SalesOrderFooter,
#                 PurchaseInvoiceFooter=PurchaseInvoiceFooter,
#                 PurchaseOrderFooter=PurchaseOrderFooter,
#                 PurchaseReturnFooter=PurchaseReturnFooter,
#                 CashRecieptFooter=CashRecieptFooter,
#                 BankRecieptFooter=BankRecieptFooter,
#                 CashPaymentFooter=CashPaymentFooter,
#                 BankPaymentFooter=BankPaymentFooter,
#                 TermsAndConditionsSales=TermsAndConditionsSales,
#                 TermsAndConditionsPurchase=TermsAndConditionsPurchase,
#                 TermsAndConditionsSaleEstimate=TermsAndConditionsSaleEstimate,
#                 Action=Action,
#                 BranchID=BranchID,
#                 CreatedUserID=CreatedUserID,
#                 CreatedDate=today,
#                 CompanyID=CompanyID,
#                 HeadFontSize=HeadFontSize,
#                 BodyFontSize=BodyFontSize,
#                 ContentFontSize=ContentFontSize,
#                 FooterFontSize=FooterFontSize,
#             )
#             print_settings_id = models.PrintSettings.objects.get(
#                 CompanyID=CompanyID, BranchID=BranchID).pk
#         response_data = {
#             "StatusCode": 6000,
#             "data": serialized.data,
#             "print_settings_id": print_settings_id
#         }
#         return Response(response_data, status=status.HTTP_200_OK)
#     else:
#         response_data = {
#             "StatusCode": 6001,
#             "message": generate_serializer_errors(serialized._errors)
#         }
#         return Response(response_data, status=status.HTTP_200_OK)


# @api_view(['POST'])
# @permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
# @renderer_classes((JSONRenderer,))
# def print_view(request,pk):
#     data = request.data
#     CompanyID = data['CompanyID']
#     CompanyID = get_company(CompanyID)
#     CreatedUserID = data['CreatedUserID']

#     instance = None
#     if models.PrintSettings.objects.filter(pk=pk).exists():
#         instance = models.PrintSettings.objects.get(pk=pk)
#         serialized = PrintRestSerializer(instance)
#         response_data = {
#             "StatusCode" : 6000,
#             "data" : serialized.data
#         }
#     else:
#         response_data = {
#             "StatusCode" : 6001,
#             "message" : "Brand Not Fount!"
#         }
#     return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def barcode_settings(request):
    today = datetime.datetime.now()
    serialized = serializers.BarcodeSettingsSerializer(data=request.data)
    if serialized.is_valid():
        data = request.data
        CompanyID = data["CompanyID"]
        CompanyID = get_company(CompanyID)
        CreatedUserID = data["CreatedUserID"]
        BranchID = data["BranchID"]

        One = serialized.data["One"]
        Two = serialized.data["Two"]
        Three = serialized.data["Three"]
        Four = serialized.data["Four"]
        Five = serialized.data["Five"]
        Six = serialized.data["Six"]
        Seven = serialized.data["Seven"]
        Eight = serialized.data["Eight"]
        Nine = serialized.data["Nine"]
        Zero = serialized.data["Zero"]
        Dot = serialized.data["Dot"]
        size = serialized.data["size"]
        template = serialized.data["template"]
        Description = serialized.data["Description"]
        IsCompanyName = serialized.data["IsCompanyName"]
        IsProductName = serialized.data["IsProductName"]
        IsPrice = serialized.data["IsPrice"]
        IsCurrencyName = serialized.data["IsCurrencyName"]
        IsPriceCode = serialized.data["IsPriceCode"]
        IsDescription = serialized.data["IsDescription"]
        IsProductDescription = serialized.data["IsProductDescription"]
        Is_MRP = serialized.data["Is_MRP"]

        Action = "A"
        print_settings_id = None
        if models.BarcodeSettings.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID
        ).exists():
            print_settings_id = models.BarcodeSettings.objects.get(
                CompanyID=CompanyID, BranchID=BranchID
            ).pk
            models.BarcodeSettings.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID
            ).update(
                One=One,
                Two=Two,
                Three=Three,
                Four=Four,
                Five=Five,
                Six=Six,
                Seven=Seven,
                Eight=Eight,
                Nine=Nine,
                Zero=Zero,
                Dot=Dot,
                size=size,
                template=template,
                Description=Description,
                IsCompanyName=IsCompanyName,
                IsProductName=IsProductName,
                IsPrice=IsPrice,
                IsCurrencyName=IsCurrencyName,
                IsPriceCode=IsPriceCode,
                IsDescription=IsDescription,
                IsProductDescription=IsProductDescription,
                Is_MRP=Is_MRP,
                Action=Action,
                BranchID=BranchID,
                CreatedUserID=CreatedUserID,
                UpdatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )
        else:
            models.BarcodeSettings.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID
            ).create(
                One=One,
                Two=Two,
                Three=Three,
                Four=Four,
                Five=Five,
                Six=Six,
                Seven=Seven,
                Eight=Eight,
                Nine=Nine,
                Zero=Zero,
                Dot=Dot,
                size=size,
                template=template,
                Description=Description,
                IsCompanyName=IsCompanyName,
                IsProductName=IsProductName,
                IsPrice=IsPrice,
                IsCurrencyName=IsCurrencyName,
                IsPriceCode=IsPriceCode,
                IsDescription=IsDescription,
                IsProductDescription=IsProductDescription,
                Is_MRP=Is_MRP,
                Action=Action,
                BranchID=BranchID,
                CreatedUserID=CreatedUserID,
                UpdatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors),
        }
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def language(request):
    today = datetime.datetime.now()
    serialized = serializers.LanguageSerializer(data=request.data)
    if serialized.is_valid():
        data = request.data
        CreatedUserID = data["CreatedUserID"]
        language = data["language"]

        Action = "A"
        print_settings_id = None
        if models.Language.objects.filter(CreatedUserID=CreatedUserID).exists():
            models.Language.objects.filter(CreatedUserID=CreatedUserID).update(
                language=language,
                CreatedUserID=CreatedUserID,
            )
        else:
            models.Language.objects.filter(CreatedUserID=CreatedUserID).create(
                language=language,
                CreatedUserID=CreatedUserID,
            )
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors),
        }
        return Response(response_data, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def create_user_type_settings(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    BranchID = data["BranchID"]

    today = datetime.datetime.now()
    serialized = serializers.UserTypeSettingsSerializer(data=request.data)
    if serialized.is_valid():
        Action = "A"
        User = request.user.id
        UserTypeValue = serialized.data["UserType"]
        # Accounts => Masters
        AccountGroupView = serialized.data["AccountGroupView"]
        AccountGroupSave = serialized.data["AccountGroupSave"]
        AccountGroupEdit = serialized.data["AccountGroupEdit"]
        AccountGroupDelete = serialized.data["AccountGroupDelete"]
        AccountLedgerView = serialized.data["AccountLedgerView"]
        AccountLedgerSave = serialized.data["AccountLedgerSave"]
        AccountLedgerEdit = serialized.data["AccountLedgerEdit"]
        AccountLedgerDelete = serialized.data["AccountLedgerDelete"]
        BankView = serialized.data["BankView"]
        BankSave = serialized.data["BankSave"]
        BankEdit = serialized.data["BankEdit"]
        BankDelete = serialized.data["BankDelete"]
        CustomerView = serialized.data["CustomerView"]
        CustomerSave = serialized.data["CustomerSave"]
        CustomerEdit = serialized.data["CustomerEdit"]
        CustomerDelete = serialized.data["CustomerDelete"]
        SupplierView = serialized.data["SupplierView"]
        SupplierSave = serialized.data["SupplierSave"]
        SupplierEdit = serialized.data["SupplierEdit"]
        SupplierDelete = serialized.data["SupplierDelete"]
        TransactionTypeView = serialized.data["TransactionTypeView"]
        TransactionTypeSave = serialized.data["TransactionTypeSave"]
        TransactionTypeEdit = serialized.data["TransactionTypeEdit"]
        TransactionTypeDelete = serialized.data["TransactionTypeDelete"]

        # Accounts => Transactions
        BankPaymentDelete = serialized.data["BankPaymentDelete"]
        BankPaymentEdit = serialized.data["BankPaymentEdit"]
        BankPaymentSave = serialized.data["BankPaymentSave"]
        BankPaymentView = serialized.data["BankPaymentView"]
        BankReceiptDelete = serialized.data["BankReceiptDelete"]
        BankReceiptEdit = serialized.data["BankReceiptEdit"]
        BankReceiptSave = serialized.data["BankReceiptSave"]
        BankReceiptView = serialized.data["BankReceiptView"]
        CashPaymentDelete = serialized.data["CashPaymentDelete"]
        CashPaymentEdit = serialized.data["CashPaymentEdit"]
        CashPaymentSave = serialized.data["CashPaymentSave"]
        CashPaymentView = serialized.data["CashPaymentView"]
        CashReceiptDelete = serialized.data["CashReceiptDelete"]
        CashReceiptEdit = serialized.data["CashReceiptEdit"]
        CashReceiptSave = serialized.data["CashReceiptSave"]
        CashReceiptView = serialized.data["CashReceiptView"]
        JournalEntryDelete = serialized.data["JournalEntryDelete"]
        JournalEntryEdit = serialized.data["JournalEntryEdit"]
        JournalEntrySave = serialized.data["JournalEntrySave"]
        JournalEntryView = serialized.data["JournalEntryView"]

        CashPaymentPrint = serialized.data["CashPaymentPrint"]
        CashReceiptPrint = serialized.data["CashReceiptPrint"]
        BankPaymentPrint = serialized.data["BankPaymentPrint"]
        BankReceiptPrint = serialized.data["BankReceiptPrint"]
        JournalEntryPrint = serialized.data["JournalEntryPrint"]

        try:
            CashPaymentDiscountLimit = serialized.data["CashPaymentDiscountLimit"]
        except:
            CashPaymentDiscountLimit = 0
        try:
            CashReceiptDiscountLimit = serialized.data["CashReceiptDiscountLimit"]
        except:
            CashReceiptDiscountLimit = 0
        try:
            BankPaymentLimit = serialized.data["BankPaymentLimit"]
        except:
            BankPaymentLimit = 0
        try:
            BankReceiptLimit = serialized.data["BankReceiptLimit"]
        except:
            BankReceiptLimit = 0
        # Accounts => Reports
        LedgerReportView = serialized.data["LedgerReportView"]
        LedgerReportPrint = serialized.data["LedgerReportPrint"]
        LedgerReportExport = serialized.data["LedgerReportExport"]
        TrialBalanceView = serialized.data["TrialBalanceView"]
        TrialBalancePrint = serialized.data["TrialBalancePrint"]
        TrialBalanceExport = serialized.data["TrialBalanceExport"]
        ProfitAndLossView = serialized.data["ProfitAndLossView"]
        ProfitAndLossPrint = serialized.data["ProfitAndLossPrint"]
        ProfitAndLossExport = serialized.data["ProfitAndLossExport"]
        BalanceSheetView = serialized.data["BalanceSheetView"]
        BalanceSheetPrint = serialized.data["BalanceSheetPrint"]
        BalanceSheetExport = serialized.data["BalanceSheetExport"]
        DailyReportView = serialized.data["DailyReportView"]
        DailyReportPrint = serialized.data["DailyReportPrint"]
        DailyReportExport = serialized.data["DailyReportExport"]
        CashBookView = serialized.data["CashBookView"]
        CashBookPrint = serialized.data["CashBookPrint"]
        CashBookExport = serialized.data["CashBookExport"]
        # ====
        BankBookReportView = serialized.data["BankBookReportView"]
        BankBookReportPrint = serialized.data["BankBookReportPrint"]
        BankBookReportExport = serialized.data["BankBookReportExport"]

        OutstandingReportView = serialized.data["OutstandingReportView"]
        OutstandingReportPrint = serialized.data["OutstandingReportPrint"]
        OutstandingReportExport = serialized.data["OutstandingReportExport"]

        RecieptReportView = serialized.data["RecieptReportView"]
        RecieptReportPrint = serialized.data["RecieptReportPrint"]
        RecieptReportExport = serialized.data["RecieptReportExport"]

        PaymentReportView = serialized.data["PaymentReportView"]
        PaymentReportPrint = serialized.data["PaymentReportPrint"]
        PaymentReportExport = serialized.data["PaymentReportExport"]
        # =====
        VATReportView = serialized.data["VATReportView"]
        VATReportPrint = serialized.data["VATReportPrint"]
        VATReportExport = serialized.data["VATReportExport"]

        # Account => GST Reports
        SalesGSTReportView = serialized.data["SalesGSTReportView"]
        SalesGSTReportPrint = serialized.data["SalesGSTReportPrint"]
        SalesGSTReportExport = serialized.data["SalesGSTReportExport"]

        PurchaseGSTReportView = serialized.data["PurchaseGSTReportView"]
        PurchaseGSTReportPrint = serialized.data["PurchaseGSTReportPrint"]
        PurchaseGSTReportExport = serialized.data["PurchaseGSTReportExport"]
        # Inventory => Masters
        ProductGroupView = serialized.data["ProductGroupView"]
        ProductGroupSave = serialized.data["ProductGroupSave"]
        ProductGroupEdit = serialized.data["ProductGroupEdit"]
        ProductGroupDelete = serialized.data["ProductGroupDelete"]
        BrandsView = serialized.data["BrandsView"]
        BrandsSave = serialized.data["BrandsSave"]
        BrandsEdit = serialized.data["BrandsEdit"]
        BrandsDelete = serialized.data["BrandsDelete"]
        TaxCategoriesView = serialized.data["TaxCategoriesView"]
        TaxCategoriesSave = serialized.data["TaxCategoriesSave"]
        TaxCategoriesEdit = serialized.data["TaxCategoriesEdit"]
        TaxCategoriesDelete = serialized.data["TaxCategoriesDelete"]
        PriceCategoriesView = serialized.data["PriceCategoriesView"]
        PriceCategoriesSave = serialized.data["PriceCategoriesSave"]
        PriceCategoriesEdit = serialized.data["PriceCategoriesEdit"]
        PriceCategoriesDelete = serialized.data["PriceCategoriesDelete"]
        WarehouseView = serialized.data["WarehouseView"]
        WarehouseSave = serialized.data["WarehouseSave"]
        WarehouseEdit = serialized.data["WarehouseEdit"]
        WarehouseDelete = serialized.data["WarehouseDelete"]
        ProductCategoriesView = serialized.data["ProductCategoriesView"]
        ProductCategoriesSave = serialized.data["ProductCategoriesSave"]
        ProductCategoriesEdit = serialized.data["ProductCategoriesEdit"]
        ProductCategoriesDelete = serialized.data["ProductCategoriesDelete"]
        ProductsView = serialized.data["ProductsView"]
        ProductsSave = serialized.data["ProductsSave"]
        ProductsEdit = serialized.data["ProductsEdit"]
        ProductsDelete = serialized.data["ProductsDelete"]
        RoutesView = serialized.data["RoutesView"]
        RoutesSave = serialized.data["RoutesSave"]
        RoutesEdit = serialized.data["RoutesEdit"]
        RoutesDelete = serialized.data["RoutesDelete"]
        UnitsView = serialized.data["UnitsView"]
        UnitsSave = serialized.data["UnitsSave"]
        UnitsEdit = serialized.data["UnitsEdit"]
        UnitsDelete = serialized.data["UnitsDelete"]

        # Inventory => Transaction
        PurchaseInvoicesView = serialized.data["PurchaseInvoicesView"]
        PurchaseInvoicesSave = serialized.data["PurchaseInvoicesSave"]
        PurchaseInvoicesEdit = serialized.data["PurchaseInvoicesEdit"]
        PurchaseInvoicesDelete = serialized.data["PurchaseInvoicesDelete"]
        WorkOrdersView = serialized.data["WorkOrdersView"]
        WorkOrdersSave = serialized.data["WorkOrdersSave"]
        WorkOrdersEdit = serialized.data["WorkOrdersEdit"]
        WorkOrdersDelete = serialized.data["WorkOrdersDelete"]
        PurchaseReturnsView = serialized.data["PurchaseReturnsView"]
        PurchaseReturnsSave = serialized.data["PurchaseReturnsSave"]
        PurchaseReturnsEdit = serialized.data["PurchaseReturnsEdit"]
        PurchaseReturnsDelete = serialized.data["PurchaseReturnsDelete"]
        SaleInvoicesView = serialized.data["SaleInvoicesView"]
        SaleInvoicesSave = serialized.data["SaleInvoicesSave"]
        SaleInvoicesEdit = serialized.data["SaleInvoicesEdit"]
        SaleInvoicesDelete = serialized.data["SaleInvoicesDelete"]
        SaleReturnsView = serialized.data["SaleReturnsView"]
        SaleReturnsSave = serialized.data["SaleReturnsSave"]
        SaleReturnsEdit = serialized.data["SaleReturnsEdit"]
        SaleReturnsDelete = serialized.data["SaleReturnsDelete"]
        OpeningStockView = serialized.data["OpeningStockView"]
        OpeningStockSave = serialized.data["OpeningStockSave"]
        OpeningStockEdit = serialized.data["OpeningStockEdit"]
        OpeningStockDelete = serialized.data["OpeningStockDelete"]
        StockTransferView = serialized.data["StockTransferView"]
        StockTransferSave = serialized.data["StockTransferSave"]
        StockTransferEdit = serialized.data["StockTransferEdit"]
        StockTransferDelete = serialized.data["StockTransferDelete"]
        ExcessStocksView = serialized.data["ExcessStocksView"]
        ExcessStocksSave = serialized.data["ExcessStocksSave"]
        ExcessStocksEdit = serialized.data["ExcessStocksEdit"]
        ExcessStocksDelete = serialized.data["ExcessStocksDelete"]
        ShortageStocksView = serialized.data["ShortageStocksView"]
        ShortageStocksSave = serialized.data["ShortageStocksSave"]
        ShortageStocksEdit = serialized.data["ShortageStocksEdit"]
        ShortageStocksDelete = serialized.data["ShortageStocksDelete"]
        DamageStocksView = serialized.data["DamageStocksView"]
        DamageStocksSave = serialized.data["DamageStocksSave"]
        DamageStocksEdit = serialized.data["DamageStocksEdit"]
        DamageStocksDelete = serialized.data["DamageStocksDelete"]
        UsedStocksView = serialized.data["UsedStocksView"]
        UsedStocksSave = serialized.data["UsedStocksSave"]
        UsedStocksEdit = serialized.data["UsedStocksEdit"]
        UsedStocksDelete = serialized.data["UsedStocksDelete"]
        StockAdjustmentsView = serialized.data["StockAdjustmentsView"]
        StockAdjustmentsSave = serialized.data["StockAdjustmentsSave"]
        StockAdjustmentsEdit = serialized.data["StockAdjustmentsEdit"]
        StockAdjustmentsDelete = serialized.data["StockAdjustmentsDelete"]
        SalesOrderView = serialized.data["SalesOrderView"]
        PurchaseOrderView = serialized.data["PurchaseOrderView"]
        SalesOrderSave = serialized.data["SalesOrderSave"]
        PurchaseOrderSave = serialized.data["PurchaseOrderSave"]
        SalesOrderEdit = serialized.data["SalesOrderEdit"]
        PurchaseOrderEdit = serialized.data["PurchaseOrderEdit"]
        SalesOrderDelete = serialized.data["SalesOrderDelete"]
        PurchaseOrderDelete = serialized.data["PurchaseOrderDelete"]
        SalesEstimateView = serialized.data["SalesEstimateView"]
        SalesEstimateSave = serialized.data["SalesEstimateSave"]
        SalesEstimateEdit = serialized.data["SalesEstimateEdit"]
        SalesEstimateDelete = serialized.data["SalesEstimateDelete"]
        # =====Print====

        PurchaseInvoicesPrint = serialized.data["PurchaseInvoicesPrint"]
        PurchaseReturnsPrint = serialized.data["PurchaseReturnsPrint"]
        SaleInvoicesPrint = serialized.data["SaleInvoicesPrint"]
        SalesOrderPrint = serialized.data["SalesOrderPrint"]
        PurchaseOrderPrint = serialized.data["PurchaseOrderPrint"]
        SalesEstimatePrint = serialized.data["SalesEstimatePrint"]
        SaleReturnsPrint = serialized.data["SaleReturnsPrint"]
        # ====Print=====

        try:
            PurchaseInvoicesDiscountLimit = serialized.data[
                "PurchaseInvoicesDiscountLimit"
            ]
        except:
            PurchaseInvoicesDiscountLimit = 0
        try:
            PurchaseReturnsDiscountLimit = serialized.data[
                "PurchaseReturnsDiscountLimit"
            ]
        except:
            PurchaseReturnsDiscountLimit = 0
        try:
            SaleInvoicesDiscountLimit = serialized.data["SaleInvoicesDiscountLimit"]
        except:
            SaleInvoicesDiscountLimit = 0
        try:
            SaleReturnsDiscountLimit = serialized.data["SaleReturnsDiscountLimit"]
        except:
            SaleReturnsDiscountLimit = 0
        # Inventory => Reports
        StockReportView = serialized.data["StockReportView"]
        StockReportPrint = serialized.data["StockReportPrint"]
        StockReportExport = serialized.data["StockReportExport"]
        StockValueReportView = serialized.data["StockValueReportView"]
        StockValueReportPrint = serialized.data["StockValueReportPrint"]
        StockValueReportExport = serialized.data["StockValueReportExport"]
        PurchaseReportView = serialized.data["PurchaseReportView"]
        PurchaseReportPrint = serialized.data["PurchaseReportPrint"]
        PurchaseReportExport = serialized.data["PurchaseReportExport"]
        SalesReportView = serialized.data["SalesReportView"]
        SalesReportPrint = serialized.data["SalesReportPrint"]
        SalesReportExport = serialized.data["SalesReportExport"]
        SalesIntegratedReportView = serialized.data["SalesIntegratedReportView"]
        SalesIntegratedReportPrint = serialized.data["SalesIntegratedReportPrint"]
        SalesIntegratedReportExport = serialized.data["SalesIntegratedReportExport"]
        PurchaseIntegratedReportPrint = serialized.data["PurchaseIntegratedReportPrint"]
        PurchaseIntegratedReportView = serialized.data["PurchaseIntegratedReportView"]
        PurchaseIntegratedReportExport = serialized.data["PurchaseIntegratedReportExport"]
        SalesRegisterReportView = serialized.data["SalesRegisterReportView"]
        SalesRegisterReportPrint = serialized.data["SalesRegisterReportPrint"]
        SalesRegisterReportExport = serialized.data["SalesRegisterReportExport"]
        BillWiseReportView = serialized.data["BillWiseReportView"]
        BillWiseReportPrint = serialized.data["BillWiseReportPrint"]
        BillWiseReportExport = serialized.data["BillWiseReportExport"]
        ExcessStockReportView = serialized.data["ExcessStockReportView"]
        ExcessStockReportPrint = serialized.data["ExcessStockReportPrint"]
        ExcessStockReportExport = serialized.data["ExcessStockReportExport"]
        DamageStockReportView = serialized.data["DamageStockReportView"]
        DamageStockReportPrint = serialized.data["DamageStockReportPrint"]
        DamageStockReportExport = serialized.data["DamageStockReportExport"]
        UsedStockReportView = serialized.data["UsedStockReportView"]
        UsedStockReportPrint = serialized.data["UsedStockReportPrint"]
        UsedStockReportExport = serialized.data["UsedStockReportExport"]
        BatchWiseReportView = serialized.data["BatchWiseReportView"]
        BatchWiseReportPrint = serialized.data["BatchWiseReportPrint"]
        BatchWiseReportExport = serialized.data["BatchWiseReportExport"]
        # ======****======
        ProductReportView = serialized.data["ProductReportView"]
        ProductReportPrint = serialized.data["ProductReportPrint"]
        ProductReportExport = serialized.data["ProductReportExport"]

        StockLedgerReportView = serialized.data["StockLedgerReportView"]
        StockLedgerReportPrint = serialized.data["StockLedgerReportPrint"]
        StockLedgerReportExport = serialized.data["StockLedgerReportExport"]

        PurchaseOrderReportView = serialized.data["PurchaseOrderReportView"]
        PurchaseOrderReportPrint = serialized.data["PurchaseOrderReportPrint"]
        PurchaseOrderReportExport = serialized.data["PurchaseOrderReportExport"]

        PurchaseRegisterReportView = serialized.data["PurchaseRegisterReportView"]
        PurchaseRegisterReportPrint = serialized.data["PurchaseRegisterReportPrint"]
        PurchaseRegisterReportExport = serialized.data["PurchaseRegisterReportExport"]

        SalesReturnRegisterReportView = serialized.data["SalesReturnRegisterReportView"]
        SalesReturnRegisterReportPrint = serialized.data[
            "SalesReturnRegisterReportPrint"
        ]
        SalesReturnRegisterReportExport = serialized.data[
            "SalesReturnRegisterReportExport"
        ]

        PurchaseReturnRegisterReportView = serialized.data[
            "PurchaseReturnRegisterReportView"
        ]
        PurchaseReturnRegisterReportPrint = serialized.data[
            "PurchaseReturnRegisterReportPrint"
        ]
        PurchaseReturnRegisterReportExport = serialized.data[
            "PurchaseReturnRegisterReportExport"
        ]

        SalesSummaryReportView = serialized.data["SalesSummaryReportView"]
        SalesSummaryReportPrint = serialized.data["SalesSummaryReportPrint"]
        SalesSummaryReportExport = serialized.data["SalesSummaryReportExport"]

        StockTransferRegisterReportView = serialized.data[
            "StockTransferRegisterReportView"
        ]
        StockTransferRegisterReportPrint = serialized.data[
            "StockTransferRegisterReportPrint"
        ]
        StockTransferRegisterReportExport = serialized.data[
            "StockTransferRegisterReportExport"
        ]

        InventoryFlowReportView = serialized.data["InventoryFlowReportView"]
        InventoryFlowReportPrint = serialized.data["InventoryFlowReportPrint"]
        InventoryFlowReportExport = serialized.data["InventoryFlowReportExport"]

        SupplierVsProductReportView = serialized.data["SupplierVsProductReportView"]
        SupplierVsProductReportPrint = serialized.data["SupplierVsProductReportPrint"]
        SupplierVsProductReportExport = serialized.data["SupplierVsProductReportExport"]

        ProductAnalysisReportView = serialized.data["ProductAnalysisReportView"]
        ProductAnalysisReportPrint = serialized.data["ProductAnalysisReportPrint"]
        ProductAnalysisReportExport = serialized.data["ProductAnalysisReportExport"]

        OpeningStockReportView = serialized.data["OpeningStockReportView"]
        OpeningStockReportPrint = serialized.data["OpeningStockReportPrint"]
        OpeningStockReportExport = serialized.data["OpeningStockReportExport"]

        ShortageStocksReportView = serialized.data["ShortageStocksReportView"]
        ShortageStocksReportPrint = serialized.data["ShortageStocksReportPrint"]
        ShortageStocksReportExport = serialized.data["ShortageStocksReportExport"]
        # ======****======

        # Payroll => Masters
        DepartmentsView = serialized.data["DepartmentsView"]
        DepartmentsSave = serialized.data["DepartmentsSave"]
        DepartmentsEdit = serialized.data["DepartmentsEdit"]
        DepartmentsDelete = serialized.data["DepartmentsDelete"]
        DesignationsView = serialized.data["DesignationsView"]
        DesignationsSave = serialized.data["DesignationsSave"]
        DesignationsEdit = serialized.data["DesignationsEdit"]
        DesignationsDelete = serialized.data["DesignationsDelete"]
        EmployeeView = serialized.data["EmployeeView"]
        EmployeeSave = serialized.data["EmployeeSave"]
        EmployeeEdit = serialized.data["EmployeeEdit"]
        EmployeeDelete = serialized.data["EmployeeDelete"]

        CategoriesView = serialized.data["CategoriesView"]
        CategoriesSave = serialized.data["CategoriesSave"]
        CategoriesEdit = serialized.data["CategoriesEdit"]
        CategoriesDelete = serialized.data["CategoriesDelete"]

        # Settings
        PrinterView = serialized.data["PrinterView"]
        BarcodeView = serialized.data["BarcodeView"]
        PrintBarcodeView = serialized.data["PrintBarcodeView"]
        UserType_instance = models.UserType.objects.get(
            id=UserTypeValue, CompanyID=CompanyID, BranchID=BranchID
        )
        # arguments order :- User, GroupName, SettingsType, SettingsValue, usertype
        # Accounts => Masters
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "AccountGroupView",
            AccountGroupView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "AccountGroupSave",
            AccountGroupSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "AccountGroupEdit",
            AccountGroupEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "AccountGroupDelete",
            AccountGroupDelete,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "AccountLedgerView",
            AccountLedgerView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "AccountLedgerSave",
            AccountLedgerSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "AccountLedgerEdit",
            AccountLedgerEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "AccountLedgerDelete",
            AccountLedgerDelete,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "BankView",
            BankView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "BankSave",
            BankSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "BankEdit",
            BankEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "BankDelete",
            BankDelete,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "CustomerView",
            CustomerView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "CustomerSave",
            CustomerSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "CustomerEdit",
            CustomerEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "CustomerDelete",
            CustomerDelete,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "SupplierView",
            SupplierView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "SupplierSave",
            SupplierSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "SupplierEdit",
            SupplierEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "SupplierDelete",
            SupplierDelete,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "TransactionTypeView",
            TransactionTypeView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "TransactionTypeSave",
            TransactionTypeSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "TransactionTypeEdit",
            TransactionTypeEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "TransactionTypeDelete",
            TransactionTypeDelete,
            UserType_instance,
        )

        # Accounts => Transactions
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "BankPaymentDelete",
            BankPaymentDelete,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "BankPaymentEdit",
            BankPaymentEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "BankPaymentSave",
            BankPaymentSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "BankPaymentView",
            BankPaymentView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "BankReceiptDelete",
            BankReceiptDelete,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "BankReceiptEdit",
            BankReceiptEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "BankReceiptSave",
            BankReceiptSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "BankReceiptView",
            BankReceiptView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "CashPaymentDelete",
            CashPaymentDelete,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "CashPaymentEdit",
            CashPaymentEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "CashPaymentSave",
            CashPaymentSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "CashPaymentView",
            CashPaymentView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "CashReceiptDelete",
            CashReceiptDelete,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "CashReceiptEdit",
            CashReceiptEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "CashReceiptSave",
            CashReceiptSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "CashReceiptView",
            CashReceiptView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "JournalEntryDelete",
            JournalEntryDelete,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "JournalEntryEdit",
            JournalEntryEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "JournalEntrySave",
            JournalEntrySave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "JournalEntryView",
            JournalEntryView,
            UserType_instance,
        )

        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "CashPaymentPrint",
            CashPaymentPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "CashReceiptPrint",
            CashReceiptPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "BankPaymentPrint",
            BankPaymentPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "BankReceiptPrint",
            BankReceiptPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "JournalEntryPrint",
            JournalEntryPrint,
            UserType_instance,
        )

        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "CashPaymentDiscountLimit",
            CashPaymentDiscountLimit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "CashReceiptDiscountLimit",
            CashReceiptDiscountLimit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "BankPaymentLimit",
            BankPaymentLimit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "BankReceiptLimit",
            BankReceiptLimit,
            UserType_instance,
        )
        # Accounts => Reports
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "LedgerReportView",
            LedgerReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "LedgerReportPrint",
            LedgerReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "LedgerReportExport",
            LedgerReportExport,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "TrialBalanceView",
            TrialBalanceView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "TrialBalancePrint",
            TrialBalancePrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "TrialBalanceExport",
            TrialBalanceExport,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "ProfitAndLossView",
            ProfitAndLossView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "ProfitAndLossPrint",
            ProfitAndLossPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "ProfitAndLossExport",
            ProfitAndLossExport,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "BalanceSheetView",
            BalanceSheetView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "BalanceSheetPrint",
            BalanceSheetPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "BalanceSheetExport",
            BalanceSheetExport,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "DailyReportView",
            DailyReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "DailyReportPrint",
            DailyReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "DailyReportExport",
            DailyReportExport,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "CashBookView",
            CashBookView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "CashBookPrint",
            CashBookPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "CashBookExport",
            CashBookExport,
            UserType_instance,
        )

        # ==========
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "BankBookReportView",
            BankBookReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "BankBookReportPrint",
            BankBookReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "BankBookReportExport",
            BankBookReportExport,
            UserType_instance,
        )

        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "OutstandingReportView",
            OutstandingReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "OutstandingReportPrint",
            OutstandingReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "OutstandingReportExport",
            OutstandingReportExport,
            UserType_instance,
        )

        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "RecieptReportView",
            RecieptReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "RecieptReportPrint",
            RecieptReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "RecieptReportExport",
            RecieptReportExport,
            UserType_instance,
        )

        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "PaymentReportView",
            PaymentReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "PaymentReportPrint",
            PaymentReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "PaymentReportExport",
            PaymentReportExport,
            UserType_instance,
        )
        # ===========

        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "VATReportView",
            VATReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "VATReportPrint",
            VATReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "VATReportExport",
            VATReportExport,
            UserType_instance,
        )

        # Accounts => GST Reports
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "SalesGSTReportView",
            SalesGSTReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "SalesGSTReportPrint",
            SalesGSTReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "SalesGSTReportExport",
            SalesGSTReportExport,
            UserType_instance,
        )

        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "PurchaseGSTReportView",
            PurchaseGSTReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "PurchaseGSTReportPrint",
            PurchaseGSTReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "PurchaseGSTReportExport",
            PurchaseGSTReportExport,
            UserType_instance,
        )

        # Inventory => Masters
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "ProductGroupView",
            ProductGroupView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "ProductGroupSave",
            ProductGroupSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "ProductGroupEdit",
            ProductGroupEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "ProductGroupDelete",
            ProductGroupDelete,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "BrandsView",
            BrandsView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "BrandsSave",
            BrandsSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "BrandsEdit",
            BrandsEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "BrandsDelete",
            BrandsDelete,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "TaxCategoriesView",
            TaxCategoriesView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "TaxCategoriesSave",
            TaxCategoriesSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "TaxCategoriesEdit",
            TaxCategoriesEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "TaxCategoriesDelete",
            TaxCategoriesDelete,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "PriceCategoriesView",
            PriceCategoriesView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "PriceCategoriesSave",
            PriceCategoriesSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "PriceCategoriesEdit",
            PriceCategoriesEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "PriceCategoriesDelete",
            PriceCategoriesDelete,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "WarehouseView",
            WarehouseView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "WarehouseSave",
            WarehouseSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "WarehouseEdit",
            WarehouseEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "WarehouseDelete",
            WarehouseDelete,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "ProductCategoriesView",
            ProductCategoriesView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "ProductCategoriesSave",
            ProductCategoriesSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "ProductCategoriesEdit",
            ProductCategoriesEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "ProductCategoriesDelete",
            ProductCategoriesDelete,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "ProductsView",
            ProductsView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "ProductsSave",
            ProductsSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "ProductsEdit",
            ProductsEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "ProductsDelete",
            ProductsDelete,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "RoutesView",
            RoutesView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "RoutesSave",
            RoutesSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "RoutesEdit",
            RoutesEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "RoutesDelete",
            RoutesDelete,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "UnitsView",
            UnitsView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "UnitsSave",
            UnitsSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "UnitsEdit",
            UnitsEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "UnitsDelete",
            UnitsDelete,
            UserType_instance,
        )

        # Inventory => Transactions
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseInvoicesView",
            PurchaseInvoicesView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseInvoicesSave",
            PurchaseInvoicesSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseInvoicesEdit",
            PurchaseInvoicesEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseInvoicesDelete",
            PurchaseInvoicesDelete,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "WorkOrdersView",
            WorkOrdersView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "WorkOrdersSave",
            WorkOrdersSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "WorkOrdersEdit",
            WorkOrdersEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "WorkOrdersDelete",
            WorkOrdersDelete,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseReturnsView",
            PurchaseReturnsView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseReturnsSave",
            PurchaseReturnsSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseReturnsEdit",
            PurchaseReturnsEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseReturnsDelete",
            PurchaseReturnsDelete,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SaleInvoicesView",
            SaleInvoicesView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SaleInvoicesSave",
            SaleInvoicesSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SaleInvoicesEdit",
            SaleInvoicesEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SaleInvoicesDelete",
            SaleInvoicesDelete,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SaleReturnsView",
            SaleReturnsView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SaleReturnsSave",
            SaleReturnsSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SaleReturnsEdit",
            SaleReturnsEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SaleReturnsDelete",
            SaleReturnsDelete,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "OpeningStockView",
            OpeningStockView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "OpeningStockSave",
            OpeningStockSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "OpeningStockEdit",
            OpeningStockEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "OpeningStockDelete",
            OpeningStockDelete,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "StockTransferView",
            StockTransferView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "StockTransferSave",
            StockTransferSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "StockTransferEdit",
            StockTransferEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "StockTransferDelete",
            StockTransferDelete,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "ExcessStocksView",
            ExcessStocksView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "ExcessStocksSave",
            ExcessStocksSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "ExcessStocksEdit",
            ExcessStocksEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "ExcessStocksDelete",
            ExcessStocksDelete,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "ShortageStocksView",
            ShortageStocksView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "ShortageStocksSave",
            ShortageStocksSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "ShortageStocksEdit",
            ShortageStocksEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "ShortageStocksDelete",
            ShortageStocksDelete,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "DamageStocksView",
            DamageStocksView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "DamageStocksSave",
            DamageStocksSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "DamageStocksEdit",
            DamageStocksEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "DamageStocksDelete",
            DamageStocksDelete,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "UsedStocksView",
            UsedStocksView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "UsedStocksSave",
            UsedStocksSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "UsedStocksEdit",
            UsedStocksEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "UsedStocksDelete",
            UsedStocksDelete,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "StockAdjustmentsView",
            StockAdjustmentsView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "StockAdjustmentsSave",
            StockAdjustmentsSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "StockAdjustmentsEdit",
            StockAdjustmentsEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "StockAdjustmentsDelete",
            StockAdjustmentsDelete,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SalesOrderView",
            SalesOrderView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseOrderView",
            PurchaseOrderView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SalesOrderSave",
            SalesOrderSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseOrderSave",
            PurchaseOrderSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SalesOrderEdit",
            SalesOrderEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseOrderEdit",
            PurchaseOrderEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SalesOrderDelete",
            SalesOrderDelete,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseOrderDelete",
            PurchaseOrderDelete,
            UserType_instance,
        )
        # -----------------------------------------
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SalesEstimateView",
            SalesEstimateView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SalesEstimateSave",
            SalesEstimateSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SalesEstimateEdit",
            SalesEstimateEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SalesEstimateDelete",
            SalesEstimateDelete,
            UserType_instance,
        )
        # -----------------------------------------
        # ----------------Print-------------------------
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseInvoicesPrint",
            PurchaseInvoicesPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseReturnsPrint",
            PurchaseReturnsPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SaleInvoicesPrint",
            SaleInvoicesPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SalesOrderPrint",
            SalesOrderPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseOrderPrint",
            PurchaseOrderPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SalesEstimatePrint",
            SalesEstimatePrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SaleReturnsPrint",
            SaleReturnsPrint,
            UserType_instance,
        )

        # ----------------Print-------------------------
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "BatchWiseReportView",
            BatchWiseReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "BatchWiseReportPrint",
            BatchWiseReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "BatchWiseReportExport",
            BatchWiseReportExport,
            UserType_instance,
        )

        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseInvoicesDiscountLimit",
            PurchaseInvoicesDiscountLimit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseReturnsDiscountLimit",
            PurchaseReturnsDiscountLimit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SaleInvoicesDiscountLimit",
            SaleInvoicesDiscountLimit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SaleReturnsDiscountLimit",
            SaleReturnsDiscountLimit,
            UserType_instance,
        )

        # Inventory => Reports
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "StockReportView",
            StockReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "StockReportPrint",
            StockReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "StockReportExport",
            StockReportExport,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "StockValueReportView",
            StockValueReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "StockValueReportPrint",
            StockValueReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "StockValueReportExport",
            StockValueReportExport,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "PurchaseReportView",
            PurchaseReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "PurchaseReportPrint",
            PurchaseReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "PurchaseReportExport",
            PurchaseReportExport,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "SalesReportView",
            SalesReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "SalesReportPrint",
            SalesReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "SalesReportExport",
            SalesReportExport,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "SalesIntegratedReportView",
            SalesIntegratedReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "SalesIntegratedReportPrint",
            SalesIntegratedReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "SalesIntegratedReportExport",
            SalesIntegratedReportExport,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "PurchaseIntegratedReportPrint",
            PurchaseIntegratedReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "PurchaseIntegratedReportView",
            PurchaseIntegratedReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "PurchaseIntegratedReportExport",
            PurchaseIntegratedReportExport,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "SalesRegisterReportView",
            SalesRegisterReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "SalesRegisterReportPrint",
            SalesRegisterReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "SalesRegisterReportExport",
            SalesRegisterReportExport,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "BillWiseReportView",
            BillWiseReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "BillWiseReportPrint",
            BillWiseReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "BillWiseReportExport",
            BillWiseReportExport,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "ExcessStockReportView",
            ExcessStockReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "ExcessStockReportPrint",
            ExcessStockReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "ExcessStockReportExport",
            ExcessStockReportExport,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "DamageStockReportView",
            DamageStockReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "DamageStockReportPrint",
            DamageStockReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "DamageStockReportExport",
            DamageStockReportExport,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "UsedStockReportView",
            UsedStockReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "UsedStockReportPrint",
            UsedStockReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "UsedStockReportExport",
            UsedStockReportExport,
            UserType_instance,
        )
        # ====******====
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "ProductReportView",
            ProductReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "ProductReportPrint",
            ProductReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "ProductReportExport",
            ProductReportExport,
            UserType_instance,
        )

        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "StockLedgerReportView",
            StockLedgerReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "StockLedgerReportPrint",
            StockLedgerReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "StockLedgerReportExport",
            StockLedgerReportExport,
            UserType_instance,
        )

        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "PurchaseOrderReportView",
            PurchaseOrderReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "PurchaseOrderReportPrint",
            PurchaseOrderReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "PurchaseOrderReportExport",
            PurchaseOrderReportExport,
            UserType_instance,
        )

        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "PurchaseRegisterReportView",
            PurchaseRegisterReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "PurchaseRegisterReportPrint",
            PurchaseRegisterReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "PurchaseRegisterReportExport",
            PurchaseRegisterReportExport,
            UserType_instance,
        )

        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "SalesReturnRegisterReportView",
            SalesReturnRegisterReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "SalesReturnRegisterReportPrint",
            SalesReturnRegisterReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "SalesReturnRegisterReportExport",
            SalesReturnRegisterReportExport,
            UserType_instance,
        )

        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "PurchaseReturnRegisterReportView",
            PurchaseReturnRegisterReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "PurchaseReturnRegisterReportPrint",
            PurchaseReturnRegisterReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "PurchaseReturnRegisterReportExport",
            PurchaseReturnRegisterReportExport,
            UserType_instance,
        )

        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "SalesSummaryReportView",
            SalesSummaryReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "SalesSummaryReportPrint",
            SalesSummaryReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "SalesSummaryReportExport",
            SalesSummaryReportExport,
            UserType_instance,
        )

        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "StockTransferRegisterReportView",
            StockTransferRegisterReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "StockTransferRegisterReportPrint",
            StockTransferRegisterReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "StockTransferRegisterReportExport",
            StockTransferRegisterReportExport,
            UserType_instance,
        )

        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "InventoryFlowReportView",
            InventoryFlowReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "InventoryFlowReportPrint",
            InventoryFlowReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "InventoryFlowReportExport",
            InventoryFlowReportExport,
            UserType_instance,
        )

        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "SupplierVsProductReportView",
            SupplierVsProductReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "SupplierVsProductReportPrint",
            SupplierVsProductReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "SupplierVsProductReportExport",
            SupplierVsProductReportExport,
            UserType_instance,
        )

        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "ProductAnalysisReportView",
            ProductAnalysisReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "ProductAnalysisReportPrint",
            ProductAnalysisReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "ProductAnalysisReportExport",
            ProductAnalysisReportExport,
            UserType_instance,
        )

        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "OpeningStockReportView",
            OpeningStockReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "OpeningStockReportPrint",
            OpeningStockReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "OpeningStockReportExport",
            OpeningStockReportExport,
            UserType_instance,
        )

        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "ShortageStocksReportView",
            ShortageStocksReportView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "ShortageStocksReportPrint",
            ShortageStocksReportPrint,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "ShortageStocksReportExport",
            ShortageStocksReportExport,
            UserType_instance,
        )

        # ====***===
        # Payroll => Masters
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Payroll_Masters",
            "DepartmentsView",
            DepartmentsView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Payroll_Masters",
            "DepartmentsSave",
            DepartmentsSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Payroll_Masters",
            "DepartmentsEdit",
            DepartmentsEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Payroll_Masters",
            "DepartmentsDelete",
            DepartmentsDelete,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Payroll_Masters",
            "DesignationsView",
            DesignationsView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Payroll_Masters",
            "DesignationsSave",
            DesignationsSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Payroll_Masters",
            "DesignationsEdit",
            DesignationsEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Payroll_Masters",
            "DesignationsDelete",
            DesignationsDelete,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Payroll_Masters",
            "EmployeeView",
            EmployeeView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Payroll_Masters",
            "EmployeeSave",
            EmployeeSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Payroll_Masters",
            "EmployeeEdit",
            EmployeeEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Payroll_Masters",
            "EmployeeDelete",
            EmployeeDelete,
            UserType_instance,
        )

        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Payroll_Masters",
            "CategoriesView",
            CategoriesView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Payroll_Masters",
            "CategoriesSave",
            CategoriesSave,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Payroll_Masters",
            "CategoriesEdit",
            CategoriesEdit,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Payroll_Masters",
            "CategoriesDelete",
            CategoriesDelete,
            UserType_instance,
        )

        # Settings
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Settings",
            "PrinterView",
            PrinterView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Settings",
            "BarcodeView",
            BarcodeView,
            UserType_instance,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Settings",
            "PrintBarcodeView",
            PrintBarcodeView,
            UserType_instance,
        )

        # request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'GeneralSettings', 'Create', 'GeneralSettings Created Successfully.', "GeneralSettings Created Successfully")
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    else:
        # request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'GeneralSettings', 'Create', 'GeneralSettings Created Failed.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors),
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def user_type_settings_list(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    BranchID = data["BranchID"]
    try:
        UserTypeValue = data["UserType"]
        UserTypeValue = models.UserType.objects.get(
            pk=UserTypeValue, CompanyID=CompanyID, BranchID=BranchID
        )
    except:
        try:
            UserTypeValue = models.UserTable.objects.get(
                CompanyID=CompanyID, customer__user__pk=CreatedUserID, Active=True
            ).UserType.id
            UserTypeValue = models.UserType.objects.get(
                pk=UserTypeValue, CompanyID=CompanyID, BranchID=BranchID
            )
        except:
            usertype_instance = models.UserType.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, UserTypeName="Admin"
            )
            user_table_instance = models.UserTable.objects.filter(
                CompanyID=CompanyID, Active=True
            ).last()
            user_table_instance.CreatedUserID = CreatedUserID
            user_table_instance.UserType = usertype_instance
            user_table_instance.save()

            UserTypeValue = models.UserTable.objects.get(
                CompanyID=CompanyID, customer__user__pk=CreatedUserID,Active=True
            ).UserType.id
            UserTypeValue = models.UserType.objects.get(
                pk=UserTypeValue, CompanyID=CompanyID, BranchID=BranchID
            )
    UserTypeName = UserTypeValue.UserTypeName
    print(UserTypeName)
    User = request.user.id

    if models.UserTypeSettings.objects.filter(
        CompanyID=CompanyID, BranchID=BranchID
    ).exists():
        # Accounts => Masters
        AccountGroupView = get_user_type_settings(
            CompanyID, BranchID, "AccountGroupView", UserTypeValue
        )
        AccountGroupSave = get_user_type_settings(
            CompanyID, BranchID, "AccountGroupSave", UserTypeValue
        )
        AccountGroupEdit = get_user_type_settings(
            CompanyID, BranchID, "AccountGroupEdit", UserTypeValue
        )
        AccountGroupDelete = get_user_type_settings(
            CompanyID, BranchID, "AccountGroupDelete", UserTypeValue
        )
        AccountLedgerView = get_user_type_settings(
            CompanyID, BranchID, "AccountLedgerView", UserTypeValue
        )
        AccountLedgerSave = get_user_type_settings(
            CompanyID, BranchID, "AccountLedgerSave", UserTypeValue
        )
        AccountLedgerEdit = get_user_type_settings(
            CompanyID, BranchID, "AccountLedgerEdit", UserTypeValue
        )
        AccountLedgerDelete = get_user_type_settings(
            CompanyID, BranchID, "AccountLedgerDelete", UserTypeValue
        )
        BankView = get_user_type_settings(
            CompanyID, BranchID, "BankView", UserTypeValue
        )
        BankSave = get_user_type_settings(
            CompanyID, BranchID, "BankSave", UserTypeValue
        )
        BankEdit = get_user_type_settings(
            CompanyID, BranchID, "BankEdit", UserTypeValue
        )
        BankDelete = get_user_type_settings(
            CompanyID, BranchID, "BankDelete", UserTypeValue
        )
        CustomerView = get_user_type_settings(
            CompanyID, BranchID, "CustomerView", UserTypeValue
        )
        CustomerSave = get_user_type_settings(
            CompanyID, BranchID, "CustomerSave", UserTypeValue
        )
        CustomerEdit = get_user_type_settings(
            CompanyID, BranchID, "CustomerEdit", UserTypeValue
        )
        CustomerDelete = get_user_type_settings(
            CompanyID, BranchID, "CustomerDelete", UserTypeValue
        )
        SupplierView = get_user_type_settings(
            CompanyID, BranchID, "SupplierView", UserTypeValue
        )
        SupplierSave = get_user_type_settings(
            CompanyID, BranchID, "SupplierSave", UserTypeValue
        )
        SupplierEdit = get_user_type_settings(
            CompanyID, BranchID, "SupplierEdit", UserTypeValue
        )
        SupplierDelete = get_user_type_settings(
            CompanyID, BranchID, "SupplierDelete", UserTypeValue
        )
        TransactionTypeView = get_user_type_settings(
            CompanyID, BranchID, "TransactionTypeView", UserTypeValue
        )
        TransactionTypeSave = get_user_type_settings(
            CompanyID, BranchID, "TransactionTypeSave", UserTypeValue
        )
        TransactionTypeEdit = get_user_type_settings(
            CompanyID, BranchID, "TransactionTypeEdit", UserTypeValue
        )
        TransactionTypeDelete = get_user_type_settings(
            CompanyID, BranchID, "TransactionTypeDelete", UserTypeValue
        )
        # Accounts => Transactions
        BankPaymentDelete = get_user_type_settings(
            CompanyID, BranchID, "BankPaymentDelete", UserTypeValue
        )
        BankPaymentEdit = get_user_type_settings(
            CompanyID, BranchID, "BankPaymentEdit", UserTypeValue
        )
        BankPaymentSave = get_user_type_settings(
            CompanyID, BranchID, "BankPaymentSave", UserTypeValue
        )
        BankPaymentView = get_user_type_settings(
            CompanyID, BranchID, "BankPaymentView", UserTypeValue
        )
        BankReceiptDelete = get_user_type_settings(
            CompanyID, BranchID, "BankReceiptDelete", UserTypeValue
        )
        BankReceiptEdit = get_user_type_settings(
            CompanyID, BranchID, "BankReceiptEdit", UserTypeValue
        )
        BankReceiptSave = get_user_type_settings(
            CompanyID, BranchID, "BankReceiptSave", UserTypeValue
        )
        BankReceiptView = get_user_type_settings(
            CompanyID, BranchID, "BankReceiptView", UserTypeValue
        )
        CashPaymentDelete = get_user_type_settings(
            CompanyID, BranchID, "CashPaymentDelete", UserTypeValue
        )
        CashPaymentEdit = get_user_type_settings(
            CompanyID, BranchID, "CashPaymentEdit", UserTypeValue
        )
        CashPaymentSave = get_user_type_settings(
            CompanyID, BranchID, "CashPaymentSave", UserTypeValue
        )
        CashPaymentView = get_user_type_settings(
            CompanyID, BranchID, "CashPaymentView", UserTypeValue
        )
        CashReceiptDelete = get_user_type_settings(
            CompanyID, BranchID, "CashReceiptDelete", UserTypeValue
        )
        CashReceiptEdit = get_user_type_settings(
            CompanyID, BranchID, "CashReceiptEdit", UserTypeValue
        )
        CashReceiptSave = get_user_type_settings(
            CompanyID, BranchID, "CashReceiptSave", UserTypeValue
        )
        CashReceiptView = get_user_type_settings(
            CompanyID, BranchID, "CashReceiptView", UserTypeValue
        )
        JournalEntryDelete = get_user_type_settings(
            CompanyID, BranchID, "JournalEntryDelete", UserTypeValue
        )
        JournalEntryEdit = get_user_type_settings(
            CompanyID, BranchID, "JournalEntryEdit", UserTypeValue
        )
        JournalEntrySave = get_user_type_settings(
            CompanyID, BranchID, "JournalEntrySave", UserTypeValue
        )
        JournalEntryView = get_user_type_settings(
            CompanyID, BranchID, "JournalEntryView", UserTypeValue
        )

        CashPaymentPrint = get_user_type_settings(
            CompanyID, BranchID, "CashPaymentPrint", UserTypeValue
        )
        CashReceiptPrint = get_user_type_settings(
            CompanyID, BranchID, "CashReceiptPrint", UserTypeValue
        )
        BankPaymentPrint = get_user_type_settings(
            CompanyID, BranchID, "BankPaymentPrint", UserTypeValue
        )
        BankReceiptPrint = get_user_type_settings(
            CompanyID, BranchID, "BankReceiptPrint", UserTypeValue
        )
        JournalEntryPrint = get_user_type_settings(
            CompanyID, BranchID, "JournalEntryPrint", UserTypeValue
        )

        CashPaymentDiscountLimit = 0
        CashReceiptDiscountLimit = 0
        BankPaymentLimit = 0
        BankReceiptLimit = 0
        if get_user_type_settings(
            CompanyID, BranchID, "CashPaymentDiscountLimit", UserTypeValue
        ):
            CashPaymentDiscountLimit = get_user_type_settings(
                CompanyID, BranchID, "CashPaymentDiscountLimit", UserTypeValue
            )
        if get_user_type_settings(
            CompanyID, BranchID, "CashReceiptDiscountLimit", UserTypeValue
        ):
            CashReceiptDiscountLimit = get_user_type_settings(
                CompanyID, BranchID, "CashReceiptDiscountLimit", UserTypeValue
            )

        if get_user_type_settings(
            CompanyID, BranchID, "BankPaymentLimit", UserTypeValue
        ):
            BankPaymentLimit = get_user_type_settings(
                CompanyID, BranchID, "BankPaymentLimit", UserTypeValue
            )

        if get_user_type_settings(
            CompanyID, BranchID, "BankReceiptLimit", UserTypeValue
        ):
            BankReceiptLimit = get_user_type_settings(
                CompanyID, BranchID, "BankReceiptLimit", UserTypeValue
            )

        # Accounts => Reports
        LedgerReportView = get_user_type_settings(
            CompanyID, BranchID, "LedgerReportView", UserTypeValue
        )
        LedgerReportPrint = get_user_type_settings(
            CompanyID, BranchID, "LedgerReportPrint", UserTypeValue
        )
        LedgerReportExport = get_user_type_settings(
            CompanyID, BranchID, "LedgerReportExport", UserTypeValue
        )
        TrialBalanceView = get_user_type_settings(
            CompanyID, BranchID, "TrialBalanceView", UserTypeValue
        )
        TrialBalancePrint = get_user_type_settings(
            CompanyID, BranchID, "TrialBalancePrint", UserTypeValue
        )
        TrialBalanceExport = get_user_type_settings(
            CompanyID, BranchID, "TrialBalanceExport", UserTypeValue
        )
        ProfitAndLossView = get_user_type_settings(
            CompanyID, BranchID, "ProfitAndLossView", UserTypeValue
        )
        ProfitAndLossPrint = get_user_type_settings(
            CompanyID, BranchID, "ProfitAndLossPrint", UserTypeValue
        )
        ProfitAndLossExport = get_user_type_settings(
            CompanyID, BranchID, "ProfitAndLossExport", UserTypeValue
        )
        BalanceSheetView = get_user_type_settings(
            CompanyID, BranchID, "BalanceSheetView", UserTypeValue
        )
        BalanceSheetPrint = get_user_type_settings(
            CompanyID, BranchID, "BalanceSheetPrint", UserTypeValue
        )
        BalanceSheetExport = get_user_type_settings(
            CompanyID, BranchID, "BalanceSheetExport", UserTypeValue
        )
        DailyReportView = get_user_type_settings(
            CompanyID, BranchID, "DailyReportView", UserTypeValue
        )
        DailyReportPrint = get_user_type_settings(
            CompanyID, BranchID, "DailyReportPrint", UserTypeValue
        )
        DailyReportExport = get_user_type_settings(
            CompanyID, BranchID, "DailyReportExport", UserTypeValue
        )
        CashBookView = get_user_type_settings(
            CompanyID, BranchID, "CashBookView", UserTypeValue
        )
        CashBookPrint = get_user_type_settings(
            CompanyID, BranchID, "CashBookPrint", UserTypeValue
        )
        CashBookExport = get_user_type_settings(
            CompanyID, BranchID, "CashBookExport", UserTypeValue
        )

        # ===========
        BankBookReportView = get_user_type_settings(
            CompanyID, BranchID, "BankBookReportView", UserTypeValue
        )
        BankBookReportPrint = get_user_type_settings(
            CompanyID, BranchID, "BankBookReportPrint", UserTypeValue
        )
        BankBookReportExport = get_user_type_settings(
            CompanyID, BranchID, "BankBookReportExport", UserTypeValue
        )

        OutstandingReportView = get_user_type_settings(
            CompanyID, BranchID, "OutstandingReportView", UserTypeValue
        )
        OutstandingReportPrint = get_user_type_settings(
            CompanyID, BranchID, "OutstandingReportPrint", UserTypeValue
        )
        OutstandingReportExport = get_user_type_settings(
            CompanyID, BranchID, "OutstandingReportExport", UserTypeValue
        )

        RecieptReportView = get_user_type_settings(
            CompanyID, BranchID, "RecieptReportView", UserTypeValue
        )
        RecieptReportPrint = get_user_type_settings(
            CompanyID, BranchID, "RecieptReportPrint", UserTypeValue
        )
        RecieptReportExport = get_user_type_settings(
            CompanyID, BranchID, "RecieptReportExport", UserTypeValue
        )

        PaymentReportView = get_user_type_settings(
            CompanyID, BranchID, "PaymentReportView", UserTypeValue
        )
        PaymentReportPrint = get_user_type_settings(
            CompanyID, BranchID, "PaymentReportPrint", UserTypeValue
        )
        PaymentReportExport = get_user_type_settings(
            CompanyID, BranchID, "PaymentReportExport", UserTypeValue
        )
        # ==========

        VATReportView = get_user_type_settings(
            CompanyID, BranchID, "VATReportView", UserTypeValue
        )
        VATReportPrint = get_user_type_settings(
            CompanyID, BranchID, "VATReportPrint", UserTypeValue
        )
        VATReportExport = get_user_type_settings(
            CompanyID, BranchID, "VATReportExport", UserTypeValue
        )

        # Accounts => GST Reports
        SalesGSTReportView = get_user_type_settings(
            CompanyID, BranchID, "SalesGSTReportView", UserTypeValue
        )
        SalesGSTReportPrint = get_user_type_settings(
            CompanyID, BranchID, "SalesGSTReportPrint", UserTypeValue
        )
        SalesGSTReportExport = get_user_type_settings(
            CompanyID, BranchID, "SalesGSTReportExport", UserTypeValue
        )

        PurchaseGSTReportView = get_user_type_settings(
            CompanyID, BranchID, "PurchaseGSTReportView", UserTypeValue
        )
        PurchaseGSTReportPrint = get_user_type_settings(
            CompanyID, BranchID, "PurchaseGSTReportPrint", UserTypeValue
        )
        PurchaseGSTReportExport = get_user_type_settings(
            CompanyID, BranchID, "PurchaseGSTReportExport", UserTypeValue
        )

        # Inventory => Masters
        ProductGroupView = get_user_type_settings(
            CompanyID, BranchID, "ProductGroupView", UserTypeValue
        )
        ProductGroupSave = get_user_type_settings(
            CompanyID, BranchID, "ProductGroupSave", UserTypeValue
        )
        ProductGroupEdit = get_user_type_settings(
            CompanyID, BranchID, "ProductGroupEdit", UserTypeValue
        )
        ProductGroupDelete = get_user_type_settings(
            CompanyID, BranchID, "ProductGroupDelete", UserTypeValue
        )
        BrandsView = get_user_type_settings(
            CompanyID, BranchID, "BrandsView", UserTypeValue
        )
        BrandsSave = get_user_type_settings(
            CompanyID, BranchID, "BrandsSave", UserTypeValue
        )
        BrandsEdit = get_user_type_settings(
            CompanyID, BranchID, "BrandsEdit", UserTypeValue
        )
        BrandsDelete = get_user_type_settings(
            CompanyID, BranchID, "BrandsDelete", UserTypeValue
        )
        TaxCategoriesView = get_user_type_settings(
            CompanyID, BranchID, "TaxCategoriesView", UserTypeValue
        )
        TaxCategoriesSave = get_user_type_settings(
            CompanyID, BranchID, "TaxCategoriesSave", UserTypeValue
        )
        TaxCategoriesEdit = get_user_type_settings(
            CompanyID, BranchID, "TaxCategoriesEdit", UserTypeValue
        )
        TaxCategoriesDelete = get_user_type_settings(
            CompanyID, BranchID, "TaxCategoriesDelete", UserTypeValue
        )
        PriceCategoriesView = get_user_type_settings(
            CompanyID, BranchID, "PriceCategoriesView", UserTypeValue
        )
        PriceCategoriesSave = get_user_type_settings(
            CompanyID, BranchID, "PriceCategoriesSave", UserTypeValue
        )
        PriceCategoriesEdit = get_user_type_settings(
            CompanyID, BranchID, "PriceCategoriesEdit", UserTypeValue
        )
        PriceCategoriesDelete = get_user_type_settings(
            CompanyID, BranchID, "PriceCategoriesDelete", UserTypeValue
        )
        WarehouseView = get_user_type_settings(
            CompanyID, BranchID, "WarehouseView", UserTypeValue
        )
        WarehouseSave = get_user_type_settings(
            CompanyID, BranchID, "WarehouseSave", UserTypeValue
        )
        WarehouseEdit = get_user_type_settings(
            CompanyID, BranchID, "WarehouseEdit", UserTypeValue
        )
        WarehouseDelete = get_user_type_settings(
            CompanyID, BranchID, "WarehouseDelete", UserTypeValue
        )
        ProductCategoriesView = get_user_type_settings(
            CompanyID, BranchID, "ProductCategoriesView", UserTypeValue
        )
        ProductCategoriesSave = get_user_type_settings(
            CompanyID, BranchID, "ProductCategoriesSave", UserTypeValue
        )
        ProductCategoriesEdit = get_user_type_settings(
            CompanyID, BranchID, "ProductCategoriesEdit", UserTypeValue
        )
        ProductCategoriesDelete = get_user_type_settings(
            CompanyID, BranchID, "ProductCategoriesDelete", UserTypeValue
        )
        ProductsView = get_user_type_settings(
            CompanyID, BranchID, "ProductsView", UserTypeValue
        )
        ProductsSave = get_user_type_settings(
            CompanyID, BranchID, "ProductsSave", UserTypeValue
        )
        ProductsEdit = get_user_type_settings(
            CompanyID, BranchID, "ProductsEdit", UserTypeValue
        )
        ProductsDelete = get_user_type_settings(
            CompanyID, BranchID, "ProductsDelete", UserTypeValue
        )
        RoutesView = get_user_type_settings(
            CompanyID, BranchID, "RoutesView", UserTypeValue
        )
        RoutesSave = get_user_type_settings(
            CompanyID, BranchID, "RoutesSave", UserTypeValue
        )
        RoutesEdit = get_user_type_settings(
            CompanyID, BranchID, "RoutesEdit", UserTypeValue
        )
        RoutesDelete = get_user_type_settings(
            CompanyID, BranchID, "RoutesDelete", UserTypeValue
        )
        UnitsView = get_user_type_settings(
            CompanyID, BranchID, "UnitsView", UserTypeValue
        )
        UnitsSave = get_user_type_settings(
            CompanyID, BranchID, "UnitsSave", UserTypeValue
        )
        UnitsEdit = get_user_type_settings(
            CompanyID, BranchID, "UnitsEdit", UserTypeValue
        )
        UnitsDelete = get_user_type_settings(
            CompanyID, BranchID, "UnitsDelete", UserTypeValue
        )
        # Inventory => Transactions
        PurchaseInvoicesView = get_user_type_settings(
            CompanyID, BranchID, "PurchaseInvoicesView", UserTypeValue
        )
        PurchaseInvoicesSave = get_user_type_settings(
            CompanyID, BranchID, "PurchaseInvoicesSave", UserTypeValue
        )
        PurchaseInvoicesEdit = get_user_type_settings(
            CompanyID, BranchID, "PurchaseInvoicesEdit", UserTypeValue
        )
        PurchaseInvoicesDelete = get_user_type_settings(
            CompanyID, BranchID, "PurchaseInvoicesDelete", UserTypeValue
        )
        WorkOrdersView = get_user_type_settings(
            CompanyID, BranchID, "WorkOrdersView", UserTypeValue
        )
        WorkOrdersSave = get_user_type_settings(
            CompanyID, BranchID, "WorkOrdersSave", UserTypeValue
        )
        WorkOrdersEdit = get_user_type_settings(
            CompanyID, BranchID, "WorkOrdersEdit", UserTypeValue
        )
        WorkOrdersDelete = get_user_type_settings(
            CompanyID, BranchID, "WorkOrdersDelete", UserTypeValue
        )
        PurchaseReturnsView = get_user_type_settings(
            CompanyID, BranchID, "PurchaseReturnsView", UserTypeValue
        )
        PurchaseReturnsSave = get_user_type_settings(
            CompanyID, BranchID, "PurchaseReturnsSave", UserTypeValue
        )
        PurchaseReturnsEdit = get_user_type_settings(
            CompanyID, BranchID, "PurchaseReturnsEdit", UserTypeValue
        )
        PurchaseReturnsDelete = get_user_type_settings(
            CompanyID, BranchID, "PurchaseReturnsDelete", UserTypeValue
        )
        SaleInvoicesView = get_user_type_settings(
            CompanyID, BranchID, "SaleInvoicesView", UserTypeValue
        )
        SaleInvoicesSave = get_user_type_settings(
            CompanyID, BranchID, "SaleInvoicesSave", UserTypeValue
        )
        SaleInvoicesEdit = get_user_type_settings(
            CompanyID, BranchID, "SaleInvoicesEdit", UserTypeValue
        )
        SaleInvoicesDelete = get_user_type_settings(
            CompanyID, BranchID, "SaleInvoicesDelete", UserTypeValue
        )
        SaleReturnsView = get_user_type_settings(
            CompanyID, BranchID, "SaleReturnsView", UserTypeValue
        )
        SaleReturnsSave = get_user_type_settings(
            CompanyID, BranchID, "SaleReturnsSave", UserTypeValue
        )
        SaleReturnsEdit = get_user_type_settings(
            CompanyID, BranchID, "SaleReturnsEdit", UserTypeValue
        )
        SaleReturnsDelete = get_user_type_settings(
            CompanyID, BranchID, "SaleReturnsDelete", UserTypeValue
        )
        OpeningStockView = get_user_type_settings(
            CompanyID, BranchID, "OpeningStockView", UserTypeValue
        )
        OpeningStockSave = get_user_type_settings(
            CompanyID, BranchID, "OpeningStockSave", UserTypeValue
        )
        OpeningStockEdit = get_user_type_settings(
            CompanyID, BranchID, "OpeningStockEdit", UserTypeValue
        )
        OpeningStockDelete = get_user_type_settings(
            CompanyID, BranchID, "OpeningStockDelete", UserTypeValue
        )
        StockTransferView = get_user_type_settings(
            CompanyID, BranchID, "StockTransferView", UserTypeValue
        )
        StockTransferSave = get_user_type_settings(
            CompanyID, BranchID, "StockTransferSave", UserTypeValue
        )
        StockTransferEdit = get_user_type_settings(
            CompanyID, BranchID, "StockTransferEdit", UserTypeValue
        )
        StockTransferDelete = get_user_type_settings(
            CompanyID, BranchID, "StockTransferDelete", UserTypeValue
        )
        ExcessStocksView = get_user_type_settings(
            CompanyID, BranchID, "ExcessStocksView", UserTypeValue
        )
        ExcessStocksSave = get_user_type_settings(
            CompanyID, BranchID, "ExcessStocksSave", UserTypeValue
        )
        ExcessStocksEdit = get_user_type_settings(
            CompanyID, BranchID, "ExcessStocksEdit", UserTypeValue
        )
        ExcessStocksDelete = get_user_type_settings(
            CompanyID, BranchID, "ExcessStocksDelete", UserTypeValue
        )
        ShortageStocksView = get_user_type_settings(
            CompanyID, BranchID, "ShortageStocksView", UserTypeValue
        )
        ShortageStocksSave = get_user_type_settings(
            CompanyID, BranchID, "ShortageStocksSave", UserTypeValue
        )
        ShortageStocksEdit = get_user_type_settings(
            CompanyID, BranchID, "ShortageStocksEdit", UserTypeValue
        )
        ShortageStocksDelete = get_user_type_settings(
            CompanyID, BranchID, "ShortageStocksDelete", UserTypeValue
        )
        DamageStocksView = get_user_type_settings(
            CompanyID, BranchID, "DamageStocksView", UserTypeValue
        )
        DamageStocksSave = get_user_type_settings(
            CompanyID, BranchID, "DamageStocksSave", UserTypeValue
        )
        DamageStocksEdit = get_user_type_settings(
            CompanyID, BranchID, "DamageStocksEdit", UserTypeValue
        )
        DamageStocksDelete = get_user_type_settings(
            CompanyID, BranchID, "DamageStocksDelete", UserTypeValue
        )
        UsedStocksView = get_user_type_settings(
            CompanyID, BranchID, "UsedStocksView", UserTypeValue
        )
        UsedStocksSave = get_user_type_settings(
            CompanyID, BranchID, "UsedStocksSave", UserTypeValue
        )
        UsedStocksEdit = get_user_type_settings(
            CompanyID, BranchID, "UsedStocksEdit", UserTypeValue
        )
        UsedStocksDelete = get_user_type_settings(
            CompanyID, BranchID, "UsedStocksDelete", UserTypeValue
        )
        StockAdjustmentsView = get_user_type_settings(
            CompanyID, BranchID, "StockAdjustmentsView", UserTypeValue
        )
        StockAdjustmentsSave = get_user_type_settings(
            CompanyID, BranchID, "StockAdjustmentsSave", UserTypeValue
        )
        StockAdjustmentsEdit = get_user_type_settings(
            CompanyID, BranchID, "StockAdjustmentsEdit", UserTypeValue
        )
        StockAdjustmentsDelete = get_user_type_settings(
            CompanyID, BranchID, "StockAdjustmentsDelete", UserTypeValue
        )
        SalesOrderView = get_user_type_settings(
            CompanyID, BranchID, "SalesOrderView", UserTypeValue
        )
        PurchaseOrderView = get_user_type_settings(
            CompanyID, BranchID, "PurchaseOrderView", UserTypeValue
        )
        SalesOrderSave = get_user_type_settings(
            CompanyID, BranchID, "SalesOrderSave", UserTypeValue
        )
        PurchaseOrderSave = get_user_type_settings(
            CompanyID, BranchID, "PurchaseOrderSave", UserTypeValue
        )
        SalesOrderEdit = get_user_type_settings(
            CompanyID, BranchID, "SalesOrderEdit", UserTypeValue
        )
        PurchaseOrderEdit = get_user_type_settings(
            CompanyID, BranchID, "PurchaseOrderEdit", UserTypeValue
        )
        SalesOrderDelete = get_user_type_settings(
            CompanyID, BranchID, "SalesOrderDelete", UserTypeValue
        )
        PurchaseOrderDelete = get_user_type_settings(
            CompanyID, BranchID, "PurchaseOrderDelete", UserTypeValue
        )

        # =====
        SalesEstimateView = get_user_type_settings(
            CompanyID, BranchID, "SalesEstimateView", UserTypeValue
        )
        SalesEstimateSave = get_user_type_settings(
            CompanyID, BranchID, "SalesEstimateSave", UserTypeValue
        )
        SalesEstimateEdit = get_user_type_settings(
            CompanyID, BranchID, "SalesEstimateEdit", UserTypeValue
        )
        SalesEstimateDelete = get_user_type_settings(
            CompanyID, BranchID, "SalesEstimateDelete", UserTypeValue
        )
        # ===Print==
        PurchaseInvoicesPrint = get_user_type_settings(
            CompanyID, BranchID, "PurchaseInvoicesPrint", UserTypeValue
        )
        PurchaseReturnsPrint = get_user_type_settings(
            CompanyID, BranchID, "PurchaseReturnsPrint", UserTypeValue
        )
        SaleInvoicesPrint = get_user_type_settings(
            CompanyID, BranchID, "SaleInvoicesPrint", UserTypeValue
        )
        SalesOrderPrint = get_user_type_settings(
            CompanyID, BranchID, "SalesOrderPrint", UserTypeValue
        )
        PurchaseOrderPrint = get_user_type_settings(
            CompanyID, BranchID, "PurchaseOrderPrint", UserTypeValue
        )
        SalesEstimatePrint = get_user_type_settings(
            CompanyID, BranchID, "SalesEstimatePrint", UserTypeValue
        )
        SaleReturnsPrint = get_user_type_settings(
            CompanyID, BranchID, "SaleReturnsPrint", UserTypeValue
        )

        # =====

        PurchaseInvoicesDiscountLimit = 0
        PurchaseReturnsDiscountLimit = 0
        SaleInvoicesDiscountLimit = 0
        SaleReturnsDiscountLimit = 0

        if get_user_type_settings(
            CompanyID, BranchID, "PurchaseInvoicesDiscountLimit", UserTypeValue
        ):
            PurchaseInvoicesDiscountLimit = get_user_type_settings(
                CompanyID, BranchID, "PurchaseInvoicesDiscountLimit", UserTypeValue
            )
        if get_user_type_settings(
            CompanyID, BranchID, "PurchaseReturnsDiscountLimit", UserTypeValue
        ):
            PurchaseReturnsDiscountLimit = get_user_type_settings(
                CompanyID, BranchID, "PurchaseReturnsDiscountLimit", UserTypeValue
            )
        if get_user_type_settings(
            CompanyID, BranchID, "SaleInvoicesDiscountLimit", UserTypeValue
        ):
            SaleInvoicesDiscountLimit = get_user_type_settings(
                CompanyID, BranchID, "SaleInvoicesDiscountLimit", UserTypeValue
            )
        if get_user_type_settings(
            CompanyID, BranchID, "SaleReturnsDiscountLimit", UserTypeValue
        ):
            SaleReturnsDiscountLimit = get_user_type_settings(
                CompanyID, BranchID, "SaleReturnsDiscountLimit", UserTypeValue
            )
        # Inventory => Reports
        StockReportView = get_user_type_settings(
            CompanyID, BranchID, "StockReportView", UserTypeValue
        )
        StockReportPrint = get_user_type_settings(
            CompanyID, BranchID, "StockReportPrint", UserTypeValue
        )
        StockReportExport = get_user_type_settings(
            CompanyID, BranchID, "StockReportExport", UserTypeValue
        )
        StockValueReportView = get_user_type_settings(
            CompanyID, BranchID, "StockValueReportView", UserTypeValue
        )
        StockValueReportPrint = get_user_type_settings(
            CompanyID, BranchID, "StockValueReportPrint", UserTypeValue
        )
        StockValueReportExport = get_user_type_settings(
            CompanyID, BranchID, "StockValueReportExport", UserTypeValue
        )
        PurchaseReportView = get_user_type_settings(
            CompanyID, BranchID, "PurchaseReportView", UserTypeValue
        )
        PurchaseReportPrint = get_user_type_settings(
            CompanyID, BranchID, "PurchaseReportPrint", UserTypeValue
        )
        PurchaseReportExport = get_user_type_settings(
            CompanyID, BranchID, "PurchaseReportExport", UserTypeValue
        )
        SalesReportView = get_user_type_settings(
            CompanyID, BranchID, "SalesReportView", UserTypeValue
        )
        SalesReportPrint = get_user_type_settings(
            CompanyID, BranchID, "SalesReportPrint", UserTypeValue
        )
        SalesReportExport = get_user_type_settings(
            CompanyID, BranchID, "SalesReportExport", UserTypeValue
        )
        SalesIntegratedReportView = get_user_type_settings(
            CompanyID, BranchID, "SalesIntegratedReportView", UserTypeValue
        )
        SalesIntegratedReportPrint = get_user_type_settings(
            CompanyID, BranchID, "SalesIntegratedReportPrint", UserTypeValue
        )
        SalesIntegratedReportExport = get_user_type_settings(
            CompanyID, BranchID, "SalesIntegratedReportExport", UserTypeValue
        )
        PurchaseIntegratedReportPrint = get_user_type_settings(
            CompanyID, BranchID, "PurchaseIntegratedReportPrint", UserTypeValue
        )
        PurchaseIntegratedReportView = get_user_type_settings(
            CompanyID, BranchID, "PurchaseIntegratedReportView", UserTypeValue
        )
        PurchaseIntegratedReportExport = get_user_type_settings(
            CompanyID, BranchID, "PurchaseIntegratedReportExport", UserTypeValue
        )
        SalesRegisterReportView = get_user_type_settings(
            CompanyID, BranchID, "SalesRegisterReportView", UserTypeValue
        )
        SalesRegisterReportPrint = get_user_type_settings(
            CompanyID, BranchID, "SalesRegisterReportPrint", UserTypeValue
        )
        SalesRegisterReportExport = get_user_type_settings(
            CompanyID, BranchID, "SalesRegisterReportExport", UserTypeValue
        )
        BillWiseReportView = get_user_type_settings(
            CompanyID, BranchID, "BillWiseReportView", UserTypeValue
        )
        BillWiseReportPrint = get_user_type_settings(
            CompanyID, BranchID, "BillWiseReportPrint", UserTypeValue
        )
        BillWiseReportExport = get_user_type_settings(
            CompanyID, BranchID, "BillWiseReportExport", UserTypeValue
        )
        ExcessStockReportView = get_user_type_settings(
            CompanyID, BranchID, "ExcessStockReportView", UserTypeValue
        )
        ExcessStockReportPrint = get_user_type_settings(
            CompanyID, BranchID, "ExcessStockReportPrint", UserTypeValue
        )
        ExcessStockReportExport = get_user_type_settings(
            CompanyID, BranchID, "ExcessStockReportExport", UserTypeValue
        )
        DamageStockReportView = get_user_type_settings(
            CompanyID, BranchID, "DamageStockReportView", UserTypeValue
        )
        DamageStockReportPrint = get_user_type_settings(
            CompanyID, BranchID, "DamageStockReportPrint", UserTypeValue
        )
        DamageStockReportExport = get_user_type_settings(
            CompanyID, BranchID, "DamageStockReportExport", UserTypeValue
        )
        UsedStockReportView = get_user_type_settings(
            CompanyID, BranchID, "UsedStockReportView", UserTypeValue
        )
        UsedStockReportPrint = get_user_type_settings(
            CompanyID, BranchID, "UsedStockReportPrint", UserTypeValue
        )
        UsedStockReportExport = get_user_type_settings(
            CompanyID, BranchID, "UsedStockReportExport", UserTypeValue
        )
        BatchWiseReportView = get_user_type_settings(
            CompanyID, BranchID, "BatchWiseReportView", UserTypeValue
        )
        BatchWiseReportPrint = get_user_type_settings(
            CompanyID, BranchID, "BatchWiseReportPrint", UserTypeValue
        )
        BatchWiseReportExport = get_user_type_settings(
            CompanyID, BranchID, "BatchWiseReportExport", UserTypeValue
        )
        # ===***===
        ProductReportView = get_user_type_settings(
            CompanyID, BranchID, "ProductReportView", UserTypeValue
        )
        ProductReportPrint = get_user_type_settings(
            CompanyID, BranchID, "ProductReportPrint", UserTypeValue
        )
        ProductReportExport = get_user_type_settings(
            CompanyID, BranchID, "ProductReportExport", UserTypeValue
        )

        StockLedgerReportView = get_user_type_settings(
            CompanyID, BranchID, "StockLedgerReportView", UserTypeValue
        )
        StockLedgerReportPrint = get_user_type_settings(
            CompanyID, BranchID, "StockLedgerReportPrint", UserTypeValue
        )
        StockLedgerReportExport = get_user_type_settings(
            CompanyID, BranchID, "StockLedgerReportExport", UserTypeValue
        )

        PurchaseOrderReportView = get_user_type_settings(
            CompanyID, BranchID, "PurchaseOrderReportView", UserTypeValue
        )
        PurchaseOrderReportPrint = get_user_type_settings(
            CompanyID, BranchID, "PurchaseOrderReportPrint", UserTypeValue
        )
        PurchaseOrderReportExport = get_user_type_settings(
            CompanyID, BranchID, "PurchaseOrderReportExport", UserTypeValue
        )

        PurchaseRegisterReportView = get_user_type_settings(
            CompanyID, BranchID, "PurchaseRegisterReportView", UserTypeValue
        )
        PurchaseRegisterReportPrint = get_user_type_settings(
            CompanyID, BranchID, "PurchaseRegisterReportPrint", UserTypeValue
        )
        PurchaseRegisterReportExport = get_user_type_settings(
            CompanyID, BranchID, "PurchaseRegisterReportExport", UserTypeValue
        )

        SalesReturnRegisterReportView = get_user_type_settings(
            CompanyID, BranchID, "SalesReturnRegisterReportView", UserTypeValue
        )
        SalesReturnRegisterReportPrint = get_user_type_settings(
            CompanyID, BranchID, "SalesReturnRegisterReportPrint", UserTypeValue
        )
        SalesReturnRegisterReportExport = get_user_type_settings(
            CompanyID, BranchID, "SalesReturnRegisterReportExport", UserTypeValue
        )

        PurchaseReturnRegisterReportView = get_user_type_settings(
            CompanyID, BranchID, "PurchaseReturnRegisterReportView", UserTypeValue
        )
        PurchaseReturnRegisterReportPrint = get_user_type_settings(
            CompanyID, BranchID, "PurchaseReturnRegisterReportPrint", UserTypeValue
        )
        PurchaseReturnRegisterReportExport = get_user_type_settings(
            CompanyID, BranchID, "PurchaseReturnRegisterReportExport", UserTypeValue
        )

        SalesSummaryReportView = get_user_type_settings(
            CompanyID, BranchID, "SalesSummaryReportView", UserTypeValue
        )
        SalesSummaryReportPrint = get_user_type_settings(
            CompanyID, BranchID, "SalesSummaryReportPrint", UserTypeValue
        )
        SalesSummaryReportExport = get_user_type_settings(
            CompanyID, BranchID, "SalesSummaryReportExport", UserTypeValue
        )

        StockTransferRegisterReportView = get_user_type_settings(
            CompanyID, BranchID, "StockTransferRegisterReportView", UserTypeValue
        )
        StockTransferRegisterReportPrint = get_user_type_settings(
            CompanyID, BranchID, "StockTransferRegisterReportPrint", UserTypeValue
        )
        StockTransferRegisterReportExport = get_user_type_settings(
            CompanyID, BranchID, "StockTransferRegisterReportExport", UserTypeValue
        )

        InventoryFlowReportView = get_user_type_settings(
            CompanyID, BranchID, "InventoryFlowReportView", UserTypeValue
        )
        InventoryFlowReportPrint = get_user_type_settings(
            CompanyID, BranchID, "InventoryFlowReportPrint", UserTypeValue
        )
        InventoryFlowReportExport = get_user_type_settings(
            CompanyID, BranchID, "InventoryFlowReportExport", UserTypeValue
        )

        SupplierVsProductReportView = get_user_type_settings(
            CompanyID, BranchID, "SupplierVsProductReportView", UserTypeValue
        )
        SupplierVsProductReportPrint = get_user_type_settings(
            CompanyID, BranchID, "SupplierVsProductReportPrint", UserTypeValue
        )
        SupplierVsProductReportExport = get_user_type_settings(
            CompanyID, BranchID, "SupplierVsProductReportExport", UserTypeValue
        )

        ProductAnalysisReportView = get_user_type_settings(
            CompanyID, BranchID, "ProductAnalysisReportView", UserTypeValue
        )
        ProductAnalysisReportPrint = get_user_type_settings(
            CompanyID, BranchID, "ProductAnalysisReportPrint", UserTypeValue
        )
        ProductAnalysisReportExport = get_user_type_settings(
            CompanyID, BranchID, "ProductAnalysisReportExport", UserTypeValue
        )

        OpeningStockReportView = get_user_type_settings(
            CompanyID, BranchID, "OpeningStockReportView", UserTypeValue
        )
        OpeningStockReportPrint = get_user_type_settings(
            CompanyID, BranchID, "OpeningStockReportPrint", UserTypeValue
        )
        OpeningStockReportExport = get_user_type_settings(
            CompanyID, BranchID, "OpeningStockReportExport", UserTypeValue
        )

        ShortageStocksReportView = get_user_type_settings(
            CompanyID, BranchID, "ShortageStocksReportView", UserTypeValue
        )
        ShortageStocksReportPrint = get_user_type_settings(
            CompanyID, BranchID, "ShortageStocksReportPrint", UserTypeValue
        )
        ShortageStocksReportExport = get_user_type_settings(
            CompanyID, BranchID, "ShortageStocksReportExport", UserTypeValue
        )
        # ===***===
        # Payroll => Masters
        DepartmentsView = get_user_type_settings(
            CompanyID, BranchID, "DepartmentsView", UserTypeValue
        )
        DepartmentsSave = get_user_type_settings(
            CompanyID, BranchID, "DepartmentsSave", UserTypeValue
        )
        DepartmentsEdit = get_user_type_settings(
            CompanyID, BranchID, "DepartmentsEdit", UserTypeValue
        )
        DepartmentsDelete = get_user_type_settings(
            CompanyID, BranchID, "DepartmentsDelete", UserTypeValue
        )
        DesignationsView = get_user_type_settings(
            CompanyID, BranchID, "DesignationsView", UserTypeValue
        )
        DesignationsSave = get_user_type_settings(
            CompanyID, BranchID, "DesignationsSave", UserTypeValue
        )
        DesignationsEdit = get_user_type_settings(
            CompanyID, BranchID, "DesignationsEdit", UserTypeValue
        )
        DesignationsDelete = get_user_type_settings(
            CompanyID, BranchID, "DesignationsDelete", UserTypeValue
        )
        EmployeeView = get_user_type_settings(
            CompanyID, BranchID, "EmployeeView", UserTypeValue
        )
        EmployeeSave = get_user_type_settings(
            CompanyID, BranchID, "EmployeeSave", UserTypeValue
        )
        EmployeeEdit = get_user_type_settings(
            CompanyID, BranchID, "EmployeeEdit", UserTypeValue
        )
        EmployeeDelete = get_user_type_settings(
            CompanyID, BranchID, "EmployeeDelete", UserTypeValue
        )

        CategoriesView = get_user_type_settings(
            CompanyID, BranchID, "CategoriesView", UserTypeValue
        )
        CategoriesSave = get_user_type_settings(
            CompanyID, BranchID, "CategoriesSave", UserTypeValue
        )
        CategoriesEdit = get_user_type_settings(
            CompanyID, BranchID, "CategoriesEdit", UserTypeValue
        )
        CategoriesDelete = get_user_type_settings(
            CompanyID, BranchID, "CategoriesDelete", UserTypeValue
        )

        # Settings
        PrinterView = get_user_type_settings(
            CompanyID, BranchID, "PrinterView", UserTypeValue
        )
        BarcodeView = get_user_type_settings(
            CompanyID, BranchID, "BarcodeView", UserTypeValue
        )
        PrintBarcodeView = get_user_type_settings(
            CompanyID, BranchID, "PrintBarcodeView", UserTypeValue
        )

        data = {
            # Accounts => Masters
            "AccountGroupView": AccountGroupView,
            "AccountGroupSave": AccountGroupSave,
            "AccountGroupEdit": AccountGroupEdit,
            "AccountGroupDelete": AccountGroupDelete,
            "AccountLedgerView": AccountLedgerView,
            "AccountLedgerSave": AccountLedgerSave,
            "AccountLedgerEdit": AccountLedgerEdit,
            "AccountLedgerDelete": AccountLedgerDelete,
            "BankView": BankView,
            "BankSave": BankSave,
            "BankEdit": BankEdit,
            "BankDelete": BankDelete,
            "CustomerView": CustomerView,
            "CustomerSave": CustomerSave,
            "CustomerEdit": CustomerEdit,
            "CustomerDelete": CustomerDelete,
            "SupplierView": SupplierView,
            "SupplierSave": SupplierSave,
            "SupplierEdit": SupplierEdit,
            "SupplierDelete": SupplierDelete,
            "TransactionTypeView": TransactionTypeView,
            "TransactionTypeSave": TransactionTypeSave,
            "TransactionTypeEdit": TransactionTypeEdit,
            "TransactionTypeDelete": TransactionTypeDelete,
            # Accounts => Transactions
            "BankPaymentDelete": BankPaymentDelete,
            "BankPaymentEdit": BankPaymentEdit,
            "BankPaymentSave": BankPaymentSave,
            "BankPaymentView": BankPaymentView,
            "BankReceiptDelete": BankReceiptDelete,
            "BankReceiptEdit": BankReceiptEdit,
            "BankReceiptSave": BankReceiptSave,
            "BankReceiptView": BankReceiptView,
            "CashPaymentDelete": CashPaymentDelete,
            "CashPaymentEdit": CashPaymentEdit,
            "CashPaymentSave": CashPaymentSave,
            "CashPaymentView": CashPaymentView,
            "CashReceiptDelete": CashReceiptDelete,
            "CashReceiptEdit": CashReceiptEdit,
            "CashReceiptSave": CashReceiptSave,
            "CashReceiptView": CashReceiptView,
            "JournalEntryDelete": JournalEntryDelete,
            "JournalEntryEdit": JournalEntryEdit,
            "JournalEntrySave": JournalEntrySave,
            "JournalEntryView": JournalEntryView,
            "CashPaymentPrint": CashPaymentPrint,
            "CashReceiptPrint": CashReceiptPrint,
            "BankPaymentPrint": BankPaymentPrint,
            "BankReceiptPrint": BankReceiptPrint,
            "JournalEntryPrint": JournalEntryPrint,
            "CashPaymentDiscountLimit": CashPaymentDiscountLimit,
            "CashReceiptDiscountLimit": CashReceiptDiscountLimit,
            "BankPaymentLimit": BankPaymentLimit,
            "BankReceiptLimit": BankReceiptLimit,
            # Accounts => Reports
            "LedgerReportView": LedgerReportView,
            "LedgerReportPrint": LedgerReportPrint,
            "LedgerReportExport": LedgerReportExport,
            "TrialBalanceView": TrialBalanceView,
            "TrialBalancePrint": TrialBalancePrint,
            "TrialBalanceExport": TrialBalanceExport,
            "ProfitAndLossView": ProfitAndLossView,
            "ProfitAndLossPrint": ProfitAndLossPrint,
            "ProfitAndLossExport": ProfitAndLossExport,
            "BalanceSheetView": BalanceSheetView,
            "BalanceSheetPrint": BalanceSheetPrint,
            "BalanceSheetExport": BalanceSheetExport,
            "DailyReportView": DailyReportView,
            "DailyReportPrint": DailyReportPrint,
            "DailyReportExport": DailyReportExport,
            "CashBookView": CashBookView,
            "CashBookPrint": CashBookPrint,
            "CashBookExport": CashBookExport,
            # =========
            "BankBookReportView": BankBookReportView,
            "BankBookReportPrint": BankBookReportPrint,
            "BankBookReportExport": BankBookReportExport,
            "OutstandingReportView": OutstandingReportView,
            "OutstandingReportPrint": OutstandingReportPrint,
            "OutstandingReportExport": OutstandingReportExport,
            "RecieptReportView": RecieptReportView,
            "RecieptReportPrint": RecieptReportPrint,
            "RecieptReportExport": RecieptReportExport,
            "PaymentReportView": PaymentReportView,
            "PaymentReportPrint": PaymentReportPrint,
            "PaymentReportExport": PaymentReportExport,
            # ======
            "VATReportView": VATReportView,
            "VATReportPrint": VATReportPrint,
            "VATReportExport": VATReportExport,
            # Accounts => GST Reports
            "SalesGSTReportView": SalesGSTReportView,
            "SalesGSTReportPrint": SalesGSTReportPrint,
            "SalesGSTReportExport": SalesGSTReportExport,
            "PurchaseGSTReportView": PurchaseGSTReportView,
            "PurchaseGSTReportPrint": PurchaseGSTReportPrint,
            "PurchaseGSTReportExport": PurchaseGSTReportExport,
            # Inventory => Masters
            "ProductGroupView": ProductGroupView,
            "ProductGroupSave": ProductGroupSave,
            "ProductGroupEdit": ProductGroupEdit,
            "ProductGroupDelete": ProductGroupDelete,
            "BrandsView": BrandsView,
            "BrandsSave": BrandsSave,
            "BrandsEdit": BrandsEdit,
            "BrandsDelete": BrandsDelete,
            "TaxCategoriesView": TaxCategoriesView,
            "TaxCategoriesSave": TaxCategoriesSave,
            "TaxCategoriesEdit": TaxCategoriesEdit,
            "TaxCategoriesDelete": TaxCategoriesDelete,
            "PriceCategoriesView": PriceCategoriesView,
            "PriceCategoriesSave": PriceCategoriesSave,
            "PriceCategoriesEdit": PriceCategoriesEdit,
            "PriceCategoriesDelete": PriceCategoriesDelete,
            "WarehouseView": WarehouseView,
            "WarehouseSave": WarehouseSave,
            "WarehouseEdit": WarehouseEdit,
            "WarehouseDelete": WarehouseDelete,
            "ProductCategoriesView": ProductCategoriesView,
            "ProductCategoriesSave": ProductCategoriesSave,
            "ProductCategoriesEdit": ProductCategoriesEdit,
            "ProductCategoriesDelete": ProductCategoriesDelete,
            "ProductsView": ProductsView,
            "ProductsSave": ProductsSave,
            "ProductsEdit": ProductsEdit,
            "ProductsDelete": ProductsDelete,
            "RoutesView": RoutesView,
            "RoutesSave": RoutesSave,
            "RoutesEdit": RoutesEdit,
            "RoutesDelete": RoutesDelete,
            "UnitsView": UnitsView,
            "UnitsSave": UnitsSave,
            "UnitsEdit": UnitsEdit,
            "UnitsDelete": UnitsDelete,
            # Inventory => Transactions
            "PurchaseInvoicesView": PurchaseInvoicesView,
            "PurchaseInvoicesSave": PurchaseInvoicesSave,
            "PurchaseInvoicesEdit": PurchaseInvoicesEdit,
            "PurchaseInvoicesDelete": PurchaseInvoicesDelete,
            "WorkOrdersView": WorkOrdersView,
            "WorkOrdersSave": WorkOrdersSave,
            "WorkOrdersEdit": WorkOrdersEdit,
            "WorkOrdersDelete": WorkOrdersDelete,
            "PurchaseReturnsView": PurchaseReturnsView,
            "PurchaseReturnsSave": PurchaseReturnsSave,
            "PurchaseReturnsEdit": PurchaseReturnsEdit,
            "PurchaseReturnsDelete": PurchaseReturnsDelete,
            "SaleInvoicesView": SaleInvoicesView,
            "SaleInvoicesSave": SaleInvoicesSave,
            "SaleInvoicesEdit": SaleInvoicesEdit,
            "SaleInvoicesDelete": SaleInvoicesDelete,
            "SaleReturnsView": SaleReturnsView,
            "SaleReturnsSave": SaleReturnsSave,
            "SaleReturnsEdit": SaleReturnsEdit,
            "SaleReturnsDelete": SaleReturnsDelete,
            "OpeningStockView": OpeningStockView,
            "OpeningStockSave": OpeningStockSave,
            "OpeningStockEdit": OpeningStockEdit,
            "OpeningStockDelete": OpeningStockDelete,
            "StockTransferView": StockTransferView,
            "StockTransferSave": StockTransferSave,
            "StockTransferEdit": StockTransferEdit,
            "StockTransferDelete": StockTransferDelete,
            "ExcessStocksView": ExcessStocksView,
            "ExcessStocksSave": ExcessStocksSave,
            "ExcessStocksEdit": ExcessStocksEdit,
            "ExcessStocksDelete": ExcessStocksDelete,
            "ShortageStocksView": ShortageStocksView,
            "ShortageStocksSave": ShortageStocksSave,
            "ShortageStocksEdit": ShortageStocksEdit,
            "ShortageStocksDelete": ShortageStocksDelete,
            "DamageStocksView": DamageStocksView,
            "DamageStocksSave": DamageStocksSave,
            "DamageStocksEdit": DamageStocksEdit,
            "DamageStocksDelete": DamageStocksDelete,
            "UsedStocksView": UsedStocksView,
            "UsedStocksSave": UsedStocksSave,
            "UsedStocksEdit": UsedStocksEdit,
            "UsedStocksDelete": UsedStocksDelete,
            "StockAdjustmentsView": StockAdjustmentsView,
            "StockAdjustmentsSave": StockAdjustmentsSave,
            "StockAdjustmentsEdit": StockAdjustmentsEdit,
            "StockAdjustmentsDelete": StockAdjustmentsDelete,
            "SalesOrderView": SalesOrderView,
            "PurchaseOrderView": PurchaseOrderView,
            "SalesOrderSave": SalesOrderSave,
            "PurchaseOrderSave": PurchaseOrderSave,
            "SalesOrderEdit": SalesOrderEdit,
            "PurchaseOrderEdit": PurchaseOrderEdit,
            "SalesOrderDelete": SalesOrderDelete,
            "PurchaseOrderDelete": PurchaseOrderDelete,
            # ===
            "SalesEstimateView": SalesEstimateView,
            "SalesEstimateSave": SalesEstimateSave,
            "SalesEstimateEdit": SalesEstimateEdit,
            "SalesEstimateDelete": SalesEstimateDelete,
            # ===Print===
            "PurchaseInvoicesPrint": PurchaseInvoicesPrint,
            "PurchaseReturnsPrint": PurchaseReturnsPrint,
            "SaleInvoicesPrint": SaleInvoicesPrint,
            "SalesOrderPrint": SalesOrderPrint,
            "PurchaseOrderPrint": PurchaseOrderPrint,
            "SalesEstimatePrint": SalesEstimatePrint,
            "SaleReturnsPrint": SaleReturnsPrint,
            # =====
            "PurchaseInvoicesDiscountLimit": PurchaseInvoicesDiscountLimit,
            "PurchaseReturnsDiscountLimit": PurchaseReturnsDiscountLimit,
            "SaleInvoicesDiscountLimit": SaleInvoicesDiscountLimit,
            "SaleReturnsDiscountLimit": SaleReturnsDiscountLimit,
            # Inventory => Reports
            "StockReportView": StockReportView,
            "StockReportPrint": StockReportPrint,
            "StockReportExport": StockReportExport,
            "StockValueReportView": StockValueReportView,
            "StockValueReportPrint": StockValueReportPrint,
            "StockValueReportExport": StockValueReportExport,
            "PurchaseReportView": PurchaseReportView,
            "PurchaseReportPrint": PurchaseReportPrint,
            "PurchaseReportExport": PurchaseReportExport,
            "SalesReportView": SalesReportView,
            "SalesReportPrint": SalesReportPrint,
            "SalesReportExport": SalesReportExport,
            "SalesIntegratedReportView": SalesIntegratedReportView,
            "SalesIntegratedReportPrint": SalesIntegratedReportPrint,
            "SalesIntegratedReportExport": SalesIntegratedReportExport,
            "PurchaseIntegratedReportPrint": PurchaseIntegratedReportPrint,
            "PurchaseIntegratedReportView": PurchaseIntegratedReportView,
            "PurchaseIntegratedReportExport": PurchaseIntegratedReportExport,
            "SalesRegisterReportView": SalesRegisterReportView,
            "SalesRegisterReportPrint": SalesRegisterReportPrint,
            "SalesRegisterReportExport": SalesRegisterReportExport,
            "BillWiseReportView": BillWiseReportView,
            "BillWiseReportPrint": BillWiseReportPrint,
            "BillWiseReportExport": BillWiseReportExport,
            "ExcessStockReportView": ExcessStockReportView,
            "ExcessStockReportPrint": ExcessStockReportPrint,
            "ExcessStockReportExport": ExcessStockReportExport,
            "DamageStockReportView": DamageStockReportView,
            "DamageStockReportPrint": DamageStockReportPrint,
            "DamageStockReportExport": DamageStockReportExport,
            "UsedStockReportView": UsedStockReportView,
            "UsedStockReportPrint": UsedStockReportPrint,
            "UsedStockReportExport": UsedStockReportExport,
            "BatchWiseReportView": BatchWiseReportView,
            "BatchWiseReportPrint": BatchWiseReportPrint,
            "BatchWiseReportExport": BatchWiseReportExport,
            # ===***===
            "ProductReportView": ProductReportView,
            "ProductReportPrint": ProductReportPrint,
            "ProductReportExport": ProductReportExport,
            "StockLedgerReportView": StockLedgerReportView,
            "StockLedgerReportPrint": StockLedgerReportPrint,
            "StockLedgerReportExport": StockLedgerReportExport,
            "PurchaseOrderReportView": PurchaseOrderReportView,
            "PurchaseOrderReportPrint": PurchaseOrderReportPrint,
            "PurchaseOrderReportExport": PurchaseOrderReportExport,
            "PurchaseRegisterReportView": PurchaseRegisterReportView,
            "PurchaseRegisterReportPrint": PurchaseRegisterReportPrint,
            "PurchaseRegisterReportExport": PurchaseRegisterReportExport,
            "SalesReturnRegisterReportView": SalesReturnRegisterReportView,
            "SalesReturnRegisterReportPrint": SalesReturnRegisterReportPrint,
            "SalesReturnRegisterReportExport": SalesReturnRegisterReportExport,
            "PurchaseReturnRegisterReportView": PurchaseReturnRegisterReportView,
            "PurchaseReturnRegisterReportPrint": PurchaseReturnRegisterReportPrint,
            "PurchaseReturnRegisterReportExport": PurchaseReturnRegisterReportExport,
            "SalesSummaryReportView": SalesSummaryReportView,
            "SalesSummaryReportPrint": SalesSummaryReportPrint,
            "SalesSummaryReportExport": SalesSummaryReportExport,
            "StockTransferRegisterReportView": StockTransferRegisterReportView,
            "StockTransferRegisterReportPrint": StockTransferRegisterReportPrint,
            "StockTransferRegisterReportExport": StockTransferRegisterReportExport,
            "InventoryFlowReportView": InventoryFlowReportView,
            "InventoryFlowReportPrint": InventoryFlowReportPrint,
            "InventoryFlowReportExport": InventoryFlowReportExport,
            "SupplierVsProductReportView": SupplierVsProductReportView,
            "SupplierVsProductReportPrint": SupplierVsProductReportPrint,
            "SupplierVsProductReportExport": SupplierVsProductReportExport,
            "ProductAnalysisReportView": ProductAnalysisReportView,
            "ProductAnalysisReportPrint": ProductAnalysisReportPrint,
            "ProductAnalysisReportExport": ProductAnalysisReportExport,
            "OpeningStockReportView": OpeningStockReportView,
            "OpeningStockReportPrint": OpeningStockReportPrint,
            "OpeningStockReportExport": OpeningStockReportExport,
            "ShortageStocksReportView": ShortageStocksReportView,
            "ShortageStocksReportPrint": ShortageStocksReportPrint,
            "ShortageStocksReportExport": ShortageStocksReportExport,
            # ===***===
            # Payroll => Masters
            "DepartmentsView": DepartmentsView,
            "DepartmentsSave": DepartmentsSave,
            "DepartmentsEdit": DepartmentsEdit,
            "DepartmentsDelete": DepartmentsDelete,
            "DesignationsView": DesignationsView,
            "DesignationsSave": DesignationsSave,
            "DesignationsEdit": DesignationsEdit,
            "DesignationsDelete": DesignationsDelete,
            "EmployeeView": EmployeeView,
            "EmployeeSave": EmployeeSave,
            "EmployeeEdit": EmployeeEdit,
            "EmployeeDelete": EmployeeDelete,
            "CategoriesView": CategoriesView,
            "CategoriesSave": CategoriesSave,
            "CategoriesEdit": CategoriesEdit,
            "CategoriesDelete": CategoriesDelete,
            # Settings
            "PrinterView": PrinterView,
            "BarcodeView": BarcodeView,
            "PrintBarcodeView": PrintBarcodeView,
            # UserType
            "UserType": str(UserTypeValue.id),
            "UserTypeName": UserTypeName,
        }
        serialized_data = json.loads(json.dumps(data))
        response_data = {
            "StatusCode": 6000,
            "data": serialized_data,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:

        # arguments order :- User, GroupName, SettingsType, SettingsValue
        # Accounts => Masters
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "AccountGroupView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "AccountGroupSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "AccountGroupEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "AccountGroupDelete",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "AccountLedgerView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "AccountLedgerSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "AccountLedgerEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "AccountLedgerDelete",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "BankView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "BankSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "BankEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "BankDelete",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "CustomerView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "CustomerSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "CustomerEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "CustomerDelete",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "SupplierView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "SupplierSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "SupplierEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "SupplierDelete",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "TransactionTypeView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "TransactionTypeSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "TransactionTypeEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Masters",
            "TransactionTypeDelete",
            True,
            UserTypeValue,
        )

        # Accounts => Transactions
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "BankPaymentDelete",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "BankPaymentEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "BankPaymentSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "BankPaymentView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "BankReceiptDelete",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "BankReceiptEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "BankReceiptSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "BankReceiptView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "CashPaymentDelete",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "CashPaymentEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "CashPaymentSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "CashPaymentView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "CashReceiptDelete",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "CashReceiptEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "CashReceiptSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "CashReceiptView",
            True,
            UserTypeValue,
        )

        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "JournalEntryDelete",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "JournalEntryEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "JournalEntrySave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "JournalEntryView",
            True,
            UserTypeValue,
        )

        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "CashPaymentPrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "CashReceiptPrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "BankPaymentPrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "BankReceiptPrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "JournalEntryPrint",
            True,
            UserTypeValue,
        )

        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "CashPaymentDiscountLimit",
            0,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "CashReceiptDiscountLimit",
            0,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "BankPaymentLimit",
            0,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Transactions",
            "BankReceiptLimit",
            0,
            UserTypeValue,
        )
        # Accounts => Reports
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "LedgerReportView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "LedgerReportPrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "LedgerReportExport",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "TrialBalanceView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "TrialBalancePrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "TrialBalanceExport",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "ProfitAndLossView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "ProfitAndLossPrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "ProfitAndLossExport",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "BalanceSheetView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "BalanceSheetPrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "BalanceSheetExport",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "DailyReportView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "DailyReportPrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "DailyReportExport",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "CashBookView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "CashBookPrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "CashBookExport",
            True,
            UserTypeValue,
        )

        # ===========
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "BankBookReportView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "BankBookReportPrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "BankBookReportExport",
            True,
            UserTypeValue,
        )

        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "OutstandingReportView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "OutstandingReportPrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "OutstandingReportExport",
            True,
            UserTypeValue,
        )

        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "RecieptReportView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "RecieptReportPrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "RecieptReportExport",
            True,
            UserTypeValue,
        )

        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "PaymentReportView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "PaymentReportPrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "PaymentReportExport",
            True,
            UserTypeValue,
        )
        # ==========

        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "VATReportView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "VATReportPrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "VATReportExport",
            True,
            UserTypeValue,
        )

        # Accounts => GST Report
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "SalesGSTReportView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "SalesGSTReportPrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "SalesGSTReportExport",
            True,
            UserTypeValue,
        )

        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "PurchaseGSTReportView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "PurchaseGSTReportPrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Accounts_Reports",
            "PurchaseGSTReportExport",
            True,
            UserTypeValue,
        )

        # Inventory => Masters
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "ProductGroupView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "ProductGroupSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "ProductGroupEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "ProductGroupDelete",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "BrandsView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "BrandsSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "BrandsEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "BrandsDelete",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "TaxCategoriesView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "TaxCategoriesSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "TaxCategoriesEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "TaxCategoriesDelete",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "PriceCategoriesView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "PriceCategoriesSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "PriceCategoriesEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "PriceCategoriesDelete",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "WarehouseView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "WarehouseSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "WarehouseEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "WarehouseDelete",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "ProductCategoriesView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "ProductCategoriesSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "ProductCategoriesEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "ProductCategoriesDelete",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "ProductsView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "ProductsSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "ProductsEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "ProductsDelete",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "RoutesView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "RoutesSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "RoutesEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "RoutesDelete",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "UnitsView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "UnitsSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "UnitsEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Masters",
            "UnitsDelete",
            True,
            UserTypeValue,
        )

        # Inventory => Transaction
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseInvoicesView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseInvoicesSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseInvoicesEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseInvoicesDelete",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "WorkOrdersView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "WorkOrdersSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "WorkOrdersEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "WorkOrdersDelete",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseReturnsView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseReturnsSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseReturnsEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseReturnsDelete",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SaleInvoicesView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SaleInvoicesSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SaleInvoicesEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SaleInvoicesDelete",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SaleReturnsView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SaleReturnsSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SaleReturnsEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SaleReturnsDelete",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "OpeningStockView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "OpeningStockSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "OpeningStockEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "OpeningStockDelete",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "StockTransferView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "StockTransferSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "StockTransferEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "StockTransferDelete",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "ExcessStocksView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "ExcessStocksSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "ExcessStocksEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "ExcessStocksDelete",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "ShortageStocksView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "ShortageStocksSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "ShortageStocksEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "ShortageStocksDelete",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "DamageStocksView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "DamageStocksSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "DamageStocksEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "DamageStocksDelete",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "UsedStocksView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "UsedStocksSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "UsedStocksEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "UsedStocksDelete",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "StockAdjustmentsView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "StockAdjustmentsSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "StockAdjustmentsEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "StockAdjustmentsDelete",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SalesOrderView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseOrderView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SalesOrderSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseOrderSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SalesOrderEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseOrderEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SalesOrderDelete",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseOrderDelete",
            True,
            UserTypeValue,
        )

        # =====
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SalesEstimateView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SalesEstimateSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SalesEstimateEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SalesEstimateDelete",
            True,
            UserTypeValue,
        )
        # =====Print=====
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseInvoicesPrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseReturnsPrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SaleInvoicesPrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SalesOrderPrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseOrderPrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SalesEstimatePrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SaleReturnsPrint",
            True,
            UserTypeValue,
        )
        # =====Print=====

        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseInvoicesDiscountLimit",
            0,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "PurchaseReturnsDiscountLimit",
            0,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SaleInvoicesDiscountLimit",
            0,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Transactions",
            "SaleReturnsDiscountLimit",
            0,
            UserTypeValue,
        )
        # Inventory => Reports
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "StockReportView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "StockReportPrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "StockReportExport",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "StockValueReportView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "StockValueReportPrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "StockValueReportExport",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "PurchaseReportView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "PurchaseReportPrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "PurchaseReportExport",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "SalesReportView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "SalesReportPrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "SalesReportExport",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "SalesIntegratedReportView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "SalesIntegratedReportPrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "SalesIntegratedReportExport",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "PurchaseIntegratedReportPrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "PurchaseIntegratedReportView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "PurchaseIntegratedReportExport",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "SalesRegisterReportView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "SalesRegisterReportPrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "SalesRegisterReportExport",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "BillWiseReportView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "BillWiseReportPrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "BillWiseReportExport",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "ExcessStockReportView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "ExcessStockReportPrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "ExcessStockReportExport",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "DamageStockReportView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "DamageStockReportPrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "DamageStockReportExport",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "UsedStockReportView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "UsedStockReportPrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "UsedStockReportExport",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "BatchWiseReportView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "BatchWiseReportPrint",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "BatchWiseReportExport",
            True,
            UserTypeValue,
        )
        # ===***===
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "ProductReportExport",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "StockLedgerReportExport",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "PurchaseOrderReportExport",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "PurchaseRegisterReportExport",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "SalesReturnRegisterReportExport",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "PurchaseReturnRegisterReportExport",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "SalesSummaryReportExport",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "StockTransferRegisterReportExport",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "InventoryFlowReportExport",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "SupplierVsProductReportExport",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "ProductAnalysisReportExport",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "OpeningStockReportExport",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Inventory_Reports",
            "ShortageStocksReportExport",
            True,
            UserTypeValue,
        )
        # ===***===
        # Payroll => Masters
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Payroll_Masters",
            "DepartmentsView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Payroll_Masters",
            "DepartmentsSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Payroll_Masters",
            "DepartmentsEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Payroll_Masters",
            "DepartmentsDelete",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Payroll_Masters",
            "DesignationsView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Payroll_Masters",
            "DesignationsSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Payroll_Masters",
            "DesignationsEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Payroll_Masters",
            "DesignationsDelete",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Payroll_Masters",
            "EmployeeView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Payroll_Masters",
            "EmployeeSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Payroll_Masters",
            "EmployeeEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Payroll_Masters",
            "EmployeeDelete",
            True,
            UserTypeValue,
        )

        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Payroll_Masters",
            "CategoriesView",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Payroll_Masters",
            "CategoriesSave",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Payroll_Masters",
            "CategoriesEdit",
            True,
            UserTypeValue,
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Payroll_Masters",
            "CategoriesDelete",
            True,
            UserTypeValue,
        )

        # Settings
        create_or_update_user_type_settings(
            User, CompanyID, BranchID, "Settings", "PrinterView", True, UserTypeValue
        )
        create_or_update_user_type_settings(
            User, CompanyID, BranchID, "Settings", "BarcodeView", True, UserTypeValue
        )
        create_or_update_user_type_settings(
            User,
            CompanyID,
            BranchID,
            "Settings",
            "PrintBarcodeView",
            True,
            UserTypeValue,
        )

        # return HttpResponse(reverse('api_v6_settings:user_type_settings_list'))
        response_data = {"StatusCode": 6000, "message": "success"}
        return Response(response_data, status=status.HTTP_200_OK)


# def print_paper(request):

#     # data = {
#     #     'today': datetime.date.today(),
#     #     'amount': 39.99,
#     #     'customer_name': 'Cooper Mann',
#     #     'order_id': 1233434,
#     # }
#     # pdf = render_to_pdf('print.html',data)
#     # return HttpResponse(pdf, content_type='application/pdf')
#     context = {
#         "title":"invoice",
#         "invoice_id": 123,
#         "customer_name": "John Cooper",
#         "amount": 1399.99,
#         "today": "Today",
#     }
#     pdf = render_to_pdf('print.html', context,no_of_page=1)
#     if pdf:
#         response = HttpResponse(pdf, content_type='application/pdf')
#         filename = "Invoice_%s.pdf" %("12341231")
#         content = "inline; filename='%s'" %(filename)
#         download = request.GET.get("download")
#         if download:
#             content = "attachment; filename='%s'" %(filename)
#         response['Content-Disposition'] = content
#         response['X-Frame-Options'] = "allow-all"
#         return response
#     return HttpResponse("Not found")


# def print_paper(request):
#     # html_template = get_template('print.html')
#     html_string = render_to_string('print.html', {})
#     pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(stylesheets=[CSS(settings.STATIC_ROOT +  '/css/print.css')])

#     response = HttpResponse(pdf_file, content_type='application/pdf')
#     response['Content-Disposition'] = 'filename="home_page.pdf"'
#     return response


@api_view(["GET"])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def print_paper(request):
    writer = PdfFileWriter()
    CompanyID = request.GET.get("CompanyID")
    BranchID = request.GET.get("BranchID")
    no_of_copies = int(request.GET.get("no_of_copies"))
    invoice_type = request.GET.get("invoice_type")
    invoice_id = request.GET.get("invoice_id")
    try:
        PriceRounding = int(request.GET.get("PriceRounding"))
    except:
        PriceRounding = 2
    company_instance = models.CompanySettings.objects.get(id=CompanyID)
    branch_instance = models.Branch.objects.get(
        BranchID=BranchID, CompanyID=company_instance
    )
    company_name = branch_instance.DisplayName
    country_instance = models.Country.objects.get(id=company_instance.Country.id)
    print_settings_instance, created = models.PrintSettingsNew.objects.get_or_create(
        CompanyID=company_instance, InvoiceType=invoice_type
    )

    data = {}
    grand_total = 0
    details = {}
    qr_code = None
    instance_serialized = {}
    invoice_time = ""
    if invoice_type == "sales_invoice":
        if models.SalesMaster.objects.filter(
            CompanyID=CompanyID, pk=invoice_id
        ).exists():
            instance = models.SalesMaster.objects.get(
                CompanyID=CompanyID, pk=invoice_id
            )
            instance_serialized = SalesMasterRestSerializer(
                instance,
                many=False,
                context={
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                    "request": request,
                },
            ).data
            details = instance_serialized["SalesDetails"]
            grand_total = instance_serialized.get("GrandTotal_print")
            invoice_time = get_country_time(
                instance.CreatedDate, country_instance.Country_Name
            )

    if invoice_type == "sales_estimate":
        if models.SalesEstimateMaster.objects.filter(
            CompanyID=CompanyID, pk=invoice_id
        ).exists():
            instance = models.SalesEstimateMaster.objects.get(
                CompanyID=CompanyID, pk=invoice_id
            )
            instance_serialized = SalesEstimateMasterRestSerializer(
                instance,
                many=False,
                context={
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                    "request": request,
                },
            ).data
            details = instance_serialized["SalesEstimateDetails"]
            grand_total = instance_serialized.get("GrandTotal")
            invoice_time = get_country_time(
                instance.CreatedDate, country_instance.Country_Name
            )

    if invoice_type == "purchase_invoice":
        if models.PurchaseMaster.objects.filter(
            CompanyID=CompanyID, pk=invoice_id
        ).exists():
            instance = models.PurchaseMaster.objects.get(
                CompanyID=CompanyID, pk=invoice_id
            )
            instance_serialized = PurchaseMasterRestSerializer(
                instance,
                many=False,
                context={
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                    "request": request,
                },
            ).data
            details = instance_serialized["PurchaseDetails"]
            grand_total = instance_serialized.get("GrandTotal_print")
            invoice_time = get_country_time(
                instance.CreatedDate, country_instance.Country_Name
            )

    if invoice_type == "sales_return":
        if models.SalesReturnMaster.objects.filter(
            CompanyID=CompanyID, pk=invoice_id
        ).exists():
            instance = models.SalesReturnMaster.objects.get(
                CompanyID=CompanyID, pk=invoice_id
            )
            instance_serialized = SalesReturnMasterRestSerializer(
                instance,
                many=False,
                context={
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                    "request": request,
                },
            ).data
            details = instance_serialized["SalesReturnDetails"]
            grand_total = instance_serialized.get("GrandTotal_print")
            invoice_time = get_country_time(
                instance.CreatedDate, country_instance.Country_Name
            )

    if invoice_type == "purchase_return":
        if models.PurchaseReturnMaster.objects.filter(
            CompanyID=CompanyID, pk=invoice_id
        ).exists():
            instance = models.PurchaseReturnMaster.objects.get(
                CompanyID=CompanyID, pk=invoice_id
            )
            instance_serialized = PurchaseReturnMasterRestSerializer(
                instance,
                many=False,
                context={
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                    "request": request,
                },
            ).data
            details = instance_serialized["PurchaseReturnDetails"]
            grand_total = instance_serialized.get("GrandTotal_print")
            invoice_time = get_country_time(
                instance.CreatedDate, country_instance.Country_Name
            )

    if invoice_type == "payment_voucher":
        if models.PaymentMaster.objects.filter(
            CompanyID=CompanyID, pk=invoice_id
        ).exists():
            instance = models.PaymentMaster.objects.get(
                CompanyID=CompanyID, pk=invoice_id
            )
            instance_serialized = PaymentMasterRestSerializer(
                instance,
                many=False,
                context={
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                },
            ).data
            details = instance_serialized["PaymentDetails"]
            grand_total = instance_serialized.get("TotalAmount_rounded")
            invoice_time = get_country_time(
                instance.CreatedDate, country_instance.Country_Name
            )
    if invoice_type == "receipt_voucher":
        if models.ReceiptMaster.objects.filter(
            CompanyID=CompanyID, pk=invoice_id
        ).exists():
            instance = models.ReceiptMaster.objects.get(
                CompanyID=CompanyID, pk=invoice_id
            )
            instance_serialized = ReceiptMasterRestSerializer(
                instance,
                many=False,
                context={
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                },
            ).data
            details = instance_serialized["ReceiptDetails"]
            grand_total = instance_serialized.get("TotalAmount_rounded")
            invoice_time = get_country_time(
                instance.CreatedDate, country_instance.Country_Name
            )

    company_instance = models.CompanySettings.objects.get(id=CompanyID)
    serialized = CompanySettingsPrintRestSerializer(
        company_instance, many=False, context={"request": request}
    )

    data = {
        "company_name": company_name,
        "country": country_instance,
        "invoice_type": invoice_type,
        "type": "pdf",
        "company": serialized.data,
        "amount_in_words": num2words(grand_total, to="cardinal", lang="en_IN"),
        "details": details,
        "data": instance_serialized,
        "PriceRounding": PriceRounding,
        "settings": print_settings_instance,
        "qr_code": qr_code,
        "invoice_time": invoice_time,
    }
    if invoice_type == "payment_voucher" or invoice_type == "receipt_voucher":
        template = get_template("payment_print.html")
    else:
        if print_settings_instance.template == "template3":
            template = get_template("print_template_three.html")
        elif print_settings_instance.template == "template2":
            template = get_template("print_template_two.html")
        else:
            template = get_template("print.html")

    html = template.render(data)

    options = {
        "page-size": "Letter",
        "encoding": "UTF-8",
        "margin-top": "0.5in",
        "margin-right": "0.5in",
        "margin-bottom": "0.5in",
        "margin-left": "0.5in",
        "custom-header": [("Accept-Encoding", "gzip")],
    }
    for i in range(no_of_copies):
        stream = BytesIO()
        stream.write(pdfkit.from_string(html, False, options=options))
        count = PdfFileReader(stream).numPages
        # writer.addPage(PdfFileReader(stream).getPage(0))

        for j in range(count):
            page = PdfFileReader(stream).getPage(j)
            writer.addPage(page)
    output = BytesIO()
    pdf = writer.write(output)
    pdf = pdfkit.from_string(html, False, options)
    response = HttpResponse(output.getvalue(), content_type="application/pdf")
    # response = HttpResponse(pdf, content_type='application/pdf')
    response["Content-Disposition"] = "inline"
    response["X-Frame-Options"] = "allow-all"
    # response['content-security-policy'] = "frame-ancestors 'self' http://localhost:3000"
    return response


# @api_view(["GET"])
# @permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
# @renderer_classes((JSONRenderer,))
# def print_paper_new(request):
#     print("#########RECEIPT MASTER########")

#     writer = PdfFileWriter()
#     CompanyID = request.GET.get("CompanyID")
#     BranchID = request.GET.get("BranchID")
#     no_of_copies = int(request.GET.get("no_of_copies"))
#     invoice_type = request.GET.get("invoice_type")
#     invoice_id = request.GET.get("invoice_id")
#     print_template = request.GET.get("print_template")
#     if print_template:
#         print_template = False
#     else:
#         print_template = True

#     try:
#         PriceRounding = int(request.GET.get("PriceRounding"))
#     except:
#         PriceRounding = 2

#     company_instance = models.CompanySettings.objects.get(id=CompanyID)
#     company_name = company_instance.CompanyName
#     if models.Branch.objects.filter(
#         BranchID=BranchID, CompanyID=company_instance
#     ).exists():
#         branch_instance = models.Branch.objects.get(
#             BranchID=BranchID, CompanyID=company_instance
#         )
#         company_name = branch_instance.DisplayName
#     country_instance = models.Country.objects.get(id=company_instance.Country.id)
#     print_settings_instance, created = models.PrintSettingsNew.objects.get_or_create(
#         CompanyID=company_instance, InvoiceType=invoice_type
#     )

#     data = {}
#     grand_total = 0
#     details = {}
#     qr_code = None
#     instance_serialized = {}
#     invoice_time = ""
#     vat_perc = ""
#     total_qty = None
#     if invoice_type == "sales_invoice":
#         if models.SalesMaster.objects.filter(
#             CompanyID=CompanyID, pk=invoice_id
#         ).exists():
#             instance = models.SalesMaster.objects.get(
#                 CompanyID=CompanyID, pk=invoice_id
#             )
#             instance_serialized = SalesMasterRestSerializer(
#                 instance,
#                 many=False,
#                 context={
#                     "CompanyID": CompanyID,
#                     "PriceRounding": PriceRounding,
#                     "request": request,
#                 },
#             ).data
#             details = instance_serialized["SalesDetails"]
#             total_qty = (
#                 models.SalesDetails.objects.filter(
#                     CompanyID=CompanyID, SalesMasterID=instance.SalesMasterID
#                 )
#                 .aggregate(Sum("Qty"))
#                 .get("Qty__sum")
#             )

#             grand_total = instance_serialized.get("GrandTotal_print")
#             invoice_time = get_country_time(
#                 instance.CreatedDate, country_instance.Country_Name
#             )
#             vat_perc = details[0]["VATPerc_print"]

#     if invoice_type == "sales_order":
#         if models.SalesOrderMaster.objects.filter(
#             CompanyID=CompanyID, pk=invoice_id
#         ).exists():
#             instance = models.SalesOrderMaster.objects.get(
#                 CompanyID=CompanyID, pk=invoice_id
#             )
#             instance_serialized = SalesOrderMasterRestSerializer(
#                 instance,
#                 many=False,
#                 context={
#                     "CompanyID": CompanyID,
#                     "PriceRounding": PriceRounding,
#                     "request": request,
#                 },
#             ).data
#             details = instance_serialized["SalesOrderDetails"]
#             grand_total = instance_serialized.get("GrandTotal_print")
#             if grand_total is None:
#                 grand_total = 0
#             invoice_time = get_country_time(
#                 instance.CreatedDate, country_instance.Country_Name
#             )

#     if invoice_type == "sales_estimate":
#         if models.SalesEstimateMaster.objects.filter(
#             CompanyID=CompanyID, pk=invoice_id
#         ).exists():
#             instance = models.SalesEstimateMaster.objects.get(
#                 CompanyID=CompanyID, pk=invoice_id
#             )
#             instance_serialized = SalesEstimateMasterRestSerializer(
#                 instance,
#                 many=False,
#                 context={
#                     "CompanyID": CompanyID,
#                     "PriceRounding": PriceRounding,
#                     "request": request,
#                 },
#             ).data
#             details = instance_serialized["SalesEstimateDetails"]
#             grand_total = instance_serialized.get("GrandTotal_print")
#             if grand_total is None:
#                 grand_total = 0
#             invoice_time = get_country_time(
#                 instance.CreatedDate, country_instance.Country_Name
#             )

#     if invoice_type == "purchase_invoice":
#         if models.PurchaseMaster.objects.filter(
#             CompanyID=CompanyID, pk=invoice_id
#         ).exists():
#             instance = models.PurchaseMaster.objects.get(
#                 CompanyID=CompanyID, pk=invoice_id
#             )
#             instance_serialized = PurchaseMasterRestSerializer(
#                 instance,
#                 many=False,
#                 context={
#                     "CompanyID": CompanyID,
#                     "PriceRounding": PriceRounding,
#                     "request": request,
#                 },
#             ).data
#             details = instance_serialized["PurchaseDetails"]
#             grand_total = instance_serialized.get("GrandTotal_print")
#             invoice_time = get_country_time(
#                 instance.CreatedDate, country_instance.Country_Name
#             )

#     if invoice_type == "sales_return":
#         if models.SalesReturnMaster.objects.filter(
#             CompanyID=CompanyID, pk=invoice_id
#         ).exists():
#             instance = models.SalesReturnMaster.objects.get(
#                 CompanyID=CompanyID, pk=invoice_id
#             )
#             instance_serialized = SalesReturnMasterRestSerializer(
#                 instance,
#                 many=False,
#                 context={
#                     "CompanyID": CompanyID,
#                     "PriceRounding": PriceRounding,
#                     "request": request,
#                 },
#             ).data
#             details = instance_serialized["SalesReturnDetails"]
#             grand_total = instance_serialized.get("GrandTotal_print")
#             invoice_time = get_country_time(
#                 instance.CreatedDate, country_instance.Country_Name
#             )

#     if invoice_type == "purchase_return":
#         if models.PurchaseReturnMaster.objects.filter(
#             CompanyID=CompanyID, pk=invoice_id
#         ).exists():
#             instance = models.PurchaseReturnMaster.objects.get(
#                 CompanyID=CompanyID, pk=invoice_id
#             )
#             instance_serialized = PurchaseReturnMasterRestSerializer(
#                 instance,
#                 many=False,
#                 context={
#                     "CompanyID": CompanyID,
#                     "PriceRounding": PriceRounding,
#                     "request": request,
#                 },
#             ).data
#             details = instance_serialized["PurchaseReturnDetails"]
#             grand_total = instance_serialized.get("GrandTotal_print")
#             invoice_time = get_country_time(
#                 instance.CreatedDate, country_instance.Country_Name
#             )

#     if invoice_type == "payment_voucher":
#         if models.PaymentMaster.objects.filter(
#             CompanyID=CompanyID, pk=invoice_id
#         ).exists():
#             instance = models.PaymentMaster.objects.get(
#                 CompanyID=CompanyID, pk=invoice_id
#             )
#             instance_serialized = PaymentMasterRestSerializer(
#                 instance,
#                 many=False,
#                 context={
#                     "CompanyID": CompanyID,
#                     "PriceRounding": PriceRounding,
#                 },
#             ).data
#             details = instance_serialized["PaymentDetails"]
#             grand_total = instance_serialized.get("TotalAmount_rounded")
#             invoice_time = get_country_time(
#                 instance.CreatedDate, country_instance.Country_Name
#             )
#     if invoice_type == "receipt_voucher":
#         if models.ReceiptMaster.objects.filter(
#             CompanyID=CompanyID, pk=invoice_id
#         ).exists():
#             instance = models.ReceiptMaster.objects.get(
#                 CompanyID=CompanyID, pk=invoice_id
#             )
#             instance_serialized = ReceiptMasterRestSerializer(
#                 instance,
#                 many=False,
#                 context={
#                     "CompanyID": CompanyID,
#                     "PriceRounding": PriceRounding,
#                 },
#             ).data
#             details = instance_serialized["ReceiptDetails"]
#             grand_total = instance_serialized.get("TotalAmount_rounded")
#             invoice_time = get_country_time(
#                 instance.CreatedDate, country_instance.Country_Name
#             )

#     if invoice_type == "journal":
#         if models.JournalMaster.objects.filter(
#             CompanyID=CompanyID, pk=invoice_id
#         ).exists():
#             instance = models.JournalMaster.objects.get(
#                 CompanyID=CompanyID, pk=invoice_id
#             )
#             instance_serialized = JournalMasterRestSerializer(
#                 instance,
#                 many=False,
#                 context={
#                     "CompanyID": CompanyID,
#                     "PriceRounding": PriceRounding,
#                 },
#             ).data
#             details = instance_serialized["JournalDetails"]
#             print(details)

#             grand_total = instance_serialized.get("TotalAmount_rounded")
#             invoice_time = get_country_time(
#                 instance.CreatedDate, country_instance.Country_Name
#             )

#     GST = models.GeneralSettings.objects.get(
#         CompanyID=CompanyID, SettingsType="GST", BranchID=1
#     ).SettingsValue
#     if models.GeneralSettings.objects.filter(
#         CompanyID=CompanyID, SettingsType="GST", BranchID=BranchID
#     ).exists():
#         GST = models.GeneralSettings.objects.get(
#             CompanyID=CompanyID, SettingsType="GST", BranchID=BranchID
#         ).SettingsValue
#     if GST == "true" or GST == "True":
#         GST = True
#     else:
#         GST = False

#     company_instance = models.CompanySettings.objects.get(id=CompanyID)
#     serialized = CompanySettingsPrintRestSerializer(
#         company_instance, many=False, context={"request": request}
#     )
#     data = {
#         "company_name": company_name,
#         "country": country_instance,
#         "invoice_type": invoice_type,
#         "type": "pdf",
#         "company": serialized.data,
#         "amount_in_words": num2words(float(grand_total), to="cardinal", lang="en_IN"),
#         "amount_in_words_arabic": num2words(
#             float(grand_total), to="cardinal", lang="ar"
#         ),
#         "details": details,
#         "data": instance_serialized,
#         "PriceRounding": PriceRounding,
#         "settings": print_settings_instance,
#         "qr_code": qr_code,
#         "invoice_time": invoice_time,
#         "print_template": print_template,
#         "GST": GST,
#         "vat_perc": vat_perc,
#         "total_qty": total_qty,
#     }
#     if invoice_type == "journal":
#         response = render(request, "journal_print.html", data)
#     elif invoice_type == "payment_voucher" or invoice_type == "receipt_voucher":
#         response = render(request, "payment_print.html", data)
#     else:
#         if print_settings_instance.template == "template9":
#             response = render(request, "print_template_seven.html", data)
#         elif print_settings_instance.template == "template8":
#             response = render(request, "print_template_six.html", data)
#         elif print_settings_instance.template == "template7":
#             response = render(request, "print_template_five.html", data)
#         elif print_settings_instance.template == "template6":
#             response = render(request, "thermalTwo.html", data)
#         elif print_settings_instance.template == "template5":
#             response = render(request, "thermalOne.html", data)
#         elif print_settings_instance.template == "template4":
#             response = render(request, "print_template_four.html", data)
#         elif print_settings_instance.template == "template3":
#             response = render(request, "print_template_three.html", data)
#         elif print_settings_instance.template == "template2":
#             response = render(request, "print_template_two.html", data)
#         else:
#             response = render(request, "print.html", data)

#     response["X-Frame-Options"] = "allow-all"
#     response["Access-Control-Allow-Origin"] = "http://localhost:3000"
#     response["Content-Security-Policy"] = "http://localhost:3000"

#     return response


@api_view(["GET"])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def print_thermal(request):
    response = render(request, "thermalTwo.html", {})
    response["X-Frame-Options"] = "allow-all"
    response["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response["Content-Security-Policy"] = "http://localhost:3000"

    return response


@api_view(["GET"])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def print_paper_new(request):
    writer = PdfFileWriter()
    CompanyID = request.GET.get("CompanyID")
    BranchID = request.GET.get("BranchID")
    no_of_copies = int(request.GET.get("no_of_copies"))
    invoice_type = request.GET.get("invoice_type")
    invoice_id = request.GET.get("invoice_id")
    print_template = request.GET.get("print_template")
    if print_template:
        print_template = False
    else:
        print_template = True

    try:
        PriceRounding = int(request.GET.get("PriceRounding"))
    except:
        PriceRounding = 2

    company_instance = models.CompanySettings.objects.get(id=CompanyID)
    company_name = company_instance.CompanyName
    if models.Branch.objects.filter(
        BranchID=BranchID, CompanyID=company_instance
    ).exists():
        branch_instance = models.Branch.objects.get(
            BranchID=BranchID, CompanyID=company_instance
        )
        company_name = branch_instance.DisplayName
    country_instance = models.Country.objects.get(id=company_instance.Country.id)
    try:
        print_settings_instance, created = models.PrintSettingsNew.objects.get_or_create(
            CompanyID=company_instance, InvoiceType=invoice_type
        )
    except:
        print_settings_instance = models.PrintSettingsNew.objects.filter(CompanyID=company_instance, InvoiceType=invoice_type).first()

    data = {}
    grand_total = 0
    details = {}
    qr_code = None
    instance_serialized = {}
    invoice_time = ""
    vat_perc = ""
    total_qty = None
    address = ""
    IsFqty = False
    if invoice_type == "sales_invoice":
        if models.SalesMaster.objects.filter(
            CompanyID=CompanyID, pk=invoice_id
        ).exists():
            instance = models.SalesMaster.objects.get(
                CompanyID=CompanyID, pk=invoice_id
            )
            instance_serialized = SalesMasterRestSerializer(
                instance,
                many=False,
                context={
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                    "request": request,
                },
            ).data
            details = instance_serialized["SalesDetails"]
            total_qty = (
                models.SalesDetails.objects.filter(
                    CompanyID=CompanyID, SalesMasterID=instance.SalesMasterID
                )
                .aggregate(Sum("Qty"))
                .get("Qty__sum")
            )

            grand_total = instance_serialized.get("GrandTotal_print")
            invoice_time = get_country_time(
                instance.CreatedDate, country_instance.Country_Name
            )
            vat_perc = details[0]["VATPerc_print"]
            IsFqty = get_GeneralSettings(
                company_instance, BranchID, "Free_Quantity_In_Sales")

    if invoice_type == "sales_order":
        if models.SalesOrderMaster.objects.filter(
            CompanyID=CompanyID, pk=invoice_id
        ).exists():
            instance = models.SalesOrderMaster.objects.get(
                CompanyID=CompanyID, pk=invoice_id
            )
            instance_serialized = SalesOrderMasterRestSerializer(
                instance,
                many=False,
                context={
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                    "request": request,
                },
            ).data

            details = instance_serialized["SalesOrderDetails"]
            grand_total = instance_serialized.get("GrandTotal_print")
            if grand_total is None:
                grand_total = 0
            invoice_time = get_country_time(
                instance.CreatedDate, country_instance.Country_Name
            )

    if invoice_type == "sales_estimate":
        if models.SalesEstimateMaster.objects.filter(
            CompanyID=CompanyID, pk=invoice_id
        ).exists():
            instance = models.SalesEstimateMaster.objects.get(
                CompanyID=CompanyID, pk=invoice_id
            )
            instance_serialized = SalesEstimateMasterRestSerializer(
                instance,
                many=False,
                context={
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                    "request": request,
                },
            ).data

            details = instance_serialized["SalesEstimateDetails"]
            grand_total = instance_serialized.get("GrandTotal_print")
            if grand_total is None:
                grand_total = 0
            invoice_time = get_country_time(
                instance.CreatedDate, country_instance.Country_Name
            )

    if invoice_type == "purchase_invoice":
        if models.PurchaseMaster.objects.filter(
            CompanyID=CompanyID, pk=invoice_id
        ).exists():
            instance = models.PurchaseMaster.objects.get(
                CompanyID=CompanyID, pk=invoice_id
            )
            instance_serialized = PurchaseMasterRestSerializer(
                instance,
                many=False,
                context={
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                    "request": request,
                },
            ).data
            details = instance_serialized["PurchaseDetails"]
            total_qty = (
                models.PurchaseDetails.objects.filter(
                    CompanyID=CompanyID, PurchaseMasterID=instance.PurchaseMasterID
                )
                .aggregate(Sum("Qty"))
                .get("Qty__sum")
            )
            grand_total = instance_serialized.get("GrandTotal_print")
            invoice_time = get_country_time(
                instance.CreatedDate, country_instance.Country_Name
            )
            IsFqty = get_GeneralSettings(
                company_instance, BranchID, "Free_Quantity_In_Purchase")

    if invoice_type == "purchase_order":
        if models.PurchaseOrderMaster.objects.filter(
            CompanyID=CompanyID, pk=invoice_id
        ).exists():
            instance = models.PurchaseOrderMaster.objects.get(
                CompanyID=CompanyID, pk=invoice_id
            )
            instance_serialized = PurchaseOrderMasterRestSerializer(
                instance,
                many=False,
                context={
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                    "request": request,
                },
            ).data
            details = instance_serialized["PurchaseOrderDetails"]
            grand_total = instance_serialized.get("GrandTotal_print")
            invoice_time = get_country_time(
                instance.CreatedDate, country_instance.Country_Name
            )

    if invoice_type == "sales_return":
        if models.SalesReturnMaster.objects.filter(
            CompanyID=CompanyID, pk=invoice_id
        ).exists():
            instance = models.SalesReturnMaster.objects.get(
                CompanyID=CompanyID, pk=invoice_id
            )
            instance_serialized = SalesReturnMasterRestSerializer(
                instance,
                many=False,
                context={
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                    "request": request,
                },
            ).data
            details = instance_serialized["SalesReturnDetails"]
            grand_total = instance_serialized.get("GrandTotal_print")
            invoice_time = get_country_time(
                instance.CreatedDate, country_instance.Country_Name
            )

    if invoice_type == "purchase_return":
        if models.PurchaseReturnMaster.objects.filter(
            CompanyID=CompanyID, pk=invoice_id
        ).exists():
            instance = models.PurchaseReturnMaster.objects.get(
                CompanyID=CompanyID, pk=invoice_id
            )
            instance_serialized = PurchaseReturnMasterRestSerializer(
                instance,
                many=False,
                context={
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                    "request": request,
                },
            ).data
            details = instance_serialized["PurchaseReturnDetails"]
            grand_total = instance_serialized.get("GrandTotal_print")
            invoice_time = get_country_time(
                instance.CreatedDate, country_instance.Country_Name
            )

    if invoice_type == "payment_voucher":
        if models.PaymentMaster.objects.filter(
            CompanyID=CompanyID, pk=invoice_id
        ).exists():
            instance = models.PaymentMaster.objects.get(
                CompanyID=CompanyID, pk=invoice_id
            )
            instance_serialized = PaymentMasterRestSerializer(
                instance,
                many=False,
                context={
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                },
            ).data
            details = instance_serialized["PaymentDetails"]
            grand_total = instance_serialized.get("TotalAmount_rounded")
            invoice_time = get_country_time(
                instance.CreatedDate, country_instance.Country_Name
            )

    if invoice_type == "receipt_voucher":
        if models.ReceiptMaster.objects.filter(
            CompanyID=CompanyID, pk=invoice_id
        ).exists():
            instance = models.ReceiptMaster.objects.get(
                CompanyID=CompanyID, pk=invoice_id
            )
            instance_serialized = ReceiptMasterRestSerializer(
                instance,
                many=False,
                context={
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                },
            ).data
            details = instance_serialized["ReceiptDetails"]
            grand_total = instance_serialized.get("TotalAmount_rounded")
            invoice_time = get_country_time(
                instance.CreatedDate, country_instance.Country_Name
            )

    if invoice_type == "stock_transfer" or invoice_type == "stock_order" :
        if models.StockTransferMaster_ID.objects.filter(
            CompanyID=CompanyID, pk=invoice_id
        ).exists():
            instance = models.StockTransferMaster_ID.objects.get(
                CompanyID=CompanyID, pk=invoice_id
            )
            instance_serialized = StockTransferMaster_IDRestSerializer(
                instance,
                many=False,
                context={
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                },
            ).data
            details = instance_serialized["Details"]
            grand_total = instance_serialized.get("GrandTotal")
            invoice_time = get_country_time(
                instance.CreatedDate, country_instance.Country_Name
            )

    if invoice_type == "journal":
        if models.JournalMaster.objects.filter(
            CompanyID=CompanyID, pk=invoice_id
        ).exists():
            instance = models.JournalMaster.objects.get(
                CompanyID=CompanyID, pk=invoice_id
            )
            instance_serialized = JournalMasterRestSerializer(
                instance,
                many=False,
                context={
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                },
            ).data
            details = instance_serialized["JournalDetails"]
            print(details)

            grand_total = 0
            invoice_time = get_country_time(
                instance.CreatedDate, country_instance.Country_Name
            )

    if invoice_type == "expense":
        if models.ExpenseMaster.objects.filter(
            CompanyID=CompanyID, pk=invoice_id
        ).exists():
            instance = models.ExpenseMaster.objects.get(
                CompanyID=CompanyID, pk=invoice_id
            )
            instance_serialized = ExpenseMasterSerializer(
                instance,
                many=False,
                context={
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                },
            ).data
            details = instance_serialized["ExpenseDetails"]
            print(details)

            grand_total = instance_serialized.get("GrandTotal")
            invoice_time = get_country_time(
                instance.CreatedDate, country_instance.Country_Name
            )
    if invoice_type == "work_order":
        if models.WorkOrderMaster.objects.filter(
            CompanyID=CompanyID, pk=invoice_id
        ).exists():
            instance = models.WorkOrderMaster.objects.get(
                CompanyID=CompanyID, pk=invoice_id
            )
            instance_serialized = WorkOrderSerializer(
                instance,
                many=False,
                context={
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                    "request": request,
                },
            ).data
            details = instance_serialized["WorkOrderDetails"]
            grand_total = instance_serialized.get("CostSum")
            invoice_time = get_country_time(
                instance.CreatedDate, country_instance.Country_Name
            )
    if models.Parties.objects.filter(
        LedgerID=instance_serialized.get("LedgerID"), CompanyID=CompanyID
    ).exists():
        party_instance = models.Parties.objects.get(
            LedgerID=instance_serialized.get("LedgerID"), CompanyID=CompanyID
        )
        PartyName = party_instance.DisplayName or ""
        Attention = party_instance.Attention or ""
        BuildingNo = party_instance.Address1 or ""
        StreetName = party_instance.Address2 or ""
        City = party_instance.City or ""
        District = party_instance.District or ""
        CountryName = ""
        if party_instance.Country:
            CountryName = (
                models.Country.objects.get(id=party_instance.Country).Country_Name or ""
            )
        StateName = ""
        if party_instance.State:
            StateName = models.State.objects.get(id=party_instance.State).Name or ""
        PostalCode = party_instance.PostalCode or ""
        Phone_Shipping = party_instance.Phone_Shipping or ""
        VATNumber = party_instance.VATNumber or ""
        if not invoice_type == "purchase_order" and not invoice_type == "purchase_invoice" and not invoice_type == "purchase_return" and not invoice_type == "receipt_voucher" and not invoice_type == "payment_voucher" and not invoice_type == "expense" and instance.BillingAddress:
            Attention = instance.BillingAddress.Attention
            BuildingNo = instance.BillingAddress.Address1
            StreetName = instance.BillingAddress.Address2
            City = instance.BillingAddress.City
            District = instance.BillingAddress.District
            PostalCode = instance.BillingAddress.PostalCode
            if instance.BillingAddress.state:
                StateName = instance.BillingAddress.state.Name
            CountryName = instance.BillingAddress.country.Country_Name
        address = f"""{Attention} {'<br/>' if Attention else ''}
            {BuildingNo} {'<br/>' if BuildingNo else ''}
            {StreetName} {'<br/>' if StreetName else ''}
            {City} {',' if City else ''} {District} {'<br/>' if City or District else ''}
            {StateName}{',' if StateName else ''} {CountryName}{',' if StateName and CountryName else ''} {PostalCode}"""
        print(address)
        print("eeeeeeeeeeeeeeeeeeeeeeeeiii")

    GST = models.GeneralSettings.objects.get(
        CompanyID=CompanyID, SettingsType="GST", BranchID=1
    ).SettingsValue
    VAT = models.GeneralSettings.objects.get(
        CompanyID=CompanyID, SettingsType="VAT", BranchID=1
    ).SettingsValue
    if models.GeneralSettings.objects.filter(
        CompanyID=CompanyID, SettingsType="GST", BranchID=BranchID
    ).exists():
        GST = models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="GST", BranchID=BranchID
        ).SettingsValue
    if GST == "true" or GST == "True":
        GST = True
    else:
        GST = False
    if VAT == "true" or  VAT == "True":
        VAT = True
    else:
        VAT = False
    company_instance = models.CompanySettings.objects.get(id=CompanyID)
    serialized = CompanySettingsPrintRestSerializer(
        company_instance, many=False, context={"request": request}
    )
    
    print(company_instance.CompanyLogo)
    data = {
        "request": request,
        "company_name": company_name,
        "country": country_instance,
        "invoice_type": invoice_type,
        "type": "pdf",
        "company": serialized.data,
        "amount_in_words": num2words(
            converted_float(grand_total), to="cardinal", lang="en_IN"
        ),
        "amount_in_words_arabic": num2words(
            converted_float(grand_total), to="cardinal", lang="ar"
        ),
        "details": details,
        "data": instance_serialized,
        "PriceRounding": PriceRounding,
        "settings": print_settings_instance,
        "qr_code": qr_code,
        "invoice_time": invoice_time,
        "print_template": print_template,
        "GST": GST,
        "VAT": VAT,
        "vat_perc": vat_perc,
        "total_qty": total_qty,
        "address": address,
        "IsFqty": IsFqty
    }
    print(print_settings_instance.template,"print_settings_instance.template8646")
    if invoice_type == "expense":
        response = render(request, "expense_print.html", data)
    elif invoice_type == "journal":
        response = render(request, "journal_print.html", data)
    elif invoice_type == "payment_voucher" or invoice_type == "receipt_voucher":
        response = render(request, "payment_print.html", data)
    elif invoice_type == "stock_transfer":
        response = render(request, "stock_transfer.html", data)
    elif invoice_type == "stock_order":
        response = render(request, "stock_order.html", data)
    elif invoice_type == "work_order":
        response = render(request, "work_order.html", data)
    else:
        print(invoice_type,"====================================8660")
        print(print_settings_instance.template)
        if print_settings_instance.template == "template11":
            response = render(request, "print_template_nine.html", data)
        elif print_settings_instance.template == "template10":
            response = render(request, "print_template_eight.html", data)
        elif print_settings_instance.template == "template9":
            response = render(request, "print_template_seven.html", data)
        elif print_settings_instance.template == "template8":
            response = render(request, "print_template_six.html", data)
        elif print_settings_instance.template == "template7":
            response = render(request, "print_template_five.html", data)
        elif print_settings_instance.template == "template6":
            response = render(request, "thermalTwo.html", data)
        elif print_settings_instance.template == "template5":
            response = render(request, "thermalOne.html", data)
        elif print_settings_instance.template == "template4":
            response = render(request, "print_template_four.html", data)
        elif print_settings_instance.template == "template3":
            response = render(request, "print_template_three.html", data)
        elif print_settings_instance.template == "template2":
            response = render(request, "print_template_two.html", data)
        else:
            response = render(request, "print.html", data)

    response["X-Frame-Options"] = "allow-all"
    response["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response["Content-Security-Policy"] = "http://localhost:3000"

    return response


@api_view(["GET"])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def print_thermal(request):
    response = render(request, "thermalTwo.html", {})
    response["X-Frame-Options"] = "allow-all"
    response["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response["Content-Security-Policy"] = "http://localhost:3000"

    return response


@api_view(["GET"])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def print_template(request):
    CompanyID = request.GET.get("CompanyID")
    invoice_type = request.GET.get("invoice_type")
    BranchID = request.GET.get("BranchID")
    company_instance = models.CompanySettings.objects.get(id=CompanyID)
    branch_instance = models.Branch.objects.get(
        BranchID=BranchID, CompanyID=company_instance
    )
    company_name = branch_instance.DisplayName
    serialized = CompanySettingsPrintRestSerializer(
        company_instance, many=False, context={"request": request}
    )
    country_instance = models.Country.objects.get(id=company_instance.Country.id)
    print(invoice_type,"===============================>>")
    try:
        print_settings_instance = models.PrintSettingsNew.objects.filter(
            CompanyID=company_instance, InvoiceType=invoice_type
        ).first()
    except:
        (
            print_settings_instance,
            created,
        ) = models.PrintSettingsNew.objects.get_or_create(
            CompanyID=company_instance, InvoiceType=invoice_type
        )

    print(print_settings_instance.template, "print_settings_instance.template8749")
    # GST = models.GeneralSettings.objects.get(
    #     CompanyID=CompanyID, SettingsType="GST", BranchID=BranchID
    # ).SettingsValue
    # print(GST)
    # if GST == "true" or GST == "True":
    #     GST = True
    # else:
    #     GST = False
    # print(GST)
    
    GST = get_GeneralSettings(CompanyID, BranchID, "GST")
    VAT = get_GeneralSettings(CompanyID, BranchID, "VAT")

    data = {
        "company_name": company_name,
        "country": country_instance,
        "path": request.path,
        "company": serialized.data,
        "invoice_type": invoice_type,
        "settings": print_settings_instance,
        "GST": GST,
        "VAT": VAT,
    }
    if invoice_type == "expense":
        response = render(request, "expense_print.html", data)
    elif invoice_type == "journal":
        response = render(request, "journal_print.html", data)
    elif invoice_type == "payment_voucher" or invoice_type == "receipt_voucher":
        response = render(request, "payment_print.html", data)
    elif invoice_type == "stock_transfer":
        response = render(request, "stock_transfer.html", data)
    elif invoice_type == "stock_order":
        response = render(request, "stock_order.html", data)
    elif invoice_type == "work_order":
        response = render(request, "work_order.html", data)
    else:
        if print_settings_instance.template == "template11":
            response = render(request, "print_template_nine.html", data)
        elif print_settings_instance.template == "template10":
            response = render(request, "print_template_eight.html", data)
        elif print_settings_instance.template == "template9":
            response = render(request, "print_template_seven.html", data)
        elif print_settings_instance.template == "template8":
            response = render(request, "print_template_six.html", data)
        elif print_settings_instance.template == "template7":
            response = render(request, "print_template_five.html", data)
        elif print_settings_instance.template == "template6":
            response = render(request, "thermalTwo.html", data)
        elif print_settings_instance.template == "template5":
            response = render(request, "thermalOne.html", data)
        elif print_settings_instance.template == "template4":
            response = render(request, "print_template_four.html", data)
        elif print_settings_instance.template == "template3":
            response = render(request, "print_template_three.html", data)
        elif print_settings_instance.template == "template2":
            response = render(request, "print_template_two.html", data)
        else:
            response = render(request, "print.html", data)
    response["X-Frame-Options"] = "allow-all"

    return response


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def print_settings(request):
    today = datetime.datetime.now()
    serialized = serializers.PrintSettingsCreateSerializer(data=request.data)
    if serialized.is_valid():
        data = request.data
        data = request.data
        CompanyID = data["CompanyID"]
        CompanyID = get_company(CompanyID)
        invoice_type = data["invoice_type"]
        HeaderOne = data["HeaderOne"]
        HeaderTwo = data["HeaderTwo"]
        HeaderThree = data["HeaderThree"]
        HeaderFour = data["HeaderFour"]
        CreatedUserID = data["CreatedUserID"]
        BranchID = data["BranchID"]
        template = serialized.data["template"]
        IsSlNo = serialized.data["IsSlNo"]
        IsQuantity = serialized.data["IsQuantity"]
        IsFreeQuantity = serialized.data["IsFreeQuantity"]
        IsHSNCode = serialized.data["IsHSNCode"]
        TransactionName = serialized.data["TransactionName"]
        BankName = serialized.data["BankName"]
        AccountNumber = serialized.data["AccountNumber"]
        IBANCode = serialized.data["IBANCode"]
        SwiftCode = serialized.data["SwiftCode"]
        IsDigitalSign = serialized.data["IsDigitalSign"]
        IsUploadSeal = serialized.data["IsUploadSeal"]
        
        try:
            DigitalSignFile = request.FILES["DigitalSignFile"]
        except:
            DigitalSignFile = None    

        try:
            SealFile = request.FILES["SealFile"]
        except:
            SealFile = None  

        IsProductName = serialized.data["IsProductName"]
        IsDescription = serialized.data["IsDescription"]
        IsProductDescription = serialized.data["IsProductDescription"]
        IsSerialNo = serialized.data["IsSerialNo"]
        IsItemCode = serialized.data["IsItemCode"]
        IsProductCode = serialized.data["IsProductCode"]
        IsRate = serialized.data["IsRate"]
        IsUnit = serialized.data["IsUnit"]
        IsTax = serialized.data["IsTax"]
        IsDiscount = serialized.data["IsDiscount"]
        IsNetTotal = serialized.data["IsNetTotal"]
        IsSalesMan = serialized.data["IsSalesMan"]
        IsSalesManPhone = serialized.data["IsSalesManPhone"]
        IsQrCode = serialized.data["IsQrCode"]
        IsLUTNumber = serialized.data["IsLUTNumber"]
        IsTenderCash = serialized.data["IsTenderCash"]
        try:
            IsReceiverSignature = serialized.data["IsReceiverSignature"]
        except:
            IsReceiverSignature = True

        try:
            IsAuthorizedSinature = serialized.data["IsAuthorizedSinature"]
        except:
            IsAuthorizedSinature = True
        
        try:
            IsPaymentStatus = serialized.data["IsPaymentStatus"]
        except:
            IsPaymentStatus = False
            
        try:
            IsPlaceOfSupply = serialized.data["IsPlaceOfSupply"]
        except:
            IsPlaceOfSupply = False
        
        try:
            IsRoute = serialized.data["IsRoute"]
        except:
            IsRoute = False
            
        try:
            IsCustomerBalance = serialized.data["IsCustomerBalance"]
        except:
            IsCustomerBalance = False

        IsLogo = serialized.data["IsLogo"]

        try:
            IsNarration = serialized.data["IsNarration"]
        except:
            IsNarration = False

        try:
            IsNote = serialized.data["IsNote"]
        except:
            IsNote = False

        try:
            IsGrossAmount = serialized.data["IsGrossAmount"]
        except:
            IsGrossAmount = True

        # payment
        IsLedgerName = serialized.data["IsLedgerName"]
        IsRefNo = serialized.data["IsRefNo"]
        IsDiscount = serialized.data["IsDiscount"]
        # payment ends
        TermsAndConditions = serialized.data["TermsAndConditions"]
        SignatureName = serialized.data["SignatureName"]


        if HeaderOne:
            if "<p>" in HeaderOne:
                HeaderOne = HeaderOne.replace("<p>", "<p><bdo>")
                HeaderOne = HeaderOne.replace("</p>", "<bdo></p>")
            if "<span>" in HeaderOne:
                HeaderOne = HeaderOne.replace("<span>", "<span><bdo>")
                HeaderOne = HeaderOne.replace("</span>", "<bdo></span>")

        if HeaderTwo:
            if "<p>" in HeaderTwo:
                HeaderTwo = HeaderTwo.replace("<p>", "<p><bdo>")
                HeaderTwo = HeaderTwo.replace("</p>", "<bdo></p>")

            if "<span>" in HeaderTwo:
                HeaderTwo = HeaderTwo.replace("<span>", "<span><bdo>")
                HeaderTwo = HeaderTwo.replace("</span>", "<bdo></span>")

        if HeaderThree:
            if "<p>" in HeaderThree:
                HeaderThree = HeaderThree.replace("<p>", "<p><bdo>")
                HeaderThree = HeaderThree.replace("</p>", "<bdo></p>")

            if "<span>" in HeaderThree:
                HeaderThree = HeaderThree.replace("<span>", "<span><bdo>")
                HeaderThree = HeaderThree.replace("</span>", "<bdo></span>")

        if HeaderFour:
            if "<p>" in HeaderFour:
                HeaderFour = HeaderFour.replace("<p>", "<p><bdo>")
                HeaderFour = HeaderFour.replace("</p>", "<bdo></p>")

            if "<span>" in HeaderFour:
                HeaderFour = HeaderFour.replace("<span>", "<span><bdo>")
                HeaderFour = HeaderFour.replace("</span>", "<bdo></span>")

        # batch
        try:
            IsBatchCode = serialized.data["IsBatchCode"]
        except:
            IsBatchCode = False
        try:
            IsExpiryDate = serialized.data["IsExpiryDate"]
        except:
            IsExpiryDate = False
        try:
            IsManufacturingDate = serialized.data["IsManufacturingDate"]
        except:
            IsManufacturingDate = False
        try:
            IsAmountInWordsArabic = serialized.data["IsAmountInWordsArabic"]
        except:
            IsAmountInWordsArabic = False

        try:
            IsTaxPerc = serialized.data["IsTaxPerc"]
        except:
            IsTaxPerc = False

        # batch ends

        Notes = serialized.data["Notes"]
        Action = "A"
        # get or create
        print(
            IsDigitalSign,
            IsUploadSeal,
            DigitalSignFile,
            SealFile,
          )
        # try:
        print_settings_instance = models.PrintSettingsNew.objects.update_or_create(
            InvoiceType=invoice_type,
            CompanyID=CompanyID,
            defaults={
                "CreatedUserID": CreatedUserID,
                "UpdatedUserID": CreatedUserID,
                "BranchID": BranchID,
                "template": template,
                "TransactionName": TransactionName,
                "BankName":BankName,
                "AccountNumber":AccountNumber,
                "IBANCode":IBANCode,
                "SwiftCode":SwiftCode,
                "IsDigitalSign":IsDigitalSign,
                "IsUploadSeal":IsUploadSeal,
                "DigitalSignFile":DigitalSignFile,
                "SealFile":SealFile,
                "SignatureName":SignatureName,
                "IsSlNo": IsSlNo,
                "IsQuantity": IsQuantity,
                "IsPaymentStatus": IsPaymentStatus,
                "IsPlaceOfSupply": IsPlaceOfSupply,
                "IsRoute": IsRoute,
                "IsCustomerBalance": IsCustomerBalance,
                "IsFreeQuantity": IsFreeQuantity,
                "IsHSNCode": IsHSNCode,
                "IsProductName": IsProductName,
                "IsProductDescription": IsProductDescription,
                "IsDescription": IsDescription,
                "IsSerialNo": IsSerialNo,
                "IsItemCode": IsItemCode,
                "IsProductCode": IsProductCode,
                "IsRate": IsRate,
                "IsUnit": IsUnit,
                "IsTax": IsTax,
                "IsDiscount": IsDiscount,
                "IsNetTotal": IsNetTotal,
                "IsSalesMan":IsSalesMan,
                "IsSalesManPhone":IsSalesManPhone,
                "IsQrCode":IsQrCode,
                "IsLUTNumber":IsLUTNumber,
                "IsTenderCash": IsTenderCash,
                "IsReceiverSignature": IsReceiverSignature,
                "IsAuthorizedSinature": IsAuthorizedSinature,
                "IsLogo": IsLogo,
                "IsNarration": IsNarration,
                "IsNote": IsNote,
                "IsGrossAmount": IsGrossAmount,
                # payment
                "IsLedgerName": IsLedgerName,
                "IsRefNo": IsRefNo,
                "IsDiscount": IsDiscount,
                # payment ends
                "TermsAndConditions": TermsAndConditions,
                "Notes": Notes,
                "Action": Action,
                "UpdatedDate": today,
                # batch
                "IsBatchCode": IsBatchCode,
                "IsExpiryDate": IsExpiryDate,
                "IsManufacturingDate": IsManufacturingDate,
                "IsAmountInWordsArabic": IsAmountInWordsArabic,
                "IsTaxPerc": IsTaxPerc,
                # batch ends
                # richtext
                "HeaderOne": HeaderOne,
                "HeaderTwo": HeaderTwo,
                "HeaderThree": HeaderThree,
                "HeaderFour": HeaderFour,
                # richtextends
            },
        )
        # except Exception as e:
        #     print("errrrrrrrrrrrrrrrrrrrrrrrr")
        #     print(e)
        #     print_settings_instance = models.PrintSettingsNew.objects.filter(
        #         InvoiceType=invoice_type, CompanyID=CompanyID
        #     ).first()
        response_data = {"StatusCode": 6000, "data": serialized.data}
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors),
        }
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def print_settings_list(request):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    invoice_type = data["invoice_type"]
    CreatedUserID = data["CreatedUserID"]
    BranchID = data["BranchID"]

    if models.PrintSettingsNew.objects.filter(
        CompanyID=CompanyID, InvoiceType=invoice_type
    ).exists():
        print_settings_instance = models.PrintSettingsNew.objects.filter(
            CompanyID=CompanyID, InvoiceType=invoice_type
        ).first()
    else:
        (
            print_settings_instance,
            created,
        ) = models.PrintSettingsNew.objects.get_or_create(
            CompanyID=CompanyID, InvoiceType=invoice_type
        )


    serialized = serializers.PrintSettingsSerializer(
        print_settings_instance, many=False
    )
    response_data = {"StatusCode": 6000, "data": serialized.data}
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def print_report_paper(request):
    lang = request.GET.get("lang")
    if lang:
        activate(lang)
    writer = PdfFileWriter()
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

    WareHouseID = request.GET.get("WareHouseID")
    RouteID = request.GET.get("RouteID")
    CustomerID = request.GET.get("CustomerID")
    ProductFilter = request.GET.get("ProductFilter")
    StockFilter = request.GET.get("StockFilter")
    ProductID = request.GET.get("ProductID")
    CategoryID = request.GET.get("CategoryID")
    GroupID = request.GET.get("GroupID")
    Barcode = request.GET.get("Barcode")
    BrandID = request.GET.get("BrandID")
    is_manualOpening = request.GET.get("is_manualOpening")
    key = request.GET.get("key")
    ManualOpeningStock = request.GET.get("ManualOpeningStock")
    ManualClosingStock = request.GET.get("ManualClosingStock")

    CashLedgersList = request.GET.get("CashLedgers")
    columns = request.GET.get("columns")
    columns_heads = []
    if columns:
        columns_heads = json.loads(columns)

    LedgerList = [x for x in LedgerList if x]
    for x in LedgerList:
        print(str(x).split(","))
        test_list = str(x).split(",")
        for i in range(0, len(test_list)):
            test_list[i] = int(test_list[i])
        LedgerList = test_list

    LedgerList = [x for x in LedgerList if x]

    # print("LedgerList", invoice_type)
    # for x in CashLedgersList:
    #     print(str(x).split(','))
    #     test_list = str(x).split(',')
    #     for i in range(0, len(test_list)):
    #         test_list[i] = int(test_list[i])
    #     CashLedgersList = test_list

    CashLedgers = LedgerList
    try:
        value = int(request.GET.get("value"))
    except:
        value = 0

    try:
        PriceRounding = int(request.GET.get("PriceRounding"))
    except:
        PriceRounding = 2

    company_instance = models.CompanySettings.objects.get(id=CompanyID)
    country_instance = models.Country.objects.get(id=company_instance.Country.id)
    print_settings_instance, created = models.PrintSettingsNew.objects.get_or_create(
        CompanyID=company_instance, InvoiceType=invoice_type
    )

    data = {}
    details = {}
    total = {}
    page_type = ""
    report_title = ""

    # Sales Report
    if invoice_type == "sales":
        page_type = "master"
        data = sales_excel_data(
            CompanyID, BranchID, FromDate, ToDate, PriceRounding, UserID, EmployeeID
        )
        try:
            details = data["sales_data"]
            total = data["sales_total"]
        except:
            details = {}
            total = {}
        report_title = str(_("SALES REPORT"))
        print("@@@@@@@@@@@@@@@@@#################", details)

    # Sales Return Report
    elif invoice_type == "sales_return":
        page_type = "return"
        data = salesReturn_excel_data(
            CompanyID, BranchID, FromDate, ToDate, PriceRounding, UserID, EmployeeID
        )
        try:
            details = data["salesReturn_data"]
            total = data["salesReturn_total"]
        except:
            details = {}
            total = {}
        report_title = str(_("RETURN REPORT"))

    # Purchase Report
    elif invoice_type == "purchases":
        page_type = "master"
        data = purchase_excel_data(
            CompanyID, BranchID, FromDate, ToDate, PriceRounding, ReffNo
        )
        print(data)
        try:
            details = data["purchase_data"]
            total = data["purchase_total"]
        except:
            details = {}
            total = {}
        report_title = str(_("PURCHASE REPORT"))

    # Purchase Return Report
    elif invoice_type == "purchases_return":
        page_type = "return"
        data = purchaseReturn_excel_data(
            CompanyID, BranchID, FromDate, ToDate, PriceRounding, ReffNo
        )
        try:
            details = data["purchaseReturn_data"]
            total = data["purchasesReturn_total"]
        except:
            details = {}
            total = {}
        report_title = str(_("RETURN REPORT"))

    # Tax Summary Report
    elif invoice_type == "tax_summary_vat" or invoice_type == "tax_summary_gst":
        if invoice_type == "tax_summary_vat":
            Type = "VAT"
        else:
            Type = "GST"

        details = taxSummary_excel_data(
            CompanyID, BranchID, FromDate, ToDate, Type, PriceRounding
        )
        total = {}
        report_title = str(_("TAX SUMMARY"))

    # Ledger Report
    elif (
        invoice_type == "all_ledger"
        or invoice_type == "ledger_wise"
        or invoice_type == "group_wise"
    ):
        if invoice_type == "all_ledger":
            ID = 0
        elif invoice_type == "ledger_wise":
            ID = 1
        elif invoice_type == "group_wise":
            ID = 2

        data = ledgerReport_excel_data(
            CompanyID,
            UserID,
            PriceRounding,
            BranchID,
            FromDate,
            ToDate,
            ID,
            value,
            ManualOpeningBalance,
        )
        try:
            details = data["data"]
        except:
            details = {}
        try:
            total = data["total"]
        except:
            total = {}
        print(total)
        report_title = str(_("LEDGER REPORT"))

    # Payment Report
    elif invoice_type == "Payment":
        data = paymentReport_excel_data(
            CompanyID,
            BranchID,
            PriceRounding,
            VoucherType,
            LedgerList,
            FromDate,
            ToDate,
        )
        try:
            details = data["data"]
        except:
            details = {}
        try:
            total = data["total"]
        except:
            total = {}

        report_title = str(_("PAYMENT REPORT"))

    # Receipt Report
    elif invoice_type == "Receipt":
        data = receiptReport_excel_data(
            CompanyID,
            BranchID,
            PriceRounding,
            VoucherType,
            LedgerList,
            FromDate,
            ToDate,
        )
        try:
            details = data["data"]
        except:
            details = {}
        try:
            total = data["total"]
        except:
            total = {}

        print(total, "OOOI")
        report_title = str(_("RECEIPT REPORT"))

    # Out Standing Report
    elif invoice_type == "OutStanding":
        data = outStandingReport_excel_data(
            CompanyID, BranchID, PriceRounding, RouteLedgers, ToDate, VoucherType
        )
        try:
            details = data["new_data"]
        except:
            details = {}
        try:
            total = data["total"]
        except:
            total = {}
        report_title = str(_("OUTSTANDING REPORT"))

    # Trail Balance Report
    elif invoice_type == "trail_balance":
        data = trialBalance_excel_data(
            CompanyID, UserID, PriceRounding, BranchID, ToDate, request
        )
        try:
            details = data["new_data"]
        except:
            details = {}
        try:
            total = data["total"]
        except:
            total = {}
        report_title = str(_("TRAIL BALANCE"))
    # Bill Wise Report
    elif invoice_type == "bill_wise":
        data = billWise_report_data(
            CompanyID,
            PriceRounding,
            WareHouseID,
            RouteID,
            UserID,
            CustomerID,
            BranchID,
            FromDate,
            ToDate,
        )
        try:
            details = data["new_data"]
        except:
            details = {}
        try:
            total = data["total"]
        except:
            total = {}
        report_title = str(_("BILL WISE REPORT"))
    # Stock Report
    elif invoice_type == "stock_report":
        data = stock_report_data(
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
        try:
            details = data["data"]
        except:
            details = {}
        try:
            total = data["total"]
        except:
            total = {}
        report_title = str(_("STOCK REPORT"))
    # Cash Book Report
    elif invoice_type == "cash_book":
        data = cash_book_report_data(
            CompanyID,
            BranchID,
            FromDate,
            ToDate,
            PriceRounding,
            ManualOpeningBalance,
            is_manualOpening,
            CashLedgers,
        )

        try:
            details = data["new_data"]
        except:
            details = {}
        try:
            total = data["total"]
        except:
            total = {}
        report_title = str(_("CASH BOOK REPORT"))
    # Bank Book Report
    elif invoice_type == "bank_book":
        data = bank_book_report_data(
            CompanyID,
            BranchID,
            FromDate,
            ToDate,
            PriceRounding,
            ManualOpeningBalance,
            is_manualOpening,
            CashLedgers,
        )

        try:
            details = data["new_data"]
        except:
            details = {}
        try:
            total = data["total"]
        except:
            total = {}
        report_title = str(_("BANK BOOK REPORT"))

    # Profit and Loss Report
    elif invoice_type == "profit_and_loss":
        details = profitAndLoss_excel_data(
            int(key),
            CompanyID,
            UserID,
            PriceRounding,
            BranchID,
            ToDate,
            FromDate,
            request,
            int(ManualOpeningStock),
            int(ManualClosingStock),
        )
        if key == "1":
            page_type = "consolidate"
        elif key == "2":
            page_type = "detailed"

        print(details, "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII")
        report_title = str(_("PROFIT AND LOSS REPORT"))
    # Balance Sheet Report
    elif invoice_type == "balance_sheet":
        data = balanceSheet_excel_data(
            CompanyID, UserID, PriceRounding, BranchID, ToDate, FromDate, request
        )
        if key == "1":
            details = data["new_data"][0]
            page_type = "consolidate"
        elif key == "2":
            details = data["new_data"][1]
            page_type = "detailed"

        print(details, "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII")
        report_title = str(_("BALANCE SHEET"))

    company_instance = models.CompanySettings.objects.get(id=CompanyID)
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
        "total": total,
        "PriceRounding": int(PriceRounding),
        "FromDate": FromDate,
        "ToDate": ToDate,
        "report_title": report_title,
        "print_template": True,
        "columns_heads": columns_heads,
    }
    if (
        invoice_type == "sales"
        or invoice_type == "sales_return"
        or invoice_type == "purchases"
        or invoice_type == "purchases_return"
    ):
        print("HIIIUOOOOOOO")
        # template = get_template('reports/invoice_print.html')

        response = render(request, "reports/invoice_print.html", data)

    elif invoice_type == "tax_summary_vat" or invoice_type == "tax_summary_gst":
        response = render(request, "reports/tax_summary_print.html", data)

    elif (
        invoice_type == "all_ledger"
        or invoice_type == "ledger_wise"
        or invoice_type == "group_wise"
    ):
        response = render(request, "reports/ledger_report_print.html", data)

    elif invoice_type == "Payment":
        response = render(request, "reports/payment_report_print.html", data)

    elif invoice_type == "Receipt":
        response = render(request, "reports/receipt_report_print.html", data)

    elif invoice_type == "OutStanding":
        response = render(request, "reports/out_standing_print.html", data)

    elif invoice_type == "trail_balance":
        response = render(request, "reports/trail_balance_print.html", data)

    elif invoice_type == "bill_wise":
        response = render(request, "reports/bill_wise_print.html", data)

    elif invoice_type == "stock_report":
        response = render(request, "reports/stock_report_print.html", data)

    elif invoice_type == "cash_book":
        response = render(request, "reports/cash_book_report_print.html", data)

    elif invoice_type == "bank_book":
        response = render(request, "reports/cash_book_report_print.html", data)

    elif invoice_type == "profit_and_loss":
        response = render(request, "reports/profit_and_loss_print.html", data)

    elif invoice_type == "balance_sheet":
        response = render(request, "reports/balance_sheet_print.html", data)

    html = template.render(data)
    options = {
        "page-size": "Letter",
        "encoding": "UTF-8",
        "margin-top": "0.5in",
        "margin-right": "0.5in",
        "margin-bottom": "0.5in",
        "margin-left": "0.5in",
    }

    # pdf = pdfkit.from_string(html, False, options)
    # response = HttpResponse(pdf, content_type='application/pdf')
    # response['Content-Disposition'] = 'attachment; filename="Sales Report.pdf"'

    pdf = pdfkit.from_string(html, False, options)
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = "inline"

    # response['Content-Disposition'] = 'inline'

    # response['X-Frame-Options'] = "allow-all"
    # response['Access-Control-Allow-Origin'] = "http://localhost:3000"
    # response['Content-Security-Policy'] = "http://localhost:3000"
    return response


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def user_role_settings_update(request):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    UserType = data["UserType"]
    UpdatedUserID = data["CreatedUserID"]
    BranchID = data["BranchID"]
    permission_datas = data["permission_datas"]
    action_type = data["action_type"]

    # parent = serialized.data['parent']
    # name = serialized.data['name']
    # view = serialized.data['view']
    # save = serialized.data['save']
    # edit = serialized.data['edit']
    # delete = serialized.data['delete']
    # print_permission = serialized.data['print_permission']
    # get or create

    for i in permission_datas:
        UserType = None
        if models.UserType.objects.filter(id=i.UserType).exists():
            UserType = models.UserType.objects.get(id=i.UserType)
        userRole_settings_instance = (
            models.UserRoleSettingsModel.objects.update_or_create(
                parent=i.parent,
                name=i.name,
                UserType=UserType,
                CompanyID=CompanyID,
                defaults={
                    "CompanyID": CompanyID,
                    "UserType": UserType,
                    "BranchID": BranchID,
                    "parent": i.parent,
                    "name": i.name,
                    "view": i.view,
                    "save": i.save,
                    "edit": i.edit,
                    "delete": i.delete,
                    "print_permission": i.print_permission,
                    "UpdatedDate": today,
                    "UpdatedUserID": UpdatedUserID,
                },
            )
        )
    response_data = {"StatusCode": 6000, "data": permission_datas}
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def user_role_settings(request):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    userType = data["UserType"]
    UpdatedUserID = data["CreatedUserID"]
    BranchID = data["BranchID"]
    permission_datas = data["permission_datas"]
    action_type = data["action_type"]
    
    try:
        PreDate = data["PreDate"]
    except:
        PreDate = 0
    try:
        PostDate = data["PostDate"]
    except:
        PostDate = 0

    user_type = None
    if type(userType) == int:
        if models.UserType.objects.filter(ID=userType, CompanyID=CompanyID).exists():
            user_type = models.UserType.objects.get(ID=userType, CompanyID=CompanyID)
    else:
        if models.UserType.objects.filter(id=userType).exists():
            user_type = models.UserType.objects.get(id=userType)

    if action_type == "List":
        all_names = []
        for i in permission_datas:
            if user_type is not None and user_type.ID == 1:
                if not models.UserRoleSettingsModel.objects.filter(
                    CompanyID=CompanyID,
                    UserType=user_type,
                    BranchID=BranchID,
                    name=i["name"],
                ).exists():
                    models.UserRoleSettingsModel.objects.create(
                        CompanyID=CompanyID,
                        UserType=user_type,
                        BranchID=BranchID,
                        name=i["name"],
                        parent=i["parent"],
                        view_permission=True,
                        save_permission=True,
                        edit_permission=True,
                        delete_permission=True,
                        print_permission=True,
                        UpdatedDate=today,
                        UpdatedUserID=UpdatedUserID,
                        PreDate=PreDate,
                        PostDate=PostDate,
                    )
                # models.UserRoleSettingsModel.objects.get_or_create(
                #     CompanyID=CompanyID,
                #     UserType=user_type,
                #     BranchID=BranchID,
                #     name=i["name"],
                #     defaults={
                #         "parent": i["parent"],
                #         "view_permission": True,
                #         "save_permission": True,
                #         "edit_permission": True,
                #         "delete_permission": True,
                #         "print_permission": True,
                #         "UpdatedDate": today,
                #         "UpdatedUserID": UpdatedUserID,
                #     },
                # )
            else:
                if not models.UserRoleSettingsModel.objects.filter(
                    CompanyID=CompanyID,
                    UserType=user_type,
                    BranchID=BranchID,
                    name=i["name"],
                ).exists():
                    models.UserRoleSettingsModel.objects.create(
                        CompanyID=CompanyID,
                        UserType=user_type,
                        BranchID=BranchID,
                        name=i["name"],
                        parent=i["parent"],
                        view_permission=i["view_permission"],
                        save_permission=i["save_permission"],
                        edit_permission=i["edit_permission"],
                        delete_permission=i["delete_permission"],
                        print_permission=i["print_permission"],
                        block_date=i["block_date"],
                        UpdatedDate=today,
                        UpdatedUserID=UpdatedUserID,
                        PreDate=PreDate,
                        PostDate=PostDate,
                    )

                # models.UserRoleSettingsModel.objects.get_or_create(
                #     CompanyID=CompanyID,
                #     UserType=user_type,
                #     BranchID=BranchID,
                #     name=i["name"],
                #     defaults={
                #         "parent": i["parent"],
                #         "view_permission": i["view_permission"],
                #         "save_permission": i["save_permission"],
                #         "edit_permission": i["edit_permission"],
                #         "delete_permission": i["delete_permission"],
                #         "print_permission": i["print_permission"],
                #         "UpdatedDate": today,
                #         "UpdatedUserID": UpdatedUserID,
                #     },
                # )
            all_names.append(i["name"])

        if (
            models.UserRoleSettingsModel.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID
            )
            .exclude(name__in=all_names)
            .exists()
        ):
            models.UserRoleSettingsModel.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID
            ).exclude(name__in=all_names).delete()

        instances = models.UserRoleSettingsModel.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, UserType=user_type
        )
        
        serialized = serializers.UserRoleSettingsSerializer(instances, many=True)

        response_data = {"StatusCode": 6000, "data": serialized.data}
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        for i in permission_datas:
            # user_type = None
            # if models.UserType.objects.filter(id=userType).exists():
            #     user_type = models.UserType.objects.get(id=userType)
            if not models.UserRoleSettingsModel.objects.filter(
                CompanyID=CompanyID,
                UserType=user_type,
                BranchID=BranchID,
                name=i["name"],
                parent=i["parent"],
            ).exists():
                models.UserRoleSettingsModel.objects.create(
                    CompanyID=CompanyID,
                    UserType=user_type,
                    BranchID=BranchID,
                    name=i["name"],
                    parent=i["parent"],
                    view_permission=i["view_permission"],
                    save_permission=i["save_permission"],
                    edit_permission=i["edit_permission"],
                    delete_permission=i["delete_permission"],
                    print_permission=i["print_permission"],
                    block_date=i["block_date"],
                    UpdatedDate=today,
                    UpdatedUserID=UpdatedUserID,
                    PreDate=PreDate,
                    PostDate=PostDate,
                )
            else:
                user_role_ins = models.UserRoleSettingsModel.objects.filter(
                    CompanyID=CompanyID,
                    UserType=user_type,
                    BranchID=BranchID,
                    name=i["name"],
                    parent=i["parent"],
                ).first()
                user_role_ins.view_permission = i["view_permission"]
                user_role_ins.save_permission = i["save_permission"]
                user_role_ins.edit_permission = i["edit_permission"]
                user_role_ins.delete_permission = i["delete_permission"]
                user_role_ins.print_permission = i["print_permission"]
                try:
                    block_date = i["block_date"]
                except:
                    block_date = False
                user_role_ins.block_date = block_date
                user_role_ins.UpdatedDate = today
                user_role_ins.UpdatedUserID = UpdatedUserID
                user_role_ins.PreDate = PreDate
                user_role_ins.PostDate = PostDate
                user_role_ins.save()

            # userRole_settings_instance = (
            #     models.UserRoleSettingsModel.objects.update_or_create(
            #         parent=i["parent"],
            #         name=i["name"],
            #         UserType=user_type,
            #         CompanyID=CompanyID,
            #         defaults={
            #             "CompanyID": CompanyID,
            #             "UserType": user_type,
            #             "BranchID": BranchID,
            #             "parent": i["parent"],
            #             "name": i["name"],
            #             "view_permission": i["view_permission"],
            #             "save_permission": i["save_permission"],
            #             "edit_permission": i["edit_permission"],
            #             "delete_permission": i["delete_permission"],
            #             "print_permission": i["print_permission"],
            #             "UpdatedDate": today,
            #             "UpdatedUserID": UpdatedUserID,
            #         },
            #     )
            # )

        response_data = {
            "StatusCode": 6002,
            "message": "User Role Settings Updated Successfully",
        }
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def convert_to_image(request):
    width = request.GET.get("width")
    if not width:
        width = 597

    data = {
        "companyName": "hello world",
        "VoucherNumber": "S12",
        "simpleDate": "15/12/2021",
        "custName": "Rabih",
        "Phone": "9400000000",
        "grossTotalSimp": "35.8",
        "discountedAmountSimp": "5",
        "totalTaxSimp": "1",
        "totalAmountDis": "2",
    }
    company_details = convert_to_base64(data, "company_details", width, 300)

    invoice_details = convert_to_base64(data, "invoice_details", width, 380)

    table_heading = convert_to_base64(data, "table_heading", width, 60)

    table_details = convert_to_base64(data, "table_details", width, 120)

    amount = convert_to_base64(data, "amount", width, 300)

    # img = open(image[0], 'rb')

    # response = FileResponse(img)
    status_code = 6000
    response_data = {
        "StatusCode": status_code,
        "company_details": company_details,
        "invoice_details": invoice_details,
        "table_heading": table_heading,
        "table_details": table_details,
        "amount": amount,
    }
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def report_export_to_excel(request):
    # content-type of response
    lang = request.GET.get("lang")
    download_type = request.GET.get("download_type")
    CompanyID = request.GET.get("CompanyID")
    BranchID = request.GET.get("BranchID")
    FromDate = request.GET.get("FromDate")
    ToDate = request.GET.get("ToDate")
    PriceRounding = int(request.GET.get("PriceRounding"))
    WareHouseID = request.GET.get("WareHouseID")
    RouteID = request.GET.get("RouteID")
    UserID = request.GET.get("UserID")
    CustomerID = request.GET.get("CustomerID")
    ProductFilter = request.GET.get("ProductFilter")
    StockFilter = request.GET.get("StockFilter")
    ProductID = request.GET.get("ProductID")
    ProductGroupID = request.GET.get("ProductGroupID")
    BatchCode = request.GET.get("BatchCode")
    CategoryID = request.GET.get("CategoryID")
    GroupID = request.GET.get("GroupID")
    Barcode = request.GET.get("Barcode")
    BrandID = request.GET.get("BrandID")
    report_type = request.GET.get("report_type")
    ManualOpeningBalance = request.GET.get("ManualOpeningBalance")
    is_manualOpening = request.GET.get("is_manualOpening")
    key = request.GET.get("key")
    ManualOpeningStock = request.GET.get("ManualOpeningStock")
    ManualClosingStock = request.GET.get("ManualClosingStock")
    ReffNo = request.GET.get("ReffNo")
    columns = request.GET.get("columns")
    profit_loss_data = request.GET.get("profit_loss_data")
    new_data = request.GET.get("new_data")
    VoucherType = request.GET.get("VoucherType")
    LedgerID = request.GET.get("LedgerID")
    PageType = request.GET.get("PageType")

    columns_heads = []
    # new_data = []
    if columns:
        columns_heads = json.loads(columns)
    print(type(new_data), "##########################", new_data)
    if new_data:
        new_data = ast.literal_eval(new_data)
    if lang:
        activate(lang)

    LedgerList = request.GET.get("CashLedgers")
    LedgerList = [x for x in LedgerList if x]
    for x in LedgerList:
        print(str(x).split(","))
        test_list = str(x).split(",")
        for i in range(0, len(test_list)):
            test_list[i] = int(test_list[i])
        LedgerList = test_list

    CashLedgers = LedgerList
    # Taiking the tittle
    title = (
        str(get_company(CompanyID).CompanyName)
        + str(",")
        + str(FromDate)
        + str(" TO ")
        + str(ToDate)
    )
    # ====

    wb = xlwt.Workbook(encoding="utf-8")
    response = HttpResponse(content_type="application/ms-excel")
    start = time.time()
    if report_type == "bill_wise":
        response["Content-Disposition"] = 'attachment; filename="Bill Wise Report.xls"'
        columns = [
            "Serial No",
            "Date",
            "Voucher Number",
            "Gross Amount",
            "TAX Amount",
            "VAT Amount",
            "Net Amount",
            "Net Cost",
            "Profit",
        ]
        data = billWise_report_data(
            CompanyID,
            PriceRounding,
            WareHouseID,
            RouteID,
            UserID,
            CustomerID,
            BranchID,
            FromDate,
            ToDate,
        )
        export_to_excel_billWise(wb, data, FromDate, ToDate, columns)
    elif report_type == "stock_report":
        response["Content-Disposition"] = 'attachment; filename="Stock Report.xls"'
        columns = [
            "Serial No",
            "Auto Barcode",
            "Product",
            "Current Stock",
            "Stock In Base Unit",
            "Purchase Price",
            "Sales Price",
        ]
        data = stock_report_data(
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
        print(data)
        export_to_excel_Stock(wb, data, FromDate, ToDate, columns)
    elif report_type == "cash_book":
        response["Content-Disposition"] = 'attachment; filename="Cash Book Report.xls"'
        columns = [
            "Serial No",
            "Voucher No",
            "Voucher Date",
            "Particulars",
            "Ledger Name",
            "Receipts",
            "Payments",
            "Balance",
        ]
        data = cash_book_report_data(
            CompanyID,
            BranchID,
            FromDate,
            ToDate,
            PriceRounding,
            ManualOpeningBalance,
            is_manualOpening,
            CashLedgers,
        )
        print(data)
        export_to_excel_cashBook(wb, data, FromDate, ToDate, columns)
    elif report_type == "bank_book":
        response["Content-Disposition"] = 'attachment; filename="Bank Book Report.xls"'
        columns = [
            "Serial No",
            "Voucher No",
            "Voucher Date",
            "Particulars",
            "Ledger Name",
            "Receipts",
            "Payments",
            "Balance",
        ]
        data = bank_book_report_data(
            CompanyID,
            BranchID,
            FromDate,
            ToDate,
            PriceRounding,
            ManualOpeningBalance,
            is_manualOpening,
            CashLedgers,
        )
        export_to_excel_bankBook(wb, data, FromDate, ToDate, columns)
    elif report_type == "trail_balance":
        response[
            "Content-Disposition"
        ] = 'attachment; filename="TrialBalance Report.xls"'
        columns = [
            str(_("Serial No")),
            str(_("Ledger Name")),
            str(_("Debit")),
            str(_("Credit")),
        ]
        data = trialBalance_excel_data(
            CompanyID, UserID, PriceRounding, BranchID, ToDate, request
        )
        export_to_excel_trialBalance(wb, data, columns)
    elif report_type == "profit_and_loss":
        response[
            "Content-Disposition"
        ] = 'attachment; filename="Profit and Loss Report.xls"'
        data = profitAndLoss_excel_data(
            VoucherType,
            int(key),
            CompanyID,
            UserID,
            PriceRounding,
            BranchID,
            ToDate,
            FromDate,
            request,
            ManualOpeningStock,
            ManualClosingStock,
        )
        export_to_excel_profitAndLoss(wb, data, int(key))
    elif report_type == "balance_sheet":
        response[
            "Content-Disposition"
        ] = 'attachment; filename="Balance Sheet Report.xls"'
        data = balanceSheet_excel_data(
            PageType,
            VoucherType,
            CompanyID,
            UserID,
            PriceRounding,
            BranchID,
            ToDate,
            FromDate,
            request,
        )
        if PageType == "Horizontal":
            export_to_excel_balanceSheet(wb, data, int(key))
        else:
            export_to_excel_balanceSingleSideSheet(wb, data, int(key))
    elif report_type == "purchase":
        title = (
            str(get_company(CompanyID).CompanyName)
            + str(",")
            + str(FromDate)
            + str(" TO ")
            + str(ToDate)
        )
        if key == "1":
            # decide file name
            response[
                "Content-Disposition"
            ] = 'attachment; filename="Purchase Report.xls"'
            data = purchase_excel_data(
                CompanyID, BranchID, FromDate, ToDate, PriceRounding, ReffNo
            )
            columns = [
                str(_("Voucher No")),
                str(_("Voucher Date")),
                str(_("Reference No")),
                str(_("Reference Date")),
                str(_("Ledger Name")),
                str(_("Gross Amount")),
                str(_("Total Tax")),
                str(_("Bill Discount")),
                str(_("Grand Total")),
            ]

            export_to_excel(wb, data, FromDate, ToDate, title, columns, columns_heads)
        else:
            response[
                "Content-Disposition"
            ] = 'attachment; filename="Purchase Return Report.xls"'
            data = purchaseReturn_excel_data(
                CompanyID, BranchID, FromDate, ToDate, PriceRounding, ReffNo
            )
            print(data)
            columns = [
                str(_("Voucher No")),
                str(_("Voucher Date")),
                str(_("Reference No")),
                str(_("Reference Date")),
                str(_("Ledger Name")),
                str(_("Gross Amount")),
                str(_("Total Tax")),
                str(_("Bill Discount")),
                str(_("Grand Total")),
            ]
            export_to_excel_purchaseRetun(
                wb, data, FromDate, ToDate, title, columns, columns_heads
            )
    elif report_type == "expence":
        response["Content-Disposition"] = 'attachment; filename="Expence Report.xls"'
        columns = [
            str(_("Voucher No")),
            str(_("Date")),
            str(_("Ledger Name")),
            str(_("Particulars")),
            str(_("TaxNumber")),
            str(_("VAT Amount")),
            str(_("IGST Amount")),
            str(_("SGST Amount")),
            str(_("CGST Amount")),
            str(_("Amount")),
            str(_("Discount")),
            str(_("Net Amount")),
        ]
        detail = expence_excel_data(
            CompanyID,
            BranchID,
            FromDate,
            ToDate,
            PriceRounding,
            CashLedgers,
        )
        try:
            data = detail["new_data"]
        except:
            data = []
        export_to_excel_expence(wb, data, FromDate, ToDate, title, columns)
    elif report_type == "batch_report":
        response["Content-Disposition"] = 'attachment; filename="Batch Report.xls"'
        columns = [
            str(_("Batch Code")),
            str(_("Date")),
            str(_("Product")),
            str(_("Product Group")),
            str(_("Mft Date")),
            str(_("Expiry Date")),
            str(_("Purchase Price")),
            str(_("Sales Price")),
            str(_("Stock")),
        ]
        detail = batch_excel_data(
            CompanyID,
            BranchID,
            FromDate,
            ToDate,
            PriceRounding,
            int(ProductGroupID),
            int(ProductID),
            int(BatchCode),
        )
        try:
            data = detail["data"]
        except:
            data = []
        print(detail)
        export_to_excel_batch(wb, data, FromDate, ToDate, title, columns)
    elif report_type == "tax_summary_vat" or report_type == "tax_summary_gst":
        # onlly PDF
        if report_type == "tax_summary_vat":
            Type = "VAT"
        else:
            Type = "GST"
        data = taxSummary_excel_data(
            CompanyID, BranchID, FromDate, ToDate, Type, PriceRounding
        )
    elif report_type == "bank_reconslation":
        response[
            "Content-Disposition"
        ] = 'attachment; filename="Reconslation Report.xls"'
        columns = [
            str(_("Date")),
            str(_("Reference No")),
            str(_("Type")),
            str(_("Statement Details")),
            str(_("Deposit")),
            str(_("Withdrawals")),
        ]
        data = bank_reconslation_date(
            CompanyID, LedgerID, BranchID, FromDate, ToDate, PriceRounding
        )
        export_to_excel_bank_reconslation(
            wb, data, FromDate, ToDate, title, columns, int(key)
        )
        VoucherType = int(key)
        print(VoucherType)

    print(time.time() - start, "((((((((((((((***report****)))))))))))))))))")
    # decide file name
    # creating workbook
    if download_type == "PDF":
        # Trail Balance Report
        if report_type == "profit_and_loss":
            VoucherType = int(key)
            report_title = str(_("PROFIT&LOSS REPORT"))
            report_name = "PROFIT&LOSS REPORT"
            template = get_template("reports/profit&loss_print.html")
        elif report_type == "balance_sheet":
            VoucherType = int(key)
            if PageType == "Horizontal":
                if VoucherType == 1:
                    data = data[0]
                elif VoucherType == 2:
                    data = data[1]
                template = get_template("reports/balance_sheet_print.html")
            else:
                data = data[0]+data[1]
                template = get_template("reports/balance_sheet_single_print.html")

            report_title = str(_("BALANCE SHEET REPORT"))
            report_name = "BALANCE SHEET REPORT"
        elif report_type == "expence":
            report_title = str(_("EXPENCE REPORT"))
            report_name = "EXPENCE REPORT"
            template = get_template("reports/expence_report_print.html")
        elif report_type == "batch_report":
            report_title = str(_("BATCH REPORT"))
            report_name = "BATCH REPORT"
            template = get_template("reports/batch_report_print.html")
        elif report_type == "tax_summary_vat" or report_type == "tax_summary_gst":
            report_title = str(_("TAX SUMMARY"))
            report_name = "TAX SUMMARY"
            template = get_template("reports/tax_summary_print.html")
        elif report_type == "bank_reconslation":
            report_title = str(_("RECONSLATION"))
            report_name = "RECONSLATION"
            template = get_template("reports/bank_reconslation.html")

        company_instance = models.CompanySettings.objects.get(id=CompanyID)
        country_instance = models.Country.objects.get(id=company_instance.Country.id)
        serialized = CompanySettingsPrintRestSerializer(
            company_instance, many=False, context={"request": request}
        )
        GST = get_GeneralSettings(CompanyID, BranchID, "GST")
        VAT = get_GeneralSettings(CompanyID, BranchID, "VAT")
        context = {
            "country": country_instance,
            # "page_type": page_type,
            "invoice_type": report_type,
            "VoucherType": VoucherType,
            "type": "pdf",
            "company": serialized.data,
            "details": data,
            "PriceRounding": int(PriceRounding),
            "FromDate": FromDate,
            "ToDate": ToDate,
            "report_title": report_title,
            "print_template": True,
            "columns_heads": columns_heads,
            "GST": GST,
            "VAT": VAT,
        }
        html = template.render(context)
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
    else:
        wb.save(response)

    return response


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def user_role_settings_list_api(request):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    userType = data["UserType"]
    BranchID = data["BranchID"]

    user_type = None
    if type(userType) == int:
        if models.UserType.objects.filter(ID=userType, CompanyID=CompanyID).exists():
            user_type = models.UserType.objects.get(ID=userType, CompanyID=CompanyID)
    else:
        if models.UserType.objects.filter(id=userType).exists():
            user_type = models.UserType.objects.get(id=userType)

    instances = models.UserRoleSettingsModel.objects.filter(
        CompanyID=CompanyID, BranchID=BranchID, UserType=user_type
    )
    serialized = serializers.UserRoleSettingsSerializer(instances, many=True)

    response_data = {"StatusCode": 6000, "data": serialized.data}
    return Response(response_data, status=status.HTTP_200_OK)
