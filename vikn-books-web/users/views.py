from django.http.response import HttpResponse
import json
from django.urls import reverse
from django.http.response import HttpResponseRedirect, HttpResponse
import json
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required
from main.decorators import ajax_required
from django.shortcuts import resolve_url, render, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.tokens import default_token_generator
from django.template.response import TemplateResponse
from django.forms.models import modelformset_factory
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
# from users.models import DatabaseStore, Customer, CustomerUser
from users.forms import DatabaseStoreForm, UserForm, LoginForm, CompanyEmployeeForm, CompanyFinancialYearForm
from main.functions import generate_form_errors
from django.contrib.auth.forms import PasswordChangeForm
from users.functions import get_auto_id
from brands.functions import createdb
from main.functions import get_current_role

from brands.models import Customer, InviteUsers, UserTable, AccountLedger, TransactionTypes, Warehouse, User_Log, UserType, Designation, Department, Employee, Employee_Log, FinancialYear, FinancialYear_Log
from users.functions import get_EmployeeCode, get_LedgerCode, get_auto_LedgerID
from users.models import CompanyEmployee, CompanyFinancialYear, CompanyAccountLedger
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.core.management.commands import loaddata
from brands.management.commands import process_db
from django.core.management import call_command
from brands.functions import get_DBS
from brands import models
from django.db.models import Q
import psycopg2
import datetime
import time
import uuid
from django.conf import settings
import os
import django
import importlib

from rest_framework.decorators import api_view, permission_classes, renderer_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from rest_framework.response import Response


# ==========users==========111
@login_required
def dashboard(request):
    current_role = get_current_role(request)
    context = {
        "title": "Dashboard",
        "is_need_flatpickr": True,
        "is_need_apexcharts": True,
        "is_need_selectize": True,
        "is_need_dashboard": True,
    }
    return render(request, "dashboard.html", context)


@login_required
def index(request):
    context = {
        "title": "Index"
    }
    return render(request, "companies/companies.html", context)


@login_required
def form_view(request):
    context = {
        "title": "Form"
    }
    return render(request, "form-view.html", context)


@login_required
def create_company(request):
    if request.method == 'POST':
        form = DatabaseStoreForm(request.POST)
        if form.is_valid():
            CompanyName = form.cleaned_data['CompanyName']
            Address1 = form.cleaned_data['Address1']
            Address2 = form.cleaned_data['Address2']
            Address3 = form.cleaned_data['Address3']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            country = form.cleaned_data['country']
            postalcode = form.cleaned_data['postalcode']
            phone = form.cleaned_data['phone']
            mobile = form.cleaned_data['mobile']
            email = form.cleaned_data['email']
            website = form.cleaned_data['website']
            currency = form.cleaned_data['currency']
            fractionalunit = form.cleaned_data['fractionalunit']
            fractionalunit = str(fractionalunit)
            vatnumber = form.cleaned_data['vatnumber']
            vatnumber = str(vatnumber)
            gstnumber = form.cleaned_data['gstnumber']
            gstnumber = str(gstnumber)
            tax1 = form.cleaned_data['tax1']
            tax1 = str(tax1)
            tax2 = form.cleaned_data['tax2']
            tax2 = str(tax2)
            tax3 = form.cleaned_data['tax3']
            tax3 = str(tax3)
            customerid = str(request.user.id)

            db_id = createdb(CompanyName, Address1, Address2, Address3, city, state, country, postalcode, phone,
                             mobile, email, website, currency, fractionalunit, vatnumber, gstnumber, tax1, tax2, tax3, customerid)

            response_data = {
                "status": "true",
                "title": "Successfully Created",
                "message": "Company created successfully.",
                "redirect": "true",
                "redirect_url": reverse('users:create_employee', kwargs={'pk': db_id})
            }
            return HttpResponse(json.dumps(response_data), content_type='application/javascript')

        else:
            message = generate_form_errors(form, formset=False)
            response_data = {
                "status": "false",
                "stable": "true",
                "title": "Form validation error",
                "message": str(message)
            }

            return HttpResponse(json.dumps(response_data), content_type='application/javascript')

    else:
        form = DatabaseStoreForm()
        context = {
            "title": "Create Company",
            "form": form,
            "redirect": "true",
            "is_company": True,
            "is_employee": False,
            "is_company_create": True,
            "is_financial_year": False,
            "is_need_flatpickr": False,
            "is_need_apexcharts": False,
            "is_need_selectize": False,
            "is_need_dashboard": False,
            "is_need_bootstrap_wizard": True,
            "is_need_form_wizard": True,
        }
        return render(request, 'companies/create_company.html', context)


@login_required
def create_employee(request, pk):
    datastore = DatabaseStore.objects.filter(pk=pk)
    designations = Designation.objects.all()
    departments = Department.objects.all()
    if request.method == 'POST':
        form = CompanyEmployeeForm(request.POST)
        if form.is_valid():
            FirstName = form.cleaned_data['FirstName']
            LastName = form.cleaned_data['LastName']
            DesignationID = form.cleaned_data['DesignationID']
            DepartmentID = form.cleaned_data['DepartmentID']
            Gender = form.cleaned_data['Gender']
            Email = form.cleaned_data['Email']

            EmployeeID = 1
            BranchID = 1
            Action = "A"
            CreatedDate = datetime.date.today()
            UpdatedDate = datetime.date.today()
            CreatedUserID = 1
            CompanyID = pk
            EmployeeCode = get_EmployeeCode(CompanyEmployee, BranchID)
            CompanyEmployee.objects.create(
                FirstName=FirstName,
                LastName=LastName,
                DesignationID=DesignationID,
                DepartmentID=DepartmentID,
                CompanyID=pk,
                Gender=Gender,
                Email=Email,
                EmployeeID=EmployeeID,
                BranchID=BranchID,
                Action=Action,
                CreatedDate=CreatedDate,
                UpdatedDate=UpdatedDate,
                CreatedUserID=CreatedUserID,
                EmployeeCode=EmployeeCode
            )
            LedgerCode = get_LedgerCode(CompanyAccountLedger, BranchID)
            LedgerID = get_auto_LedgerID(CompanyAccountLedger, BranchID)
            CompanyAccountLedger.objects.create(
                CompanyID=pk,
                LedgerID=LedgerID,
                BranchID=BranchID,
                LedgerName=FirstName,
                LedgerCode=LedgerCode,
                AccountGroupUnder=32,
                OpeningBalance=0,
                CrOrDr="Dr",
                IsActive=True,
                IsDefault=False,
                CreatedUserID=request.user.id,
                CreatedDate=CreatedDate,
                UpdatedDate=UpdatedDate,
                Action=Action,
            )
            datastore.update(is_employee=True)
            response_data = {
                "status": "true",
                "title": "Successfully Created",
                "message": "Company created successfully.",
                "redirect": "true",
                "redirect_url": reverse('users:create_financial_year', kwargs={'pk': pk})
            }
            return HttpResponse(json.dumps(response_data), content_type='application/javascript')

        else:
            print(form.errors)
            message = generate_form_errors(form, formset=False)
            response_data = {
                "status": "false",
                "stable": "true",
                "title": "Form validation error",
                "message": str(message)
            }

            return HttpResponse(json.dumps(response_data), content_type='application/javascript')

    else:
        form = CompanyEmployeeForm()
        context = {
            "title": "Create Company",
            "form": form,
            "redirect": "true",
            "is_company": False,
            "is_employee": True,
            "designations": designations,
            "departments": departments,
            "is_financial_year": False,
            "is_need_flatpickr": False,
            "is_need_apexcharts": False,
            "is_need_selectize": False,
            "is_need_dashboard": False,
            "is_need_bootstrap_wizard": True,
            "is_need_form_wizard": True,
        }
        return render(request, 'companies/create_company.html', context)


@login_required
def create_financial_year(request, pk):
    datastore = DatabaseStore.objects.filter(pk=pk)
    if request.method == 'POST':
        form = CompanyFinancialYearForm(request.POST)
        if form.is_valid():
            FinancialYearID = 1
            CompanyID = pk
            Action = "A"
            FromDate = form.cleaned_data['FromDate']
            ToDate = form.cleaned_data['ToDate']
            IsClosed = False
            Notes = form.cleaned_data['Notes']
            CreatedDate = datetime.date.today()
            UpdatedDate = datetime.date.today()
            CreatedUserID = 1

            no_of_days = ToDate - FromDate
            no_of_days = str(no_of_days).split(' ')
            if no_of_days[0] == '364' or no_of_days[0] == '365':

                CompanyFinancialYear.objects.create(
                    FinancialYearID=FinancialYearID,
                    CompanyID=CompanyID,
                    Action=Action,
                    FromDate=FromDate,
                    ToDate=ToDate,
                    IsClosed=IsClosed,
                    Notes=Notes,
                    CreatedDate=CreatedDate,
                    UpdatedDate=UpdatedDate,
                    CreatedUserID=CreatedUserID,
                )

                datastore.update(is_financial_year=True)

            else:
                response_data = {
                    "status": "false",
                    "stable": "true",
                    "title": "You Have Entered Invalid Financial year",
                    "message": "The financial year must be one year"
                }
                return HttpResponse(json.dumps(response_data), content_type='application/javascript')

            get_DBS()
            response_data = {
                "status": "true",
                "title": "Successfully Created",
                "message": "Company created successfully.",
                "redirect": "true",
                "redirect_url": reverse('users:companies')
            }
            return HttpResponse(json.dumps(response_data), content_type='application/javascript')

        else:
            message = generate_form_errors(form, formset=False)
            response_data = {
                "status": "false",
                "stable": "true",
                "title": "Form validation error",
                "message": str(message)
            }

            return HttpResponse(json.dumps(response_data), content_type='application/javascript')

    else:
        strings = time.strftime("%Y")
        t = strings.split(',')
        numbers = [int(x) for x in t]
        from_date = str(numbers[0])
        to_date = str(numbers[0]+1)
        fin_from_date = str(from_date+'-04-01')
        fin_to_date = str(to_date+'-03-31')
        form = CompanyFinancialYearForm(
            initial={'FromDate': fin_from_date, 'ToDate': fin_to_date})
        context = {
            "title": "Create Company",
            "form": form,
            "redirect": "true",
            "is_company": False,
            "is_employee": False,
            "is_financial_year": True,
            "is_need_flatpickr": False,
            "is_need_apexcharts": False,
            "is_need_selectize": False,
            "is_need_dashboard": False,
            "is_need_bootstrap_wizard": True,
            "is_need_form_wizard": True,
        }
        return render(request, 'companies/create_company.html', context)


# @login_required
# def companies(request):
#     current_role = get_current_role(request)
#     try:
#         is_customerid = DatabaseStore.objects.filter(customerid=request.user.id)[0]
#     except:
#         is_customerid = None
#     if current_role == "superadmin":

#         is_customer = False
#         if is_customerid == None:
#             is_customer = False
#         else:
#             is_customer = True

#         instances = DatabaseStore.objects.all()

#         query = request.GET.get("q")
#         if query:
#             instances = instances.filter(Q(DatabaseName__icontains=query))
#             # title = "Classes - %s" %query

#         context = {
#             "title" : "Create Compnay",
#             "caption" : "Home",
#             "is_login" : False,
#             "is_customer" : is_customer,
#             'instances': instances,
#         }
#         if not is_customer:
#             return HttpResponseRedirect(reverse('users:create_company'))
#         else:
#             return render(request,'companies/companies.html',context)
#     else:
#         return HttpResponseRedirect(reverse('dashboard'))


@login_required
def create_db_user(request, pk):
    datastore = get_object_or_404(DatabaseStore.objects.filter(id=pk))
    database = datastore.DefaultDatabase
    cash_accounts = AccountLedger.objects.filter(AccountGroupUnder=9)
    bank_accounts = AccountLedger.objects.filter(AccountGroupUnder=8)
    sales_accounts = AccountLedger.objects.filter(AccountGroupUnder=74)
    purchase_accounts = AccountLedger.objects.filter(AccountGroupUnder=48)
    warehouses = Warehouse.objects.all()

    sales_gst_types = TransactionTypes.objects.filter(
        MasterTypeID=6, BranchID=1)
    purchase_gst_types = TransactionTypes.objects.filter(
        MasterTypeID=7, BranchID=1)
    vat_types = TransactionTypes.objects.filter(MasterTypeID=8, BranchID=1)
    user_types = UserType.objects.all()
    employee = get_object_or_404(CompanyEmployee.objects.filter(CompanyID=pk))
    financial_year = get_object_or_404(
        CompanyFinancialYear.objects.filter(CompanyID=pk))
    accountledger = get_object_or_404(
        CompanyAccountLedger.objects.filter(CompanyID=pk))

    try:
        db_id = get_object_or_404(CustomerUser.objects.filter(databaseid=pk))
    except:
        db_id = None

    if request.method == 'POST':
        form = UserForm(request.POST)
        Cash_Account = request.POST.get("Cash_Account")
        Bank_Account = request.POST.get("Bank_Account")
        warehouse = request.POST.get("Warehouse")
        Sales_Account = request.POST.get("Sales_Account")
        Sales_Return_Account = request.POST.get("Sales_Return_Account")
        Purchase_Account = request.POST.get("Purchase_Account")
        Purchase_Return_Account = request.POST.get("Purchase_Return_Account")
        Sales_GST_Type = request.POST.get("Sales_GST_Type")
        Purchase_GST_Type = request.POST.get("Purchase_GST_Type")
        VAT_Type = request.POST.get("VAT_Type")
        ExpiryDate = request.POST.get("ExpiryDate")
        UserTypeID = request.POST.get("UserTypeID")

        if form.is_valid():
            data = form.save(commit=False)
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            message = ""
            error = False
            if User.objects.filter(email=email).exists():
                error = True
                message += "This email already exists."
            elif User.objects.filter(username=username).exists():
                error = True
                message += "This username already exists."

            if not error:
                branchid = 1
                id = get_auto_id(UserTable, branchid, database)
                action = "A"
                employeeid = 1
                isactive = True
                createduserid = request.user.id
                createddate = datetime.date.today()
                databaseid = pk

                user_table = models.UserTable(
                    ID=id,
                    UserTypeID=UserTypeID,
                    BranchID=branchid,
                    Action=action,
                    UserName=username,
                    Password=password,
                    EmployeeID=employeeid,
                    IsActive=isactive,
                    CreatedUserID=createduserid,
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

                )
                user_table.save(using=database)

                user_log_table = models.User_Log(
                    TransactionID=id,
                    UserTypeID=UserTypeID,
                    BranchID=branchid,
                    Action=action,
                    UserName=username,
                    Password=password,
                    EmployeeID=employeeid,
                    IsActive=isactive,
                    CreatedUserID=createduserid,
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

                )
                user_log_table.save(using=database)

                employee_save = models.Employee(
                    FirstName=employee.FirstName,
                    LastName=employee.LastName,
                    EmployeeID=employee.EmployeeID,
                    DesignationID=employee.DesignationID,
                    DepartmentID=employee.DepartmentID,
                    Gender=employee.Gender,
                    Email=employee.Email,
                    BranchID=5,
                    Action=employee.Action,
                    CreatedDate=employee.CreatedDate,
                    UpdatedDate=employee.UpdatedDate,
                    CreatedUserID=employee.CreatedUserID,
                    EmployeeCode=employee.EmployeeCode
                )
                employee_save.save(using=database)

                employee_log = models.Employee_Log(
                    FirstName=employee.FirstName,
                    LastName=employee.LastName,
                    TransactionID=employee.EmployeeID,
                    DesignationID=employee.DesignationID,
                    DepartmentID=employee.DepartmentID,
                    Gender=employee.Gender,
                    Email=employee.Email,
                    BranchID=5,
                    Action=employee.Action,
                    CreatedDate=employee.CreatedDate,
                    UpdatedDate=employee.UpdatedDate,
                    CreatedUserID=employee.CreatedUserID,
                    EmployeeCode=employee.EmployeeCode
                )
                employee_log.save(using=database)

                accountledger_save = models.AccountLedger(
                    LedgerID=accountledger.LedgerID,
                    BranchID=5,
                    LedgerName=accountledger.LedgerName,
                    LedgerCode=accountledger.LedgerCode,
                    AccountGroupUnder=accountledger.AccountGroupUnder,
                    OpeningBalance=accountledger.OpeningBalance,
                    CrOrDr=accountledger.CrOrDr,
                    IsActive=accountledger.IsActive,
                    IsDefault=accountledger.IsDefault,
                    CreatedUserID=accountledger.CreatedUserID,
                    CreatedDate=accountledger.CreatedDate,
                    UpdatedDate=accountledger.UpdatedDate,
                    Action=accountledger.Action,
                )
                accountledger_save.save(using=database)

                accountledger_log_save = models.AccountLedger_Log(
                    TransactionID=accountledger.LedgerID,
                    BranchID=5,
                    LedgerName=accountledger.LedgerName,
                    LedgerCode=accountledger.LedgerCode,
                    AccountGroupUnder=accountledger.AccountGroupUnder,
                    OpeningBalance=accountledger.OpeningBalance,
                    CrOrDr=accountledger.CrOrDr,
                    IsActive=accountledger.IsActive,
                    IsDefault=accountledger.IsDefault,
                    CreatedUserID=accountledger.CreatedUserID,
                    CreatedDate=accountledger.CreatedDate,
                    UpdatedDate=accountledger.UpdatedDate,
                    Action=accountledger.Action,
                )
                accountledger_log_save.save(using=database)

                financial_year_save = models.FinancialYear(
                    FinancialYearID=financial_year.FinancialYearID,
                    Action=financial_year.Action,
                    FromDate=financial_year.FromDate,
                    ToDate=financial_year.ToDate,
                    IsClosed=financial_year.IsClosed,
                    Notes=financial_year.Notes,
                    CreatedDate=financial_year.CreatedDate,
                    UpdatedDate=financial_year.UpdatedDate,
                    CreatedUserID=financial_year.CreatedUserID,
                )
                financial_year_save.save(using=database)

                financial_year_save = models.FinancialYear_Log(
                    TransactionID=financial_year.FinancialYearID,
                    Action=financial_year.Action,
                    FromDate=financial_year.FromDate,
                    ToDate=financial_year.ToDate,
                    IsClosed=financial_year.IsClosed,
                    Notes=financial_year.Notes,
                    CreatedDate=financial_year.CreatedDate,
                    UpdatedDate=financial_year.UpdatedDate,
                    CreatedUserID=financial_year.CreatedUserID,
                )
                financial_year_save.save(using=database)

                data.save()

                CustomerUser.objects.create(
                    databaseid=databaseid,
                    email=email,
                    username=username,
                    password=password,
                    user=data
                )
                response_data = {
                    "status": "true",
                    "title": "Successfully Created",
                    "message": "Company created successfully.",
                    "redirect": "true",
                    "redirect_url": reverse('users:companies')
                }
                return HttpResponse(json.dumps(response_data), content_type='application/javascript')
            else:
                response_data = {
                    'status': 'false',
                    'title': "Can't create this user",
                    'redirect': 'true',
                    'message': message,
                }

        else:
            message = generate_form_errors(form, formset=False)
            response_data = {
                "status": "false",
                "stable": "true",
                "title": "Form validation error",
                "message": str(message)
            }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        if datastore.is_employee == False:
            return HttpResponseRedirect(reverse('users:create_employee', kwargs={'pk': pk}))
        elif datastore.is_financial_year == False:
            return HttpResponseRedirect(reverse('users:create_financial_year', kwargs={'pk': pk}))
        elif db_id == None:
            form = UserForm(request.POST)
            context = {
                "title": "User Login",
                "caption": "Home",
                "form": form,
                "cash_accounts": cash_accounts,
                "bank_accounts": bank_accounts,
                "sales_accounts": sales_accounts,
                "purchase_accounts": purchase_accounts,
                "warehouses": warehouses,
                "sales_gst_types": sales_gst_types,
                "purchase_gst_types": purchase_gst_types,
                "vat_types": vat_types,
                "user_types": user_types,
            }
            return render(request, 'companies/create_db_user.html', context)
        else:
            return HttpResponseRedirect(reverse('users:login_db_user'))


@login_required
def login_db_user(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                response_data = {
                    'status': 'true',
                    "redirect": 'true',
                    "no-poup": 'true',
                    'redirect_url': reverse('dashboard')
                }
            else:
                response_data = {
                    'status': 'false',
                    'stable': 'true',
                    'title': "User not exists",
                    "message": "User with this username and password does not exist."
                }
            return HttpResponse(json.dumps(response_data), content_type='application/javascript')
        else:
            message = generate_form_errors(form, formset=False)
            response_data = {
                'status': 'false',
                'stable': 'true',
                'title': "From validation error.",
                "message": message
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = LoginForm(request.POST)
        context = {
            "title": "User Login",
            "caption": "Home",
            "form": form
        }
        return render(request, 'companies/login_db_user.html', context)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def create_user(request):
    data = request.data
    today = datetime.datetime.now()
    user = None
    user_id = data['id']
    first_name = data['first_name']
    last_name = data['last_name']
    email = data['email']
    username = data['username']
    password = data['password']
    is_superuser = False
    last_login = data['last_login']

    if InviteUsers.objects.filter(Email=email).exists():
        active = True
        invited_user = InviteUsers.objects.filter(Email=email).first()
        if not User.objects.filter(id=user_id).exists():
            user = User.objects.create_user(
                id=user_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password,
                is_superuser=False,
                is_active=True,
            )
            if not Customer.objects.filter(user=user).exists():
                customer = Customer.objects.create(
                    user=user,
                    LastLoginCompanyID=invited_user.CompanyID
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
        # print(User.objects.get(email=data['email']))
        if not User.objects.filter(pk=user_id,email=data['email']).exists():
            user = User.objects.create_user(
                id=user_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password,
                is_superuser=False,
                is_active=True,
            )
            if not Customer.objects.filter(user=user).exists():
                Customer.objects.create(
                    user=user,
                    VerificationTokenTime=today
                )
        else:
            user = User.objects.get(pk=user_id,email=data['email'])
            user.is_active = True
            user.save()

        
    response_data = {
        "message": "success",
    }
    return Response(response_data, status=status.HTTP_200_OK)

