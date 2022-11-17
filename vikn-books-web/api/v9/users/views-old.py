from brands.models import UserTable, User_Log, UserType, CompanySettings, SoftwareVersion, SoftwareVersionLog, MasterType, MasterType_Log
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login
from rest_framework.renderers import JSONRenderer
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v9.users.serializers import UserTableSerializer, UserListSerializer, UserTableRestSerializer, UserTypeSerializer, UserTypeRestSerializer, LoginSerializer, SignupSerializer, CreateCompanySerializer, CreateEmployeeSerializer, CreateFinancialYearSerializer, MyCompaniesSerializer, CompaniesSerializer, UserAccountsSerializer, AccountLedgerSerializer, WarehouseSerializer, TransactionTypesSerializer, UserTypesSerializer, GeneralSettingsSerializer, GeneralSettingsListSerializer, UserViewSerializer, CustomerUserViewSerializer, UpdateSerializer, CustomersSerializer, UserTypeSerializer, ActivityLogSerializer
from api.v9.brands.serializers import ListSerializer
from api.v9.users.functions import generate_serializer_errors
from brands.models import GeneralSettings, UserTable, AccountLedger, TransactionTypes, Warehouse, User_Log, UserType, Designation, Department, Employee, Employee_Log, FinancialYear, FinancialYear_Log, Customer, State, Country
from rest_framework import status
from brands import models as administrations_models
from django.contrib.auth.models import User, Group
from api.v9.users.functions import get_auto_id
from brands import models
from api.v9.general.functions import get_current_role
from users.models import CompanyEmployee, CompanyFinancialYear, CompanyAccountLedger
import datetime
from users.functions import get_EmployeeCode, get_LedgerCode, get_auto_LedgerID
from brands.functions import createdb
from django.utils.translation import ugettext_lazy as _
import requests
from django.shortcuts import get_object_or_404
from django.contrib.auth import logout
from users.models import CustomerUser, DatabaseStore
from api.v9.ledgerPosting.functions import convertOrderdDict
from main.functions import get_company, activity_log, get_visitors_details
from main.utils import send_html_mail
from django.db.models import Max, Q
from api.v9.users.functions import send_email, get_master_auto_id
from rest_framework.views import APIView
from rest_framework import parsers, renderers, status
from django_rest_passwordreset.models import ResetPasswordToken
from django_rest_passwordreset.views import get_password_reset_token_expiry_time
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from datetime import timedelta
from api.v9.users.serializers import CustomTokenSerializer, SoftwareVersionSerializer
from django.core.mail import EmailMultiAlternatives, EmailMessage, send_mail
from django.dispatch import receiver
from django.template.loader import render_to_string
from django_rest_passwordreset.signals import reset_password_token_created
from mailqueue.models import MailerMessage
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from datetime import date
import json
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime as newDatetime
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from testproject.settings import DEFAULT_FROM_EMAIL
from django.template import loader


def call_paginator_all(model_object, page_number, items_per_page):
    paginator = Paginator(model_object, items_per_page)
    content = paginator.page(page_number)
    return content


def list_pagination(list_value, items_per_page, page_no):
    paginator_object = Paginator(list_value, items_per_page)
    get_value = paginator_object.page(page_no).object_list
    return get_value


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

            # request , company, log_type, user, source, action, message, description
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


def send_mail_verification(user, request):
    context = {
        'email': user.email,
        'domain': request.META['HTTP_ORIGIN'],
        'site_name': 'viknbooks.com',
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'user': user,
        'token': default_token_generator.make_token(user),
        'current_user': user.username,
        'username': user.username,
        'reset_password_url': f"http://localhost:3000/signUp-verification/{user.id}",
        # 'reset_password_url': f"https://www.viknbooks.vikncodes.com/signUp-verification/{user.id}",
        # 'reset_password_url': f"https://www.viknbooks.com/signUp-verification/{user.id}",
    }

    subject_template_name = 'email/user_reset_password.txt'
    email_template_name = 'email/signup_email.html'

    email_html_message = render_to_string('email/signup_email.html', context)

    # subject = loader.render_to_string(subject_template_name, c)
    # subject = ''.join(subject.splitlines())
    # email = loader.render_to_string(email_template_name, c)

    subject = "Email Verification for {title}".format(title="viknbooks.com"),

    send_mail(subject, email_html_message, DEFAULT_FROM_EMAIL,
              [user.email], fail_silently=False)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def user_signup(request):
    today = datetime.datetime.now()
    serialized = SignupSerializer(data=request.data)
    data = request.data
    if serialized.is_valid():
        first_name = serialized.validated_data['first_name']
        last_name = serialized.validated_data['last_name']
        username = serialized.validated_data['username']
        email = serialized.validated_data['email']
        password1 = serialized.validated_data['password1']
        password2 = serialized.validated_data['password2']

        try:
            Phone = data['phone']
        except:
            Phone = None

        try:
            country = data['Country']
        except:
            country = None

        try:
            state = data['State']
        except:
            state = None

        country_ins = None
        state_ins = None
        print("_++_______________++++++++++++++")
        print(country)
        print(state)
        if Country.objects.filter(id=country).exists():
            country_ins = Country.objects.get(id=country)

        if State.objects.filter(id=state).exists():
            state_ins = State.objects.get(id=state)

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
        elif User.objects.filter(email__iexact=email).exists():
            message = "A user with that email already exists."
            error = True
        elif len(username) < min_username_length:
            message = ("Username must have at least %i characters" %
                       min_password_length)
            error = True
        else:
            username = username

        if not error:
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password1,
                is_superuser=False,
                is_active=False
            )
            Customer.objects.create(
                user=user,
                Phone=Phone,
                Country=country_ins,
                State=state_ins,
            )

            send_mail_verification(user, request)

            # context = {
            #     'current_user': username,
            #     'username': username,
            #     # 'email': reset_password_token.user.email,
            #     'email': email,
            #     'reset_password_url': f"http://localhost:3000/signUp-verification/{user.id}",
            #     # 'reset_password_url': f"https://www.viknbooks.vikncodes.com//signUp-verification/{user.id}",
            #     # 'reset_password_url': f"https://www.viknbooks.com/signUp-verification/{user.id}",
            #     'token': "reset_password_token.key"
            # }

            # email_html_message = render_to_string('email/signup_email.html', context)

            # email_plaintext_message = render_to_string(
            #     'email/user_reset_password.txt', context)

            # msg = EmailMultiAlternatives(
            #     # title:
            #     "Email Verification for {title}".format(title="viknbooks.com"),
            #     # message:
            #     email_plaintext_message,
            #     # from:
            #     "noreply@somehost.local",
            #     # to:
            #     [email]
            # )

            # subject = "Email Verification for {title}".format(title="viknbooks.com")
            # html_content = email_html_message
            # recipient_list = email
            # sender = "noreply@somehost.local"
            # send_html_mail(subject,html_content,sender,recipient_list)

            # msg = EmailMessage(
            #     # title:
            #     "Email Verification for {title}".format(title="viknbooks.com"),
            #     # message:
            #     email_html_message,
            #     # from:
            #     "noreply@somehost.local",
            #     # to:
            #     [email]
            # )
            # # msg.attach_alternative(email_html_message, "text/html")
            # msg.content_subtype = "html"
            # msg.send()
            # serialized.save()

            # to_email = email
            # mail_subject = "Email Verification for {title}".format(title="viknbooks.com")
            # message = "your_content"

            # message = render_to_string('email/signup_email.html', context)
            # send_message = EmailMessage(mail_subject, message, to=[to_email])
            # send_message.content_subtype = "html"
            # send_message.send()

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


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def signUp_verified(request):
    today = datetime.datetime.now()
    data = request.data
    UserID = data['UserID']

    if User.objects.filter(id=UserID).exists():
        user = User.objects.filter(id=UserID).update(is_active=True)

        response_data = {
            "StatusCode": 6000,
        }
    else:
        response_data = {
            "StatusCode": 6001,
        }

    return Response(response_data, status=status.HTTP_200_OK)
    # else:
    #     response_data = {
    #         "StatusCode": 6001,
    #         "message": message
    #     }

    # return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def user_view(request, pk):
    instance = Customer.objects.get(user__pk=pk)

    customer_serialized = CustomerUserViewSerializer(
        instance, context={"request": request})
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
            if photo:
                instance.photo = photo

            instance.DateOfBirth = DateOfBirth
            instance.Country = Countries
            instance.Phone = Phone
            instance.State = States
            instance.City = City
            instance.Address = Address
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
    is_verified = False
    customer_ins = None
    if serialized.is_valid():

        username = serialized.data['username']
        password = serialized.data['password']

        if User.objects.filter(email=username).exists():
            email = username
            username = User.objects.get(email=email).username

        if User.objects.filter(username=username).exists():
            user_ins = User.objects.get(username=username)
            if user_ins.is_active == True:
                is_verified = True

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
            if request.is_secure():
                protocol = "https://"

            web_host = request.get_host()
            request_url = protocol + web_host + "/api/v1/auth/token/"
            response = requests.post(request_url, headers=headers, data=data)
            if response.status_code == 200:
                token_datas = response.json()
                LastToken = token_datas['access']
                # info= get_visitors_details(request)
                # mac_address = info['mac-address']
                # mac_adds = ['74:40:bb:d9:bd:25']
                # if not mac_address in mac_adds:
                if Customer.objects.filter(user__username=username).exists():
                    customer_ins = Customer.objects.filter(
                        user__username=username).first()
                    customer_ins.LastLoginToken = LastToken
                    customer_ins.save()

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

                        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Sales_Account).exists():
                            Sales_Account_name = get_object_or_404(AccountLedger.objects.filter(
                                CompanyID=CompanyID, LedgerID=Sales_Account)).LedgerName

                        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Sales_Return_Account).exists():
                            Sales_Return_Account_name = get_object_or_404(AccountLedger.objects.filter(
                                CompanyID=CompanyID, LedgerID=Sales_Return_Account)).LedgerName

                        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Purchase_Account).exists():
                            Purchase_Account_name = get_object_or_404(AccountLedger.objects.filter(
                                CompanyID=CompanyID, LedgerID=Purchase_Account)).LedgerName

                        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Purchase_Return_Account).exists():
                            Purchase_Return_Account_name = get_object_or_404(AccountLedger.objects.filter(
                                CompanyID=CompanyID, LedgerID=Purchase_Return_Account)).LedgerName

                        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Cash_Account).exists():
                            Cash_Account_name = get_object_or_404(AccountLedger.objects.filter(
                                CompanyID=CompanyID, LedgerID=Cash_Account)).LedgerName

                        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Bank_Account).exists():
                            Bank_Account_name = get_object_or_404(AccountLedger.objects.filter(
                                CompanyID=CompanyID, LedgerID=Bank_Account)).LedgerName

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
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="VAT").SettingsValue
                            check_GST = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="GST").SettingsValue
                            check_TAX1 = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="TAX1").SettingsValue
                            check_TAX2 = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="TAX2").SettingsValue
                            check_TAX3 = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="TAX3").SettingsValue
                            check_Trading = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="Trading").SettingsValue
                            check_Restaurant = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="Restaurant").SettingsValue
                            check_QtyDecimalPoint = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="QtyDecimalPoint").SettingsValue
                            check_PriceDecimalPoint = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="PriceDecimalPoint").SettingsValue
                            check_PreDateTransaction = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="PreDateTransaction").SettingsValue
                            check_PostDateTransaction = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="PostDateTransaction").SettingsValue
                            check_Additional_Discount = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="Additional_Discount").SettingsValue
                            check_Bill_Discount = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="Bill_Discount").SettingsValue
                            check_Negatine_Stock = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="Negatine_Stock").SettingsValue
                            check_Increment_Qty_In_POS = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="Increment_Qty_In_POS").SettingsValue
                            check_Kitchen_Print = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="Kitchen_Print").SettingsValue
                            check_Order_Print = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="Order_Print").SettingsValue
                            check_Print_After_Save_Active = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="Print_After_Save_Active").SettingsValue
                            QtyDecimalPoint = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="QtyDecimalPoint").SettingsValue
                            PriceDecimalPoint = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="PriceDecimalPoint").SettingsValue
                            PreDateTransaction = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="PreDateTransaction").SettingsValue
                            PostDateTransaction = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="PostDateTransaction").SettingsValue

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

                company_count = CompanySettings.objects.filter(
                    owner=data['user_id']).count()
                ExpiryDate = ""
                CompanyName = ""
                if customer_ins.LastLoginCompanyID:
                    CompanyID = customer_ins.LastLoginCompanyID
                else:
                    if company_count == 1:
                        CompanyID = CompanySettings.objects.get(
                            owner=data['user_id'], is_deleted=False).id
                        ExpiryDate = CompanySettings.objects.get(
                            owner=data['user_id']).ExpiryDate
                    else:
                        CompanyID = CompanySettings.objects.filter(
                            owner=data['user_id'], is_deleted=False).last().id
                if CompanyID:
                    company_instance = CompanySettings.objects.get(
                        id=CompanyID, is_deleted=False)
                    CompanyName = company_instance.CompanyName
                    CountryName = company_instance.Country.Country_Name
                    CountryID = company_instance.Country.id
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
                        "CompanyName": CompanyName,
                        "CountryName": CountryName,
                        "CountryID": CountryID,
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
                        'username': username,
                        'company_count': company_count,
                        'ExpiryDate': ExpiryDate
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
            if is_verified == False:
                error = "Please Verify Your Email to Login"
            else:
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
def user_login_admins(request):
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
    is_verified = False
    if serialized.is_valid():

        username = serialized.data['username']
        password = serialized.data['password']

        if User.objects.filter(email=username).exists():
            email = username
            username = User.objects.get(email=email).username

        if User.objects.filter(username=username).exists():
            user_ins = User.objects.get(username=username)
            if user_ins.is_active == True:
                is_verified = True

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
            if request.is_secure():
                protocol = "https://"

            web_host = request.get_host()
            request_url = protocol + web_host + "/api/v1/auth/token/"
            response = requests.post(request_url, headers=headers, data=data)
            if response.status_code == 200:
                # token_datas = response.json()
                # LastToken = token_datas['access']
                # info= get_visitors_details(request)
                # mac_address = info['mac-address']
                # mac_adds = ['74:40:bb:d9:bd:25']
                # if not mac_address in mac_adds:
                #     if Customer.objects.filter(user__username=username).exists():
                #         customer_ins = Customer.objects.filter(user__username=username).first()
                #         customer_ins.LastLoginToken = LastToken
                #         customer_ins.save()

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
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="VAT").SettingsValue
                            check_GST = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="GST").SettingsValue
                            check_TAX1 = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="TAX1").SettingsValue
                            check_TAX2 = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="TAX2").SettingsValue
                            check_TAX3 = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="TAX3").SettingsValue
                            check_Trading = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="Trading").SettingsValue
                            check_Restaurant = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="Restaurant").SettingsValue
                            check_QtyDecimalPoint = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="QtyDecimalPoint").SettingsValue
                            check_PriceDecimalPoint = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="PriceDecimalPoint").SettingsValue
                            check_PreDateTransaction = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="PreDateTransaction").SettingsValue
                            check_PostDateTransaction = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="PostDateTransaction").SettingsValue
                            check_Additional_Discount = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="Additional_Discount").SettingsValue
                            check_Bill_Discount = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="Bill_Discount").SettingsValue
                            check_Negatine_Stock = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="Negatine_Stock").SettingsValue
                            check_Increment_Qty_In_POS = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="Increment_Qty_In_POS").SettingsValue
                            check_Kitchen_Print = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="Kitchen_Print").SettingsValue
                            check_Order_Print = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="Order_Print").SettingsValue
                            check_Print_After_Save_Active = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="Print_After_Save_Active").SettingsValue
                            QtyDecimalPoint = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="QtyDecimalPoint").SettingsValue
                            PriceDecimalPoint = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="PriceDecimalPoint").SettingsValue
                            PreDateTransaction = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="PreDateTransaction").SettingsValue
                            PostDateTransaction = administrations_models.GeneralSettings.objects.get(
                                BranchID=BranchID, CompanyID=CompanyID, SettingsType="PostDateTransaction").SettingsValue

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

                company_count = CompanySettings.objects.filter(
                    owner=data['user_id']).count()
                ExpiryDate = ""
                if company_count == 1:
                    CompanyID = CompanySettings.objects.get(
                        owner=data['user_id']).id
                    ExpiryDate = CompanySettings.objects.get(
                        owner=data['user_id']).ExpiryDate

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
                        'username': username,
                        'company_count': company_count,
                        'ExpiryDate': ExpiryDate
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
            if is_verified == False:
                error = "Please Verify Your Email to Login"
            else:
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
        Permission = i['Permission']
        print(ExpiryDate)
        ExpiryDate = date.today().strftime("%Y-%m-%d")
        if i['ExpiryDate'] != None:
            ExpiryDate = i['ExpiryDate']
        dic = {
            'id': id,
            'CompanyName': CompanyName,
            'company_type': company_type,
            'ExpiryDate': ExpiryDate,
            'Permission': Permission,
        }
        data.append(dic)

    for i in member_company_json:
        id = i['id']
        CompanyName = i['CompanyName']
        company_type = i['company_type']
        Permission = i['Permission']
        ExpiryDate = date.today().strftime("%Y-%m-%d")
        if i['ExpiryDate'] != None:
            ExpiryDate = i['ExpiryDate']
        dic = {
            'id': id,
            'CompanyName': CompanyName,
            'company_type': company_type,
            'ExpiryDate': ExpiryDate,
            'Permission': Permission,
        }
        data.append(dic)

    tes_arry = []
    final_array = []
    for i in data:
        if not i['id'] in tes_arry:
            tes_arry.append(i['id'])
            final_array.append(i)

    CurrentVersion = 0
    MinimumVersion = 0
    if SoftwareVersion.objects.exists():
        CurrentVersion = SoftwareVersion.objects.get().CurrentVersion
        MinimumVersion = SoftwareVersion.objects.get().MinimumVersion

    software_version_dic = {
        "CurrentVersion": CurrentVersion,
        "MinimumVersion": MinimumVersion,
    }
    response_data = {
        "StatusCode": 6000,
        "data": final_array,
        "SoftwareVersion": software_version_dic
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
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    BranchID = data['BranchID']
    try:
        loyalty_point_value = data['loyalty_PointValue']
    except:
        loyalty_point_value = ""

    serialized = GeneralSettingsSerializer(data=request.data)
    if serialized.is_valid():
        try:
            EnableShippingCharge = serialized.data['EnableShippingCharge']
        except:
            EnableShippingCharge = False

        QtyDecimalPoint = serialized.data['QtyDecimalPoint']
        PriceDecimalPoint = serialized.data['PriceDecimalPoint']
        PreDateTransaction = serialized.data['PreDateTransaction']
        PostDateTransaction = serialized.data['PostDateTransaction']
        RoundingFigure = serialized.data['RoundingFigure']
        RoundOffPurchase = serialized.data['RoundOffPurchase']
        RoundOffSales = serialized.data['RoundOffSales']
        VAT = serialized.data['VAT']
        GST = serialized.data['GST']
        Tax1 = serialized.data['Tax1']
        Tax2 = serialized.data['Tax2']
        Tax3 = serialized.data['Tax3']
        Additional_Discount = serialized.data['Additional_Discount']
        Bill_Discount = serialized.data['Bill_Discount']
        Negative_Stock_Show = serialized.data['Negative_Stock_Show']
        Increment_Qty_In_POS = serialized.data['Increment_Qty_In_POS']
        Kitchen_Print = serialized.data['Kitchen_Print']
        Order_Print = serialized.data['Order_Print']
        Print_After_Save_Active = serialized.data['Print_After_Save_Active']
        Show_Sales_Type = str(serialized.data['Show_Sales_Type'])
        Show_Purchase_Type = serialized.data['Show_Purchase_Type']
        Purchase_GST_Type = serialized.data['Purchase_GST_Type']
        Sales_GST_Type = serialized.data['Sales_GST_Type']
        Sales_VAT_Type = serialized.data['Sales_VAT_Type']
        Purchase_VAT_Type = serialized.data['Purchase_VAT_Type']
        MultiUnit = serialized.data['MultiUnit']
        Loyalty_Point_Expire = serialized.data['Loyalty_Point_Expire']
        is_Loyalty_SalesReturn_MinimumSalePrice = serialized.data[
            'is_Loyalty_SalesReturn_MinimumSalePrice']
        AllowNegativeStockSales = serialized.data['AllowNegativeStockSales']
        PriceCategory = serialized.data['PriceCategory']
        InclusiveRateSales = serialized.data['InclusiveRateSales']
        InclusiveRatePurchase = serialized.data['InclusiveRatePurchase']
        InclusiveRateWorkOrder = serialized.data['InclusiveRateWorkOrder']
        ShowDiscountInSales = serialized.data['ShowDiscountInSales']
        ShowSupplierInSales = serialized.data['ShowSupplierInSales']
        ShowDueBalanceInSales = serialized.data['ShowDueBalanceInSales']
        ShowDueBalanceInPurchase = serialized.data['ShowDueBalanceInPurchase']
        ShowEmployeesInSales = serialized.data['ShowEmployeesInSales']
        EnableSerialNoInSales = serialized.data['EnableSerialNoInSales']
        EnableItemCodeNoInSales = serialized.data['EnableItemCodeNoInSales']
        EnableSalesManInSales = serialized.data['EnableSalesManInSales']
        ShowWarrantyPeriodInProduct = serialized.data['ShowWarrantyPeriodInProduct']
        ShowDescriptionInSales = serialized.data['ShowDescriptionInSales']
        AllowExtraSerielNos = serialized.data['AllowExtraSerielNos']
        Free_Quantity_In_Sales = serialized.data['Free_Quantity_In_Sales']
        Free_Quantity_In_Purchase = serialized.data['Free_Quantity_In_Purchase']
        ShowCustomerInPurchase = serialized.data['ShowCustomerInPurchase']
        ShowManDateAndExpDatePurchase = serialized.data['ShowManDateAndExpDatePurchase']
        ShowDiscountInPurchase = serialized.data['ShowDiscountInPurchase']
        ShowDiscountInPayments = serialized.data['ShowDiscountInPayments']
        ShowDiscountInReceipts = serialized.data['ShowDiscountInReceipts']
        EnableLoyaltySettings = serialized.data['EnableLoyaltySettings']
        CustomerBasedPrint = serialized.data['CustomerBasedPrint']
        EnableCardNetWork = serialized.data['EnableCardNetWork']
        BlockTransactionsByDate = serialized.data['BlockTransactionsByDate']
        EnableCardDetails = serialized.data['EnableCardDetails']
        SalesPriceUpdate = serialized.data['SalesPriceUpdate']
        PurchasePriceUpdate = serialized.data['PurchasePriceUpdate']
        AllowCashReceiptMoreSaleAmt = serialized.data['AllowCashReceiptMoreSaleAmt']
        AllowCashReceiptMorePurchaseAmt = serialized.data['AllowCashReceiptMorePurchaseAmt']
        AllowAdvanceReceiptinSales = serialized.data['AllowAdvanceReceiptinSales']
        AllowAdvanceReceiptinPurchase = serialized.data['AllowAdvanceReceiptinPurchase']
        AllowQtyDividerinSales = serialized.data['AllowQtyDividerinSales']
        ReferenceBillNo = serialized.data['ReferenceBillNo']
        BlockSalesPrice = serialized.data['BlockSalesPrice']
        VoucherNoAutoGenerate = serialized.data['VoucherNoAutoGenerate']
        EnableVoucherNoUserWise = serialized.data['EnableVoucherNoUserWise']
        ShowSalesPriceInPurchase = serialized.data['ShowSalesPriceInPurchase']
        ShowSettingsinSales = serialized.data['ShowSettingsinSales']
        ShowSettingsinPurchase = serialized.data['ShowSettingsinPurchase']
        EnableProductBatchWise = serialized.data['EnableProductBatchWise']
        AllowUpdateBatchPriceInSales = serialized.data['AllowUpdateBatchPriceInSales']
        EnableTransilationInProduct = serialized.data['EnableTransilationInProduct']
        ShowPositiveStockInSales = serialized.data['ShowPositiveStockInSales']
        ShowNegativeBatchInSales = serialized.data['ShowNegativeBatchInSales']
        CreateBatchForWorkOrder = serialized.data['CreateBatchForWorkOrder']
        ShowYearMonthCalanderInWorkOrder = serialized.data['ShowYearMonthCalanderInWorkOrder']
        KFC = serialized.data['KFC']
        blockSaleByBillDisct = serialized.data['blockSaleByBillDisct']
        BatchCriteria = serialized.data['BatchCriteria']

        if Bill_Discount == "True" or Bill_Discount == True:
            Bill_Discount = "true"
        if Bill_Discount == "False" or Bill_Discount == False:
            Bill_Discount = "false"

        print("================------------------===========")

        if KFC == "true":
            KFC = True
        else:
            KFC = False

        if QtyDecimalPoint.isnumeric() and PriceDecimalPoint.isnumeric() and RoundingFigure.isnumeric() and RoundOffPurchase.isnumeric() and RoundOffSales.isnumeric():

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

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="loyalty_point_value").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="loyalty_point_value",
                    SettingsValue=loyalty_point_value,
                    BranchID=1, GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="loyalty_point_value"
                ).update(
                    SettingsValue=loyalty_point_value,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="Loyalty_Point_Expire").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="Loyalty_Point_Expire",
                    SettingsValue=Loyalty_Point_Expire,
                    BranchID=1, GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="Loyalty_Point_Expire"
                ).update(
                    SettingsValue=Loyalty_Point_Expire,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="is_Loyalty_SalesReturn_MinimumSalePrice").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="is_Loyalty_SalesReturn_MinimumSalePrice",
                    SettingsValue=is_Loyalty_SalesReturn_MinimumSalePrice,
                    BranchID=1, GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="is_Loyalty_SalesReturn_MinimumSalePrice"
                ).update(
                    SettingsValue=is_Loyalty_SalesReturn_MinimumSalePrice,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )

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

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="AllowNegativeStockSales").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="AllowNegativeStockSales",
                    SettingsValue=AllowNegativeStockSales,
                    BranchID=1, GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="AllowNegativeStockSales"
                ).update(
                    SettingsValue=AllowNegativeStockSales,
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

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="InclusiveRateWorkOrder").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="InclusiveRateWorkOrder",
                    SettingsValue=InclusiveRateWorkOrder,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="InclusiveRateWorkOrder"
                ).update(
                    SettingsValue=InclusiveRateWorkOrder,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowDiscountInSales").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="ShowDiscountInSales",
                    SettingsValue=ShowDiscountInSales,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="ShowDiscountInSales"
                ).update(
                    SettingsValue=ShowDiscountInSales,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowSupplierInSales").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="ShowSupplierInSales",
                    SettingsValue=ShowSupplierInSales,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="ShowSupplierInSales"
                ).update(
                    SettingsValue=ShowSupplierInSales,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="EnableShippingCharge").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="EnableShippingCharge",
                    SettingsValue=EnableShippingCharge,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="EnableShippingCharge"
                ).update(
                    SettingsValue=EnableShippingCharge,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowDueBalanceInSales").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="ShowDueBalanceInSales",
                    SettingsValue=ShowDueBalanceInSales,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="ShowDueBalanceInSales"
                ).update(
                    SettingsValue=ShowDueBalanceInSales,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowDueBalanceInPurchase").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="ShowDueBalanceInPurchase",
                    SettingsValue=ShowDueBalanceInPurchase,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="ShowDueBalanceInPurchase"
                ).update(
                    SettingsValue=ShowDueBalanceInPurchase,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowEmployeesInSales").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="ShowEmployeesInSales",
                    SettingsValue=ShowEmployeesInSales,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="ShowEmployeesInSales"
                ).update(
                    SettingsValue=ShowEmployeesInSales,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="EnableSerialNoInSales").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="EnableSerialNoInSales",
                    SettingsValue=EnableSerialNoInSales,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="EnableSerialNoInSales"
                ).update(
                    SettingsValue=EnableSerialNoInSales,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="EnableItemCodeNoInSales").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="EnableItemCodeNoInSales",
                    SettingsValue=EnableItemCodeNoInSales,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="EnableItemCodeNoInSales"
                ).update(
                    SettingsValue=EnableItemCodeNoInSales,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="EnableSalesManInSales").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="EnableSalesManInSales",
                    SettingsValue=EnableSalesManInSales,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="EnableSalesManInSales"
                ).update(
                    SettingsValue=EnableSalesManInSales,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowWarrantyPeriodInProduct").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="ShowWarrantyPeriodInProduct",
                    SettingsValue=ShowWarrantyPeriodInProduct,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="ShowWarrantyPeriodInProduct"
                ).update(
                    SettingsValue=ShowWarrantyPeriodInProduct,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowDescriptionInSales").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="ShowDescriptionInSales",
                    SettingsValue=ShowDescriptionInSales,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="ShowDescriptionInSales"
                ).update(
                    SettingsValue=ShowDescriptionInSales,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="AllowExtraSerielNos").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="AllowExtraSerielNos",
                    SettingsValue=AllowExtraSerielNos,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="AllowExtraSerielNos"
                ).update(
                    SettingsValue=AllowExtraSerielNos,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="Free_Quantity_In_Sales").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="Free_Quantity_In_Sales",
                    SettingsValue=Free_Quantity_In_Sales,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="Free_Quantity_In_Sales"
                ).update(
                    SettingsValue=Free_Quantity_In_Sales,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="Free_Quantity_In_Purchase").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="Free_Quantity_In_Purchase",
                    SettingsValue=Free_Quantity_In_Purchase,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="Free_Quantity_In_Purchase"
                ).update(
                    SettingsValue=Free_Quantity_In_Purchase,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowCustomerInPurchase").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="ShowCustomerInPurchase",
                    SettingsValue=ShowCustomerInPurchase,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="ShowCustomerInPurchase"
                ).update(
                    SettingsValue=ShowCustomerInPurchase,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowManDateAndExpDatePurchase").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="ShowManDateAndExpDatePurchase",
                    SettingsValue=ShowManDateAndExpDatePurchase,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="ShowManDateAndExpDatePurchase"
                ).update(
                    SettingsValue=ShowManDateAndExpDatePurchase,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowDiscountInPurchase").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="ShowDiscountInPurchase",
                    SettingsValue=ShowDiscountInPurchase,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="ShowDiscountInPurchase"
                ).update(
                    SettingsValue=ShowDiscountInPurchase,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowDiscountInPayments").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="ShowDiscountInPayments",
                    SettingsValue=ShowDiscountInPayments,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="ShowDiscountInPayments"
                ).update(
                    SettingsValue=ShowDiscountInPayments,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="EnableLoyaltySettings").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="EnableLoyaltySettings",
                    SettingsValue=EnableLoyaltySettings,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="EnableLoyaltySettings"
                ).update(
                    SettingsValue=EnableLoyaltySettings,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="CustomerBasedPrint").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="CustomerBasedPrint",
                    SettingsValue=CustomerBasedPrint,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="CustomerBasedPrint"
                ).update(
                    SettingsValue=CustomerBasedPrint,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowDiscountInReceipts").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="ShowDiscountInReceipts",
                    SettingsValue=ShowDiscountInReceipts,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="ShowDiscountInReceipts"
                ).update(
                    SettingsValue=ShowDiscountInReceipts,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="EnableCardNetWork").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="EnableCardNetWork",
                    SettingsValue=EnableCardNetWork,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="EnableCardNetWork"
                ).update(
                    SettingsValue=EnableCardNetWork,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="BlockTransactionsByDate").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="BlockTransactionsByDate",
                    SettingsValue=BlockTransactionsByDate,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="BlockTransactionsByDate"
                ).update(
                    SettingsValue=BlockTransactionsByDate,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="EnableCardDetails").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="EnableCardDetails",
                    SettingsValue=EnableCardDetails,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="EnableCardDetails"
                ).update(
                    SettingsValue=EnableCardDetails,
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

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="PurchasePriceUpdate").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="PurchasePriceUpdate",
                    SettingsValue=PurchasePriceUpdate,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="PurchasePriceUpdate"
                ).update(
                    SettingsValue=PurchasePriceUpdate,
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

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="AllowCashReceiptMorePurchaseAmt").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="AllowCashReceiptMorePurchaseAmt",
                    SettingsValue=AllowCashReceiptMorePurchaseAmt,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="AllowCashReceiptMorePurchaseAmt"
                ).update(
                    SettingsValue=AllowCashReceiptMorePurchaseAmt,
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

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="AllowAdvanceReceiptinPurchase").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="AllowAdvanceReceiptinPurchase",
                    SettingsValue=AllowAdvanceReceiptinPurchase,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="AllowAdvanceReceiptinPurchase"
                ).update(
                    SettingsValue=AllowAdvanceReceiptinPurchase,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action)

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="AllowQtyDividerinSales").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="AllowQtyDividerinSales",
                    SettingsValue=AllowQtyDividerinSales,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="AllowQtyDividerinSales"
                ).update(
                    SettingsValue=AllowQtyDividerinSales,
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

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="VoucherNoAutoGenerate").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="VoucherNoAutoGenerate",
                    SettingsValue=VoucherNoAutoGenerate,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="VoucherNoAutoGenerate"
                ).update(
                    SettingsValue=VoucherNoAutoGenerate,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action)

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="EnableVoucherNoUserWise").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="EnableVoucherNoUserWise",
                    SettingsValue=EnableVoucherNoUserWise,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="EnableVoucherNoUserWise"
                ).update(
                    SettingsValue=EnableVoucherNoUserWise,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action)

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowSalesPriceInPurchase").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="ShowSalesPriceInPurchase",
                    SettingsValue=ShowSalesPriceInPurchase,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="ShowSalesPriceInPurchase"
                ).update(
                    SettingsValue=ShowSalesPriceInPurchase,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action)

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowSettingsinSales").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="ShowSettingsinSales",
                    SettingsValue=ShowSettingsinSales,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="ShowSettingsinSales"
                ).update(
                    SettingsValue=ShowSettingsinSales,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action)

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowSettingsinPurchase").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="ShowSettingsinPurchase",
                    SettingsValue=ShowSettingsinPurchase,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="ShowSettingsinPurchase"
                ).update(
                    SettingsValue=ShowSettingsinPurchase,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action)

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="EnableProductBatchWise").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="EnableProductBatchWise",
                    SettingsValue=EnableProductBatchWise,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="EnableProductBatchWise"
                ).update(
                    SettingsValue=EnableProductBatchWise,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action)

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="AllowUpdateBatchPriceInSales").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="AllowUpdateBatchPriceInSales",
                    SettingsValue=AllowUpdateBatchPriceInSales,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="AllowUpdateBatchPriceInSales"
                ).update(
                    SettingsValue=AllowUpdateBatchPriceInSales,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action)

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="EnableTransilationInProduct").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="EnableTransilationInProduct",
                    SettingsValue=EnableTransilationInProduct,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="EnableTransilationInProduct"
                ).update(
                    SettingsValue=EnableTransilationInProduct,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action)

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowPositiveStockInSales").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="ShowPositiveStockInSales",
                    SettingsValue=ShowPositiveStockInSales,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="ShowPositiveStockInSales"
                ).update(
                    SettingsValue=ShowPositiveStockInSales,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action)

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowNegativeBatchInSales").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="ShowNegativeBatchInSales",
                    SettingsValue=ShowNegativeBatchInSales,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="ShowNegativeBatchInSales"
                ).update(
                    SettingsValue=ShowNegativeBatchInSales,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action)

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="CreateBatchForWorkOrder").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="CreateBatchForWorkOrder",
                    SettingsValue=CreateBatchForWorkOrder,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="CreateBatchForWorkOrder"
                ).update(
                    SettingsValue=CreateBatchForWorkOrder,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action)

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowYearMonthCalanderInWorkOrder").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="ShowYearMonthCalanderInWorkOrder",
                    SettingsValue=ShowYearMonthCalanderInWorkOrder,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="ShowYearMonthCalanderInWorkOrder"
                ).update(
                    SettingsValue=ShowYearMonthCalanderInWorkOrder,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action)

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="KFC").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="KFC",
                    SettingsValue=KFC,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="KFC"
                ).update(
                    SettingsValue=KFC,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action)

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="BatchCriteria").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="BatchCriteria",
                    SettingsValue=BatchCriteria,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="BatchCriteria"
                ).update(
                    SettingsValue=BatchCriteria,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action)

            if not administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="blockSaleByBillDisct").exists():
                administrations_models.GeneralSettings.objects.create(
                    CompanyID=CompanyID,
                    GeneralSettingsID=max_id(),
                    SettingsType="blockSaleByBillDisct",
                    SettingsValue=blockSaleByBillDisct,
                    BranchID=1,
                    GroupName="Inventory",
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.filter(
                    CompanyID=CompanyID,
                    SettingsType="blockSaleByBillDisct"
                ).update(
                    SettingsValue=blockSaleByBillDisct,
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
            if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="RoundOffPurchase").exists():
                administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="RoundOffPurchase").update(
                    SettingsValue=RoundOffPurchase,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.create(CompanyID=CompanyID,
                                                                      GeneralSettingsID=max_id(),
                                                                      SettingsType="RoundOffPurchase",
                                                                      SettingsValue=RoundOffPurchase,
                                                                      BranchID=1, GroupName="Inventory",
                                                                      UpdatedDate=today,
                                                                      CreatedUserID=User,
                                                                      Action=Action)

            if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="RoundOffSales").exists():
                administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="RoundOffSales").update(
                    SettingsValue=RoundOffSales,
                    UpdatedDate=today,
                    CreatedUserID=User,
                    Action=Action
                )
            else:
                administrations_models.GeneralSettings.objects.create(CompanyID=CompanyID,
                                                                      GeneralSettingsID=max_id(),
                                                                      SettingsType="RoundOffSales",
                                                                      SettingsValue=RoundOffSales,
                                                                      BranchID=1, GroupName="Inventory",
                                                                      UpdatedDate=today,
                                                                      CreatedUserID=User,
                                                                      Action=Action)

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
            # request , company, log_type, user, source, action, message, description
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
            # request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'GeneralSettings', 'Create', 'GeneralSettings Created Failed.', "enterd invalid number")
            response_data = {
                "StatusCode": 6001,
                "message": "You enterd an invalid number"
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
def general_settings_list(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    BranchID = data['BranchID']
    check_PreDateTransaction = 30
    check_PostDateTransaction = 30
    PreDateTransaction = 30
    PostDateTransaction = 30
    if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        instances = administrations_models.GeneralSettings.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID)
        # =====
        try:
            loyalty_point_value = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="loyalty_point_value").SettingsValue
        except:
            loyalty_point_value = ""
        # ======
        check_Purchase_GST_Type = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Purchase_GST_Type").SettingsValue
        check_Sales_GST_Type = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Sales_GST_Type").SettingsValue
        check_Sales_VAT_Type = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Sales_VAT_Type").SettingsValue
        check_Purchase_VAT_Type = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Purchase_VAT_Type").SettingsValue
        # check_Free_Quantity_In_Sales = administrations_models.GeneralSettings.objects.get(
        #     BranchID=BranchID,CompanyID=CompanyID, SettingsType="Free_Quantity_In_Sales").SettingsValue
        # check_Free_Quantity_In_Purchase = administrations_models.GeneralSettings.objects.get(
        #     BranchID=BranchID,CompanyID=CompanyID, SettingsType="Free_Quantity_In_Purchase").SettingsValue
        check_Show_Sales_Type = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Show_Sales_Type").SettingsValue
        check_Show_Purchase_Type = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Show_Purchase_Type").SettingsValue
        check_VAT = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="VAT").SettingsValue
        check_GST = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="GST").SettingsValue
        check_TAX1 = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="TAX1").SettingsValue
        check_TAX2 = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="TAX2").SettingsValue
        check_TAX3 = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="TAX3").SettingsValue
        check_Trading = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Trading").SettingsValue
        check_Restaurant = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Restaurant").SettingsValue
        check_QtyDecimalPoint = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="QtyDecimalPoint").SettingsValue
        check_PriceDecimalPoint = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="PriceDecimalPoint").SettingsValue
        if check_VAT == "true" or check_VAT == True or check_VAT == "True":
            check_Purchase_VAT_Type = 32
            check_Sales_VAT_Type = 32

        if administrations_models.GeneralSettings.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="PreDateTransaction").exists():
            check_PreDateTransaction = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="PreDateTransaction").SettingsValue
        if administrations_models.GeneralSettings.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="PostDateTransaction").exists():
            check_PostDateTransaction = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="PostDateTransaction").SettingsValue
        check_Additional_Discount = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Additional_Discount").SettingsValue
        check_Bill_Discount = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Bill_Discount").SettingsValue
        check_Negatine_Stock = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Negatine_Stock").SettingsValue
        check_Increment_Qty_In_POS = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Increment_Qty_In_POS").SettingsValue
        check_Kitchen_Print = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Kitchen_Print").SettingsValue
        check_Order_Print = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Order_Print").SettingsValue
        check_Print_After_Save_Active = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Print_After_Save_Active").SettingsValue
        QtyDecimalPoint = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="QtyDecimalPoint").SettingsValue

        if administrations_models.GeneralSettings.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="PreDateTransaction").exists():
            PreDateTransaction = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="PreDateTransaction").SettingsValue
        if administrations_models.GeneralSettings.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="PostDateTransaction").exists():
            PostDateTransaction = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="PostDateTransaction").SettingsValue

        PriceDecimalPoint = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="PriceDecimalPoint").SettingsValue
        RoundingFigure = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="RoundingFigure").SettingsValue

        RoundOffPurchase = 5
        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="RoundOffPurchase").exists():
            RoundOffPurchase = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="RoundOffPurchase").SettingsValue

        RoundOffSales = 5
        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="RoundOffSales").exists():
            RoundOffSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="RoundOffSales").SettingsValue

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
        Loyalty_Point_Expire = False
        is_Loyalty_SalesReturn_MinimumSalePrice = False
        AllowNegativeStockSales = False
        PriceCategory = False
        InclusiveRateSales = False
        InclusiveRatePurchase = False
        InclusiveRateWorkOrder = False
        ShowDiscountInSales = False
        ShowSupplierInSales = False
        EnableShippingCharge = False
        ShowDueBalanceInSales = False
        ShowDueBalanceInPurchase = False
        ShowEmployeesInSales = False
        EnableSerialNoInSales = False
        EnableItemCodeNoInSales = False
        EnableSalesManInSales = False
        ShowWarrantyPeriodInProduct = False
        ShowDescriptionInSales = False
        AllowExtraSerielNos = False
        Free_Quantity_In_Sales = False
        Free_Quantity_In_Purchase = False
        ShowCustomerInPurchase = False
        ShowManDateAndExpDatePurchase = False
        ShowDiscountInPurchase = False
        ShowDiscountInPayments = False
        ShowDiscountInReceipts = False
        EnableLoyaltySettings = False
        CustomerBasedPrint = False
        EnableCardNetWork = False
        BlockTransactionsByDate = False
        EnableCardDetails = False
        SalesPriceUpdate = False
        PurchasePriceUpdate = False
        AllowCashReceiptMoreSaleAmt = False
        AllowCashReceiptMorePurchaseAmt = False
        AllowAdvanceReceiptinSales = False
        AllowAdvanceReceiptinPurchase = False
        AllowQtyDividerinSales = False
        ReferenceBillNo = False
        BlockSalesPrice = False
        VoucherNoAutoGenerate = False
        EnableVoucherNoUserWise = False
        ShowSalesPriceInPurchase = False
        ShowSettingsinSales = False
        ShowSettingsinPurchase = False
        EnableProductBatchWise = False
        AllowUpdateBatchPriceInSales = False
        EnableTransilationInProduct = False
        ShowPositiveStockInSales = False
        ShowNegativeBatchInSales = False
        CreateBatchForWorkOrder = False
        ShowYearMonthCalanderInWorkOrder = False
        KFC = False
        BatchCriteria = ""
        blockSaleByBillDisct = False

        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="Loyalty_Point_Expire").exists():
            Loyalty_Point_Expire = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="Loyalty_Point_Expire").SettingsValue
            if Loyalty_Point_Expire == "True":
                Loyalty_Point_Expire = True
            else:
                Loyalty_Point_Expire = False

        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="is_Loyalty_SalesReturn_MinimumSalePrice").exists():
            is_Loyalty_SalesReturn_MinimumSalePrice = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="is_Loyalty_SalesReturn_MinimumSalePrice").SettingsValue
            if is_Loyalty_SalesReturn_MinimumSalePrice == "True":
                is_Loyalty_SalesReturn_MinimumSalePrice = True
            else:
                is_Loyalty_SalesReturn_MinimumSalePrice = False

        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="MultiUnit").exists():
            MultiUnit = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="MultiUnit").SettingsValue
            if MultiUnit == "True":
                MultiUnit = True
            else:
                MultiUnit = False

        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="AllowNegativeStockSales").exists():
            AllowNegativeStockSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="AllowNegativeStockSales").SettingsValue
            if AllowNegativeStockSales == "True":
                AllowNegativeStockSales = True
            else:
                AllowNegativeStockSales = False

        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="PriceCategory").exists():
            PriceCategory = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="PriceCategory").SettingsValue
            if PriceCategory == "True":
                PriceCategory = True
            else:
                PriceCategory = False

        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="InclusiveRateSales").exists():
            InclusiveRateSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="InclusiveRateSales").SettingsValue
            if InclusiveRateSales == "True":
                InclusiveRateSales = True
            else:
                InclusiveRateSales = False

        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="InclusiveRatePurchase").exists():
            InclusiveRatePurchase = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="InclusiveRatePurchase").SettingsValue
            if InclusiveRatePurchase == "True":
                InclusiveRatePurchase = True
            else:
                InclusiveRatePurchase = False

        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="InclusiveRateWorkOrder").exists():
            InclusiveRateWorkOrder = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="InclusiveRateWorkOrder").SettingsValue
            if InclusiveRateWorkOrder == "True":
                InclusiveRateWorkOrder = True
            else:
                InclusiveRateWorkOrder = False

        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowDiscountInSales").exists():
            ShowDiscountInSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowDiscountInSales").SettingsValue
            if ShowDiscountInSales == "True":
                ShowDiscountInSales = True
            else:
                ShowDiscountInSales = False

        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowSupplierInSales").exists():
            ShowSupplierInSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowSupplierInSales").SettingsValue
            if ShowSupplierInSales == "True":
                ShowSupplierInSales = True
            else:
                ShowSupplierInSales = False

        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="EnableShippingCharge").exists():
            EnableShippingCharge = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableShippingCharge").SettingsValue
            if EnableShippingCharge == "True":
                EnableShippingCharge = True
            else:
                EnableShippingCharge = False

        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowDueBalanceInSales").exists():
            ShowDueBalanceInSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowDueBalanceInSales").SettingsValue
            if ShowDueBalanceInSales == "True":
                ShowDueBalanceInSales = True
            else:
                ShowDueBalanceInSales = False

        if administrations_models.GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowDueBalanceInPurchase").exists():
            ShowDueBalanceInPurchase = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowDueBalanceInPurchase").SettingsValue
            if ShowDueBalanceInPurchase == "True":
                ShowDueBalanceInPurchase = True
            else:
                ShowDueBalanceInPurchase = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowEmployeesInSales").exists():
            ShowEmployeesInSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowEmployeesInSales").SettingsValue
            if ShowEmployeesInSales == "True":
                ShowEmployeesInSales = True
            else:
                ShowEmployeesInSales = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableSerialNoInSales").exists():
            EnableSerialNoInSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableSerialNoInSales").SettingsValue
            if EnableSerialNoInSales == "True":
                EnableSerialNoInSales = True
            else:
                EnableSerialNoInSales = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableItemCodeNoInSales").exists():
            EnableItemCodeNoInSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableItemCodeNoInSales").SettingsValue
            if EnableItemCodeNoInSales == "True":
                EnableItemCodeNoInSales = True
            else:
                EnableItemCodeNoInSales = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableSalesManInSales").exists():
            EnableSalesManInSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableSalesManInSales").SettingsValue
            if EnableSalesManInSales == "True":
                EnableSalesManInSales = True
            else:
                EnableSalesManInSales = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowWarrantyPeriodInProduct").exists():
            ShowWarrantyPeriodInProduct = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowWarrantyPeriodInProduct").SettingsValue
            if ShowWarrantyPeriodInProduct == "True":
                ShowWarrantyPeriodInProduct = True
            else:
                ShowWarrantyPeriodInProduct = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowDescriptionInSales").exists():
            ShowDescriptionInSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowDescriptionInSales").SettingsValue
            if ShowDescriptionInSales == "True":
                ShowDescriptionInSales = True
            else:
                ShowDescriptionInSales = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="AllowExtraSerielNos").exists():
            AllowExtraSerielNos = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="AllowExtraSerielNos").SettingsValue
            if AllowExtraSerielNos == "True":
                AllowExtraSerielNos = True
            else:
                AllowExtraSerielNos = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="Free_Quantity_In_Sales").exists():
            Free_Quantity_In_Sales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="Free_Quantity_In_Sales").SettingsValue
            if Free_Quantity_In_Sales == "True":
                Free_Quantity_In_Sales = True
            else:
                Free_Quantity_In_Sales = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="Free_Quantity_In_Purchase").exists():
            Free_Quantity_In_Purchase = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="Free_Quantity_In_Purchase").SettingsValue
            if Free_Quantity_In_Purchase == "True":
                Free_Quantity_In_Purchase = True
            else:
                Free_Quantity_In_Purchase = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowCustomerInPurchase").exists():
            ShowCustomerInPurchase = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowCustomerInPurchase").SettingsValue
            if ShowCustomerInPurchase == "True":
                ShowCustomerInPurchase = True
            else:
                ShowCustomerInPurchase = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowManDateAndExpDatePurchase").exists():
            ShowManDateAndExpDatePurchase = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowManDateAndExpDatePurchase").SettingsValue
            if ShowManDateAndExpDatePurchase == "True":
                ShowManDateAndExpDatePurchase = True
            else:
                ShowManDateAndExpDatePurchase = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowDiscountInPurchase").exists():
            ShowDiscountInPurchase = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowDiscountInPurchase").SettingsValue
            if ShowDiscountInPurchase == "True":
                ShowDiscountInPurchase = True
            else:
                ShowDiscountInPurchase = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowDiscountInPayments").exists():
            ShowDiscountInPayments = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowDiscountInPayments").SettingsValue
            if ShowDiscountInPayments == "True":
                ShowDiscountInPayments = True
            else:
                ShowDiscountInPayments = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowDiscountInReceipts").exists():
            ShowDiscountInReceipts = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowDiscountInReceipts").SettingsValue
            if ShowDiscountInReceipts == "True":
                ShowDiscountInReceipts = True
            else:
                ShowDiscountInReceipts = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableLoyaltySettings").exists():
            EnableLoyaltySettings = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableLoyaltySettings").SettingsValue
            if EnableLoyaltySettings == "True":
                EnableLoyaltySettings = True
            else:
                EnableLoyaltySettings = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="CustomerBasedPrint").exists():
            CustomerBasedPrint = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="CustomerBasedPrint").SettingsValue
            if CustomerBasedPrint == "True":
                CustomerBasedPrint = True
            else:
                CustomerBasedPrint = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableCardNetWork").exists():
            EnableCardNetWork = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableCardNetWork").SettingsValue
            if EnableCardNetWork == "True":
                EnableCardNetWork = True
            else:
                EnableCardNetWork = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="BlockTransactionsByDate").exists():
            BlockTransactionsByDate = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="BlockTransactionsByDate").SettingsValue
            if BlockTransactionsByDate == "True":
                BlockTransactionsByDate = True
            else:
                BlockTransactionsByDate = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableCardDetails").exists():
            EnableCardDetails = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableCardDetails").SettingsValue
            if EnableCardDetails == "True":
                EnableCardDetails = True
            else:
                EnableCardDetails = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="SalesPriceUpdate").exists():
            SalesPriceUpdate = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="SalesPriceUpdate").SettingsValue
            if SalesPriceUpdate == "True":
                SalesPriceUpdate = True
            else:
                SalesPriceUpdate = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="PurchasePriceUpdate").exists():
            PurchasePriceUpdate = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="PurchasePriceUpdate").SettingsValue
            if PurchasePriceUpdate == "True":
                PurchasePriceUpdate = True
            else:
                PurchasePriceUpdate = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="AllowCashReceiptMoreSaleAmt").exists():
            AllowCashReceiptMoreSaleAmt = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="AllowCashReceiptMoreSaleAmt").SettingsValue

            if AllowCashReceiptMoreSaleAmt == "True":
                AllowCashReceiptMoreSaleAmt = True
            else:
                AllowCashReceiptMoreSaleAmt = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="AllowCashReceiptMorePurchaseAmt").exists():
            AllowCashReceiptMorePurchaseAmt = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="AllowCashReceiptMorePurchaseAmt").SettingsValue

            if AllowCashReceiptMorePurchaseAmt == "True":
                AllowCashReceiptMorePurchaseAmt = True
            else:
                AllowCashReceiptMorePurchaseAmt = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="AllowAdvanceReceiptinSales").exists():
            AllowAdvanceReceiptinSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="AllowAdvanceReceiptinSales").SettingsValue

            if AllowAdvanceReceiptinSales == "True":
                AllowAdvanceReceiptinSales = True
            else:
                AllowAdvanceReceiptinSales = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="AllowAdvanceReceiptinPurchase").exists():
            AllowAdvanceReceiptinPurchase = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="AllowAdvanceReceiptinPurchase").SettingsValue

            if AllowAdvanceReceiptinPurchase == "True":
                AllowAdvanceReceiptinPurchase = True
            else:
                AllowAdvanceReceiptinPurchase = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="AllowQtyDividerinSales").exists():
            AllowQtyDividerinSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="AllowQtyDividerinSales").SettingsValue

            if AllowQtyDividerinSales == "True":
                AllowQtyDividerinSales = True
            else:
                AllowQtyDividerinSales = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="ReferenceBillNo").exists():
            ReferenceBillNo = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ReferenceBillNo").SettingsValue

            if ReferenceBillNo == "True":
                ReferenceBillNo = True
            else:
                ReferenceBillNo = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="BlockSalesPrice").exists():
            BlockSalesPrice = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="BlockSalesPrice").SettingsValue
            if BlockSalesPrice == "True":
                BlockSalesPrice = True
            else:
                BlockSalesPrice = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="VoucherNoAutoGenerate").exists():
            VoucherNoAutoGenerate = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="VoucherNoAutoGenerate").SettingsValue
            if VoucherNoAutoGenerate == "True":
                VoucherNoAutoGenerate = True
            else:
                VoucherNoAutoGenerate = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableVoucherNoUserWise").exists():
            EnableVoucherNoUserWise = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableVoucherNoUserWise").SettingsValue
            if EnableVoucherNoUserWise == "True":
                EnableVoucherNoUserWise = True
            else:
                EnableVoucherNoUserWise = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowSalesPriceInPurchase").exists():
            ShowSalesPriceInPurchase = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowSalesPriceInPurchase").SettingsValue
            if ShowSalesPriceInPurchase == "True":
                ShowSalesPriceInPurchase = True
            else:
                ShowSalesPriceInPurchase = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowSettingsinSales").exists():
            ShowSettingsinSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowSettingsinSales").SettingsValue
            if ShowSettingsinSales == "True":
                ShowSettingsinSales = True
            else:
                ShowSettingsinSales = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowSettingsinPurchase").exists():
            ShowSettingsinPurchase = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowSettingsinPurchase").SettingsValue
            if ShowSettingsinPurchase == "True":
                ShowSettingsinPurchase = True
            else:
                ShowSettingsinPurchase = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableProductBatchWise").exists():
            EnableProductBatchWise = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
            if EnableProductBatchWise == "True":
                EnableProductBatchWise = True
            else:
                EnableProductBatchWise = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="AllowUpdateBatchPriceInSales").exists():
            AllowUpdateBatchPriceInSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="AllowUpdateBatchPriceInSales").SettingsValue
            if AllowUpdateBatchPriceInSales == "True":
                AllowUpdateBatchPriceInSales = True
            else:
                AllowUpdateBatchPriceInSales = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableTransilationInProduct").exists():
            EnableTransilationInProduct = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableTransilationInProduct").SettingsValue
            if EnableTransilationInProduct == "True":
                EnableTransilationInProduct = True
            else:
                EnableTransilationInProduct = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowPositiveStockInSales").exists():
            ShowPositiveStockInSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowPositiveStockInSales").SettingsValue
            if ShowPositiveStockInSales == "True":
                ShowPositiveStockInSales = True
            else:
                ShowPositiveStockInSales = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowNegativeBatchInSales").exists():
            ShowNegativeBatchInSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowNegativeBatchInSales").SettingsValue
            if ShowNegativeBatchInSales == "True":
                ShowNegativeBatchInSales = True
            else:
                ShowNegativeBatchInSales = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="CreateBatchForWorkOrder").exists():
            CreateBatchForWorkOrder = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="CreateBatchForWorkOrder").SettingsValue
            if CreateBatchForWorkOrder == "True":
                CreateBatchForWorkOrder = True
            else:
                CreateBatchForWorkOrder = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowYearMonthCalanderInWorkOrder").exists():
            ShowYearMonthCalanderInWorkOrder = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowYearMonthCalanderInWorkOrder").SettingsValue
            if ShowYearMonthCalanderInWorkOrder == "True":
                ShowYearMonthCalanderInWorkOrder = True
            else:
                ShowYearMonthCalanderInWorkOrder = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="KFC").exists():
            KFC = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="KFC").SettingsValue
            if KFC == "True":
                KFC = True
            else:
                KFC = False
        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="BatchCriteria").exists():
            BatchCriteria = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="BatchCriteria").SettingsValue

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="blockSaleByBillDisct").exists():
            blockSaleByBillDisct = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="blockSaleByBillDisct").SettingsValue
            if blockSaleByBillDisct == "True":
                blockSaleByBillDisct = True
            else:
                blockSaleByBillDisct = False

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

        # if check_Free_Quantity_In_Sales == 'false':
        #     check_Free_Quantity_In_Sales = ''

        # if check_Free_Quantity_In_Purchase == 'false':
        #     check_Free_Quantity_In_Purchase = ''

        if check_Show_Sales_Type == 'false':
            check_Show_Sales_Type = ''

        if check_Show_Purchase_Type == 'false':
            check_Show_Purchase_Type = ''

        # if check_VAT == 'true':
        #     Tax_Active = 'VAT'
        # else:
        #     Tax_Active = 'GST'

        dic = {
            "loyalty_point_value": loyalty_point_value,
            "check_Purchase_GST_Type": check_Purchase_GST_Type,
            "check_Sales_GST_Type": check_Sales_GST_Type,
            "check_Sales_VAT_Type": check_Sales_VAT_Type,
            "check_Purchase_VAT_Type": check_Purchase_VAT_Type,
            # "check_Free_Quantity_In_Sales": check_Free_Quantity_In_Sales,
            # "check_Free_Quantity_In_Purchase": check_Free_Quantity_In_Purchase,
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
            "RoundOffPurchase": RoundOffPurchase,
            "RoundOffSales": RoundOffSales,
            "Business_Type": Business_Type,
            "sales_gst_types": sales_gst_types.data,
            "purchase_gst_types": purchase_gst_types.data,
            "vat_types": vat_types.data,
            "MultiUnit": MultiUnit,
            "Loyalty_Point_Expire": Loyalty_Point_Expire,
            "is_Loyalty_SalesReturn_MinimumSalePrice": is_Loyalty_SalesReturn_MinimumSalePrice,
            "AllowNegativeStockSales": AllowNegativeStockSales,
            "PriceCategory": PriceCategory,
            "InclusiveRateSales": InclusiveRateSales,
            "InclusiveRatePurchase": InclusiveRatePurchase,
            "InclusiveRateWorkOrder": InclusiveRateWorkOrder,
            "ShowDiscountInSales": ShowDiscountInSales,
            "ShowSupplierInSales": ShowSupplierInSales,
            "EnableShippingCharge": EnableShippingCharge,
            "ShowDueBalanceInSales": ShowDueBalanceInSales,
            "ShowDueBalanceInPurchase": ShowDueBalanceInPurchase,
            "ShowEmployeesInSales": ShowEmployeesInSales,
            "EnableSerialNoInSales": EnableSerialNoInSales,
            "EnableItemCodeNoInSales": EnableItemCodeNoInSales,
            "EnableSalesManInSales": EnableSalesManInSales,
            "ShowWarrantyPeriodInProduct": ShowWarrantyPeriodInProduct,
            "ShowDescriptionInSales": ShowDescriptionInSales,
            "AllowExtraSerielNos": AllowExtraSerielNos,
            "Free_Quantity_In_Sales": Free_Quantity_In_Sales,
            "Free_Quantity_In_Purchase": Free_Quantity_In_Purchase,
            "ShowCustomerInPurchase": ShowCustomerInPurchase,
            "ShowManDateAndExpDatePurchase": ShowManDateAndExpDatePurchase,
            "ShowDiscountInPurchase": ShowDiscountInPurchase,
            "ShowDiscountInPayments": ShowDiscountInPayments,
            "ShowDiscountInReceipts": ShowDiscountInReceipts,
            "EnableLoyaltySettings": EnableLoyaltySettings,
            "CustomerBasedPrint": CustomerBasedPrint,
            "EnableCardNetWork": EnableCardNetWork,
            "BlockTransactionsByDate": BlockTransactionsByDate,
            "EnableCardDetails": EnableCardDetails,
            "SalesPriceUpdate": SalesPriceUpdate,
            "PurchasePriceUpdate": PurchasePriceUpdate,
            "AllowCashReceiptMoreSaleAmt": AllowCashReceiptMoreSaleAmt,
            "AllowCashReceiptMorePurchaseAmt": AllowCashReceiptMorePurchaseAmt,
            "AllowAdvanceReceiptinSales": AllowAdvanceReceiptinSales,
            "AllowAdvanceReceiptinPurchase": AllowAdvanceReceiptinPurchase,
            "AllowQtyDividerinSales": AllowQtyDividerinSales,
            "ReferenceBillNo": ReferenceBillNo,
            "BlockSalesPrice": BlockSalesPrice,
            "VoucherNoAutoGenerate": VoucherNoAutoGenerate,
            "EnableVoucherNoUserWise": EnableVoucherNoUserWise,
            "ShowSalesPriceInPurchase": ShowSalesPriceInPurchase,
            "ShowSettingsinSales": ShowSettingsinSales,
            "ShowSettingsinPurchase": ShowSettingsinPurchase,
            "EnableProductBatchWise": EnableProductBatchWise,
            "AllowUpdateBatchPriceInSales": AllowUpdateBatchPriceInSales,
            "EnableTransilationInProduct": EnableTransilationInProduct,
            "ShowPositiveStockInSales": ShowPositiveStockInSales,
            "ShowNegativeBatchInSales": ShowNegativeBatchInSales,
            "CreateBatchForWorkOrder": CreateBatchForWorkOrder,
            "ShowYearMonthCalanderInWorkOrder": ShowYearMonthCalanderInWorkOrder,
            "KFC": KFC,
            "BatchCriteria": BatchCriteria,
            "blockSaleByBillDisct": blockSaleByBillDisct,
            # "sales_vat_types" : sales_vat_types.data,
            # "purchase_vat_types" : purchase_vat_types.data,
            # "Tax_Active" : Tax_Active,
        }
        # request , company, log_type, user, source, action, message, description
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
    CINNumber = get_company(CompanyID).CINNumber
    Description = get_company(CompanyID).Description
    IsTrialVersion = get_company(CompanyID).IsTrialVersion
    Edition = get_company(CompanyID).Edition
    # usertable exceed delete
    NoOfUsers = int(get_company(CompanyID).NoOfUsers)
    usertable_count = UserTable.objects.filter(CompanyID=CompanyID).count()
    if usertable_count > NoOfUsers:
        corrent_user = usertable_count - NoOfUsers
        last_user_table_instance = UserTable.objects.filter(CompanyID=CompanyID)[
            corrent_user:]
        UserTable.objects.exclude(
            CompanyID=CompanyID, pk__in=last_user_table_instance).delete()
    # # usertable exceed delete ends here
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
    company_expire_date = ExpiryDate
    is_owner = True
    user_type = ""
    # =============Uvais================
    # ===========VAT======
    vat = False
    gst = False
    if GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="VAT").exists():
        vat = GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="VAT").SettingsValue
    if GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="GST").exists():
        gst = GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="GST").SettingsValue
    comapny_instance = get_company(CompanyID)
    if vat == "true" or vat == "True" or vat == True:
        vat = True
    else:
        vat = False
    if gst == "true" or gst == "True" or gst == True:
        gst = True
    else:
        gst = False
    print(vat, gst, "OOOOOOOOOOOOOOOOOOOOOOOOO############################")
    comapny_instance.is_gst = gst
    comapny_instance.is_vat = vat
    comapny_instance.save()

    if not MasterType.objects.filter(CompanyID__pk=CompanyID, BranchID=BranchID, Name="Loyalty Card Type").exists():
        MasterTypeID = get_master_auto_id(MasterType, BranchID, CompanyID)
        print(CompanyID, "contextcontextcontextcontextcontextcontext")
        # if CompanySettings.objects.filter(pk=CompanyID).exists():
        comp_instance = CompanySettings.objects.get(pk=CompanyID)
        MasterType.objects.create(
            BranchID=BranchID,
            MasterTypeID=MasterTypeID,
            Name="Loyalty Card Type",
            Action="A",

            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=userId,
            CompanyID=comp_instance,
        )
        MasterType_Log.objects.create(
            BranchID=BranchID,
            TransactionID=MasterTypeID,
            Name="Loyalty Card Type",
            Action="A",

            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=userId,
            CompanyID=comp_instance,
        )
    if not MasterType.objects.filter(CompanyID__pk=CompanyID, BranchID=BranchID, Name="Loyalty Card Status").exists():
        MasterTypeID = get_master_auto_id(MasterType, BranchID, CompanyID)
        comp_instance = CompanySettings.objects.get(pk=CompanyID)
        MasterType.objects.create(
            BranchID=BranchID,
            MasterTypeID=MasterTypeID,
            Name="Loyalty Card Status",
            Action="A",

            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=userId,
            CompanyID=comp_instance,
        )
        MasterType_Log.objects.create(
            BranchID=BranchID,
            TransactionID=MasterTypeID,
            Name="Loyalty Card Status",
            Action="A",

            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=userId,
            CompanyID=comp_instance,
        )
    # =============End================

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
        is_owner = user_table_instance.is_owner
        user_type = user_table_instance.UserType.ID

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
    State_Code = ''
    CompanyLogo = ''
    Address1 = ''
    Address2 = ''
    Address3 = ''
    City = ''
    BussinesType = ''
    if CompanySettings.objects.filter(id=CompanyID).exists():
        com_ins = CompanySettings.objects.get(id=CompanyID)
        BussinesType = com_ins.business_type.Name
        Country = CompanySettings.objects.get(id=CompanyID).Country.id
        CountryName = CompanySettings.objects.get(
            id=CompanyID).Country.Country_Name
        CurrencySymbol = CompanySettings.objects.get(
            id=CompanyID).Country.Symbol
        State = CompanySettings.objects.get(id=CompanyID).State.id
        StateName = CompanySettings.objects.get(id=CompanyID).State.Name
        State_Code = CompanySettings.objects.get(id=CompanyID).State.State_Code
        if CompanySettings.objects.get(id=CompanyID).CompanyLogo:
            CompanyLogo = CompanySettings.objects.get(
                id=CompanyID).CompanyLogo.url
        if CompanySettings.objects.get(id=CompanyID).City:
            City = CompanySettings.objects.get(
                id=CompanyID).City

        if CompanySettings.objects.get(id=CompanyID).Address1:
            Address1 = CompanySettings.objects.get(
                id=CompanyID).Address1
        if CompanySettings.objects.get(id=CompanyID).Address2:
            Address2 = CompanySettings.objects.get(
                id=CompanyID).Address2
        if CompanySettings.objects.get(id=CompanyID).Address3:
            Address3 = CompanySettings.objects.get(
                id=CompanyID).Address3

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
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="VAT").SettingsValue
        check_GST = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="GST").SettingsValue
        check_TAX1 = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="TAX1").SettingsValue
        check_TAX2 = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="TAX2").SettingsValue
        check_TAX3 = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="TAX3").SettingsValue
        check_Trading = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Trading").SettingsValue
        check_Restaurant = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Restaurant").SettingsValue
        check_QtyDecimalPoint = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="QtyDecimalPoint").SettingsValue
        check_PriceDecimalPoint = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="PriceDecimalPoint").SettingsValue
        check_Additional_Discount = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Additional_Discount").SettingsValue
        check_Bill_Discount = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Bill_Discount").SettingsValue
        check_Negatine_Stock = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Negatine_Stock").SettingsValue
        check_Increment_Qty_In_POS = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Increment_Qty_In_POS").SettingsValue
        check_Kitchen_Print = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Kitchen_Print").SettingsValue
        check_Order_Print = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Order_Print").SettingsValue
        check_Print_After_Save_Active = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Print_After_Save_Active").SettingsValue
        QtyDecimalPoint = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="QtyDecimalPoint").SettingsValue
        PriceDecimalPoint = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="PriceDecimalPoint").SettingsValue
        Show_Sales_Type = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Show_Sales_Type").SettingsValue
        Show_Purchase_Type = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Show_Purchase_Type").SettingsValue
        Sales_VAT_Type = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Sales_VAT_Type").SettingsValue
        Purchase_VAT_Type = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Purchase_VAT_Type").SettingsValue
        Sales_GST_Type = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Sales_GST_Type").SettingsValue
        Purchase_GST_Type = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Purchase_GST_Type").SettingsValue

        RoundingFigure = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="RoundingFigure").SettingsValue
        RoundOffPurchase = 5
        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="RoundOffPurchase").exists():
            RoundOffPurchase = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="RoundOffPurchase").SettingsValue

        RoundOffSales = 5
        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="RoundOffSales").exists():
            RoundOffSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="RoundOffSales").SettingsValue

        Sales_VAT_Type = int(Sales_VAT_Type)
        Purchase_VAT_Type = int(Purchase_VAT_Type)
        Sales_GST_Type = int(Sales_GST_Type)
        Purchase_GST_Type = int(Purchase_GST_Type)
        # if TransactionTypes.objects.filter(CompanyID=CompanyID,TransactionTypesID=VAT_Type,BranchID=BranchID).exists():
        #     VAT_Type_name = get_object_or_404(TransactionTypes.objects.filter(CompanyID=CompanyID,TransactionTypesID=VAT_Type,BranchID=BranchID)).Name

        MultiUnit = False
        AllowNegativeStockSales = False
        PreDateTransaction = 30
        PostDateTransaction = 30
        PriceCategory = False
        BlockSalesPrice = False
        VoucherNoAutoGenerate = False
        EnableVoucherNoUserWise = True
        ShowSalesPriceInPurchase = False
        ShowSettingsinSales = False
        ShowSettingsinPurchase = False
        EnableProductBatchWise = False
        AllowUpdateBatchPriceInSales = False
        SalesPriceUpdate = False
        PurchasePriceUpdate = False
        EnableTransilationInProduct = False
        ShowPositiveStockInSales = True
        ShowNegativeBatchInSales = False
        CreateBatchForWorkOrder = False
        ShowYearMonthCalanderInWorkOrder = False
        KFC = False
        BatchCriteria = ""
        blockSaleByBillDisct = False
        AllowCashReceiptMoreSaleAmt = False
        AllowCashReceiptMorePurchaseAmt = False
        AllowAdvanceReceiptinSales = False
        AllowAdvanceReceiptinPurchase = False
        AllowQtyDividerinSales = False
        InclusiveRatePurchase = False
        InclusiveRateSales = False
        InclusiveRateWorkOrder = False
        ShowDiscountInSales = False
        ShowSupplierInSales = False
        EnableShippingCharge = False
        ShowDueBalanceInSales = False
        ShowDueBalanceInPurchase = False
        ShowEmployeesInSales = False
        EnableSerialNoInSales = False
        EnableItemCodeNoInSales = False
        EnableSalesManInSales = False
        ShowWarrantyPeriodInProduct = False
        ShowDescriptionInSales = False
        AllowExtraSerielNos = False
        Free_Quantity_In_Sales = False
        Free_Quantity_In_Purchase = False
        ShowCustomerInPurchase = False
        ShowManDateAndExpDatePurchase = False
        ShowDiscountInPurchase = False
        ShowDiscountInPayments = False
        ShowDiscountInReceipts = False
        EnableCardNetWork = False
        BlockTransactionsByDate = False
        EnableCardDetails = False
        loyalty_PointValue = ""
        EnableLoyaltySettings = False
        CustomerBasedPrint = False
        Loyalty_Point_Expire = False
        is_Loyalty_SalesReturn_MinimumSalePrice = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="loyalty_point_value").exists():
            loyalty_PointValue = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="loyalty_point_value").SettingsValue
            # Loyalty_arr = loyalty_point_value.split(',')
            # for i in Loyalty_arr:
            #     if i:
            #         s = i.split('-')
            #         dic = {
            #             "LoyaltyPoint": s[0],
            #             "LoyaltyValue": s[1],
            #         }
            #         loyalty_taskList.append(dic)

            #         print(i, "HABEEEB RAHMAN", s)
        print(loyalty_PointValue, "YUYYUYUYUYUYUYUYUYUYUYU")

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableLoyaltySettings").exists():
            EnableLoyaltySettings = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableLoyaltySettings").SettingsValue
            if EnableLoyaltySettings == "True":
                EnableLoyaltySettings = True
            else:
                EnableLoyaltySettings = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="CustomerBasedPrint").exists():
            CustomerBasedPrint = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="CustomerBasedPrint").SettingsValue
            if CustomerBasedPrint == "True":
                CustomerBasedPrint = True
            else:
                CustomerBasedPrint = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="Loyalty_Point_Expire").exists():
            Loyalty_Point_Expire = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="Loyalty_Point_Expire").SettingsValue
            if Loyalty_Point_Expire == "True":
                Loyalty_Point_Expire = True
            else:
                Loyalty_Point_Expire = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="is_Loyalty_SalesReturn_MinimumSalePrice").exists():
            is_Loyalty_SalesReturn_MinimumSalePrice = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="is_Loyalty_SalesReturn_MinimumSalePrice").SettingsValue
            if is_Loyalty_SalesReturn_MinimumSalePrice == "True":
                is_Loyalty_SalesReturn_MinimumSalePrice = True
            else:
                is_Loyalty_SalesReturn_MinimumSalePrice = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="MultiUnit").exists():
            MultiUnit = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="MultiUnit").SettingsValue
            if MultiUnit == "True":
                MultiUnit = True
            else:
                MultiUnit = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="AllowNegativeStockSales").exists():
            AllowNegativeStockSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="AllowNegativeStockSales").SettingsValue
            if AllowNegativeStockSales == "True":
                AllowNegativeStockSales = True
            else:
                AllowNegativeStockSales = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="PriceCategory").exists():
            PriceCategory = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="PriceCategory").SettingsValue
            if PriceCategory == "True":
                PriceCategory = True

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="PreDateTransaction").exists():
            PreDateTransaction = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="PreDateTransaction").SettingsValue
        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="PostDateTransaction").exists():
            PostDateTransaction = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="PostDateTransaction").SettingsValue

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="BlockSalesPrice").exists():
            BlockSalesPrice = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="BlockSalesPrice").SettingsValue
            if BlockSalesPrice == "True":
                BlockSalesPrice = True
            else:
                BlockSalesPrice = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="VoucherNoAutoGenerate").exists():
            VoucherNoAutoGenerate = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="VoucherNoAutoGenerate").SettingsValue
            if VoucherNoAutoGenerate == "True":
                VoucherNoAutoGenerate = True
            else:
                VoucherNoAutoGenerate = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableVoucherNoUserWise").exists():
            EnableVoucherNoUserWise = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableVoucherNoUserWise").SettingsValue
            if EnableVoucherNoUserWise == "True":
                EnableVoucherNoUserWise = True
            else:
                EnableVoucherNoUserWise = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowSalesPriceInPurchase").exists():
            ShowSalesPriceInPurchase = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowSalesPriceInPurchase").SettingsValue
            if ShowSalesPriceInPurchase == "True":
                ShowSalesPriceInPurchase = True
            else:
                ShowSalesPriceInPurchase = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowSettingsinSales").exists():
            ShowSettingsinSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowSettingsinSales").SettingsValue
            if ShowSettingsinSales == "True":
                ShowSettingsinSales = True
            else:
                ShowSettingsinSales = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowSettingsinPurchase").exists():
            ShowSettingsinPurchase = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowSettingsinPurchase").SettingsValue
            if ShowSettingsinPurchase == "True":
                ShowSettingsinPurchase = True
            else:
                ShowSettingsinPurchase = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableProductBatchWise").exists():
            EnableProductBatchWise = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
            if EnableProductBatchWise == "True":
                EnableProductBatchWise = True
            else:
                EnableProductBatchWise = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="AllowUpdateBatchPriceInSales").exists():
            AllowUpdateBatchPriceInSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="AllowUpdateBatchPriceInSales").SettingsValue
            if AllowUpdateBatchPriceInSales == "True":
                AllowUpdateBatchPriceInSales = True
            else:
                AllowUpdateBatchPriceInSales = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="SalesPriceUpdate").exists():
            SalesPriceUpdate = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="SalesPriceUpdate").SettingsValue
            if SalesPriceUpdate == "True":
                SalesPriceUpdate = True
            else:
                SalesPriceUpdate = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="PurchasePriceUpdate").exists():
            PurchasePriceUpdate = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="PurchasePriceUpdate").SettingsValue
            if PurchasePriceUpdate == "True":
                PurchasePriceUpdate = True
            else:
                PurchasePriceUpdate = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableTransilationInProduct").exists():
            EnableTransilationInProduct = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableTransilationInProduct").SettingsValue
            if EnableTransilationInProduct == "True":
                EnableTransilationInProduct = True
            else:
                EnableTransilationInProduct = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowPositiveStockInSales").exists():
            ShowPositiveStockInSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowPositiveStockInSales").SettingsValue
            if ShowPositiveStockInSales == "True":
                ShowPositiveStockInSales = True
            else:
                ShowPositiveStockInSales = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowNegativeBatchInSales").exists():
            ShowNegativeBatchInSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowNegativeBatchInSales").SettingsValue
            if ShowNegativeBatchInSales == "True":
                ShowNegativeBatchInSales = True
            else:
                ShowNegativeBatchInSales = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="CreateBatchForWorkOrder").exists():
            CreateBatchForWorkOrder = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="CreateBatchForWorkOrder").SettingsValue
            if CreateBatchForWorkOrder == "True":
                CreateBatchForWorkOrder = True
            else:
                CreateBatchForWorkOrder = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowYearMonthCalanderInWorkOrder").exists():
            ShowYearMonthCalanderInWorkOrder = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowYearMonthCalanderInWorkOrder").SettingsValue
            if ShowYearMonthCalanderInWorkOrder == "True":
                ShowYearMonthCalanderInWorkOrder = True
            else:
                ShowYearMonthCalanderInWorkOrder = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="KFC").exists():
            KFC = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="KFC").SettingsValue
            if KFC == "True":
                KFC = True
            else:
                KFC = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="BatchCriteria").exists():
            BatchCriteria = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="BatchCriteria").SettingsValue

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="blockSaleByBillDisct").exists():
            blockSaleByBillDisct = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="blockSaleByBillDisct").SettingsValue
            if blockSaleByBillDisct == "True":
                blockSaleByBillDisct = True
            else:
                blockSaleByBillDisct = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="AllowCashReceiptMoreSaleAmt").exists():
            AllowCashReceiptMoreSaleAmt = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="AllowCashReceiptMoreSaleAmt").SettingsValue
            if AllowCashReceiptMoreSaleAmt == "True":
                AllowCashReceiptMoreSaleAmt = True
            else:
                AllowCashReceiptMoreSaleAmt = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="AllowCashReceiptMorePurchaseAmt").exists():
            AllowCashReceiptMorePurchaseAmt = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="AllowCashReceiptMorePurchaseAmt").SettingsValue
            if AllowCashReceiptMorePurchaseAmt == "True":
                AllowCashReceiptMorePurchaseAmt = True
            else:
                AllowCashReceiptMorePurchaseAmt = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="AllowAdvanceReceiptinSales").exists():
            AllowAdvanceReceiptinSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="AllowAdvanceReceiptinSales").SettingsValue
            if AllowAdvanceReceiptinSales == "True":
                AllowAdvanceReceiptinSales = True
            else:
                AllowAdvanceReceiptinSales = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="AllowAdvanceReceiptinPurchase").exists():
            AllowAdvanceReceiptinPurchase = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="AllowAdvanceReceiptinPurchase").SettingsValue
            if AllowAdvanceReceiptinPurchase == "True":
                AllowAdvanceReceiptinPurchase = True
            else:
                AllowAdvanceReceiptinPurchase = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="AllowQtyDividerinSales").exists():
            AllowQtyDividerinSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="AllowQtyDividerinSales").SettingsValue
            if AllowQtyDividerinSales == "True":
                AllowQtyDividerinSales = True
            else:
                AllowQtyDividerinSales = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="InclusiveRatePurchase").exists():
            InclusiveRatePurchase = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="InclusiveRatePurchase").SettingsValue
            if InclusiveRatePurchase == "True":
                InclusiveRatePurchase = True
            else:
                InclusiveRatePurchase = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="InclusiveRateSales").exists():
            InclusiveRateSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="InclusiveRateSales").SettingsValue
            if InclusiveRateSales == "True":
                InclusiveRateSales = True
            else:
                InclusiveRateSales = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="InclusiveRateWorkOrder").exists():
            InclusiveRateWorkOrder = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="InclusiveRateWorkOrder").SettingsValue
            if InclusiveRateWorkOrder == "True":
                InclusiveRateWorkOrder = True
            else:
                InclusiveRateWorkOrder = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowDiscountInSales").exists():
            ShowDiscountInSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowDiscountInSales").SettingsValue
            if ShowDiscountInSales == "True":
                ShowDiscountInSales = True
            else:
                ShowDiscountInSales = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowSupplierInSales").exists():
            ShowSupplierInSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowSupplierInSales").SettingsValue
            if ShowSupplierInSales == "True":
                ShowSupplierInSales = True
            else:
                ShowSupplierInSales = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableShippingCharge").exists():
            EnableShippingCharge = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableShippingCharge").SettingsValue
            if EnableShippingCharge == "True":
                EnableShippingCharge = True
            else:
                EnableShippingCharge = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowDueBalanceInSales").exists():
            ShowDueBalanceInSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowDueBalanceInSales").SettingsValue
            if ShowDueBalanceInSales == "True":
                ShowDueBalanceInSales = True
            else:
                ShowDueBalanceInSales = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowDueBalanceInPurchase").exists():
            ShowDueBalanceInPurchase = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowDueBalanceInPurchase").SettingsValue
            if ShowDueBalanceInPurchase == "True":
                ShowDueBalanceInPurchase = True
            else:
                ShowDueBalanceInPurchase = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowEmployeesInSales").exists():
            ShowEmployeesInSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowEmployeesInSales").SettingsValue
            if ShowEmployeesInSales == "True":
                ShowEmployeesInSales = True
            else:
                ShowEmployeesInSales = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableSerialNoInSales").exists():
            EnableSerialNoInSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableSerialNoInSales").SettingsValue
            if EnableSerialNoInSales == "True":
                EnableSerialNoInSales = True
            else:
                EnableSerialNoInSales = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableItemCodeNoInSales").exists():
            EnableItemCodeNoInSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableItemCodeNoInSales").SettingsValue
            if EnableItemCodeNoInSales == "True":
                EnableItemCodeNoInSales = True
            else:
                EnableItemCodeNoInSales = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableSalesManInSales").exists():
            EnableSalesManInSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableSalesManInSales").SettingsValue
            if EnableSalesManInSales == "True":
                EnableSalesManInSales = True
            else:
                EnableSalesManInSales = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowWarrantyPeriodInProduct").exists():
            ShowWarrantyPeriodInProduct = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowWarrantyPeriodInProduct").SettingsValue
            if ShowWarrantyPeriodInProduct == "True":
                ShowWarrantyPeriodInProduct = True
            else:
                ShowWarrantyPeriodInProduct = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowDescriptionInSales").exists():
            ShowDescriptionInSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowDescriptionInSales").SettingsValue
            if ShowDescriptionInSales == "True":
                ShowDescriptionInSales = True
            else:
                ShowDescriptionInSales = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="AllowExtraSerielNos").exists():
            AllowExtraSerielNos = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="AllowExtraSerielNos").SettingsValue
            if AllowExtraSerielNos == "True":
                AllowExtraSerielNos = True
            else:
                AllowExtraSerielNos = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="Free_Quantity_In_Sales").exists():
            Free_Quantity_In_Sales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="Free_Quantity_In_Sales").SettingsValue
            if Free_Quantity_In_Sales == "True":
                Free_Quantity_In_Sales = True
            else:
                Free_Quantity_In_Sales = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="Free_Quantity_In_Purchase").exists():
            Free_Quantity_In_Purchase = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="Free_Quantity_In_Purchase").SettingsValue
            if Free_Quantity_In_Purchase == "True":
                Free_Quantity_In_Purchase = True
            else:
                Free_Quantity_In_Purchase = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowCustomerInPurchase").exists():
            ShowCustomerInPurchase = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowCustomerInPurchase").SettingsValue
            if ShowCustomerInPurchase == "True":
                ShowCustomerInPurchase = True
            else:
                ShowCustomerInPurchase = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowManDateAndExpDatePurchase").exists():
            ShowManDateAndExpDatePurchase = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowManDateAndExpDatePurchase").SettingsValue
            if ShowManDateAndExpDatePurchase == "True":
                ShowManDateAndExpDatePurchase = True
            else:
                ShowManDateAndExpDatePurchase = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowDiscountInPurchase").exists():
            ShowDiscountInPurchase = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowDiscountInPurchase").SettingsValue
            if ShowDiscountInPurchase == "True":
                ShowDiscountInPurchase = True
            else:
                ShowDiscountInPurchase = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowDiscountInPayments").exists():
            ShowDiscountInPayments = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowDiscountInPayments").SettingsValue
            if ShowDiscountInPayments == "True":
                ShowDiscountInPayments = True
            else:
                ShowDiscountInPayments = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowDiscountInReceipts").exists():
            ShowDiscountInReceipts = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="ShowDiscountInReceipts").SettingsValue
            if ShowDiscountInReceipts == "True":
                ShowDiscountInReceipts = True
            else:
                ShowDiscountInReceipts = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableCardNetWork").exists():
            EnableCardNetWork = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableCardNetWork").SettingsValue
            if EnableCardNetWork == "True":
                EnableCardNetWork = True
            else:
                EnableCardNetWork = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="BlockTransactionsByDate").exists():
            BlockTransactionsByDate = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="BlockTransactionsByDate").SettingsValue
            if BlockTransactionsByDate == "True":
                BlockTransactionsByDate = True
            else:
                BlockTransactionsByDate = False

        if administrations_models.GeneralSettings.objects.filter(BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableCardDetails").exists():
            EnableCardDetails = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableCardDetails").SettingsValue
            if EnableCardDetails == "True":
                EnableCardDetails = True
            else:
                EnableCardDetails = False

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
        IsHSNCode = True
        IsProductCode = True
        IsReceivedAmount = True
        # print bank details===START
        IsBankDetails = False
        BankNameFooter = ""
        AccountNumberFooter = ""
        BranchIFCFooter = ""
        # print bank details===END
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
        TermsAndConditionsSales = ""
        TermsAndConditionsPurchase = ""
        TermsAndConditionsSaleEstimate = ""
        HeadFontSize = ""
        BodyFontSize = ""
        ContentFontSize = ""
        FooterFontSize = ""
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
            IsHSNCode = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsHSNCode
            IsProductCode = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsProductCode

            IsReceivedAmount = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsReceivedAmount
            # print Bank details ====START
            IsBankDetails = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).IsBankDetails
            BankNameFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).BankNameFooter
            AccountNumberFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).AccountNumberFooter
            BranchIFCFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).BranchIFCFooter
            # print Bank details ====END

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
            TermsAndConditionsSales = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).TermsAndConditionsSales
            TermsAndConditionsPurchase = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).TermsAndConditionsPurchase
            TermsAndConditionsSaleEstimate = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).TermsAndConditionsSaleEstimate

            HeadFontSize = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).HeadFontSize
            BodyFontSize = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).BodyFontSize
            ContentFontSize = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).ContentFontSize
            FooterFontSize = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID).FooterFontSize

        # if administrations_models.GeneralSettings.objects.filter(
        #         CompanyID=CompanyID, SettingsType="Free_Quantity_In_Sales").exists():
        #     Free_Quantity_In_Sales = administrations_models.GeneralSettings.objects.get(
        #         CompanyID=CompanyID, SettingsType="Free_Quantity_In_Sales").SettingsValue
        #     if Free_Quantity_In_Sales == "true":
        #         Free_Quantity_In_Sales = True
        #     else:
        #         Free_Quantity_In_Sales = False

        # if administrations_models.GeneralSettings.objects.filter(
        #         CompanyID=CompanyID, SettingsType="Free_Quantity_In_Purchase").exists():
        #     Free_Quantity_In_Purchase = administrations_models.GeneralSettings.objects.get(
        #         CompanyID=CompanyID, SettingsType="Free_Quantity_In_Purchase").SettingsValue
        #     if Free_Quantity_In_Purchase == "true":
        #         Free_Quantity_In_Purchase = True
        #     else:
        #         Free_Quantity_In_Purchase = False
        today = newDatetime.strptime(today, '%Y-%m-%d')
        remaining_days = company_expire_date - today.date()
        if administrations_models.GeneralSettings.objects.filter(
                CompanyID=CompanyID, SettingsType="Bill_Discount").exists():
            Bill_Discount = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="Bill_Discount").SettingsValue
            if Bill_Discount == "true":
                Bill_Discount = True
            else:
                Bill_Discount = False

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
            "IsHSNCode": IsHSNCode,
            "IsProductCode": IsProductCode,
            "IsReceivedAmount": IsReceivedAmount,
            # print Bank details ====START
            "IsBankDetails": IsBankDetails,
            "BankNameFooter": BankNameFooter,
            "AccountNumberFooter": AccountNumberFooter,
            "BranchIFCFooter": BranchIFCFooter,
            # print Bank details ====END
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
            "TermsAndConditionsSales": TermsAndConditionsSales,
            "TermsAndConditionsPurchase": TermsAndConditionsPurchase,
            "TermsAndConditionsSaleEstimate": TermsAndConditionsSaleEstimate,
            "HeadFontSize": HeadFontSize,
            "BodyFontSize": BodyFontSize,
            "ContentFontSize": ContentFontSize,
            "FooterFontSize": FooterFontSize,

        }

        dic = {
            # "Free_Quantity_In_Sales": Free_Quantity_In_Sales,
            "loyalty_PointValue": loyalty_PointValue,
            "EnableLoyaltySettings": EnableLoyaltySettings,
            "CustomerBasedPrint": CustomerBasedPrint,
            "Loyalty_Point_Expire": Loyalty_Point_Expire,
            "is_Loyalty_SalesReturn_MinimumSalePrice": is_Loyalty_SalesReturn_MinimumSalePrice,
            # "Free_Quantity_In_Purchase": Free_Quantity_In_Purchase,
            "Bill_Discount": Bill_Discount,
            "MultiUnit": MultiUnit,
            "AllowNegativeStockSales": AllowNegativeStockSales,
            "PriceCategory": PriceCategory,
            "BlockSalesPrice": BlockSalesPrice,
            "VoucherNoAutoGenerate": VoucherNoAutoGenerate,
            "EnableVoucherNoUserWise": EnableVoucherNoUserWise,
            "ShowSalesPriceInPurchase": ShowSalesPriceInPurchase,
            "ShowSettingsinSales": ShowSettingsinSales,
            "ShowSettingsinPurchase": ShowSettingsinPurchase,
            "EnableProductBatchWise": EnableProductBatchWise,
            "AllowUpdateBatchPriceInSales": AllowUpdateBatchPriceInSales,
            "SalesPriceUpdate": SalesPriceUpdate,
            "PurchasePriceUpdate": PurchasePriceUpdate,
            "EnableTransilationInProduct": EnableTransilationInProduct,
            "ShowPositiveStockInSales": ShowPositiveStockInSales,
            "ShowNegativeBatchInSales": ShowNegativeBatchInSales,
            "CreateBatchForWorkOrder": CreateBatchForWorkOrder,
            "ShowYearMonthCalanderInWorkOrder": ShowYearMonthCalanderInWorkOrder,
            "KFC": KFC,
            "BatchCriteria": BatchCriteria,
            "blockSaleByBillDisct": blockSaleByBillDisct,
            "AllowCashReceiptMoreSaleAmt": AllowCashReceiptMoreSaleAmt,
            "AllowCashReceiptMorePurchaseAmt": AllowCashReceiptMorePurchaseAmt,
            "AllowAdvanceReceiptinSales": AllowAdvanceReceiptinSales,
            "AllowAdvanceReceiptinPurchase": AllowAdvanceReceiptinPurchase,
            "AllowQtyDividerinSales": AllowQtyDividerinSales,
            "InclusiveRatePurchase": InclusiveRatePurchase,
            "InclusiveRateSales": InclusiveRateSales,
            "InclusiveRateWorkOrder": InclusiveRateWorkOrder,
            "ShowDiscountInSales": ShowDiscountInSales,
            "ShowSupplierInSales": ShowSupplierInSales,
            "EnableShippingCharge": EnableShippingCharge,
            "ShowDueBalanceInSales": ShowDueBalanceInSales,
            "ShowDueBalanceInPurchase": ShowDueBalanceInPurchase,
            "ShowEmployeesInSales": ShowEmployeesInSales,
            "EnableSerialNoInSales": EnableSerialNoInSales,
            "EnableItemCodeNoInSales": EnableItemCodeNoInSales,
            "EnableSalesManInSales": EnableSalesManInSales,
            "ShowWarrantyPeriodInProduct": ShowWarrantyPeriodInProduct,
            "ShowDescriptionInSales": ShowDescriptionInSales,
            "AllowExtraSerielNos": AllowExtraSerielNos,
            "Free_Quantity_In_Sales": Free_Quantity_In_Sales,
            "Free_Quantity_In_Purchase": Free_Quantity_In_Purchase,
            "ShowCustomerInPurchase": ShowCustomerInPurchase,
            "ShowManDateAndExpDatePurchase": ShowManDateAndExpDatePurchase,
            "ShowDiscountInPurchase": ShowDiscountInPurchase,
            "ShowDiscountInPayments": ShowDiscountInPayments,
            "ShowDiscountInReceipts": ShowDiscountInReceipts,
            "EnableCardNetWork": EnableCardNetWork,
            "BlockTransactionsByDate": BlockTransactionsByDate,
            "EnableCardDetails": EnableCardDetails,
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
            "RoundOffPurchase": RoundOffPurchase,
            "RoundOffSales": RoundOffSales,
            "Business_Type": BussinesType,
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
        CurrentVersion = 0
        MinimumVersion = 0
        if SoftwareVersion.objects.exists():
            CurrentVersion = SoftwareVersion.objects.get().CurrentVersion
            MinimumVersion = SoftwareVersion.objects.get().MinimumVersion

        software_version_dic = {
            "CurrentVersion": CurrentVersion,
            "MinimumVersion": MinimumVersion,
        }
        success = 6000
        message = "success!"

        # if administrations_models.UserTable.objects.filter(CompanyID=CompanyID)

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
                "CurrencySymbol": CurrencySymbol,
                "CompanyLogo": CompanyLogo,
                "State": State,
                "StateName": StateName,
                "State_Code": State_Code,
                "Address1": Address1,
                "Address2": Address2,
                "Address3": Address3,
                "City": City,
                "CompanyName": CompanyName,
                "CRNumber": CRNumber,
                "CINNumber": CINNumber,
                "Description": Description,
                "financial_FromDate": financial_FromDate,
                "financial_ToDate": financial_ToDate,
                "print_response": print_response,
                "SoftwareVersion": software_version_dic,
                "IsTrialVersion": IsTrialVersion,
                "Edition": Edition,
                "remaining_days": remaining_days.days,
                "is_owner": is_owner,
                "user_type": user_type
            },
            status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Not Found"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def activity_logs(request):
    customer = request.data['customer']
    organization = request.data['organization']
    log_type = request.data['log_type']
    is_solved = request.data['is_solved']

    try:
        page_number = request.data['page_no']
    except:
        page_number = ""

    try:
        items_per_page = request.data['items_per_page']
    except:
        items_per_page = ""

    if administrations_models.Activity_Log.objects.exists():
        if customer and organization and is_solved and log_type:
            instances = administrations_models.Activity_Log.objects.filter(
                user__pk=customer, company__pk=organization, is_solved=is_solved, log_type=log_type)
        elif customer and organization and is_solved == False and log_type:
            instances = administrations_models.Activity_Log.objects.filter(
                user__pk=customer, company__pk=organization, is_solved=is_solved, log_type=log_type)
        elif customer and organization and log_type:
            instances = administrations_models.Activity_Log.objects.filter(
                user__pk=customer, company__pk=organization, is_solved=is_solved, log_type=log_type)
        elif customer and organization and is_solved:
            instances = administrations_models.Activity_Log.objects.filter(
                user__pk=customer, company__pk=organization, is_solved=is_solved)
        elif customer and organization and is_solved == False:
            instances = administrations_models.Activity_Log.objects.filter(
                user__pk=customer, company__pk=organization, is_solved=is_solved)
        elif customer and organization and is_solved:
            instances = administrations_models.Activity_Log.objects.filter(
                user__pk=customer, company__pk=organization)
        elif customer and organization and is_solved == False:
            instances = administrations_models.Activity_Log.objects.filter(
                user__pk=customer, company__pk=organization)
        elif customer and is_solved:
            instances = administrations_models.Activity_Log.objects.filter(
                user__pk=customer, is_solved=True)
        elif customer and is_solved == False:
            instances = administrations_models.Activity_Log.objects.filter(
                user__pk=customer, is_solved=False)
        elif organization and is_solved:
            instances = administrations_models.Activity_Log.objects.filter(
                company__pk=organization)
        elif organization and is_solved == False:
            instances = administrations_models.Activity_Log.objects.filter(
                company__pk=organization, is_solved=False)
        elif is_solved:
            instances = administrations_models.Activity_Log.objects.filter(
                is_solved=is_solved)
        elif is_solved == False:
            instances = administrations_models.Activity_Log.objects.filter(
                is_solved=is_solved)
        elif log_type and is_solved:
            instances = administrations_models.Activity_Log.objects.filter(
                log_type=log_type, is_solved=False)
        elif log_type and is_solved == False:
            instances = administrations_models.Activity_Log.objects.filter(
                log_type=log_type, is_solved=False)
        else:
            instances = administrations_models.Activity_Log.objects.all()

        if page_number and items_per_page:
            count = len(instances)
            instances = list_pagination(
                instances,
                items_per_page,
                page_number
            )
        else:
            count = len(instances)
        serializer = ActivityLogSerializer(instances, many=True)
        response_data = {
            "StatusCode": 6000,
            "data": serializer.data,
            "count": count
        }
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "No activity found"
        }
        return Response(response_data, status=status.HTTP_200_OK)


@ api_view(['POST'])
@ permission_classes((IsAuthenticated,))
@ renderer_classes((JSONRenderer,))
def activity_log_solve(request):
    id = request.data['id']
    is_solved = request.data['is_solved']
    print(id)
    print(is_solved)
    print(type(is_solved))
    instance = administrations_models.Activity_Log.objects.get(id=id)
    instance.is_solved = is_solved
    instance.save()
    response_data = {
        "StatusCode": 6000,
    }
    return Response(response_data, status=status.HTTP_200_OK)


@ api_view(['GET'])
@ permission_classes((IsAuthenticated,))
@ renderer_classes((JSONRenderer,))
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

@ receiver(reset_password_token_created)
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
        'reset_password_url': "http://localhost:3000/password-confirm",
        # 'reset_password_url': "https://www.viknbooks.vikncodes.com/password-confirm",
        # 'reset_password_url': "https://www.viknbooks.com/password-confirm",
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


@ api_view(['POST'])
@ permission_classes((IsAuthenticated,))
@ renderer_classes((JSONRenderer,))
def create_software_version(request):
    data = request.data
    CreatedUserID = data['CreatedUserID']
    CurrentVersion = data['CurrentVersion']
    MinimumVersion = data['MinimumVersion']
    today = datetime.datetime.now()
    if not SoftwareVersion.objects.exists():
        software_instance = SoftwareVersion.objects.create(
            CurrentVersion=CurrentVersion,
            MinimumVersion=MinimumVersion,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            UpdatedUserID=CreatedUserID,
        )
        SoftwareVersionLog.objects.create(
            TransactionID=software_instance.id,
            CurrentVersion=CurrentVersion,
            MinimumVersion=MinimumVersion,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            UpdatedUserID=CreatedUserID,
        )
    else:
        software_instance = SoftwareVersion.objects.update(
            CurrentVersion=CurrentVersion,
            MinimumVersion=MinimumVersion,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            UpdatedUserID=CreatedUserID,
        )
        SoftwareVersionLog.objects.update(
            CurrentVersion=CurrentVersion,
            MinimumVersion=MinimumVersion,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            UpdatedUserID=CreatedUserID,
        )
    response_data = {
        "StatusCode": 6000,
    }
    return Response(response_data, status=status.HTTP_200_OK)


@ api_view(['POST'])
@ permission_classes((IsAuthenticated,))
@ renderer_classes((JSONRenderer,))
def software_versions(request):
    data = request.data
    today = datetime.datetime.now()
    CreatedUserID = data['CreatedUserID']
    if SoftwareVersion.objects.exists():
        instances = SoftwareVersion.objects.get()
        serialized = SoftwareVersionSerializer(instances)
        # request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Brand', 'View', 'Brand list', 'The user viewed brands')

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        software_instance = SoftwareVersion.objects.create(
            CurrentVersion=1,
            MinimumVersion=1,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            UpdatedUserID=CreatedUserID,
        )
        SoftwareVersionLog.objects.create(
            TransactionID=software_instance.id,
            CurrentVersion=1,
            MinimumVersion=1,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            UpdatedUserID=CreatedUserID,
        )
        instances = SoftwareVersion.objects.get()
        serialized = SoftwareVersionSerializer(instances)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }

        return Response(response_data, status=status.HTTP_200_OK)


@ api_view(['GET'])
@ permission_classes((AllowAny,))
@ renderer_classes((JSONRenderer,))
def software_version(request):
    data = request.data
    today = datetime.datetime.now()
    if SoftwareVersion.objects.exists():
        instances = SoftwareVersion.objects.get()
        serialized = SoftwareVersionSerializer(instances)
        # request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Brand', 'View', 'Brand list', 'The user viewed brands')

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Software version not found"
        }
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def user_list(request):
    if User.objects.filter().exists():
        instances = User.objects.all()
        serialized = UserListSerializer(
            instances, many=True,)

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "No users"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def user_list_filter(request):
    data = request.data
    EditionName = data['EditionName']
    is_trialVersion = False
    if EditionName == "Trial Versions":
        is_trialVersion = True
    user_ids = []
    if is_trialVersion == True and CompanySettings.objects.filter(IsTrialVersion=True).exists():
        comapny_instances = CompanySettings.objects.filter(IsTrialVersion=True)
        user_ids = comapny_instances.values_list('owner', flat=True)
    else:
        if CompanySettings.objects.filter(Edition=EditionName).exists():
            comapny_instances = CompanySettings.objects.filter(
                Edition=EditionName)
            user_ids = comapny_instances.values_list('owner', flat=True)
    if User.objects.filter(id__in=user_ids).exists():
        instances = User.objects.filter(id__in=user_ids)
        serialized = UserListSerializer(
            instances, many=True,)

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "No users"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def get_last_user_token(request):
    data = request.data
    username = data['username']

    LastToken = ""
    if Customer.objects.filter(user__username=username).exists():
        instance = Customer.objects.filter(user__username=username).first()
        LastToken = instance.LastLoginToken
    response_data = {
        "StatusCode": 6000,
        "LastToken": LastToken,
    }

    return Response(response_data, status=status.HTTP_200_OK)
