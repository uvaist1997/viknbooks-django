from brands.models import UserTable, User_Log, UserType, CompanySettings
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login
from rest_framework.renderers import JSONRenderer
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v1.users.serializers import UserTableSerializer, UserTableRestSerializer, UserTypeSerializer, UserTypeRestSerializer, LoginSerializer, SignupSerializer, CreateCompanySerializer, CreateEmployeeSerializer, CreateFinancialYearSerializer, MyCompaniesSerializer, CompaniesSerializer, UserAccountsSerializer, AccountLedgerSerializer, WarehouseSerializer, TransactionTypesSerializer, UserTypesSerializer, GeneralSettingsSerializer, GeneralSettingsListSerializer, UserViewSerializer, CustomerUserViewSerializer, UpdateSerializer, CustomersSerializer, UserTypeSerializer, ActivityLogSerializer
from api.v1.brands.serializers import ListSerializer
from api.v1.users.functions import generate_serializer_errors
from brands.models import UserTable, AccountLedger, TransactionTypes, Warehouse, User_Log, UserType, Designation, Department, Employee, Employee_Log, FinancialYear, FinancialYear_Log, Customer, State, Country
from rest_framework import status
from brands import models as administrations_models
from django.contrib.auth.models import User, Group
from api.v1.users.functions import get_auto_id
from brands import models
from api.v1.general.functions import get_current_role
from users.models import CompanyEmployee, CompanyFinancialYear, CompanyAccountLedger
import datetime
from users.functions import get_EmployeeCode, get_LedgerCode, get_auto_LedgerID
from brands.functions import createdb
from django.utils.translation import ugettext_lazy as _
import requests
from django.shortcuts import get_object_or_404
from django.contrib.auth import logout
from users.models import CustomerUser, DatabaseStore
from api.v1.ledgerPosting.functions import convertOrderdDict
from main.functions import get_company, activity_log
from django.db.models import Max
from api.v1.users.functions import send_email
from rest_framework.views import APIView
from rest_framework import parsers, renderers, status
from django_rest_passwordreset.models import ResetPasswordToken
from django_rest_passwordreset.views import get_password_reset_token_expiry_time
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from datetime import timedelta
from api.v1.users.serializers import CustomTokenSerializer
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string
from django_rest_passwordreset.signals import reset_password_token_created
from mailqueue.models import MailerMessage
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from datetime import date
import json


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_user(request):
    today = datetime.datetime.now()
    serialized = UserTableSerializer(data=request.data)

    if serialized.is_valid():
        BranchID = serialized.data['BranchID']
        UserName = serialized.data['UserName']
        Password = serialized.data['Password']
        EmployeeID = serialized.data['EmployeeID']
        UserTypeID = serialized.data['UserTypeID']
        CreatedUserID = serialized.data['CreatedUserID']
        IsActive = serialized.data['IsActive']

        Action = 'A'

        ID = get_auto_id(UserTable, BranchID, CompanyID)

        is_nameExist = False

        UserNameLow = UserName.lower()

        users = UserTable.objects.filter(CompanyID=CompanyID)

        for user in users:
            user_name = user.UserName

            userName = user_name.lower()

            if UserNameLow == userName:
                is_nameExist = True

        if not is_nameExist:

            # serialized.save(ID=ID,CreatedDate=today,ModifiedDate=today)
            UserTable.objects.create(
                ID=ID,
                BranchID=BranchID,
                UserName=UserName,
                Password=Password,
                EmployeeID=EmployeeID,
                UserTypeID=UserTypeID,
                IsActive=IsActive,
                CreatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
                CompanyID=CompanyID
            )

            User_Log.objects.create(
                TransactionID=ID,
                BranchID=BranchID,
                UserName=UserName,
                Password=Password,
                EmployeeID=EmployeeID,
                UserTypeID=UserTypeID,
                IsActive=IsActive,
                CreatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
                CompanyID=CompanyID
            )

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Users',
                         'Create', 'Users created successfully.', 'Users saved successfully.')

            data = {"ID": ID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "User Name Already Exist!!!"
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
def edit_user(request, pk):
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    today = datetime.datetime.now()
    serialized = UserTableSerializer(data=request.data)
    instance = UserTable.objects.get(pk=pk, CompanyID=CompanyID)

    BranchID = instance.BranchID
    ID = instance.ID
    CreatedUserID = instance.CreatedUserID
    instanceUserName = instance.UserName

    if serialized.is_valid():

        UserName = serialized.data['UserName']
        Password = serialized.data['Password']
        UserTypeID = serialized.data['UserTypeID']
        EmployeeID = serialized.data['EmployeeID']
        IsActive = serialized.data['IsActive']

        Action = 'M'

        is_nameExist = False
        user_ok = False

        UserNameLow = UserName.lower()

        users = UserTable.objects.filter(CompanyID=CompanyID)

        for user in users:
            user_name = user.UserName

            userName = user_name.lower()

            if UserNameLow == userName:
                is_nameExist = True

            if instanceUserName.lower() == UserNameLow:

                user_ok = True

        if user_ok:

            instance.UserName = UserName
            instance.Password = Password
            instance.UserTypeID = UserTypeID
            instance.EmployeeID = EmployeeID
            instance.IsActive = IsActive
            instance.Action = Action
            instance.save()

            User_Log.objects.create(
                TransactionID=ID,
                BranchID=BranchID,
                UserName=UserName,
                Password=Password,
                UserTypeID=UserTypeID,
                EmployeeID=EmployeeID,
                IsActive=IsActive,
                CreatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
                CompanyID=CompanyID
            )

            data = {"ID": ID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:

            if is_nameExist:

                response_data = {
                    "StatusCode": 6001,
                    "message": "User Name Already exist with this Branch ID"
                }
                return Response(response_data, status=status.HTTP_200_OK)

            else:
                instance.UserName = UserName
                instance.Password = Password
                instance.UserTypeID = UserTypeID
                instance.EmployeeID = EmployeeID
                instance.IsActive = IsActive
                instance.Action = Action
                instance.save()

                User_Log.objects.create(
                    TransactionID=ID,
                    BranchID=BranchID,
                    UserName=UserName,
                    Password=Password,
                    UserTypeID=UserTypeID,
                    EmployeeID=EmployeeID,
                    IsActive=IsActive,
                    CreatedDate=today,
                    CreatedUserID=CreatedUserID,
                    Action=Action,
                    CompanyID=CompanyID
                )

                data = {"ID": ID}
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
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def users(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if UserTable.objects.filter(CompanyID=CompanyID).exists():
            instances = UserTable.objects.filter(CompanyID=CompanyID)
            serialized = UserTableRestSerializer(
                instances, many=True, context={"CompanyID": CompanyID})

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "User Not Found in this BranchID!"
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
def customers(request):
    data = request.data
    # serializer = ListSerializer(data=request.data)
    if Customer.objects.all().exists():
        instances = Customer.objects.all()
        serializer = CustomersSerializer(instances, many=True)
        response_data = {
            "StatusCode": 6000,
            "data": serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Customer Not Found"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def user_types(request):
    data = request.data
    # serializer = ListSerializer(data=request.data)
    if UserType.objects.all().exists():
        instances = UserType.objects.all()
        serializer = UserTypeSerializer(instances, many=True)
        response_data = {
            "StatusCode": 6000,
            "data": serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Customer Not Found"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def user(request, pk):
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    instance = None

    if UserTable.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = UserTable.objects.get(CompanyID=CompanyID, pk=pk)
    if instance:
        serialized = UserTableRestSerializer(
            instance, context={"CompanyID": CompanyID})
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "User Table Not Fount!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_user(request, pk):
    today = datetime.datetime.now()
    instance = None
    if UserTable.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = UserTable.objects.get(CompanyID=CompanyID, pk=pk)
    if instance:
        BranchID = instance.BranchID
        ID = instance.ID
        UserName = instance.UserName
        Password = instance.Password
        EmployeeID = instance.EmployeeID
        CreatedUserID = instance.CreatedUserID
        CreatedDate = instance.CreatedDate
        IsActive = instance.IsActive
        Action = "D"

        instance.delete()
        User_Log.objects.create(
            TransactionID=ID,
            BranchID=BranchID,
            UserName=UserName,
            Password=Password,
            EmployeeID=EmployeeID,
            IsActive=IsActive,
            CreatedDate=today,
            CreatedUserID=CreatedUserID,
            Action=Action,
            CompanyID=CompanyID
        )
        response_data = {
            "StatusCode": 6000,
            "message": "User Table Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "User Table Not Fount!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_user_type(request):
    today = datetime.datetime.now()
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    serialized = UserTypeSerializer(data=request.data)

    if serialized.is_valid():
        UserTypeName = serialized.data['UserTypeName']
        BranchID = serialized.data['BranchID']
        Notes = serialized.data['Notes']
        CreatedUserID = serialized.data['CreatedUserID']

        ID = get_auto_id(UserType, BranchID, CompanyID)

        is_nameExist = False

        UserNameLow = UserTypeName.lower()

        UserTypes = UserType.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID)

        for userType in UserTypes:
            user_name = userType.UserTypeName

            userName = user_name.lower()

            if UserNameLow == userName:
                is_nameExist = True

        if not is_nameExist:

            # serialized.save(ID=ID,CreatedDate=today,ModifiedDate=today)
            UserType.objects.create(
                ID=ID,
                UserTypeName=UserTypeName,
                BranchID=BranchID,
                Notes=Notes,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                CompanyID=CompanyID
            )

            data = {"ID": ID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "User Type Name Already Exist!!!"
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
def userTypes(request):
    serialized1 = ListSerializer(data=request.data)
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if UserType.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():

            instances = UserType.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)

            serialized = UserTypeRestSerializer(instances, many=True)

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "User Type Not Found in this BranchID!"
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
def userType(request, pk):
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)

    if UserType.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = UserType.objects.get(CompanyID=CompanyID, pk=pk)
    if instance:
        serialized = UserTypeRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "User Table Not Fount!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def edit_userType(request, pk):
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    today = datetime.datetime.now()
    serialized = UserTypeSerializer(data=request.data)
    instance = UserType.objects.get(CompanyID=CompanyID, pk=pk)

    BranchID = instance.BranchID
    ID = instance.ID
    CreatedUserID = instance.CreatedUserID
    instanceUserTypeName = instance.UserTypeName

    if serialized.is_valid():

        UserTypeName = serialized.data['UserTypeName']
        Notes = serialized.data['Notes']

        is_nameExist = False
        user_ok = False

        UserTypeNameLow = UserTypeName.lower()

        users = UserType.objects.filter(CompanyID=CompanyID, BranchID=BranchID)

        for user in users:
            userType_name = user.UserTypeName

            userTypeName = userType_name.lower()

            if UserTypeNameLow == userTypeName:
                is_nameExist = True

            if instanceUserTypeName.lower() == UserTypeNameLow:

                user_ok = True

        if user_ok:

            instance.UserTypeName = UserTypeName
            instance.Notes = Notes
            instance.save()

            data = {"ID": ID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            if is_nameExist:

                response_data = {
                    "StatusCode": 6001,
                    "message": "UserType Name Already exist with this Branch ID"
                }
                return Response(response_data, status=status.HTTP_200_OK)

            else:
                instance.UserTypeName = UserTypeName
                instance.Notes = Notes
                instance.save()

                data = {"ID": ID}
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
def delete_userType(request, pk):
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    today = datetime.datetime.now()
    instance = None
    if UserType.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = UserType.objects.get(CompanyID=CompanyID, pk=pk)
    if instance:
        ID = instance.ID
        UserTypeName = instance.UserTypeName
        BranchID = instance.BranchID
        Notes = instance.Notes
        CreatedUserID = instance.CreatedUserID
        CreatedDate = instance.CreatedDate

        instance.delete()

        response_data = {
            "StatusCode": 6000,
            "message": "User Type Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "User Type Not Fount!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def user_signup(request):
    today = datetime.datetime.now()
    serialized = SignupSerializer(data=request.data)

    if serialized.is_valid():
        first_name = serialized.validated_data['first_name']
        last_name = serialized.validated_data['last_name']
        username = serialized.validated_data['username']
        email = serialized.validated_data['email']
        password1 = serialized.validated_data['password1']
        password2 = serialized.validated_data['password2']
        message = ""
        error = False

        bad_domains = ['guerrillamail.com']
        if '@' in email:
            email_domain = email.split('@')[1]
        else:
            message = "Please enter a proper Email"

        if User.objects.filter(email__iexact=email, is_active=True):
            message = "This email address is already in use."
            error = True
        elif email_domain in bad_domains:
            message = (
                "Registration using %s email addresses is not allowed. Please supply a different email address.") % email_domain
            error = True
            email = email

        min_password_length = 6

        if len(password1) < min_password_length:
            message = ("Password must have at least %i characters" %
                       min_password_length)
            error = True
        else:
            password1 = password1

        if password1 and password2 and password1 != password2:
            message = 'password_mismatch'
            error = True
            password2 = password2

        min_username_length = 6

        existing = User.objects.filter(username__iexact=username)
        if existing.exists():
            message = "A user with that username already exists."
            error = True
        elif len(username) < min_username_length:
            message = ("Username must have at least %i characters" %
                       min_password_length)
            error = True
        else:
            username = username

        if not error:
            # serialized.save()
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password1,
                is_superuser=False,
            )
            Customer.objects.create(
                user=user,
            )

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": message
            }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def user_view(request, pk):
    instance = Customer.objects.get(user__pk=pk)

    customer_serialized = CustomerUserViewSerializer(instance)
    serialized = UserViewSerializer(instance.user)

    response_data = {
        "StatusCode": 6000,
        "data": serialized.data,
        "customer_data": customer_serialized.data
    }
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def update_user(request):
    data = request.data
    photo = data['photo']
    user_id = data['user_id']

    DateOfBirth = data['DateOfBirth']
    if DateOfBirth == 'null':
        DateOfBirth = None
    else:
        DateOfBirth = DateOfBirth
    Country_pk = data['Country']
    if Country_pk == 'null':
        Country_pk = None
        Countries = None
    else:
        Countries = Country.objects.get(pk=Country_pk)

    Phone = data['Phone']
    if Phone == 'null' or '':
        Phone = None
    else:
        Phone = Phone
    State_pk = data['State']
    if State_pk == 'null':
        States = None
        State_pk = None
    else:
        States = State.objects.get(pk=State_pk)

    City = data['City']
    if City == 'null' or '':
        City = None
    else:
        City = City
    Address = data['Address']
    if Address == 'null' or '':
        Address = None
    else:
        Address = Address
    today = datetime.datetime.now()
    serialized = UpdateSerializer(data=request.data)

    if serialized.is_valid():
        first_name = serialized.validated_data['first_name']
        last_name = serialized.validated_data['last_name']
        username = serialized.validated_data['username']
        email = serialized.validated_data['email']

        message = ""
        error = False

        min_username_length = 6
        existing_user = User.objects.exclude(username__in=[username])
        existing_email = User.objects.exclude(email__in=[email])
        if username in existing_user:
            error = True
            message += "This username already exists."

        if email in existing_email:
            error = True
            message += "This email already exists."

        elif len(username) < min_username_length:
            message = ("Username must have at least %i characters" %
                       min_password_length)
            error = True
        else:
            username = username

        if not error:

            user = User.objects.filter(pk=user_id).update(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
            )
            instance = Customer.objects.get(user__pk=user_id)
            instance.photo=photo
            instance.DateOfBirth=DateOfBirth
            instance.Country=Countries
            instance.Phone=Phone
            instance.State=States
            instance.City=City
            instance.Address=Address
            instance.save()
            
            data = serialized.data
            response_data = {
                "StatusCode": 6000,
                "data": data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": message
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
def user_login(request):
    serialized = LoginSerializer(data=request.data)
    CompanyID = ""
    CreatedUserID = ""
    EmployeeID = ""
    Cash_Account = ""
    Bank_Account = ""
    WarehouseID = ""
    Sales_Account = ""
    Sales_Return_Account = ""
    Purchase_Account = ""
    Purchase_Return_Account = ""
    Sales_GST_Type = ""
    Purchase_GST_Type = ""
    VAT_Type = ""
    BranchID = 1
    if serialized.is_valid():

        username = serialized.data['username']
        password = serialized.data['password']

        if User.objects.filter(email=username).exists():
            email = username
            username = User.objects.get(email=email).username

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)

            request.session['current_role'] = get_current_role(request)

            headers = {
                'Content-Type': 'application/json',
            }

            data = '{"username": "' + username + \
                '", "password": "' + password + '" }'

            protocol = "http://"
            # if request.is_secure():
            # protocol = "https://"

            web_host = request.get_host()
            request_url = protocol + web_host + "/api/v1/auth/token/"
            response = requests.post(request_url, headers=headers, data=data)

            if response.status_code == 200:
                dic = ""
                Sales_Account_name = ""
                Sales_Return_Account_name = ""
                Purchase_Account_name = ""
                Purchase_Return_Account_name = ""
                Employee_name = ""
                Cash_Account_name = ""
                Bank_Account_name = ""
                Warehouse_name = ""
                VAT_Type_name = ""
                Sales_GST_Type_name = ""
                Purchase_GST_Type_name = ""
                if User.objects.filter(username=username, password=password, is_superuser=False).exists():
                    if UserTable.objects.filter(UserName=username, Password=password).exists():
                        CompanyID = get_object_or_404(UserTable.objects.filter(
                            UserName=username, Password=password)).CompanyID.id

                # else:
                #     CompanyID = ""
                #     CreatedUserID = ""
                #     EmployeeID = ""
                #     Cash_Account = ""
                #     Bank_Account = ""
                #     Warehouse = ""
                #     Sales_Account = ""
                #     Sales_Return_Account = ""
                #     Purchase_Account = ""
                #     Purchase_Return_Account = ""
                #     Sales_GST_Type = ""
                #     Purchase_GST_Type = ""
                #     VAT_Type = ""

                        user_table_instance = get_object_or_404(UserTable.objects.filter(
                            CompanyID=CompanyID, UserName=username, Password=password))
                        EmployeeID = user_table_instance.EmployeeID
                        Cash_Account = user_table_instance.Cash_Account
                        Bank_Account = user_table_instance.Bank_Account
                        WarehouseID = user_table_instance.Warehouse
                        Sales_Account = user_table_instance.Sales_Account
                        Sales_Return_Account = user_table_instance.Sales_Return_Account
                        Purchase_Account = user_table_instance.Purchase_Account
                        Purchase_Return_Account = user_table_instance.Purchase_Return_Account
                        Sales_GST_Type = user_table_instance.Sales_GST_Type
                        Purchase_GST_Type = user_table_instance.Purchase_GST_Type
                        VAT_Type = user_table_instance.VAT_Type

                        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Sales_Account, BranchID=BranchID).exists():
                            Sales_Account_name = get_object_or_404(AccountLedger.objects.filter(
                                CompanyID=CompanyID, LedgerID=Sales_Account, BranchID=BranchID)).LedgerName

                        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Sales_Return_Account, BranchID=BranchID).exists():
                            Sales_Return_Account_name = get_object_or_404(AccountLedger.objects.filter(
                                CompanyID=CompanyID, LedgerID=Sales_Return_Account, BranchID=BranchID)).LedgerName

                        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Purchase_Account, BranchID=BranchID).exists():
                            Purchase_Account_name = get_object_or_404(AccountLedger.objects.filter(
                                CompanyID=CompanyID, LedgerID=Purchase_Account, BranchID=BranchID)).LedgerName

                        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Purchase_Return_Account, BranchID=BranchID).exists():
                            Purchase_Return_Account_name = get_object_or_404(AccountLedger.objects.filter(
                                CompanyID=CompanyID, LedgerID=Purchase_Return_Account, BranchID=BranchID)).LedgerName

                        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Cash_Account, BranchID=BranchID).exists():
                            Cash_Account_name = get_object_or_404(AccountLedger.objects.filter(
                                CompanyID=CompanyID, LedgerID=Cash_Account, BranchID=BranchID)).LedgerName

                        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Bank_Account, BranchID=BranchID).exists():
                            Bank_Account_name = get_object_or_404(AccountLedger.objects.filter(
                                CompanyID=CompanyID, LedgerID=Bank_Account, BranchID=BranchID)).LedgerName

                        if Employee.objects.filter(CompanyID=CompanyID, EmployeeID=EmployeeID, BranchID=BranchID).exists():
                            Employee_name = get_object_or_404(Employee.objects.filter(
                                CompanyID=CompanyID, EmployeeID=EmployeeID, BranchID=BranchID)).FirstName

                        if TransactionTypes.objects.filter(CompanyID=CompanyID, TransactionTypesID=VAT_Type, BranchID=BranchID).exists():
                            VAT_Type_name = get_object_or_404(TransactionTypes.objects.filter(
                                CompanyID=CompanyID, TransactionTypesID=VAT_Type, BranchID=BranchID)).Name

                        if TransactionTypes.objects.filter(CompanyID=CompanyID, TransactionTypesID=Sales_GST_Type, BranchID=BranchID).exists():
                            Sales_GST_Type_name = get_object_or_404(TransactionTypes.objects.filter(
                                CompanyID=CompanyID, TransactionTypesID=Sales_GST_Type, BranchID=BranchID)).Name

                        if TransactionTypes.objects.filter(CompanyID=CompanyID, TransactionTypesID=Purchase_GST_Type, BranchID=BranchID).exists():
                            Purchase_GST_Type_name = get_object_or_404(TransactionTypes.objects.filter(
                                CompanyID=CompanyID, TransactionTypesID=Purchase_GST_Type, BranchID=BranchID)).Name

                        if Warehouse.objects.filter(CompanyID=CompanyID, WarehouseID=WarehouseID, BranchID=BranchID).exists():
                            Warehouse_name = get_object_or_404(Warehouse.objects.filter(
                                CompanyID=CompanyID, WarehouseID=WarehouseID, BranchID=BranchID)).WarehouseName
                    # else:
                    #     DataBase = ""
                    #     CreatedUserID = None
                    #     EmployeeID = None
                    #     Cash_Account = None
                    #     Bank_Account = None
                    #     WarehouseID = None
                    #     Sales_Account = None
                    #     Sales_Return_Account = None
                    #     Purchase_Account = None
                    #     Purchase_Return_Account = None
                    #     Sales_GST_Type = None
                    #     Purchase_GST_Type = None
                    #     VAT_Type = None

                        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
                            check_VAT = administrations_models.GeneralSettings.objects.get(
                                CompanyID=CompanyID, SettingsType="VAT").SettingsValue
                            check_GST = administrations_models.GeneralSettings.objects.get(
                                CompanyID=CompanyID, SettingsType="GST").SettingsValue
                            check_TAX1 = administrations_models.GeneralSettings.objects.get(
                                CompanyID=CompanyID, SettingsType="TAX1").SettingsValue
                            check_TAX2 = administrations_models.GeneralSettings.objects.get(
                                CompanyID=CompanyID, SettingsType="TAX2").SettingsValue
                            check_TAX3 = administrations_models.GeneralSettings.objects.get(
                                CompanyID=CompanyID, SettingsType="TAX3").SettingsValue
                            check_Trading = administrations_models.GeneralSettings.objects.get(
                                CompanyID=CompanyID, SettingsType="Trading").SettingsValue
                            check_Restaurant = administrations_models.GeneralSettings.objects.get(
                                CompanyID=CompanyID, SettingsType="Restaurant").SettingsValue
                            check_QtyDecimalPoint = administrations_models.GeneralSettings.objects.get(
                                CompanyID=CompanyID, SettingsType="QtyDecimalPoint").SettingsValue
                            check_PriceDecimalPoint = administrations_models.GeneralSettings.objects.get(
                                CompanyID=CompanyID, SettingsType="PriceDecimalPoint").SettingsValue
                            check_PreDateTransaction = administrations_models.GeneralSettings.objects.get(
                                CompanyID=CompanyID, SettingsType="PreDateTransaction").SettingsValue
                            check_PostDateTransaction = administrations_models.GeneralSettings.objects.get(
                                CompanyID=CompanyID, SettingsType="PostDateTransaction").SettingsValue
                            check_Additional_Discount = administrations_models.GeneralSettings.objects.get(
                                CompanyID=CompanyID, SettingsType="Additional_Discount").SettingsValue
                            check_Bill_Discount = administrations_models.GeneralSettings.objects.get(
                                CompanyID=CompanyID, SettingsType="Bill_Discount").SettingsValue
                            check_Negatine_Stock = administrations_models.GeneralSettings.objects.get(
                                CompanyID=CompanyID, SettingsType="Negatine_Stock").SettingsValue
                            check_Increment_Qty_In_POS = administrations_models.GeneralSettings.objects.get(
                                CompanyID=CompanyID, SettingsType="Increment_Qty_In_POS").SettingsValue
                            check_Kitchen_Print = administrations_models.GeneralSettings.objects.get(
                                CompanyID=CompanyID, SettingsType="Kitchen_Print").SettingsValue
                            check_Order_Print = administrations_models.GeneralSettings.objects.get(
                                CompanyID=CompanyID, SettingsType="Order_Print").SettingsValue
                            check_Print_After_Save_Active = administrations_models.GeneralSettings.objects.get(
                                CompanyID=CompanyID, SettingsType="Print_After_Save_Active").SettingsValue
                            QtyDecimalPoint = administrations_models.GeneralSettings.objects.get(
                                CompanyID=CompanyID, SettingsType="QtyDecimalPoint").SettingsValue
                            PriceDecimalPoint = administrations_models.GeneralSettings.objects.get(
                                CompanyID=CompanyID, SettingsType="PriceDecimalPoint").SettingsValue
                            PreDateTransaction = administrations_models.GeneralSettings.objects.get(
                                CompanyID=CompanyID, SettingsType="PreDateTransaction").SettingsValue
                            PostDateTransaction = administrations_models.GeneralSettings.objects.get(
                                CompanyID=CompanyID, SettingsType="PostDateTransaction").SettingsValue

                            if check_TAX1 == 'false':
                                check_TAX1 = ''

                            if check_TAX2 == 'false':
                                check_TAX2 = ''

                            if check_TAX3 == 'false':
                                check_TAX3 = ''

                            if check_Additional_Discount == 'false':
                                check_Additional_Discount = ''

                            if check_Bill_Discount == 'false':
                                check_Bill_Discount = ''

                            if check_Negatine_Stock == 'false':
                                check_Negatine_Stock = ''

                            if check_Increment_Qty_In_POS == 'false':
                                check_Increment_Qty_In_POS = ''

                            if check_Kitchen_Print == 'false':
                                check_Kitchen_Print = ''

                            if check_Order_Print == 'false':
                                check_Order_Print = ''

                            if check_Print_After_Save_Active == 'false':
                                check_Print_After_Save_Active = ''

                            if check_Trading == 'false':
                                check_Trading = ''

                            if check_Restaurant == 'false':
                                check_Restaurant = ''

                            if check_Trading == 'true':
                                Business_Type = 'Trading'
                            else:
                                Business_Type = 'Restaurant'

                            if check_VAT == 'false':
                                check_VAT = ''

                            if check_GST == 'false':
                                check_GST = ''

                            # if check_VAT == 'true':
                            #     Tax_Active = 'VAT'
                            # else:
                            #     Tax_Active = 'GST'

                            dic = {
                                "check_VAT": check_VAT,
                                "check_GST": check_GST,
                                "check_TAX1": check_TAX1,
                                "check_TAX2": check_TAX2,
                                "check_TAX3": check_TAX3,
                                "check_Trading": check_Trading,
                                "check_Restaurant": check_Restaurant,
                                "check_QtyDecimalPoint": check_QtyDecimalPoint,
                                "check_PriceDecimalPoint": check_PriceDecimalPoint,
                                "check_PreDateTransaction": check_PreDateTransaction,
                                "check_PostDateTransaction": check_PostDateTransaction,
                                "check_Additional_Discount": check_Additional_Discount,
                                "check_Bill_Discount": check_Bill_Discount,
                                "check_Negatine_Stock": check_Negatine_Stock,
                                "check_Increment_Qty_In_POS": check_Increment_Qty_In_POS,
                                "check_Kitchen_Print": check_Kitchen_Print,
                                "check_Order_Print": check_Order_Print,
                                "check_Print_After_Save_Active": check_Print_After_Save_Active,
                                "QtyDecimalPoint": QtyDecimalPoint,
                                "PriceDecimalPoint": PriceDecimalPoint,
                                "Business_Type": Business_Type,
                                # "Tax_Active" : Tax_Active,
                            }

                data = response.json()

                success = 6000
                message = "Login successfully"
                return Response(
                    {
                        'success': success,
                        'data': data,
                        'refresh': data['refresh'],
                        'access': data['access'],
                        'user_id': data['user_id'],
                        'role': data['role'],
                        'message': message,
                        'error': None,
                        "CompanyID": CompanyID,
                        "CreatedUserID": CreatedUserID,
                        "EmployeeID": EmployeeID,
                        "Cash_Account": Cash_Account,
                        "Bank_Account": Bank_Account,
                        "Warehouse": WarehouseID,
                        "Sales_Account": Sales_Account,
                        "Sales_Return_Account": Sales_Return_Account,
                        "Purchase_Account": Purchase_Account,
                        "Purchase_Return_Account": Purchase_Return_Account,
                        "Sales_GST_Type": Sales_GST_Type,
                        "Purchase_GST_Type": Purchase_GST_Type,
                        "VAT_Type": VAT_Type,
                        "settingsData": dic,
                        "Sales_Account_name": Sales_Account_name,
                        "Sales_Return_Account_name": Sales_Return_Account_name,
                        "Purchase_Account_name": Purchase_Account_name,
                        "Purchase_Return_Account_name": Purchase_Return_Account_name,
                        "Cash_Account_name": Cash_Account_name,
                        "Bank_Account_name": Bank_Account_name,
                        "Employee_name": Employee_name,
                        "VAT_Type_name": VAT_Type_name,
                        "Sales_GST_Type_name": Sales_GST_Type_name,
                        "Purchase_GST_Type_name": Purchase_GST_Type_name,
                        "Warehouse_name": Warehouse_name,
                        'username': username
                    },
                    status=status.HTTP_200_OK)
            else:
                success = 6001
                data = None
                error = "please contact admin to solve this problem."
                return Response(
                    {
                        'success': success,
                        'data': data,
                        'error': error
                    },
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            success = 6001
            data = None
            error = "User not found"
            return Response(
                {
                    'success': success,
                    'data': data,
                    'error': error
                },
                status=status.HTTP_400_BAD_REQUEST)

    else:
        message = generate_serializer_errors(serialized._errors)
        success = 6001
        data = None
        return Response(
            {
                'success': success,
                'data': data,
                'error': message,
            },
            status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def check_user(request):
    CompanyID = request.data['CompanyID']
    CompanyID = get_object_or_404(CompanySettings.objects.filter(id=CompanyID))
    user = False
    if UserTable.objects.filter(CompanyID=CompanyID).exists():
        user = True
        response_data = {
            "StatusCode": 6000,
            "user": user
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        user = False
        response_data = {
            "StatusCode": 6001,
            "user": user
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def logout_view(request):
    try:
        request.user.auth_token.delete()
    except (AttributeError, ObjectDoesNotExist):
        pass
    if getattr(settings, 'REST_SESSION_LOGIN', True):
        logout(request)
    response_data = {
        'StatusCode': 6000,
        'message': "Logout successfully",
        'error': None,
    }
    if getattr(settings, 'REST_USE_JWT', False):
        from rest_framework_jwt.settings import api_settings as jwt_settings
        if jwt_settings.JWT_AUTH_COOKIE:
            response_data.delete_cookie(jwt_settings.JWT_AUTH_COOKIE)

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_company(request):
    serialized = CreateCompanySerializer(data=request.data)
    if serialized.is_valid():
        CompanyName = serialized.data['CompanyName']
        Address1 = serialized.data['Address1']
        Address2 = serialized.data['Address2']
        Address3 = serialized.data['Address3']
        city = serialized.data['city']
        state = serialized.data['state']
        country = serialized.data['country']
        postalcode = serialized.data['postalcode']
        phone = serialized.data['phone']
        mobile = serialized.data['mobile']
        email = serialized.data['email']
        website = serialized.data['website']
        currency = serialized.data['currency']
        fractionalunit = serialized.data['fractionalunit']
        vatnumber = serialized.data['vatnumber']
        gstnumber = serialized.data['gstnumber']
        tax1 = serialized.data['tax1']
        tax2 = serialized.data['tax2']
        tax3 = serialized.data['tax3']
        customerid = 1

        db_id = createdb(CompanyName, Address1, Address2, Address3, city, state, country, postalcode, phone,
                         mobile, email, website, currency, fractionalunit, vatnumber, gstnumber, tax1, tax2, tax3, customerid)

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data,
            "message": "company successfully created",
            "db_id": db_id
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


# @api_view(['POST'])
# @permission_classes((AllowAny,))
# @renderer_classes((JSONRenderer,))
# def companies(request):
#     userId = request.data['userId']
#     userId = get_object_or_404(User.objects.filter(id=userId))
#     instances = models.CompanySettings.objects.filter(owner=userId)
#     serialized = MyCompaniesSerializer(instances,many=True)
#     response_data = {
#         "StatusCode" : 6000,
#         "data" : serialized.data,
#     }

#     return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def companies(request):
    userId = request.data['userId']
    userId = get_object_or_404(User.objects.filter(id=userId))
    my_company_instances = models.CompanySettings.objects.filter(
        owner=userId, is_deleted=False)
    my_company_serialized = MyCompaniesSerializer(
        my_company_instances, many=True)
    my_company_json = convertOrderdDict(my_company_serialized.data)

    member_company_instances = models.UserTable.objects.filter(
        customer__user=userId)
    member_company_serialized = CompaniesSerializer(
        member_company_instances, many=True)
    member_company_json = convertOrderdDict(member_company_serialized.data)

    data = []
    for i in my_company_json:
        id = i['id']
        CompanyName = i['CompanyName']
        company_type = i['company_type']
        ExpiryDate = i['ExpiryDate']
        print(ExpiryDate)
        ExpiryDate = date.today().strftime("%Y-%m-%d")
        if i['ExpiryDate'] != None:
            ExpiryDate = i['ExpiryDate']
        dic = {
            'id': id,
            'CompanyName': CompanyName,
            'company_type': company_type,
            'ExpiryDate': ExpiryDate,
        }
        data.append(dic)

    for i in member_company_json:
        id = i['id']
        CompanyName = i['CompanyName']
        company_type = i['company_type']
        ExpiryDate = date.today().strftime("%Y-%m-%d")
        if i['ExpiryDate'] != None:
            ExpiryDate = i['ExpiryDate']
        dic = {
            'id': id,
            'CompanyName': CompanyName,
            'company_type': company_type,
            'ExpiryDate': ExpiryDate,
        }
        data.append(dic)

    tes_arry = []
    final_array = []
    for i in data:
        if not i['id'] in tes_arry:
            tes_arry.append(i['id'])
            final_array.append(i)

    response_data = {
        "StatusCode": 6000,
        "data": final_array,
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def user_accounts(request):
    CompanyID = request.data['CompanyID']
    BranchID = request.data['BranchID']
    CompanyID = get_company(CompanyID)
    cash_accounts = AccountLedger.objects.filter(
        AccountGroupUnder=9, CompanyID=CompanyID)
    cash_accounts = AccountLedgerSerializer(cash_accounts, many=True)
    bank_accounts = AccountLedger.objects.filter(
        AccountGroupUnder=8, CompanyID=CompanyID)
    bank_accounts = AccountLedgerSerializer(bank_accounts, many=True)
    sales_accounts = AccountLedger.objects.filter(
        AccountGroupUnder=74, CompanyID=CompanyID)
    sales_accounts = AccountLedgerSerializer(sales_accounts, many=True)
    purchase_accounts = AccountLedger.objects.filter(
        AccountGroupUnder=48, CompanyID=CompanyID)
    purchase_accounts = AccountLedgerSerializer(purchase_accounts, many=True)
    warehouses = Warehouse.objects.all()
    warehouses = WarehouseSerializer(warehouses, many=True)

    sales_gst_types = TransactionTypes.objects.filter(
        MasterTypeID=6, BranchID=BranchID, CompanyID=CompanyID)
    sales_gst_types = TransactionTypesSerializer(sales_gst_types, many=True)
    purchase_gst_types = TransactionTypes.objects.filter(
        MasterTypeID=7, BranchID=BranchID, CompanyID=CompanyID)
    purchase_gst_types = TransactionTypesSerializer(
        purchase_gst_types, many=True)
    vat_types = TransactionTypes.objects.filter(
        MasterTypeID=8, BranchID=BranchID, CompanyID=CompanyID)
    vat_types = TransactionTypesSerializer(vat_types, many=True)
    user_types = UserType.objects.filter(
        BranchID=BranchID, CompanyID=CompanyID)
    user_types = UserTypesSerializer(user_types, many=True)
    response_data = {
        "StatusCode": 6000,
        "cash_accounts": cash_accounts.data,
        "bank_accounts": bank_accounts.data,
        "sales_accounts": sales_accounts.data,
        "purchase_accounts": purchase_accounts.data,
        "warehouses": warehouses.data,
        "sales_gst_types": sales_gst_types.data,
        "purchase_gst_types": purchase_gst_types.data,
        "vat_types": vat_types.data,
        "user_types": user_types.data
    }
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_company_user(request, pk):
    CompanyID = request.data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = request.data['BranchID']
    today = datetime.datetime.now()
    cash_accounts = AccountLedger.objects.filter(
        AccountGroupUnder=9, CompanyID=CompanyID)
    bank_accounts = AccountLedger.objects.filter(
        AccountGroupUnder=8, CompanyID=CompanyID)
    sales_accounts = AccountLedger.objects.filter(
        AccountGroupUnder=74, CompanyID=CompanyID)
    purchase_accounts = AccountLedger.objects.filter(
        AccountGroupUnder=48, CompanyID=CompanyID)
    warehouses = Warehouse.objects.filter(CompanyID=CompanyID)
    sales_gst_types = TransactionTypes.objects.filter(
        MasterTypeID=6, BranchID=BranchID, CompanyID=CompanyID)
    purchase_gst_types = TransactionTypes.objects.filter(
        MasterTypeID=7, BranchID=BranchID, CompanyID=CompanyID)
    vat_types = TransactionTypes.objects.filter(
        MasterTypeID=8, BranchID=BranchID, CompanyID=CompanyID)
    user_types = UserType.objects.filter(CompanyID=CompanyID)

    serialized = UserAccountsSerializer(data=request.data)
    if serialized.is_valid():
        Cash_Account = serialized.data["Cash_Account"]
        Bank_Account = serialized.data["Bank_Account"]
        warehouse = serialized.data["warehouse"]
        Sales_Account = serialized.data["Sales_Account"]
        Sales_Return_Account = serialized.data["Sales_Return_Account"]
        Purchase_Account = serialized.data["Purchase_Account"]
        Purchase_Return_Account = serialized.data["Purchase_Return_Account"]
        Sales_GST_Type = serialized.data["Sales_GST_Type"]
        Purchase_GST_Type = serialized.data["Purchase_GST_Type"]
        VAT_Type = serialized.data["VAT_Type"]
        ExpiryDate = serialized.data["ExpiryDate"]
        UserTypeID = serialized.data["UserTypeID"]
        CreatedUserID = serialized.data["CreatedUserID"]
        UpdatedDate = today

        email = serialized.data['email']
        username = serialized.data['username']
        password1 = serialized.data['password1']
        password2 = serialized.data['password2']

        message = ""
        error = False
        if password1 == password2:
            if UserTable.objects.filter(CompanyID__Email=email, CompanyID=CompanyID).exists():
                error = True
                message += "This email already exists."
            elif UserTable.objects.filter(UserName=username, CompanyID=CompanyID).exists():
                error = True
                message += "This username already exists."

            if not error:
                branchid = 1
                id = get_auto_id(UserTable, branchid, CompanyID)
                action = "A"
                employeeid = 1
                isactive = True
                createddate = datetime.date.today()
                databaseid = pk

                User.objects.create_user(
                    email=email,
                    username=username,
                    password=password1,
                )
                UserTable.objects.create(
                    CompanyID=CompanyID,
                    ID=id,
                    UserTypeID=UserTypeID,
                    BranchID=branchid,
                    Action=action,
                    UserName=username,
                    Password=password1,
                    EmployeeID=employeeid,
                    IsActive=isactive,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=createddate,
                    Cash_Account=Cash_Account,
                    Bank_Account=Bank_Account,
                    Warehouse=warehouse,
                    Sales_Account=Sales_Account,
                    Sales_Return_Account=Sales_Return_Account,
                    Purchase_Account=Purchase_Account,
                    Purchase_Return_Account=Purchase_Return_Account,
                    Sales_GST_Type=Sales_GST_Type,
                    Purchase_GST_Type=Purchase_GST_Type,
                    VAT_Type=VAT_Type,
                    ExpiryDate=ExpiryDate,
                    UpdatedDate=UpdatedDate,
                )

                User_Log.objects.create(
                    CompanyID=CompanyID,
                    TransactionID=id,
                    UserTypeID=UserTypeID,
                    BranchID=branchid,
                    Action=action,
                    UserName=username,
                    Password=password1,
                    EmployeeID=employeeid,
                    IsActive=isactive,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=createddate,
                    Cash_Account=Cash_Account,
                    Bank_Account=Bank_Account,
                    Warehouse=warehouse,
                    Sales_Account=Sales_Account,
                    Sales_Return_Account=Sales_Return_Account,
                    Purchase_Account=Purchase_Account,
                    Purchase_Return_Account=Purchase_Return_Account,
                    Sales_GST_Type=Sales_GST_Type,
                    Purchase_GST_Type=Purchase_GST_Type,
                    VAT_Type=VAT_Type,
                    ExpiryDate=ExpiryDate,
                    UpdatedDate=UpdatedDate,
                )

                response_data = {
                    "StatusCode": 6000,
                    "data": serialized.data,
                    "message": "user successfully created",
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "can't create this user",
                }
                return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Password mismatch",
            }
            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors),
        }
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_general_settings(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    BranchID = data['BranchID']

    today = datetime.datetime.now()
    serialized = GeneralSettingsSerializer(data=request.data)
    if serialized.is_valid():
        QtyDecimalPoint = serialized.data['QtyDecimalPoint']
        PriceDecimalPoint = serialized.data['PriceDecimalPoint']
        PreDateTransaction = serialized.data['PreDateTransaction']
        PostDateTransaction = serialized.data['PostDateTransaction']
        RoundingFigure = serialized.data['RoundingFigure']
        # Tax_Active = serialized.data['Tax_Active']
        VAT = serialized.data['VAT']
        GST = serialized.data['GST']
        Tax1 = serialized.data['Tax1']
        Tax2 = serialized.data['Tax2']
        Tax3 = serialized.data['Tax3']
        Additional_Discount = serialized.data['Additional_Discount']
        Bill_Discount = serialized.data['Bill_Discount']
        # Business_Type = serialized.data['Business_Type']
        Negative_Stock_Show = serialized.data['Negative_Stock_Show']
        Increment_Qty_In_POS = serialized.data['Increment_Qty_In_POS']
        Kitchen_Print = serialized.data['Kitchen_Print']
        Order_Print = serialized.data['Order_Print']
        Print_After_Save_Active = serialized.data['Print_After_Save_Active']
        Free_Quantity_In_Sales = serialized.data['Free_Quantity_In_Sales']
        Free_Quantity_In_Purchase = serialized.data['Free_Quantity_In_Purchase']
        Show_Sales_Type = serialized.data['Show_Sales_Type']
        Show_Purchase_Type = serialized.data['Show_Purchase_Type']
        Purchase_GST_Type = serialized.data['Purchase_GST_Type']
        Sales_GST_Type = serialized.data['Sales_GST_Type']
        Sales_VAT_Type = serialized.data['Sales_VAT_Type']
        Purchase_VAT_Type = serialized.data['Purchase_VAT_Type']
        MultiUnit = serialized.data['MultiUnit']
        PriceCategory = serialized.data['PriceCategory']
        InclusiveRateSales = serialized.data['InclusiveRateSales']
        InclusiveRatePurchase = serialized.data['InclusiveRatePurchase']
        SalesPriceUpdate = serialized.data['SalesPriceUpdate']
        AllowCashReceiptMoreSaleAmt = serialized.data['AllowCashReceiptMoreSaleAmt']
        AllowAdvanceReceiptinSales = serialized.data['AllowAdvanceReceiptinSales']
        ReferenceBillNo = serialized.data['ReferenceBillNo']
        BlockSalesPrice = serialized.data['BlockSalesPrice']

        if QtyDecimalPoint.isnumeric() and PriceDecimalPoint.isnumeric() and RoundingFigure.isnumeric():

            if Negative_Stock_Show == None:
                Negative_Stock_Show = False

            if Kitchen_Print == None:
                Kitchen_Print = False

            if Order_Print == None:
                Order_Print = False

            if Print_After_Save_Active == None:
                Print_After_Save_Active = False

            Action = "M"
            User = request.user.id

            def max_id():
                general_settings_id = administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID).aggregate(Max('GeneralSettingsID'))
                general_settings_id = general_settings_id.get(
                    'GeneralSettingsID__max', 0)
                general_settings_id += 1
                return general_settings_id

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="MultiUnit").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="MultiUnit",
                    SettingsValue=MultiUnit,
                    BranchID=1, GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="MultiUnit"
                ).update(
                    SettingsValue=MultiUnit,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="PriceCategory").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="PriceCategory",
                    SettingsValue=PriceCategory,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="PriceCategory"
                ).update(
                    SettingsValue=PriceCategory,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="InclusiveRateSales").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="InclusiveRateSales",
                    SettingsValue=InclusiveRateSales,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="InclusiveRateSales"
                ).update(
                    SettingsValue=InclusiveRateSales,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action)

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="InclusiveRatePurchase").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="InclusiveRatePurchase",
                    SettingsValue=InclusiveRatePurchase,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="InclusiveRatePurchase"
                ).update(
                    SettingsValue=InclusiveRatePurchase,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="SalesPriceUpdate").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="SalesPriceUpdate",
                    SettingsValue=SalesPriceUpdate,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="SalesPriceUpdate"
                ).update(
                    SettingsValue=SalesPriceUpdate,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action)

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="AllowCashReceiptMoreSaleAmt").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="AllowCashReceiptMoreSaleAmt",
                    SettingsValue=AllowCashReceiptMoreSaleAmt,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="AllowCashReceiptMoreSaleAmt"
                ).update(
                    SettingsValue=AllowCashReceiptMoreSaleAmt,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action)

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="AllowAdvanceReceiptinSales").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="AllowAdvanceReceiptinSales",
                    SettingsValue=AllowAdvanceReceiptinSales,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="AllowAdvanceReceiptinSales"
                ).update(
                    SettingsValue=AllowAdvanceReceiptinSales,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action)

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ReferenceBillNo").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="ReferenceBillNo",
                    SettingsValue=ReferenceBillNo,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="ReferenceBillNo"
                ).update(
                    SettingsValue=ReferenceBillNo,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action)

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="BlockSalesPrice").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="BlockSalesPrice",
                    SettingsValue=BlockSalesPrice,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="BlockSalesPrice"
                ).update(
                    SettingsValue=BlockSalesPrice,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action)

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="PreDateTransaction").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="PreDateTransaction",
                    SettingsValue=PreDateTransaction,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="PreDateTransaction"
                ).update(
                    SettingsValue=PreDateTransaction,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action)

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="PostDateTransaction").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="PostDateTransaction",
                    SettingsValue=PostDateTransaction,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="PostDateTransaction"
                ).update(
                    SettingsValue=PostDateTransaction,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action)

            administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID,
                                                                  SettingsType="Purchase_GST_Type"
                                                                  ).update(
                SettingsValue=Purchase_GST_Type,
                UpdatedDate=today,
                CreatedUserID=User,
                Action=Action
            )
            administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID,
                                                                  SettingsType="Sales_GST_Type"
                                                                  ).update(
                SettingsValue=Sales_GST_Type,
                UpdatedDate=today,
                CreatedUserID=User,
                Action=Action
            )
            administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID,
                                                                  SettingsType="Sales_VAT_Type"
                                                                  ).update(
                SettingsValue=Sales_VAT_Type,
                UpdatedDate=today,
                CreatedUserID=User,
                Action=Action
            )
            administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID,
                                                                  SettingsType="Purchase_VAT_Type"
                                                                  ).update(
                SettingsValue=Purchase_VAT_Type,
                UpdatedDate=today,
                CreatedUserID=User,
                Action=Action
            )
            administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID,
                                                                  SettingsType="Free_Quantity_In_Sales"
                                                                  ).update(
                SettingsValue=Free_Quantity_In_Sales,
                UpdatedDate=today,
                CreatedUserID=User,
                Action=Action
            )
            administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID,
                                                                  SettingsType="Free_Quantity_In_Purchase"
                                                                  ).update(
                SettingsValue=Free_Quantity_In_Purchase,
                UpdatedDate=today,
                CreatedUserID=User,
                Action=Action
            )
            administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID,
                                                                  SettingsType="Show_Sales_Type"
                                                                  ).update(
                SettingsValue=Show_Sales_Type,
                UpdatedDate=today,
                CreatedUserID=User,
                Action=Action
            )
            administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID,
                                                                  SettingsType="Show_Purchase_Type"
                                                                  ).update(
                SettingsValue=Show_Purchase_Type,
                UpdatedDate=today,
                CreatedUserID=User,
                Action=Action
            )
            administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID,
                                                                  SettingsType="VAT"
                                                                  ).update(
                SettingsValue=VAT,
                UpdatedDate=today,
                CreatedUserID=User,
                Action=Action
            )
            administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID,
                                                                  SettingsType="GST"
                                                                  ).update(
                SettingsValue=GST,
                UpdatedDate=today,
                CreatedUserID=User,
                Action=Action
            )
            administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID,
                                                                  SettingsType="TAX1"
                                                                  ).update(
                SettingsValue=Tax1,
                UpdatedDate=today,
                CreatedUserID=User,
                Action=Action
            )
            administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID,
                                                                  SettingsType="TAX2"
                                                                  ).update(
                SettingsValue=Tax2,
                UpdatedDate=today,
                CreatedUserID=User,
                Action=Action
            )
            administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID,
                                                                  SettingsType="TAX3"
                                                                  ).update(
                SettingsValue=Tax3,
                UpdatedDate=today,
                CreatedUserID=User,
                Action=Action
            )
            # administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID,SettingsType="Trading").update(SettingsValue=Trading, UpdatedDate=today, CreatedUserID=User, Action=Action)
            # administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID,SettingsType="Restaurant").update(SettingsValue=Restaurant, UpdatedDate=today, CreatedUserID=User, Action=Action)
            administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID,
                                                                  SettingsType="QtyDecimalPoint"
                                                                  ).update(
                SettingsValue=QtyDecimalPoint,
                UpdatedDate=today,
                CreatedUserID=User,
                Action=Action
            )
            administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID,
                                                                  SettingsType="PriceDecimalPoint"
                                                                  ).update(
                SettingsValue=PriceDecimalPoint,
                UpdatedDate=today,
                CreatedUserID=User,
                Action=Action
            )
            administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID,
                                                                  SettingsType="RoundingFigure"
                                                                  ).update(
                SettingsValue=RoundingFigure,
                UpdatedDate=today,
                CreatedUserID=User,
                Action=Action
            )
            administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID,
                                                                  SettingsType="Additional_Discount"
                                                                  ).update(
                SettingsValue=Additional_Discount,
                UpdatedDate=today,
                CreatedUserID=User,
                Action=Action
            )
            administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID,
                                                                  SettingsType="Bill_Discount"
                                                                  ).update(
                SettingsValue=Bill_Discount,
                UpdatedDate=today,
                CreatedUserID=User,
                Action=Action
            )
            administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID,
                                                                  SettingsType="Negatine_Stock"
                                                                  ).update(
                SettingsValue=Negative_Stock_Show,
                UpdatedDate=today,
                CreatedUserID=User,
                Action=Action
            )

            # if administrations_models.GeneralSettings.objects.get(CompanyID=CompanyID,SettingsType="Restaurant").SettingsValue == "true":
            #     administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID,SettingsType="Increment_Qty_In_POS").update(SettingsValue=Increment_Qty_In_POS, UpdatedDate=today, CreatedUserID=User, Action=Action)
            #     administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID,SettingsType="Kitchen_Print").update(SettingsValue=Kitchen_Print, UpdatedDate=today, CreatedUserID=User, Action=Action)
            #     administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID,SettingsType="Order_Print").update(SettingsValue=Order_Print, UpdatedDate=today, CreatedUserID=User, Action=Action)
            #     administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID,SettingsType="Print_After_Save_Active").update(SettingsValue=Print_After_Save_Active, UpdatedDate=today, CreatedUserID=User, Action=Action)
            # else:
            #     administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID,SettingsType="Increment_Qty_In_POS").update(SettingsValue="false", UpdatedDate=today, CreatedUserID=User, Action=Action)
            #     administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID,SettingsType="Kitchen_Print").update(SettingsValue="false", UpdatedDate=today, CreatedUserID=User, Action=Action)
            #     administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID,SettingsType="Order_Print").update(SettingsValue="false", UpdatedDate=today, CreatedUserID=User, Action=Action)
            #     administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID,SettingsType="Print_After_Save_Active").update(SettingsValue="false", UpdatedDate=today, CreatedUserID=User, Action=Action)
            general_settings = administrations_models.GeneralSettings.objects.filter(
                CompanyID=CompanyID)

            Purchase_VAT_Type_name = ''
            Sales_VAT_Type_name = ''
            Sales_GST_Type_name = ''
            Purchase_GST_Type_name = ''
            if TransactionTypes.objects.filter(CompanyID=CompanyID, TransactionTypesID=Purchase_VAT_Type, BranchID=BranchID).exists():
                Purchase_VAT_Type_name = get_object_or_404(TransactionTypes.objects.filter(CompanyID=CompanyID,
                                                                                           TransactionTypesID=Purchase_VAT_Type,
                                                                                           BranchID=BranchID)).Name

            if TransactionTypes.objects.filter(CompanyID=CompanyID, TransactionTypesID=Sales_VAT_Type, BranchID=BranchID).exists():
                Sales_VAT_Type_name = get_object_or_404(TransactionTypes.objects.filter(CompanyID=CompanyID,
                                                                                        TransactionTypesID=Sales_VAT_Type,
                                                                                        BranchID=BranchID)).Name

            if TransactionTypes.objects.filter(CompanyID=CompanyID, TransactionTypesID=Sales_GST_Type, BranchID=BranchID).exists():
                Sales_GST_Type_name = get_object_or_404(TransactionTypes.objects.filter(CompanyID=CompanyID,
                                                                                        TransactionTypesID=Sales_GST_Type,
                                                                                        BranchID=BranchID)).Name

            if TransactionTypes.objects.filter(CompanyID=CompanyID, TransactionTypesID=Purchase_GST_Type, BranchID=BranchID).exists():
                Purchase_GST_Type_name = get_object_or_404(TransactionTypes.objects.filter(CompanyID=CompanyID,
                                                                                           TransactionTypesID=Purchase_GST_Type,
                                                                                           BranchID=BranchID)).Name

            for settings in general_settings:

                administrations_models.GeneralSettings_Log.objects.create(
                    TransactionID=settings.GeneralSettingsID,
                    BranchID=settings.BranchID,
                    GroupName=settings.GroupName,
                    SettingsType=settings.SettingsType,
                    SettingsValue=settings.SettingsValue,
                    Action=settings.Action,
                    CreatedDate=settings.CreatedDate,
                    UpdatedDate=settings.UpdatedDate,
                    CreatedUserID=settings.CreatedUserID,
                    CompanyID=CompanyID
                )
            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'GeneralSettings', 'Create', 'GeneralSettings Created Successfully.', "GeneralSettings Created Successfully")
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "Purchase_VAT_Type_name": Purchase_VAT_Type_name,
                "Sales_VAT_Type_name": Sales_VAT_Type_name,
                "Sales_GST_Type_name": Sales_GST_Type_name,
                "Purchase_GST_Type_name": Purchase_GST_Type_name,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'GeneralSettings', 'Create', 'GeneralSettings Created Failed.', "enterd invalid number")
            response_data = {
                "StatusCode": 6001,
                "message": "You enterd an invalid number"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        #request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'GeneralSettings', 'Create', 'GeneralSettings Created Failed.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def general_settings_list(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    BranchID = data['BranchID']
    check_PreDateTransaction = 10
    check_PostDateTransaction = 10
    PreDateTransaction = 10
    PostDateTransaction = 10
    if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        instances = administrations_models.GeneralSettings.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID)
        check_Purchase_GST_Type = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Purchase_GST_Type").SettingsValue
        check_Sales_GST_Type = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Sales_GST_Type").SettingsValue
        check_Sales_VAT_Type = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Sales_VAT_Type").SettingsValue
        check_Purchase_VAT_Type = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Purchase_VAT_Type").SettingsValue
        check_Free_Quantity_In_Sales = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Free_Quantity_In_Sales").SettingsValue
        check_Free_Quantity_In_Purchase = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Free_Quantity_In_Purchase").SettingsValue
        check_Show_Sales_Type = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Show_Sales_Type").SettingsValue
        check_Show_Purchase_Type = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Show_Purchase_Type").SettingsValue
        check_VAT = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="VAT").SettingsValue
        check_GST = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="GST").SettingsValue
        check_TAX1 = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="TAX1").SettingsValue
        check_TAX2 = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="TAX2").SettingsValue
        check_TAX3 = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="TAX3").SettingsValue
        check_Trading = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Trading").SettingsValue
        check_Restaurant = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Restaurant").SettingsValue
        check_QtyDecimalPoint = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="QtyDecimalPoint").SettingsValue
        check_PriceDecimalPoint = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="PriceDecimalPoint").SettingsValue

        if administrations_models.GeneralSettings.objects.filter(
            CompanyID=CompanyID, SettingsType="PreDateTransaction").exists():
            check_PreDateTransaction = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="PreDateTransaction").SettingsValue
        if administrations_models.GeneralSettings.objects.filter(
            CompanyID=CompanyID, SettingsType="PostDateTransaction").exists():
            check_PostDateTransaction = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="PostDateTransaction").SettingsValue
        check_Additional_Discount = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Additional_Discount").SettingsValue
        check_Bill_Discount = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Bill_Discount").SettingsValue
        check_Negatine_Stock = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Negatine_Stock").SettingsValue
        check_Increment_Qty_In_POS = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Increment_Qty_In_POS").SettingsValue
        check_Kitchen_Print = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Kitchen_Print").SettingsValue
        check_Order_Print = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Order_Print").SettingsValue
        check_Print_After_Save_Active = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Print_After_Save_Active").SettingsValue
        QtyDecimalPoint = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="QtyDecimalPoint").SettingsValue

        if administrations_models.GeneralSettings.objects.filter(
            CompanyID=CompanyID, SettingsType="PreDateTransaction").exists():
            PreDateTransaction = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="PreDateTransaction").SettingsValue
        if administrations_models.GeneralSettings.objects.filter(
            CompanyID=CompanyID, SettingsType="PostDateTransaction").exists():
            PostDateTransaction = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="PostDateTransaction").SettingsValue

        PriceDecimalPoint = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="PriceDecimalPoint").SettingsValue
        RoundingFigure = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="RoundingFigure").SettingsValue

        sales_gst_types = TransactionTypes.objects.filter(
            MasterTypeID=6, BranchID=BranchID, CompanyID=CompanyID)
        sales_gst_types = TransactionTypesSerializer(
            sales_gst_types, many=True)
        purchase_gst_types = TransactionTypes.objects.filter(
            MasterTypeID=7, BranchID=BranchID, CompanyID=CompanyID)
        purchase_gst_types = TransactionTypesSerializer(
            purchase_gst_types, many=True)
        vat_types = TransactionTypes.objects.filter(
            MasterTypeID=8, BranchID=BranchID, CompanyID=CompanyID)
        vat_types = TransactionTypesSerializer(vat_types, many=True)
        MultiUnit = False
        PriceCategory = False
        InclusiveRateSales = False
        InclusiveRatePurchase = False
        SalesPriceUpdate = False
        AllowCashReceiptMoreSaleAmt = False
        AllowAdvanceReceiptinSales = False
        ReferenceBillNo = False
        BlockSalesPrice = False
        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="MultiUnit").exists():
            MultiUnit = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="MultiUnit").SettingsValue
            if MultiUnit == "True":
                MultiUnit = True
            else:
                MultiUnit = False

        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="PriceCategory").exists():
            PriceCategory = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="PriceCategory").SettingsValue
            if PriceCategory == "True":
                PriceCategory = True
            else:
                PriceCategory = False

        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="InclusiveRateSales").exists():
            InclusiveRateSales = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="InclusiveRateSales").SettingsValue
            if InclusiveRateSales == "True":
                InclusiveRateSales = True
            else:
                InclusiveRateSales = False

        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="InclusiveRatePurchase").exists():
            InclusiveRatePurchase = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="InclusiveRatePurchase").SettingsValue
            if InclusiveRatePurchase == "True":
                InclusiveRatePurchase = True
            else:
                InclusiveRatePurchase = False

        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="SalesPriceUpdate").exists():
            SalesPriceUpdate = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="SalesPriceUpdate").SettingsValue
            if SalesPriceUpdate == "True":
                SalesPriceUpdate = True
            else:
                SalesPriceUpdate = False

        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="AllowCashReceiptMoreSaleAmt").exists():
            AllowCashReceiptMoreSaleAmt = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="AllowCashReceiptMoreSaleAmt").SettingsValue
            
            if AllowCashReceiptMoreSaleAmt == "True":
                AllowCashReceiptMoreSaleAmt = True
            else:
                AllowCashReceiptMoreSaleAmt = False

        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="AllowAdvanceReceiptinSales").exists():
            AllowAdvanceReceiptinSales = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="AllowAdvanceReceiptinSales").SettingsValue

            if AllowAdvanceReceiptinSales == "True":
                AllowAdvanceReceiptinSales = True
            else:
                AllowAdvanceReceiptinSales = False
                
        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ReferenceBillNo").exists():
            ReferenceBillNo = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="ReferenceBillNo").SettingsValue

            if ReferenceBillNo == "True":
                ReferenceBillNo = True
            else:
                ReferenceBillNo = False

        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="BlockSalesPrice").exists():
            BlockSalesPrice = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="BlockSalesPrice").SettingsValue
            if BlockSalesPrice == "True":
                BlockSalesPrice = True
            else:
                BlockSalesPrice = False

        if check_TAX1 == 'false':
            check_TAX1 = ''

        if check_TAX2 == 'false':
            check_TAX2 = ''

        if check_TAX3 == 'false':
            check_TAX3 = ''

        if check_Additional_Discount == 'false':
            check_Additional_Discount = ''

        if check_Bill_Discount == 'false':
            check_Bill_Discount = ''

        if check_Negatine_Stock == 'false':
            check_Negatine_Stock = ''

        if check_Increment_Qty_In_POS == 'false':
            check_Increment_Qty_In_POS = ''

        if check_Kitchen_Print == 'false':
            check_Kitchen_Print = ''

        if check_Order_Print == 'false':
            check_Order_Print = ''

        if check_Print_After_Save_Active == 'false':
            check_Print_After_Save_Active = ''

        if check_Trading == 'false':
            check_Trading = ''

        if check_Restaurant == 'false':
            check_Restaurant = ''

        if check_Trading == 'true':
            Business_Type = 'Trading'
        else:
            Business_Type = 'Restaurant'

        if check_VAT == 'false':
            check_VAT = ''

        if check_GST == 'false':
            check_GST = ''

        if check_Free_Quantity_In_Sales == 'false':
            check_Free_Quantity_In_Sales = ''

        if check_Free_Quantity_In_Purchase == 'false':
            check_Free_Quantity_In_Purchase = ''

        if check_Show_Sales_Type == 'false':
            check_Show_Sales_Type = ''

        if check_Show_Purchase_Type == 'false':
            check_Show_Purchase_Type = ''

        # if check_VAT == 'true':
        #     Tax_Active = 'VAT'
        # else:
        #     Tax_Active = 'GST'


        dic = {
            "check_Purchase_GST_Type": check_Purchase_GST_Type,
            "check_Sales_GST_Type": check_Sales_GST_Type,
            "check_Sales_VAT_Type": check_Sales_VAT_Type,
            "check_Purchase_VAT_Type": check_Purchase_VAT_Type,
            "check_Free_Quantity_In_Sales": check_Free_Quantity_In_Sales,
            "check_Free_Quantity_In_Purchase": check_Free_Quantity_In_Purchase,
            "check_Show_Sales_Type": check_Show_Sales_Type,
            "check_Show_Purchase_Type": check_Show_Purchase_Type,
            "check_VAT": check_VAT,
            "check_GST": check_GST,
            "check_TAX1": check_TAX1,
            "check_TAX2": check_TAX2,
            "check_TAX3": check_TAX3,
            "check_Trading": check_Trading,
            "check_Restaurant": check_Restaurant,
            "check_QtyDecimalPoint": check_QtyDecimalPoint,
            "check_PriceDecimalPoint": check_PriceDecimalPoint,
            "check_PreDateTransaction": check_PreDateTransaction,
            "check_PostDateTransaction": check_PostDateTransaction,
            "check_Additional_Discount": check_Additional_Discount,
            "check_Bill_Discount": check_Bill_Discount,
            "check_Negatine_Stock": check_Negatine_Stock,
            "check_Increment_Qty_In_POS": check_Increment_Qty_In_POS,
            "check_Kitchen_Print": check_Kitchen_Print,
            "check_Order_Print": check_Order_Print,
            "check_Print_After_Save_Active": check_Print_After_Save_Active,
            "QtyDecimalPoint": QtyDecimalPoint,
            "PreDateTransaction": PreDateTransaction,
            "PostDateTransaction": PostDateTransaction,
            "PriceDecimalPoint": PriceDecimalPoint,
            "RoundingFigure": RoundingFigure,
            "Business_Type": Business_Type,
            "sales_gst_types": sales_gst_types.data,
            "purchase_gst_types": purchase_gst_types.data,
            "vat_types": vat_types.data,
            "MultiUnit": MultiUnit,
            "PriceCategory": PriceCategory,
            "InclusiveRateSales": InclusiveRateSales,
            "InclusiveRatePurchase": InclusiveRatePurchase,
            "SalesPriceUpdate": SalesPriceUpdate,
            "AllowCashReceiptMoreSaleAmt": AllowCashReceiptMoreSaleAmt,
            "AllowAdvanceReceiptinSales": AllowAdvanceReceiptinSales,
            "ReferenceBillNo": ReferenceBillNo,
            "BlockSalesPrice": BlockSalesPrice,
            # "sales_vat_types" : sales_vat_types.data,
            # "purchase_vat_types" : purchase_vat_types.data,
            # "Tax_Active" : Tax_Active,
        }
        #request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'GeneralSettings', 'List', 'GeneralSettings List Viewed Successfully.', "GeneralSettings List Viewed Successfully.")
        response_data = {
            "StatusCode": 6000,
            "data": dic,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Brands Not Found in this BranchID!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def get_defaults(request):
    data = request.data
    CompanyID = data['CompanyID']
    BranchID = data['BranchID']
    userId = data['userId']
    Sales_Account_name = ""
    Sales_Return_Account_name = ""
    Purchase_Account_name = ""
    Purchase_Return_Account_name = ""
    Cash_Account_name = ""
    Bank_Account_name = ""
    Warehouse_name = ""
    VAT_Type_name = ""
    Sales_GST_Type_name = ""
    Purchase_GST_Type_name = ""
    Sales_VAT_Type_name = ""
    Purchase_VAT_Type_name = ""
    CompanyName = get_company(CompanyID).CompanyName
    CRNumber = get_company(CompanyID).CRNumber
    Description = get_company(CompanyID).Description

    today = str(datetime.date.today())
    ExpiryDate = CompanySettings.objects.get(pk=CompanyID).ExpiryDate
    DefaultAccountForUser = False
    Sales_Account = 85
    Sales_Return_Account = 86
    Purchase_Account = 69
    Purchase_Return_Account = 70
    Cash_Account = 1
    Bank_Account = 92
    WarehouseID = 1

    if UserTable.objects.filter(CompanyID__pk=CompanyID, customer__user=userId).exists():
        user_table_instance = UserTable.objects.get(
            CompanyID__pk=CompanyID, customer__user=userId)
        DefaultAccountForUser = UserTable.objects.get(
            CompanyID=CompanyID, customer__user__pk=userId).DefaultAccountForUser
        Cash_Account = user_table_instance.Cash_Account
        Bank_Account = user_table_instance.Bank_Account
        Sales_Account = user_table_instance.Sales_Account
        Sales_Return_Account = user_table_instance.Sales_Return_Account
        Purchase_Account = user_table_instance.Purchase_Account
        Purchase_Return_Account = user_table_instance.Purchase_Return_Account
        ExpiryDate = user_table_instance.ExpiryDate

        # else:
        #     Sales_Account = 85
        #     Sales_Return_Account = 86
        #     Purchase_Account = 69
        #     Purchase_Return_Account = 70
        #     Cash_Account = 1
        #     Bank_Account = 92
        # VAT_Type = 32
        # Sales_GST_Type = 20
        # Purchase_GST_Type = 26

        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Sales_Account, BranchID=BranchID).exists():
            Sales_Account_name = get_object_or_404(AccountLedger.objects.filter(
                CompanyID=CompanyID, LedgerID=Sales_Account, BranchID=BranchID)).LedgerName

        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Sales_Return_Account, BranchID=BranchID).exists():
            Sales_Return_Account_name = get_object_or_404(AccountLedger.objects.filter(
                CompanyID=CompanyID, LedgerID=Sales_Return_Account, BranchID=BranchID)).LedgerName

        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Purchase_Account, BranchID=BranchID).exists():
            Purchase_Account_name = get_object_or_404(AccountLedger.objects.filter(
                CompanyID=CompanyID, LedgerID=Purchase_Account, BranchID=BranchID)).LedgerName

        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Purchase_Return_Account, BranchID=BranchID).exists():
            Purchase_Return_Account_name = get_object_or_404(AccountLedger.objects.filter(
                CompanyID=CompanyID, LedgerID=Purchase_Return_Account, BranchID=BranchID)).LedgerName

        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Cash_Account, BranchID=BranchID).exists():
            Cash_Account_name = get_object_or_404(AccountLedger.objects.filter(
                CompanyID=CompanyID, LedgerID=Cash_Account, BranchID=BranchID)).LedgerName

        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Bank_Account, BranchID=BranchID).exists():
            Bank_Account_name = get_object_or_404(AccountLedger.objects.filter(
                CompanyID=CompanyID, LedgerID=Bank_Account, BranchID=BranchID)).LedgerName

        # if Employee.objects.filter(CompanyID=CompanyID,EmployeeID=EmployeeID,BranchID=BranchID).exists():
        #     Employee_name = get_object_or_404(Employee.objects.filter(CompanyID=CompanyID,EmployeeID=EmployeeID,BranchID=BranchID)).FirstName

        # if TransactionTypes.objects.filter(CompanyID=CompanyID,TransactionTypesID=VAT_Type,BranchID=BranchID).exists():
        #     VAT_Type_name = get_object_or_404(TransactionTypes.objects.filter(CompanyID=CompanyID,TransactionTypesID=VAT_Type,BranchID=BranchID)).Name

        # if TransactionTypes.objects.filter(CompanyID=CompanyID,TransactionTypesID=Sales_GST_Type,BranchID=BranchID).exists():
        #     Sales_GST_Type_name = get_object_or_404(TransactionTypes.objects.filter(CompanyID=CompanyID,TransactionTypesID=Sales_GST_Type,BranchID=BranchID)).Name

        # if TransactionTypes.objects.filter(CompanyID=CompanyID,TransactionTypesID=Purchase_GST_Type,BranchID=BranchID).exists():
        #     Purchase_GST_Type_name = get_object_or_404(TransactionTypes.objects.filter(CompanyID=CompanyID,TransactionTypesID=Purchase_GST_Type,BranchID=BranchID)).Name

        if Warehouse.objects.filter(CompanyID=CompanyID, WarehouseID=WarehouseID, BranchID=BranchID).exists():
            Warehouse_name = get_object_or_404(Warehouse.objects.filter(
                CompanyID=CompanyID, WarehouseID=WarehouseID, BranchID=BranchID)).WarehouseName

    Country = ''
    CountryName = ''
    State = ''
    StateName = ''
    CompanyLogo = ''
    if CompanySettings.objects.filter(id=CompanyID).exists():
        Country = CompanySettings.objects.get(id=CompanyID).Country.id
        CountryName = CompanySettings.objects.get(
            id=CompanyID).Country.Country_Name
        State = CompanySettings.objects.get(id=CompanyID).State.id
        StateName = CompanySettings.objects.get(id=CompanyID).State.Name
        CompanyLogo = CompanySettings.objects.get(id=CompanyID).CompanyLogo

    if FinancialYear.objects.filter(CompanyID=CompanyID, IsClosed=False).exists():
        financialyear = FinancialYear.objects.filter(
            CompanyID=CompanyID, IsClosed=False).first()
        financial_FromDate = financialyear.FromDate
        financial_ToDate = financialyear.ToDate
    else:
        try:
            financialyear = FinancialYear.objects.filter(
                CompanyID=CompanyID).first()
            financial_FromDate = financialyear.FromDate
            financial_ToDate = financialyear.ToDate
        except:
            financial_FromDate = ""
            financial_ToDate = ""
            # response_data = {
            #     "StatusCode": 6001,
            #     "title": "Financial Year not found",
            #     "message": "Financial Year not found please contact admin"
            # }
            # return Response(response_data, status=status.HTTP_200_OK)

    if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        check_VAT = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="VAT").SettingsValue
        check_GST = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="GST").SettingsValue
        check_TAX1 = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="TAX1").SettingsValue
        check_TAX2 = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="TAX2").SettingsValue
        check_TAX3 = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="TAX3").SettingsValue
        check_Trading = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Trading").SettingsValue
        check_Restaurant = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Restaurant").SettingsValue
        check_QtyDecimalPoint = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="QtyDecimalPoint").SettingsValue
        check_PriceDecimalPoint = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="PriceDecimalPoint").SettingsValue
        check_Additional_Discount = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Additional_Discount").SettingsValue
        check_Bill_Discount = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Bill_Discount").SettingsValue
        check_Negatine_Stock = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Negatine_Stock").SettingsValue
        check_Increment_Qty_In_POS = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Increment_Qty_In_POS").SettingsValue
        check_Kitchen_Print = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Kitchen_Print").SettingsValue
        check_Order_Print = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Order_Print").SettingsValue
        check_Print_After_Save_Active = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Print_After_Save_Active").SettingsValue
        QtyDecimalPoint = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="QtyDecimalPoint").SettingsValue
        PriceDecimalPoint = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="PriceDecimalPoint").SettingsValue
        Show_Sales_Type = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Show_Sales_Type").SettingsValue
        Show_Purchase_Type = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Show_Purchase_Type").SettingsValue
        Sales_VAT_Type = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Sales_VAT_Type").SettingsValue
        Purchase_VAT_Type = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Purchase_VAT_Type").SettingsValue
        Sales_GST_Type = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Sales_GST_Type").SettingsValue
        Purchase_GST_Type = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="Purchase_GST_Type").SettingsValue

        RoundingFigure = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="RoundingFigure").SettingsValue

        Sales_VAT_Type = int(Sales_VAT_Type)
        Purchase_VAT_Type = int(Purchase_VAT_Type)
        Sales_GST_Type = int(Sales_GST_Type)
        Purchase_GST_Type = int(Purchase_GST_Type)
        # if TransactionTypes.objects.filter(CompanyID=CompanyID,TransactionTypesID=VAT_Type,BranchID=BranchID).exists():
        #     VAT_Type_name = get_object_or_404(TransactionTypes.objects.filter(CompanyID=CompanyID,TransactionTypesID=VAT_Type,BranchID=BranchID)).Name
        MultiUnit = ""
        PreDateTransaction = ""
        PostDateTransaction = ""
        PriceCategory = False
        BlockSalesPrice = False
        AllowCashReceiptMoreSaleAmt = False
        AllowAdvanceReceiptinSales = False
        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="MultiUnit").exists():
            MultiUnit = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="MultiUnit").SettingsValue
            if MultiUnit == "True":
                MultiUnit = True
            else:
                MultiUnit = False

        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="PriceCategory").exists():
            PriceCategory = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="PriceCategory").SettingsValue
            if PriceCategory == "True":
                PriceCategory = True
           

        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="PreDateTransaction").exists():
            PreDateTransaction = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="PreDateTransaction").SettingsValue
        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="PostDateTransaction").exists():
            PostDateTransaction = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="PostDateTransaction").SettingsValue

        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="BlockSalesPrice").exists():
            BlockSalesPrice = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="BlockSalesPrice").SettingsValue
            if BlockSalesPrice == "True":
                BlockSalesPrice = True
            else:
                BlockSalesPrice = False


        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="AllowCashReceiptMoreSaleAmt").exists():
            AllowCashReceiptMoreSaleAmt = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="AllowCashReceiptMoreSaleAmt").SettingsValue
            if AllowCashReceiptMoreSaleAmt == "True":
                AllowCashReceiptMoreSaleAmt = True
            else:
                AllowCashReceiptMoreSaleAmt = False

        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="AllowAdvanceReceiptinSales").exists():
            AllowAdvanceReceiptinSales = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="AllowAdvanceReceiptinSales").SettingsValue
            if AllowAdvanceReceiptinSales == "True":
                AllowAdvanceReceiptinSales = True
            else:
                AllowAdvanceReceiptinSales = False

        if TransactionTypes.objects.filter(CompanyID=CompanyID, TransactionTypesID=Sales_VAT_Type, BranchID=BranchID).exists():
            Sales_VAT_Type_name = get_object_or_404(TransactionTypes.objects.filter(
                CompanyID=CompanyID, TransactionTypesID=Sales_VAT_Type, BranchID=BranchID)).Name

        if TransactionTypes.objects.filter(CompanyID=CompanyID, TransactionTypesID=Purchase_VAT_Type, BranchID=BranchID).exists():
            Purchase_VAT_Type_name = get_object_or_404(TransactionTypes.objects.filter(
                CompanyID=CompanyID, TransactionTypesID=Purchase_VAT_Type, BranchID=BranchID)).Name

        if TransactionTypes.objects.filter(CompanyID=CompanyID, TransactionTypesID=Sales_GST_Type, BranchID=BranchID).exists():
            Sales_GST_Type_name = get_object_or_404(TransactionTypes.objects.filter(
                CompanyID=CompanyID, TransactionTypesID=Sales_GST_Type, BranchID=BranchID)).Name

        if TransactionTypes.objects.filter(CompanyID=CompanyID, TransactionTypesID=Purchase_GST_Type, BranchID=BranchID).exists():
            Purchase_GST_Type_name = get_object_or_404(TransactionTypes.objects.filter(
                CompanyID=CompanyID, TransactionTypesID=Purchase_GST_Type, BranchID=BranchID)).Name

        if Show_Sales_Type == 'false':
            Show_Sales_Type = ''

        if Show_Purchase_Type == 'false':
            Show_Purchase_Type = ''

        if check_TAX1 == 'false':
            check_TAX1 = ''

        if check_TAX2 == 'false':
            check_TAX2 = ''

        if check_TAX3 == 'false':
            check_TAX3 = ''

        if check_Additional_Discount == 'false':
            check_Additional_Discount = ''

        if check_Bill_Discount == 'false':
            check_Bill_Discount = ''

        if check_Negatine_Stock == 'false':
            check_Negatine_Stock = ''

        if check_Increment_Qty_In_POS == 'false':
            check_Increment_Qty_In_POS = ''

        if check_Kitchen_Print == 'false':
            check_Kitchen_Print = ''

        if check_Order_Print == 'false':
            check_Order_Print = ''

        if check_Print_After_Save_Active == 'false':
            check_Print_After_Save_Active = ''

        if check_Trading == 'false':
            check_Trading = ''

        if check_Restaurant == 'false':
            check_Restaurant = ''

        if check_Trading == 'true':
            Business_Type = 'Trading'
        else:
            Business_Type = 'Restaurant'

        if check_VAT == 'false':
            check_VAT = ''

        if check_GST == 'false':
            check_GST = ''

        # if check_VAT == 'true':
        #     Tax_Active = 'VAT'
        # else:
        #     Tax_Active = 'GST'
        template = "template1"
        IsDefaultThermalPrinter = True
        PageSize = "3.14"
        IsCompanyLogo = True
        IsCompanyName = True
        IsDescription = True
        IsAddress = True
        IsMobile = True
        IsEmail = True
        IsTaxNo = True
        IsCRNo = True
        IsCurrentBalance = True
        SalesInvoiceTrName = "Sales Invoice"
        SalesOrderTrName = "Sales Order"
        SalesReturnTrName = "Sales Return"
        PurchaseInvoiceTrName = "Purchase Invoice"
        PurchaseOrderTrName = "Purchase Order"
        PurchaseReturnTrName = "Purchase Return"
        CashRecieptTrName = "Cash Reciept"
        BankRecieptTrName = "Bank Reciept"
        CashPaymentTrName = "Cash Payment"
        BankPaymentTrName = "Bank Payment"
        IsInclusiveTaxUnitPrice = True
        IsInclusiveTaxNetAmount = True
        IsFlavour = True
        IsShowDescription = True
        IsTotalQuantity = True
        IsTaxDetails = True
        IsReceivedAmount = True
        SalesInvoiceFooter = ""
        SalesReturnFooter = ""
        SalesOrderFooter = ""
        PurchaseInvoiceFooter = ""
        PurchaseOrderFooter = ""
        PurchaseReturnFooter = ""
        CashRecieptFooter = ""
        BankRecieptFooter = ""
        CashPaymentFooter = ""
        BankPaymentFooter = ""
        if administrations_models.PrintSettings.objects.filter(CompanyID=CompanyID).exists():
            template = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).template
            IsDefaultThermalPrinter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsDefaultThermalPrinter
            PageSize = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).PageSize
            IsCompanyLogo = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsCompanyLogo
            IsCompanyName = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsCompanyName
            IsDescription = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsDescription
            IsAddress = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsAddress
            IsMobile = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsMobile
            IsEmail = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsEmail
            IsTaxNo = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsTaxNo
            IsCRNo = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsCRNo
            IsCurrentBalance = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsCurrentBalance
            SalesInvoiceTrName = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).SalesInvoiceTrName
            SalesOrderTrName = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).SalesOrderTrName
            SalesReturnTrName = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).SalesReturnTrName
            PurchaseInvoiceTrName = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).PurchaseInvoiceTrName
            PurchaseOrderTrName = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).PurchaseOrderTrName
            PurchaseReturnTrName = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).PurchaseReturnTrName
            CashRecieptTrName = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).CashRecieptTrName
            BankRecieptTrName = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).BankRecieptTrName
            CashPaymentTrName = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).CashPaymentTrName
            BankPaymentTrName = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).BankPaymentTrName
            IsInclusiveTaxUnitPrice = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsInclusiveTaxUnitPrice
            IsInclusiveTaxNetAmount = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsInclusiveTaxNetAmount
            IsFlavour = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsFlavour
            IsShowDescription = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsShowDescription
            IsTotalQuantity = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsTotalQuantity
            IsTaxDetails = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsTaxDetails
            IsReceivedAmount = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsReceivedAmount
            SalesInvoiceFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).SalesInvoiceFooter
            SalesReturnFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).SalesReturnFooter
            SalesOrderFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).SalesOrderFooter
            PurchaseInvoiceFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).PurchaseInvoiceFooter
            PurchaseOrderFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).PurchaseOrderFooter
            PurchaseReturnFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).PurchaseReturnFooter
            CashRecieptFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).CashRecieptFooter
            BankRecieptFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).BankRecieptFooter
            CashPaymentFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).CashPaymentFooter
            BankPaymentFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).BankPaymentFooter

        print_response = {
            "template": template,
            "IsDefaultThermalPrinter": IsDefaultThermalPrinter,
            "PageSize": PageSize,
            "IsCompanyLogo": IsCompanyLogo,
            "IsCompanyName": IsCompanyName,
            "IsDescription": IsDescription,
            "IsAddress": IsAddress,
            "IsMobile": IsMobile,
            "IsEmail": IsEmail,
            "IsTaxNo": IsTaxNo,
            "IsCRNo": IsCRNo,
            "IsCurrentBalance": IsCurrentBalance,
            "SalesInvoiceTrName": SalesInvoiceTrName,
            "SalesOrderTrName": SalesOrderTrName,
            "SalesReturnTrName": SalesReturnTrName,
            "PurchaseInvoiceTrName": PurchaseInvoiceTrName,
            "PurchaseOrderTrName": PurchaseOrderTrName,
            "PurchaseReturnTrName": PurchaseReturnTrName,
            "CashRecieptTrName": CashRecieptTrName,
            "BankRecieptTrName": BankRecieptTrName,
            "CashPaymentTrName": CashPaymentTrName,
            "BankPaymentTrName": BankPaymentTrName,
            "IsInclusiveTaxUnitPrice": IsInclusiveTaxUnitPrice,
            "IsInclusiveTaxNetAmount": IsInclusiveTaxNetAmount,
            "IsFlavour": IsFlavour,
            "IsShowDescription": IsShowDescription,
            "IsTotalQuantity": IsTotalQuantity,
            "IsTaxDetails": IsTaxDetails,
            "IsReceivedAmount": IsReceivedAmount,
            "SalesInvoiceFooter": SalesInvoiceFooter,
            "SalesReturnFooter": SalesReturnFooter,
            "SalesOrderFooter": SalesOrderFooter,
            "PurchaseInvoiceFooter": PurchaseInvoiceFooter,
            "PurchaseOrderFooter": PurchaseOrderFooter,
            "PurchaseReturnFooter": PurchaseReturnFooter,
            "CashRecieptFooter": CashRecieptFooter,
            "BankRecieptFooter": BankRecieptFooter,
            "CashPaymentFooter": CashPaymentFooter,
            "BankPaymentFooter": BankPaymentFooter,

        }

        dic = {
            "MultiUnit": MultiUnit,
            "PriceCategory":PriceCategory,
            "BlockSalesPrice" : BlockSalesPrice,
            "AllowCashReceiptMoreSaleAmt" : AllowCashReceiptMoreSaleAmt,
            "AllowAdvanceReceiptinSales" : AllowAdvanceReceiptinSales,
            "PreDateTransaction": PreDateTransaction,
            "PostDateTransaction": PostDateTransaction,
            "check_VAT": check_VAT,
            "check_GST": check_GST,
            "check_TAX1": check_TAX1,
            "check_TAX2": check_TAX2,
            "check_TAX3": check_TAX3,
            "check_Trading": check_Trading,
            "check_Restaurant": check_Restaurant,
            "check_QtyDecimalPoint": check_QtyDecimalPoint,
            "check_PriceDecimalPoint": check_PriceDecimalPoint,
            "check_Additional_Discount": check_Additional_Discount,
            "check_Bill_Discount": check_Bill_Discount,
            "check_Negatine_Stock": check_Negatine_Stock,
            "check_Increment_Qty_In_POS": check_Increment_Qty_In_POS,
            "check_Kitchen_Print": check_Kitchen_Print,
            "check_Order_Print": check_Order_Print,
            "check_Print_After_Save_Active": check_Print_After_Save_Active,
            "QtyDecimalPoint": QtyDecimalPoint,
            "PriceDecimalPoint": PriceDecimalPoint,
            "RoundingFigure": RoundingFigure,
            "Business_Type": Business_Type,
            "today": today,
            "ExpiryDate": ExpiryDate,
            # "Tax_Active" : Tax_Active,
            "VAT_Type_name": VAT_Type_name,
            "Sales_VAT_Type_name": Sales_VAT_Type_name,
            "Purchase_VAT_Type_name": Purchase_VAT_Type_name,
            "Sales_GST_Type_name": Sales_GST_Type_name,
            "Purchase_GST_Type_name": Purchase_GST_Type_name,
            "Sales_GST_Type": Sales_GST_Type,
            "Purchase_GST_Type": Purchase_GST_Type,
            "Sales_VAT_Type": Sales_VAT_Type,
            "Purchase_VAT_Type": Purchase_VAT_Type,
            "Show_Sales_Type": Show_Sales_Type,
            "Show_Purchase_Type": Show_Purchase_Type,


        }

        success = 6000
        message = "success!"
        return Response(
            {
                'success': success,
                'StatusCode': success,
                'message': message,
                'error': None,
                "DefaultAccountForUser": DefaultAccountForUser,
                "Cash_Account": Cash_Account,
                "Bank_Account": Bank_Account,
                "Warehouse": WarehouseID,
                "Sales_Account": Sales_Account,
                "Sales_Return_Account": Sales_Return_Account,
                "Purchase_Account": Purchase_Account,
                "Purchase_Return_Account": Purchase_Return_Account,
                "Sales_GST_Type": Sales_GST_Type,
                "Purchase_GST_Type": Purchase_GST_Type,
                # "VAT_Type" : VAT_Type,
                "settingsData": dic,
                "Sales_Account_name": Sales_Account_name,
                "Sales_Return_Account_name": Sales_Return_Account_name,
                "Purchase_Account_name": Purchase_Account_name,
                "Purchase_Return_Account_name": Purchase_Return_Account_name,
                "Cash_Account_name": Cash_Account_name,
                "Bank_Account_name": Bank_Account_name,
                # "VAT_Type_name" : VAT_Type_name,
                "Sales_GST_Type_name": Sales_GST_Type_name,
                "Purchase_GST_Type_name": Purchase_GST_Type_name,
                "Warehouse_name": Warehouse_name,
                "Country": Country,
                "CountryName": CountryName,
                "CompanyLogo": CompanyLogo.url,
                "State": State,
                "StateName": StateName,
                "CompanyName": CompanyName,
                "CRNumber": CRNumber,
                "Description": Description,
                "financial_FromDate": financial_FromDate,
                "financial_ToDate": financial_ToDate,
                "print_response": print_response,
            },
            status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Not Found"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def activity_logs(request):
    if administrations_models.Activity_Log.objects.exists():
        instances = administrations_models.Activity_Log.objects.all()
        serializer = ActivityLogSerializer(instances, many=True)
        response_data = {
            "StatusCode": 6000,
            "data": serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "No activity found"
        }
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def activity_log(request, pk):
    if administrations_models.Activity_Log.objects.filter(pk=pk).exists():
        instance = administrations_models.Activity_Log.objects.get(pk=pk)
        serializer = ActivityLogSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serializer.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Activity not found."
        }

    return Response(response_data, status=status.HTTP_200_OK)


# @api_view(['POST'])
# @permission_classes((IsAuthenticated,))
# @renderer_classes((JSONRenderer,))
# def forgot_password(request):
#     data = request.data
#     today = datetime.datetime.now()
#     serialized = ForgorPasswordSerializer(data=request.data)
#     if serialized.is_valid():
#         email = serialized.data['email']
#         if User.objects.filter(email=email).exists():
#             template_name = ''
#             subject = 'MESSAGE'
#             context = {
#                 'email' : email,
#             }
#             html_content = render_to_string(template_name,context)

#             send_email(email,subject,content,name,phone,html_content)

#             response_data = {
#                 "StatusCode" : 6000,
#                 "title" : f'A mail have sent to {email}',
#                 "message" : 'Please check your Email'
#             }
#             return Response(response_data, status=status.HTTP_200_OK)
#         else:
#             response_data = {
#                 "StatusCode" : 6001,
#                 "title" : f'Account not found in your {email}',
#                 "message" : 'Please create a new account'
#             }
#             return Response(response_data, status=status.HTTP_200_OK)
#     else:
#         response_data = {
#             "StatusCode" : 6001,
#             "message" : generate_serializer_errors(serialized._errors)
#         }
#         return Response(response_data, status=status.HTTP_200_OK)


# @receiver(reset_password_token_created)
# def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
#     """
#     Handles password reset tokens
#     When a token is created, an e-mail needs to be sent to the user
#     :param sender: View Class that sent the signal
#     :param instance: View Instance that sent the signal
#     :param reset_password_token: Token Model Object
#     :param args:
#     :param kwargs:
#     :return:
#     """
#     # send an e-mail to the user
#     context = {
#         'current_user': reset_password_token.user,
#         'username': reset_password_token.user.username,
#         'email': reset_password_token.user.email,
#         'reset_password_url': "{}?token={}".format(
#             instance.request.build_absolute_uri(reverse('password_reset:reset-password-confirm')),
#             reset_password_token.key)
#     }
#     template_name = 'email/email_token.html'
#     subject = 'MESSAGE'
#     context = {
#         'current_user': reset_password_token.user,
#         'username': reset_password_token.user.username,
#         'email': reset_password_token.user.email,
#         'reset_password_url': "{}?token={}".format(
#             instance.request.build_absolute_uri(reverse('password_reset:reset-password-confirm')),
#             reset_password_token.key)
#     }
#     html_content = render_to_string(template_name,context)
#     user_email = reset_password_token.user.email
#     content = ''
#     name = ''
#     phone = ''
#     send_email(user_email,subject,content,name,phone,html_content)

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param args:
    :param kwargs:
    :return:
    """
    # send an e-mail to the user
    # 'reset_password_url': "{}?token={}".format(
    #         instance.request.build_absolute_uri(reverse('password_reset:reset-password-confirm')),
    #         reset_password_token.key),
    context = {
        'current_user': reset_password_token.user,
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        'reset_password_url': "http://localhost:8000/password-confirm",
        'token': reset_password_token.key
    }

    # render email text
    # email_html_message = render_to_string('email/user_reset_password.html', context)
    email_html_message = render_to_string('email/email.html', context)
    email_plaintext_message = render_to_string(
        'email/user_reset_password.txt', context)

    msg = EmailMultiAlternatives(
        # title:
        "Password Reset for {title}".format(title="viknbooks.com"),
        # message:
        email_plaintext_message,
        # from:
        "noreply@somehost.local",
        # to:
        [reset_password_token.user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()
