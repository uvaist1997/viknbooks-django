import datetime
import json
from datetime import date
from datetime import datetime as newDatetime
from datetime import timedelta

import requests
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.models import Group, User
from django.contrib.auth.tokens import default_token_generator
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage, EmailMultiAlternatives, send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Max, Q
from django.dispatch import receiver
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import ugettext_lazy as _
from django_rest_passwordreset.models import ResetPasswordToken
from django_rest_passwordreset.signals import reset_password_token_created
from django_rest_passwordreset.views import get_password_reset_token_expiry_time
from mailqueue.models import MailerMessage
from rest_framework import parsers, renderers, status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from api.v9.brands.serializers import ListSerializer
from api.v9.companySettings.serializers import CompanySettingsRestSerializer
from api.v9.general.functions import get_current_role
from api.v9.ledgerPosting.functions import convertOrderdDict
from api.v9.users.functions import (
    create_or_update_general_settings,
    generate_serializer_errors,
    get_account_ledger,
    get_auto_id,
    get_general_settings,
    get_master_auto_id,
    send_email,
    update_general_settings,
    validate_email_address,
)
from api.v9.users.serializers import (
    AccountLedgerSerializer,
    ActivityLogSerializer,
    ChangePasswordSerializer,
    CompaniesSerializer,
    CreateCompanySerializer,
    CreateEmployeeSerializer,
    CreateFinancialYearSerializer,
    CustomersSerializer,
    CustomerUserViewSerializer,
    CustomTokenSerializer,
    EditAccountInfo,
    EditProfile,
    GeneralSettingsListSerializer,
    GeneralSettingsSerializer,
    ImageSerializer,
    LoginSerializer,
    MyCompaniesSerializer,
    ResetPasswordSerializer,
    SignupSerializer,
    SoftwareVersionSerializer,
    TransactionTypesSerializer,
    UpdateSerializer,
    UserAccountsSerializer,
    UserCredentialSerializer,
    UserListSerializer,
    UsernameEmailSerializer,
    UsernameSerializer,
    UserTableRestSerializer,
    UserTableSerializer,
    UserTypeRestSerializer,
    UserTypeSerializer,
    UserTypesSerializer,
    UserViewSerializer,
    ValidateSerializer,
    WarehouseSerializer,
)
from brands import models
from brands import models as administrations_models
from brands.functions import createdb
from brands.models import (
    AccountLedger,
    CompanySettings,
    Country,
    Customer,
    Department,
    Designation,
    Employee,
    Employee_Log,
    FinancialYear,
    FinancialYear_Log,
    GeneralSettings,
    InviteUsers,
    MasterType,
    MasterType_Log,
    SoftwareVersion,
    SoftwareVersionLog,
    State,
    TransactionTypes,
    User_Log,
    UserTable,
    UserType,
    VersionDetails,
    Warehouse,
)
from main.functions import (
    CheckTokenExpired,
    activity_log,
    generateTokenNo,
    get_company,
    get_visitors_details,
)
from main.utils import send_html_mail
from testproject.settings import DEFAULT_FROM_EMAIL
from users.functions import get_auto_LedgerID, get_EmployeeCode, get_LedgerCode
from users.models import (
    CompanyAccountLedger,
    CompanyEmployee,
    CompanyFinancialYear,
    CustomerUser,
    DatabaseStore,
)


def call_paginator_all(model_object, page_number, items_per_page):
    paginator = Paginator(model_object, items_per_page)
    content = paginator.page(page_number)
    return content


def list_pagination(list_value, items_per_page, page_no):
    paginator_object = Paginator(list_value, items_per_page)
    get_value = paginator_object.page(page_no).object_list
    return get_value


@api_view(["POST"])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_user(request):
    today = datetime.datetime.now()
    serialized = UserTableSerializer(data=request.data)

    if serialized.is_valid():
        BranchID = serialized.data["BranchID"]
        UserName = serialized.data["UserName"]
        Password = serialized.data["Password"]
        EmployeeID = serialized.data["EmployeeID"]
        UserTypeID = serialized.data["UserTypeID"]
        CreatedUserID = serialized.data["CreatedUserID"]
        IsActive = serialized.data["IsActive"]

        Action = "A"

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
                CompanyID=CompanyID,
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
                CompanyID=CompanyID,
            )

            # request , company, log_type, user, source, action, message, description
            activity_log(
                request._request,
                CompanyID,
                "Information",
                CreatedUserID,
                "Users",
                "Create",
                "Users created successfully.",
                "Users saved successfully.",
            )

            data = {"ID": ID}
            data.update(serialized.data)
            response_data = {"StatusCode": 6000, "data": data}

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "User Name Already Exist!!!",
            }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors),
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def edit_user(request, pk):
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    today = datetime.datetime.now()
    serialized = UserTableSerializer(data=request.data)
    instance = UserTable.objects.get(pk=pk, CompanyID=CompanyID)

    BranchID = instance.BranchID
    ID = instance.ID
    CreatedUserID = instance.CreatedUserID
    instanceUserName = instance.UserName

    if serialized.is_valid():

        UserName = serialized.data["UserName"]
        Password = serialized.data["Password"]
        UserTypeID = serialized.data["UserTypeID"]
        EmployeeID = serialized.data["EmployeeID"]
        IsActive = serialized.data["IsActive"]

        Action = "M"

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
                CompanyID=CompanyID,
            )

            data = {"ID": ID}
            data.update(serialized.data)
            response_data = {"StatusCode": 6000, "data": data}

            return Response(response_data, status=status.HTTP_200_OK)

        else:

            if is_nameExist:

                response_data = {
                    "StatusCode": 6001,
                    "message": "User Name Already exist with this Branch ID",
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
                    CompanyID=CompanyID,
                )

                data = {"ID": ID}
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
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def users(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():
        BranchID = serialized1.data["BranchID"]
        if UserTable.objects.filter(CompanyID=CompanyID).exists():
            instances = UserTable.objects.filter(CompanyID=CompanyID)
            serialized = UserTableRestSerializer(
                instances, many=True, context={"CompanyID": CompanyID}
            )

            response_data = {"StatusCode": 6000, "data": serialized.data}

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "User Not Found in this BranchID!",
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
@renderer_classes((JSONRenderer,))
def customers(request):
    data = request.data
    # serializer = ListSerializer(data=request.data)
    if Customer.objects.all().exists():
        instances = Customer.objects.all()
        serializer = CustomersSerializer(instances, many=True)
        response_data = {"StatusCode": 6000, "data": serializer.data}

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {"StatusCode": 6001, "message": "Customer Not Found"}

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def user_types(request):
    data = request.data
    # serializer = ListSerializer(data=request.data)
    if UserType.objects.all().exists():
        instances = UserType.objects.all()
        serializer = UserTypeSerializer(instances, many=True)
        response_data = {"StatusCode": 6000, "data": serializer.data}

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {"StatusCode": 6001, "message": "Customer Not Found"}

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def user(request, pk):
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    instance = None

    if UserTable.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = UserTable.objects.get(CompanyID=CompanyID, pk=pk)
    if instance:
        serialized = UserTableRestSerializer(instance, context={"CompanyID": CompanyID})
        response_data = {"StatusCode": 6000, "data": serialized.data}
    else:
        response_data = {"StatusCode": 6001, "message": "User Table Not Fount!"}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
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
            CompanyID=CompanyID,
        )
        response_data = {
            "StatusCode": 6000,
            "message": "User Table Deleted Successfully!",
        }
    else:
        response_data = {"StatusCode": 6001, "message": "User Table Not Fount!"}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_user_type(request):
    today = datetime.datetime.now()
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    serialized = UserTypeSerializer(data=request.data)

    if serialized.is_valid():
        UserTypeName = serialized.data["UserTypeName"]
        BranchID = serialized.data["BranchID"]
        Notes = serialized.data["Notes"]
        CreatedUserID = serialized.data["CreatedUserID"]

        ID = get_auto_id(UserType, BranchID, CompanyID)

        is_nameExist = False

        UserNameLow = UserTypeName.lower()

        UserTypes = UserType.objects.filter(CompanyID=CompanyID, BranchID=BranchID)

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
                CompanyID=CompanyID,
            )

            data = {"ID": ID}
            data.update(serialized.data)
            response_data = {"StatusCode": 6000, "data": data}

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "User Type Name Already Exist!!!",
            }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors),
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def userTypes(request):
    serialized1 = ListSerializer(data=request.data)
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)

    if serialized1.is_valid():

        BranchID = serialized1.data["BranchID"]

        if UserType.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():

            instances = UserType.objects.filter(CompanyID=CompanyID, BranchID=BranchID)

            serialized = UserTypeRestSerializer(instances, many=True)

            response_data = {"StatusCode": 6000, "data": serialized.data}

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "User Type Not Found in this BranchID!",
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
@renderer_classes((JSONRenderer,))
def userType(request, pk):
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)

    if UserType.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = UserType.objects.get(CompanyID=CompanyID, pk=pk)
    if instance:
        serialized = UserTypeRestSerializer(instance)
        response_data = {"StatusCode": 6000, "data": serialized.data}
    else:
        response_data = {"StatusCode": 6001, "message": "User Table Not Fount!"}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def edit_userType(request, pk):
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    today = datetime.datetime.now()
    serialized = UserTypeSerializer(data=request.data)
    instance = UserType.objects.get(CompanyID=CompanyID, pk=pk)

    BranchID = instance.BranchID
    ID = instance.ID
    CreatedUserID = instance.CreatedUserID
    instanceUserTypeName = instance.UserTypeName

    if serialized.is_valid():

        UserTypeName = serialized.data["UserTypeName"]
        Notes = serialized.data["Notes"]

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
            response_data = {"StatusCode": 6000, "data": data}

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            if is_nameExist:

                response_data = {
                    "StatusCode": 6001,
                    "message": "UserType Name Already exist with this Branch ID",
                }
                return Response(response_data, status=status.HTTP_200_OK)

            else:
                instance.UserTypeName = UserTypeName
                instance.Notes = Notes
                instance.save()

                data = {"ID": ID}
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
@renderer_classes((JSONRenderer,))
def delete_userType(request, pk):
    CompanyID = data["CompanyID"]
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
            "message": "User Type Deleted Successfully!",
        }
    else:
        response_data = {"StatusCode": 6001, "message": "User Type Not Fount!"}

    return Response(response_data, status=status.HTTP_200_OK)


def send_mail_verification(user, request):
    print("send_mail_verification function")
    token = ""
    # domain = "https://viknbooks.com"
    # domain = "https://vikncodes.in/"
    domain = "http://localhost:3000"
    # if request.META:
    #     domain = request.META['HTTP_ORIGIN']
    if Customer.objects.filter(user=user).exists():
        token = Customer.objects.filter(user=user).first().VerificationToken
    context = {
        "email": user.email,
        "domain": domain,
        "site_name": "viknbooks.com",
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "user": user,
        # 'token': default_token_generator.make_token(user),
        "token": token,
        "current_user": user.first_name + " " + user.last_name,
        "username": user.username,
        "reset_password_url": f"{domain}/signUp-verification/{user.id}/{token}/",
    }

    # email_html_message = render_to_string('email/signup_email.html', context)
    email_html_message = render_to_string("email/one_time_password.html", context)
    subject = "Email Verification for {title}".format(title="viknbooks.com")

    # send_mail(subject, email_html_message, DEFAULT_FROM_EMAIL,
    #           [user.email], fail_silently=False)
    # send_message = EmailMessage(subject, email_html_message, to=[user.email])
    # send_message.content_subtype = "html"
    # send_message.send()

    msg = EmailMultiAlternatives(
        # title:
        "Email Verification",
        # message:
        subject,
        # from:
        "noreply@somehost.local",
        # to:
        [user.email],
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()


@api_view(["POST"])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def user_signup(request):
    today = datetime.datetime.now()
    serialized = SignupSerializer(data=request.data)
    data = request.data
    if serialized.is_valid():
        first_name = serialized.validated_data["first_name"]
        last_name = serialized.validated_data["last_name"]
        username = serialized.validated_data["username"]
        email = serialized.validated_data["email"]
        password1 = serialized.validated_data["password1"]
        password2 = serialized.validated_data["password2"]

        try:
            Phone = data["phone"]
        except:
            Phone = None

        try:
            country = data["Country"]
        except:
            country = None

        try:
            state = data["State"]
        except:
            state = None

        country_ins = None
        state_ins = None
        if Country.objects.filter(id=country).exists():
            country_ins = Country.objects.get(id=country)

        if State.objects.filter(id=state).exists():
            state_ins = State.objects.get(id=state)

        message = ""
        error = False

        bad_domains = ["guerrillamail.com"]
        if "@" in email:
            email_domain = email.split("@")[1]
        else:
            message = "Please enter a proper Email"

        if User.objects.filter(email__iexact=email, is_active=True):
            message = "This email address is already in use."
            error = True
        elif email_domain in bad_domains:
            message = (
                "Registration using %s email addresses is not allowed. Please supply a different email address."
            ) % email_domain
            error = True
            email = email

        min_password_length = 6

        if len(password1) < min_password_length:
            message = "Password must have at least %i characters" % min_password_length
            error = True
        else:
            password1 = password1

        if password1 and password2 and password1 != password2:
            message = "password_mismatch"
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
            message = "Username must have at least %i characters" % min_password_length
            error = True
        else:
            username = username

        active = False

        if not error:
            try:
                timezone = data["timezone"]
            except:
                timezone = None

            verificationToken = generateTokenNo()

            if InviteUsers.objects.filter(Email=email).exists():
                active = True
                invited_user = InviteUsers.objects.filter(Email=email).first()
                user = User.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    username=username,
                    password=password1,
                    is_superuser=False,
                )
                customer = Customer.objects.create(
                    user=user,
                    Phone=Phone,
                    Country=country_ins,
                    State=state_ins,
                    LastLoginCompanyID=invited_user.CompanyID,
                    VerificationToken=verificationToken,
                    VerificationTokenTime=today,
                    TimeZone=timezone,
                )

                user_table = UserTable.objects.create(
                    CompanyID=invited_user.CompanyID,
                    UserType=invited_user.UserType,
                    DefaultAccountForUser=invited_user.DefaultAccountForUser,
                    CreatedUserID=invited_user.InvitedUserID,
                    customer=customer,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Cash_Account=invited_user.Cash_Account,
                    Bank_Account=invited_user.Bank_Account,
                    Sales_Account=invited_user.Sales_Account,
                    Sales_Return_Account=invited_user.Sales_Return_Account,
                    Purchase_Account=invited_user.Purchase_Account,
                    Purchase_Return_Account=invited_user.Purchase_Return_Account,
                    JoinedDate=today.date(),
                    ExpiryDate=invited_user.ExpiryDate,
                    is_web=invited_user.is_web,
                    is_mobile=invited_user.is_mobile,
                    is_pos=invited_user.is_pos,
                    BranchID=invited_user.BranchID,
                    show_all_warehouse=invited_user.show_all_warehouse,
                    DefaultWarehouse=invited_user.DefaultWarehouse,
                )

                User_Log.objects.create(
                    TransactionID=user_table.id,
                    CompanyID=invited_user.CompanyID,
                    UserType=invited_user.UserType,
                    DefaultAccountForUser=invited_user.DefaultAccountForUser,
                    CreatedUserID=invited_user.InvitedUserID,
                    customer=customer,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Cash_Account=invited_user.Cash_Account,
                    Bank_Account=invited_user.Bank_Account,
                    Sales_Account=invited_user.Sales_Account,
                    Sales_Return_Account=invited_user.Sales_Return_Account,
                    Purchase_Account=invited_user.Purchase_Account,
                    Purchase_Return_Account=invited_user.Purchase_Return_Account,
                    JoinedDate=today.date(),
                    ExpiryDate=invited_user.ExpiryDate,
                    is_web=invited_user.is_web,
                    is_mobile=invited_user.is_mobile,
                    is_pos=invited_user.is_pos,
                    BranchID=invited_user.BranchID,
                    show_all_warehouse=invited_user.show_all_warehouse,
                    DefaultWarehouse=invited_user.DefaultWarehouse,
                )

                invited_user.delete()

            else:
                user = User.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    username=username,
                    password=password1,
                    is_superuser=False,
                    is_active=False,
                )
                Customer.objects.create(
                    user=user,
                    Phone=Phone,
                    Country=country_ins,
                    State=state_ins,
                    VerificationToken=verificationToken,
                    VerificationTokenTime=today,
                    TimeZone=timezone,
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
                "data": serialized.data,
                "userID": user.id,
                "active": active,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {"StatusCode": 6001, "message": message}

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors),
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def signUp_verified(request):
    today = datetime.datetime.now()
    data = request.data
    UserID = data["UserID"]
    try:
        token = data["token"]
    except:
        token = None

    if User.objects.filter(id=UserID).exists():
        user = User.objects.get(id=UserID)
        customer_ins = Customer.objects.filter(user=user).first()
        VerificationToken = customer_ins.VerificationToken
        VerificationTokenTime = customer_ins.VerificationTokenTime
        TimeZone = customer_ins.TimeZone
        is_token_expired = CheckTokenExpired(TimeZone, VerificationTokenTime)
        if int(token) == int(VerificationToken) and is_token_expired == False:
            print("its entered")
            user = User.objects.filter(id=UserID).update(is_active=True)

            response_data = {
                "StatusCode": 6000,
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "OTP Expired.please verify again",
            }
    else:
        response_data = {"StatusCode": 6001, "message": "User not found"}

    return Response(response_data, status=status.HTTP_200_OK)
    # else:
    #     response_data = {
    #         "StatusCode": 6001,
    #         "message": message
    #     }

    # return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def resend_verification_code(request):
    today = datetime.datetime.now()
    serialized = UsernameEmailSerializer(data=request.data)
    message = "Invalid Input"
    success = 6001
    status_code = status.HTTP_400_BAD_REQUEST

    userID = None
    if serialized.is_valid():
        data = serialized.data["data"]
        message = f"No user is associated with this {data}"
        success = 6001
        status_code = status.HTTP_400_BAD_REQUEST
        try:
            time_zone = data["timezone"]
        except:
            timezone = None

        verificationToken = generateTokenNo()
        if validate_email_address(data) is True:
            """
            If the input is an valid email address, then the following code will lookup for users associated with that email address. If found then an email will be sent to the address, else an error message will be printed on the screen.
            """
            if User.objects.filter(email=data).exists():
                user = User.objects.get(email=data)
                if Customer.objects.filter(user=user).exists():
                    Customer.objects.filter(user=user).update(
                        VerificationToken=verificationToken,
                        VerificationTokenTime=today,
                        TimeZone=timezone,
                    )
                    send_mail_verification(user, request)
                    userID = user.id

                message = "An email has been sent to {0}. Please check its inbox to continue Resend verification.".format(
                    data
                )
                success = 6000
                status_code = status.HTTP_200_OK

        else:
            message = "This username does not exist in the system"
            success = 6001
            status_code = status.HTTP_400_BAD_REQUEST

            """
            If the input is an username, then the following code will lookup for users associated with that user. If found then an email will be sent to the user's address, else an error message will be printed on the screen.
            """
            if User.objects.filter(email=data).exists():
                user = User.objects.get(email=data)
                if Customer.objects.filter(user=user).exists():
                    Customer.objects.filter(user=user).update(
                        VerificationToken=verificationToken,
                        VerificationTokenTime=today,
                        TimeZone=timezone,
                    )
                    send_mail_verification(user, request)
                    userID = user.id
                message = "Email has been sent to {0}'s email address. Please check its inbox to continue Resend verification.".format(
                    data
                )
                success = 6000
                status_code = status.HTTP_200_OK

    return Response(
        {"message": message, "success": success, "userID": userID}, status=status_code
    )


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def user_view(request, pk):
    instance = Customer.objects.get(user__pk=pk)

    customer_serialized = CustomerUserViewSerializer(
        instance, context={"request": request}
    )
    serialized = UserViewSerializer(instance.user)

    response_data = {
        "StatusCode": 6000,
        "data": serialized.data,
        "customer_data": customer_serialized.data,
    }
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def update_user(request):
    data = request.data
    photo = data["photo"]
    user_id = data["user_id"]

    DateOfBirth = data["DateOfBirth"]
    if DateOfBirth == "null":
        DateOfBirth = None
    else:
        DateOfBirth = DateOfBirth
    Country_pk = data["Country"]
    if Country_pk == "null":
        Country_pk = None
        Countries = None
    else:
        Countries = Country.objects.get(pk=Country_pk)

    Phone = data["Phone"]
    if Phone == "null" or "":
        Phone = None
    else:
        Phone = Phone
    State_pk = data["State"]
    if State_pk == "null":
        States = None
        State_pk = None
    else:
        States = State.objects.get(pk=State_pk)

    City = data["City"]
    if City == "null" or "":
        City = None
    else:
        City = City
    Address = data["Address"]
    if Address == "null" or "":
        Address = None
    else:
        Address = Address
    today = datetime.datetime.now()

    serialized = UpdateSerializer(data=request.data)

    if serialized.is_valid():
        first_name = serialized.validated_data["first_name"]
        last_name = serialized.validated_data["last_name"]
        username = serialized.validated_data["username"]
        email = serialized.validated_data["email"]

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
            message = "Username must have at least %i characters" % min_password_length
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
            response_data = {"StatusCode": 6000, "data": data}
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {"StatusCode": 6001, "message": message}

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors),
        }
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def user_login(request):
    serialized = LoginSerializer(data=request.data)
    CreatedUserID = ""
    is_verified = False
    is_login = False
    user_name_ok = False
    password_ok = False
    customer_ins = None
    data = request.data
    user_id = None
    try:
        is_mobile = data["is_mobile"]
    except:
        is_mobile = False

    if serialized.is_valid():
        username = serialized.data["username"]
        password = serialized.data["password"]
        user_insts = None
        user_email = ""
        if User.objects.filter(email=username).exists():
            email = username
            username = User.objects.get(email=email).username
            user_id = User.objects.get(email=email).id
            user_name_ok = True
            user_insts = User.objects.get(email=email)
        elif User.objects.filter(username=username).exists():
            user_name_ok = True
            user_id = User.objects.get(username=username).id
            user_insts = User.objects.get(username=username)
        if user_insts:
            user_email = user_insts.email
            password_ok = user_insts.check_password(password)
        user = authenticate(username=username, password=password)
        if user:
            is_login = True
            # if User.objects.filter(username=username).exists():
            #     user_ins = User.objects.get(username=username)
            if user.is_active == True:
                is_verified = True
        if user is not None:
            login(request, user)
            request.session["current_role"] = get_current_role(request)
            headers = {
                "Content-Type": "application/json",
            }
            # data = '{"username": "' + username + \
            #     '", "password": "' + password + '" }'
            data = {"username": username, "password": password}
            protocol = "http://"
            if request.is_secure():
                protocol = "https://"

            web_host = request.get_host()
            # request_url = protocol + web_host + "/api/v1/auth/token/"
            request_url = "https://api.accounts.vikncodes.in//api/v1/auth/token/"

            response = requests.post(
                request_url, headers=headers, data=json.dumps(data)
            )
            if response.status_code == 200:
                token_datas = response.json()
                LastToken = token_datas["access"]

                if Customer.objects.filter(user__username=username).exists():
                    customer_ins = Customer.objects.filter(
                        user__username=username
                    ).first()
                    if is_mobile == True:
                        customer_ins.LastLoginTokenMobile = LastToken
                    else:
                        customer_ins.LastLoginToken = LastToken
                    customer_ins.save()

                data = response.json()
                success = 6000
                message = "Login successfully"
                customer_instance = Customer.objects.get(user__id=data["user_id"])
                photo = ""
                if customer_instance.photo:
                    photo = protocol + web_host + customer_instance.photo.url

                return Response(
                    {
                        "success": success,
                        "data": data,
                        "refresh": data["refresh"],
                        "access": data["access"],
                        "user_id": data["user_id"],
                        "role": data["role"],
                        "message": message,
                        "error": None,
                        "CreatedUserID": CreatedUserID,
                        "username": username,
                        "photo": photo,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                success = 6001
                data = None
                error = "please contact admin to solve this problem."
                return Response(
                    {"success": success, "data": data, "error": error},
                    status=status.HTTP_200_OK,
                )
        else:
            success = 6001
            data = None
            error_code = 6002
            if user_name_ok and password_ok == False:
                error = "Password Incorrect"
            elif user_name_ok and is_verified == False:
                error = "Please Verify Your Email to Login"
                error_code = 6003
                data = user_id
            else:
                error = "User not found"
            return Response(
                {
                    "success": success,
                    "data": data,
                    "error": error,
                    "error_code": error_code,
                    "user_email": user_email
                },
                status=status.HTTP_200_OK,
            )
    else:
        message = generate_serializer_errors(serialized._errors)
        success = 6001
        data = None
        return Response(
            {
                "success": success,
                "data": data,
                "error": message,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def check_username(request):
    try:
        username = request.data["username"]
    except:
        username = ""
    try:
        email = request.data["email"]
    except:
        email = ""

    is_username = False
    is_email = False
    if User.objects.filter(username__iexact=username).exists():
        is_username = True
    if User.objects.filter(email__iexact=email).exists():
        is_email = True
    return Response(
        {
            "is_username": is_username,
            "is_email": is_email,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def switch_company(request):
    CompanyID = request.data["CompanyID"]
    user_id = request.data["user_id"]
    response_data = {
        "StatusCode": 6001,
        "message": "failed",
    }
    http_status = status.HTTP_400_BAD_REQUEST
    if (
        Customer.objects.filter(user__id=user_id).exists()
        and CompanySettings.objects.filter(id=CompanyID).exists()
    ):
        company_instance = CompanySettings.objects.get(id=CompanyID)
        Customer.objects.filter(user__id=user_id).update(
            LastLoginCompanyID=company_instance
        )
        serialized = CompanySettingsRestSerializer(
            company_instance,
            many=False,
            context={"request": request, "user_id": user_id},
        )
        response_data = {
            "data": serialized.data,
            "StatusCode": 6000,
            "message": "company successfully switched",
        }
        http_status = status.HTTP_200_OK

    return Response(response_data, status=http_status)


@api_view(["POST"])
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

        username = serialized.data["username"]
        password = serialized.data["password"]

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

            request.session["current_role"] = get_current_role(request)

            headers = {
                "Content-Type": "application/json",
            }

            # data = '{"username": "' + username + \
            #     '", "password": "' + password + '" }'

            data = {"username": username, "password": password}
            protocol = "http://"
            if request.is_secure():
                protocol = "https://"

            web_host = request.get_host()
            request_url = protocol + web_host + "/api/v1/auth/token/"

            response = requests.post(
                request_url, headers=headers, data=json.dumps(data)
            )
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
                if User.objects.filter(
                    username=username, password=password, is_superuser=False
                ).exists():
                    if UserTable.objects.filter(
                        UserName=username, Password=password
                    ).exists():
                        CompanyID = get_object_or_404(
                            UserTable.objects.filter(
                                UserName=username, Password=password
                            )
                        ).CompanyID.id

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

                        user_table_instance = get_object_or_404(
                            UserTable.objects.filter(
                                CompanyID=CompanyID,
                                UserName=username,
                                Password=password,
                            )
                        )
                        EmployeeID = user_table_instance.EmployeeID
                        Cash_Account = user_table_instance.Cash_Account
                        Bank_Account = user_table_instance.Bank_Account
                        WarehouseID = user_table_instance.Warehouse
                        Sales_Account = user_table_instance.Sales_Account
                        Sales_Return_Account = user_table_instance.Sales_Return_Account
                        Purchase_Account = user_table_instance.Purchase_Account
                        Purchase_Return_Account = (
                            user_table_instance.Purchase_Return_Account
                        )
                        Sales_GST_Type = user_table_instance.Sales_GST_Type
                        Purchase_GST_Type = user_table_instance.Purchase_GST_Type
                        VAT_Type = user_table_instance.VAT_Type

                        if AccountLedger.objects.filter(
                            CompanyID=CompanyID, LedgerID=Sales_Account
                        ).exists():
                            Sales_Account_name = get_object_or_404(
                                AccountLedger.objects.filter(
                                    CompanyID=CompanyID, LedgerID=Sales_Account
                                )
                            ).LedgerName

                        if AccountLedger.objects.filter(
                            CompanyID=CompanyID, LedgerID=Sales_Return_Account
                        ).exists():
                            Sales_Return_Account_name = get_object_or_404(
                                AccountLedger.objects.filter(
                                    CompanyID=CompanyID, LedgerID=Sales_Return_Account
                                )
                            ).LedgerName

                        if AccountLedger.objects.filter(
                            CompanyID=CompanyID, LedgerID=Purchase_Account
                        ).exists():
                            Purchase_Account_name = get_object_or_404(
                                AccountLedger.objects.filter(
                                    CompanyID=CompanyID, LedgerID=Purchase_Account
                                )
                            ).LedgerName

                        if AccountLedger.objects.filter(
                            CompanyID=CompanyID, LedgerID=Purchase_Return_Account
                        ).exists():
                            Purchase_Return_Account_name = get_object_or_404(
                                AccountLedger.objects.filter(
                                    CompanyID=CompanyID,
                                    LedgerID=Purchase_Return_Account,
                                )
                            ).LedgerName

                        if AccountLedger.objects.filter(
                            CompanyID=CompanyID, LedgerID=Cash_Account
                        ).exists():
                            Cash_Account_name = get_object_or_404(
                                AccountLedger.objects.filter(
                                    CompanyID=CompanyID, LedgerID=Cash_Account
                                )
                            ).LedgerName

                        if AccountLedger.objects.filter(
                            CompanyID=CompanyID, LedgerID=Bank_Account
                        ).exists():
                            Bank_Account_name = get_object_or_404(
                                AccountLedger.objects.filter(
                                    CompanyID=CompanyID, LedgerID=Bank_Account
                                )
                            ).LedgerName

                        if Employee.objects.filter(
                            CompanyID=CompanyID,
                            EmployeeID=EmployeeID,
                            BranchID=BranchID,
                        ).exists():
                            Employee_name = get_object_or_404(
                                Employee.objects.filter(
                                    CompanyID=CompanyID,
                                    EmployeeID=EmployeeID,
                                    BranchID=BranchID,
                                )
                            ).FirstName

                        if TransactionTypes.objects.filter(
                            CompanyID=CompanyID,
                            TransactionTypesID=VAT_Type,
                            BranchID=BranchID,
                        ).exists():
                            VAT_Type_name = get_object_or_404(
                                TransactionTypes.objects.filter(
                                    CompanyID=CompanyID,
                                    TransactionTypesID=VAT_Type,
                                    BranchID=BranchID,
                                )
                            ).Name

                        if TransactionTypes.objects.filter(
                            CompanyID=CompanyID,
                            TransactionTypesID=Sales_GST_Type,
                            BranchID=BranchID,
                        ).exists():
                            Sales_GST_Type_name = get_object_or_404(
                                TransactionTypes.objects.filter(
                                    CompanyID=CompanyID,
                                    TransactionTypesID=Sales_GST_Type,
                                    BranchID=BranchID,
                                )
                            ).Name

                        if TransactionTypes.objects.filter(
                            CompanyID=CompanyID,
                            TransactionTypesID=Purchase_GST_Type,
                            BranchID=BranchID,
                        ).exists():
                            Purchase_GST_Type_name = get_object_or_404(
                                TransactionTypes.objects.filter(
                                    CompanyID=CompanyID,
                                    TransactionTypesID=Purchase_GST_Type,
                                    BranchID=BranchID,
                                )
                            ).Name

                        if Warehouse.objects.filter(
                            CompanyID=CompanyID,
                            WarehouseID=WarehouseID,
                            BranchID=BranchID,
                        ).exists():
                            Warehouse_name = get_object_or_404(
                                Warehouse.objects.filter(
                                    CompanyID=CompanyID,
                                    WarehouseID=WarehouseID,
                                    BranchID=BranchID,
                                )
                            ).WarehouseName
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

                        if administrations_models.GeneralSettings.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID
                        ).exists():
                            check_VAT = (
                                administrations_models.GeneralSettings.objects.get(
                                    BranchID=BranchID,
                                    CompanyID=CompanyID,
                                    SettingsType="VAT",
                                ).SettingsValue
                            )
                            check_GST = (
                                administrations_models.GeneralSettings.objects.get(
                                    BranchID=BranchID,
                                    CompanyID=CompanyID,
                                    SettingsType="GST",
                                ).SettingsValue
                            )
                            check_TAX1 = (
                                administrations_models.GeneralSettings.objects.get(
                                    BranchID=BranchID,
                                    CompanyID=CompanyID,
                                    SettingsType="TAX1",
                                ).SettingsValue
                            )
                            check_TAX2 = (
                                administrations_models.GeneralSettings.objects.get(
                                    BranchID=BranchID,
                                    CompanyID=CompanyID,
                                    SettingsType="TAX2",
                                ).SettingsValue
                            )
                            check_TAX3 = (
                                administrations_models.GeneralSettings.objects.get(
                                    BranchID=BranchID,
                                    CompanyID=CompanyID,
                                    SettingsType="TAX3",
                                ).SettingsValue
                            )
                            check_Trading = (
                                administrations_models.GeneralSettings.objects.get(
                                    BranchID=BranchID,
                                    CompanyID=CompanyID,
                                    SettingsType="Trading",
                                ).SettingsValue
                            )
                            check_Restaurant = (
                                administrations_models.GeneralSettings.objects.get(
                                    BranchID=BranchID,
                                    CompanyID=CompanyID,
                                    SettingsType="Restaurant",
                                ).SettingsValue
                            )
                            check_QtyDecimalPoint = (
                                administrations_models.GeneralSettings.objects.get(
                                    BranchID=BranchID,
                                    CompanyID=CompanyID,
                                    SettingsType="QtyDecimalPoint",
                                ).SettingsValue
                            )
                            check_loyalty_PointValue = (
                                administrations_models.GeneralSettings.objects.get(
                                    BranchID=BranchID,
                                    CompanyID=CompanyID,
                                    SettingsType="loyalty_PointValue",
                                ).SettingsValue
                            )
                            check_PriceDecimalPoint = (
                                administrations_models.GeneralSettings.objects.get(
                                    BranchID=BranchID,
                                    CompanyID=CompanyID,
                                    SettingsType="PriceDecimalPoint",
                                ).SettingsValue
                            )
                            check_PreDateTransaction = (
                                administrations_models.GeneralSettings.objects.get(
                                    BranchID=BranchID,
                                    CompanyID=CompanyID,
                                    SettingsType="PreDateTransaction",
                                ).SettingsValue
                            )
                            check_PostDateTransaction = (
                                administrations_models.GeneralSettings.objects.get(
                                    BranchID=BranchID,
                                    CompanyID=CompanyID,
                                    SettingsType="PostDateTransaction",
                                ).SettingsValue
                            )
                            check_Additional_Discount = (
                                administrations_models.GeneralSettings.objects.get(
                                    BranchID=BranchID,
                                    CompanyID=CompanyID,
                                    SettingsType="Additional_Discount",
                                ).SettingsValue
                            )
                            check_Bill_Discount = (
                                administrations_models.GeneralSettings.objects.get(
                                    BranchID=BranchID,
                                    CompanyID=CompanyID,
                                    SettingsType="Bill_Discount",
                                ).SettingsValue
                            )
                            check_Negatine_Stock = (
                                administrations_models.GeneralSettings.objects.get(
                                    BranchID=BranchID,
                                    CompanyID=CompanyID,
                                    SettingsType="Negatine_Stock",
                                ).SettingsValue
                            )
                            check_Increment_Qty_In_POS = (
                                administrations_models.GeneralSettings.objects.get(
                                    BranchID=BranchID,
                                    CompanyID=CompanyID,
                                    SettingsType="Increment_Qty_In_POS",
                                ).SettingsValue
                            )
                            check_Kitchen_Print = (
                                administrations_models.GeneralSettings.objects.get(
                                    BranchID=BranchID,
                                    CompanyID=CompanyID,
                                    SettingsType="Kitchen_Print",
                                ).SettingsValue
                            )
                            check_Order_Print = (
                                administrations_models.GeneralSettings.objects.get(
                                    BranchID=BranchID,
                                    CompanyID=CompanyID,
                                    SettingsType="Order_Print",
                                ).SettingsValue
                            )
                            check_Print_After_Save_Active = (
                                administrations_models.GeneralSettings.objects.get(
                                    BranchID=BranchID,
                                    CompanyID=CompanyID,
                                    SettingsType="Print_After_Save_Active",
                                ).SettingsValue
                            )
                            QtyDecimalPoint = (
                                administrations_models.GeneralSettings.objects.get(
                                    BranchID=BranchID,
                                    CompanyID=CompanyID,
                                    SettingsType="QtyDecimalPoint",
                                ).SettingsValue
                            )
                            loyalty_PointValue = (
                                administrations_models.GeneralSettings.objects.get(
                                    BranchID=BranchID,
                                    CompanyID=CompanyID,
                                    SettingsType="loyalty_PointValue",
                                ).SettingsValue
                            )
                            PriceDecimalPoint = (
                                administrations_models.GeneralSettings.objects.get(
                                    BranchID=BranchID,
                                    CompanyID=CompanyID,
                                    SettingsType="PriceDecimalPoint",
                                ).SettingsValue
                            )
                            PreDateTransaction = (
                                administrations_models.GeneralSettings.objects.get(
                                    BranchID=BranchID,
                                    CompanyID=CompanyID,
                                    SettingsType="PreDateTransaction",
                                ).SettingsValue
                            )
                            PostDateTransaction = (
                                administrations_models.GeneralSettings.objects.get(
                                    BranchID=BranchID,
                                    CompanyID=CompanyID,
                                    SettingsType="PostDateTransaction",
                                ).SettingsValue
                            )

                            if check_TAX1 == "false":
                                check_TAX1 = ""

                            if check_TAX2 == "false":
                                check_TAX2 = ""

                            if check_TAX3 == "false":
                                check_TAX3 = ""

                            if check_Additional_Discount == "false":
                                check_Additional_Discount = ""

                            if check_Bill_Discount == "false":
                                check_Bill_Discount = ""

                            if check_Negatine_Stock == "false":
                                check_Negatine_Stock = ""

                            if check_Increment_Qty_In_POS == "false":
                                check_Increment_Qty_In_POS = ""

                            if check_Kitchen_Print == "false":
                                check_Kitchen_Print = ""

                            if check_Order_Print == "false":
                                check_Order_Print = ""

                            if check_Print_After_Save_Active == "false":
                                check_Print_After_Save_Active = ""

                            if check_Trading == "false":
                                check_Trading = ""

                            if check_Restaurant == "false":
                                check_Restaurant = ""

                            if check_Trading == "true":
                                Business_Type = "Trading"
                            else:
                                Business_Type = "Restaurant"

                            if check_VAT == "false":
                                check_VAT = ""

                            if check_GST == "false":
                                check_GST = ""

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
                                "check_loyalty_PointValue": check_loyalty_PointValue,
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
                                "loyalty_PointValue": loyalty_PointValue,
                                "QtyDecimalPoint": QtyDecimalPoint,
                                "PriceDecimalPoint": PriceDecimalPoint,
                                "Business_Type": Business_Type,
                                # "Tax_Active" : Tax_Active,
                            }

                data = response.json()

                success = 6000
                message = "Login successfully"

                company_count = CompanySettings.objects.filter(
                    owner=data["user_id"]
                ).count()
                ExpiryDate = ""
                if company_count == 1:
                    CompanyID = CompanySettings.objects.get(owner=data["user_id"]).id
                    ExpiryDate = CompanySettings.objects.get(
                        owner=data["user_id"]
                    ).ExpiryDate

                return Response(
                    {
                        "success": success,
                        "data": data,
                        "refresh": data["refresh"],
                        "access": data["access"],
                        "user_id": data["user_id"],
                        "role": data["role"],
                        "message": message,
                        "error": None,
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
                        "username": username,
                        "company_count": company_count,
                        "ExpiryDate": ExpiryDate,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                success = 6001
                data = None
                error = "please contact admin to solve this problem."
                return Response(
                    {"success": success, "data": data, "error": error},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            success = 6001
            data = None
            if is_verified == False:
                error = "Please Verify Your Email to Login"
            else:
                error = "User not found"
            return Response(
                {"success": success, "data": data, "error": error},
                status=status.HTTP_400_BAD_REQUEST,
            )

    else:
        message = generate_serializer_errors(serialized._errors)
        success = 6001
        data = None
        return Response(
            {
                "success": success,
                "data": data,
                "error": message,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def check_user(request):
    CompanyID = request.data["CompanyID"]
    CompanyID = get_object_or_404(CompanySettings.objects.filter(id=CompanyID))
    user = False
    if UserTable.objects.filter(CompanyID=CompanyID).exists():
        user = True
        response_data = {"StatusCode": 6000, "user": user}

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        user = False
        response_data = {"StatusCode": 6001, "user": user}

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def logout_view(request):
    try:
        request.user.auth_token.delete()
    except (AttributeError, ObjectDoesNotExist):
        pass
    if getattr(settings, "REST_SESSION_LOGIN", True):
        logout(request)
    response_data = {
        "StatusCode": 6000,
        "message": "Logout successfully",
        "error": None,
    }
    if getattr(settings, "REST_USE_JWT", False):
        from rest_framework_jwt.settings import api_settings as jwt_settings

        if jwt_settings.JWT_AUTH_COOKIE:
            response_data.delete_cookie(jwt_settings.JWT_AUTH_COOKIE)

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_company(request):
    serialized = CreateCompanySerializer(data=request.data)
    if serialized.is_valid():
        CompanyName = serialized.data["CompanyName"]
        Address1 = serialized.data["Address1"]
        Address2 = serialized.data["Address2"]
        Address3 = serialized.data["Address3"]
        city = serialized.data["city"]
        state = serialized.data["state"]
        country = serialized.data["country"]
        postalcode = serialized.data["postalcode"]
        phone = serialized.data["phone"]
        mobile = serialized.data["mobile"]
        email = serialized.data["email"]
        website = serialized.data["website"]
        currency = serialized.data["currency"]
        fractionalunit = serialized.data["fractionalunit"]
        vatnumber = serialized.data["vatnumber"]
        gstnumber = serialized.data["gstnumber"]
        tax1 = serialized.data["tax1"]
        tax2 = serialized.data["tax2"]
        tax3 = serialized.data["tax3"]
        customerid = 1

        db_id = createdb(
            CompanyName,
            Address1,
            Address2,
            Address3,
            city,
            state,
            country,
            postalcode,
            phone,
            mobile,
            email,
            website,
            currency,
            fractionalunit,
            vatnumber,
            gstnumber,
            tax1,
            tax2,
            tax3,
            customerid,
        )

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data,
            "message": "company successfully created",
            "db_id": db_id,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors),
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def companies(request):
    userId = request.data["userId"]
    try:
        is_mobile = request.data["is_mobile"]
    except:
        is_mobile = False

    userId = get_object_or_404(User.objects.filter(id=userId))
    my_company_instances = models.CompanySettings.objects.filter(
        owner=userId, is_deleted=False
    )
    my_company_serialized = MyCompaniesSerializer(
        my_company_instances, many=True, context={"request": request}
    )

    if is_mobile == True:
        member_company_instances = models.UserTable.objects.filter(
            customer__user=userId, is_mobile=True, CompanyID__is_deleted=False
        )
    else:
        member_company_instances = models.UserTable.objects.filter(
            customer__user=userId, is_web=True, CompanyID__is_deleted=False
        )

    member_company_serialized = CompaniesSerializer(
        member_company_instances, many=True, context={"request": request}
    )

    data = []
    for i in my_company_serialized.data:
        id = i["id"]
        CompanyName = i["CompanyName"]
        company_type = i["company_type"]
        ExpiryDate = i["ExpiryDate"]
        Permission = i["Permission"]
        CompanyLogo = i["CompanyLogo"]
        Edition = i["Edition"]
        CompanyDataPerc = i["CompanyDataPerc"]

        print(ExpiryDate)
        ExpiryDate = date.today().strftime("%Y-%m-%d")
        if i["ExpiryDate"] != None:
            ExpiryDate = i["ExpiryDate"]
        dic = {
            "id": id,
            "CompanyName": CompanyName,
            "company_type": company_type,
            "ExpiryDate": ExpiryDate,
            "Permission": Permission,
            "CompanyLogo": CompanyLogo,
            "Edition": Edition,
            "CompanyDataPerc": CompanyDataPerc,
        }
        data.append(dic)

    for i in member_company_serialized.data:
        id = i["id"]
        CompanyName = i["CompanyName"]
        company_type = i["company_type"]
        Permission = i["Permission"]
        CompanyLogo = i["CompanyLogo"]
        Edition = i["Edition"]
        CompanyDataPerc = i["CompanyDataPerc"]
        ExpiryDate = date.today().strftime("%Y-%m-%d")
        if i["ExpiryDate"] != None:
            ExpiryDate = i["ExpiryDate"]
        dic = {
            "id": id,
            "CompanyName": CompanyName,
            "company_type": company_type,
            "ExpiryDate": ExpiryDate,
            "Permission": Permission,
            "CompanyLogo": CompanyLogo,
            "Edition": Edition,
            "CompanyDataPerc": CompanyDataPerc,
        }
        data.append(dic)

    tes_arry = []
    final_array = []
    for i in data:
        if not i["id"] in tes_arry:
            tes_arry.append(i["id"])
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
        "SoftwareVersion": software_version_dic,
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def user_accounts(request):
    CompanyID = request.data["CompanyID"]
    BranchID = request.data["BranchID"]
    CompanyID = get_company(CompanyID)
    cash_accounts = AccountLedger.objects.filter(
        AccountGroupUnder=9, CompanyID=CompanyID
    )
    cash_accounts = AccountLedgerSerializer(cash_accounts, many=True)
    bank_accounts = AccountLedger.objects.filter(
        AccountGroupUnder=8, CompanyID=CompanyID
    )
    bank_accounts = AccountLedgerSerializer(bank_accounts, many=True)
    sales_accounts = AccountLedger.objects.filter(
        AccountGroupUnder=74, CompanyID=CompanyID
    )
    sales_accounts = AccountLedgerSerializer(sales_accounts, many=True)
    purchase_accounts = AccountLedger.objects.filter(
        AccountGroupUnder=48, CompanyID=CompanyID
    )
    purchase_accounts = AccountLedgerSerializer(purchase_accounts, many=True)
    warehouses = Warehouse.objects.all()
    warehouses = WarehouseSerializer(warehouses, many=True)

    sales_gst_types = TransactionTypes.objects.filter(
        MasterTypeID=6, CompanyID=CompanyID
    )
    sales_gst_types = TransactionTypesSerializer(sales_gst_types, many=True)
    purchase_gst_types = TransactionTypes.objects.filter(
        MasterTypeID=7, CompanyID=CompanyID
    )
    purchase_gst_types = TransactionTypesSerializer(purchase_gst_types, many=True)
    vat_types = TransactionTypes.objects.filter(MasterTypeID=8, CompanyID=CompanyID)
    vat_types = TransactionTypesSerializer(vat_types, many=True)
    user_types = UserType.objects.filter(CompanyID=CompanyID)
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
        "user_types": user_types.data,
    }
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_company_user(request, pk):
    CompanyID = request.data["CompanyID"]
    CompanyID = get_company(CompanyID)
    BranchID = request.data["BranchID"]
    today = datetime.datetime.now()
    cash_accounts = AccountLedger.objects.filter(
        AccountGroupUnder=9, CompanyID=CompanyID
    )
    bank_accounts = AccountLedger.objects.filter(
        AccountGroupUnder=8, CompanyID=CompanyID
    )
    sales_accounts = AccountLedger.objects.filter(
        AccountGroupUnder=74, CompanyID=CompanyID
    )
    purchase_accounts = AccountLedger.objects.filter(
        AccountGroupUnder=48, CompanyID=CompanyID
    )
    warehouses = Warehouse.objects.filter(CompanyID=CompanyID)
    sales_gst_types = TransactionTypes.objects.filter(
        MasterTypeID=6, BranchID=BranchID, CompanyID=CompanyID
    )
    purchase_gst_types = TransactionTypes.objects.filter(
        MasterTypeID=7, BranchID=BranchID, CompanyID=CompanyID
    )
    vat_types = TransactionTypes.objects.filter(
        MasterTypeID=8, BranchID=BranchID, CompanyID=CompanyID
    )
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

        email = serialized.data["email"]
        username = serialized.data["username"]
        password1 = serialized.data["password1"]
        password2 = serialized.data["password2"]

        message = ""
        error = False
        if password1 == password2:
            if UserTable.objects.filter(
                CompanyID__Email=email, CompanyID=CompanyID
            ).exists():
                error = True
                message += "This email already exists."
            elif UserTable.objects.filter(
                UserName=username, CompanyID=CompanyID
            ).exists():
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


@api_view(["POST"])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_general_settings(request):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    BranchID = data["BranchID"]
    try:
        loyalty_point_value = data["loyalty_PointValue"]
    except:
        loyalty_point_value = ""

    serialized = GeneralSettingsSerializer(data=request.data)
    if serialized.is_valid():
        try:
            EnableShippingCharge = serialized.data["EnableShippingCharge"]
        except:
            EnableShippingCharge = False
        try:
            AutoIncrimentQty = serialized.data["AutoIncrimentQty"]
        except:
            AutoIncrimentQty = False

        # general => general
        BlockTransactionsByDate = serialized.data["BlockTransactionsByDate"]
        EnableCardDetails = serialized.data["EnableCardDetails"]
        EnableCardNetWork = serialized.data["EnableCardNetWork"]
        EnableLoyaltySettings = serialized.data["EnableLoyaltySettings"]
        PostDateTransaction = serialized.data["PostDateTransaction"]
        PreDateTransaction = serialized.data["PreDateTransaction"]
        ShowDiscountInPayments = serialized.data["ShowDiscountInPayments"]
        ShowDiscountInReceipts = serialized.data["ShowDiscountInReceipts"]
        EnableBillwise = serialized.data["EnableBillwise"]
        # general => decimal points
        PriceDecimalPoint = serialized.data["PriceDecimalPoint"]
        QtyDecimalPoint = serialized.data["QtyDecimalPoint"]
        loyalty_PointValue = serialized.data["loyalty_PointValue"]
        # inventory => general
        CreateBatchForWorkOrder = serialized.data["CreateBatchForWorkOrder"]
        ShowAllProductsInWorkOrder = serialized.data["ShowAllProductsInWorkOrder"]
        EnableProductBatchWise = serialized.data["EnableProductBatchWise"]
        EnableDuplicateProductName = serialized.data["EnableDuplicateProductName"]
        EnableWarehouse = serialized.data["EnableWarehouse"]
        EnableCreditPeriod = serialized.data["EnableCreditPeriod"]
        show_productcode_InsearchSale = serialized.data["show_productcode_InsearchSale"]
        show_productcode_InsearchPurchase = serialized.data[
            "show_productcode_InsearchPurchase"
        ]
        show_stock_InsearchSale = serialized.data["show_stock_InsearchSale"]
        show_stock_InsearchPurchase = serialized.data["show_stock_InsearchPurchase"]
        show_purchasePrice_InsearchSale = serialized.data[
            "show_purchasePrice_InsearchSale"
        ]
        show_salesPrice_InsearchPurchase = serialized.data[
            "show_salesPrice_InsearchPurchase"
        ]
        EnableTransilationInProduct = serialized.data["EnableTransilationInProduct"]
        InclusiveRateWorkOrder = serialized.data["InclusiveRateWorkOrder"]
        MultiUnit = serialized.data["MultiUnit"]
        Negative_Stock_Show = serialized.data["Negative_Stock_Show"]
        PriceCategory = serialized.data["PriceCategory"]
        ShowWarrantyPeriodInProduct = serialized.data["ShowWarrantyPeriodInProduct"]
        ShowYearMonthCalanderInWorkOrder = serialized.data[
            "ShowYearMonthCalanderInWorkOrder"
        ]
        VoucherNoAutoGenerate = serialized.data["VoucherNoAutoGenerate"]
        BatchCriteria = serialized.data["BatchCriteria"]
        # inventory => general => loyalty settings
        is_Loyalty_SalesReturn_MinimumSalePrice = serialized.data[
            "is_Loyalty_SalesReturn_MinimumSalePrice"
        ]
        # inventory => sales
        AllowAdvanceReceiptinSales = serialized.data["AllowAdvanceReceiptinSales"]
        AllowCashReceiptMoreSaleAmt = serialized.data["AllowCashReceiptMoreSaleAmt"]
        AllowNegativeStockSales = serialized.data["AllowNegativeStockSales"]
        AllowNegativeStockInStockTransfer = serialized.data[
            "AllowNegativeStockInStockTransfer"
        ]
        AllowQtyDividerinSales = serialized.data["AllowQtyDividerinSales"]
        AllowUpdateBatchPriceInSales = serialized.data["AllowUpdateBatchPriceInSales"]
        BlockSalesPrice = serialized.data["BlockSalesPrice"]
        BlockSalesBelowPurchase = serialized.data["BlockSalesBelowPurchase"]
        ShowProfitinSalesRegisterReport = serialized.data[
            "ShowProfitinSalesRegisterReport"
        ]
        ShowCustomerLastSalesPriceinSales = serialized.data[
            "ShowCustomerLastSalesPriceinSales"
        ]
        ShowSupplierLastPurchasePriceinPurchase = serialized.data[
            "ShowSupplierLastPurchasePriceinPurchase"
        ]
        EnableItemCodeNoInSales = serialized.data["EnableItemCodeNoInSales"]
        EnableCreditLimit = serialized.data["EnableCreditLimit"]
        EnableFaeraSettings = serialized.data["EnableFaeraSettings"]
        EnableSalesManInSales = serialized.data["EnableSalesManInSales"]
        EnableSerialNoInSales = serialized.data["EnableSerialNoInSales"]
        # EnableShippingCharge
        Free_Quantity_In_Sales = serialized.data["Free_Quantity_In_Sales"]
        InclusiveRateSales = serialized.data["InclusiveRateSales"]
        SalesPriceUpdate = serialized.data["SalesPriceUpdate"]
        ShowDescriptionInSales = serialized.data["ShowDescriptionInSales"]
        ShowDiscountInSales = serialized.data["ShowDiscountInSales"]
        ShowEmployeesInSales = serialized.data["ShowEmployeesInSales"]
        ShowNegativeBatchInSales = serialized.data["ShowNegativeBatchInSales"]
        ShowSettingsinSales = serialized.data["ShowSettingsinSales"]
        ShowSupplierInSales = serialized.data["ShowSupplierInSales"]
        blockSaleByBillDisct = serialized.data["blockSaleByBillDisct"]
        RoundOffSales = serialized.data["RoundOffSales"]
        # inventory => purchase
        AllowAdvanceReceiptinPurchase = serialized.data["AllowAdvanceReceiptinPurchase"]
        AllowCashReceiptMorePurchaseAmt = serialized.data[
            "AllowCashReceiptMorePurchaseAmt"
        ]
        Free_Quantity_In_Purchase = serialized.data["Free_Quantity_In_Purchase"]
        InclusiveRatePurchase = serialized.data["InclusiveRatePurchase"]
        PurchasePriceUpdate = serialized.data["PurchasePriceUpdate"]
        ReferenceBillNo = serialized.data["ReferenceBillNo"]
        ShowCustomerInPurchase = serialized.data["ShowCustomerInPurchase"]
        ShowDiscountInPurchase = serialized.data["ShowDiscountInPurchase"]
        ShowManDateAndExpDatePurchase = serialized.data["ShowManDateAndExpDatePurchase"]
        ShowSalesPriceInPurchase = serialized.data["ShowSalesPriceInPurchase"]
        ShowMaximumStockAlert = serialized.data["ShowMaximumStockAlert"]
        ShowSettingsinPurchase = serialized.data["ShowSettingsinPurchase"]
        RoundOffPurchase = serialized.data["RoundOffPurchase"]

        RoundingFigure = serialized.data["RoundingFigure"]
        VAT = serialized.data["VAT"]
        GST = serialized.data["GST"]
        KFC = serialized.data["KFC"]
        Tax1 = serialized.data["Tax1"]
        Tax2 = serialized.data["Tax2"]
        Tax3 = serialized.data["Tax3"]
        Additional_Discount = serialized.data["Additional_Discount"]
        Bill_Discount = serialized.data["Bill_Discount"]
        Increment_Qty_In_POS = serialized.data["Increment_Qty_In_POS"]
        Kitchen_Print = serialized.data["Kitchen_Print"]
        Order_Print = serialized.data["Order_Print"]
        Print_After_Save_Active = serialized.data["Print_After_Save_Active"]
        Show_Sales_Type = str(serialized.data["Show_Sales_Type"])
        Show_Purchase_Type = serialized.data["Show_Purchase_Type"]
        Purchase_GST_Type = serialized.data["Purchase_GST_Type"]
        Sales_GST_Type = serialized.data["Sales_GST_Type"]
        Sales_VAT_Type = serialized.data["Sales_VAT_Type"]
        Purchase_VAT_Type = serialized.data["Purchase_VAT_Type"]
        Loyalty_Point_Expire = serialized.data["Loyalty_Point_Expire"]
        ShowPositiveStockInSales = serialized.data["ShowPositiveStockInSales"]
        ShowDueBalanceInSales = serialized.data["ShowDueBalanceInSales"]
        ShowDueBalanceInPurchase = serialized.data["ShowDueBalanceInPurchase"]
        AllowExtraSerielNos = serialized.data["AllowExtraSerielNos"]
        EnableVoucherNoUserWise = serialized.data["EnableVoucherNoUserWise"]
        CustomerBasedPrint = serialized.data["CustomerBasedPrint"]

        if (
            QtyDecimalPoint.isnumeric()
            and PriceDecimalPoint.isnumeric()
            and RoundingFigure.isnumeric()
            and RoundOffPurchase.isnumeric()
            and RoundOffSales.isnumeric()
        ):

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

            # CompanyID, SettingsType, SettingsValue, GroupName, User,Action
            # general => general
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "BlockTransactionsByDate",
                BlockTransactionsByDate,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "EnableCardDetails",
                EnableCardDetails,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "loyalty_point_value",
                loyalty_point_value,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "is_Loyalty_SalesReturn_MinimumSalePrice",
                is_Loyalty_SalesReturn_MinimumSalePrice,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID, CompanyID, "MultiUnit", MultiUnit, "Inventory", User, Action
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "AllowNegativeStockSales",
                AllowNegativeStockSales,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "AllowNegativeStockInStockTransfer",
                AllowNegativeStockInStockTransfer,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "PriceCategory",
                PriceCategory,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "InclusiveRateSales",
                InclusiveRateSales,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "InclusiveRatePurchase",
                InclusiveRatePurchase,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "InclusiveRateWorkOrder",
                InclusiveRateWorkOrder,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "ShowDiscountInSales",
                ShowDiscountInSales,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "ShowSupplierInSales",
                ShowSupplierInSales,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "EnableShippingCharge",
                EnableShippingCharge,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "AutoIncrimentQty",
                AutoIncrimentQty,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "ShowDueBalanceInSales",
                ShowDueBalanceInSales,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "ShowDueBalanceInPurchase",
                ShowDueBalanceInPurchase,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "ShowEmployeesInSales",
                ShowEmployeesInSales,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "EnableSerialNoInSales",
                EnableSerialNoInSales,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "EnableItemCodeNoInSales",
                EnableItemCodeNoInSales,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "EnableCreditLimit",
                EnableCreditLimit,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "EnableFaeraSettings",
                EnableFaeraSettings,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "EnableSalesManInSales",
                EnableSalesManInSales,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "ShowWarrantyPeriodInProduct",
                ShowWarrantyPeriodInProduct,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "ShowDescriptionInSales",
                ShowDescriptionInSales,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "AllowExtraSerielNos",
                AllowExtraSerielNos,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "Free_Quantity_In_Sales",
                Free_Quantity_In_Sales,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "Free_Quantity_In_Purchase",
                Free_Quantity_In_Purchase,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "ShowCustomerInPurchase",
                ShowCustomerInPurchase,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "ShowManDateAndExpDatePurchase",
                ShowManDateAndExpDatePurchase,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "ShowDiscountInPurchase",
                ShowDiscountInPurchase,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "ShowDiscountInPayments",
                ShowDiscountInPayments,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "EnableLoyaltySettings",
                EnableLoyaltySettings,
                "Inventory",
                User,
                Action,
            )

            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "CustomerBasedPrint",
                CustomerBasedPrint,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "ShowDiscountInReceipts",
                ShowDiscountInReceipts,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "EnableBillwise",
                EnableBillwise,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "EnableCardNetWork",
                EnableCardNetWork,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "SalesPriceUpdate",
                SalesPriceUpdate,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "PurchasePriceUpdate",
                PurchasePriceUpdate,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "AllowCashReceiptMoreSaleAmt",
                AllowCashReceiptMoreSaleAmt,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "AllowCashReceiptMorePurchaseAmt",
                AllowCashReceiptMorePurchaseAmt,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "AllowAdvanceReceiptinSales",
                AllowAdvanceReceiptinSales,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "AllowAdvanceReceiptinPurchase",
                AllowAdvanceReceiptinPurchase,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "AllowQtyDividerinSales",
                AllowQtyDividerinSales,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "ReferenceBillNo",
                ReferenceBillNo,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "BlockSalesPrice",
                BlockSalesPrice,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "BlockSalesBelowPurchase",
                BlockSalesBelowPurchase,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "ShowProfitinSalesRegisterReport",
                ShowProfitinSalesRegisterReport,
                "Inventory",
                User,
                Action,
            )

            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "ShowCustomerLastSalesPriceinSales",
                ShowCustomerLastSalesPriceinSales,
                "Inventory",
                User,
                Action,
            )

            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "ShowSupplierLastPurchasePriceinPurchase",
                ShowSupplierLastPurchasePriceinPurchase,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "VoucherNoAutoGenerate",
                VoucherNoAutoGenerate,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "EnableVoucherNoUserWise",
                EnableVoucherNoUserWise,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "ShowSalesPriceInPurchase",
                ShowSalesPriceInPurchase,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "ShowMaximumStockAlert",
                ShowMaximumStockAlert,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "ShowSettingsinSales",
                ShowSettingsinSales,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "ShowSettingsinPurchase",
                ShowSettingsinPurchase,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "EnableProductBatchWise",
                EnableProductBatchWise,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "EnableDuplicateProductName",
                EnableDuplicateProductName,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "EnableWarehouse",
                EnableWarehouse,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "EnableCreditPeriod",
                EnableCreditPeriod,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "show_productcode_InsearchSale",
                show_productcode_InsearchSale,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "show_productcode_InsearchPurchase",
                show_productcode_InsearchPurchase,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "show_stock_InsearchSale",
                show_stock_InsearchSale,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "show_stock_InsearchPurchase",
                show_stock_InsearchPurchase,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "show_purchasePrice_InsearchSale",
                show_purchasePrice_InsearchSale,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "show_salesPrice_InsearchPurchase",
                show_salesPrice_InsearchPurchase,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "AllowUpdateBatchPriceInSales",
                AllowUpdateBatchPriceInSales,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "EnableTransilationInProduct",
                EnableTransilationInProduct,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "ShowPositiveStockInSales",
                ShowPositiveStockInSales,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "ShowNegativeBatchInSales",
                ShowNegativeBatchInSales,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "CreateBatchForWorkOrder",
                CreateBatchForWorkOrder,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "ShowAllProductsInWorkOrder",
                ShowAllProductsInWorkOrder,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "ShowYearMonthCalanderInWorkOrder",
                ShowYearMonthCalanderInWorkOrder,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID, CompanyID, "KFC", KFC, "Inventory", User, Action
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "BatchCriteria",
                BatchCriteria,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "blockSaleByBillDisct",
                blockSaleByBillDisct,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "PreDateTransaction",
                PreDateTransaction,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "PostDateTransaction",
                PostDateTransaction,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "RoundOffPurchase",
                RoundOffPurchase,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "RoundOffSales",
                RoundOffSales,
                "Inventory",
                User,
                Action,
            )
            create_or_update_general_settings(
                BranchID,
                CompanyID,
                "loyalty_PointValue",
                loyalty_PointValue,
                "Inventory",
                User,
                Action,
            )

            # CompanyID, SettingsType, SettingsValue, User, Action
            update_general_settings(
                CompanyID, "Purchase_GST_Type", Purchase_GST_Type, User, Action
            )
            update_general_settings(
                CompanyID, "Sales_GST_Type", Sales_GST_Type, User, Action
            )
            update_general_settings(
                CompanyID, "Sales_VAT_Type", Sales_VAT_Type, User, Action
            )
            update_general_settings(
                CompanyID, "Purchase_VAT_Type", Purchase_VAT_Type, User, Action
            )
            update_general_settings(
                CompanyID, "Show_Sales_Type", Show_Sales_Type, User, Action
            )
            update_general_settings(
                CompanyID, "Show_Purchase_Type", Show_Purchase_Type, User, Action
            )
            update_general_settings(CompanyID, "VAT", VAT, User, Action)
            update_general_settings(CompanyID, "GST", GST, User, Action)
            update_general_settings(CompanyID, "TAX1", Tax1, User, Action)
            update_general_settings(CompanyID, "TAX2", Tax2, User, Action)
            update_general_settings(CompanyID, "TAX3", Tax3, User, Action)
            update_general_settings(
                CompanyID, "QtyDecimalPoint", QtyDecimalPoint, User, Action
            )
            update_general_settings(
                CompanyID, "loyalty_PointValue", loyalty_PointValue, User, Action
            )
            update_general_settings(
                CompanyID, "PriceDecimalPoint", PriceDecimalPoint, User, Action
            )
            update_general_settings(
                CompanyID, "RoundingFigure", RoundingFigure, User, Action
            )
            update_general_settings(
                CompanyID, "Additional_Discount", Additional_Discount, User, Action
            )
            update_general_settings(
                CompanyID, "Bill_Discount", Bill_Discount, User, Action
            )
            update_general_settings(
                CompanyID, "Negatine_Stock", Negative_Stock_Show, User, Action
            )

            Purchase_VAT_Type_name = ""
            Sales_VAT_Type_name = ""
            Sales_GST_Type_name = ""
            Purchase_GST_Type_name = ""
            if TransactionTypes.objects.filter(
                CompanyID=CompanyID,
                TransactionTypesID=Purchase_VAT_Type,
                BranchID=BranchID,
            ).exists():
                Purchase_VAT_Type_name = get_object_or_404(
                    TransactionTypes.objects.filter(
                        CompanyID=CompanyID,
                        TransactionTypesID=Purchase_VAT_Type,
                        BranchID=BranchID,
                    )
                ).Name

            if TransactionTypes.objects.filter(
                CompanyID=CompanyID,
                TransactionTypesID=Sales_VAT_Type,
                BranchID=BranchID,
            ).exists():
                Sales_VAT_Type_name = get_object_or_404(
                    TransactionTypes.objects.filter(
                        CompanyID=CompanyID,
                        TransactionTypesID=Sales_VAT_Type,
                        BranchID=BranchID,
                    )
                ).Name

            if TransactionTypes.objects.filter(
                CompanyID=CompanyID,
                TransactionTypesID=Sales_GST_Type,
                BranchID=BranchID,
            ).exists():
                Sales_GST_Type_name = get_object_or_404(
                    TransactionTypes.objects.filter(
                        CompanyID=CompanyID,
                        TransactionTypesID=Sales_GST_Type,
                        BranchID=BranchID,
                    )
                ).Name

            if TransactionTypes.objects.filter(
                CompanyID=CompanyID,
                TransactionTypesID=Purchase_GST_Type,
                BranchID=BranchID,
            ).exists():
                Purchase_GST_Type_name = get_object_or_404(
                    TransactionTypes.objects.filter(
                        CompanyID=CompanyID,
                        TransactionTypesID=Purchase_GST_Type,
                        BranchID=BranchID,
                    )
                ).Name

            general_settings = administrations_models.GeneralSettings.objects.filter(
                CompanyID=CompanyID
            )
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
                    CompanyID=CompanyID,
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
                "message": "You enterd an invalid number",
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
@renderer_classes((JSONRenderer,))
def general_settings_list(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]

    BranchID = data["BranchID"]
    PreDateTransaction = 30
    PostDateTransaction = 30
    if administrations_models.GeneralSettings.objects.filter(
        CompanyID=CompanyID, BranchID=BranchID
    ).exists():
        instances = administrations_models.GeneralSettings.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID
        )
        # =====
        try:
            loyalty_point_value = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID,
                BranchID=BranchID,
                SettingsType="loyalty_point_value",
            ).SettingsValue
        except:
            loyalty_point_value = ""
        # ======
        test = get_general_settings(BranchID, CompanyID, "AllowNegativeStockSales")
        print(test, "AllowNegativeStockSales", BranchID)
        Purchase_GST_Type = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, BranchID=BranchID, SettingsType="Purchase_GST_Type"
        ).SettingsValue
        Sales_GST_Type = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, BranchID=BranchID, SettingsType="Sales_GST_Type"
        ).SettingsValue
        Sales_VAT_Type = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, BranchID=BranchID, SettingsType="Sales_VAT_Type"
        ).SettingsValue
        Purchase_VAT_Type = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, BranchID=BranchID, SettingsType="Purchase_VAT_Type"
        ).SettingsValue
        QtyDecimalPoint = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, BranchID=BranchID, SettingsType="QtyDecimalPoint"
        ).SettingsValue
        loyalty_PointValue = 0
        if administrations_models.GeneralSettings.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, SettingsType="loyalty_PointValue"
        ).exists():
            loyalty_PointValue = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID,
                BranchID=BranchID,
                SettingsType="loyalty_PointValue",
            ).SettingsValue

        PriceDecimalPoint = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, BranchID=BranchID, SettingsType="PriceDecimalPoint"
        ).SettingsValue
        if administrations_models.GeneralSettings.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, SettingsType="PreDateTransaction"
        ).exists():
            PreDateTransaction = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID,
                BranchID=BranchID,
                SettingsType="PreDateTransaction",
            ).SettingsValue
        if administrations_models.GeneralSettings.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, SettingsType="PostDateTransaction"
        ).exists():
            PostDateTransaction = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID,
                BranchID=BranchID,
                SettingsType="PostDateTransaction",
            ).SettingsValue

        PriceDecimalPoint = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, BranchID=BranchID, SettingsType="PriceDecimalPoint"
        ).SettingsValue
        RoundingFigure = administrations_models.GeneralSettings.objects.get(
            CompanyID=CompanyID, BranchID=BranchID, SettingsType="RoundingFigure"
        ).SettingsValue

        RoundOffPurchase = 5
        if administrations_models.GeneralSettings.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, SettingsType="RoundOffPurchase"
        ).exists():
            RoundOffPurchase = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, SettingsType="RoundOffPurchase"
            ).SettingsValue

        RoundOffSales = 5
        if administrations_models.GeneralSettings.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, SettingsType="RoundOffSales"
        ).exists():
            RoundOffSales = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, SettingsType="RoundOffSales"
            ).SettingsValue

        BatchCriteria = ""
        if administrations_models.GeneralSettings.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, SettingsType="BatchCriteria"
        ).exists():
            BatchCriteria = administrations_models.GeneralSettings.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, SettingsType="BatchCriteria"
            ).SettingsValue

        Show_Sales_Type = get_general_settings(BranchID, CompanyID, "Show_Sales_Type")
        Show_Purchase_Type = get_general_settings(
            BranchID, CompanyID, "Show_Purchase_Type"
        )
        VAT = get_general_settings(BranchID, CompanyID, "VAT")
        GST = get_general_settings(BranchID, CompanyID, "GST")
        TAX1 = get_general_settings(BranchID, CompanyID, "TAX1")
        TAX2 = get_general_settings(BranchID, CompanyID, "TAX2")
        TAX3 = get_general_settings(BranchID, CompanyID, "TAX3")
        Show_Sales_Type = get_general_settings(BranchID, CompanyID, "Show_Sales_Type")
        Additional_Discount = get_general_settings(
            BranchID, CompanyID, "Additional_Discount"
        )
        Bill_Discount = get_general_settings(BranchID, CompanyID, "Bill_Discount")
        Negative_Stock_Show = get_general_settings(
            BranchID, CompanyID, "Negatine_Stock"
        )
        Increment_Qty_In_POS = get_general_settings(
            BranchID, CompanyID, "Increment_Qty_In_POS"
        )
        Kitchen_Print = get_general_settings(BranchID, CompanyID, "Kitchen_Print")
        Order_Print = get_general_settings(BranchID, CompanyID, "Order_Print")
        Print_After_Save_Active = get_general_settings(
            BranchID, CompanyID, "Print_After_Save_Active"
        )
        Loyalty_Point_Expire = get_general_settings(
            BranchID, CompanyID, "Loyalty_Point_Expire"
        )
        is_Loyalty_SalesReturn_MinimumSalePrice = get_general_settings(
            BranchID, CompanyID, "is_Loyalty_SalesReturn_MinimumSalePrice"
        )
        MultiUnit = get_general_settings(BranchID, CompanyID, "MultiUnit")
        AllowNegativeStockSales = get_general_settings(
            BranchID, CompanyID, "AllowNegativeStockSales"
        )
        AllowNegativeStockInStockTransfer = get_general_settings(
            BranchID, CompanyID, "AllowNegativeStockInStockTransfer"
        )
        PriceCategory = get_general_settings(BranchID, CompanyID, "PriceCategory")
        InclusiveRateSales = get_general_settings(
            BranchID, CompanyID, "InclusiveRateSales"
        )
        InclusiveRatePurchase = get_general_settings(
            BranchID, CompanyID, "InclusiveRatePurchase"
        )
        InclusiveRateWorkOrder = get_general_settings(
            BranchID, CompanyID, "InclusiveRateWorkOrder"
        )
        ShowDiscountInSales = get_general_settings(
            BranchID, CompanyID, "ShowDiscountInSales"
        )
        ShowSupplierInSales = get_general_settings(
            BranchID, CompanyID, "ShowSupplierInSales"
        )
        EnableShippingCharge = get_general_settings(
            BranchID, CompanyID, "EnableShippingCharge"
        )
        AutoIncrimentQty = get_general_settings(BranchID, CompanyID, "AutoIncrimentQty")
        ShowDueBalanceInSales = get_general_settings(
            BranchID, CompanyID, "ShowDueBalanceInSales"
        )
        ShowDueBalanceInPurchase = get_general_settings(
            BranchID, CompanyID, "ShowDueBalanceInPurchase"
        )
        ShowEmployeesInSales = get_general_settings(
            BranchID, CompanyID, "ShowEmployeesInSales"
        )
        EnableSerialNoInSales = get_general_settings(
            BranchID, CompanyID, "EnableSerialNoInSales"
        )
        EnableItemCodeNoInSales = get_general_settings(
            BranchID, CompanyID, "EnableItemCodeNoInSales"
        )
        EnableCreditLimit = get_general_settings(
            BranchID, CompanyID, "EnableCreditLimit"
        )
        EnableFaeraSettings = get_general_settings(
            BranchID, CompanyID, "EnableFaeraSettings"
        )
        EnableSalesManInSales = get_general_settings(
            BranchID, CompanyID, "EnableSalesManInSales"
        )
        ShowWarrantyPeriodInProduct = get_general_settings(
            BranchID, CompanyID, "ShowWarrantyPeriodInProduct"
        )
        ShowDescriptionInSales = get_general_settings(
            BranchID, CompanyID, "ShowDescriptionInSales"
        )
        AllowExtraSerielNos = get_general_settings(
            BranchID, CompanyID, "AllowExtraSerielNos"
        )
        Free_Quantity_In_Sales = get_general_settings(
            BranchID, CompanyID, "Free_Quantity_In_Sales"
        )
        Free_Quantity_In_Purchase = get_general_settings(
            BranchID, CompanyID, "Free_Quantity_In_Purchase"
        )
        ShowCustomerInPurchase = get_general_settings(
            BranchID, CompanyID, "ShowCustomerInPurchase"
        )
        ShowManDateAndExpDatePurchase = get_general_settings(
            BranchID, CompanyID, "ShowManDateAndExpDatePurchase"
        )
        ShowDiscountInPurchase = get_general_settings(
            BranchID, CompanyID, "ShowDiscountInPurchase"
        )
        ShowDiscountInPayments = get_general_settings(
            BranchID, CompanyID, "ShowDiscountInPayments"
        )
        ShowDiscountInReceipts = get_general_settings(
            BranchID, CompanyID, "ShowDiscountInReceipts"
        )
        EnableBillwise = get_general_settings(BranchID, CompanyID, "EnableBillwise")
        EnableLoyaltySettings = get_general_settings(
            BranchID, CompanyID, "EnableLoyaltySettings"
        )

        CustomerBasedPrint = get_general_settings(
            BranchID, CompanyID, "CustomerBasedPrint"
        )
        EnableCardNetWork = get_general_settings(
            BranchID, CompanyID, "EnableCardNetWork"
        )
        BlockTransactionsByDate = get_general_settings(
            BranchID, CompanyID, "BlockTransactionsByDate"
        )
        EnableCardDetails = get_general_settings(
            BranchID, CompanyID, "EnableCardDetails"
        )
        SalesPriceUpdate = get_general_settings(BranchID, CompanyID, "SalesPriceUpdate")
        PurchasePriceUpdate = get_general_settings(
            BranchID, CompanyID, "PurchasePriceUpdate"
        )
        AllowCashReceiptMoreSaleAmt = get_general_settings(
            BranchID, CompanyID, "AllowCashReceiptMoreSaleAmt"
        )
        AllowCashReceiptMorePurchaseAmt = get_general_settings(
            BranchID, CompanyID, "AllowCashReceiptMorePurchaseAmt"
        )
        AllowAdvanceReceiptinSales = get_general_settings(
            BranchID, CompanyID, "AllowAdvanceReceiptinSales"
        )
        AllowAdvanceReceiptinPurchase = get_general_settings(
            BranchID, CompanyID, "AllowAdvanceReceiptinPurchase"
        )
        AllowQtyDividerinSales = get_general_settings(
            BranchID, CompanyID, "AllowQtyDividerinSales"
        )
        ReferenceBillNo = get_general_settings(BranchID, CompanyID, "ReferenceBillNo")
        BlockSalesPrice = get_general_settings(
            BranchID, CompanyID, "BlockSalesPrice")
        BlockSalesBelowPurchase = get_general_settings(
            BranchID, CompanyID, "BlockSalesBelowPurchase")
        ShowProfitinSalesRegisterReport = get_general_settings(
            BranchID, CompanyID, "ShowProfitinSalesRegisterReport"
        )

        ShowCustomerLastSalesPriceinSales = get_general_settings(
            BranchID, CompanyID, "ShowCustomerLastSalesPriceinSales"
        )

        ShowSupplierLastPurchasePriceinPurchase = get_general_settings(
            BranchID, CompanyID, "ShowSupplierLastPurchasePriceinPurchase"
        )
        VoucherNoAutoGenerate = get_general_settings(
            BranchID, CompanyID, "VoucherNoAutoGenerate"
        )
        EnableVoucherNoUserWise = get_general_settings(
            BranchID, CompanyID, "EnableVoucherNoUserWise"
        )
        ShowSalesPriceInPurchase = get_general_settings(
            BranchID, CompanyID, "ShowSalesPriceInPurchase"
        )
        ShowMaximumStockAlert = get_general_settings(
            BranchID, CompanyID, "ShowMaximumStockAlert"
        )
        ShowSettingsinSales = get_general_settings(
            BranchID, CompanyID, "ShowSettingsinSales"
        )
        ShowSettingsinPurchase = get_general_settings(
            BranchID, CompanyID, "ShowSettingsinPurchase"
        )
        EnableProductBatchWise = get_general_settings(
            BranchID, CompanyID, "EnableProductBatchWise"
        )
        EnableDuplicateProductName = get_general_settings(
            BranchID, CompanyID, "EnableDuplicateProductName"
        )
        EnableWarehouse = get_general_settings(
            BranchID, CompanyID, "EnableWarehouse")
        EnableCreditPeriod = get_general_settings(
            BranchID, CompanyID, "EnableCreditPeriod")
        show_productcode_InsearchSale = get_general_settings(
            BranchID, CompanyID, "show_productcode_InsearchSale"
        )
        show_productcode_InsearchPurchase = get_general_settings(
            BranchID, CompanyID, "show_productcode_InsearchPurchase"
        )
        show_stock_InsearchSale = get_general_settings(
            BranchID, CompanyID, "show_stock_InsearchSale"
        )
        show_stock_InsearchPurchase = get_general_settings(
            BranchID, CompanyID, "show_stock_InsearchPurchase"
        )
        show_purchasePrice_InsearchSale = get_general_settings(
            BranchID, CompanyID, "show_purchasePrice_InsearchSale"
        )
        show_salesPrice_InsearchPurchase = get_general_settings(
            BranchID, CompanyID, "show_salesPrice_InsearchPurchase"
        )
        AllowUpdateBatchPriceInSales = get_general_settings(
            BranchID, CompanyID, "AllowUpdateBatchPriceInSales"
        )
        EnableTransilationInProduct = get_general_settings(
            BranchID, CompanyID, "EnableTransilationInProduct"
        )
        ShowPositiveStockInSales = get_general_settings(
            BranchID, CompanyID, "ShowPositiveStockInSales"
        )
        ShowNegativeBatchInSales = get_general_settings(
            BranchID, CompanyID, "ShowNegativeBatchInSales"
        )
        CreateBatchForWorkOrder = get_general_settings(
            BranchID, CompanyID, "CreateBatchForWorkOrder"
        )
        ShowAllProductsInWorkOrder = get_general_settings(
            BranchID, CompanyID, "ShowAllProductsInWorkOrder"
        )
        ShowYearMonthCalanderInWorkOrder = get_general_settings(
            BranchID, CompanyID, "ShowYearMonthCalanderInWorkOrder"
        )
        KFC = get_general_settings(BranchID, CompanyID, "KFC")
        blockSaleByBillDisct = get_general_settings(
            BranchID, CompanyID, "blockSaleByBillDisct"
        )

        if VAT == "true" or VAT == True or VAT == "True":
            Purchase_VAT_Type = 32
            Sales_VAT_Type = 32

        sales_gst_types = TransactionTypes.objects.filter(
            MasterTypeID=6, CompanyID=CompanyID
        )
        sales_gst_types = TransactionTypesSerializer(sales_gst_types, many=True)
        purchase_gst_types = TransactionTypes.objects.filter(
            MasterTypeID=7, CompanyID=CompanyID
        )
        purchase_gst_types = TransactionTypesSerializer(purchase_gst_types, many=True)
        vat_types = TransactionTypes.objects.filter(MasterTypeID=8, CompanyID=CompanyID)
        vat_types = TransactionTypesSerializer(vat_types, many=True)

        if TransactionTypes.objects.filter(
            CompanyID=CompanyID, TransactionTypesID=Sales_VAT_Type
        ).exists():
            Sales_VAT_Type_name = get_object_or_404(
                TransactionTypes.objects.filter(
                    CompanyID=CompanyID, TransactionTypesID=Sales_VAT_Type
                )
            ).Name

        if TransactionTypes.objects.filter(
            CompanyID=CompanyID, TransactionTypesID=Purchase_VAT_Type
        ).exists():
            Purchase_VAT_Type_name = get_object_or_404(
                TransactionTypes.objects.filter(
                    CompanyID=CompanyID, TransactionTypesID=Purchase_VAT_Type
                )
            ).Name

        if TransactionTypes.objects.filter(
            CompanyID=CompanyID, TransactionTypesID=Sales_GST_Type
        ).exists():
            Sales_GST_Type_name = get_object_or_404(
                TransactionTypes.objects.filter(
                    CompanyID=CompanyID, TransactionTypesID=Sales_GST_Type
                )
            ).Name

        if TransactionTypes.objects.filter(
            CompanyID=CompanyID, TransactionTypesID=Purchase_GST_Type
        ).exists():
            Purchase_GST_Type_name = get_object_or_404(
                TransactionTypes.objects.filter(
                    CompanyID=CompanyID, TransactionTypesID=Purchase_GST_Type
                )
            ).Name

        dic = {
            "loyalty_point_value": loyalty_point_value,
            "Purchase_GST_Type": Purchase_GST_Type,
            "Sales_GST_Type": Sales_GST_Type,
            "Sales_VAT_Type": Sales_VAT_Type,
            "Purchase_VAT_Type": Purchase_VAT_Type,
            "Show_Sales_Type": Show_Sales_Type,
            "Show_Purchase_Type": Show_Purchase_Type,
            "VAT": VAT,
            "GST": GST,
            "Tax1": TAX1,
            "Tax2": TAX2,
            "Tax3": TAX3,
            "QtyDecimalPoint": QtyDecimalPoint,
            "loyalty_PointValue": loyalty_PointValue,
            "PriceDecimalPoint": PriceDecimalPoint,
            "PreDateTransaction": PreDateTransaction,
            "PostDateTransaction": PostDateTransaction,
            "Additional_Discount": Additional_Discount,
            "Bill_Discount": Bill_Discount,
            "Negative_Stock_Show": Negative_Stock_Show,
            "Increment_Qty_In_POS": Increment_Qty_In_POS,
            "Kitchen_Print": Kitchen_Print,
            "Order_Print": Order_Print,
            "Print_After_Save_Active": Print_After_Save_Active,
            "QtyDecimalPoint": QtyDecimalPoint,
            "loyalty_PointValue": loyalty_PointValue,
            "PreDateTransaction": PreDateTransaction,
            "PostDateTransaction": PostDateTransaction,
            "PriceDecimalPoint": PriceDecimalPoint,
            "RoundingFigure": RoundOffSales,
            "RoundOffPurchase": RoundOffPurchase,
            "RoundOffSales": RoundOffSales,
            "sales_gst_types": sales_gst_types.data,
            "purchase_gst_types": purchase_gst_types.data,
            "vat_types": vat_types.data,
            "MultiUnit": MultiUnit,
            "Loyalty_Point_Expire": Loyalty_Point_Expire,
            "is_Loyalty_SalesReturn_MinimumSalePrice": is_Loyalty_SalesReturn_MinimumSalePrice,
            "AllowNegativeStockSales": AllowNegativeStockSales,
            "AllowNegativeStockInStockTransfer": AllowNegativeStockInStockTransfer,
            "PriceCategory": PriceCategory,
            "InclusiveRateSales": InclusiveRateSales,
            "InclusiveRatePurchase": InclusiveRatePurchase,
            "InclusiveRateWorkOrder": InclusiveRateWorkOrder,
            "ShowDiscountInSales": ShowDiscountInSales,
            "ShowSupplierInSales": ShowSupplierInSales,
            "EnableShippingCharge": EnableShippingCharge,
            "AutoIncrimentQty": AutoIncrimentQty,
            "ShowDueBalanceInSales": ShowDueBalanceInSales,
            "ShowDueBalanceInPurchase": ShowDueBalanceInPurchase,
            "ShowEmployeesInSales": ShowEmployeesInSales,
            "EnableSerialNoInSales": EnableSerialNoInSales,
            "EnableItemCodeNoInSales": EnableItemCodeNoInSales,
            "EnableCreditLimit": EnableCreditLimit,
            "EnableFaeraSettings": EnableFaeraSettings,
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
            "EnableBillwise": EnableBillwise,
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
            "BlockSalesBelowPurchase": BlockSalesBelowPurchase,
            "ShowProfitinSalesRegisterReport": ShowProfitinSalesRegisterReport,
            "ShowCustomerLastSalesPriceinSales": ShowCustomerLastSalesPriceinSales,
            "ShowSupplierLastPurchasePriceinPurchase": ShowSupplierLastPurchasePriceinPurchase,
            "VoucherNoAutoGenerate": VoucherNoAutoGenerate,
            "EnableVoucherNoUserWise": EnableVoucherNoUserWise,
            "ShowSalesPriceInPurchase": ShowSalesPriceInPurchase,
            "ShowMaximumStockAlert": ShowMaximumStockAlert,
            "ShowSettingsinSales": ShowSettingsinSales,
            "ShowSettingsinPurchase": ShowSettingsinPurchase,
            "EnableProductBatchWise": EnableProductBatchWise,
            "EnableDuplicateProductName": EnableDuplicateProductName,
            "EnableWarehouse": EnableWarehouse,
            "EnableCreditPeriod": EnableCreditPeriod,
            "show_productcode_InsearchSale": show_productcode_InsearchSale,
            "show_productcode_InsearchPurchase": show_productcode_InsearchPurchase,
            "show_stock_InsearchSale": show_stock_InsearchSale,
            "show_stock_InsearchPurchase": show_stock_InsearchPurchase,
            "show_purchasePrice_InsearchSale": show_purchasePrice_InsearchSale,
            "show_salesPrice_InsearchPurchase": show_salesPrice_InsearchPurchase,
            "AllowUpdateBatchPriceInSales": AllowUpdateBatchPriceInSales,
            "EnableTransilationInProduct": EnableTransilationInProduct,
            "ShowPositiveStockInSales": ShowPositiveStockInSales,
            "ShowNegativeBatchInSales": ShowNegativeBatchInSales,
            "CreateBatchForWorkOrder": CreateBatchForWorkOrder,
            "ShowAllProductsInWorkOrder": ShowAllProductsInWorkOrder,
            "ShowYearMonthCalanderInWorkOrder": ShowYearMonthCalanderInWorkOrder,
            "KFC": KFC,
            "BatchCriteria": BatchCriteria,
            "blockSaleByBillDisct": blockSaleByBillDisct,
            "Sales_VAT_Type_name": Sales_VAT_Type_name,
            "Purchase_VAT_Type_name": Purchase_VAT_Type_name,
            "Sales_GST_Type_name": Sales_GST_Type_name,
            "Purchase_GST_Type_name": Purchase_GST_Type_name,
        }
        # request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'GeneralSettings', 'List', 'GeneralSettings List Viewed Successfully.', "GeneralSettings List Viewed Successfully.")
        response_data = {
            "StatusCode": 6000,
            "data": dic,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {"StatusCode": 6001, "message": "Settings not found"}
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def get_company_details(request):
    userId = request.data["userId"]
    # BranchID = request.data['BranchID']

    company_count = CompanySettings.objects.filter(
        owner__pk=userId, is_deleted=False
    ).count()
    CompanyName = ""
    CountryName = ""
    CountryID = ""
    CountryCode = ""
    BussinesType = ""
    Country = ""
    CurrencySymbol = ""
    State = ""
    StateName = ""
    State_Code = ""
    CompanyLogo = ""
    City = ""
    Address1 = ""
    Address2 = ""
    Address3 = ""
    ExpiryDate = ""
    Edition = ""
    EnableZatca = False

    # if Customer.objects.filter(user__pk=userId).exists() and CompanySettings.objects.filter(owner__pk=userId, is_deleted=False).exists():
    if Customer.objects.filter(user__pk=userId).exists() and (
        CompanySettings.objects.filter(owner__pk=userId, is_deleted=False).exists()
        or UserTable.objects.filter(customer__user=userId).exists()
    ):
        customer_instance = Customer.objects.get(user__pk=userId)
        LastLoginCompanyID = None
        if customer_instance.LastLoginCompanyID:
            LastLoginCompanyID = customer_instance.LastLoginCompanyID
        elif UserTable.objects.filter(customer__user=userId).exists():
            LastLoginCompanyID = (
                UserTable.objects.filter(customer__user=userId).last().CompanyID
            )
        if LastLoginCompanyID:
            pk = LastLoginCompanyID.id
            if CompanySettings.objects.filter(pk=pk, is_deleted=False).exists():
                CompanyID = pk
        else:
            if company_count == 1:
                CompanyID = CompanySettings.objects.get(
                    owner__pk=userId, is_deleted=False
                ).id
                ExpiryDate = CompanySettings.objects.get(
                    owner__pk=userId, is_deleted=False
                ).ExpiryDate
            else:
                CompanyID = (
                    CompanySettings.objects.filter(owner__pk=userId, is_deleted=False)
                    .last()
                    .id
                )

        if CompanyID:
            company_instance = CompanySettings.objects.get(
                pk=CompanyID, is_deleted=False
            )
            CompanyName = company_instance.CompanyName
            CountryName = company_instance.Country.Country_Name
            CountryID = company_instance.Country.id
            CountryCode = company_instance.Country.CountryCode
            BussinesType = company_instance.business_type.Name
            Country = company_instance.Country.id
            CurrencySymbol = company_instance.Country.Symbol
            State = company_instance.State.id
            StateName = company_instance.State.Name
            State_Code = company_instance.State.State_Code
            if company_instance.CompanyLogo and hasattr(
                company_instance.CompanyLogo, "url"
            ):
                CompanyLogo = company_instance.CompanyLogo.url
            City = company_instance.City
            Address1 = company_instance.Address1
            Address2 = company_instance.Address2
            Address3 = company_instance.Address3
            Edition = company_instance.Edition
            ExpiryDate = company_instance.ExpiryDate
            EnableZatca = company_instance.EnableZatca
            serialized = CompanySettingsRestSerializer(
                company_instance,
                many=False,
                context={"request": request, "userId": userId},
            )
        response_data = {
            "data": {
                **serialized.data,
                "company_count": company_count,
                "CompanyID": CompanyID,
                "ExpiryDate": ExpiryDate,
            },
            "StatusCode": 6000,
            "message": "success",
        }
    else:
        response_data = {"StatusCode": 6001, "message": "company not found"}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def get_financial_year(request):
    CompanyID = request.data["CompanyID"]
    # BranchID = request.data['BranchID']
    # userId = request.data['userId']

    if FinancialYear.objects.filter(CompanyID=CompanyID, IsClosed=False).exists():
        financialyear = FinancialYear.objects.filter(
            CompanyID=CompanyID, IsClosed=False
        ).first()
        financial_FromDate = financialyear.FromDate
        financial_ToDate = financialyear.ToDate
    else:
        try:
            financialyear = FinancialYear.objects.filter(CompanyID=CompanyID).first()
            financial_FromDate = financialyear.FromDate
            financial_ToDate = financialyear.ToDate
        except:
            financial_FromDate = ""
            financial_ToDate = ""

    data = {
        "financial_FromDate": financial_FromDate,
        "financial_ToDate": financial_ToDate,
    }
    response_data = {"data": data, "StatusCode": 6000, "message": "success"}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def get_user_table(request):
    CompanyID = request.data["CompanyID"]
    BranchID = request.data["BranchID"]
    userId = request.data["userId"]

    DefaultAccountForUser = False
    Cash_Account = 1
    Bank_Account = 92
    Sales_Account = 85
    Sales_Return_Account = 86
    Purchase_Account = 69
    Purchase_Return_Account = 70
    ExpiryDate = ""
    is_owner = True
    user_type = 1
    Warehouse_name = ""
    WarehouseID = 1
    EmployeeID = 1
    VAT_Type_name = ""
    Sales_GST_Type_name = ""
    Purchase_GST_Type_name = ""
    Sales_Account_name = ""
    Sales_Return_Account_name = ""
    Purchase_Account_name = ""
    Purchase_Return_Account_name = ""
    Cash_Account_name = ""
    Bank_Account_name = ""
    Employee_name = ""

    if UserTable.objects.filter(
        CompanyID__pk=CompanyID, customer__user=userId
    ).exists():
        user_table_instance = UserTable.objects.get(
            CompanyID__pk=CompanyID, customer__user=userId
        )
        DefaultAccountForUser = UserTable.objects.get(
            CompanyID=CompanyID, customer__user__pk=userId
        ).DefaultAccountForUser
        Cash_Account = user_table_instance.Cash_Account
        Bank_Account = user_table_instance.Bank_Account
        Sales_Account = user_table_instance.Sales_Account
        Sales_Return_Account = user_table_instance.Sales_Return_Account
        Purchase_Account = user_table_instance.Purchase_Account
        Purchase_Return_Account = user_table_instance.Purchase_Return_Account
        ExpiryDate = user_table_instance.ExpiryDate
        is_owner = user_table_instance.is_owner
        try:
            user_type = user_table_instance.UserType.ID
        except:
            user_type = 1
        # WarehouseID = user_table_instance.Warehouse
        # EmployeeID = user_table_instance.EmployeeID
        # VAT_Type = user_table_instance.VAT_Type
        # Sales_GST_Type = user_table_instance.Sales_GST_Type
        # Purchase_GST_Type = user_table_instance.Purchase_GST_Type

        Sales_Account_name = get_account_ledger(CompanyID, Sales_Account, BranchID)
        Sales_Return_Account_name = get_account_ledger(
            CompanyID, Sales_Return_Account, BranchID
        )
        Purchase_Account_name = get_account_ledger(
            CompanyID, Purchase_Account, BranchID
        )
        Purchase_Return_Account_name = get_account_ledger(
            CompanyID, Purchase_Return_Account, BranchID
        )
        Cash_Account_name = get_account_ledger(CompanyID, Cash_Account, BranchID)
        Bank_Account_name = get_account_ledger(CompanyID, Bank_Account, BranchID)

    if Warehouse.objects.filter(
        CompanyID=CompanyID, WarehouseID=WarehouseID, BranchID=BranchID
    ).exists():
        Warehouse_name = get_object_or_404(
            Warehouse.objects.filter(
                CompanyID=CompanyID, WarehouseID=WarehouseID, BranchID=BranchID
            )
        ).WarehouseName

    if Employee.objects.filter(
        CompanyID=CompanyID, EmployeeID=EmployeeID, BranchID=BranchID
    ).exists():
        Employee_name = get_object_or_404(
            Employee.objects.filter(
                CompanyID=CompanyID, EmployeeID=EmployeeID, BranchID=BranchID
            )
        ).FirstName

    # if TransactionTypes.objects.filter(CompanyID=CompanyID, TransactionTypesID=VAT_Type, BranchID=BranchID).exists():
    #     VAT_Type_name = get_object_or_404(TransactionTypes.objects.filter(
    #         CompanyID=CompanyID, TransactionTypesID=VAT_Type, BranchID=BranchID)).Name

    # if TransactionTypes.objects.filter(CompanyID=CompanyID, TransactionTypesID=Sales_GST_Type, BranchID=BranchID).exists():
    #     Sales_GST_Type_name = get_object_or_404(TransactionTypes.objects.filter(
    #         CompanyID=CompanyID, TransactionTypesID=Sales_GST_Type, BranchID=BranchID)).Name

    # if TransactionTypes.objects.filter(CompanyID=CompanyID, TransactionTypesID=Purchase_GST_Type, BranchID=BranchID).exists():
    #     Purchase_GST_Type_name = get_object_or_404(TransactionTypes.objects.filter(
    #         CompanyID=CompanyID, TransactionTypesID=Purchase_GST_Type, BranchID=BranchID)).Name

    data = {
        "Cash_Account": Cash_Account,
        "Bank_Account": Bank_Account,
        "Sales_Account": Sales_Account,
        "Sales_Return_Account": Sales_Return_Account,
        "Purchase_Account": Purchase_Account,
        "Purchase_Return_Account": Purchase_Return_Account,
        "ExpiryDate": ExpiryDate,
        "Warehouse_name": Warehouse_name,
        "Employee_name": Employee_name,
        "DefaultAccountForUser": DefaultAccountForUser,
        "is_owner": is_owner,
        "user_type": user_type,
        "Sales_Account_name": Sales_Account_name,
        "Sales_Return_Account_name": Sales_Return_Account_name,
        "Purchase_Account_name": Purchase_Account_name,
        "Purchase_Return_Account_name": Purchase_Return_Account_name,
        "Cash_Account_name": Cash_Account_name,
        "Bank_Account_name": Bank_Account_name,
        "VAT_Type_name": VAT_Type_name,
        "Sales_GST_Type_name": Sales_GST_Type_name,
        "Purchase_GST_Type_name": Purchase_GST_Type_name,
    }
    response_data = {"data": data, "StatusCode": 6000, "message": "success"}
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def get_defaults(request):
    data = request.data
    CompanyID = data["CompanyID"]
    BranchID = data["BranchID"]
    userId = data["userId"]
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
    VATNumber = get_company(CompanyID).VATNumber
    GSTNumber = get_company(CompanyID).GSTNumber
    Phone = get_company(CompanyID).Phone
    usertable_count = UserTable.objects.filter(CompanyID=CompanyID).count()
    if usertable_count > NoOfUsers:
        corrent_user = usertable_count - NoOfUsers
        last_user_table_instance = UserTable.objects.filter(CompanyID=CompanyID)[
            corrent_user:
        ]
        UserTable.objects.exclude(
            CompanyID=CompanyID, pk__in=last_user_table_instance
        ).delete()
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
    DefaultAccountForUser = None
    show_all_warehouse = True
    if UserTable.objects.filter(
        CompanyID=CompanyID, customer__user__pk=userId
    ).exists():
        WarehouseID = UserTable.objects.get(
            CompanyID=CompanyID, customer__user__pk=userId
        ).DefaultWarehouse
        show_all_warehouse = UserTable.objects.get(
            CompanyID=CompanyID, customer__user__pk=userId
        ).show_all_warehouse
    # =============Uvais================
    # ===========VAT======
    vat = False
    gst = False
    if GeneralSettings.objects.filter(
        BranchID=BranchID, CompanyID=CompanyID, SettingsType="VAT"
    ).exists():
        vat = GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="VAT"
        ).SettingsValue
    if GeneralSettings.objects.filter(
        BranchID=BranchID, CompanyID=CompanyID, SettingsType="GST"
    ).exists():
        gst = GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="GST"
        ).SettingsValue
    comapny_instance = get_company(CompanyID)
    if vat == "true" or vat == "True" or vat == True:
        vat = True
    else:
        vat = False
    if gst == "true" or gst == "True" or gst == True:
        gst = True
    else:
        gst = False
    comapny_instance.is_gst = gst
    comapny_instance.is_vat = vat
    comapny_instance.save()

    if not MasterType.objects.filter(
        CompanyID__pk=CompanyID, BranchID=BranchID, Name="Loyalty Card Type"
    ).exists():
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
    if not MasterType.objects.filter(
        CompanyID__pk=CompanyID, BranchID=BranchID, Name="Loyalty Card Status"
    ).exists():
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

    if UserTable.objects.filter(
        CompanyID__pk=CompanyID, customer__user=userId
    ).exists():
        user_table_instance = UserTable.objects.get(
            CompanyID__pk=CompanyID, customer__user=userId
        )
        DefaultAccountForUser = UserTable.objects.get(
            CompanyID=CompanyID, customer__user__pk=userId
        ).DefaultAccountForUser
        Cash_Account = user_table_instance.Cash_Account
        Bank_Account = user_table_instance.Bank_Account
        Sales_Account = user_table_instance.Sales_Account
        Sales_Return_Account = user_table_instance.Sales_Return_Account
        Purchase_Account = user_table_instance.Purchase_Account
        Purchase_Return_Account = user_table_instance.Purchase_Return_Account
        ExpiryDate = user_table_instance.ExpiryDate
        is_owner = user_table_instance.is_owner
        user_type = user_table_instance.UserType.ID

        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=Sales_Account
        ).exists():
            Sales_Account_name = get_object_or_404(
                AccountLedger.objects.filter(
                    CompanyID=CompanyID, LedgerID=Sales_Account
                )
            ).LedgerName

        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=Sales_Return_Account
        ).exists():
            Sales_Return_Account_name = get_object_or_404(
                AccountLedger.objects.filter(
                    CompanyID=CompanyID, LedgerID=Sales_Return_Account
                )
            ).LedgerName

        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=Purchase_Account
        ).exists():
            Purchase_Account_name = get_object_or_404(
                AccountLedger.objects.filter(
                    CompanyID=CompanyID, LedgerID=Purchase_Account
                )
            ).LedgerName

        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=Purchase_Return_Account
        ).exists():
            Purchase_Return_Account_name = get_object_or_404(
                AccountLedger.objects.filter(
                    CompanyID=CompanyID, LedgerID=Purchase_Return_Account
                )
            ).LedgerName

        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=Cash_Account
        ).exists():
            Cash_Account_name = get_object_or_404(
                AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Cash_Account)
            ).LedgerName

        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=Bank_Account
        ).exists():
            Bank_Account_name = get_object_or_404(
                AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=Bank_Account)
            ).LedgerName

        if Warehouse.objects.filter(
            CompanyID=CompanyID, WarehouseID=WarehouseID, BranchID=BranchID
        ).exists():
            Warehouse_name = get_object_or_404(
                Warehouse.objects.filter(
                    CompanyID=CompanyID, WarehouseID=WarehouseID, BranchID=BranchID
                )
            ).WarehouseName

    Country = ""
    CountryName = ""
    State = ""
    StateName = ""
    State_Code = ""
    CompanyLogo = ""
    Address1 = ""
    Address2 = ""
    Address3 = ""
    City = ""
    BussinesType = ""
    if CompanySettings.objects.filter(id=CompanyID).exists():
        com_ins = CompanySettings.objects.get(id=CompanyID)
        BussinesType = com_ins.business_type.Name
        Country = CompanySettings.objects.get(id=CompanyID).Country.id
        CountryName = CompanySettings.objects.get(id=CompanyID).Country.Country_Name
        CurrencySymbol = CompanySettings.objects.get(id=CompanyID).Country.Symbol
        State = CompanySettings.objects.get(id=CompanyID).State.id
        StateName = CompanySettings.objects.get(id=CompanyID).State.Name
        State_Code = CompanySettings.objects.get(id=CompanyID).State.State_Code
        if CompanySettings.objects.get(id=CompanyID).CompanyLogo:
            CompanyLogo = CompanySettings.objects.get(id=CompanyID).CompanyLogo.url
        if CompanySettings.objects.get(id=CompanyID).City:
            City = CompanySettings.objects.get(id=CompanyID).City

        if CompanySettings.objects.get(id=CompanyID).Address1:
            Address1 = CompanySettings.objects.get(id=CompanyID).Address1
        if CompanySettings.objects.get(id=CompanyID).Address2:
            Address2 = CompanySettings.objects.get(id=CompanyID).Address2
        if CompanySettings.objects.get(id=CompanyID).Address3:
            Address3 = CompanySettings.objects.get(id=CompanyID).Address3

    if FinancialYear.objects.filter(CompanyID=CompanyID, IsClosed=False).exists():
        financialyear = FinancialYear.objects.filter(
            CompanyID=CompanyID, IsClosed=False
        ).first()
        financial_FromDate = financialyear.FromDate
        financial_ToDate = financialyear.ToDate
    else:
        try:
            financialyear = FinancialYear.objects.filter(CompanyID=CompanyID).first()
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

    if administrations_models.GeneralSettings.objects.filter(
        CompanyID=CompanyID, BranchID=BranchID
    ).exists():

        QtyDecimalPoint = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="QtyDecimalPoint"
        ).SettingsValue
        # loyalty_PointValue = administrations_models.GeneralSettings.objects.get(
        #     BranchID=BranchID, CompanyID=CompanyID, SettingsType="loyalty_PointValue"
        # ).SettingsValue
        PriceDecimalPoint = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="PriceDecimalPoint"
        ).SettingsValue
        Show_Sales_Type = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Show_Sales_Type"
        ).SettingsValue
        Show_Purchase_Type = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Show_Purchase_Type"
        ).SettingsValue
        Sales_VAT_Type = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Sales_VAT_Type"
        ).SettingsValue
        Purchase_VAT_Type = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Purchase_VAT_Type"
        ).SettingsValue
        Sales_GST_Type = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Sales_GST_Type"
        ).SettingsValue
        Purchase_GST_Type = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="Purchase_GST_Type"
        ).SettingsValue

        RoundingFigure = administrations_models.GeneralSettings.objects.get(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="RoundingFigure"
        ).SettingsValue
        RoundOffPurchase = 5
        if administrations_models.GeneralSettings.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, SettingsType="RoundOffPurchase"
        ).exists():
            RoundOffPurchase = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="RoundOffPurchase"
            ).SettingsValue

        RoundOffSales = 5
        if administrations_models.GeneralSettings.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, SettingsType="RoundOffSales"
        ).exists():
            RoundOffSales = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="RoundOffSales"
            ).SettingsValue

        Sales_VAT_Type = int(Sales_VAT_Type)
        Purchase_VAT_Type = int(Purchase_VAT_Type)
        Sales_GST_Type = int(Sales_GST_Type)
        Purchase_GST_Type = int(Purchase_GST_Type)

        PreDateTransaction = 30
        PostDateTransaction = 30
        EnableVoucherNoUserWise = True
        ShowSettingsinSales = False
        EnableProductBatchWise = False
        EnableDuplicateProductName = False
        EnableWarehouse = False
        EnableCreditPeriod = False
        show_productcode_InsearchSale = False
        show_productcode_InsearchPurchase = False
        show_stock_InsearchSale = False
        show_stock_InsearchPurchase = False
        show_purchasePrice_InsearchSale = False
        show_salesPrice_InsearchPurchase = False
        ShowYearMonthCalanderInWorkOrder = False
        BatchCriteria = ""
        loyalty_PointValue = ""

        if administrations_models.GeneralSettings.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="loyalty_point_value"
        ).exists():
            loyalty_PointValue = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID,
                CompanyID=CompanyID,
                SettingsType="loyalty_point_value",
            ).SettingsValue

        if administrations_models.GeneralSettings.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="PreDateTransaction"
        ).exists():
            PreDateTransaction = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID,
                CompanyID=CompanyID,
                SettingsType="PreDateTransaction",
            ).SettingsValue
        if administrations_models.GeneralSettings.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="PostDateTransaction"
        ).exists():
            PostDateTransaction = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID,
                CompanyID=CompanyID,
                SettingsType="PostDateTransaction",
            ).SettingsValue

        if administrations_models.GeneralSettings.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID, SettingsType="BatchCriteria"
        ).exists():
            BatchCriteria = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="BatchCriteria"
            ).SettingsValue

        # CompanyID, SettingsType
        EnableLoyaltySettings = get_general_settings(
            BranchID, CompanyID, "EnableLoyaltySettings"
        )
        CustomerBasedPrint = get_general_settings(
            BranchID, CompanyID, "CustomerBasedPrint"
        )
        Loyalty_Point_Expire = get_general_settings(
            BranchID, CompanyID, "Loyalty_Point_Expire"
        )
        is_Loyalty_SalesReturn_MinimumSalePrice = get_general_settings(
            BranchID, CompanyID, "is_Loyalty_SalesReturn_MinimumSalePrice"
        )
        MultiUnit = get_general_settings(BranchID, CompanyID, "MultiUnit")
        AllowNegativeStockSales = get_general_settings(
            BranchID, CompanyID, "AllowNegativeStockSales"
        )
        AllowNegativeStockInStockTransfer = get_general_settings(
            BranchID, CompanyID, "AllowNegativeStockInStockTransfer"
        )
        PriceCategory = get_general_settings(BranchID, CompanyID, "PriceCategory")
        BlockSalesPrice = get_general_settings(
            BranchID, CompanyID, "BlockSalesPrice")
        BlockSalesBelowPurchase = get_general_settings(
            BranchID, CompanyID, "BlockSalesBelowPurchase")
        ShowProfitinSalesRegisterReport = get_general_settings(
            BranchID, CompanyID, "ShowProfitinSalesRegisterReport"
        )

        ShowCustomerLastSalesPriceinSales = get_general_settings(
            BranchID, CompanyID, "ShowCustomerLastSalesPriceinSales"
        )
        ShowSupplierLastPurchasePriceinPurchase = get_general_settings(
            BranchID, CompanyID, "ShowSupplierLastPurchasePriceinPurchase"
        )

        VoucherNoAutoGenerate = get_general_settings(
            BranchID, CompanyID, "VoucherNoAutoGenerate"
        )
        EnableVoucherNoUserWise = get_general_settings(
            BranchID, CompanyID, "EnableVoucherNoUserWise"
        )
        ShowSalesPriceInPurchase = get_general_settings(
            BranchID, CompanyID, "ShowSalesPriceInPurchase"
        )
        ShowMaximumStockAlert = get_general_settings(
            BranchID, CompanyID, "ShowMaximumStockAlert"
        )
        ShowSettingsinSales = get_general_settings(
            BranchID, CompanyID, "ShowSettingsinSales"
        )
        ShowSettingsinPurchase = get_general_settings(
            BranchID, CompanyID, "ShowSettingsinPurchase"
        )
        EnableProductBatchWise = get_general_settings(
            BranchID, CompanyID, "EnableProductBatchWise"
        )
        EnableDuplicateProductName = get_general_settings(
            BranchID, CompanyID, "EnableDuplicateProductName"
        )
        EnableWarehouse = get_general_settings(
            BranchID, CompanyID, "EnableWarehouse")
        EnableCreditPeriod = get_general_settings(
            BranchID, CompanyID, "EnableCreditPeriod")
        show_productcode_InsearchSale = get_general_settings(
            BranchID, CompanyID, "show_productcode_InsearchSale"
        )
        show_productcode_InsearchPurchase = get_general_settings(
            BranchID, CompanyID, "show_productcode_InsearchPurchase"
        )
        show_stock_InsearchSale = get_general_settings(
            BranchID, CompanyID, "show_stock_InsearchSale"
        )
        show_stock_InsearchPurchase = get_general_settings(
            BranchID, CompanyID, "show_stock_InsearchPurchase"
        )
        show_purchasePrice_InsearchSale = get_general_settings(
            BranchID, CompanyID, "show_purchasePrice_InsearchSale"
        )
        show_salesPrice_InsearchPurchase = get_general_settings(
            BranchID, CompanyID, "show_salesPrice_InsearchPurchase"
        )
        AllowUpdateBatchPriceInSales = get_general_settings(
            BranchID, CompanyID, "AllowUpdateBatchPriceInSales"
        )
        SalesPriceUpdate = get_general_settings(BranchID, CompanyID, "SalesPriceUpdate")
        PurchasePriceUpdate = get_general_settings(
            BranchID, CompanyID, "PurchasePriceUpdate"
        )
        EnableTransilationInProduct = get_general_settings(
            BranchID, CompanyID, "EnableTransilationInProduct"
        )
        ShowPositiveStockInSales = get_general_settings(
            BranchID, CompanyID, "ShowPositiveStockInSales"
        )
        ShowNegativeBatchInSales = get_general_settings(
            BranchID, CompanyID, "ShowNegativeBatchInSales"
        )
        CreateBatchForWorkOrder = get_general_settings(
            BranchID, CompanyID, "CreateBatchForWorkOrder"
        )
        ShowAllProductsInWorkOrder = get_general_settings(
            BranchID, CompanyID, "ShowAllProductsInWorkOrder"
        )
        KFC = get_general_settings(BranchID, CompanyID, "KFC")
        blockSaleByBillDisct = get_general_settings(
            BranchID, CompanyID, "blockSaleByBillDisct"
        )
        AllowCashReceiptMoreSaleAmt = get_general_settings(
            BranchID, CompanyID, "AllowCashReceiptMoreSaleAmt"
        )
        AllowCashReceiptMorePurchaseAmt = get_general_settings(
            BranchID, CompanyID, "AllowCashReceiptMorePurchaseAmt"
        )
        AllowAdvanceReceiptinSales = get_general_settings(
            BranchID, CompanyID, "AllowAdvanceReceiptinSales"
        )
        AllowAdvanceReceiptinPurchase = get_general_settings(
            BranchID, CompanyID, "AllowAdvanceReceiptinPurchase"
        )
        AllowQtyDividerinSales = get_general_settings(
            BranchID, CompanyID, "AllowQtyDividerinSales"
        )
        InclusiveRatePurchase = get_general_settings(
            BranchID, CompanyID, "InclusiveRatePurchase"
        )
        InclusiveRateSales = get_general_settings(
            BranchID, CompanyID, "InclusiveRateSales"
        )
        InclusiveRateWorkOrder = get_general_settings(
            BranchID, CompanyID, "InclusiveRateWorkOrder"
        )
        ShowDiscountInSales = get_general_settings(
            BranchID, CompanyID, "ShowDiscountInSales"
        )
        ShowSupplierInSales = get_general_settings(
            BranchID, CompanyID, "ShowSupplierInSales"
        )
        EnableShippingCharge = get_general_settings(
            BranchID, CompanyID, "EnableShippingCharge"
        )
        AutoIncrimentQty = get_general_settings(BranchID, CompanyID, "AutoIncrimentQty")
        ShowDueBalanceInSales = get_general_settings(
            BranchID, CompanyID, "ShowDueBalanceInSales"
        )
        ShowDueBalanceInPurchase = get_general_settings(
            BranchID, CompanyID, "ShowDueBalanceInPurchase"
        )
        ShowEmployeesInSales = get_general_settings(
            BranchID, CompanyID, "ShowEmployeesInSales"
        )
        EnableSerialNoInSales = get_general_settings(
            BranchID, CompanyID, "EnableSerialNoInSales"
        )
        EnableItemCodeNoInSales = get_general_settings(
            BranchID, CompanyID, "EnableItemCodeNoInSales"
        )
        EnableCreditLimit = get_general_settings(
            BranchID, CompanyID, "EnableCreditLimit"
        )
        EnableFaeraSettings = get_general_settings(
            BranchID, CompanyID, "EnableFaeraSettings"
        )
        EnableSalesManInSales = get_general_settings(
            BranchID, CompanyID, "EnableSalesManInSales"
        )
        ShowWarrantyPeriodInProduct = get_general_settings(
            BranchID, CompanyID, "ShowWarrantyPeriodInProduct"
        )
        ShowDescriptionInSales = get_general_settings(
            BranchID, CompanyID, "ShowDescriptionInSales"
        )
        AllowExtraSerielNos = get_general_settings(
            BranchID, CompanyID, "AllowExtraSerielNos"
        )
        Free_Quantity_In_Sales = get_general_settings(
            BranchID, CompanyID, "Free_Quantity_In_Sales"
        )
        Free_Quantity_In_Purchase = get_general_settings(
            BranchID, CompanyID, "Free_Quantity_In_Purchase"
        )
        ShowCustomerInPurchase = get_general_settings(
            BranchID, CompanyID, "ShowCustomerInPurchase"
        )
        ShowManDateAndExpDatePurchase = get_general_settings(
            BranchID, CompanyID, "ShowManDateAndExpDatePurchase"
        )
        ShowDiscountInPurchase = get_general_settings(
            BranchID, CompanyID, "ShowDiscountInPurchase"
        )
        ShowDiscountInPayments = get_general_settings(
            BranchID, CompanyID, "ShowDiscountInPayments"
        )
        ShowDiscountInReceipts = get_general_settings(
            BranchID, CompanyID, "ShowDiscountInReceipts"
        )
        EnableBillwise = get_general_settings(BranchID, CompanyID, "EnableBillwise")
        EnableCardNetWork = get_general_settings(
            BranchID, CompanyID, "EnableCardNetWork"
        )
        BlockTransactionsByDate = get_general_settings(
            BranchID, CompanyID, "BlockTransactionsByDate"
        )
        EnableCardDetails = get_general_settings(
            BranchID, CompanyID, "EnableCardDetails"
        )

        Show_Sales_Type = get_general_settings(BranchID, CompanyID, "Show_Sales_Type")
        Show_Purchase_Type = get_general_settings(
            BranchID, CompanyID, "Show_Purchase_Type"
        )
        TAX1 = get_general_settings(BranchID, CompanyID, "TAX1")
        TAX2 = get_general_settings(BranchID, CompanyID, "TAX2")
        TAX3 = get_general_settings(BranchID, CompanyID, "TAX3")
        Additional_Discount = get_general_settings(
            BranchID, CompanyID, "Additional_Discount"
        )
        Bill_Discount = get_general_settings(BranchID, CompanyID, "Bill_Discount")
        Negatine_Stock = get_general_settings(BranchID, CompanyID, "Negatine_Stock")
        Increment_Qty_In_POS = get_general_settings(
            BranchID, CompanyID, "Increment_Qty_In_POS"
        )
        Kitchen_Print = get_general_settings(BranchID, CompanyID, "Kitchen_Print")
        Order_Print = get_general_settings(BranchID, CompanyID, "Order_Print")
        Print_After_Save_Active = get_general_settings(
            BranchID, CompanyID, "Print_After_Save_Active"
        )
        VAT = get_general_settings(BranchID, CompanyID, "VAT")
        GST = get_general_settings(BranchID, CompanyID, "GST")

        if TransactionTypes.objects.filter(
            CompanyID=CompanyID, TransactionTypesID=Sales_VAT_Type, BranchID=BranchID
        ).exists():
            Sales_VAT_Type_name = get_object_or_404(
                TransactionTypes.objects.filter(
                    CompanyID=CompanyID,
                    TransactionTypesID=Sales_VAT_Type,
                    BranchID=BranchID,
                )
            ).Name

        if TransactionTypes.objects.filter(
            CompanyID=CompanyID, TransactionTypesID=Purchase_VAT_Type, BranchID=BranchID
        ).exists():
            Purchase_VAT_Type_name = get_object_or_404(
                TransactionTypes.objects.filter(
                    CompanyID=CompanyID,
                    TransactionTypesID=Purchase_VAT_Type,
                    BranchID=BranchID,
                )
            ).Name

        if TransactionTypes.objects.filter(
            CompanyID=CompanyID, TransactionTypesID=Sales_GST_Type, BranchID=BranchID
        ).exists():
            Sales_GST_Type_name = get_object_or_404(
                TransactionTypes.objects.filter(
                    CompanyID=CompanyID,
                    TransactionTypesID=Sales_GST_Type,
                    BranchID=BranchID,
                )
            ).Name

        if TransactionTypes.objects.filter(
            CompanyID=CompanyID, TransactionTypesID=Purchase_GST_Type, BranchID=BranchID
        ).exists():
            Purchase_GST_Type_name = get_object_or_404(
                TransactionTypes.objects.filter(
                    CompanyID=CompanyID,
                    TransactionTypesID=Purchase_GST_Type,
                    BranchID=BranchID,
                )
            ).Name

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
        if administrations_models.PrintSettings.objects.filter(
            CompanyID=CompanyID
        ).exists():
            template = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).template
            IsDefaultThermalPrinter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).IsDefaultThermalPrinter
            PageSize = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).PageSize
            IsCompanyLogo = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).IsCompanyLogo
            IsCompanyName = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).IsCompanyName
            IsDescription = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).IsDescription
            IsAddress = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).IsAddress
            IsMobile = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).IsMobile
            IsEmail = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).IsEmail
            IsTaxNo = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).IsTaxNo
            IsCRNo = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).IsCRNo
            IsCurrentBalance = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).IsCurrentBalance
            SalesInvoiceTrName = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).SalesInvoiceTrName
            SalesOrderTrName = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).SalesOrderTrName
            SalesReturnTrName = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).SalesReturnTrName
            PurchaseInvoiceTrName = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).PurchaseInvoiceTrName
            PurchaseOrderTrName = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).PurchaseOrderTrName
            PurchaseReturnTrName = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).PurchaseReturnTrName
            CashRecieptTrName = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).CashRecieptTrName
            BankRecieptTrName = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).BankRecieptTrName
            CashPaymentTrName = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).CashPaymentTrName
            BankPaymentTrName = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).BankPaymentTrName
            IsInclusiveTaxUnitPrice = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).IsInclusiveTaxUnitPrice
            IsInclusiveTaxNetAmount = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).IsInclusiveTaxNetAmount
            IsFlavour = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).IsFlavour
            IsShowDescription = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).IsShowDescription
            IsTotalQuantity = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).IsTotalQuantity
            IsTaxDetails = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).IsTaxDetails
            IsHSNCode = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).IsHSNCode
            IsProductCode = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).IsProductCode

            IsReceivedAmount = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).IsReceivedAmount
            # print Bank details ====START
            IsBankDetails = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).IsBankDetails
            BankNameFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).BankNameFooter
            AccountNumberFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).AccountNumberFooter
            BranchIFCFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).BranchIFCFooter
            # print Bank details ====END

            SalesInvoiceFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).SalesInvoiceFooter
            SalesReturnFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).SalesReturnFooter
            SalesOrderFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).SalesOrderFooter
            PurchaseInvoiceFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).PurchaseInvoiceFooter
            PurchaseOrderFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).PurchaseOrderFooter
            PurchaseReturnFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).PurchaseReturnFooter
            CashRecieptFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).CashRecieptFooter
            BankRecieptFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).BankRecieptFooter
            CashPaymentFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).CashPaymentFooter
            BankPaymentFooter = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).BankPaymentFooter
            TermsAndConditionsSales = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).TermsAndConditionsSales
            TermsAndConditionsPurchase = (
                administrations_models.PrintSettings.objects.get(
                    CompanyID=CompanyID
                ).TermsAndConditionsPurchase
            )
            TermsAndConditionsSaleEstimate = (
                administrations_models.PrintSettings.objects.get(
                    CompanyID=CompanyID
                ).TermsAndConditionsSaleEstimate
            )

            HeadFontSize = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).HeadFontSize
            BodyFontSize = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).BodyFontSize
            ContentFontSize = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).ContentFontSize
            FooterFontSize = administrations_models.PrintSettings.objects.get(
                CompanyID=CompanyID
            ).FooterFontSize

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
        today = newDatetime.strptime(today, "%Y-%m-%d")
        remaining_days = company_expire_date - today.date()
        if administrations_models.GeneralSettings.objects.filter(
            CompanyID=CompanyID, SettingsType="Bill_Discount"
        ).exists():
            Bill_Discount = administrations_models.GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="Bill_Discount"
            ).SettingsValue
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
            "AllowNegativeStockInStockTransfer": AllowNegativeStockInStockTransfer,
            "PriceCategory": PriceCategory,
            "BlockSalesPrice": BlockSalesPrice,
            "BlockSalesBelowPurchase": BlockSalesBelowPurchase,
            "ShowProfitinSalesRegisterReport": ShowProfitinSalesRegisterReport,
            "ShowCustomerLastSalesPriceinSales": ShowCustomerLastSalesPriceinSales,
            "ShowSupplierLastPurchasePriceinPurchase": ShowSupplierLastPurchasePriceinPurchase,
            "VoucherNoAutoGenerate": VoucherNoAutoGenerate,
            "EnableVoucherNoUserWise": EnableVoucherNoUserWise,
            "ShowSalesPriceInPurchase": ShowSalesPriceInPurchase,
            "ShowMaximumStockAlert": ShowMaximumStockAlert,
            "ShowSettingsinSales": ShowSettingsinSales,
            "ShowSettingsinPurchase": ShowSettingsinPurchase,
            "EnableProductBatchWise": EnableProductBatchWise,
            "EnableDuplicateProductName": EnableDuplicateProductName,
            "EnableWarehouse": EnableWarehouse,
            "EnableCreditPeriod": EnableCreditPeriod,
            "show_productcode_InsearchSale": show_productcode_InsearchSale,
            "show_productcode_InsearchPurchase": show_productcode_InsearchPurchase,
            "show_stock_InsearchSale": show_stock_InsearchSale,
            "show_stock_InsearchPurchase": show_stock_InsearchPurchase,
            "show_purchasePrice_InsearchSale": show_purchasePrice_InsearchSale,
            "show_salesPrice_InsearchPurchase": show_salesPrice_InsearchPurchase,
            "AllowUpdateBatchPriceInSales": AllowUpdateBatchPriceInSales,
            "SalesPriceUpdate": SalesPriceUpdate,
            "PurchasePriceUpdate": PurchasePriceUpdate,
            "EnableTransilationInProduct": EnableTransilationInProduct,
            "ShowPositiveStockInSales": ShowPositiveStockInSales,
            "ShowNegativeBatchInSales": ShowNegativeBatchInSales,
            "CreateBatchForWorkOrder": CreateBatchForWorkOrder,
            "ShowAllProductsInWorkOrder": ShowAllProductsInWorkOrder,
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
            "AutoIncrimentQty": AutoIncrimentQty,
            "ShowDueBalanceInSales": ShowDueBalanceInSales,
            "ShowDueBalanceInPurchase": ShowDueBalanceInPurchase,
            "ShowEmployeesInSales": ShowEmployeesInSales,
            "EnableSerialNoInSales": EnableSerialNoInSales,
            "EnableItemCodeNoInSales": EnableItemCodeNoInSales,
            "EnableCreditLimit": EnableCreditLimit,
            "EnableFaeraSettings": EnableFaeraSettings,
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
            "EnableBillwise": EnableBillwise,
            "EnableCardNetWork": EnableCardNetWork,
            "BlockTransactionsByDate": BlockTransactionsByDate,
            "EnableCardDetails": EnableCardDetails,
            "PreDateTransaction": str(PreDateTransaction),
            "PostDateTransaction": str(PostDateTransaction),
            "VAT": VAT,
            "GST": GST,
            "TAX1": TAX1,
            "TAX2": TAX2,
            "TAX3": TAX3,
            "loyalty_PointValue": loyalty_PointValue,
            "Additional_Discount": Additional_Discount,
            "Bill_Discount": Bill_Discount,
            "Negatine_Stock": Negatine_Stock,
            "Increment_Qty_In_POS": Increment_Qty_In_POS,
            "Kitchen_Print": Kitchen_Print,
            "Order_Print": Order_Print,
            "Print_After_Save_Active": Print_After_Save_Active,
            "QtyDecimalPoint": QtyDecimalPoint,
            "PriceDecimalPoint": PriceDecimalPoint,
            "RoundingFigure": RoundingFigure,
            "RoundOffPurchase": RoundOffPurchase,
            "RoundOffSales": RoundOffSales,
            "Business_Type": BussinesType,
            "today": today,
            "ExpiryDate": get_company(CompanyID).ExpiryDate,
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
                "success": success,
                "StatusCode": success,
                "message": message,
                "error": None,
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
                "user_type": user_type,
                "VATNumber": VATNumber,
                "GSTNumber": GSTNumber,
                "Phone": Phone,
                "show_all_warehouse": show_all_warehouse,
            },
            status=status.HTTP_200_OK,
        )

    else:
        response_data = {"StatusCode": 6001, "message": "Not Found"}

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def activity_logs(request):
    customer = request.data["customer"]
    organization = request.data["organization"]
    log_type = request.data["log_type"]
    is_solved = request.data["is_solved"]

    try:
        page_number = request.data["page_no"]
    except:
        page_number = ""

    try:
        items_per_page = request.data["items_per_page"]
    except:
        items_per_page = ""

    if administrations_models.Activity_Log.objects.exists():
        if customer and organization and is_solved and log_type:
            instances = administrations_models.Activity_Log.objects.filter(
                user__pk=customer,
                company__pk=organization,
                is_solved=is_solved,
                log_type=log_type,
            )
        elif customer and organization and is_solved == False and log_type:
            instances = administrations_models.Activity_Log.objects.filter(
                user__pk=customer,
                company__pk=organization,
                is_solved=is_solved,
                log_type=log_type,
            )
        elif customer and organization and log_type:
            instances = administrations_models.Activity_Log.objects.filter(
                user__pk=customer,
                company__pk=organization,
                is_solved=is_solved,
                log_type=log_type,
            )
        elif customer and organization and is_solved:
            instances = administrations_models.Activity_Log.objects.filter(
                user__pk=customer, company__pk=organization, is_solved=is_solved
            )
        elif customer and organization and is_solved == False:
            instances = administrations_models.Activity_Log.objects.filter(
                user__pk=customer, company__pk=organization, is_solved=is_solved
            )
        elif customer and organization and is_solved:
            instances = administrations_models.Activity_Log.objects.filter(
                user__pk=customer, company__pk=organization
            )
        elif customer and organization and is_solved == False:
            instances = administrations_models.Activity_Log.objects.filter(
                user__pk=customer, company__pk=organization
            )
        elif customer and is_solved:
            instances = administrations_models.Activity_Log.objects.filter(
                user__pk=customer, is_solved=True
            )
        elif customer and is_solved == False:
            instances = administrations_models.Activity_Log.objects.filter(
                user__pk=customer, is_solved=False
            )
        elif organization and is_solved:
            instances = administrations_models.Activity_Log.objects.filter(
                company__pk=organization
            )
        elif organization and is_solved == False:
            instances = administrations_models.Activity_Log.objects.filter(
                company__pk=organization, is_solved=False
            )
        elif is_solved:
            instances = administrations_models.Activity_Log.objects.filter(
                is_solved=is_solved
            )
        elif is_solved == False:
            instances = administrations_models.Activity_Log.objects.filter(
                is_solved=is_solved
            )
        elif log_type and is_solved:
            instances = administrations_models.Activity_Log.objects.filter(
                log_type=log_type, is_solved=False
            )
        elif log_type and is_solved == False:
            instances = administrations_models.Activity_Log.objects.filter(
                log_type=log_type, is_solved=False
            )
        else:
            instances = administrations_models.Activity_Log.objects.all()

        if page_number and items_per_page:
            count = len(instances)
            instances = list_pagination(instances, items_per_page, page_number)
        else:
            count = len(instances)
        serializer = ActivityLogSerializer(instances, many=True)
        response_data = {"StatusCode": 6000, "data": serializer.data, "count": count}
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {"StatusCode": 6001, "message": "No activity found"}
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def activity_log_solve(request):
    id = request.data["id"]
    is_solved = request.data["is_solved"]
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


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def activity_log(request, pk):
    if administrations_models.Activity_Log.objects.filter(pk=pk).exists():
        instance = administrations_models.Activity_Log.objects.get(pk=pk)
        serializer = ActivityLogSerializer(instance)
        response_data = {"StatusCode": 6000, "data": serializer.data}
    else:
        response_data = {"StatusCode": 6001, "message": "Activity not found."}

    return Response(response_data, status=status.HTTP_200_OK)


@receiver(reset_password_token_created)
def password_reset_token_created(
    sender, instance, reset_password_token, *args, **kwargs
):
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
        "current_user": reset_password_token.user,
        "username": reset_password_token.user.username,
        "email": reset_password_token.user.email,
        'reset_password_url': "http://localhost:3000/password-confirm",
        # 'reset_password_url': "https://www.viknbooks.vikncodes.com/password-confirm",
        # "reset_password_url": "https://www.viknbooks.com/password-confirm",
        # 'reset_password_url': "https://www.vikncodes.in/password-confirm",
        "token": reset_password_token.key,
    }

    # render email text
    # email_html_message = render_to_string('email/user_reset_password.html', context)
    email_html_message = render_to_string("email/email.html", context)
    email_plaintext_message = render_to_string("email/user_reset_password.txt", context)

    msg = EmailMultiAlternatives(
        # title:
        "Password Reset for {title}".format(title="viknbooks.com"),
        # message:
        email_plaintext_message,
        # from:
        "noreply@somehost.local",
        # to:
        [reset_password_token.user.email],
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_software_version(request):
    data = request.data
    CreatedUserID = data["CreatedUserID"]
    CurrentVersion = data["CurrentVersion"]
    MinimumVersion = data["MinimumVersion"]
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


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def software_versions(request):
    data = request.data
    today = datetime.datetime.now()
    CreatedUserID = data["CreatedUserID"]
    if SoftwareVersion.objects.exists():
        instances = SoftwareVersion.objects.get()
        serialized = SoftwareVersionSerializer(instances)
        # request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Brand', 'View', 'Brand list', 'The user viewed brands')

        response_data = {"StatusCode": 6000, "data": serialized.data}
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
        response_data = {"StatusCode": 6000, "data": serialized.data}

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def software_version(request):
    data = request.data
    today = datetime.datetime.now()
    if SoftwareVersion.objects.exists():
        instances = SoftwareVersion.objects.get()
        serialized = SoftwareVersionSerializer(instances)
        # request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Brand', 'View', 'Brand list', 'The user viewed brands')

        response_data = {"StatusCode": 6000, "data": serialized.data}
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {"StatusCode": 6001, "message": "Software version not found"}
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def user_list(request):
    if User.objects.filter().exists():
        instances = User.objects.all()
        serialized = UserListSerializer(
            instances,
            many=True,
        )

        response_data = {"StatusCode": 6000, "data": serialized.data}

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {"StatusCode": 6001, "message": "No users"}

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def user_list_filter(request):
    data = request.data
    EditionName = data["EditionName"]
    is_trialVersion = False
    if EditionName == "Trial Versions":
        is_trialVersion = True
    user_ids = []
    if (
        is_trialVersion == True
        and CompanySettings.objects.filter(IsTrialVersion=True).exists()
    ):
        comapny_instances = CompanySettings.objects.filter(IsTrialVersion=True)
        user_ids = comapny_instances.values_list("owner", flat=True)
    else:
        if CompanySettings.objects.filter(Edition=EditionName).exists():
            comapny_instances = CompanySettings.objects.filter(Edition=EditionName)
            user_ids = comapny_instances.values_list("owner", flat=True)
    if User.objects.filter(id__in=user_ids).exists():
        instances = User.objects.filter(id__in=user_ids)
        serialized = UserListSerializer(
            instances,
            many=True,
        )

        response_data = {"StatusCode": 6000, "data": serialized.data}

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {"StatusCode": 6001, "message": "No users"}

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def get_last_user_token(request):
    data = request.data
    user_id = data["user_id"]
    try:
        is_mobile = data["is_mobile"]
    except:
        is_mobile = False

    LastToken = ""
    VersionNo = ""
    Message = ""
    is_updation = False
    if Customer.objects.filter(user__id=user_id).exists():
        instance = Customer.objects.filter(user__id=user_id).first()
        if is_mobile == True:
            LastToken = instance.LastLoginTokenMobile
            if VersionDetails.objects.filter(is_mobile=True).exists():
                version_detail = VersionDetails.objects.filter(is_mobile=True).first()
                VersionNo = version_detail.Version
                Message = version_detail.Message
                is_updation = version_detail.is_updation
        else:
            LastToken = instance.LastLoginToken
            if VersionDetails.objects.filter(is_web=True).exists():
                version_detail = VersionDetails.objects.filter(is_web=True).first()
                VersionNo = version_detail.Version
                Message = version_detail.Message
                is_updation = version_detail.is_updation

    response_data = {
        "StatusCode": 6000,
        "LastToken": LastToken,
        "VersionNo": VersionNo,
        "Message": Message,
        "is_updation": is_updation,
    }

    return Response(response_data, status=status.HTTP_200_OK)


def reset_password(user, request, is_mobile):
    if is_mobile:
        context = {
            "current_user": user,
            "username": user.username,
            "email": user.email,
            'reset_password_url': "http://localhost:3000/password-confirm",
            # 'reset_password_url': "https://www.viknbooks.vikncodes.com/password-confirm",
            # "reset_password_url": "https://www.viknbooks.com/password-confirm",
            # 'reset_password_url': "https://www.vikncodes.in/password-confirm",
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": default_token_generator.make_token(user),
            "is_mobile": is_mobile
        }
        email_html_message = render_to_string("email/email.html", context)
        email_plaintext_message = render_to_string(
            "email/user_reset_password.txt", context
        )

        msg = EmailMultiAlternatives(
            # title:
            "Password Reset for {title}".format(title="viknbooks.com"),
            # message:
            email_plaintext_message,
            # from:
            "noreply@somehost.local",
            # to:
            [user.email],
        )
        msg.attach_alternative(email_html_message, "text/html")
        msg.send()

    else:
        c = {
            "email": user.email,
            "domain": request.META["HTTP_ORIGIN"],
            "site_name": "your site",
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "user": user,
            "token": default_token_generator.make_token(user),
        }
        # copied from
        # django/contrib/admin/templates/registration/password_reset_subject.txt
        # to templates directory
        email_template_name = "email/password_reset_conform.html"
        # copied from
        # django/contrib/admin/templates/registration/password_reset_email.html
        # to templates directory
        # subject = loader.render_to_string("viknbooks password reset", c)
        # Email subject *must not* contain newlines
        # subject = ''.join(subject.splitlines())
        email = loader.render_to_string(email_template_name, c)
        send_mail(
            "viknbooks password reset",
            email,
            DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )


@api_view(["POST"])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def forgot_password(request):
    serialized = UsernameEmailSerializer(data=request.data)
    message = "Invalid Input"
    success = 6001
    status_code = status.HTTP_400_BAD_REQUEST
    try:
        is_mobile = request.data["is_mobile"]
    except:
        is_mobile = False

    if serialized.is_valid():
        data = serialized.data["data"]
        message = f"No user is associated with this {data}"
        success = 6001
        status_code = status.HTTP_400_BAD_REQUEST

        if validate_email_address(data) is True:
            """
            If the input is an valid email address, then the following code will lookup for users associated with that email address. If found then an email will be sent to the address, else an error message will be printed on the screen.
            """
            associated_users = User.objects.filter(Q(email=data) | Q(username=data))
            if associated_users.exists():
                for user in associated_users:
                    reset_password(user, request, is_mobile)

                message = "An email has been sent to {0}. Please check its inbox to continue reseting password.".format(
                    data
                )
                success = 6000
                status_code = status.HTTP_200_OK

        else:
            message = "This username does not exist in the system"
            success = 6001
            status_code = status.HTTP_400_BAD_REQUEST

            """
            If the input is an username, then the following code will lookup for users associated with that user. If found then an email will be sent to the user's address, else an error message will be printed on the screen.
            """
            associated_users = User.objects.filter(username=data)
            if associated_users.exists():
                for user in associated_users:
                    reset_password(user, request, is_mobile)
                message = "Email has been sent to {0}'s email address. Please check its inbox to continue reseting password.".format(
                    data
                )
                success = 6000
                status_code = status.HTTP_200_OK

    return Response(
        {
            "message": message,
            "success": success,
        },
        status=status_code,
    )


def mobile_signup(request):
    today = datetime.datetime.now()
    serialized = SignupSerializer(data=request.data)
    data = request.data
    if serialized.is_valid():
        first_name = serialized.validated_data["first_name"]
        last_name = serialized.validated_data["last_name"]
        username = serialized.validated_data["username"]
        email = serialized.validated_data["email"]
        password1 = serialized.validated_data["password1"]
        password2 = serialized.validated_data["password2"]

        try:
            Phone = data["phone"]
        except:
            Phone = None

        try:
            country = data["Country"]
        except:
            country = None

        try:
            state = data["State"]
        except:
            state = None

        country_ins = None
        state_ins = None
        if Country.objects.filter(id=country).exists():
            country_ins = Country.objects.get(id=country)

        if State.objects.filter(id=state).exists():
            state_ins = State.objects.get(id=state)

        message = ""
        error = False

        bad_domains = ["guerrillamail.com"]
        if "@" in email:
            email_domain = email.split("@")[1]
        else:
            message = "Please enter a proper Email"

        if User.objects.filter(email__iexact=email, is_active=True):
            message = "This email address is already in use."
            error = True
        elif email_domain in bad_domains:
            message = (
                "Registration using %s email addresses is not allowed. Please supply a different email address."
            ) % email_domain
            error = True
            email = email

        min_password_length = 6

        if len(password1) < min_password_length:
            message = "Password must have at least %i characters" % min_password_length
            error = True
        else:
            password1 = password1

        if password1 and password2 and password1 != password2:
            message = "password_mismatch"
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
            message = "Username must have at least %i characters" % min_password_length
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
                is_active=True,
            )
            Customer.objects.create(
                user=user,
                Phone=Phone,
                Country=country_ins,
                State=state_ins,
            )

            response_data = {"StatusCode": 6000, "data": serialized.data}

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {"StatusCode": 6001, "message": message}

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors),
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def forgot_password_confirm(request, uidb64, token):
    serialized = ResetPasswordSerializer(data=request.data)
    """
    View that checks the hash in a password reset link and presents a
    form for entering a new password.
    """
    UserModel = get_user_model()
    assert uidb64 is not None and token is not None  # checked by URLconf
    try:
        uid = urlsafe_base64_decode(uidb64)
        user = UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        message = "Password reset has not been successful."
        success = 6001
        if serialized.is_valid():
            new_password1 = serialized.data["new_password1"]
            new_password2 = serialized.data["new_password2"]
            if new_password1 == new_password2:
                user.set_password(new_password1)
                user.save()
                message = "Password has been reset."
                success = 6000
            else:
                message = "Password not matching"
                success = 6001

    else:
        message = "The reset password link is no longer valid."
        success = 6001

    return Response(
        {
            "message": message,
            "success": success,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def user_invite(request):
    today = datetime.datetime.now()
    serialized = ValidateSerializer(data=request.data)
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    if serialized.is_valid():
        email = serialized.data["email"]
        UserTypeID = data["UserType"]
        ExpiryDate = data["date"]
        BranchID = data["branch"]
        DefaultAccountForUser = data["DefaultAccountForUser"]
        Cash_Account = data["Cash_Account"]
        Bank_Account = data["Bank_Account"]
        Sales_Account = data["Sales_Account"]
        Sales_Return_Account = data["Sales_Return_Account"]
        Purchase_Account = data["Purchase_Account"]
        Purchase_Return_Account = data["Purchase_Return_Account"]
        is_web = data["is_web"]
        is_mobile = data["is_mobile"]
        is_pos = data["is_pos"]
        CreatedUserID = data["CreatedUserID"]
        try:
            show_all_warehouse = data["show_all_warehouse"]
        except:
            show_all_warehouse = True

        try:
            DefaultWarehouse = data["DefaultWarehouse"]
        except:
            DefaultWarehouse = 1

        userType = None
        if UserType.objects.filter(id=UserTypeID).exists():
            userType = UserType.objects.get(id=UserTypeID)
        message = ""
        error = False
        NoOfUsers = int(CompanyID.NoOfUsers)
        usertable_count = UserTable.objects.filter(CompanyID=CompanyID).count()
        customer = None
        is_create = True
        if Customer.objects.filter(user__email=email).exists():
            customer = Customer.objects.filter(user__email=email).first()
        if UserTable.objects.filter(CompanyID=CompanyID, customer=customer).exists():
            is_create = False
        if is_create == False or usertable_count < NoOfUsers:
            if User.objects.filter(email__iexact=email, is_active=True):
                customer = None
                send_mail_invitaion(email, request,"existedUser")
                if Customer.objects.filter(user__email=email).exists():
                    customer = Customer.objects.filter(user__email=email).first()
                    if is_web == False and customer.LastLoginCompanyID == CompanyID:
                        LastLoginCompanyID = None
                        if CompanySettings.objects.filter(
                            owner__email=email, is_deleted=False
                        ).exists():
                            LastLoginCompanyID = CompanySettings.objects.filter(
                                owner__email=email, is_deleted=False
                            ).last()
                        customer.LastLoginCompanyID = LastLoginCompanyID
                        customer.save()

                if UserTable.objects.filter(
                    CompanyID=CompanyID, customer=customer
                ).exists():
                    UserTable.objects.filter(
                        CompanyID=CompanyID, customer=customer
                    ).update(
                        UpdatedDate=today,
                        UserType=userType,
                        ExpiryDate=ExpiryDate,
                        DefaultAccountForUser=DefaultAccountForUser,
                        Cash_Account=Cash_Account,
                        Bank_Account=Bank_Account,
                        Sales_Account=Sales_Account,
                        Sales_Return_Account=Sales_Return_Account,
                        Purchase_Account=Purchase_Account,
                        Purchase_Return_Account=Purchase_Return_Account,
                        Action="M",
                        is_web=is_web,
                        is_mobile=is_mobile,
                        is_pos=is_pos,
                        BranchID=BranchID,
                        show_all_warehouse=show_all_warehouse,
                        DefaultWarehouse=DefaultWarehouse,
                    )
                    User_Log.objects.create(
                        UpdatedDate=today,
                        UserType=userType,
                        ExpiryDate=ExpiryDate,
                        DefaultAccountForUser=DefaultAccountForUser,
                        Cash_Account=Cash_Account,
                        Bank_Account=Bank_Account,
                        Sales_Account=Sales_Account,
                        Sales_Return_Account=Sales_Return_Account,
                        Purchase_Account=Purchase_Account,
                        Purchase_Return_Account=Purchase_Return_Account,
                        Action="M",
                        is_web=is_web,
                        is_mobile=is_mobile,
                        is_pos=is_pos,
                        BranchID=BranchID,
                        show_all_warehouse=show_all_warehouse,
                        DefaultWarehouse=DefaultWarehouse,
                    )
                    response_data = {"StatusCode": 6000, "data": serialized.data}

                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    user_table = UserTable.objects.create(
                        CompanyID=CompanyID,
                        UserType=userType,
                        DefaultAccountForUser=DefaultAccountForUser,
                        CreatedUserID=CreatedUserID,
                        customer=customer,
                        CreatedDate=today,
                        UpdatedDate=today,
                        Cash_Account=Cash_Account,
                        Bank_Account=Bank_Account,
                        Sales_Account=Sales_Account,
                        Sales_Return_Account=Sales_Return_Account,
                        Purchase_Account=Purchase_Account,
                        Purchase_Return_Account=Purchase_Return_Account,
                        JoinedDate=today.date(),
                        ExpiryDate=ExpiryDate,
                        Action="A",
                        is_web=is_web,
                        is_mobile=is_mobile,
                        is_pos=is_pos,
                        BranchID=BranchID,
                        show_all_warehouse=show_all_warehouse,
                        DefaultWarehouse=DefaultWarehouse,
                    )

                    User_Log.objects.create(
                        TransactionID=user_table.id,
                        CompanyID=CompanyID,
                        UserType=userType,
                        DefaultAccountForUser=DefaultAccountForUser,
                        CreatedUserID=CreatedUserID,
                        customer=customer,
                        CreatedDate=today,
                        UpdatedDate=today,
                        Cash_Account=Cash_Account,
                        Bank_Account=Bank_Account,
                        Sales_Account=Sales_Account,
                        Sales_Return_Account=Sales_Return_Account,
                        Purchase_Account=Purchase_Account,
                        Purchase_Return_Account=Purchase_Return_Account,
                        JoinedDate=today.date(),
                        ExpiryDate=ExpiryDate,
                        Action="A",
                        is_web=is_web,
                        is_mobile=is_mobile,
                        is_pos=is_pos,
                        BranchID=BranchID,
                        show_all_warehouse=show_all_warehouse,
                        DefaultWarehouse=DefaultWarehouse,
                    )

                    response_data = {"StatusCode": 6000, "data": serialized.data}

                    return Response(response_data, status=status.HTTP_200_OK)

            else:
                send_mail_invitaion(email, request,"NonexistedUser")
                # today = today.date()
                if InviteUsers.objects.filter(
                    Email=email,
                    CompanyID=CompanyID,
                    InvitedDate__range=(today - datetime.timedelta(days=10), today),
                ).exists():
                    invited_users = InviteUsers.objects.filter(
                        Email=email,
                        CompanyID=CompanyID,
                        InvitedDate__range=(today - datetime.timedelta(days=10), today),
                    ).first()
                    invited_users.InvitedDate = today.date()
                    invited_users.InvitedUserID = CreatedUserID
                    invited_users.UserType = userType
                    invited_users.DefaultAccountForUser = DefaultAccountForUser
                    invited_users.Cash_Account = Cash_Account
                    invited_users.Bank_Account = Bank_Account
                    invited_users.Sales_Account = Sales_Account
                    invited_users.Sales_Return_Account = Sales_Return_Account
                    invited_users.Purchase_Account = Purchase_Account
                    invited_users.Purchase_Return_Account = Purchase_Return_Account
                    invited_users.is_web = is_web
                    invited_users.is_mobile = is_mobile
                    invited_users.is_pos = is_pos
                    invited_users.ExpiryDate = ExpiryDate
                    invited_users.BranchID = BranchID
                    invited_users.show_all_warehouse = show_all_warehouse
                    invited_users.DefaultWarehouse = DefaultWarehouse
                    invited_users.save()
                else:
                    if InviteUsers.objects.filter(
                        Email=email, CompanyID=CompanyID
                    ).exists():
                        InviteUsers.objects.filter(
                            Email=email, CompanyID=CompanyID
                        ).delete()
                    InviteUsers.objects.create(
                        Email=email,
                        CompanyID=CompanyID,
                        InvitedUserID=CreatedUserID,
                        InvitedDate=today.date(),
                        UserType=userType,
                        DefaultAccountForUser=DefaultAccountForUser,
                        Cash_Account=Cash_Account,
                        Bank_Account=Bank_Account,
                        Sales_Account=Sales_Account,
                        Sales_Return_Account=Sales_Return_Account,
                        Purchase_Account=Purchase_Account,
                        Purchase_Return_Account=Purchase_Return_Account,
                        is_web=is_web,
                        is_mobile=is_mobile,
                        is_pos=is_pos,
                        ExpiryDate=ExpiryDate,
                        BranchID=BranchID,
                        show_all_warehouse=show_all_warehouse,
                        DefaultWarehouse=DefaultWarehouse,
                    )

                response_data = {"StatusCode": 6000, "data": serialized.data}

                return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "can't invite,Limit got over",
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors),
        }

        return Response(response_data, status=status.HTTP_200_OK)


def send_mail_invitaion(email, request,type="NonexistedUser"):
    # reset_password_url = "https://viknbooks.com/signup"
    # reset_password_url = "https://vikncodes.in/signup"
    if type == "existedUser":
        reset_password_url = "http://localhost:3000/signin"
        # reset_password_url = "https://vikncodes.in/signin"
        # reset_password_url = "https://viknbooks.com/signin"
    else:
        reset_password_url = "http://localhost:3000/signup"
        # reset_password_url = "https://vikncodes.in/signup"
        # reset_password_url = "https://viknbooks.com/signup"
    context = {
        "email": email,
        "domain": request.META["HTTP_ORIGIN"],
        "site_name": "viknbooks.com",
        "reset_password_url": reset_password_url,
    }

    subject_template_name = "email/user_reset_password.txt"
    email_template_name = "email/user_invitation.html"

    email_html_message = render_to_string("email/user_invitation.html", context)

    # subject = loader.render_to_string(subject_template_name, c)
    # subject = ''.join(subject.splitlines())
    # email = loader.render_to_string(email_template_name, c)

    subject = ("Invitation for {title}".format(title="viknbooks.com"),)

    send_mail(
        subject, email_html_message, DEFAULT_FROM_EMAIL, [email], fail_silently=False
    )


@api_view(["GET"])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def render_one_time_template(request):

    data = {}

    response = render(request, "email/one_time_password.html", data)
    response["X-Frame-Options"] = "allow-all"

    return response


# added by suhaib


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_profile(request):
    user_Id = request.data["userId"]
    serialized = EditProfile(data=request.data)
    instance = User.objects.get(id=user_Id)

    try:
        photo = request.data["photo"]
    except:
        photo = None

    if instance:
        if serialized.is_valid():
            Name = serialized.data["Name"]
            Gender = serialized.data["Gender"]
            Country = serialized.data["Country"]
            State = serialized.data["State"]
            Language = serialized.data["Language"]
            TimeZone = serialized.data["TimeZone"]
            try:
                Street = request.data["Street"]
            except:
                Street = None
            try:
                ZipCode = request.data["ZipCode"]
            except:
                ZipCode = None
            try:
                Address = request.data["Address"]
            except:
                Address = None
            try:
                City = request.data["City"]
            except:
                City = None

            userinstance = User.objects.get(id=user_Id)
            userinstance.first_name = Name
            userinstance.save()

            customer_instance = models.Customer.objects.get(user=userinstance)
            country_instance = models.Country.objects.get(id=Country)
            state_instance = models.State.objects.get(id=State)

            if photo:
                customer_instance.photo = photo

            customer_instance.Gender = Gender
            customer_instance.Country = country_instance
            customer_instance.State = state_instance
            customer_instance.Language = Language
            customer_instance.TimeZone = TimeZone
            customer_instance.Street = Street
            customer_instance.ZipCode = ZipCode
            customer_instance.Address = Address
            customer_instance.City = City
            customer_instance.save()

            photo = ImageSerializer(
                customer_instance, many=False, context={"request": request}
            ).data.get("photo")
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "photo": photo,
                "message": "successfully updated",
            }

        else:
            response_data = {
                "StatusCode": 6001,
                "message": generate_serializer_errors(serialized._errors),
            }
    else:
        response_data = {"StatusCode": 6001, "message": "User not found."}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_account_info(request):
    user_Id = request.data["userId"]
    serialized = EditAccountInfo(data=request.data)
    instance = User.objects.get(id=user_Id)

    if instance:
        if serialized.is_valid():
            email = serialized.data["email"]
            phone = serialized.data["phone"]

            userinstance = User.objects.get(id=user_Id)
            userinstance.email = email
            userinstance.save()

            customer_instance = models.Customer.objects.get(user=userinstance)
            customer_instance.Phone = phone
            customer_instance.save()

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "message": "successfully updated",
            }

        else:
            response_data = {
                "StatusCode": 6001,
                "message": generate_serializer_errors(serialized._errors),
            }
    else:
        response_data = {"StatusCode": 6001, "message": "User not found."}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def change_password(request):
    user_Id = request.data["userId"]
    serialized = ChangePasswordSerializer(data=request.data)
    instance = User.objects.get(id=user_Id)
    if instance:
        if serialized.is_valid():
            old_password = serialized.data["old_password"]
            new_password = serialized.data["new_password"]
            confirm_password = serialized.data["confirm_password"]

            userinstance = User.objects.get(id=user_Id)

            is_password = userinstance.check_password(old_password)
            if is_password:
                if new_password == confirm_password:
                    if len(new_password) <= 8:
                        response_data = {
                            "StatusCode": 6001,
                            "message": "length should be at least 8",
                        }
                    else:
                        userinstance.set_password(new_password)
                        userinstance.save()
                        response_data = {
                            "StatusCode": 6000,
                            "data": serialized.data,
                            "message": "successfully updated",
                        }
                else:
                    response_data = {
                        "StatusCode": 6001,
                        "message": "new password and confirm password does not match",
                    }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "old password does not match",
                }
        else:
            response_data = {
                "StatusCode": 6001,
                "message": generate_serializer_errors(serialized._errors),
            }
    else:
        response_data = {"StatusCode": 6001, "message": "User not found."}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def change_username(request):
    user_Id = request.data["userId"]
    serialized = UsernameSerializer(data=request.data)
    instance = User.objects.get(id=user_Id)
    if instance:
        if serialized.is_valid():
            username = serialized.data["username"]
            userinstance = User.objects.get(id=user_Id)

            if len(username) <= 8:
                response_data = {
                    "StatusCode": 6001,
                    "message": "length should be at least 8",
                }
            else:
                userinstance.username = username
                userinstance.save()
                response_data = {
                    "StatusCode": 6000,
                    "data": serialized.data,
                    "message": "successfully updated",
                }
        else:
            response_data = {
                "StatusCode": 6001,
                "message": generate_serializer_errors(serialized._errors),
            }
    else:
        response_data = {"StatusCode": 6001, "message": "User not found."}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def view_customer(request, pk):
    instance = User.objects.get(id=pk)
    serialized = UserListSerializer(instance, many=False, context={"request": request})

    response_data = {"StatusCode": 6000, "data": serialized.data}
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_user_account(request):
    user_Id = request.data["userId"]
    serialized = UserCredentialSerializer(data=request.data)
    instance = User.objects.get(id=user_Id)
    if instance:
        if serialized.is_valid():
            username = serialized.data["username"]
            password = serialized.data["password"]
            userinstance = User.objects.get(id=user_Id)
            is_password = userinstance.check_password(password)
            if is_password:
                if userinstance.username == username:
                    userinstance.is_active = False
                    userinstance.save()

                    response_data = {
                        "StatusCode": 6000,
                        "message": "Your account successfully deleted",
                    }
                else:
                    response_data = {
                        "StatusCode": 6001,
                        "message": "username does not match.",
                    }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "password does not match",
                }

        else:
            response_data = {
                "StatusCode": 6001,
                "message": generate_serializer_errors(serialized._errors),
            }
    else:
        response_data = {"StatusCode": 6001, "message": "User not found."}

    return Response(response_data, status=status.HTTP_200_OK)


# ends here


def send_mail_renew_request(
    email,
    request,
    company_name,
    user_name,
    user_email,
    user_phone,
    company_expiry_date,
    company_address,
    cc_email
):
    context = {
        "email": email,
        "domain": request.META["HTTP_ORIGIN"],
        "user_name": user_name,
        "company_name": company_name,
        "user_email": user_email,
        "user_phone": user_phone,
        "company_expiry_date": company_expiry_date,
        "company_address": company_address,
        "site_name": "Viknbooks",
    }

    email_html_message = render_to_string("email/renew_email.html", context)

    subject = ("Renew Organization Plan",)

    send_mail(
        subject, email_html_message, DEFAULT_FROM_EMAIL, [email],cc=[cc_email], fail_silently=False
    )
