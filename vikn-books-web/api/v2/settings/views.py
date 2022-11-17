from brands.models import Settings, Settings_Log, PrintSettings, BarcodeSettings, Language
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v2.settings.serializers import SettingsSerializer, SettingsRestSerializer, PrintSettingsSerializer, BarcodeSettingsSerializer, LanguageSerializer
from api.v2.brands.serializers import ListSerializer
from api.v2.settings.functions import generate_serializer_errors
from rest_framework import status
from api.v2.settings.functions import get_auto_id
from main.functions import get_company, activity_log
import datetime



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_settings(request):
    today = datetime.datetime.now()
    serialized = SettingsSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        PriceList = serialized.data['PriceList']
        GroupName = serialized.data['GroupName']
        SettingsType = serialized.data['SettingsType']
        SettingsValue = serialized.data['SettingsValue']
        CreatedUserID = serialized.data['CreatedUserID']
        
        Action = "A"

        SettingsID = get_auto_id(Settings,BranchID)

        Settings.objects.create(
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

        Settings_Log.objects.create(
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

        data = {"SettingsID" : SettingsID}
        data.update(serialized.data)
        response_data = {
            "StatusCode" : 6000,
            "data" : data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def edit_settings(request,pk):
    today = datetime.datetime.now()
    serialized = SettingsSerializer(data=request.data)
    instance = None
    if Settings.objects.filter(pk=pk).exists():
        instance = Settings.objects.get(pk=pk)

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

            Settings_Log.objects.create(
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

            data = {"SettingsID" : SettingsID}
            data.update(serialized.data)
            response_data = {
                "StatusCode" : 6000,
                "data" : data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode" : 6001,
                "message" : generate_serializer_errors(serialized._errors)
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Settings Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_settings(request):
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if Settings.objects.filter(BranchID=BranchID).exists():

            instances = Settings.objects.filter(BranchID=BranchID)

            serialized = SettingsRestSerializer(instances,many=True)

            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
            "StatusCode" : 6001,
            "message" : "Settings Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def settings(request,pk):
    instance = None
    if Settings.objects.filter(pk=pk).exists():
        instance = Settings.objects.get(pk=pk)
    if instance:
        serialized = SettingsRestSerializer(instance)
        response_data = {
            "StatusCode" : 6000,
            "data" : serialized.data
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Settings Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_settings(request,pk):
    today = datetime.datetime.now()
    instance = None
    if Settings.objects.filter(pk=pk).exists():
        instance = Settings.objects.get(pk=pk)
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

        Settings_Log.objects.create(
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
            "StatusCode" : 6000,
            "message" : "Settings Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Settings Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def print_settings(request):
    today = datetime.datetime.now()
    serialized = PrintSettingsSerializer(data=request.data)
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
        Action = "A"
        print_settings_id = None
        if PrintSettings.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
            print_settings_id = PrintSettings.objects.get(CompanyID=CompanyID,BranchID=BranchID).pk
            PrintSettings.objects.filter(CompanyID=CompanyID,BranchID=BranchID).update(
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
                Action=Action,
                BranchID=BranchID,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                CompanyID=CompanyID,
                )
        else:
            PrintSettings.objects.filter(CompanyID=CompanyID,BranchID=BranchID).create(
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
                Action=Action,
                BranchID=BranchID,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                CompanyID=CompanyID,
                )
            print_settings_id = PrintSettings.objects.get(CompanyID=CompanyID,BranchID=BranchID).pk
        print(print_settings)
        print("hellllllllllllllllo")
        response_data = {
            "StatusCode" : 6000,
            "data" : serialized.data,
            "print_settings_id" : print_settings_id
        }
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : generate_serializer_errors(serialized._errors)
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
#     if PrintSettings.objects.filter(pk=pk).exists():
#         instance = PrintSettings.objects.get(pk=pk)
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
    serialized = BarcodeSettingsSerializer(data=request.data)
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
        if BarcodeSettings.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
            print_settings_id = BarcodeSettings.objects.get(CompanyID=CompanyID,BranchID=BranchID).pk
            BarcodeSettings.objects.filter(CompanyID=CompanyID,BranchID=BranchID).update(
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
            BarcodeSettings.objects.filter(CompanyID=CompanyID,BranchID=BranchID).create(
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
            "StatusCode" : 6000,
            "data" : serialized.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : generate_serializer_errors(serialized._errors)
        }
        return Response(response_data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def language(request):
    today = datetime.datetime.now()
    serialized = LanguageSerializer(data=request.data)
    if serialized.is_valid():
        data = request.data
        CreatedUserID = data['CreatedUserID']
        language = data['language']
      
        Action = "A"
        print_settings_id = None
        if Language.objects.filter(CreatedUserID=CreatedUserID).exists():
            Language.objects.filter(CreatedUserID=CreatedUserID).update(
                language=language,
                CreatedUserID=CreatedUserID,
                )
        else:
            Language.objects.filter(CreatedUserID=CreatedUserID).create(
                language=language,
                CreatedUserID=CreatedUserID,
                )
        response_data = {
            "StatusCode" : 6000,
            "data" : serialized.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : generate_serializer_errors(serialized._errors)
        }
        return Response(response_data, status=status.HTTP_200_OK)