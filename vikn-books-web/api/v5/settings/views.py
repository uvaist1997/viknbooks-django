from brands import models
from django.urls import reverse
# from brands.models import Settings, Settings_Log, PrintSettings, BarcodeSettings, Language
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v5.settings import serializers
from api.v5.brands.serializers import ListSerializer
from api.v5.settings.functions import generate_serializer_errors
from rest_framework import status
from api.v5.settings.functions import get_auto_id
from main.functions import get_company, activity_log
from api.v5.settings.functions import create_or_update_user_type_settings, get_user_type_settings
from django.shortcuts import render
from django.http import HttpResponse
import datetime
import json


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_settings(request):
    today = datetime.datetime.now()
    serialized = serializers.SettingsSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        PriceList = serialized.data['PriceList']
        GroupName = serialized.data['GroupName']
        SettingsType = serialized.data['SettingsType']
        SettingsValue = serialized.data['SettingsValue']
        CreatedUserID = serialized.data['CreatedUserID']

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
        response_data = {
            "StatusCode": 6000,
            "data": data
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
            PriceList = serialized.data['PriceList']
            GroupName = serialized.data['GroupName']
            SettingsType = serialized.data['SettingsType']
            SettingsValue = serialized.data['SettingsValue']

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
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6001,
                "message": generate_serializer_errors(serialized._errors)
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Settings Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_settings(request):
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if models.Settings.objects.filter(BranchID=BranchID).exists():

            instances = models.Settings.objects.filter(BranchID=BranchID)

            serialized = serializers.SettingsRestSerializer(
                instances, many=True)

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Settings Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def settings(request, pk):
    instance = None
    if models.Settings.objects.filter(pk=pk).exists():
        instance = models.Settings.objects.get(pk=pk)
    if instance:
        serialized = serializers.SettingsRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Settings Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
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
            "message": "Settings Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Settings Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def print_settings(request):
    today = datetime.datetime.now()
    serialized = serializers.PrintSettingsSerializer(data=request.data)
    if serialized.is_valid():
        data = request.data
        CompanyID = data['CompanyID']
        CompanyID = get_company(CompanyID)
        CreatedUserID = data['CreatedUserID']
        BranchID = data['BranchID']

        template = serialized.data['template']
        IsDefaultThermalPrinter = serialized.data['IsDefaultThermalPrinter']
        PageSize = serialized.data['PageSize']
        IsCompanyLogo = serialized.data['IsCompanyLogo']
        IsCompanyName = serialized.data['IsCompanyName']
        IsDescription = serialized.data['IsDescription']
        IsAddress = serialized.data['IsAddress']
        IsMobile = serialized.data['IsMobile']
        IsEmail = serialized.data['IsEmail']
        IsTaxNo = serialized.data['IsTaxNo']
        IsCRNo = serialized.data['IsCRNo']
        IsCurrentBalance = serialized.data['IsCurrentBalance']
        SalesInvoiceTrName = serialized.data['SalesInvoiceTrName']
        SalesOrderTrName = serialized.data['SalesOrderTrName']
        SalesReturnTrName = serialized.data['SalesReturnTrName']
        PurchaseInvoiceTrName = serialized.data['PurchaseInvoiceTrName']
        PurchaseOrderTrName = serialized.data['PurchaseOrderTrName']
        PurchaseReturnTrName = serialized.data['PurchaseReturnTrName']
        CashRecieptTrName = serialized.data['CashRecieptTrName']
        BankRecieptTrName = serialized.data['BankRecieptTrName']
        CashPaymentTrName = serialized.data['CashPaymentTrName']
        BankPaymentTrName = serialized.data['BankPaymentTrName']
        IsInclusiveTaxUnitPrice = serialized.data['IsInclusiveTaxUnitPrice']
        IsInclusiveTaxNetAmount = serialized.data['IsInclusiveTaxNetAmount']
        IsFlavour = serialized.data['IsFlavour']
        IsShowDescription = serialized.data['IsShowDescription']
        IsTotalQuantity = serialized.data['IsTotalQuantity']
        IsTaxDetails = serialized.data['IsTaxDetails']
        IsHSNCode = serialized.data['IsHSNCode']
        IsProductCode = serialized.data['IsProductCode']

        IsReceivedAmount = serialized.data['IsReceivedAmount']
        SalesInvoiceFooter = serialized.data['SalesInvoiceFooter']
        SalesReturnFooter = serialized.data['SalesReturnFooter']
        SalesOrderFooter = serialized.data['SalesOrderFooter']
        PurchaseInvoiceFooter = serialized.data['PurchaseInvoiceFooter']
        PurchaseOrderFooter = serialized.data['PurchaseOrderFooter']
        PurchaseReturnFooter = serialized.data['PurchaseReturnFooter']
        CashRecieptFooter = serialized.data['CashRecieptFooter']
        BankRecieptFooter = serialized.data['BankRecieptFooter']
        CashPaymentFooter = serialized.data['CashPaymentFooter']
        BankPaymentFooter = serialized.data['BankPaymentFooter']
        TermsAndConditionsSales = serialized.data['TermsAndConditionsSales']
        TermsAndConditionsPurchase = serialized.data['TermsAndConditionsPurchase']
        TermsAndConditionsSaleEstimate = serialized.data['TermsAndConditionsSaleEstimate']
        HeadFontSize = serialized.data['HeadFontSize']
        BodyFontSize = serialized.data['BodyFontSize']
        ContentFontSize = serialized.data['ContentFontSize']
        FooterFontSize = serialized.data['FooterFontSize']
        Action = "A"
        print_settings_id = None
        if models.PrintSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            print_settings_id = models.PrintSettings.objects.get(
                CompanyID=CompanyID, BranchID=BranchID).pk
            models.PrintSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID).update(
                template=template,
                IsDefaultThermalPrinter=IsDefaultThermalPrinter,
                PageSize=PageSize,
                IsCompanyLogo=IsCompanyLogo,
                IsCompanyName=IsCompanyName,
                IsDescription=IsDescription,
                IsAddress=IsAddress,
                IsMobile=IsMobile,
                IsEmail=IsEmail,
                IsTaxNo=IsTaxNo,
                IsCRNo=IsCRNo,
                IsCurrentBalance=IsCurrentBalance,
                SalesInvoiceTrName=SalesInvoiceTrName,
                SalesOrderTrName=SalesOrderTrName,
                SalesReturnTrName=SalesReturnTrName,
                PurchaseInvoiceTrName=PurchaseInvoiceTrName,
                PurchaseOrderTrName=PurchaseOrderTrName,
                PurchaseReturnTrName=PurchaseReturnTrName,
                CashRecieptTrName=CashRecieptTrName,
                BankRecieptTrName=BankRecieptTrName,
                CashPaymentTrName=CashPaymentTrName,
                BankPaymentTrName=BankPaymentTrName,
                IsInclusiveTaxUnitPrice=IsInclusiveTaxUnitPrice,
                IsInclusiveTaxNetAmount=IsInclusiveTaxNetAmount,
                IsFlavour=IsFlavour,
                IsShowDescription=IsShowDescription,
                IsTotalQuantity=IsTotalQuantity,
                IsTaxDetails=IsTaxDetails,
                IsHSNCode=IsHSNCode,
                IsProductCode=IsProductCode,
                IsReceivedAmount=IsReceivedAmount,
                SalesInvoiceFooter=SalesInvoiceFooter,
                SalesReturnFooter=SalesReturnFooter,
                SalesOrderFooter=SalesOrderFooter,
                PurchaseInvoiceFooter=PurchaseInvoiceFooter,
                PurchaseOrderFooter=PurchaseOrderFooter,
                PurchaseReturnFooter=PurchaseReturnFooter,
                CashRecieptFooter=CashRecieptFooter,
                BankRecieptFooter=BankRecieptFooter,
                CashPaymentFooter=CashPaymentFooter,
                BankPaymentFooter=BankPaymentFooter,
                TermsAndConditionsSales=TermsAndConditionsSales,
                TermsAndConditionsPurchase=TermsAndConditionsPurchase,
                TermsAndConditionsSaleEstimate=TermsAndConditionsSaleEstimate,
                Action=Action,
                BranchID=BranchID,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                CompanyID=CompanyID,
                HeadFontSize=HeadFontSize,
                BodyFontSize=BodyFontSize,
                ContentFontSize=ContentFontSize,
                FooterFontSize=FooterFontSize,
            )
        else:
            models.PrintSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID).create(
                template=template,
                IsDefaultThermalPrinter=IsDefaultThermalPrinter,
                PageSize=PageSize,
                IsCompanyLogo=IsCompanyLogo,
                IsCompanyName=IsCompanyName,
                IsDescription=IsDescription,
                IsAddress=IsAddress,
                IsMobile=IsMobile,
                IsEmail=IsEmail,
                IsTaxNo=IsTaxNo,
                IsCRNo=IsCRNo,
                IsCurrentBalance=IsCurrentBalance,
                SalesInvoiceTrName=SalesInvoiceTrName,
                SalesOrderTrName=SalesOrderTrName,
                SalesReturnTrName=SalesReturnTrName,
                PurchaseInvoiceTrName=PurchaseInvoiceTrName,
                PurchaseOrderTrName=PurchaseOrderTrName,
                PurchaseReturnTrName=PurchaseReturnTrName,
                CashRecieptTrName=CashRecieptTrName,
                BankRecieptTrName=BankRecieptTrName,
                CashPaymentTrName=CashPaymentTrName,
                BankPaymentTrName=BankPaymentTrName,
                IsInclusiveTaxUnitPrice=IsInclusiveTaxUnitPrice,
                IsInclusiveTaxNetAmount=IsInclusiveTaxNetAmount,
                IsFlavour=IsFlavour,
                IsShowDescription=IsShowDescription,
                IsTotalQuantity=IsTotalQuantity,
                IsTaxDetails=IsTaxDetails,
                IsHSNCode=IsHSNCode,
                IsProductCode=IsProductCode,
                IsReceivedAmount=IsReceivedAmount,
                SalesInvoiceFooter=SalesInvoiceFooter,
                SalesReturnFooter=SalesReturnFooter,
                SalesOrderFooter=SalesOrderFooter,
                PurchaseInvoiceFooter=PurchaseInvoiceFooter,
                PurchaseOrderFooter=PurchaseOrderFooter,
                PurchaseReturnFooter=PurchaseReturnFooter,
                CashRecieptFooter=CashRecieptFooter,
                BankRecieptFooter=BankRecieptFooter,
                CashPaymentFooter=CashPaymentFooter,
                BankPaymentFooter=BankPaymentFooter,
                TermsAndConditionsSales=TermsAndConditionsSales,
                TermsAndConditionsPurchase=TermsAndConditionsPurchase,
                TermsAndConditionsSaleEstimate=TermsAndConditionsSaleEstimate,
                Action=Action,
                BranchID=BranchID,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                CompanyID=CompanyID,
                HeadFontSize=HeadFontSize,
                BodyFontSize=BodyFontSize,
                ContentFontSize=ContentFontSize,
                FooterFontSize=FooterFontSize,
            )
            print_settings_id = models.PrintSettings.objects.get(
                CompanyID=CompanyID, BranchID=BranchID).pk
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data,
            "print_settings_id": print_settings_id
        }
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }
        return Response(response_data, status=status.HTTP_200_OK)


# @api_view(['POST'])
# @permission_classes((IsAuthenticated,))
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

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def barcode_settings(request):
    today = datetime.datetime.now()
    serialized = serializers.BarcodeSettingsSerializer(data=request.data)
    if serialized.is_valid():
        data = request.data
        CompanyID = data['CompanyID']
        CompanyID = get_company(CompanyID)
        CreatedUserID = data['CreatedUserID']
        BranchID = data['BranchID']

        One = serialized.data['One']
        Two = serialized.data['Two']
        Three = serialized.data['Three']
        Four = serialized.data['Four']
        Five = serialized.data['Five']
        Six = serialized.data['Six']
        Seven = serialized.data['Seven']
        Eight = serialized.data['Eight']
        Nine = serialized.data['Nine']
        Zero = serialized.data['Zero']
        Dot = serialized.data['Dot']
        size = serialized.data['size']
        template = serialized.data['template']
        Description = serialized.data['Description']
        IsCompanyName = serialized.data['IsCompanyName']
        IsProductName = serialized.data['IsProductName']
        IsPrice = serialized.data['IsPrice']
        IsCurrencyName = serialized.data['IsCurrencyName']
        IsPriceCode = serialized.data['IsPriceCode']
        IsDescription = serialized.data['IsDescription']
        Is_MRP = serialized.data['Is_MRP']

        Action = "A"
        print_settings_id = None
        if models.BarcodeSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            print_settings_id = models.BarcodeSettings.objects.get(
                CompanyID=CompanyID, BranchID=BranchID).pk
            models.BarcodeSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID).update(
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
            models.BarcodeSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID).create(
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
            "message": generate_serializer_errors(serialized._errors)
        }
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def language(request):
    today = datetime.datetime.now()
    serialized = serializers.LanguageSerializer(data=request.data)
    if serialized.is_valid():
        data = request.data
        CreatedUserID = data['CreatedUserID']
        language = data['language']

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
            "message": generate_serializer_errors(serialized._errors)
        }
        return Response(response_data, status=status.HTTP_200_OK)
# ---------------------------------------------------------------------


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_user_type_settings(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    BranchID = data['BranchID']

    today = datetime.datetime.now()
    serialized = serializers.UserTypeSettingsSerializer(data=request.data)
    if serialized.is_valid():
        Action = "A"
        User = request.user.id
        UserTypeValue = serialized.data['UserType']
        # Accounts => Masters
        AccountGroupView = serialized.data['AccountGroupView']
        AccountGroupSave = serialized.data['AccountGroupSave']
        AccountGroupEdit = serialized.data['AccountGroupEdit']
        AccountGroupDelete = serialized.data['AccountGroupDelete']
        AccountLedgerView = serialized.data['AccountLedgerView']
        AccountLedgerSave = serialized.data['AccountLedgerSave']
        AccountLedgerEdit = serialized.data['AccountLedgerEdit']
        AccountLedgerDelete = serialized.data['AccountLedgerDelete']
        BankView = serialized.data['BankView']
        BankSave = serialized.data['BankSave']
        BankEdit = serialized.data['BankEdit']
        BankDelete = serialized.data['BankDelete']
        CustomerView = serialized.data['CustomerView']
        CustomerSave = serialized.data['CustomerSave']
        CustomerEdit = serialized.data['CustomerEdit']
        CustomerDelete = serialized.data['CustomerDelete']
        SupplierView = serialized.data['SupplierView']
        SupplierSave = serialized.data['SupplierSave']
        SupplierEdit = serialized.data['SupplierEdit']
        SupplierDelete = serialized.data['SupplierDelete']
        TransactionTypeView = serialized.data['TransactionTypeView']
        TransactionTypeSave = serialized.data['TransactionTypeSave']
        TransactionTypeEdit = serialized.data['TransactionTypeEdit']
        TransactionTypeDelete = serialized.data['TransactionTypeDelete']

        # Accounts => Transactions
        BankPaymentDelete = serialized.data['BankPaymentDelete']
        BankPaymentEdit = serialized.data['BankPaymentEdit']
        BankPaymentSave = serialized.data['BankPaymentSave']
        BankPaymentView = serialized.data['BankPaymentView']
        BankReceiptDelete = serialized.data['BankReceiptDelete']
        BankReceiptEdit = serialized.data['BankReceiptEdit']
        BankReceiptSave = serialized.data['BankReceiptSave']
        BankReceiptView = serialized.data['BankReceiptView']
        CashPaymentDelete = serialized.data['CashPaymentDelete']
        CashPaymentEdit = serialized.data['CashPaymentEdit']
        CashPaymentSave = serialized.data['CashPaymentSave']
        CashPaymentView = serialized.data['CashPaymentView']
        CashReceiptDelete = serialized.data['CashReceiptDelete']
        CashReceiptEdit = serialized.data['CashReceiptEdit']
        CashReceiptSave = serialized.data['CashReceiptSave']
        CashReceiptView = serialized.data['CashReceiptView']
        JournalEntryDelete = serialized.data['JournalEntryDelete']
        JournalEntryEdit = serialized.data['JournalEntryEdit']
        JournalEntrySave = serialized.data['JournalEntrySave']
        JournalEntryView = serialized.data['JournalEntryView']

        try:
            CashPaymentDiscountLimit = serialized.data['CashPaymentDiscountLimit']
        except:
            CashPaymentDiscountLimit = 0
        try:
            CashReceiptDiscountLimit = serialized.data['CashReceiptDiscountLimit']
        except:
            CashReceiptDiscountLimit = 0
        try:
            BankPaymentLimit = serialized.data['BankPaymentLimit']
        except:
            BankPaymentLimit = 0
        try:
            BankReceiptLimit = serialized.data['BankReceiptLimit']
        except:
            BankReceiptLimit = 0
        # Accounts => Reports
        LedgerReportView = serialized.data['LedgerReportView']
        LedgerReportPrint = serialized.data['LedgerReportPrint']
        LedgerReportExport = serialized.data['LedgerReportExport']
        TrialBalanceView = serialized.data['TrialBalanceView']
        TrialBalancePrint = serialized.data['TrialBalancePrint']
        TrialBalanceExport = serialized.data['TrialBalanceExport']
        ProfitAndLossView = serialized.data['ProfitAndLossView']
        ProfitAndLossPrint = serialized.data['ProfitAndLossPrint']
        ProfitAndLossExport = serialized.data['ProfitAndLossExport']
        BalanceSheetView = serialized.data['BalanceSheetView']
        BalanceSheetPrint = serialized.data['BalanceSheetPrint']
        BalanceSheetExport = serialized.data['BalanceSheetExport']
        DailyReportView = serialized.data['DailyReportView']
        DailyReportPrint = serialized.data['DailyReportPrint']
        DailyReportExport = serialized.data['DailyReportExport']
        CashBookView = serialized.data['CashBookView']
        CashBookPrint = serialized.data['CashBookPrint']
        CashBookExport = serialized.data['CashBookExport']
        VATReportView = serialized.data['VATReportView']
        VATReportPrint = serialized.data['VATReportPrint']
        VATReportExport = serialized.data['VATReportExport']

        # Inventory => Masters
        ProductGroupView = serialized.data['ProductGroupView']
        ProductGroupSave = serialized.data['ProductGroupSave']
        ProductGroupEdit = serialized.data['ProductGroupEdit']
        ProductGroupDelete = serialized.data['ProductGroupDelete']
        BrandsView = serialized.data['BrandsView']
        BrandsSave = serialized.data['BrandsSave']
        BrandsEdit = serialized.data['BrandsEdit']
        BrandsDelete = serialized.data['BrandsDelete']
        TaxCategoriesView = serialized.data['TaxCategoriesView']
        TaxCategoriesSave = serialized.data['TaxCategoriesSave']
        TaxCategoriesEdit = serialized.data['TaxCategoriesEdit']
        TaxCategoriesDelete = serialized.data['TaxCategoriesDelete']
        PriceCategoriesView = serialized.data['PriceCategoriesView']
        PriceCategoriesSave = serialized.data['PriceCategoriesSave']
        PriceCategoriesEdit = serialized.data['PriceCategoriesEdit']
        PriceCategoriesDelete = serialized.data['PriceCategoriesDelete']
        WarehouseView = serialized.data['WarehouseView']
        WarehouseSave = serialized.data['WarehouseSave']
        WarehouseEdit = serialized.data['WarehouseEdit']
        WarehouseDelete = serialized.data['WarehouseDelete']
        ProductCategoriesView = serialized.data['ProductCategoriesView']
        ProductCategoriesSave = serialized.data['ProductCategoriesSave']
        ProductCategoriesEdit = serialized.data['ProductCategoriesEdit']
        ProductCategoriesDelete = serialized.data['ProductCategoriesDelete']
        ProductsView = serialized.data['ProductsView']
        ProductsSave = serialized.data['ProductsSave']
        ProductsEdit = serialized.data['ProductsEdit']
        ProductsDelete = serialized.data['ProductsDelete']
        RoutesView = serialized.data['RoutesView']
        RoutesSave = serialized.data['RoutesSave']
        RoutesEdit = serialized.data['RoutesEdit']
        RoutesDelete = serialized.data['RoutesDelete']
        UnitsView = serialized.data['UnitsView']
        UnitsSave = serialized.data['UnitsSave']
        UnitsEdit = serialized.data['UnitsEdit']
        UnitsDelete = serialized.data['UnitsDelete']

        # Inventory => Transaction
        PurchaseInvoicesView = serialized.data['PurchaseInvoicesView']
        PurchaseInvoicesSave = serialized.data['PurchaseInvoicesSave']
        PurchaseInvoicesEdit = serialized.data['PurchaseInvoicesEdit']
        PurchaseInvoicesDelete = serialized.data['PurchaseInvoicesDelete']
        WorkOrdersView = serialized.data['WorkOrdersView']
        WorkOrdersSave = serialized.data['WorkOrdersSave']
        WorkOrdersEdit = serialized.data['WorkOrdersEdit']
        WorkOrdersDelete = serialized.data['WorkOrdersDelete']
        PurchaseReturnsView = serialized.data['PurchaseReturnsView']
        PurchaseReturnsSave = serialized.data['PurchaseReturnsSave']
        PurchaseReturnsEdit = serialized.data['PurchaseReturnsEdit']
        PurchaseReturnsDelete = serialized.data['PurchaseReturnsDelete']
        SaleInvoicesView = serialized.data['SaleInvoicesView']
        SaleInvoicesSave = serialized.data['SaleInvoicesSave']
        SaleInvoicesEdit = serialized.data['SaleInvoicesEdit']
        SaleInvoicesDelete = serialized.data['SaleInvoicesDelete']
        SaleReturnsView = serialized.data['SaleReturnsView']
        SaleReturnsSave = serialized.data['SaleReturnsSave']
        SaleReturnsEdit = serialized.data['SaleReturnsEdit']
        SaleReturnsDelete = serialized.data['SaleReturnsDelete']
        OpeningStockView = serialized.data['OpeningStockView']
        OpeningStockSave = serialized.data['OpeningStockSave']
        OpeningStockEdit = serialized.data['OpeningStockEdit']
        OpeningStockDelete = serialized.data['OpeningStockDelete']
        StockTransferView = serialized.data['StockTransferView']
        StockTransferSave = serialized.data['StockTransferSave']
        StockTransferEdit = serialized.data['StockTransferEdit']
        StockTransferDelete = serialized.data['StockTransferDelete']
        ExcessStocksView = serialized.data['ExcessStocksView']
        ExcessStocksSave = serialized.data['ExcessStocksSave']
        ExcessStocksEdit = serialized.data['ExcessStocksEdit']
        ExcessStocksDelete = serialized.data['ExcessStocksDelete']
        ShortageStocksView = serialized.data['ShortageStocksView']
        ShortageStocksSave = serialized.data['ShortageStocksSave']
        ShortageStocksEdit = serialized.data['ShortageStocksEdit']
        ShortageStocksDelete = serialized.data['ShortageStocksDelete']
        DamageStocksView = serialized.data['DamageStocksView']
        DamageStocksSave = serialized.data['DamageStocksSave']
        DamageStocksEdit = serialized.data['DamageStocksEdit']
        DamageStocksDelete = serialized.data['DamageStocksDelete']
        UsedStocksView = serialized.data['UsedStocksView']
        UsedStocksSave = serialized.data['UsedStocksSave']
        UsedStocksEdit = serialized.data['UsedStocksEdit']
        UsedStocksDelete = serialized.data['UsedStocksDelete']
        StockAdjustmentsView = serialized.data['StockAdjustmentsView']
        StockAdjustmentsSave = serialized.data['StockAdjustmentsSave']
        StockAdjustmentsEdit = serialized.data['StockAdjustmentsEdit']
        StockAdjustmentsDelete = serialized.data['StockAdjustmentsDelete']
        SalesOrderView = serialized.data['SalesOrderView']
        SalesOrderSave = serialized.data['SalesOrderSave']
        SalesOrderEdit = serialized.data['SalesOrderEdit']
        SalesOrderDelete = serialized.data['SalesOrderDelete']
        SalesEstimateView = serialized.data['SalesEstimateView']
        SalesEstimateSave = serialized.data['SalesEstimateSave']
        SalesEstimateEdit = serialized.data['SalesEstimateEdit']
        SalesEstimateDelete = serialized.data['SalesEstimateDelete']

        try:
            PurchaseInvoicesDiscountLimit = serialized.data['PurchaseInvoicesDiscountLimit']
        except:
            PurchaseInvoicesDiscountLimit = 0
        try:
            PurchaseReturnsDiscountLimit = serialized.data['PurchaseReturnsDiscountLimit']
        except:
            PurchaseReturnsDiscountLimit = 0
        try:
            SaleInvoicesDiscountLimit = serialized.data['SaleInvoicesDiscountLimit']
        except:
            SaleInvoicesDiscountLimit = 0
        try:
            SaleReturnsDiscountLimit = serialized.data['SaleReturnsDiscountLimit']
        except:
            SaleReturnsDiscountLimit = 0
        # Inventory => Reports
        StockReportView = serialized.data['StockReportView']
        StockReportPrint = serialized.data['StockReportPrint']
        StockReportExport = serialized.data['StockReportExport']
        StockValueReportView = serialized.data['StockValueReportView']
        StockValueReportPrint = serialized.data['StockValueReportPrint']
        StockValueReportExport = serialized.data['StockValueReportExport']
        PurchaseReportView = serialized.data['PurchaseReportView']
        PurchaseReportPrint = serialized.data['PurchaseReportPrint']
        PurchaseReportExport = serialized.data['PurchaseReportExport']
        SalesReportView = serialized.data['SalesReportView']
        SalesReportPrint = serialized.data['SalesReportPrint']
        SalesReportExport = serialized.data['SalesReportExport']
        SalesIntegratedReportView = serialized.data['SalesIntegratedReportView']
        SalesIntegratedReportPrint = serialized.data['SalesIntegratedReportPrint']
        SalesIntegratedReportExport = serialized.data['SalesIntegratedReportExport']
        SalesRegisterReportView = serialized.data['SalesRegisterReportView']
        SalesRegisterReportPrint = serialized.data['SalesRegisterReportPrint']
        SalesRegisterReportExport = serialized.data['SalesRegisterReportExport']
        BillWiseReportView = serialized.data['BillWiseReportView']
        BillWiseReportPrint = serialized.data['BillWiseReportPrint']
        BillWiseReportExport = serialized.data['BillWiseReportExport']
        ExcessStockReportView = serialized.data['ExcessStockReportView']
        ExcessStockReportPrint = serialized.data['ExcessStockReportPrint']
        ExcessStockReportExport = serialized.data['ExcessStockReportExport']
        DamageStockReportView = serialized.data['DamageStockReportView']
        DamageStockReportPrint = serialized.data['DamageStockReportPrint']
        DamageStockReportExport = serialized.data['DamageStockReportExport']
        UsedStockReportView = serialized.data['UsedStockReportView']
        UsedStockReportPrint = serialized.data['UsedStockReportPrint']
        UsedStockReportExport = serialized.data['UsedStockReportExport']
        BatchWiseReportView = serialized.data['BatchWiseReportView']
        BatchWiseReportPrint = serialized.data['BatchWiseReportPrint']
        BatchWiseReportExport = serialized.data['BatchWiseReportExport']

        # Payroll => Masters
        DepartmentsView = serialized.data['DepartmentsView']
        DepartmentsSave = serialized.data['DepartmentsSave']
        DepartmentsEdit = serialized.data['DepartmentsEdit']
        DepartmentsDelete = serialized.data['DepartmentsDelete']
        DesignationsView = serialized.data['DesignationsView']
        DesignationsSave = serialized.data['DesignationsSave']
        DesignationsEdit = serialized.data['DesignationsEdit']
        DesignationsDelete = serialized.data['DesignationsDelete']
        EmployeeView = serialized.data['EmployeeView']
        EmployeeSave = serialized.data['EmployeeSave']
        EmployeeEdit = serialized.data['EmployeeEdit']
        EmployeeDelete = serialized.data['EmployeeDelete']

        # Settings
        PrinterView = serialized.data['PrinterView']
        BarcodeView = serialized.data['BarcodeView']
        PrintBarcodeView = serialized.data['PrintBarcodeView']
        UserType_instance = models.UserType.objects.get(id=UserTypeValue, CompanyID=CompanyID,
                                                        BranchID=BranchID)
        # arguments order :- User, GroupName, SettingsType, SettingsValue, usertype
        # Accounts => Masters
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "AccountGroupView", AccountGroupView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "AccountGroupSave", AccountGroupSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "AccountGroupEdit", AccountGroupEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "AccountGroupDelete", AccountGroupDelete, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "AccountLedgerView", AccountLedgerView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "AccountLedgerSave", AccountLedgerSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "AccountLedgerEdit", AccountLedgerEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "AccountLedgerDelete", AccountLedgerDelete, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "BankView", BankView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "BankSave", BankSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "BankEdit", BankEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "BankDelete", BankDelete, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "CustomerView", CustomerView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "CustomerSave", CustomerSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "CustomerEdit", CustomerEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "CustomerDelete", CustomerDelete, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "SupplierView", SupplierView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "SupplierSave", SupplierSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "SupplierEdit", SupplierEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "SupplierDelete", SupplierDelete, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "TransactionTypeView", TransactionTypeView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "TransactionTypeSave", TransactionTypeSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "TransactionTypeEdit", TransactionTypeEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "TransactionTypeDelete", TransactionTypeDelete, UserType_instance)

        # Accounts => Transactions
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "BankPaymentDelete", BankPaymentDelete, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "BankPaymentEdit", BankPaymentEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "BankPaymentSave", BankPaymentSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "BankPaymentView", BankPaymentView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "BankReceiptDelete", BankReceiptDelete, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "BankReceiptEdit", BankReceiptEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "BankReceiptSave", BankReceiptSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "BankReceiptView", BankReceiptView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "CashPaymentDelete", CashPaymentDelete, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "CashPaymentEdit", CashPaymentEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "CashPaymentSave", CashPaymentSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "CashPaymentView", CashPaymentView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "CashReceiptDelete", CashReceiptDelete, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "CashReceiptEdit", CashReceiptEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "CashReceiptSave", CashReceiptSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "CashReceiptView", CashReceiptView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "JournalEntryDelete", JournalEntryDelete, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "JournalEntryEdit", JournalEntryEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "JournalEntrySave", JournalEntrySave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "JournalEntryView", JournalEntryView, UserType_instance)

        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "CashPaymentDiscountLimit", CashPaymentDiscountLimit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "CashReceiptDiscountLimit", CashReceiptDiscountLimit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "BankPaymentLimit", BankPaymentLimit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "BankReceiptLimit", BankReceiptLimit, UserType_instance)
        # Accounts => Reports
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "LedgerReportView", LedgerReportView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "LedgerReportPrint", LedgerReportPrint, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "LedgerReportExport", LedgerReportExport, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "TrialBalanceView", TrialBalanceView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "TrialBalancePrint", TrialBalancePrint, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "TrialBalanceExport", TrialBalanceExport, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "ProfitAndLossView", ProfitAndLossView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "ProfitAndLossPrint", ProfitAndLossPrint, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "ProfitAndLossExport", ProfitAndLossExport, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "BalanceSheetView", BalanceSheetView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "BalanceSheetPrint", BalanceSheetPrint, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "BalanceSheetExport", BalanceSheetExport, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "DailyReportView", DailyReportView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "DailyReportPrint", DailyReportPrint, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "DailyReportExport", DailyReportExport, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "CashBookView", CashBookView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "CashBookPrint", CashBookPrint, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "CashBookExport", CashBookExport, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "VATReportView", VATReportView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "VATReportPrint", VATReportPrint, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "VATReportExport", VATReportExport, UserType_instance)

        # Inventory => Masters
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductGroupView", ProductGroupView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductGroupSave", ProductGroupSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductGroupEdit", ProductGroupEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductGroupDelete", ProductGroupDelete, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "BrandsView", BrandsView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "BrandsSave", BrandsSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "BrandsEdit", BrandsEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "BrandsDelete", BrandsDelete, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "TaxCategoriesView", TaxCategoriesView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "TaxCategoriesSave", TaxCategoriesSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "TaxCategoriesEdit", TaxCategoriesEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "TaxCategoriesDelete", TaxCategoriesDelete, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "PriceCategoriesView", PriceCategoriesView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "PriceCategoriesSave", PriceCategoriesSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "PriceCategoriesEdit", PriceCategoriesEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "PriceCategoriesDelete", PriceCategoriesDelete, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "WarehouseView", WarehouseView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "WarehouseSave", WarehouseSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "WarehouseEdit", WarehouseEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "WarehouseDelete", WarehouseDelete, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductCategoriesView", ProductCategoriesView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductCategoriesSave", ProductCategoriesSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductCategoriesEdit", ProductCategoriesEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductCategoriesDelete", ProductCategoriesDelete, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductsView", ProductsView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductsSave", ProductsSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductsEdit", ProductsEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductsDelete", ProductsDelete, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "RoutesView", RoutesView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "RoutesSave", RoutesSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "RoutesEdit", RoutesEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "RoutesDelete", RoutesDelete, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "UnitsView", UnitsView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "UnitsSave", UnitsSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "UnitsEdit", UnitsEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "UnitsDelete", UnitsDelete, UserType_instance)

        # Inventory => Transactions
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "PurchaseInvoicesView", PurchaseInvoicesView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "PurchaseInvoicesSave", PurchaseInvoicesSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "PurchaseInvoicesEdit", PurchaseInvoicesEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "PurchaseInvoicesDelete", PurchaseInvoicesDelete, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "WorkOrdersView", WorkOrdersView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "WorkOrdersSave", WorkOrdersSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "WorkOrdersEdit", WorkOrdersEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "WorkOrdersDelete", WorkOrdersDelete, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "PurchaseReturnsView", PurchaseReturnsView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "PurchaseReturnsSave", PurchaseReturnsSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "PurchaseReturnsEdit", PurchaseReturnsEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "PurchaseReturnsDelete", PurchaseReturnsDelete, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SaleInvoicesView", SaleInvoicesView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SaleInvoicesSave", SaleInvoicesSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SaleInvoicesEdit", SaleInvoicesEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SaleInvoicesDelete", SaleInvoicesDelete, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SaleReturnsView", SaleReturnsView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SaleReturnsSave", SaleReturnsSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SaleReturnsEdit", SaleReturnsEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SaleReturnsDelete", SaleReturnsDelete, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "OpeningStockView", OpeningStockView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "OpeningStockSave", OpeningStockSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "OpeningStockEdit", OpeningStockEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "OpeningStockDelete", OpeningStockDelete, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "StockTransferView", StockTransferView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "StockTransferSave", StockTransferSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "StockTransferEdit", StockTransferEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "StockTransferDelete", StockTransferDelete, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "ExcessStocksView", ExcessStocksView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "ExcessStocksSave", ExcessStocksSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "ExcessStocksEdit", ExcessStocksEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "ExcessStocksDelete", ExcessStocksDelete, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "ShortageStocksView", ShortageStocksView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "ShortageStocksSave", ShortageStocksSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "ShortageStocksEdit", ShortageStocksEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "ShortageStocksDelete", ShortageStocksDelete, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "DamageStocksView", DamageStocksView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "DamageStocksSave", DamageStocksSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "DamageStocksEdit", DamageStocksEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "DamageStocksDelete", DamageStocksDelete, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "UsedStocksView", UsedStocksView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "UsedStocksSave", UsedStocksSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "UsedStocksEdit", UsedStocksEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "UsedStocksDelete", UsedStocksDelete, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "StockAdjustmentsView", StockAdjustmentsView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "StockAdjustmentsSave", StockAdjustmentsSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "StockAdjustmentsEdit", StockAdjustmentsEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "StockAdjustmentsDelete", StockAdjustmentsDelete, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SalesOrderView", SalesOrderView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SalesOrderSave", SalesOrderSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SalesOrderEdit", SalesOrderEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SalesOrderDelete", SalesOrderDelete, UserType_instance)
        # -----------------------------------------
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SalesEstimateView", SalesEstimateView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SalesEstimateSave", SalesEstimateSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SalesEstimateEdit", SalesEstimateEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SalesEstimateDelete", SalesEstimateDelete, UserType_instance)
        # -----------------------------------------
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "BatchWiseReportView", BatchWiseReportView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "BatchWiseReportPrint", BatchWiseReportPrint, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "BatchWiseReportExport", BatchWiseReportExport, UserType_instance)

        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "PurchaseInvoicesDiscountLimit", PurchaseInvoicesDiscountLimit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "PurchaseReturnsDiscountLimit", PurchaseReturnsDiscountLimit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SaleInvoicesDiscountLimit", SaleInvoicesDiscountLimit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SaleReturnsDiscountLimit", SaleReturnsDiscountLimit, UserType_instance)

        # Inventory => Reports
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "StockReportView", StockReportView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "StockReportPrint", StockReportPrint, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "StockReportExport", StockReportExport, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "StockValueReportView", StockValueReportView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "StockValueReportPrint", StockValueReportPrint, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "StockValueReportExport", StockValueReportExport, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "PurchaseReportView", PurchaseReportView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "PurchaseReportPrint", PurchaseReportPrint, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "PurchaseReportExport", PurchaseReportExport, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "SalesReportView", SalesReportView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "SalesReportPrint", SalesReportPrint, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "SalesReportExport", SalesReportExport, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "SalesIntegratedReportView", SalesIntegratedReportView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "SalesIntegratedReportPrint", SalesIntegratedReportPrint, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "SalesIntegratedReportExport", SalesIntegratedReportExport, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "SalesRegisterReportView", SalesRegisterReportView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "SalesRegisterReportPrint", SalesRegisterReportPrint, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "SalesRegisterReportExport", SalesRegisterReportExport, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "BillWiseReportView", BillWiseReportView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "BillWiseReportPrint", BillWiseReportPrint, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "BillWiseReportExport", BillWiseReportExport, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "ExcessStockReportView", ExcessStockReportView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "ExcessStockReportPrint", ExcessStockReportPrint, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "ExcessStockReportExport", ExcessStockReportExport, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "DamageStockReportView", DamageStockReportView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "DamageStockReportPrint", DamageStockReportPrint, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "DamageStockReportExport", DamageStockReportExport, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "UsedStockReportView", UsedStockReportView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "UsedStockReportPrint", UsedStockReportPrint, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "UsedStockReportExport", UsedStockReportExport, UserType_instance)
        # Payroll => Masters
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "DepartmentsView", DepartmentsView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "DepartmentsSave", DepartmentsSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "DepartmentsEdit", DepartmentsEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "DepartmentsDelete", DepartmentsDelete, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "DesignationsView", DesignationsView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "DesignationsSave", DesignationsSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "DesignationsEdit", DesignationsEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "DesignationsDelete", DesignationsDelete, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "EmployeeView", EmployeeView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "EmployeeSave", EmployeeSave, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "EmployeeEdit", EmployeeEdit, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "EmployeeDelete", EmployeeDelete, UserType_instance)

        # Settings
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Settings", "PrinterView", PrinterView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Settings", "BarcodeView", BarcodeView, UserType_instance)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Settings", "PrintBarcodeView", PrintBarcodeView, UserType_instance)

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
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def user_type_settings_list(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    BranchID = data['BranchID']
    try:
        UserTypeValue = data['UserType']
        UserTypeValue = models.UserType.objects.get(
            pk=UserTypeValue, CompanyID=CompanyID, BranchID=BranchID)
    except:
        try:
            UserTypeValue = models.UserTable.objects.get(
                CompanyID=CompanyID, customer__user__pk=CreatedUserID).UserType.id
            UserTypeValue = models.UserType.objects.get(
                pk=UserTypeValue, CompanyID=CompanyID, BranchID=BranchID)
        except:
            usertype_instance = models.UserType.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, UserTypeName="Admin")
            user_table_instance = models.UserTable.objects.filter(
                CompanyID=CompanyID).last()
            user_table_instance.CreatedUserID = CreatedUserID
            user_table_instance.UserType = usertype_instance
            user_table_instance.save()

            UserTypeValue = models.UserTable.objects.get(
                CompanyID=CompanyID, customer__user__pk=CreatedUserID).UserType.id
            UserTypeValue = models.UserType.objects.get(
                pk=UserTypeValue, CompanyID=CompanyID, BranchID=BranchID)
    UserTypeName = UserTypeValue.UserTypeName
    print(UserTypeName)
    User = request.user.id

    if models.UserTypeSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        # Accounts => Masters
        AccountGroupView = get_user_type_settings(
            CompanyID, BranchID, "AccountGroupView", UserTypeValue)
        AccountGroupSave = get_user_type_settings(
            CompanyID, BranchID, "AccountGroupSave", UserTypeValue)
        AccountGroupEdit = get_user_type_settings(
            CompanyID, BranchID, "AccountGroupEdit", UserTypeValue)
        AccountGroupDelete = get_user_type_settings(
            CompanyID, BranchID, "AccountGroupDelete", UserTypeValue)
        AccountLedgerView = get_user_type_settings(
            CompanyID, BranchID, "AccountLedgerView", UserTypeValue)
        AccountLedgerSave = get_user_type_settings(
            CompanyID, BranchID, "AccountLedgerSave", UserTypeValue)
        AccountLedgerEdit = get_user_type_settings(
            CompanyID, BranchID, "AccountLedgerEdit", UserTypeValue)
        AccountLedgerDelete = get_user_type_settings(
            CompanyID, BranchID, "AccountLedgerDelete", UserTypeValue)
        BankView = get_user_type_settings(
            CompanyID, BranchID, "BankView", UserTypeValue)
        BankSave = get_user_type_settings(
            CompanyID, BranchID, "BankSave", UserTypeValue)
        BankEdit = get_user_type_settings(
            CompanyID, BranchID, "BankEdit", UserTypeValue)
        BankDelete = get_user_type_settings(
            CompanyID, BranchID, "BankDelete", UserTypeValue)
        CustomerView = get_user_type_settings(
            CompanyID, BranchID, "CustomerView", UserTypeValue)
        CustomerSave = get_user_type_settings(
            CompanyID, BranchID, "CustomerSave", UserTypeValue)
        CustomerEdit = get_user_type_settings(
            CompanyID, BranchID, "CustomerEdit", UserTypeValue)
        CustomerDelete = get_user_type_settings(
            CompanyID, BranchID, "CustomerDelete", UserTypeValue)
        SupplierView = get_user_type_settings(
            CompanyID, BranchID, "SupplierView", UserTypeValue)
        SupplierSave = get_user_type_settings(
            CompanyID, BranchID, "SupplierSave", UserTypeValue)
        SupplierEdit = get_user_type_settings(
            CompanyID, BranchID, "SupplierEdit", UserTypeValue)
        SupplierDelete = get_user_type_settings(
            CompanyID, BranchID, "SupplierDelete", UserTypeValue)
        TransactionTypeView = get_user_type_settings(
            CompanyID, BranchID, "TransactionTypeView", UserTypeValue)
        TransactionTypeSave = get_user_type_settings(
            CompanyID, BranchID, "TransactionTypeSave", UserTypeValue)
        TransactionTypeEdit = get_user_type_settings(
            CompanyID, BranchID, "TransactionTypeEdit", UserTypeValue)
        TransactionTypeDelete = get_user_type_settings(
            CompanyID, BranchID, "TransactionTypeDelete", UserTypeValue)
        # Accounts => Transactions
        BankPaymentDelete = get_user_type_settings(
            CompanyID, BranchID, "BankPaymentDelete", UserTypeValue)
        BankPaymentEdit = get_user_type_settings(
            CompanyID, BranchID, "BankPaymentEdit", UserTypeValue)
        BankPaymentSave = get_user_type_settings(
            CompanyID, BranchID, "BankPaymentSave", UserTypeValue)
        BankPaymentView = get_user_type_settings(
            CompanyID, BranchID, "BankPaymentView", UserTypeValue)
        BankReceiptDelete = get_user_type_settings(
            CompanyID, BranchID, "BankReceiptDelete", UserTypeValue)
        BankReceiptEdit = get_user_type_settings(
            CompanyID, BranchID, "BankReceiptEdit", UserTypeValue)
        BankReceiptSave = get_user_type_settings(
            CompanyID, BranchID, "BankReceiptSave", UserTypeValue)
        BankReceiptView = get_user_type_settings(
            CompanyID, BranchID, "BankReceiptView", UserTypeValue)
        CashPaymentDelete = get_user_type_settings(
            CompanyID, BranchID, "CashPaymentDelete", UserTypeValue)
        CashPaymentEdit = get_user_type_settings(
            CompanyID, BranchID, "CashPaymentEdit", UserTypeValue)
        CashPaymentSave = get_user_type_settings(
            CompanyID, BranchID, "CashPaymentSave", UserTypeValue)
        CashPaymentView = get_user_type_settings(
            CompanyID, BranchID, "CashPaymentView", UserTypeValue)
        CashReceiptDelete = get_user_type_settings(
            CompanyID, BranchID, "CashReceiptDelete", UserTypeValue)
        CashReceiptEdit = get_user_type_settings(
            CompanyID, BranchID, "CashReceiptEdit", UserTypeValue)
        CashReceiptSave = get_user_type_settings(
            CompanyID, BranchID, "CashReceiptSave", UserTypeValue)
        CashReceiptView = get_user_type_settings(
            CompanyID, BranchID, "CashReceiptView", UserTypeValue)
        JournalEntryDelete = get_user_type_settings(
            CompanyID, BranchID, "JournalEntryDelete", UserTypeValue)
        JournalEntryEdit = get_user_type_settings(
            CompanyID, BranchID, "JournalEntryEdit", UserTypeValue)
        JournalEntrySave = get_user_type_settings(
            CompanyID, BranchID, "JournalEntrySave", UserTypeValue)
        JournalEntryView = get_user_type_settings(
            CompanyID, BranchID, "JournalEntryView", UserTypeValue)

        CashPaymentDiscountLimit = 0
        CashReceiptDiscountLimit = 0
        BankPaymentLimit = 0
        BankReceiptLimit = 0
        if get_user_type_settings(
                CompanyID, BranchID, "CashPaymentDiscountLimit", UserTypeValue):
            CashPaymentDiscountLimit = get_user_type_settings(
                CompanyID, BranchID, "CashPaymentDiscountLimit", UserTypeValue)
        if get_user_type_settings(
                CompanyID, BranchID, "CashReceiptDiscountLimit", UserTypeValue):
            CashReceiptDiscountLimit = get_user_type_settings(
                CompanyID, BranchID, "CashReceiptDiscountLimit", UserTypeValue)

        if get_user_type_settings(
                CompanyID, BranchID, "BankPaymentLimit", UserTypeValue):
            BankPaymentLimit = get_user_type_settings(
                CompanyID, BranchID, "BankPaymentLimit", UserTypeValue)

        if get_user_type_settings(
                CompanyID, BranchID, "BankReceiptLimit", UserTypeValue):
            BankReceiptLimit = get_user_type_settings(
                CompanyID, BranchID, "BankReceiptLimit", UserTypeValue)

        # Accounts => Reports
        LedgerReportView = get_user_type_settings(
            CompanyID, BranchID, "LedgerReportView", UserTypeValue)
        LedgerReportPrint = get_user_type_settings(
            CompanyID, BranchID, "LedgerReportPrint", UserTypeValue)
        LedgerReportExport = get_user_type_settings(
            CompanyID, BranchID, "LedgerReportExport", UserTypeValue)
        TrialBalanceView = get_user_type_settings(
            CompanyID, BranchID, "TrialBalanceView", UserTypeValue)
        TrialBalancePrint = get_user_type_settings(
            CompanyID, BranchID, "TrialBalancePrint", UserTypeValue)
        TrialBalanceExport = get_user_type_settings(
            CompanyID, BranchID, "TrialBalanceExport", UserTypeValue)
        ProfitAndLossView = get_user_type_settings(
            CompanyID, BranchID, "ProfitAndLossView", UserTypeValue)
        ProfitAndLossPrint = get_user_type_settings(
            CompanyID, BranchID, "ProfitAndLossPrint", UserTypeValue)
        ProfitAndLossExport = get_user_type_settings(
            CompanyID, BranchID, "ProfitAndLossExport", UserTypeValue)
        BalanceSheetView = get_user_type_settings(
            CompanyID, BranchID, "BalanceSheetView", UserTypeValue)
        BalanceSheetPrint = get_user_type_settings(
            CompanyID, BranchID, "BalanceSheetPrint", UserTypeValue)
        BalanceSheetExport = get_user_type_settings(
            CompanyID, BranchID, "BalanceSheetExport", UserTypeValue)
        DailyReportView = get_user_type_settings(
            CompanyID, BranchID, "DailyReportView", UserTypeValue)
        DailyReportPrint = get_user_type_settings(
            CompanyID, BranchID, "DailyReportPrint", UserTypeValue)
        DailyReportExport = get_user_type_settings(
            CompanyID, BranchID, "DailyReportExport", UserTypeValue)
        CashBookView = get_user_type_settings(
            CompanyID, BranchID, "CashBookView", UserTypeValue)
        CashBookPrint = get_user_type_settings(
            CompanyID, BranchID, "CashBookPrint", UserTypeValue)
        CashBookExport = get_user_type_settings(
            CompanyID, BranchID, "CashBookExport", UserTypeValue)
        VATReportView = get_user_type_settings(
            CompanyID, BranchID, "VATReportView", UserTypeValue)
        VATReportPrint = get_user_type_settings(
            CompanyID, BranchID, "VATReportPrint", UserTypeValue)
        VATReportExport = get_user_type_settings(
            CompanyID, BranchID, "VATReportExport", UserTypeValue)

        # Inventory => Masters
        ProductGroupView = get_user_type_settings(
            CompanyID, BranchID, "ProductGroupView", UserTypeValue)
        ProductGroupSave = get_user_type_settings(
            CompanyID, BranchID, "ProductGroupSave", UserTypeValue)
        ProductGroupEdit = get_user_type_settings(
            CompanyID, BranchID, "ProductGroupEdit", UserTypeValue)
        ProductGroupDelete = get_user_type_settings(
            CompanyID, BranchID, "ProductGroupDelete", UserTypeValue)
        BrandsView = get_user_type_settings(
            CompanyID, BranchID, "BrandsView", UserTypeValue)
        BrandsSave = get_user_type_settings(
            CompanyID, BranchID, "BrandsSave", UserTypeValue)
        BrandsEdit = get_user_type_settings(
            CompanyID, BranchID, "BrandsEdit", UserTypeValue)
        BrandsDelete = get_user_type_settings(
            CompanyID, BranchID, "BrandsDelete", UserTypeValue)
        TaxCategoriesView = get_user_type_settings(
            CompanyID, BranchID, "TaxCategoriesView", UserTypeValue)
        TaxCategoriesSave = get_user_type_settings(
            CompanyID, BranchID, "TaxCategoriesSave", UserTypeValue)
        TaxCategoriesEdit = get_user_type_settings(
            CompanyID, BranchID, "TaxCategoriesEdit", UserTypeValue)
        TaxCategoriesDelete = get_user_type_settings(
            CompanyID, BranchID, "TaxCategoriesDelete", UserTypeValue)
        PriceCategoriesView = get_user_type_settings(
            CompanyID, BranchID, "PriceCategoriesView", UserTypeValue)
        PriceCategoriesSave = get_user_type_settings(
            CompanyID, BranchID, "PriceCategoriesSave", UserTypeValue)
        PriceCategoriesEdit = get_user_type_settings(
            CompanyID, BranchID, "PriceCategoriesEdit", UserTypeValue)
        PriceCategoriesDelete = get_user_type_settings(
            CompanyID, BranchID, "PriceCategoriesDelete", UserTypeValue)
        WarehouseView = get_user_type_settings(
            CompanyID, BranchID, "WarehouseView", UserTypeValue)
        WarehouseSave = get_user_type_settings(
            CompanyID, BranchID, "WarehouseSave", UserTypeValue)
        WarehouseEdit = get_user_type_settings(
            CompanyID, BranchID, "WarehouseEdit", UserTypeValue)
        WarehouseDelete = get_user_type_settings(
            CompanyID, BranchID, "WarehouseDelete", UserTypeValue)
        ProductCategoriesView = get_user_type_settings(
            CompanyID, BranchID, "ProductCategoriesView", UserTypeValue)
        ProductCategoriesSave = get_user_type_settings(
            CompanyID, BranchID, "ProductCategoriesSave", UserTypeValue)
        ProductCategoriesEdit = get_user_type_settings(
            CompanyID, BranchID, "ProductCategoriesEdit", UserTypeValue)
        ProductCategoriesDelete = get_user_type_settings(
            CompanyID, BranchID, "ProductCategoriesDelete", UserTypeValue)
        ProductsView = get_user_type_settings(
            CompanyID, BranchID, "ProductsView", UserTypeValue)
        ProductsSave = get_user_type_settings(
            CompanyID, BranchID, "ProductsSave", UserTypeValue)
        ProductsEdit = get_user_type_settings(
            CompanyID, BranchID, "ProductsEdit", UserTypeValue)
        ProductsDelete = get_user_type_settings(
            CompanyID, BranchID, "ProductsDelete", UserTypeValue)
        RoutesView = get_user_type_settings(
            CompanyID, BranchID, "RoutesView", UserTypeValue)
        RoutesSave = get_user_type_settings(
            CompanyID, BranchID, "RoutesSave", UserTypeValue)
        RoutesEdit = get_user_type_settings(
            CompanyID, BranchID, "RoutesEdit", UserTypeValue)
        RoutesDelete = get_user_type_settings(
            CompanyID, BranchID, "RoutesDelete", UserTypeValue)
        UnitsView = get_user_type_settings(
            CompanyID, BranchID, "UnitsView", UserTypeValue)
        UnitsSave = get_user_type_settings(
            CompanyID, BranchID, "UnitsSave", UserTypeValue)
        UnitsEdit = get_user_type_settings(
            CompanyID, BranchID, "UnitsEdit", UserTypeValue)
        UnitsDelete = get_user_type_settings(
            CompanyID, BranchID, "UnitsDelete", UserTypeValue)
        # Inventory => Transactions
        PurchaseInvoicesView = get_user_type_settings(
            CompanyID, BranchID, "PurchaseInvoicesView", UserTypeValue)
        PurchaseInvoicesSave = get_user_type_settings(
            CompanyID, BranchID, "PurchaseInvoicesSave", UserTypeValue)
        PurchaseInvoicesEdit = get_user_type_settings(
            CompanyID, BranchID, "PurchaseInvoicesEdit", UserTypeValue)
        PurchaseInvoicesDelete = get_user_type_settings(
            CompanyID, BranchID, "PurchaseInvoicesDelete", UserTypeValue)
        WorkOrdersView = get_user_type_settings(
            CompanyID, BranchID, "WorkOrdersView", UserTypeValue)
        WorkOrdersSave = get_user_type_settings(
            CompanyID, BranchID, "WorkOrdersSave", UserTypeValue)
        WorkOrdersEdit = get_user_type_settings(
            CompanyID, BranchID, "WorkOrdersEdit", UserTypeValue)
        WorkOrdersDelete = get_user_type_settings(
            CompanyID, BranchID, "WorkOrdersDelete", UserTypeValue)
        PurchaseReturnsView = get_user_type_settings(
            CompanyID, BranchID, "PurchaseReturnsView", UserTypeValue)
        PurchaseReturnsSave = get_user_type_settings(
            CompanyID, BranchID, "PurchaseReturnsSave", UserTypeValue)
        PurchaseReturnsEdit = get_user_type_settings(
            CompanyID, BranchID, "PurchaseReturnsEdit", UserTypeValue)
        PurchaseReturnsDelete = get_user_type_settings(
            CompanyID, BranchID, "PurchaseReturnsDelete", UserTypeValue)
        SaleInvoicesView = get_user_type_settings(
            CompanyID, BranchID, "SaleInvoicesView", UserTypeValue)
        SaleInvoicesSave = get_user_type_settings(
            CompanyID, BranchID, "SaleInvoicesSave", UserTypeValue)
        SaleInvoicesEdit = get_user_type_settings(
            CompanyID, BranchID, "SaleInvoicesEdit", UserTypeValue)
        SaleInvoicesDelete = get_user_type_settings(
            CompanyID, BranchID, "SaleInvoicesDelete", UserTypeValue)
        SaleReturnsView = get_user_type_settings(
            CompanyID, BranchID, "SaleReturnsView", UserTypeValue)
        SaleReturnsSave = get_user_type_settings(
            CompanyID, BranchID, "SaleReturnsSave", UserTypeValue)
        SaleReturnsEdit = get_user_type_settings(
            CompanyID, BranchID, "SaleReturnsEdit", UserTypeValue)
        SaleReturnsDelete = get_user_type_settings(
            CompanyID, BranchID, "SaleReturnsDelete", UserTypeValue)
        OpeningStockView = get_user_type_settings(
            CompanyID, BranchID, "OpeningStockView", UserTypeValue)
        OpeningStockSave = get_user_type_settings(
            CompanyID, BranchID, "OpeningStockSave", UserTypeValue)
        OpeningStockEdit = get_user_type_settings(
            CompanyID, BranchID, "OpeningStockEdit", UserTypeValue)
        OpeningStockDelete = get_user_type_settings(
            CompanyID, BranchID, "OpeningStockDelete", UserTypeValue)
        StockTransferView = get_user_type_settings(
            CompanyID, BranchID, "StockTransferView", UserTypeValue)
        StockTransferSave = get_user_type_settings(
            CompanyID, BranchID, "StockTransferSave", UserTypeValue)
        StockTransferEdit = get_user_type_settings(
            CompanyID, BranchID, "StockTransferEdit", UserTypeValue)
        StockTransferDelete = get_user_type_settings(
            CompanyID, BranchID, "StockTransferDelete", UserTypeValue)
        ExcessStocksView = get_user_type_settings(
            CompanyID, BranchID, "ExcessStocksView", UserTypeValue)
        ExcessStocksSave = get_user_type_settings(
            CompanyID, BranchID, "ExcessStocksSave", UserTypeValue)
        ExcessStocksEdit = get_user_type_settings(
            CompanyID, BranchID, "ExcessStocksEdit", UserTypeValue)
        ExcessStocksDelete = get_user_type_settings(
            CompanyID, BranchID, "ExcessStocksDelete", UserTypeValue)
        ShortageStocksView = get_user_type_settings(
            CompanyID, BranchID, "ShortageStocksView", UserTypeValue)
        ShortageStocksSave = get_user_type_settings(
            CompanyID, BranchID, "ShortageStocksSave", UserTypeValue)
        ShortageStocksEdit = get_user_type_settings(
            CompanyID, BranchID, "ShortageStocksEdit", UserTypeValue)
        ShortageStocksDelete = get_user_type_settings(
            CompanyID, BranchID, "ShortageStocksDelete", UserTypeValue)
        DamageStocksView = get_user_type_settings(
            CompanyID, BranchID, "DamageStocksView", UserTypeValue)
        DamageStocksSave = get_user_type_settings(
            CompanyID, BranchID, "DamageStocksSave", UserTypeValue)
        DamageStocksEdit = get_user_type_settings(
            CompanyID, BranchID, "DamageStocksEdit", UserTypeValue)
        DamageStocksDelete = get_user_type_settings(
            CompanyID, BranchID, "DamageStocksDelete", UserTypeValue)
        UsedStocksView = get_user_type_settings(
            CompanyID, BranchID, "UsedStocksView", UserTypeValue)
        UsedStocksSave = get_user_type_settings(
            CompanyID, BranchID, "UsedStocksSave", UserTypeValue)
        UsedStocksEdit = get_user_type_settings(
            CompanyID, BranchID, "UsedStocksEdit", UserTypeValue)
        UsedStocksDelete = get_user_type_settings(
            CompanyID, BranchID, "UsedStocksDelete", UserTypeValue)
        StockAdjustmentsView = get_user_type_settings(
            CompanyID, BranchID, "StockAdjustmentsView", UserTypeValue)
        StockAdjustmentsSave = get_user_type_settings(
            CompanyID, BranchID, "StockAdjustmentsSave", UserTypeValue)
        StockAdjustmentsEdit = get_user_type_settings(
            CompanyID, BranchID, "StockAdjustmentsEdit", UserTypeValue)
        StockAdjustmentsDelete = get_user_type_settings(
            CompanyID, BranchID, "StockAdjustmentsDelete", UserTypeValue)
        SalesOrderView = get_user_type_settings(
            CompanyID, BranchID, "SalesOrderView", UserTypeValue)
        SalesOrderSave = get_user_type_settings(
            CompanyID, BranchID, "SalesOrderSave", UserTypeValue)
        SalesOrderEdit = get_user_type_settings(
            CompanyID, BranchID, "SalesOrderEdit", UserTypeValue)
        SalesOrderDelete = get_user_type_settings(
            CompanyID, BranchID, "SalesOrderDelete", UserTypeValue)

        # =====
        SalesEstimateView = get_user_type_settings(
            CompanyID, BranchID, "SalesEstimateView", UserTypeValue)
        SalesEstimateSave = get_user_type_settings(
            CompanyID, BranchID, "SalesEstimateSave", UserTypeValue)
        SalesEstimateEdit = get_user_type_settings(
            CompanyID, BranchID, "SalesEstimateEdit", UserTypeValue)
        SalesEstimateDelete = get_user_type_settings(
            CompanyID, BranchID, "SalesEstimateDelete", UserTypeValue)
        # =====

        PurchaseInvoicesDiscountLimit = 0
        PurchaseReturnsDiscountLimit = 0
        SaleInvoicesDiscountLimit = 0
        SaleReturnsDiscountLimit = 0

        if get_user_type_settings(
                CompanyID, BranchID, "PurchaseInvoicesDiscountLimit", UserTypeValue):
            PurchaseInvoicesDiscountLimit = get_user_type_settings(
                CompanyID, BranchID, "PurchaseInvoicesDiscountLimit", UserTypeValue)
        if get_user_type_settings(
                CompanyID, BranchID, "PurchaseReturnsDiscountLimit", UserTypeValue):
            PurchaseReturnsDiscountLimit = get_user_type_settings(
                CompanyID, BranchID, "PurchaseReturnsDiscountLimit", UserTypeValue)
        if get_user_type_settings(
                CompanyID, BranchID, "SaleInvoicesDiscountLimit", UserTypeValue):
            SaleInvoicesDiscountLimit = get_user_type_settings(
                CompanyID, BranchID, "SaleInvoicesDiscountLimit", UserTypeValue)
        if get_user_type_settings(
                CompanyID, BranchID, "SaleReturnsDiscountLimit", UserTypeValue):
            SaleReturnsDiscountLimit = get_user_type_settings(
                CompanyID, BranchID, "SaleReturnsDiscountLimit", UserTypeValue)
        # Inventory => Reports
        StockReportView = get_user_type_settings(
            CompanyID, BranchID, "StockReportView", UserTypeValue)
        StockReportPrint = get_user_type_settings(
            CompanyID, BranchID, "StockReportPrint", UserTypeValue)
        StockReportExport = get_user_type_settings(
            CompanyID, BranchID, "StockReportExport", UserTypeValue)
        StockValueReportView = get_user_type_settings(
            CompanyID, BranchID, "StockValueReportView", UserTypeValue)
        StockValueReportPrint = get_user_type_settings(
            CompanyID, BranchID, "StockValueReportPrint", UserTypeValue)
        StockValueReportExport = get_user_type_settings(
            CompanyID, BranchID, "StockValueReportExport", UserTypeValue)
        PurchaseReportView = get_user_type_settings(
            CompanyID, BranchID, "PurchaseReportView", UserTypeValue)
        PurchaseReportPrint = get_user_type_settings(
            CompanyID, BranchID, "PurchaseReportPrint", UserTypeValue)
        PurchaseReportExport = get_user_type_settings(
            CompanyID, BranchID, "PurchaseReportExport", UserTypeValue)
        SalesReportView = get_user_type_settings(
            CompanyID, BranchID, "SalesReportView", UserTypeValue)
        SalesReportPrint = get_user_type_settings(
            CompanyID, BranchID, "SalesReportPrint", UserTypeValue)
        SalesReportExport = get_user_type_settings(
            CompanyID, BranchID, "SalesReportExport", UserTypeValue)
        SalesIntegratedReportView = get_user_type_settings(
            CompanyID, BranchID, "SalesIntegratedReportView", UserTypeValue)
        SalesIntegratedReportPrint = get_user_type_settings(
            CompanyID, BranchID, "SalesIntegratedReportPrint", UserTypeValue)
        SalesIntegratedReportExport = get_user_type_settings(
            CompanyID, BranchID, "SalesIntegratedReportExport", UserTypeValue)
        SalesRegisterReportView = get_user_type_settings(
            CompanyID, BranchID, "SalesRegisterReportView", UserTypeValue)
        SalesRegisterReportPrint = get_user_type_settings(
            CompanyID, BranchID, "SalesRegisterReportPrint", UserTypeValue)
        SalesRegisterReportExport = get_user_type_settings(
            CompanyID, BranchID, "SalesRegisterReportExport", UserTypeValue)
        BillWiseReportView = get_user_type_settings(
            CompanyID, BranchID, "BillWiseReportView", UserTypeValue)
        BillWiseReportPrint = get_user_type_settings(
            CompanyID, BranchID, "BillWiseReportPrint", UserTypeValue)
        BillWiseReportExport = get_user_type_settings(
            CompanyID, BranchID, "BillWiseReportExport", UserTypeValue)
        ExcessStockReportView = get_user_type_settings(
            CompanyID, BranchID, "ExcessStockReportView", UserTypeValue)
        ExcessStockReportPrint = get_user_type_settings(
            CompanyID, BranchID, "ExcessStockReportPrint", UserTypeValue)
        ExcessStockReportExport = get_user_type_settings(
            CompanyID, BranchID, "ExcessStockReportExport", UserTypeValue)
        DamageStockReportView = get_user_type_settings(
            CompanyID, BranchID, "DamageStockReportView", UserTypeValue)
        DamageStockReportPrint = get_user_type_settings(
            CompanyID, BranchID, "DamageStockReportPrint", UserTypeValue)
        DamageStockReportExport = get_user_type_settings(
            CompanyID, BranchID, "DamageStockReportExport", UserTypeValue)
        UsedStockReportView = get_user_type_settings(
            CompanyID, BranchID, "UsedStockReportView", UserTypeValue)
        UsedStockReportPrint = get_user_type_settings(
            CompanyID, BranchID, "UsedStockReportPrint", UserTypeValue)
        UsedStockReportExport = get_user_type_settings(
            CompanyID, BranchID, "UsedStockReportExport", UserTypeValue)
        BatchWiseReportView = get_user_type_settings(
            CompanyID, BranchID, "BatchWiseReportView", UserTypeValue)
        BatchWiseReportPrint = get_user_type_settings(
            CompanyID, BranchID, "BatchWiseReportPrint", UserTypeValue)
        BatchWiseReportExport = get_user_type_settings(
            CompanyID, BranchID, "BatchWiseReportExport", UserTypeValue)
        # Payroll => Masters
        DepartmentsView = get_user_type_settings(
            CompanyID, BranchID, "DepartmentsView", UserTypeValue)
        DepartmentsSave = get_user_type_settings(
            CompanyID, BranchID, "DepartmentsSave", UserTypeValue)
        DepartmentsEdit = get_user_type_settings(
            CompanyID, BranchID, "DepartmentsEdit", UserTypeValue)
        DepartmentsDelete = get_user_type_settings(
            CompanyID, BranchID, "DepartmentsDelete", UserTypeValue)
        DesignationsView = get_user_type_settings(
            CompanyID, BranchID, "DesignationsView", UserTypeValue)
        DesignationsSave = get_user_type_settings(
            CompanyID, BranchID, "DesignationsSave", UserTypeValue)
        DesignationsEdit = get_user_type_settings(
            CompanyID, BranchID, "DesignationsEdit", UserTypeValue)
        DesignationsDelete = get_user_type_settings(
            CompanyID, BranchID, "DesignationsDelete", UserTypeValue)
        EmployeeView = get_user_type_settings(
            CompanyID, BranchID, "EmployeeView", UserTypeValue)
        EmployeeSave = get_user_type_settings(
            CompanyID, BranchID, "EmployeeSave", UserTypeValue)
        EmployeeEdit = get_user_type_settings(
            CompanyID, BranchID, "EmployeeEdit", UserTypeValue)
        EmployeeDelete = get_user_type_settings(
            CompanyID, BranchID, "EmployeeDelete", UserTypeValue)
        # Settings
        PrinterView = get_user_type_settings(
            CompanyID, BranchID, "PrinterView", UserTypeValue)
        BarcodeView = get_user_type_settings(
            CompanyID, BranchID, "BarcodeView", UserTypeValue)
        PrintBarcodeView = get_user_type_settings(
            CompanyID, BranchID, "PrintBarcodeView", UserTypeValue)

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
            "VATReportView": VATReportView,
            "VATReportPrint": VATReportPrint,
            "VATReportExport": VATReportExport,

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
            "SalesOrderSave": SalesOrderSave,
            "SalesOrderEdit": SalesOrderEdit,
            "SalesOrderDelete": SalesOrderDelete,
            # ===
            "SalesEstimateView": SalesEstimateView,
            "SalesEstimateSave": SalesEstimateSave,
            "SalesEstimateEdit": SalesEstimateEdit,
            "SalesEstimateDelete": SalesEstimateDelete,
            # ===
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
            User, CompanyID,
            BranchID, "Accounts_Masters", "AccountGroupView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "AccountGroupSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "AccountGroupEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "AccountGroupDelete", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "AccountLedgerView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "AccountLedgerSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "AccountLedgerEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "AccountLedgerDelete", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "BankView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "BankSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "BankEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "BankDelete", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "CustomerView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "CustomerSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "CustomerEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "CustomerDelete", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "SupplierView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "SupplierSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "SupplierEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "SupplierDelete", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "TransactionTypeView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "TransactionTypeSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "TransactionTypeEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Masters", "TransactionTypeDelete", True, UserTypeValue)

        # Accounts => Transactions
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "BankPaymentDelete", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "BankPaymentEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "BankPaymentSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "BankPaymentView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "BankReceiptDelete", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "BankReceiptEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "BankReceiptSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "BankReceiptView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "CashPaymentDelete", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "CashPaymentEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "CashPaymentSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "CashPaymentView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "CashReceiptDelete", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "CashReceiptEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "CashReceiptSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "CashReceiptView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "JournalEntryDelete", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "JournalEntryEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "JournalEntrySave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "JournalEntryView", True, UserTypeValue)

        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "CashPaymentDiscountLimit", 0, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "CashReceiptDiscountLimit", 0, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "BankPaymentLimit", 0, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Transactions", "BankReceiptLimit", 0, UserTypeValue)
        # Accounts => Reports
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "LedgerReportView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "LedgerReportPrint", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "LedgerReportExport", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "TrialBalanceView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "TrialBalancePrint", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "TrialBalanceExport", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "ProfitAndLossView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "ProfitAndLossPrint", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "ProfitAndLossExport", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "BalanceSheetView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "BalanceSheetPrint", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "BalanceSheetExport", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "DailyReportView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "DailyReportPrint", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "DailyReportExport", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "CashBookView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "CashBookPrint", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "CashBookExport", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "VATReportView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "VATReportPrint", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Accounts_Reports", "VATReportExport", True, UserTypeValue)

        # Inventory => Masters
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductGroupView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductGroupSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductGroupEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductGroupDelete", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "BrandsView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "BrandsSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "BrandsEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "BrandsDelete", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "TaxCategoriesView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "TaxCategoriesSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "TaxCategoriesEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "TaxCategoriesDelete", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "PriceCategoriesView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "PriceCategoriesSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "PriceCategoriesEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "PriceCategoriesDelete", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "WarehouseView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "WarehouseSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "WarehouseEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "WarehouseDelete", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductCategoriesView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductCategoriesSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductCategoriesEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductCategoriesDelete", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductsView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductsSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductsEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "ProductsDelete", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "RoutesView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "RoutesSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "RoutesEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "RoutesDelete", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "UnitsView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "UnitsSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "UnitsEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Masters", "UnitsDelete", True, UserTypeValue)

        # Inventory => Transaction
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "PurchaseInvoicesView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "PurchaseInvoicesSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "PurchaseInvoicesEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "PurchaseInvoicesDelete", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "WorkOrdersView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "WorkOrdersSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "WorkOrdersEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "WorkOrdersDelete", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "PurchaseReturnsView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "PurchaseReturnsSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "PurchaseReturnsEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "PurchaseReturnsDelete", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SaleInvoicesView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SaleInvoicesSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SaleInvoicesEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SaleInvoicesDelete", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SaleReturnsView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SaleReturnsSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SaleReturnsEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SaleReturnsDelete", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "OpeningStockView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "OpeningStockSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "OpeningStockEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "OpeningStockDelete", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "StockTransferView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "StockTransferSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "StockTransferEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "StockTransferDelete", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "ExcessStocksView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "ExcessStocksSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "ExcessStocksEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "ExcessStocksDelete", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "ShortageStocksView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "ShortageStocksSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "ShortageStocksEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "ShortageStocksDelete", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "DamageStocksView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "DamageStocksSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "DamageStocksEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "DamageStocksDelete", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "UsedStocksView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "UsedStocksSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "UsedStocksEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "UsedStocksDelete", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "StockAdjustmentsView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "StockAdjustmentsSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "StockAdjustmentsEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "StockAdjustmentsDelete", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SalesOrderView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SalesOrderSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SalesOrderEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SalesOrderDelete", True, UserTypeValue)

        # =====
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SalesEstimateView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SalesEstimateSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SalesEstimateEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SalesEstimateDelete", True, UserTypeValue)
        # =====

        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "PurchaseInvoicesDiscountLimit", 0, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "PurchaseReturnsDiscountLimit", 0, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SaleInvoicesDiscountLimit", 0, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Transactions", "SaleReturnsDiscountLimit", 0, UserTypeValue)
        # Inventory => Reports
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "StockReportView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "StockReportPrint", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "StockReportExport", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "StockValueReportView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "StockValueReportPrint", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "StockValueReportExport", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "PurchaseReportView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "PurchaseReportPrint", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "PurchaseReportExport", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "SalesReportView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "SalesReportPrint", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "SalesReportExport", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "SalesIntegratedReportView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "SalesIntegratedReportPrint", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "SalesIntegratedReportExport", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "SalesRegisterReportView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "SalesRegisterReportPrint", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "SalesRegisterReportExport", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "BillWiseReportView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "BillWiseReportPrint", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "BillWiseReportExport", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "ExcessStockReportView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "ExcessStockReportPrint", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "ExcessStockReportExport", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "DamageStockReportView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "DamageStockReportPrint", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "DamageStockReportExport", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "UsedStockReportView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "UsedStockReportPrint", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "UsedStockReportExport", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "BatchWiseReportView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "BatchWiseReportPrint", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Inventory_Reports", "BatchWiseReportExport", True, UserTypeValue)
        # Payroll => Masters
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "DepartmentsView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "DepartmentsSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "DepartmentsEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "DepartmentsDelete", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "DesignationsView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "DesignationsSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "DesignationsEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "DesignationsDelete", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "EmployeeView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "EmployeeSave", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "EmployeeEdit", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Payroll_Masters", "EmployeeDelete", True, UserTypeValue)

        # Settings
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Settings", "PrinterView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Settings", "BarcodeView", True, UserTypeValue)
        create_or_update_user_type_settings(
            User, CompanyID,
            BranchID, "Settings", "PrintBarcodeView", True, UserTypeValue)

        # return HttpResponse(reverse('api_v5_settings:user_type_settings_list'))
        response_data = {
            "StatusCode": 6000,
            "message": "success"
        }
        return Response(response_data, status=status.HTTP_200_OK)
