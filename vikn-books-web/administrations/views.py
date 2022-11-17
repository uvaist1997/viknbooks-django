import json
import os
import datetime
import pytz
from django.utils import timezone
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.http.response import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.http import JsonResponse
from django.db.models import Q
from django.conf import settings
from django.template.loader import render_to_string
from brands import models as administrations_models
from users.models import CustomerUser, DatabaseStore
# from brands.models import UserTable, User_Log, AccountLedger, AccountLedger_Log
from django.db import models
from administrations.forms import GeneralSettingsForm, FinancialYearForm, DatabaseStoreForm
from api.v1.accountLedgers.functions import get_LedgerCode
from accounts.functions import generate_form_errors, get_auto_LedgerID
from api.v1.designation.functions import get_auto_id
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from administrations.forms import UserForm
from main.functions import get_DataBase
from administrations.functions import get_auto_id_user_type, get_auto_id_financial_year
from administrations.forms import UserTypeForm
import datetime



@login_required
def create_general_settings(request):
    DataBase = get_DataBase(request)
    
    today = datetime.date.today()
    if request.method == 'POST':
        form = GeneralSettingsForm(request.POST)
        if form.is_valid(): 
            data = form.save(commit=False)
            QtyDecimalPoint = request.POST.get('QtyDecimalPoint')
            PriceDecimalPoint = request.POST.get('PriceDecimalPoint')
            if QtyDecimalPoint.isnumeric() and PriceDecimalPoint.isnumeric():

                Tax_Active = request.POST.get('Tax_Active')
                if Tax_Active == "VAT":
                    VAT = "True"
                    GST = "False"
                elif Tax_Active == "GST":
                    GST = "True"
                    VAT = "False"
                else:
                    GST = "False"
                    VAT = "False"

                Tax1 = request.POST.get('Tax1')
                Tax2 = request.POST.get('Tax2')
                Tax3 = request.POST.get('Tax3')
                if Tax1 == None:
                    Tax1 = "False"

                if Tax2 == None:
                    Tax2 = "False"

                if Tax3 == None:
                    Tax3 = "False"

                Additional_Discount = request.POST.get('Additional_Discount')
                Bill_Discount = request.POST.get('Bill_Discount')
                if Additional_Discount == None:
                    Additional_Discount = "False"
                if Bill_Discount == None:
                    Bill_Discount = "False"

                Business_Type = request.POST.get('Business_Type')
                if Business_Type == "Trading":
                    Trading = "True"
                    Restaurant = "False"
                elif Business_Type == "Restaurant":
                    Restaurant = "True"
                    Trading = "False"
                else:
                    Trading = "False"
                    Restaurant = "False"

                Negative_Stock_Show = request.POST.get('Negative_Stock_Show')
                if Negative_Stock_Show == None:
                    Negative_Stock_Show = False

                Increment_Qty_In_POS = request.POST.get('Increment_Qty_In_POS')
                if Increment_Qty_In_POS == None:
                    Increment_Qty_In_POS = False

                Kitchen_Print = request.POST.get('Kitchen_Print')
                if Kitchen_Print == None:
                    Kitchen_Print = False

                Order_Print = request.POST.get('Order_Print')
                if Order_Print == None:
                    Order_Print = False

                Print_After_Save_Active = request.POST.get('Print_After_Save_Active')
                if Print_After_Save_Active == None:
                    Print_After_Save_Active = False

                Action = "M"
                User = request.user.id

                administrations_models.GeneralSettings.objects.using(DataBase).filter(SettingsType="VAT").update(SettingsValue=VAT, UpdatedDate=today, CreatedUserID=User, Action=Action)
                administrations_models.GeneralSettings.objects.using(DataBase).filter(SettingsType="GST").update(SettingsValue=GST, UpdatedDate=today, CreatedUserID=User, Action=Action)
                administrations_models.GeneralSettings.objects.using(DataBase).filter(SettingsType="TAX1").update(SettingsValue=Tax1, UpdatedDate=today, CreatedUserID=User, Action=Action)
                administrations_models.GeneralSettings.objects.using(DataBase).filter(SettingsType="TAX2").update(SettingsValue=Tax2, UpdatedDate=today, CreatedUserID=User, Action=Action)
                administrations_models.GeneralSettings.objects.using(DataBase).filter(SettingsType="TAX3").update(SettingsValue=Tax3, UpdatedDate=today, CreatedUserID=User, Action=Action)
                administrations_models.GeneralSettings.objects.using(DataBase).filter(SettingsType="Trading").update(SettingsValue=Trading, UpdatedDate=today, CreatedUserID=User, Action=Action)
                administrations_models.GeneralSettings.objects.using(DataBase).filter(SettingsType="Restaurant").update(SettingsValue=Restaurant, UpdatedDate=today, CreatedUserID=User, Action=Action)
                administrations_models.GeneralSettings.objects.using(DataBase).filter(SettingsType="QtyDecimalPoint").update(SettingsValue=QtyDecimalPoint, UpdatedDate=today, CreatedUserID=User, Action=Action)
                administrations_models.GeneralSettings.objects.using(DataBase).filter(SettingsType="PriceDecimalPoint").update(SettingsValue=PriceDecimalPoint, UpdatedDate=today, CreatedUserID=User, Action=Action)
                administrations_models.GeneralSettings.objects.using(DataBase).filter(SettingsType="Additional_Discount").update(SettingsValue=Additional_Discount, UpdatedDate=today, CreatedUserID=User, Action=Action)
                administrations_models.GeneralSettings.objects.using(DataBase).filter(SettingsType="Bill_Discount").update(SettingsValue=Bill_Discount, UpdatedDate=today, CreatedUserID=User, Action=Action)
                administrations_models.GeneralSettings.objects.using(DataBase).filter(SettingsType="Negatine_Stock").update(SettingsValue=Negative_Stock_Show, UpdatedDate=today, CreatedUserID=User, Action=Action)
                
                if administrations_models.GeneralSettings.objects.using(DataBase).get(SettingsType="Restaurant").SettingsValue == "True":
                    administrations_models.GeneralSettings.objects.using(DataBase).filter(SettingsType="Increment_Qty_In_POS").update(SettingsValue=Increment_Qty_In_POS, UpdatedDate=today, CreatedUserID=User, Action=Action)
                    administrations_models.GeneralSettings.objects.using(DataBase).filter(SettingsType="Kitchen_Print").update(SettingsValue=Kitchen_Print, UpdatedDate=today, CreatedUserID=User, Action=Action)
                    administrations_models.GeneralSettings.objects.using(DataBase).filter(SettingsType="Order_Print").update(SettingsValue=Order_Print, UpdatedDate=today, CreatedUserID=User, Action=Action)
                    administrations_models.GeneralSettings.objects.using(DataBase).filter(SettingsType="Print_After_Save_Active").update(SettingsValue=Print_After_Save_Active, UpdatedDate=today, CreatedUserID=User, Action=Action)
                else:
                    administrations_models.GeneralSettings.objects.using(DataBase).filter(SettingsType="Increment_Qty_In_POS").update(SettingsValue="False", UpdatedDate=today, CreatedUserID=User, Action=Action)
                    administrations_models.GeneralSettings.objects.using(DataBase).filter(SettingsType="Kitchen_Print").update(SettingsValue="False", UpdatedDate=today, CreatedUserID=User, Action=Action)
                    administrations_models.GeneralSettings.objects.using(DataBase).filter(SettingsType="Order_Print").update(SettingsValue="False", UpdatedDate=today, CreatedUserID=User, Action=Action)
                    administrations_models.GeneralSettings.objects.using(DataBase).filter(SettingsType="Print_After_Save_Active").update(SettingsValue="False", UpdatedDate=today, CreatedUserID=User, Action=Action)
                general_settings = administrations_models.GeneralSettings.objects.using(DataBase).all()

                for settings in general_settings:

                    administrations_models.GeneralSettings_Log.objects.using(DataBase).create(
                        TransactionID = settings.GeneralSettingsID,
                        BranchID = settings.BranchID,
                        GroupName = settings.GroupName,
                        SettingsType = settings.SettingsType,
                        SettingsValue = settings.SettingsValue,
                        Action = settings.Action,
                        CreatedDate = settings.CreatedDate,
                        UpdatedDate = settings.UpdatedDate,
                        CreatedUserID = settings.CreatedUserID,
                        )
                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("General Settings Created Successfully!")),
                }
            else:
                response_data = {
                    'status' : 'false',
                    'stable' : 'true',
                    'title' : str(_("Please enter a number")),
                    "message" : str("You enterd an invalid number")
                }

            return HttpResponse(json.dumps(response_data), content_type='application/javascript')

        else:
            message = generate_form_errors(form,formset=False)
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("Form validation error")),
                "message" : str(message)
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        check_VAT = administrations_models.GeneralSettings.objects.using(DataBase).get(SettingsType="VAT").SettingsValue
        check_GST = administrations_models.GeneralSettings.objects.using(DataBase).get(SettingsType="GST").SettingsValue
        check_TAX1 = administrations_models.GeneralSettings.objects.using(DataBase).get(SettingsType="TAX1").SettingsValue
        check_TAX2 = administrations_models.GeneralSettings.objects.using(DataBase).get(SettingsType="TAX2").SettingsValue
        check_TAX3 = administrations_models.GeneralSettings.objects.using(DataBase).get(SettingsType="TAX3").SettingsValue
        check_Trading = administrations_models.GeneralSettings.objects.using(DataBase).get(SettingsType="Trading").SettingsValue
        check_Restaurant = administrations_models.GeneralSettings.objects.using(DataBase).get(SettingsType="Restaurant").SettingsValue
        check_QtyDecimalPoint = administrations_models.GeneralSettings.objects.using(DataBase).get(SettingsType="QtyDecimalPoint").SettingsValue
        check_PriceDecimalPoint = administrations_models.GeneralSettings.objects.using(DataBase).get(SettingsType="PriceDecimalPoint").SettingsValue
        check_Additional_Discount = administrations_models.GeneralSettings.objects.using(DataBase).get(SettingsType="Additional_Discount").SettingsValue
        check_Bill_Discount = administrations_models.GeneralSettings.objects.using(DataBase).get(SettingsType="Bill_Discount").SettingsValue
        check_Negatine_Stock = administrations_models.GeneralSettings.objects.using(DataBase).get(SettingsType="Negatine_Stock").SettingsValue
        check_Increment_Qty_In_POS = administrations_models.GeneralSettings.objects.using(DataBase).get(SettingsType="Increment_Qty_In_POS").SettingsValue
        check_Kitchen_Print = administrations_models.GeneralSettings.objects.using(DataBase).get(SettingsType="Kitchen_Print").SettingsValue
        check_Order_Print = administrations_models.GeneralSettings.objects.using(DataBase).get(SettingsType="Order_Print").SettingsValue
        check_Print_After_Save_Active = administrations_models.GeneralSettings.objects.using(DataBase).get(SettingsType="Print_After_Save_Active").SettingsValue
        QtyDecimalPoint = administrations_models.GeneralSettings.objects.using(DataBase).get(SettingsType="QtyDecimalPoint").SettingsValue
        PriceDecimalPoint = administrations_models.GeneralSettings.objects.using(DataBase).get(SettingsType="PriceDecimalPoint").SettingsValue

        context = {
            "is_need_flatpickr" : False,
            "is_need_apexcharts" : False,
            "is_need_selectize" : False,
            "is_need_dashboard" : False,
            "is_need_switchery" : False,
            "is_need_bootstrap_wizard" : True,
            "is_need_form_wizard" : True,

            "check_VAT" : check_VAT,
            "check_GST" : check_GST,
            "check_TAX1" : check_TAX1,
            "check_TAX2" : check_TAX2,
            "check_TAX3" : check_TAX3,
            "check_Trading" : check_Trading,
            "check_Restaurant" : check_Restaurant,
            "check_QtyDecimalPoint" : check_QtyDecimalPoint,
            "check_PriceDecimalPoint" : check_PriceDecimalPoint,
            "check_Additional_Discount" : check_Additional_Discount,
            "check_Bill_Discount" : check_Bill_Discount,
            "check_Negatine_Stock" : check_Negatine_Stock,
            "check_Increment_Qty_In_POS" : check_Increment_Qty_In_POS,
            "check_Kitchen_Print" : check_Kitchen_Print,
            "check_Order_Print" : check_Order_Print,
            "check_Print_After_Save_Active" : check_Print_After_Save_Active,
            "QtyDecimalPoint" : QtyDecimalPoint,
            "PriceDecimalPoint" : PriceDecimalPoint,


            "title" : "General Settings",
        }
        return render(request,"administrations/masters/create_general_settings.html",context)


@login_required
def create_user(request):
    from users.functions import get_auto_id


    DataBase = get_DataBase(request)
    cash_accounts = administrations_models.AccountLedger.objects.using(DataBase).filter(AccountGroupUnder=9)
    bank_accounts = administrations_models.AccountLedger.objects.using(DataBase).filter(AccountGroupUnder=8)
    sales_accounts = administrations_models.AccountLedger.objects.using(DataBase).filter(AccountGroupUnder=74)
    purchase_accounts = administrations_models.AccountLedger.objects.using(DataBase).filter(AccountGroupUnder=48)
    warehouses = administrations_models.Warehouse.objects.using(DataBase).all()
    
    sales_gst_types = administrations_models.TransactionTypes.objects.using(DataBase).filter(MasterTypeID=6, BranchID=1)
    purchase_gst_types = administrations_models.TransactionTypes.objects.using(DataBase).filter(MasterTypeID=7, BranchID=1)
    vat_types = administrations_models.TransactionTypes.objects.using(DataBase).filter(MasterTypeID=8, BranchID=1)
    user_types = administrations_models.UserType.objects.using(DataBase).all()

    DataBaseID = get_object_or_404(DatabaseStore.objects.filter(DefaultDatabase=DataBase))
    DataBaseID = DataBaseID.id

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
                id = get_auto_id(administrations_models.UserTable,branchid,DataBase)
                action = "A"
                employeeid = 1
                isactive = True
                createduserid = request.user.id
                createddate = datetime.date.today()

                user_table = administrations_models.UserTable(
                    ID = id,
                    UserTypeID = UserTypeID,
                    BranchID = branchid,
                    Action = action,
                    UserName = username,
                    Password = password,
                    EmployeeID = employeeid,
                    IsActive = isactive,
                    CreatedUserID = createduserid,
                    CreatedDate = createddate,
                    Cash_Account = Cash_Account,
                    Bank_Account = Bank_Account,
                    Warehouse = warehouse,
                    Sales_Account = Sales_Account,
                    Sales_Return_Account = Sales_Return_Account,
                    Purchase_Account = Purchase_Account,
                    Purchase_Return_Account = Purchase_Return_Account,
                    Sales_GST_Type = Sales_GST_Type,
                    Purchase_GST_Type = Purchase_GST_Type,
                    VAT_Type = VAT_Type,
                    ExpiryDate=ExpiryDate,

                    )
                user_table.save(using=DataBase)

                user_log_table = administrations_models.User_Log(
                    TransactionID = id,
                    UserTypeID = UserTypeID,
                    BranchID = branchid,
                    Action = action,
                    UserName = username,
                    Password = password,
                    EmployeeID = employeeid,
                    IsActive = isactive,
                    CreatedUserID = createduserid,
                    CreatedDate = createddate,
                    Cash_Account = Cash_Account,
                    Bank_Account = Bank_Account,
                    Warehouse = warehouse,
                    Sales_Account = Sales_Account,
                    Sales_Return_Account = Sales_Return_Account,
                    Purchase_Account = Purchase_Account,
                    Purchase_Return_Account = Purchase_Return_Account,
                    Sales_GST_Type = Sales_GST_Type,
                    Purchase_GST_Type = Purchase_GST_Type,
                    VAT_Type = VAT_Type,
                    ExpiryDate=ExpiryDate,

                    )
                user_log_table.save(using=DataBase)
                data.save()
                CustomerUser.objects.create(
                    databaseid = DataBaseID,
                    email = email,
                    username = username,
                    password = password,
                    user = data
                )  

                response_data = {
                        "status" : "true",
                        "title" : "Successfully Created",
                        "message" : "Company created successfully.",
                        "redirect" : "true",
                        "redirect_url" : reverse('administrations:users')
                    }   
                return HttpResponse(json.dumps(response_data), content_type='application/javascript')
            else:
                response_data = {
                    'status' : 'false',     
                    'title' : "Can't create this user",       
                    'redirect' : 'true', 
                    'message' : message,
                }
        
        else:            
            message = generate_form_errors(form,formset=False)      
            response_data = {
                "status" : "false",
                "stable" : "true",
                "title" : "Form validation error",
                "message": str(message)
            }        
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = UserForm(request.POST)
        context = {
            "title" : "User Login",
            "caption" : "Home",
            "form" : form,
            "cash_accounts" : cash_accounts,
            "bank_accounts" : bank_accounts,
            "sales_accounts" : sales_accounts,
            "purchase_accounts" : purchase_accounts,
            "warehouses" : warehouses,
            "sales_gst_types" : sales_gst_types,
            "purchase_gst_types" : purchase_gst_types,
            "vat_types" : vat_types,
            "user_types" : user_types,
        }
        return render(request,'administrations/masters/create_user.html',context)


@login_required
def users(request):
    DataBase = get_DataBase(request)
    DataBaseID = get_object_or_404(DatabaseStore.objects.filter(DefaultDatabase=DataBase))
    DataBaseID = DataBaseID.id
    instances = CustomerUser.objects.filter(databaseid = DataBaseID)
    context = {
        'instances' : instances,
        'title' : 'User'
    }
    return render(request,"administrations/masters/users.html",context)


@login_required
def view_user(request,pk):
    DataBase = get_DataBase(request)
    instance = CustomerUser.objects.get(pk=pk)
    user_table = get_object_or_404(administrations_models.UserTable.objects.using(DataBase).filter(UserName=instance.username))

    cash_account = administrations_models.AccountLedger.objects.using(DataBase).get(id=user_table.Cash_Account).LedgerName
    bank_account = administrations_models.AccountLedger.objects.using(DataBase).get(id=user_table.Bank_Account).LedgerName
    sales_account = administrations_models.AccountLedger.objects.using(DataBase).get(id=user_table.Sales_Account).LedgerName
    sales_return = administrations_models.AccountLedger.objects.using(DataBase).get(id=user_table.Sales_Return_Account).LedgerName
    purchase_account = administrations_models.AccountLedger.objects.using(DataBase).get(id=user_table.Purchase_Account).LedgerName
    purchase_return = administrations_models.AccountLedger.objects.using(DataBase).get(id=user_table.Purchase_Return_Account).LedgerName
    warehouses = administrations_models.Warehouse.objects.using(DataBase).get(WarehouseID=user_table.Warehouse).WarehouseName
    
    sales_gst_type = administrations_models.TransactionTypes.objects.using(DataBase).get(TransactionTypesID=user_table.Sales_GST_Type, BranchID=1).Name
    purchase_gst_type = administrations_models.TransactionTypes.objects.using(DataBase).get(TransactionTypesID=user_table.Purchase_GST_Type, BranchID=1).Name
    vat_type = administrations_models.TransactionTypes.objects.using(DataBase).get(TransactionTypesID=user_table.VAT_Type, BranchID=1).Name
    user_type = administrations_models.UserType.objects.using(DataBase).get(ID=user_table.UserTypeID).UserTypeName
    context = {
        'instance' : instance,
        'title' : 'User',
        'user_table' : user_table,
        'cash_account' : cash_account,
        'bank_account' : bank_account,
        'sales_account' : sales_account,
        'purchase_account' : purchase_account,
        'warehouses' : warehouses,
        'sales_gst_type' : sales_gst_type,
        'purchase_gst_type' : purchase_gst_type,
        'vat_type' : vat_type,
        'user_type' : user_type,
        "sales_return" : sales_return,
        "purchase_return" : purchase_return,
    }
    return render(request,"administrations/masters/user.html",context)


@login_required
def edit_user(request,pk):
    from users.functions import get_auto_id


    DataBase = get_DataBase(request)
    cash_accounts = administrations_models.AccountLedger.objects.using(DataBase).filter(AccountGroupUnder=9)
    bank_accounts = administrations_models.AccountLedger.objects.using(DataBase).filter(AccountGroupUnder=8)
    sales_accounts = administrations_models.AccountLedger.objects.using(DataBase).filter(AccountGroupUnder=74)
    purchase_accounts = administrations_models.AccountLedger.objects.using(DataBase).filter(AccountGroupUnder=48)
    warehouses = administrations_models.Warehouse.objects.using(DataBase).all()
    
    sales_gst_types = administrations_models.TransactionTypes.objects.using(DataBase).filter(MasterTypeID=6, BranchID=1)
    purchase_gst_types = administrations_models.TransactionTypes.objects.using(DataBase).filter(MasterTypeID=7, BranchID=1)
    vat_types = administrations_models.TransactionTypes.objects.using(DataBase).filter(MasterTypeID=8, BranchID=1)
    user_types = administrations_models.UserType.objects.using(DataBase).all()
    DataBaseID = get_object_or_404(DatabaseStore.objects.filter(DefaultDatabase=DataBase))
    DataBaseID = DataBaseID.id
    instance = CustomerUser.objects.get(pk=pk)
    user_table = administrations_models.UserTable.objects.using(DataBase).filter(UserName=instance.username)
    if request.method == 'POST':
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
        form = UserForm(request.POST,instance=instance.user)
        if form.is_valid(): 
            data = form.save(commit=False)
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            message = ""  
            error = False

            existing_user = User.objects.exclude(username__in=[instance.username])
            if username in existing_user:
                error = True
                message += "This username already exists."

            if not error:
                branchid = 1
                id = get_auto_id(administrations_models.UserTable,branchid,DataBase)
                action = "A"
                employeeid = 1
                isactive = True
                createduserid = request.user.id
                createddate = datetime.date.today()

                user_table.update(
                    ID = id,
                    UserTypeID = UserTypeID,
                    BranchID = branchid,
                    Action = action,
                    UserName = username,
                    Password = password,
                    EmployeeID = employeeid,
                    IsActive = isactive,
                    CreatedUserID = createduserid,
                    CreatedDate = createddate,
                    Cash_Account = Cash_Account,
                    Bank_Account = Bank_Account,
                    Warehouse = warehouse,
                    Sales_Account = Sales_Account,
                    Sales_Return_Account = Sales_Return_Account,
                    Purchase_Account = Purchase_Account,
                    Purchase_Return_Account = Purchase_Return_Account,
                    Sales_GST_Type = Sales_GST_Type,
                    Purchase_GST_Type = Purchase_GST_Type,
                    VAT_Type = VAT_Type,
                    ExpiryDate = ExpiryDate,
                    )

                user_log_table = administrations_models.User_Log(
                    TransactionID = id,
                    UserTypeID = UserTypeID,
                    BranchID = branchid,
                    Action = action,
                    UserName = username,
                    Password = password,
                    EmployeeID = employeeid,
                    IsActive = isactive,
                    CreatedUserID = createduserid,
                    CreatedDate = createddate,
                    Cash_Account = Cash_Account,
                    Bank_Account = Bank_Account,
                    Warehouse = warehouse,
                    Sales_Account = Sales_Account,
                    Sales_Return_Account = Sales_Return_Account,
                    Purchase_Account = Purchase_Account,
                    Purchase_Return_Account = Purchase_Return_Account,
                    Sales_GST_Type = Sales_GST_Type,
                    Purchase_GST_Type = Purchase_GST_Type,
                    VAT_Type = VAT_Type,

                    )
                user_log_table.save(using=DataBase)
                data.save()
                customer_instance = CustomerUser.objects.filter(pk=pk)
                customer_instance.update(
                    databaseid = DataBaseID,
                    email = email,
                    username = username,
                    password = password,
                    user = data
                )  

            response_data = {
                "status" : "true",
                "title" : str(_("Successfully Updated")),
                "message" : str(_("User Updated Successfully!")),
                "redirect" : "true",
                "redirect_url" : reverse('administrations:view_user',kwargs={'pk':instance.pk})
            }
            
        else:
            message = generate_form_errors(form,formset=False)
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("Form validation error")),
                "message" : str(message)
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = UserForm(instance=instance.user)
        context = {
            "title" : "Edit User",
            "caption" : "Home",
            "form" : form,
            "cash_accounts" : cash_accounts,
            "bank_accounts" : bank_accounts,
            "sales_accounts" : sales_accounts,
            "purchase_accounts" : purchase_accounts,
            "warehouses" : warehouses,
            "sales_gst_types" : sales_gst_types,
            "purchase_gst_types" : purchase_gst_types,
            "vat_types" : vat_types,
            "user_types" : user_types,
        }
        return render(request,'administrations/masters/create_user.html',context)


@login_required
def delete_user(request,pk):
    from users.functions import get_auto_id

    DataBase = get_DataBase(request)
    today = datetime.date.today()    
    instance = CustomerUser.objects.get(pk=pk)
    DataBaseID = get_object_or_404(DatabaseStore.objects.filter(DefaultDatabase=DataBase))
    DataBaseID = DataBaseID.id
    first_user = CustomerUser.objects.filter(databaseid=DataBaseID).first()
    user_table = get_object_or_404(administrations_models.UserTable.objects.using(DataBase).filter(UserName=instance.username))
    if request.user == instance.user:
        response_data = {
            'status' : 'false',
            'stable' : 'true',
            'title' : str(_("Can't delete this User")),
            "message" : str(_("You are deleting your own credentials"))
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    elif pk == first_user.id:
        response_data = {
            'status' : 'false',
            'stable' : 'true',
            'title' : str(_("Can't delete this User")),
            "message" : str(_("Can't delete this User! this is default User!"))
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        User.objects.filter(username=instance.username).delete()
        instance.delete()

        administrations_models.User_Log.objects.using(DataBase).create(
            TransactionID = get_auto_id(administrations_models.UserTable ,user_table.BranchID ,DataBase),
            UserTypeID = user_table.UserTypeID,
            BranchID = user_table.BranchID,
            Action = user_table.Action,
            UserName = user_table.UserName,
            Password = user_table.Password,
            EmployeeID = user_table.EmployeeID,
            IsActive = user_table.IsActive,
            CreatedUserID = user_table.CreatedUserID,
            CreatedDate = user_table.CreatedDate,
            Cash_Account = user_table.Cash_Account,
            Bank_Account = user_table.Bank_Account,
            Warehouse = user_table.Warehouse,
            Sales_Account = user_table.Sales_Account,
            Sales_Return_Account = user_table.Sales_Return_Account,
            Purchase_Account = user_table.Purchase_Account,
            Purchase_Return_Account = user_table.Purchase_Return_Account,
            Sales_GST_Type = user_table.Sales_GST_Type,
            Purchase_GST_Type = user_table.Purchase_GST_Type,
            VAT_Type = user_table.VAT_Type,
            ExpiryDate = user_table.ExpiryDate
            )
        user_table.delete()

        response_data = {
            "status" : "true",
            "title" : str(_("Successfully Deleted")),
            "message" : str(_("User Deleted Successfully.")),
            "redirect" : "true",
            "redirect_url" : reverse('administrations:users')
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')


@login_required
def create_user_type(request):

    DataBase = get_DataBase(request)

    today = datetime.date.today()
    if request.method == 'POST':
        form = UserTypeForm(request.POST)
        if form.is_valid(): 
            data = form.save(commit=False)
            data.Action = "A"
            data.BranchID = 1
            data.CreatedUserID = request.user.id
            data.ID = get_auto_id_user_type(administrations_models.UserType,data.BranchID, DataBase)
            administrations_models.UserTypeLog.objects.using(DataBase).create(
                TransactionID = data.ID,
                UserTypeName = data.UserTypeName,
                BranchID = data.BranchID,
                Notes = data.Notes,
                CreatedUserID = data.CreatedUserID,
                CreatedDate = today,
                UpdatedDate = today,
                Action = data.Action,
                IsActive = data.IsActive,
                )
            data.save(using=DataBase)

            response_data = {
                "status" : "true",
                "title" : str(_("Successfully Created")),
                "message" : str(_("User Type Created Successfully!")),
                "redirect" : "true",
                "redirect_url" : reverse('administrations:user_types')
            }
        else:
            message = generate_form_errors(form,formset=False)
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("Form validation error")),
                "message" : str(message)
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = UserTypeForm()
        context = {
            "title" : "create User Type",
            "form" : form
        }
        return render(request,"administrations/masters/create_user_type.html",context)


@login_required
def user_types(request):
    DataBase = get_DataBase(request)
    instances = administrations_models.UserType.objects.using(DataBase).all()
    context = {
        'instances' : instances,
        'title' : 'User Type'
    }
    return render(request,"administrations/masters/user_types.html",context)


@login_required
def user_type(request,pk):
    DataBase = get_DataBase(request)
    instance = administrations_models.UserType.objects.using(DataBase).get(pk=pk)
    context = {
        'instance' : instance,
        'title' : 'User Type'
    }
    return render(request,"administrations/masters/user_type.html",context)


@login_required
def edit_user_type(request,pk):
    DataBase = get_DataBase(request)
    today = datetime.date.today()
    instance = administrations_models.UserType.objects.using(DataBase).get(pk=pk)
    if request.method == 'POST':
        form = UserTypeForm(request.POST,instance=instance)
        if form.is_valid(): 
            data = form.save(commit=False)
            data.Action = "M"
            data.UpdatedDate = today
            administrations_models.UserTypeLog.objects.using(DataBase).create(
                TransactionID = data.ID,
                UserTypeName = data.UserTypeName,
                BranchID = data.BranchID,
                Notes = data.Notes,
                CreatedUserID = data.CreatedUserID,
                CreatedDate = today,
                UpdatedDate = today,
                Action = data.Action,
                IsActive = data.IsActive,
                )
            data.save(using=DataBase)

            response_data = {
                "status" : "true",
                "title" : str(_("Successfully Updated")),
                "message" : str(_("User Type Updated Successfully!")),
                "redirect" : "true",
                "redirect_url" : reverse('administrations:user_type',kwargs={'pk':instance.pk})
            }
            
        else:
            message = generate_form_errors(form,formset=False)
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("Form validation error")),
                "message" : str(message)
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = UserTypeForm(instance=instance)
        context = {
            "title" : "Edit User Type",
            "form" : form
        }
        return render(request,"administrations/masters/create_user_type.html",context)


@login_required
def delete_user_type(request,pk):
    DataBase = get_DataBase(request)
    today = today = datetime.date.today()
    instance = administrations_models.UserType.objects.using(DataBase).get(pk=pk)

    if pk == "1" and pk == "2":
        response_data = {
            'status' : 'false',
            'stable' : 'true',
            'title' : str(_("can't delete this User Type")),
            "message" : str(_("Can't delete this User Type! this is default User Type!"))
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        administrations_models.UserTypeLog.objects.using(DataBase).create(
            TransactionID = instance.ID,
            UserTypeName = instance.UserTypeName,
            BranchID = instance.BranchID,
            Notes = instance.Notes,
            CreatedUserID = instance.CreatedUserID,
            CreatedDate = today,
            UpdatedDate = today,
            Action = 'M',
            IsActive = instance.IsActive,
            )
        instance.delete()
        
        response_data = {
            "status" : "true",
            "title" : str(_("Successfully Deleted")),
            "message" : str(_("User Type Deleted Successfully.")),
            "redirect" : "true",
            "redirect_url" : reverse('administrations:user_types')
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
# UserType ends


@login_required
def create_financial_year(request):

    DataBase = get_DataBase(request)

    today = datetime.date.today()
    if request.method == 'POST':
        instances = administrations_models.FinancialYear.objects.using(DataBase).filter(IsClosed=True)
        form = FinancialYearForm(request.POST)
        if not administrations_models.FinancialYear.objects.using(DataBase).filter(IsClosed=False).exists():

            if form.is_valid(): 
                FromDate = form.cleaned_data['FromDate']
                ToDate = form.cleaned_data['ToDate']
                days = ToDate - FromDate
                days = str(days).split(' ')

                test = administrations_models.FinancialYear.objects.using(DataBase).filter(IsClosed=True)
                date_arr = []
                for i in test:
                    date_form = i.FromDate
                    date_to = i.ToDate
                    # database date filter
                    start = datetime.datetime.strptime(str(date_form), "%Y-%m-%d")
                    end = datetime.datetime.strptime(str(date_to), "%Y-%m-%d")
                    date_array = \
                        (start + datetime.timedelta(days=x) for x in range(0, (end-start).days))

                    for date_object in date_array:
                        date = date_object.strftime("%Y-%m-%d")
                        date_arr.append(date)
                if str(FromDate) in date_arr or str(ToDate) in date_arr:
                    response_data = {
                    "status" : "false",
                    "stable" : "true",
                    "title" : "Financial Year",
                    "message" : str('This Financial Year is Alredy Exists')
                    }  
                    return HttpResponse(json.dumps(response_data), content_type='application/javascript')
                else:
                    # cheking minimum 1year
                    if  days[0] == '364' or days[0] == '365':
                            
                        data = form.save(commit=False)
                        data.Action = 'A'
                        data.CreatedUserID = request.user.id
                        auto_id = get_auto_id_financial_year(administrations_models.FinancialYear, DataBase)
                        data.FinancialYearID = auto_id
                        data.CreatedDate = today
                        data.UpdatedDate = today
                        data.save(using=DataBase)    


                        administrations_models.FinancialYear_Log.objects.using(DataBase).create(
                            TransactionID = data.FinancialYearID,
                            Action = data.Action,
                            FromDate = data.FromDate,
                            ToDate = data.ToDate,
                            IsClosed = data.IsClosed,
                            Notes = data.Notes,
                            CreatedDate = data.CreatedDate,
                            UpdatedDate = data.UpdatedDate,
                            CreatedUserID = data.CreatedUserID,
                            )
                        response_data = {
                            "status" : "true",
                            "title" : str(_("Successfully Created")),
                            "message" : str(_("Financial Year created successfully")),
                            "redirect" : "true",
                            "redirect_url" : reverse('administrations:financial_years')
                        }   
                    else:
                        response_data = {
                            "status" : "false",
                            "stable" : "true",
                            "title" : "Date Exists",
                            "message" : str('Financial Year Must Have 1 Year')
                        }  
                        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
                
            else:    
                print(form.errors)
                print("////////////////////////////////")        
                message = generate_form_errors_new(form,formset=False)     
                        
                response_data = {
                    "status" : "false",
                    "stable" : "true",
                    "title" : "Form validation error",
                    "message" : str(message)
                }   
            
            return HttpResponse(json.dumps(response_data), content_type='application/javascript')
        else:
            response_data = {
                    "status" : "false",
                    "stable" : "true",
                    "title" : "Financial Year",
                    "message" : str('Current Financial Year is not Closed')
                }   
            
            return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = FinancialYearForm()
        context = {
            "title" : "Create Financial Year",
            "form" : form
        }
        return render(request,"administrations/masters/create_financial_year.html",context)


@login_required
def financial_years(request):
    DataBase = get_DataBase(request)
    instances = administrations_models.FinancialYear.objects.using(DataBase).all()
    context = {
        'instances' : instances,
        'title' : 'Financial'
    }
    return render(request,"administrations/masters/financial_years.html",context)


@login_required
def financial_year(request,pk):
    DataBase = get_DataBase(request)
    instance = administrations_models.FinancialYear.objects.using(DataBase).get(pk=pk)
    context = {
        'instance' : instance,
        'title' : 'Financial'
    }
    return render(request,"administrations/masters/financial_year.html",context)


@login_required
def edit_financial_year(request,pk):
    DataBase = get_DataBase(request)
    today = datetime.date.today()
    instance = administrations_models.FinancialYear.objects.using(DataBase).get(pk=pk)
    if request.method == 'POST':
        form = FinancialYearForm(request.POST,instance=instance)
        if form.is_valid(): 
            data = form.save(commit=False)
            data.Action = "M"
            data.UpdatedDate = today
            administrations_models.FinancialYear_Log.objects.using(DataBase).create(
                TransactionID = data.FinancialYearID,
                Action = data.Action,
                FromDate = data.FromDate,
                ToDate = data.ToDate,
                IsClosed = data.IsClosed,
                Notes = data.Notes,
                CreatedDate = data.CreatedDate,
                UpdatedDate = data.UpdatedDate,
                CreatedUserID = data.CreatedUserID,
                )
            data.save(using=DataBase)

            response_data = {
                "status" : "true",
                "title" : str(_("Successfully Updated")),
                "message" : str(_("Financial Year Updated Successfully!")),
                "redirect" : "true",
                "redirect_url" : reverse('administrations:financial_year',kwargs={'pk':instance.pk})
            }
            
        else:
            message = generate_form_errors(form,formset=False)
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("Form validation error")),
                "message" : str(message)
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = FinancialYearForm(instance=instance)
        context = {
            "title" : "Edit Financial Year",
            "form" : form,
            "is_edit" : True,
        }
        return render(request,"administrations/masters/create_financial_year.html",context)


@login_required
def delete_financial_year(request,pk):
    DataBase = get_DataBase(request)
    today = today = datetime.date.today()
    instance = administrations_models.FinancialYear.objects.using(DataBase).get(pk=pk)

    if pk == "1" and pk == "2":
        response_data = {
            'status' : 'false',
            'stable' : 'true',
            'title' : str(_("can't delete this Financial Year")),
            "message" : str(_("Can't delete this Financial! this is default Financial!"))
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        administrations_models.FinancialYear_Log.objects.using(DataBase).create(
            TransactionID = instance.FinancialYearID,
            Action = instance.Action,
            FromDate = instance.FromDate,
            ToDate = instance.ToDate,
            IsClosed = instance.IsClosed,
            Notes = instance.Notes,
            CreatedDate = instance.CreatedDate,
            UpdatedDate = today,
            CreatedUserID = instance.CreatedUserID,
            )
        instance.delete()
        
        response_data = {
            "status" : "true",
            "title" : str(_("Successfully Deleted")),
            "message" : str(_("Financial Deleted Successfully.")),
            "redirect" : "true",
            "redirect_url" : reverse('administrations:financial_years')
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
# FinancialYear ends

@login_required
def update_company_settings(request,pk):
    DataBase = get_DataBase(request)
    today = datetime.date.today()
    instance = DatabaseStore.objects.get(pk=pk)
    if request.method == 'POST':
        form = DatabaseStoreForm(request.POST,instance=instance)
        if form.is_valid(): 
            data = form.save(commit=False)
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


            data.DefaultDatabase = instance.DefaultDatabase
            data.DatabaseName = instance.DatabaseName
            data.CompanyName = CompanyName
            data.Address1 = Address1
            data.Address2 = Address2
            data.Address3 = Address3
            data.username = instance.username
            data.password = instance.password
            data.city = city
            data.state = state
            data.country = country
            data.postalcode = postalcode
            data.phone = phone
            data.mobile = mobile
            data.email = email
            data.website = website
            data.currency = currency
            data.fractionalunit = fractionalunit
            data.vatnumber = vatnumber
            data.gstnumber = gstnumber
            data.tax1 = tax1
            data.tax2 = tax2
            data.tax3 = tax3
            data.customerid = customerid
            data.CreatedDate = instance.CreatedDate
            data.host = instance.host
            data.port = instance.port
            data.is_process = instance.is_process
            data.is_employee = instance.is_employee
            data.is_financial_year = instance.is_financial_year

            data.save()

            response_data = {
                "status" : "true",
                "title" : str(_("Successfully Updated")),
                "message" : str(_("Company Updated Successfully!")),
                "redirect" : "false",
            }
            
        else:
            message = generate_form_errors(form,formset=False)
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("Form validation error")),
                "message" : str(message)
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = DatabaseStoreForm(instance=instance)
        context = {
            "title" : "Update Company Settings",
            "form" : form
        }
        return render(request,"administrations/masters/create_company_settings.html",context)