from brands.models import LoyaltyCustomer, AccountLedger, AccountGroup, LoyaltyCustomer_Log, TransactionTypes, MasterType
from api.v10.transactionTypes.serializers import TransactionTypesSerializer, TransactionTypesRestSerializer, ListSerializerByMasterName
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes,authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from api.v10.loyaltyCustomer.serializers import LoyaltyCustomerSerializer, LoyaltyCustomerRestSerializer
from api.v10.brands.serializers import ListSerializer
from api.v10.loyaltyCustomer.functions import generate_serializer_errors
from rest_framework import status
from api.v10.loyaltyCustomer.functions import get_auto_id, get_auto_DepartmentID
from main.functions import get_company, activity_log
import datetime
from api.v10.accountLedgers.serializers import AccountLedgerSerializer, AccountLedgerRestSerializer, LedgerReportSerializer, AccountLedgerListSerializer
from api.v10.transactionTypes.functions import get_auto_id as trans_type_get_auto_id


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def create_loyaltyCustomer(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = LoyaltyCustomerSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        MobileNo = serialized.data['MobileNo']
        FirstName = serialized.data['FirstName']
        LastName = serialized.data['LastName']
        Address1 = serialized.data['Address1']
        Address2 = serialized.data['Address2']
        CardNumber = serialized.data['CardNumber']
        CardStatusID = data['CardStatusID']
        CardTypeID = data['CardTypeID']
        CardStatusName = data['CardStatusName']
        CardTypeName = data['CardTypeName']

        Action = 'A'
        MobileNo_ok = False
        CardNumber_ok = False
        LoyaltyCustomerID = get_auto_id(LoyaltyCustomer, BranchID, CompanyID)
        loyalty_instances = LoyaltyCustomer.objects.filter(BranchID=BranchID, CompanyID=CompanyID)
        if loyalty_instances.filter(MobileNo=MobileNo).exists():
            MobileNo_ok = True
        if loyalty_instances.filter(CardNumber=CardNumber).exists():
            CardNumber_ok = True
        is_firstnameExist = False

        sundry_debtor_instance = None
        try:
            AccountLedgerID = serialized.data['AccountLedgerID']
        except:
            AccountLedgerID = None
        if AccountLedger.objects.filter(pk=AccountLedgerID).exists() and not AccountLedgerID == None:
            sundry_debtor_instance = AccountLedger.objects.get(
                pk=AccountLedgerID)
        print(sundry_debtor_instance,"sundry_debtor_instance")

        if not MobileNo_ok:
            if not CardNumber_ok:
                a = loyalty_instances.filter(AccountLedgerID=sundry_debtor_instance).exclude(AccountLedgerID=None)
                for i in a:
                    print(i.AccountLedgerID,'loyalty_instances.filter(AccountLedgerID=sundry_debtor_instance)')
                if not loyalty_instances.filter(AccountLedgerID=sundry_debtor_instance).exclude(AccountLedgerID=None).exists():
                    card_status_instance = None
                    card_type_instance = None
                    # if TransactionTypes.objects.filter(pk=CardStatusID).exists():
                    #     card_status_instance = TransactionTypes.objects.get(
                    #         pk=CardStatusID)
                    # if TransactionTypes.objects.filter(pk=CardTypeID).exists():
                    #     card_type_instance = TransactionTypes.objects.get(
                    #         pk=CardTypeID)
                    card_status = MasterType.objects.get(Name="Loyalty Card Status",CompanyID=CompanyID, BranchID=BranchID).MasterTypeID
                    card_type = MasterType.objects.get(Name="Loyalty Card Type",CompanyID=CompanyID, BranchID=BranchID).MasterTypeID
                    try:
                        card_status_instance = TransactionTypes.objects.get(id=CardStatusID)
                    except:
                        if TransactionTypes.objects.filter(Name__iexact=CardStatusName,MasterTypeID=card_status,CompanyID=CompanyID).exists():
                            card_status_instance = TransactionTypes.objects.get(Name__iexact=CardStatusName,MasterTypeID=card_status,CompanyID=CompanyID)
                        else:
                            TransactionTypesID = trans_type_get_auto_id(TransactionTypes, BranchID, CompanyID)                          
                            card_status_instance = TransactionTypes.objects.create(
                                MasterTypeID=card_status,
                                CompanyID=CompanyID,
                                BranchID=BranchID,
                                CreatedUserID=request.user.id,
                                Action="A",
                                CreatedDate=today,
                                Name=CardStatusName.title(),
                                TransactionTypesID=TransactionTypesID
                                )


                    try:
                        card_type_instance = TransactionTypes.objects.get(id=CardTypeID)
                    except:
                        if TransactionTypes.objects.filter(Name__iexact=CardTypeName,MasterTypeID=card_type,CompanyID=CompanyID).exists():
                            card_type_instance = TransactionTypes.objects.get(Name__iexact=CardTypeName,MasterTypeID=card_type,CompanyID=CompanyID)
                        else:
                            TransactionTypesID = trans_type_get_auto_id(TransactionTypes, BranchID, CompanyID)                          
                            card_type_instance = TransactionTypes.objects.create(
                                MasterTypeID=card_type,
                                CompanyID=CompanyID,
                                BranchID=BranchID,
                                CreatedUserID=request.user.id
                                ,Action="A",
                                CreatedDate=today,
                                Name=CardTypeName.title(),
                                TransactionTypesID=TransactionTypesID

                                )

                    if not is_firstnameExist:
                        # serialized.save(BrandID=BrandID,CreatedDate=today,ModifiedDate=today)
                        loyaltyinstance = LoyaltyCustomer.objects.create(
                            LoyaltyCustomerID=LoyaltyCustomerID,
                            BranchID=BranchID,

                            MobileNo=MobileNo,
                            FirstName=FirstName,
                            LastName=LastName,
                            Address1=Address1,
                            Address2=Address2,
                            CardNumber=CardNumber,
                            CardStatusID=card_status_instance,
                            CardTypeID=card_type_instance,
                            AccountLedgerID=sundry_debtor_instance,

                            CreatedDate=today,
                            UpdatedDate=today,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )

                        LoyaltyCustomer_Log.objects.create(
                            BranchID=BranchID,
                            LoyaltyCustomerID=LoyaltyCustomerID,

                            MobileNo=MobileNo,
                            FirstName=FirstName,
                            LastName=LastName,
                            Address1=Address1,
                            Address2=Address2,
                            CardNumber=CardNumber,
                            CardStatusID=card_status_instance,
                            CardTypeID=card_type_instance,
                            AccountLedgerID=sundry_debtor_instance,

                            CreatedDate=today,
                            UpdatedDate=today,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )

                        data = {"LoyaltyCustomerID": LoyaltyCustomerID}
                        data.update(serialized.data)
                        response_data = {
                            "StatusCode": 6000,
                            "LoyaltyCustomerID": loyaltyinstance.LoyaltyCustomerID,
                            "data": data
                        }

                        return Response(response_data, status=status.HTTP_200_OK)
                else:
                    response_data = {
                        "StatusCode": 6001,
                        "message": "This customer is already exist!!!"
                    }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "Card Number  Exists"
                }

                return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Mobile Number exists"
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
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def edit_loyaltyCustomer(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = LoyaltyCustomerSerializer(data=request.data)
    instance = LoyaltyCustomer.objects.get(pk=pk, CompanyID=CompanyID)
    BranchID = instance.BranchID
    LoyaltyCustomerID = instance.LoyaltyCustomerID
    if serialized.is_valid():
        MobileNo = serialized.data['MobileNo']
        FirstName = serialized.data['FirstName']
        LastName = serialized.data['LastName']
        Address1 = serialized.data['Address1']
        Address2 = serialized.data['Address2']
        AccountLedgerID = serialized.data['AccountLedgerID']
        CardNumber = serialized.data['CardNumber']
        CardTypeID = data['CardTypeID']
        CardStatusID = data['CardStatusID']
        CardStatusName = data['CardStatusName']
        CardTypeName = data['CardTypeName']

        Action = 'M'
        is_Exist = False
        LoyaltyCustomer_ok = False
        if LoyaltyCustomer.objects.filter(BranchID=BranchID, CompanyID=CompanyID, MobileNo=MobileNo).exclude(id=pk).exists():
            LoyaltyCustomer_ok = True
        if LoyaltyCustomer.objects.filter(BranchID=BranchID, CompanyID=CompanyID, AccountLedgerID__pk=AccountLedgerID).exclude(id=pk).exists():
            is_Exist = True
        # NameLow = Name.lower()

        # LoyaltyCustomers = LoyaltyCustomer.objects.filter(
        #     BranchID=BranchID, CompanyID=CompanyID)

        # for LoyaltyCustomer in LoyaltyCustomers:
        #     name = LoyaltyCustomer.Name

        #     LoyaltyCustomerName = name.lower()

        #     if NameLow == LoyaltyCustomerName:
        #         is_nameExist = True

        #     if instancename.lower() == NameLow:

        #         LoyaltyCustomer_ok = True
        if not is_Exist:
            if not LoyaltyCustomer_ok:
                card_status_instance = None
                card_type_instance = None
                
                card_status = MasterType.objects.get(Name="Loyalty Card Status",CompanyID=CompanyID, BranchID=BranchID).MasterTypeID
                card_type = MasterType.objects.get(Name="Loyalty Card Type",CompanyID=CompanyID, BranchID=BranchID).MasterTypeID
                try:
                    card_status_instance = TransactionTypes.objects.get(id=CardStatusID)
                except:
                    if TransactionTypes.objects.filter(Name__iexact=CardStatusName,MasterTypeID=card_status,CompanyID=CompanyID).exists():
                        card_status_instance = TransactionTypes.objects.get(Name__iexact=CardStatusName,MasterTypeID=card_status,CompanyID=CompanyID)
                    else:
                        TransactionTypesID = trans_type_get_auto_id(TransactionTypes, BranchID, CompanyID)                          
                        card_status_instance = TransactionTypes.objects.create(
                            MasterTypeID=card_status,
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            CreatedUserID=request.user.id,
                            Action="A",
                            CreatedDate=today,
                            Name=CardStatusName.title(),
                            TransactionTypesID=TransactionTypesID
                            )


                try:
                    card_type_instance = TransactionTypes.objects.get(id=CardTypeID)
                except:
                    if TransactionTypes.objects.filter(Name__iexact=CardTypeName,MasterTypeID=card_type,CompanyID=CompanyID).exists():
                        card_type_instance = TransactionTypes.objects.get(Name__iexact=CardTypeName,MasterTypeID=card_type,CompanyID=CompanyID)
                    else:
                        TransactionTypesID = trans_type_get_auto_id(TransactionTypes, BranchID, CompanyID)                          
                        card_type_instance = TransactionTypes.objects.create(
                            MasterTypeID=card_type,
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            CreatedUserID=request.user.id
                            ,Action="A",
                            CreatedDate=today,
                            Name=CardTypeName.title(),
                            TransactionTypesID=TransactionTypesID

                            )

                sundry_debtor_instance = None

                try:
                    AccountLedgerID = serialized.data['AccountLedgerID']
                    print("KAYARYUM")
                except:
                    print("NONE")
                    AccountLedgerID = None
                if AccountLedger.objects.filter(pk=AccountLedgerID).exists():
                    sundry_debtor_instance = AccountLedger.objects.get(
                        pk=AccountLedgerID)
                    instance.AccountLedgerID = sundry_debtor_instance

                instance.MobileNo = MobileNo
                instance.FirstName = FirstName
                instance.LastName = LastName
                instance.Address1 = Address1
                instance.Address2 = Address2
                instance.CardNumber = CardNumber
                instance.CardStatusID = card_status_instance
                instance.CardTypeID = card_type_instance

                instance.Action = Action
                instance.UpdatedDate = today
                instance.CreatedUserID = CreatedUserID
                instance.save()

                LoyaltyCustomer_Log.objects.create(
                    BranchID=BranchID,

                    LoyaltyCustomerID=LoyaltyCustomerID,

                    MobileNo=MobileNo,
                    FirstName=FirstName,
                    LastName=LastName,
                    Address1=Address1,
                    Address2=Address2,
                    AccountLedgerID=sundry_debtor_instance,
                    CardNumber=CardNumber,
                    CardStatusID=card_status_instance,
                    CardTypeID=card_type_instance,

                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                )

                data = {"LoyaltyCustomerID": LoyaltyCustomerID}
                data.update(serialized.data)
                response_data = {
                    "StatusCode": 6000,
                    "data": data
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "Mobile Num Exists"
                }

                return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "This customer is already exist!!!"
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
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def loyaltyCustomers(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if LoyaltyCustomer.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
            instances = LoyaltyCustomer.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID)
            serialized = LoyaltyCustomerRestSerializer(instances, many=True)
            print(serialized.data,"==========================================")
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Loyalty Customer Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def loyaltyCustomer(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instance = None
    if LoyaltyCustomer.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = LoyaltyCustomer.objects.get(pk=pk, CompanyID=CompanyID)
        serialized = LoyaltyCustomerRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Loyalty Customer Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def delete_loyaltyCustomer(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if LoyaltyCustomer.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = LoyaltyCustomer.objects.get(pk=pk, CompanyID=CompanyID)
        BranchID = instance.BranchID
        LoyaltyCustomerID = instance.LoyaltyCustomerID

        Action = "D"

        instance.delete()

        LoyaltyCustomer_Log.objects.create(
            BranchID=BranchID,

            LoyaltyCustomerID=LoyaltyCustomerID,
            MobileNo=instance.MobileNo,
            FirstName=instance.FirstName,
            LastName=instance.LastName,
            Address1=instance.Address1,
            Address2=instance.Address2,
            AccountLedgerID=instance.AccountLedgerID,
            CardNumber=instance.CardNumber,
            CardTypeID=instance.CardTypeID,
            CardStatusID=instance.CardStatusID,


            CreatedDate=today,
            UpdatedDate=today,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CompanyID=CompanyID,
        )

        response_data = {
            "StatusCode": 6000,
            "message": "Loyalty Customer Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Loyalty Customer Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def card_types(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']
        MasterTypeID = None

        if MasterType.objects.filter(BranchID=BranchID, CompanyID=CompanyID, Name="Loyalty Card Type").exists():
            MasterTypeID = MasterType.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, Name="Loyalty Card Type").MasterTypeID

        if TransactionTypes.objects.filter(BranchID=BranchID, CompanyID=CompanyID, MasterTypeID=MasterTypeID).exists():
            instances = TransactionTypes.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID, MasterTypeID=MasterTypeID)

            serialized = TransactionTypesRestSerializer(
                instances, many=True, context={"CompanyID": CompanyID})
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'TransactionTypes', 'List',
                         'TransactionTypes List Viewed Successfully.', "TransactionTypes List Viewed Successfully")
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'TransactionTypes', 'List',
                         'TransactionTypes List Viewed Failed.', "Transaction Types Not Found in this Branch")
            response_data = {
                "StatusCode": 6001,
                "message": "Transaction Types Not Found in this Branch!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def card_status(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']
        MasterTypeID = None
        if MasterType.objects.filter(BranchID=BranchID, CompanyID=CompanyID, Name="Loyalty Card Status"):
            MasterTypeID = MasterType.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, Name="Loyalty Card Status").MasterTypeID

        if TransactionTypes.objects.filter(BranchID=BranchID, CompanyID=CompanyID, MasterTypeID=MasterTypeID).exists():
            instances = TransactionTypes.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID, MasterTypeID=MasterTypeID)

            serialized = TransactionTypesRestSerializer(
                instances, many=True, context={"CompanyID": CompanyID})
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'TransactionTypes', 'List',
                         'TransactionTypes List Viewed Successfully.', "TransactionTypes List Viewed Successfully")
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'TransactionTypes', 'List',
                         'TransactionTypes List Viewed Failed.', "Transaction Types Not Found in this Branch")
            response_data = {
                "StatusCode": 6001,
                "message": "Transaction Types Not Found in this Branch!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def sundry_debtors(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        AccountGroupID = AccountGroup.objects.get(
            CompanyID=CompanyID, AccountGroupName="Sundry Debtors").AccountGroupID
        if AccountLedger.objects.filter(CompanyID=CompanyID, AccountGroupUnder=AccountGroupID).exists():
            instances = AccountLedger.objects.filter(
                CompanyID=CompanyID, AccountGroupUnder=AccountGroupID)

            serialized = AccountLedgerRestSerializer(
                instances, many=True, context={"CompanyID": CompanyID})
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'TransactionTypes', 'List',
                         'TransactionTypes List Viewed Successfully.', "TransactionTypes List Viewed Successfully")
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'TransactionTypes', 'List',
                         'TransactionTypes List Viewed Failed.', "Transaction Types Not Found in this Branch")
            response_data = {
                "StatusCode": 6001,
                "message": "Transaction Types Not Found in this Branch!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def get_mobileNo_detail(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    val = data['val']
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        instances = LoyaltyCustomer.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID)
        is_exist = False
        for i in instances:
            print(i.MobileNo)
            if val == i.MobileNo:
                is_exist = True
        print(is_exist)
        if not is_exist:
            response_data = {
                "StatusCode": 6000,
            }
        else:
            response_data = {
                "StatusCode": 6001,
                'message': "Mobile Number exists"
            }
        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def get_cardNumber_detail(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    val = data['val']
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        instances = LoyaltyCustomer.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID)
        is_exist = False
        for i in instances:
            print(i.CardNumber)
            if val == i.CardNumber:
                is_exist = True
        print(is_exist)
        if not is_exist:
            response_data = {
                "StatusCode": 6000,
            }
        else:
            response_data = {
                "StatusCode": 6001,
                'message': "Card Number exists"
            }
        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)
