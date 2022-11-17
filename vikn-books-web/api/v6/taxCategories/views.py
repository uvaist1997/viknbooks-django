from brands.models import TaxCategory, TaxCategory_Log, POSHoldDetails, PurchaseMaster, PurchaseOrderDetails,\
    PurchaseReturnMaster, SalesMaster, SalesOrderDetails, SalesReturnMaster, Product, TaxType, GeneralSettings,\
    PurchaseOrderMaster,SalesOrderMaster
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v6.taxCategories.serializers import TaxCategorySerializer, TaxCategoryRestSerializer, ListSerializerTaxType, TaxTypeSerializer, ListTaxTypeSerializer
from api.v6.brands.serializers import ListSerializer
from api.v6.taxCategories.functions import generate_serializer_errors
from rest_framework import status
from api.v6.taxCategories.functions import get_auto_id
import datetime
from main.functions import get_company, activity_log
from api.v6.ledgerPosting.functions import convertOrderdDict


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_taxCategory(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    serialized = TaxCategorySerializer(data=request.data)

    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        TaxName = serialized.data['TaxName']
        TaxType = serialized.data['TaxType']
        PurchaseTax = serialized.data['PurchaseTax']
        SalesTax = serialized.data['SalesTax']
        Inclusive = serialized.data['Inclusive']

        Action = "A"

        if TaxType == "VAT":
            TaxType = 1

        elif TaxType == "GST":
            TaxType = 2

        elif TaxType == "TAX1":
            TaxType = 3

        elif TaxType == "TAX2":
            TaxType = 4

        elif TaxType == "TAX3":
            TaxType = 5
        elif TaxType == "None":
            TaxType = 6

        TaxID = get_auto_id(TaxCategory, BranchID, CompanyID)

        is_nameExist = False

        TaxNameLow = TaxName.lower()

        taxCategories = TaxCategory.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID)

        for taxCategory in taxCategories:
            tax_name = taxCategory.TaxName

            taxName = tax_name.lower()

            if TaxNameLow == taxName:
                is_nameExist = True

        if not is_nameExist:

            # serialized.save(UnitID=UnitID,CreatedDate=today,ModifiedDate=today)
            TaxCategory.objects.create(
                TaxID=TaxID,
                BranchID=BranchID,
                TaxName=TaxName,
                TaxType=TaxType,
                PurchaseTax=PurchaseTax,
                SalesTax=SalesTax,
                Inclusive=Inclusive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID
            )

            TaxCategory_Log.objects.create(
                BranchID=BranchID,
                TransactionID=TaxID,
                TaxName=TaxName,
                TaxType=TaxType,
                PurchaseTax=PurchaseTax,
                SalesTax=SalesTax,
                Inclusive=Inclusive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID
            )

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'TaxCategory',
                         'Create', 'TaxCategory created successfully.', 'TaxCategory saved successfully.')

            data = {"TaxID": TaxID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'TaxCategory',
                         'Create', 'TaxCategory created Failed.', 'TaxCategory Name Already Exist.')
            response_data = {
                "StatusCode": 6001,
                "message": "TaxCategory Name Already Exist!!!"
            }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'TaxCategory', 'Create',
                     'TaxCategory created Failed.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def edit_taxCategory(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = TaxCategorySerializer(data=request.data)
    instance = TaxCategory.objects.get(pk=pk, CompanyID=CompanyID)

    BranchID = instance.BranchID
    TaxID = instance.TaxID
    instanceTaxName = instance.TaxName

    if serialized.is_valid():

        TaxName = serialized.data['TaxName']
        TaxType = serialized.data['TaxType']
        PurchaseTax = serialized.data['PurchaseTax']
        SalesTax = serialized.data['SalesTax']
        Inclusive = serialized.data['Inclusive']

        Action = "M"

        if TaxType == "VAT":
            TaxType = 1

        elif TaxType == "GST":
            TaxType = 2

        elif TaxType == "TAX1":
            TaxType = 3

        elif TaxType == "TAX2":
            TaxType = 4

        elif TaxType == "TAX3":
            TaxType = 5
        elif TaxType == "None":
            TaxType = 6

        is_nameExist = False
        tax_ok = False

        TaxNameLow = TaxName.lower()

        taxCategories = TaxCategory.objects.filter(BranchID=BranchID)

        for taxCategory in taxCategories:
            tax_name = taxCategory.TaxName

            taxName = tax_name.lower()

            if TaxNameLow == taxName:
                is_nameExist = True

            if instanceTaxName.lower() == TaxNameLow:

                tax_ok = True

        if tax_ok:

            instance.TaxName = TaxName
            instance.TaxType = TaxType
            instance.PurchaseTax = PurchaseTax
            instance.SalesTax = SalesTax
            instance.Inclusive = Inclusive
            instance.Action = Action
            instance.CreatedUserID = CreatedUserID
            instance.UpdatedDate = today
            instance.save()

            TaxCategory_Log.objects.create(
                BranchID=BranchID,
                TransactionID=TaxID,
                TaxName=TaxName,
                TaxType=TaxType,
                PurchaseTax=PurchaseTax,
                SalesTax=SalesTax,
                Inclusive=Inclusive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID
            )

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'TaxCategory',
                         'Edit', 'TaxCategory updated Successfully.', "TaxCategory updated Successfully.")

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:

            if is_nameExist:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'TaxCategory', 'Edit',
                             'TaxCategory updated Failed.', "TaxCategory Name Already exist with this Branch")
                response_data = {
                    "StatusCode": 6001,
                    "message": "TaxCategory Name Already exist with this Branch"
                }
                return Response(response_data, status=status.HTTP_200_OK)

            else:
                instance.TaxName = TaxName
                instance.TaxType = TaxType
                instance.PurchaseTax = PurchaseTax
                instance.SalesTax = SalesTax
                instance.Action = Action
                instance.CreatedUserID = CreatedUserID
                instance.UpdatedDate = today
                instance.save()

                TaxCategory_Log.objects.create(
                    BranchID=BranchID,
                    TransactionID=TaxID,
                    TaxName=TaxName,
                    TaxType=TaxType,
                    PurchaseTax=PurchaseTax,
                    SalesTax=SalesTax,
                    Inclusive=Inclusive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID
                )

                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'TaxCategory',
                             'Edit', 'TaxCategory updated Successfully.', "TaxCategory updated Successfully.")

                response_data = {
                    "StatusCode": 6000,
                    "data": serialized.data
                }

                return Response(response_data, status=status.HTTP_200_OK)

    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'TaxCategory', 'Edit',
                     'TaxCategory updated Failed.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def taxCategories(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if TaxCategory.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():

            check_VAT = GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="VAT").SettingsValue
            check_GST = GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="GST").SettingsValue
            check_TAX1 = GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="TAX1").SettingsValue
            check_TAX2 = GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="TAX2").SettingsValue
            check_TAX3 = GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="TAX3").SettingsValue

            checkTax = []

            if check_VAT == 'false':
                checkTax.append('1')
            if check_GST == 'false':
                checkTax.append('2')
            if check_TAX1 == 'false':
                checkTax.append('3')
            if check_TAX2 == 'false':
                checkTax.append('4')
            if check_TAX3 == 'false':
                checkTax.append('5')

            instances = TaxCategory.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID).exclude(TaxType__in=checkTax)
            serialized = TaxCategoryRestSerializer(instances, many=True, context={
                                                   "CompanyID": CompanyID, "PriceRounding": PriceRounding})

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'TaxCategory',
                         'List', 'TaxCategory List Viewed Successfully.', "TaxCategory List Viewed Successfully")
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'TaxCategory',
                         'List', 'TaxCategory List Viewed Failed.', "Tax Category Not Found in this Branch")

            response_data = {
                "StatusCode": 6001,
                "message": "Tax Category Not Found in this Branch!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def taxCategory(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    instance = None

    if TaxCategory.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = TaxCategory.objects.get(pk=pk, CompanyID=CompanyID)

        serialized = TaxCategoryRestSerializer(
            instance, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding})
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'TaxCategory', 'View',
                     'TaxCategory Single Viewed Successfully.', "TaxCategory Single Viewed Successfully.")

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'TaxCategory',
                     'View', 'TaxCategory Single Viewed Failed.', "TaxCategory Not Found")
        response_data = {
            "StatusCode": 6001,
            "message": "TaxCategory Not Found"
        }
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_taxCategory(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    instance = None
    posholdDetails_exist = None
    purchaseDetails_exist = None
    purchaseOrderDetails_exist = None
    purchaseReturnDetails_exist = None
    salesDetails_exist = None
    salesOrderDetails_exist = None
    salesReturnDetails_exist = None
    if pk == "1":
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'TaxCategory',
                     'Delete', 'TaxCategory Deleted Failed.', "User Tried to Delete Default TaxCategory")
        response_data = {
            "StatusCode": 6001,
            "message": "You Can't Delete this TaxCategory!!!"
        }
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        if TaxCategory.objects.filter(pk=pk, CompanyID=CompanyID).exists():
            print("><.................../'''''''''''''''''''''''''~~~~~<>")
            instance = TaxCategory.objects.get(pk=pk, CompanyID=CompanyID)
            BranchID = instance.BranchID
            TaxID = instance.TaxID
            TaxName = instance.TaxName
            TaxType = instance.TaxType
            PurchaseTax = instance.PurchaseTax
            SalesTax = instance.SalesTax
            Inclusive = instance.Inclusive
            Action = "D"

            is_productExist = False
            if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VatID=TaxID).exists():
                is_productExist = True
            elif Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, GST=TaxID).exists():
                is_productExist = True
            elif Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Tax1=TaxID).exists():
                is_productExist = True
            elif Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Tax2=TaxID).exists():
                is_productExist = True
            elif Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Tax3=TaxID).exists():
                is_productExist = True

            posholdDetails_exist = POSHoldDetails.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, TaxID=TaxID).exists()
            purchaseDetails_exist = PurchaseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, TaxID=TaxID).exists()
            purchaseOrderDetails_exist = PurchaseOrderMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, TaxID=TaxID).exists()
            purchaseReturnDetails_exist = PurchaseReturnMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, TaxID=TaxID).exists()
            salesDetails_exist = SalesMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, TaxID=TaxID).exists()
            salesOrderDetails_exist = SalesOrderMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, TaxID=TaxID).exists()
            salesReturnDetails_exist = SalesReturnMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, TaxID=TaxID).exists()

            if not posholdDetails_exist and not purchaseDetails_exist and not purchaseOrderDetails_exist and not purchaseReturnDetails_exist and not salesDetails_exist and not salesOrderDetails_exist and not salesReturnDetails_exist and is_productExist == False:
                instance.delete()

                TaxCategory_Log.objects.create(
                    BranchID=BranchID,
                    TransactionID=TaxID,
                    TaxName=TaxName,
                    TaxType=TaxType,
                    PurchaseTax=PurchaseTax,
                    SalesTax=SalesTax,
                    Inclusive=Inclusive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID
                )

                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'TaxCategory',
                             'Delete', 'TaxCategory Deleted Successfully.', "TaxCategory Deleted Successfully")
                response_data = {
                    "StatusCode": 6000,
                    "title": "Success",
                    "message": "TaxCategory Deleted Successfully!"
                }
            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'TaxCategory', 'Delete',
                             'TaxCategory Deleted Failed.', "can't Delete this TaxCategory,this TaxID is using somewhere")
                response_data = {
                    "StatusCode": 6001,
                    "title": "Failed",
                    "message": "You Cant Delete this TaxCategory,this TaxID is using somewhere!!"
                }
        else:
            response_data = {
                "StatusCode": 6001,
                "title": "Failed",
                "message": "TaxCategory Not Fount!"
            }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def taxListByType(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    serialized1 = ListSerializerTaxType(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']
        TaxType = serialized1.data['TaxType']

        taxArr = [6, TaxType]

        if TaxCategory.objects.filter(CompanyID=CompanyID, BranchID=BranchID, TaxType__in=taxArr).exists():
            TaxCategoryInstance = TaxCategory.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, TaxType__in=taxArr)

            serialized = TaxTypeSerializer(TaxCategoryInstance, many=True)

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "TaxCategory Not Found under this Tax Type!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID or MasterName You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def get_tax_details(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    BranchID = data['BranchID']
    ProductTaxID = data['ProductTaxID']
    

    GST_PurchaseTax = 0
    GST_SalesTax = 0
    Vat_SalesTax = 0
    Vat_PurchaseTax = 0
    GST_Inclusive = False
    Vat_Inclusive = False

    if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=ProductTaxID, BranchID=BranchID).exists():
        tax = TaxCategory.objects.get(
            CompanyID=CompanyID, TaxID=ProductTaxID, BranchID=BranchID)
        GST_PurchaseTax = tax.PurchaseTax
        GST_SalesTax = tax.SalesTax
        GST_Inclusive = tax.Inclusive


    if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=ProductTaxID, BranchID=BranchID).exists():
        tax = TaxCategory.objects.get(
            CompanyID=CompanyID, TaxID=ProductTaxID, BranchID=BranchID)
        Vat_PurchaseTax = tax.PurchaseTax
        Vat_SalesTax = tax.SalesTax
        Vat_Inclusive = tax.Inclusive
    
    response_data = {
        "StatusCode": 6000,
        "GST_PurchaseTax": float(GST_PurchaseTax),
        "GST_SalesTax": float(GST_SalesTax),
        "Vat_PurchaseTax": float(Vat_PurchaseTax),
        "Vat_SalesTax": float(Vat_SalesTax),
        "GST_Inclusive": GST_Inclusive,
        "Vat_Inclusive": Vat_Inclusive,
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def listTaxType(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if TaxType.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            check_VAT = GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="VAT").SettingsValue
            check_GST = GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="GST").SettingsValue
            check_TAX1 = GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="TAX1").SettingsValue
            check_TAX2 = GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="TAX2").SettingsValue
            check_TAX3 = GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="TAX3").SettingsValue

            checkTax = []

            if check_VAT == 'false':
                checkTax.append('VAT')
            if check_GST == 'false':
                checkTax.append('GST')
            if check_TAX1 == 'false':
                checkTax.append('TAX1')
            if check_TAX2 == 'false':
                checkTax.append('TAX2')
            if check_TAX3 == 'false':
                checkTax.append('TAX3')

            instances = TaxType.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID).exclude(TaxTypeName__in=checkTax)
            serialized = ListTaxTypeSerializer(instances, many=True)

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Tax Type Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)
