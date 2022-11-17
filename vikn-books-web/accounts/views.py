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
from brands.models import Brand, AccountGroup, Branch, Brand_Log, Branch_Log, AccountLedger, AccountLedger_Log, LedgerPosting, LedgerPosting_Log,\
 Parties, Parties_Log, PurchaseOrderMaster, SalesOrderMaster, Employee, Bank, Bank_Log, AccountGroup_Log, Country, TransactionTypes, TransactionTypes_Log,\
 PaymentMaster, PaymentMaster_Log, PaymentDetails, PaymentDetails_Log, ReceiptMaster, ReceiptMaster_Log, ReceiptDetails, ReceiptDetails_Log, JournalMaster,\
 JournalMaster_Log, JournalDetails, JournalDetails_Log

from accounts.forms import AccountLedgerForm, BranchForm, BankForm, AccountGroupForm, CustomerForm, TransactionTypesForm, PaymentDetailsForm, \
PaymentMasterForm,ReceiptMasterForm ,ReceiptDetailsForm, JournalMasterForm, JournalDetailsForm
from accounts.functions import generate_form_errors,get_auto_id, get_auto_Branchid, get_auto_LedgerID, get_auto_EmployeeID, get_auto_AccountGroupID,\
get_auto_partyID
from django.forms.models import inlineformset_factory, formset_factory
from api.v1.accountLedgers.functions import get_LedgerCode, get_auto_LedgerPostid, get_auto_idfor_party
from api.v1.banks.functions import get_auto_Bankid
from django.utils.translation import gettext_lazy as _
from users.models import DatabaseStore, CustomerUser
from django.contrib.auth.decorators import login_required
from api.v1.parties.functions import get_auto_idLedger, get_PartyCode
from django.forms.widgets import TextInput, Textarea, FileInput, Select, RadioSelect, DateInput, CheckboxInput
from accounts.functions import check_groupforProfitandLoss, get_GroupCode, get_auto_TransactionTypesID, generateVoucherNo, get_base64_file
import datetime
import base64
from django.core.files.base import ContentFile
from main.functions import get_DataBase


@login_required
def create_accountGroup(request):
    DataBase = get_DataBase(request)
    today = datetime.date.today()

    if request.method == 'POST':
        form = AccountGroupForm(request.POST)
        AccountGroupUnder = request.POST.get('AccountGroupUnder')

        if form.is_valid(): 
            data = form.save(commit=False)

            is_nameExist = False
            AccountGroupNameLow = data.AccountGroupName.lower()
            groups = AccountGroup.objects.using(DataBase).all()

            for group in groups:
                group_name = group.AccountGroupName
                AccountGroupName = group_name.lower()

                if AccountGroupNameLow == AccountGroupName:
                    is_nameExist = True

            if not is_nameExist:
                data.CreatedDate = today
                data.UpdatedDate=today
                data.Action = "A"
                data.CreatedUserID = user.id
                data.AccountGroupUnder = AccountGroupUnder
                data.AccountGroupID = get_auto_AccountGroupID(AccountGroup,DataBase)

                AccountGroup_Log.objects.using(DataBase).create(
                    AccountGroupName=data.AccountGroupName,
                    TransactionID=data.AccountGroupID,
                    GroupCode=data.GroupCode,
                    AccountGroupUnder=data.AccountGroupUnder,
                    Notes=data.Notes,
                    CreatedUserID=data.CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    IsActive=data.IsActive,
                    IsDefault=data.IsDefault,
                    Action="A",
                    )

                data.save(using=DataBase)

                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("AccountGroup Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('accounts:account_groups')
                }
            else:
                response_data = {
                    "status" : "false",
                    "title" : str(_("AccountGroup Already Exist")),
                    "message" : str(_("AccountGroup Name is Already exist with in the BranchID")),
                    "redirect" : "true",
                    "redirect_url" : reverse('accounts:create_accountGroup')
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
        GroupCode = get_GroupCode(AccountGroup,DataBase)
        accountGroups = AccountGroup.objects.all()
        form = AccountGroupForm(initial={ 'GroupCode' : GroupCode})
        context = {
            "is_need_flatpickr" : False,
            "is_need_apexcharts" : False,
            "is_need_selectize" : False,
            "is_need_dashboard" : False,

            "title" : "Create Account Group",
            "form" : form,
            "accountGroups" : accountGroups
        }
        return render(request,"accounts/master/create_account_group.html",context)


@login_required
def edit_accountGroup(request,pk):
    DataBase = get_DataBase(request)

    today = datetime.date.today()
    instance = AccountGroup.objects.using(DataBase).get(pk=pk)
    AccountGroupID = instance.AccountGroupID
    GroupCode = instance.GroupCode
    instanceAccountGroupName = instance.AccountGroupName

    if request.method == 'POST':
        form = AccountGroupForm(request.POST,instance=instance)
        AccountGroupUnder = request.POST.get('AccountGroupUnder')

        if form.is_valid(): 
            data = form.save(commit=False)
            AccountGroupName = data.AccountGroupName
            is_nameExist = False
            ledger_ok = False

            is_nameExist = False
            AccountGroupNameLow = data.AccountGroupName.lower()
            groups = AccountGroup.objects.using(DataBase).all()

            for group in groups:
                group_name = group.AccountGroupName
                AccountGroupName = group_name.lower()

                if AccountGroupNameLow == AccountGroupName:
                    is_nameExist = True

                if instanceAccountGroupName.lower() == AccountGroupNameLow:
                    ledger_ok = True

            if ledger_ok:
                data.UpdatedDate=today
                data.Action = "M"
                data.CreatedUserID = user.id
                data.AccountGroupUnder = AccountGroupUnder

                AccountGroup_Log.objects.using(DataBase).create(
                    AccountGroupName=data.AccountGroupName,
                    TransactionID=AccountGroupID,
                    GroupCode=GroupCode,
                    AccountGroupUnder=data.AccountGroupUnder,
                    Notes=data.Notes,
                    CreatedUserID=data.CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    IsActive=data.IsActive,
                    IsDefault=data.IsDefault,
                    Action="M",
                    )

                data.save(using=DataBase)

                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Updated")),
                    "message" : str(_("AccountGroup Updated Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('accounts:account_groups')
                }

            else:
                if is_nameExist:
                    response_data = {
                        "status" : "false",
                        "title" : str(_("AccountGroup Already Exist")),
                        "message" : str(_("AccountGroup Name is Already exist with in the BranchID")),
                        "redirect" : "true",
                        "redirect_url" : reverse('accounts:edit_accountGroup',kwargs={'pk:instance.pk'})
                    }
                else:
                    data.UpdatedDate=today
                    data.Action = "M"
                    data.CreatedUserID = user.id
                    data.AccountGroupUnder = AccountGroupUnder

                    AccountGroup_Log.objects.using(DataBase).create(
                        AccountGroupName=data.AccountGroupName,
                        TransactionID=AccountGroupID,
                        GroupCode=GroupCode,
                        AccountGroupUnder=data.AccountGroupUnder,
                        Notes=data.Notes,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        IsActive=data.IsActive,
                        IsDefault=data.IsDefault,
                        Action="M",
                        )

                    data.save(using=DataBase)

                    response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Updated")),
                    "message" : str(_("AccountGroup Updated Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('accounts:account_groups')
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
        GroupCode = get_GroupCode(AccountGroup,DataBase)
        accountGroups = AccountGroup.objects.all()
        form = AccountGroupForm(instance=instance)
        context = {
            "is_need_flatpickr" : False,
            "is_need_apexcharts" : False,
            "is_need_selectize" : False,
            "is_need_dashboard" : False,
            "is_edit" : True,

            "title" : "Edit Account Group",
            "form" : form,
            "instance" : instance,
            "accountGroups" : accountGroups
        }
        return render(request,"accounts/master/create_account_group.html",context)


@login_required
def account_groups(request):
    DataBase = get_DataBase(request)
    instances = AccountGroup.objects.using(DataBase).all()
    query = request.GET.get("q")
    if query:
        instances = instances.filter(Q(AccountGroupName__icontains=query) | Q(GroupCode__icontains=query) | Q(AccountGroupUnder__icontains=query) | Q(Notes__icontains=query) | Q(CreatedDate__icontains=query))
    context = {
        "is_need_flatpickr" : False,
        "is_need_apexcharts" : False,
        "is_need_selectize" : False,
        "is_need_dashboard" : False,

        'instances' : instances,
        'title' : 'Account Groups'
    }
    return render(request,"accounts/master/account_groups.html",context)


@login_required
def view_accountGroup(request,pk):
    DataBase = get_DataBase(request)

    instance = AccountGroup.objects.using(DataBase).get(pk=pk)
    context = {
        "is_need_flatpickr" : False,
        "is_need_apexcharts" : False,
        "is_need_selectize" : False,
        "is_need_dashboard" : False,

        'instance' : instance,
        'title' : 'AccountGroup'
    }
    return render(request,"accounts/master/account_group.html",context)


@login_required
def delete_accountGroup(request,pk):
    DataBase = get_DataBase(request)

    today = datetime.date.today()    
    instance = AccountGroup.objects.using(DataBase).get(pk=pk)

    AccountGroup_Log.objects.using(DataBase).create(
        AccountGroupName=instance.AccountGroupName,
        TransactionID=instance.AccountGroupID,
        GroupCode=instance.GroupCode,
        AccountGroupUnder=instance.AccountGroupUnder,
        Notes=instance.Notes,
        CreatedUserID=user.id,
        CreatedDate=today,
        UpdatedDate=today,
        IsActive=instance.IsActive,
        IsDefault=instance.IsDefault,
        Action="A",
        )
    instance.delete()
    
    response_data = {
        "status" : "true",
        "title" : str(_("Successfully Deleted")),
        "message" : str(_("AccountGroup Deleted Successfully.")),
        "redirect" : "true",
        "redirect_url" : reverse('accounts:account_groups')
    }
    return HttpResponse(json.dumps(response_data), content_type='application/javascript')


@login_required
def create_accountLedger(request):
    DataBase = get_DataBase(request)

    today = datetime.date.today()
    if request.method == 'POST':
        form = AccountLedgerForm(request.POST)
        account_group = request.POST.get('account_group')
        CrOrDr = request.POST.get('crOdr')
        if form.is_valid(): 
            data = form.save(commit=False)
            LedgerName = data.LedgerName

            is_nameExist = False
            LedgerNameLow = LedgerName.lower()
            ledgers = AccountLedger.objects.using(DataBase).filter(BranchID=1)

            for ledger in ledgers:
                ledger_name = ledger.LedgerName
                LedgerName = ledger_name.lower()

                if LedgerNameLow == LedgerName:
                    is_nameExist = True

            if not is_nameExist:
                data.CreatedDate = today
                data.UpdatedDate=today
                data.Action = "A"
                data.BranchID = 1
                data.AccountGroupUnder = account_group
                data.CrOrDr = CrOrDr
                data.CreatedUserID = 1
                data.LedgerID = get_auto_LedgerID(AccountLedger,data.BranchID,DataBase)
                data.LedgerCode = get_LedgerCode(AccountLedger, data.BranchID,DataBase)
                AccountLedger_Log.objects.using(DataBase).create(
                    BranchID=data.BranchID,
                    TransactionID=data.LedgerID,
                    LedgerName=data.LedgerName,
                    LedgerCode=data.LedgerCode,
                    AccountGroupUnder=account_group,
                    OpeningBalance=data.OpeningBalance,
                    CrOrDr=CrOrDr,
                    Notes=data.Notes,
                    IsActive=data.IsActive,
                    IsDefault=data.IsDefault,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action="A",
                    CreatedUserID=1,
                    )

                if float(data.OpeningBalance) > 0:
                    Credit = 0.00
                    Debit = 0.00

                    if CrOrDr == "Cr":
                        Credit = data.OpeningBalance

                    elif CrOrDr == "Dr":
                        Debit = data.OpeningBalance

                    VoucherType = "LOB"

                    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,data.BranchID)

                    LedgerPosting.objects.using(DataBase).create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=today,
                        VoucherMasterID=data.LedgerID,
                        VoucherType=VoucherType,
                        LedgerID=data.LedgerID,
                        Debit=Debit,
                        Credit=Credit,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=1,
                        CreatedDate=today,
                        UpdatedDate=today,
                        )

                    LedgerPosting_Log.objects.using(DataBase).create(
                        TransactionID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=today,
                        VoucherMasterID=data.LedgerID,
                        VoucherType=VoucherType,
                        LedgerID=data.LedgerID,
                        Debit=Debit,
                        Credit=Credit,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=1,
                        CreatedDate=today,
                        UpdatedDate=today,
                        )

                if account_group == "10" or account_group == "29":
                    PartyName = data.LedgerName
                    if account_group == "10":
                        PartyType = "customer"


                    elif account_group == "29":
                        PartyType = "supplier"

                    PartyID = get_auto_idfor_party(Parties,data.BranchID)
                    PartyCode = data.LedgerCode

                    Parties.objects.using(DataBase).create(
                        PartyID=PartyID,
                        BranchID=data.BranchID,
                        PartyType=PartyType,
                        LedgerID=data.LedgerID,
                        PartyCode=PartyCode,
                        PartyName=PartyName,
                        PriceCategoryID=1,
                        RouteID=1,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        OpeningBalance=data.OpeningBalance,
                        )

                    Parties_Log.objects.using(DataBase).create(
                        TransactionID=PartyID,
                        BranchID=data.BranchID,
                        PartyType=PartyType,
                        LedgerID=data.LedgerID,
                        PartyCode=PartyCode,
                        PartyName=PartyName,
                        PriceCategoryID=1,
                        RouteID=1,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        OpeningBalance=data.OpeningBalance,
                        )
                elif account_group == "8":
                
                    BankID = get_auto_Bankid(Bank,BranchID)

                    Bank.objects.using(DataBase).create(
                        BankID=BankID,
                        BranchID=data.BranchID,
                        LedgerCode=data.LedgerCode,
                        Name=data.LedgerName,
                        LedgerName=data.LedgerName,
                        CrOrDr=CrOrDr,
                        OpeningBalance=data.OpeningBalance,
                        Notes=data.Notes,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        Action=data.Action,
                        )

                    Bank_Log.objects.using(DataBase).create(
                        TransactionID=BankID,
                        BranchID=data.BranchID,
                        LedgerCode=data.LedgerCode,
                        Name=data.LedgerName,
                        LedgerName=data.LedgerName,
                        CrOrDr=CrOrDr,
                        OpeningBalance=data.OpeningBalance,
                        Notes=data.Notes,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        Action=data.Action,
                        )

                elif account_group == "32":
                
                    EmployeeID = get_auto_EmployeeID(Employee,data.BranchID)

                    Employee.objects.using(DataBase).create(
                        EmployeeID=EmployeeID,
                        BranchID=data.BranchID,
                        EmployeeCode=data.LedgerCode,
                        EmployeeName=data.LedgerName,
                        LedgerID=data.LedgerID,
                        DateOfJoining=today,
                        Notes=data.Notes,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        )

                    Employee_Log.objects.using(DataBase).create(
                        TransactionID=EmployeeID,
                        BranchID=data.BranchID,
                        EmployeeCode=data.LedgerCode,
                        EmployeeName=data.LedgerName,
                        LedgerID=data.LedgerID,
                        DateOfJoining=today,
                        Notes=data.Notes,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        )

                data.save()

                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("AccountLedger Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('accounts:accountLedgers')
                }
            else:
                response_data = {
                    "status" : "false",
                    "title" : str(_("AccountLedger Already Exist")),
                    "message" : str(_("AccountLedger Name is Already exist with in the BranchID")),
                    "redirect" : "true",
                    "redirect_url" : reverse('accounts:create_accountLedger')
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
        form = AccountLedgerForm()
        lst = [1, 2, 3]
        accountGroups = AccountGroup.objects.using(DataBase).all().exclude(pk__in=lst)
        context = {
            "is_need_flatpickr" : False,
            "is_need_apexcharts" : False,
            "is_need_selectize" : False,
            "is_need_dashboard" : False,

            "title" : "Create Account Ledger",
            "form" : form,
            "accountGroups" : accountGroups
        }
        return render(request,"accounts/master/create_account_ledger.html",context)


@login_required
def accountLedgers(request):

    instances = AccountLedger.objects.using(DataBase).all()
    context = {
        "is_need_flatpickr" : False,
        "is_need_apexcharts" : False,
        "is_need_selectize" : False,
        "is_need_dashboard" : False,

        'instances' : instances,
        'title' : 'Account Ledgers'
    }
    return render(request,"accounts/master/account_ledgers.html",context)


@login_required
def view_accountLedger(request,pk):
    DataBase = get_DataBase(request)

    instance = AccountLedger.objects.using(DataBase).get(pk=pk)
    context = {
        "is_need_flatpickr" : False,
        "is_need_apexcharts" : False,
        "is_need_selectize" : False,
        "is_need_dashboard" : False,

        'instance' : instance,
        'title' : 'Ledger'
    }
    return render(request,"accounts/master/account_ledger.html",context)


@login_required
def edit_accountLedger(request,pk):
    DataBase = get_DataBase(request)

    today = datetime.date.today()
    instance = AccountLedger.objects.using(DataBase).get(pk=pk)
    instanceLedgerName = instance.LedgerName
    LedgerID = instance.LedgerID
    LedgerCode = instance.LedgerCode
    if request.method == 'POST':
        form = AccountLedgerForm(request.POST,instance=instance)
        account_group = request.POST.get('account_group')
        CrOrDr = request.POST.get('crOdr')
        if form.is_valid():
            data = form.save(commit=False)
            LedgerName = data.LedgerName
            is_nameExist = False
            ledger_ok = False

            LedgerNameLow = LedgerName.lower()

            ledegrs = AccountLedger.objects.using(DataBase).filter(BranchID=1)

            for ledger in ledegrs:
                ledger_name = ledger.LedgerName

                ledgerName = ledger_name.lower()

                if LedgerNameLow == ledgerName:
                    is_nameExist = True

                if instanceLedgerName.lower() == LedgerNameLow:
                    ledger_ok = True
            if ledger_ok:
                data.UpdatedDate=today
                data.Action = "M"
                data.BranchID = 1
                data.AccountGroupUnder = account_group
                data.CrOrDr = CrOrDr
                data.CreatedUserID = 1
                AccountLedger_Log.objects.using(DataBase).create(
                    BranchID=data.BranchID,
                    TransactionID=LedgerID,
                    LedgerName=data.LedgerName,
                    LedgerCode=LedgerCode,
                    AccountGroupUnder=account_group,
                    OpeningBalance=data.OpeningBalance,
                    CrOrDr=CrOrDr,
                    Notes=data.Notes,
                    IsActive=data.IsActive,
                    IsDefault=data.IsDefault,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action="M",
                    CreatedUserID=1,
                    )

                if float(data.OpeningBalance) > 0:
                    Credit = 0.00
                    Debit = 0.00

                    if CrOrDr == "Cr":
                        Credit = data.OpeningBalance

                    elif CrOrDr == "Dr":
                        Debit = data.OpeningBalance

                    VoucherType = "LOB"

                    if LedgerPosting.objects.using(DataBase).filter(LedgerID=data.LedgerID,BranchID=data.BranchID,VoucherMasterID=data.LedgerID,VoucherType="LOB").exists():
                        ledgerPostInstance = LedgerPosting.objects.get(LedgerID=data.LedgerID,BranchID=data.BranchID,VoucherMasterID=data.LedgerID,VoucherType="LOB")
                        ledgerPostInstance.Date = today
                        ledgerPostInstance.Debit = Debit
                        ledgerPostInstance.Credit = Credit
                        ledgerPostInstance.Action = "M"
                        ledgerPostInstance.CreatedDate = today
                        ledgerPostInstance.UpdatedDate = today
                        ledgerPostInstance.save()

                        LedgerPosting_Log.objects.using(DataBase).create(
                            TransactionID=ledgerPostInstance.LedgerPostingID,
                            BranchID=data.BranchID,
                            Date=today,
                            VoucherMasterID=data.LedgerID,
                            VoucherType=VoucherType,
                            LedgerID=data.LedgerID,
                            Debit=Debit,
                            Credit=Credit,
                            Action=data.Action,
                            CreatedUserID=data.CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            )
                else:
                    if LedgerPosting.objects.using(DataBase).filter(LedgerID=data.LedgerID,BranchID=data.BranchID,VoucherMasterID=data.LedgerID,VoucherType="LOB").exists():
                        ledgerPostInstance = LedgerPosting.objects.get(LedgerID=data.LedgerID,BranchID=data.BranchID,VoucherMasterID=data.LedgerID,VoucherType="LOB")
                        ledgerPostInstance.Date = today
                        ledgerPostInstance.Debit = Debit
                        ledgerPostInstance.Credit = Credit
                        ledgerPostInstance.Action = "D"
                        ledgerPostInstance.CreatedDate = today
                        ledgerPostInstance.delete()

                if account_group == "10" or account_group == "29":

                    PartyName = LedgerName
                    if account_group == "10":
                        PartyType = "customer"


                    elif account_group == "29":
                        PartyType = "supplier"

                    PartyCode = LedgerCode

                    if Parties.objects.using(DataBase).filter(BranchID=data.BranchID,LedgerID=data.LedgerID,PartyType=PartyType).exists():
                        partyInstance = Parties.objects.get(BranchID=data.BranchID,LedgerID=data.LedgerID,PartyType=PartyType)
                        partyInstance.PartyName = PartyName
                        partyInstance.Action = "M"
                        partyInstance.CreatedDate = today
                        partyInstance.OpeningBalance = data.OpeningBalance
                        partyInstance.save(using=DataBase)

                        Parties_Log.objects.using(DataBase).create(
                            TransactionID=partyInstance.PartyID,
                            BranchID=data.BranchID,
                            PartyType=PartyType,
                            LedgerID=data.LedgerID,
                            PartyCode=PartyCode,
                            PartyName=PartyName,
                            PriceCategoryID=1,
                            RouteID=1,
                            IsActive=data.IsActive,
                            Action="M",
                            CreatedUserID=data.CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            OpeningBalance=data.OpeningBalance,
                            )

                elif account_group == "8":
                
                    if Bank.objects.using(DataBase).filter(BranchID=data.BranchID,LedgerCode=LedgerCode).exists():
                        bankInstance = Bank.objects.get(BranchID=data.BranchID,LedgerCode=LedgerCode)
                        bankInstance.Name = data.LedgerName
                        bankInstance.LedgerName = data.LedgerName
                        bankInstance.CrOrDr = CrOrDr
                        bankInstance.OpeningBalance = data.OpeningBalance
                        bankInstance.Notes = data.Notes
                        bankInstance.CreatedDate = today
                        bankInstance.Action = "M"
                        bankInstance.save(using=DataBase)

                        Bank_Log.objects.using(DataBase).create(
                            TransactionID=bankInstance.BankID,
                            BranchID=data.BranchID,
                            LedgerCode=LedgerCode,
                            Name=data.LedgerName,
                            LedgerName=data.LedgerName,
                            CrOrDr=CrOrDr,
                            OpeningBalance=data.OpeningBalance,
                            Notes=data.Notes,
                            CreatedUserID=data.CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            Action=data.Action,
                            )

                elif account_group == "32":
                
                    if Employee.objects.using(DataBase).filter(BranchID=data.BranchID,LedgerID=data.LedgerID,EmployeeCode=LedgerCode).exists():
                        employeeInstance = Employee.objects.get(BranchID=data.BranchID,LedgerID=data.LedgerID,EmployeeCode=LedgerCode)
                        employeeInstance.EmployeeName = data.LedgerName
                        employeeInstance.Notes = data.Notes
                        employeeInstance.Action = "M"
                        employeeInstance.CreatedDate = today
                        employeeInstance.save()

                        Employee_Log.objects.using(DataBase).create(
                            TransactionID=employeeInstance.EmployeeID,
                            BranchID=data.BranchID,
                            EmployeeCode=LedgerCode,
                            EmployeeName=data.LedgerName,
                            LedgerID=data.LedgerID,
                            DateOfJoining=today,
                            Notes=data.Notes,
                            Action=data.Action,
                            CreatedUserID=data.CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            )
                data.save(using=DataBase)

                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("AccountLedger Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('accountLedgers:accountLedgers')
                }
            else:
                if is_nameExist:
                    response_data = {
                        "status" : "false",
                        "title" : str(_("AccountLedger Already Exist")),
                        "message" : str(_("AccountLedger Name is Already exist with in the BranchID")),
                        "redirect" : "true",
                        "redirect_url" : reverse('accountLedgers:create_brand')
                    }
                else:
                    data.CreatedDate = today
                    data.UpdatedDate=today
                    data.Action = "M"
                    data.BranchID = 1
                    data.account_group = account_group
                    data.CrOrDr = CrOrDr
                    data.CreatedUserID = 1
                    AccountLedger_Log.objects.using(DataBase).create(
                        BranchID=data.BranchID,
                        TransactionID=LedgerID,
                        LedgerName=data.LedgerName,
                        LedgerCode=LedgerCode,
                        account_group=account_group,
                        OpeningBalance=data.OpeningBalance,
                        CrOrDr=CrOrDr,
                        Notes=data.Notes,
                        IsActive=data.IsActive,
                        IsDefault=data.IsDefault,
                        CreatedDate=today,
                        UpdatedDate=today,
                        Action="M",
                        CreatedUserID=1,
                        )

                    if float(data.OpeningBalance) > 0:
                        Credit = 0.00
                        Debit = 0.00

                        if CrOrDr == "Cr":
                            Credit = data.OpeningBalance

                        elif CrOrDr == "Dr":
                            Debit = data.OpeningBalance

                        VoucherType = "LOB"

                        if LedgerPosting.objects.using(DataBase).filter(LedgerID=data.LedgerID,BranchID=data.BranchID,VoucherMasterID=data.LedgerID,VoucherType="LOB").exists():
                            ledgerPostInstance = LedgerPosting.objects.get(LedgerID=data.LedgerID,BranchID=data.BranchID,VoucherMasterID=data.LedgerID,VoucherType="LOB")
                            ledgerPostInstance.Date = today
                            ledgerPostInstance.Debit = Debit
                            ledgerPostInstance.Credit = Credit
                            ledgerPostInstance.Action = "M"
                            ledgerPostInstance.CreatedDate = today
                            ledgerPostInstance.save(using=DataBase)

                            LedgerPosting_Log.objects.using(DataBase).create(
                                TransactionID=ledgerPostInstance.LedgerPostingID,
                                BranchID=data.BranchID,
                                Date=today,
                                VoucherMasterID=data.LedgerID,
                                VoucherType=VoucherType,
                                LedgerID=data.LedgerID,
                                Debit=Debit,
                                Credit=Credit,
                                Action=data.Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                )
                    else:
                        if LedgerPosting.objects.using(DataBase).filter(LedgerID=data.LedgerID,BranchID=data.BranchID,VoucherMasterID=data.LedgerID,VoucherType="LOB").exists():
                            ledgerPostInstance = LedgerPosting.objects.using(DataBase).get(LedgerID=data.LedgerID,BranchID=data.BranchID,VoucherMasterID=data.LedgerID,VoucherType="LOB")
                            ledgerPostInstance.Date = today
                            ledgerPostInstance.Debit = Debit
                            ledgerPostInstance.Credit = Credit
                            ledgerPostInstance.Action = "D"
                            ledgerPostInstance.CreatedDate = today
                            ledgerPostInstance.using(DataBase).delete()

                    if account_group == "10" or account_group == "29":

                        PartyName = LedgerName
                        if account_group == "10":
                            PartyType = "customer"


                        elif account_group == "29":
                            PartyType = "supplier"

                        PartyCode = LedgerCode

                        if Parties.objects.using(DataBase).filter(BranchID=data.BranchID,LedgerID=data.LedgerID,PartyType=PartyType).exists():
                            partyInstance = Parties.objects.using(DataBase).get(BranchID=data.BranchID,LedgerID=data.LedgerID,PartyType=PartyType)
                            partyInstance.PartyName = PartyName
                            partyInstance.Action = "M"
                            partyInstance.CreatedDate = today
                            partyInstance.OpeningBalance = data.OpeningBalance
                            partyInstance.save(using=DataBase)

                            Parties_Log.objects.using(DataBase).create(
                                TransactionID=partyInstance.PartyID,
                                BranchID=data.BranchID,
                                PartyType=PartyType,
                                LedgerID=data.LedgerID,
                                PartyCode=PartyCode,
                                PartyName=PartyName,
                                PriceCategoryID=1,
                                RouteID=1,
                                IsActive=data.IsActive,
                                Action="M",
                                CreatedUserID=data.CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                OpeningBalance=data.OpeningBalance,
                                )

                    elif account_group == "8":
                    
                        if Bank.objects.using(DataBase).filter(BranchID=data.BranchID,LedgerCode=LedgerCode).exists():
                            bankInstance = Bank.objects.using(DataBase).get(BranchID=data.BranchID,LedgerCode=LedgerCode)
                            bankInstance.Name = data.LedgerName
                            bankInstance.LedgerName = data.LedgerName
                            bankInstance.CrOrDr = CrOrDr
                            bankInstance.OpeningBalance = data.OpeningBalance
                            bankInstance.Notes = data.Notes
                            bankInstance.CreatedDate = today
                            bankInstance.Action = "M"
                            bankInstance.save(using=DataBase)

                            Bank_Log.objects.using(DataBase).create(
                                TransactionID=bankInstance.BankID,
                                BranchID=data.BranchID,
                                LedgerCode=LedgerCode,
                                Name=data.LedgerName,
                                LedgerName=data.LedgerName,
                                CrOrDr=CrOrDr,
                                OpeningBalance=data.OpeningBalance,
                                Notes=data.Notes,
                                CreatedUserID=data.CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                Action=data.Action,
                                )

                    elif account_group == "32":
                    
                        if Employee.objects.using(DataBase).filter(BranchID=data.BranchID,LedgerID=data.LedgerID,EmployeeCode=LedgerCode).exists():
                            employeeInstance = Employee.objects.using(DataBase).get(BranchID=data.BranchID,LedgerID=data.LedgerID,EmployeeCode=LedgerCode)
                            employeeInstance.EmployeeName = data.LedgerName
                            employeeInstance.Notes = data.Notes
                            employeeInstance.Action = "M"
                            employeeInstance.CreatedDate = today
                            employeeInstance.save(using=DataBase)

                            Employee_Log.objects.using(DataBase).create(
                                TransactionID=employeeInstance.EmployeeID,
                                BranchID=data.BranchID,
                                EmployeeCode=LedgerCode,
                                EmployeeName=data.LedgerName,
                                LedgerID=data.LedgerID,
                                DateOfJoining=today,
                                Notes=data.Notes,
                                Action=data.Action,
                                CreatedUserID=data.CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                )
                    data.save(using=DataBase)

                    response_data = {
                        "status" : "true",
                        "title" : str(_("Successfully Updated")),
                        "message" : str(_("AccountLedger Updated Successfully!")),
                        "redirect" : "true",
                        "redirect_url" : reverse('accountLedgers:accountLedgers')
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
        form = AccountLedgerForm(instance=instance)
        accountGroups = AccountGroup.objects.using(DataBase).all()
        context = {
            "is_need_flatpickr" : False,
            "is_need_apexcharts" : False,
            "is_need_selectize" : False,
            "is_need_dashboard" : False,

            "title" : "Edit Account Ledger",
            "form" : form,
            "accountGroups" : accountGroups,
            "is_edit" : True,
            "instance" : instance
        }
        return render(request,"accounts/master/create_account_ledger.html",context)


@login_required
def delete_accountLedger(request,pk):
    today = datetime.date.today()
    instance = None
    ledgerPostInstance = None
    LPInstances = None
    purchaseOrderMaster_exist = None
    salesOrderMaster_exist = None
    parties_exist = None
    employees_exist = None
    if AccountLedger.objects.using(DataBase).filter(pk=pk).exists():
        instance = AccountLedger.objects.using(DataBase).get(pk=pk)

        BranchID = instance.BranchID
        LedgerID = instance.LedgerID
        LedgerName = instance.LedgerName
        LedgerCode = instance.LedgerCode
        AccountGroupUnder = instance.AccountGroupUnder
        OpeningBalance = instance.OpeningBalance
        CrOrDr = instance.CrOrDr
        Notes = instance.Notes
        IsActive = instance.IsActive
        IsDefault = instance.IsDefault
        CreatedUserID = instance.CreatedUserID
        Action = "D"
        
        LPInstances = LedgerPosting.objects.using(DataBase).filter(BranchID=BranchID,LedgerID=LedgerID).exclude(VoucherType="LOB")
            
        purchaseOrderMaster_exist = PurchaseOrderMaster.objects.using(DataBase).filter(BranchID=BranchID,LedgerID=LedgerID).exists()
        salesOrderMaster_exist = SalesOrderMaster.objects.using(DataBase).filter(BranchID=BranchID,LedgerID=LedgerID).exists()
        parties_exist = Parties.objects.using(DataBase).filter(BranchID=BranchID,LedgerID=LedgerID).exists()
        employees_exist = Employee.objects.using(DataBase).filter(BranchID=BranchID,LedgerID=LedgerID).exists()


        if not employees_exist and not parties_exist and not salesOrderMaster_exist and not purchaseOrderMaster_exist and not LPInstances:
        # if not LPInstances:
            instance.using(DataBase).delete()

            AccountLedger_Log.objects.using(DataBase).create(
                BranchID=BranchID,
                TransactionID=LedgerID,
                LedgerName=LedgerName,
                LedgerCode=LedgerCode,
                AccountGroupUnder=AccountGroupUnder,
                OpeningBalance=OpeningBalance,
                CrOrDr=CrOrDr,
                Notes=Notes,
                IsActive=IsActive,
                IsDefault=IsDefault,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                )

            if LedgerPosting.objects.using(DataBase).filter(LedgerID=LedgerID,BranchID=BranchID).exists():
                ledgerPostInstances = LedgerPosting.objects.using(DataBase).filter(LedgerID=LedgerID,BranchID=BranchID)
                
                for ledgerPostInstance in ledgerPostInstances:
                    LedgerPostingID = ledgerPostInstance.LedgerPostingID
                    VoucherType = ledgerPostInstance.VoucherType
                    Debit = ledgerPostInstance.Debit
                    Credit = ledgerPostInstance.Credit
                    IsActive = ledgerPostInstance.IsActive
                    CreatedUserID = ledgerPostInstance.CreatedUserID

                    ledgerPostInstance.using(DataBase).delete()

                    LedgerPosting_Log.objects.using(DataBase).create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=today,
                        VoucherMasterID=LedgerID,
                        VoucherType=VoucherType,
                        LedgerID=LedgerID,
                        Debit=Debit,
                        Credit=Credit,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        )

            response_data = {
                "status" : "true",
                "title" : str(_("Successfully Deleted")),
                "message" : str(_("AccountLedger Deleted Successfully.")),
                "redirect" : "true",
                "redirect_url" : reverse('accounts:accountLedgers')
            }
            return HttpResponse(json.dumps(response_data), content_type='application/javascript')

        else:
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("can't delete this AccountLedger")),
                "message" : str(_("Can't delete this AccountLedger!"))
            }
            return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        response_data = {
            'status' : 'false',
            'stable' : 'true',
            'title' : str(_("can't delete this AccountLedger")),
            "message" : str(_("Can't delete this AccountLedger!"))
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')


# branchs
@login_required
def create_branch(request):
    DataBase = get_DataBase(request)
    today = datetime.date.today()
    if request.method == 'POST':
        form = BranchForm(request.POST)
        if form.is_valid(): 
            data = form.save(commit=False)
            data.CreatedDate = today
            data.UpdatedDate=today
            data.Action = "A"
            data.CreatedUserID = 1
            data.BranchID = get_auto_Branchid(Branch)
            Branch_Log.objects.using(DataBase).create(
                TransactionID=data.BranchID,
                BranchName=data.BranchName,
                BranchLocation=data.BranchLocation,
                Action=data.Action,
                CreatedUserID=data.CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                )
            data.save(using=DataBase)

            response_data = {
                "status" : "true",
                "title" : str(_("Successfully Created")),
                "message" : str(_("Branch Created Successfully!")),
                "redirect" : "true",
                "redirect_url" : reverse('accounts:branchs')
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
        form = BranchForm()
        context = {
            "is_need_flatpickr" : False,
            "is_need_apexcharts" : False,
            "is_need_selectize" : False,
            "is_need_dashboard" : False,

            "title" : "create Branch",
            "form" : form
        }
        return render(request,"accounts/master/create_branch.html",context)


@login_required
def branchs(request):
    DataBase = get_DataBase(request)
    instances = Branch.objects.using(DataBase).all()
    context = {
        "is_need_flatpickr" : False,
        "is_need_apexcharts" : False,
        "is_need_selectize" : False,
        "is_need_dashboard" : False,

        'instances' : instances,
        'title' : 'Branchs'
    }
    return render(request,"accounts/master/branchs.html",context)


@login_required
def view_branch(request,pk):
    instance = Branch.objects.using(DataBase).get(pk=pk)
    context = {
        "is_need_flatpickr" : False,
        "is_need_apexcharts" : False,
        "is_need_selectize" : False,
        "is_need_dashboard" : False,

        'instance' : instance,
    }
    return render(request,"accounts/master/branch.html",context)


@login_required
def edit_branch(request,pk):
    today = datetime.date.today()
    instance = Branch.objects.using(DataBase).get(pk=pk)
    if request.method == 'POST':
        form = BranchForm(request.POST,instance=instance)
        if form.is_valid(): 
            data = form.save(commit=False)
            data.CreatedDate = today
            data.UpdatedDate=today
            data.Action = "M"
            data.BranchID = 1
            data.CreatedUserID = 1
            Branch_Log.objects.using(DataBase).create(
                TransactionID=instance.BranchID,
                BranchName=data.BranchName,
                BranchLocation=data.BranchLocation,
                Action=data.Action,
                CreatedUserID=data.CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                )
            data.save(using=DataBase)

            response_data = {
                "status" : "true",
                "title" : str(_("Successfully Updated")),
                "message" : str(_("Branch Updated Successfully!")),
                "redirect" : "true",
                "redirect_url" : reverse('accounts:view_branch',kwargs={'pk':instance.pk})
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
        form = BranchForm(instance=instance)
        context = {
            "is_need_flatpickr" : False,
            "is_need_apexcharts" : False,
            "is_need_selectize" : False,
            "is_need_dashboard" : False,

            "title" : "Edit Branch",
            "form" : form
        }
        return render(request,"accounts/master/create_branch.html",context)


@login_required
def delete_branch(request,pk):
    today = datetime.date.today()    
    instance = Branch.objects.using(DataBase).get(pk=pk)
    if pk == "1":
        response_data = {
            'status' : 'false',
            'stable' : 'true',
            'title' : str(_("can't delete this brand")),
            "message" : str(_("Can't delete this brand! this is default brand!"))
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        instance.using(DataBase).delete()
        Branch_Log.objects.using(DataBase).create(
            TransactionID=instance.BranchID,
            BranchName=instance.BranchName,
            BranchLocation=instance.BranchLocation,
            Action=instance.Action,
            CreatedUserID=instance.CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            )
        
        response_data = {
            "status" : "true",
            "title" : str(_("Successfully Deleted")),
            "message" : str(_("Branch Deleted Successfully.")),
            "redirect" : "true",
            "redirect_url" : reverse('accounts:branchs')
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
# branch ends here

# brands
@login_required
def create_brand(request):
    DataBase = get_DataBase(request)

    today = datetime.date.today()
    if request.method == 'POST':
        form = BrandForm(request.POST)
        if form.is_valid(): 
            data = form.save(commit=False)
            BrandName = data.BrandName

            is_nameExist = False
            BrandNameLow = BrandName.lower()
            brands = Brand.objects.using(DataBase).filter(BranchID=1)

            for brand in brands:
                brand_name = brand.BrandName
                brandName = brand_name.lower()

                if BrandNameLow == brandName:
                    is_nameExist = True

            if not is_nameExist:
                data.CreatedDate = today
                data.UpdatedDate=today
                data.Action = "A"
                data.BranchID = 1
                data.CreatedUserID = 1
                data.BrandID = get_auto_id(Brand,data.BranchID)
                Brand_Log.objects.using(DataBase).create(
                    BranchID=data.BranchID,
                    TransactionID=data.BrandID,
                    BrandName=data.BrandName,
                    Notes=data.Notes,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=1,
                    Action=data.Action,
                    )
                data.save(using=DataBase)

                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("Brand Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('accounts:brands')
                }
            else:
                response_data = {
                    "status" : "false",
                    "title" : str(_("Brand Already Exist")),
                    "message" : str(_("Brand Name is Already exist with in the BranchID")),
                    "redirect" : "true",
                    "redirect_url" : reverse('accounts:create_brand')
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
        form = BrandForm(request)
        context = {
            "is_need_flatpickr" : False,
            "is_need_apexcharts" : False,
            "is_need_selectize" : False,
            "is_need_dashboard" : False,

            "title" : "create Brand",
            "form" : form
        }
        return render(request,"accounts/master/create_brand.html",context)


@login_required
def view_brand(request,pk):
    instance = Brand.objects.using(DataBase).get(pk=pk)
    context = {
        "is_need_flatpickr" : False,
        "is_need_apexcharts" : False,
        "is_need_selectize" : False,
        "is_need_dashboard" : False,

        'instance' : instance,
    }
    return render(request,"accounts/master/brand.html",context)


# banks starts here
@login_required
def create_bank(request):
    DataBase = get_DataBase(request)
    
    today = datetime.date.today()
    if request.method == 'POST':
        form = BankForm(request.POST)
        if form.is_valid(): 
            data = form.save(commit=False)
            LedgerName = data.Name
            AccountGroupUnder = 8

            is_nameExist = False
            LedgerNameLow = LedgerName.lower()
            ledgers = AccountLedger.objects.filter(BranchID=1)

            for ledger in ledgers:
                ledger_name = ledger.LedgerName
                LedgerName = ledger_name.lower()

                if LedgerNameLow == LedgerName:
                    is_nameExist = True

            if not is_nameExist:
                data.CreatedDate = today
                data.UpdatedDate=today
                data.Action = "A"
                data.BranchID = 1
                data.CreatedUserID = request.user.id
                data.LedgerName = data.Name
                data.BankID = get_auto_Bankid(Bank,data.BranchID,DataBase)
                data.LedgerCode = get_LedgerCode(AccountLedger, data.BranchID, DataBase)
                LedgerID = get_auto_LedgerID(AccountLedger,data.BranchID, DataBase)
                Bank_Log.objects.using(DataBase).create(
                    BranchID=data.BranchID,
                    TransactionID=data.BankID,
                    LedgerCode=data.LedgerCode,
                    Name=data.Name,
                    LedgerName=data.Name,
                    AccountNumber=data.AccountNumber,
                    CrOrDr=data.CrOrDr,
                    BranchCode=data.BranchCode,
                    IFSCCode=data.IFSCCode,
                    MICRCode=data.MICRCode,
                    Status=data.Status,
                    OpeningBalance=data.OpeningBalance,
                    Address=data.Address,
                    City=data.City,
                    State=data.State,
                    Country=data.Country,
                    PostalCode=data.PostalCode,
                    Phone=data.Phone,
                    Mobile=data.Mobile,
                    Email=data.Email,
                    Notes=data.Notes,
                    CreatedUserID=data.CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=data.Action,
                    )

                AccountLedger.objects.using(DataBase).create(
                    LedgerID=LedgerID,
                    BranchID=data.BranchID,
                    LedgerName=data.Name,
                    LedgerCode=data.LedgerCode,
                    AccountGroupUnder=AccountGroupUnder,
                    OpeningBalance=data.OpeningBalance,
                    CrOrDr=data.CrOrDr,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Notes=data.Notes,
                    Action=data.Action,
                    CreatedUserID=data.CreatedUserID,
                    )

                AccountLedger_Log.objects.using(DataBase).create(
                    TransactionID=LedgerID,
                    BranchID=data.BranchID,
                    LedgerName=data.Name,
                    LedgerCode=data.LedgerCode,
                    AccountGroupUnder=AccountGroupUnder,
                    OpeningBalance=data.OpeningBalance,
                    CrOrDr=data.CrOrDr,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Notes=data.Notes,
                    Action=data.Action,
                    CreatedUserID=data.CreatedUserID,
                    )

                if float(data.OpeningBalance) > 0:
                    Credit = 0.00
                    Debit = 0.00

                    if data.CrOrDr == "Cr":
                        Credit = data.OpeningBalance

                    elif data.CrOrDr == "Dr":
                        Debit = data.OpeningBalance

                    VoucherType = "LOB"

                    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,data.BranchID, DataBase)

                    LedgerPosting.objects.using(DataBase).create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=today,
                        VoucherMasterID=LedgerID,
                        VoucherType=VoucherType,
                        LedgerID=LedgerID,
                        Debit=Debit,
                        Credit=Credit,
                        Action=data.Action,
                        CreatedUserID=1,
                        CreatedDate=today,
                        UpdatedDate=today,
                        )

                    LedgerPosting_Log.objects.using(DataBase).create(
                        TransactionID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=today,
                        VoucherMasterID=LedgerID,
                        VoucherType=VoucherType,
                        LedgerID=LedgerID,
                        Debit=Debit,
                        Credit=Credit,
                        Action=data.Action,
                        CreatedUserID=1,
                        CreatedDate=today,
                        UpdatedDate=today,
                        )
                data.save(using=DataBase)

                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("Bank Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('accounts:banks')
                }
            else:
                response_data = {
                    "status" : "false",
                    "title" : str(_("Bank Already Exist")),
                    "message" : str(_("Bank Name is Already exist with in the BranchID")),
                    "redirect" : "true",
                    "redirect_url" : reverse('accounts:create_bank')
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
        form = BankForm()
        accountGroups = AccountGroup.objects.all()
        context = {
            "is_need_flatpickr" : False,
            "is_need_apexcharts" : False,
            "is_need_selectize" : False,
            "is_need_dashboard" : False,

            "title" : "Create Bank",
            "form" : form,
            "accountGroups" : accountGroups
        }
        return render(request,"accounts/master/create_bank.html",context)


@login_required
def banks(request):
    DataBase = get_DataBase(request)
    
    instances = Bank.objects.using(DataBase).all()
    context = {
        "is_need_flatpickr" : False,
        "is_need_apexcharts" : False,
        "is_need_selectize" : False,
        "is_need_dashboard" : False,

        'instances' : instances,
        'title' : 'Banks'
    }
    return render(request,"accounts/master/banks.html",context)


@login_required
def view_bank(request,pk):
    DataBase = get_DataBase(request)

    instance = Bank.objects.using(DataBase).get(pk=pk)
    context = {
        "is_need_flatpickr" : False,
        "is_need_apexcharts" : False,
        "is_need_selectize" : False,
        "is_need_dashboard" : False,

        'instance' : instance,
        'title' : 'Bank'
    }
    return render(request,"accounts/master/bank.html",context)


@login_required
def edit_bank(request,pk):
    DataBase = get_DataBase(request)

    today = datetime.date.today()
    instance = Bank.objects.using(DataBase).get(pk=pk)
    instanceLedgerName = instance.LedgerName
    LedgerCode = instance.LedgerCode
    BankID = instance.BankID
    if request.method == 'POST':
        form = BankForm(request.POST,instance=instance)
        if form.is_valid():
            data = form.save(commit=False)
            LedgerName = data.Name
            AccountGroupUnder = 8

            is_nameExist = False
            accountLedger_ok = False

            LedgerNameLow = LedgerName.lower()

            account_ledgers = AccountLedger.objects.using(DataBase).filter(BranchID=data.BranchID)

            for account_ledger in account_ledgers:

                ledger_name = account_ledger.LedgerName
                ledgerName = ledger_name.lower()

                if LedgerNameLow == ledgerName:
                    is_nameExist = True

                if instanceLedgerName.lower() == LedgerNameLow:

                    accountLedger_ok = True
            if accountLedger_ok:
                data.CreatedDate = today
                data.UpdatedDate=today
                data.Action = "M"
                data.BranchID = 1
                data.CreatedUserID = request.user.id
                data.LedgerName = LedgerName
                Bank_Log.objects.using(DataBase).create(
                    BranchID=data.BranchID,
                    TransactionID=BankID,
                    LedgerCode=LedgerCode,
                    Name=data.Name,
                    LedgerName=LedgerName,
                    AccountNumber=data.AccountNumber,
                    CrOrDr=data.CrOrDr,
                    BranchCode=data.BranchCode,
                    IFSCCode=data.IFSCCode,
                    MICRCode=data.MICRCode,
                    Status=data.Status,
                    OpeningBalance=data.OpeningBalance,
                    Address=data.Address,
                    City=data.City,
                    State=data.State,
                    Country=data.Country,
                    PostalCode=data.PostalCode,
                    Phone=data.Phone,
                    Mobile=data.Mobile,
                    Email=data.Email,
                    Notes=data.Notes,
                    CreatedUserID=data.CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=data.Action,
                    )


                if AccountLedger.objects.using(DataBase).filter(LedgerName=instanceLedgerName,BranchID=data.BranchID).exists():
                    account_ledger = AccountLedger.objects.using(DataBase).get(LedgerName=instanceLedgerName,BranchID=data.BranchID)
                    LedgerID = account_ledger.LedgerID
                    account_ledger.LedgerName = data.Name
                    account_ledger.OpeningBalance = data.OpeningBalance
                    account_ledger.CrOrDr = data.CrOrDr
                    account_ledger.CreatedDate = today
                    account_ledger.Notes = data.Notes
                    account_ledger.Action = data.Action
                    account_ledger.save(using=DataBase)

                    AccountLedger_Log.objects.using(DataBase).create(
                        BranchID=data.BranchID,
                        TransactionID=LedgerID,
                        LedgerName=data.Name,
                        LedgerCode=LedgerCode,
                        AccountGroupUnder=AccountGroupUnder,
                        OpeningBalance=data.OpeningBalance,
                        CrOrDr=data.CrOrDr,
                        CreatedDate=today,
                        UpdatedDate=today,
                        Notes=data.Notes,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        )
                if LedgerPosting.objects.using(DataBase).filter(LedgerID=LedgerID,BranchID=data.BranchID,VoucherMasterID=LedgerID,VoucherType="LOB").exists():
                    ledgerPostInstance = LedgerPosting.objects.using(DataBase).get(LedgerID=LedgerID,BranchID=data.BranchID,VoucherMasterID=LedgerID,VoucherType="LOB")
                    ledgerPostInstance.delete()

                if float(data.OpeningBalance) > 0:
                    Credit = 0.00
                    Debit = 0.00

                    if data.CrOrDr == "Cr":
                        Credit = data.OpeningBalance

                    elif data.CrOrDr == "Dr":
                        Debit = data.OpeningBalance

                    VoucherType = "LOB"

                    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,data.BranchID,DataBase)

                    LedgerPosting.objects.using(DataBase).create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=today,
                        VoucherMasterID=LedgerID,
                        VoucherType=VoucherType,
                        LedgerID=LedgerID,
                        Debit=Debit,
                        Credit=Credit,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        )

                    LedgerPosting_Log.objects.using(DataBase).create(
                        TransactionID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=today,
                        VoucherMasterID=LedgerID,
                        VoucherType=VoucherType,
                        LedgerID=LedgerID,
                        Debit=Debit,
                        Credit=Credit,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        )
                data.save()

                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("Bank Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('accounts:banks')
                }
            else:
                if is_nameExist:
                    response_data = {
                        "status" : "false",
                        "title" : str(_("Bank Already Exist")),
                        "message" : str(_("Bank Name is Already exist with in the BranchID")),
                        "redirect" : "true",
                        "redirect_url" : reverse('accounts:create_bank')
                    }
                else:
                    data.CreatedDate = today
                    data.UpdatedDate=today
                    data.Action = "M"
                    data.BranchID = 1
                    data.CreatedUserID = 1
                    data.LedgerName = LedgerName
                    Bank_Log.objects.using(DataBase).create(
                        BranchID=data.BranchID,
                        TransactionID=BankID,
                        LedgerCode=LedgerCode,
                        Name=data.Name,
                        LedgerName=LedgerName,
                        AccountNumber=data.AccountNumber,
                        CrOrDr=data.CrOrDr,
                        BranchCode=data.BranchCode,
                        IFSCCode=data.IFSCCode,
                        MICRCode=data.MICRCode,
                        Status=data.Status,
                        OpeningBalance=data.OpeningBalance,
                        Address=data.Address,
                        City=data.City,
                        State=data.State,
                        Country=data.Country,
                        PostalCode=data.PostalCode,
                        Phone=data.Phone,
                        Mobile=data.Mobile,
                        Email=data.Email,
                        Notes=data.Notes,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        Action=data.Action,
                        )


                    if AccountLedger.objects.using(DataBase).filter(LedgerName=instanceLedgerName,BranchID=data.BranchID).exists():
                        account_ledger = AccountLedger.objects.using(DataBase).get(LedgerName=instanceLedgerName,BranchID=data.BranchID)
                        LedgerID = account_ledger.LedgerID
                        account_ledger.LedgerName = data.Name
                        account_ledger.OpeningBalance = data.OpeningBalance
                        account_ledger.CrOrDr = data.CrOrDr
                        account_ledger.CreatedDate = today
                        account_ledger.Notes = data.Notes
                        account_ledger.Action = data.Action
                        account_ledger.save(using=DataBase)

                        AccountLedger_Log.objects.using(DataBase).create(
                            BranchID=data.BranchID,
                            TransactionID=LedgerID,
                            LedgerName=data.Name,
                            LedgerCode=LedgerCode,
                            AccountGroupUnder=AccountGroupUnder,
                            OpeningBalance=data.OpeningBalance,
                            CrOrDr=data.CrOrDr,
                            CreatedDate=today,
                            UpdatedDate=today,
                            Notes=data.Notes,
                            Action=data.Action,
                            CreatedUserID=data.CreatedUserID,
                            )
                        if LedgerPosting.objects.using(DataBase).filter(LedgerID=LedgerID,BranchID=data.BranchID,VoucherMasterID=LedgerID,VoucherType="LOB").exists():
                            ledgerPostInstance = LedgerPosting.objects.using(DataBase).get(LedgerID=LedgerID,BranchID=data.BranchID,VoucherMasterID=LedgerID,VoucherType="LOB")
                            ledgerPostInstance.delete()

                        if float(data.OpeningBalance) > 0:
                            Credit = 0.00
                            Debit = 0.00

                            if data.CrOrDr == "Cr":
                                Credit = data.OpeningBalance

                            elif data.CrOrDr == "Dr":
                                Debit = data.OpeningBalance

                            VoucherType = "LOB"

                            LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,data.BranchID,DataBase)

                            LedgerPosting.objects.using(DataBase).create(
                                LedgerPostingID=LedgerPostingID,
                                BranchID=data.BranchID,
                                Date=today,
                                VoucherMasterID=LedgerID,
                                VoucherType=VoucherType,
                                LedgerID=LedgerID,
                                Debit=Debit,
                                Credit=Credit,
                                Action=data.Action,
                                CreatedUserID=data.CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                )

                            LedgerPosting_Log.objects.using(DataBase).create(
                                TransactionID=LedgerPostingID,
                                BranchID=data.BranchID,
                                Date=today,
                                VoucherMasterID=LedgerID,
                                VoucherType=VoucherType,
                                LedgerID=LedgerID,
                                Debit=Debit,
                                Credit=Credit,
                                Action=data.Action,
                                CreatedUserID=data.CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                )
                        data.save(using=DataBase)

                    response_data = {
                        "status" : "true",
                        "title" : str(_("Successfully Updated")),
                        "message" : str(_("Bank Updated Successfully!")),
                        "redirect" : "true",
                        "redirect_url" : reverse('accounts:banks')
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
        form = BankForm(instance=instance)
        accountGroups = AccountGroup.objects.using(DataBase).all()
        context = {
            "is_need_flatpickr" : False,
            "is_need_apexcharts" : False,
            "is_need_selectize" : False,
            "is_need_dashboard" : False,

            "title" : "Edit Bank",
            "form" : form,
            "accountGroups" : accountGroups,
            "is_edit" : True,
            "instance" : instance
        }
        return render(request,"accounts/master/create_bank.html",context)


@login_required
def delete_bank(request,pk):
    DataBase = get_DataBase(request)

    today = datetime.date.today()
    instance = None
    if Bank.objects.using(DataBase).filter(pk=pk).exists():
        instance = Bank.objects.using(DataBase).get(pk=pk)

        BankID = instance.BankID
        BranchID = instance.BranchID
        LedgerCode = instance.LedgerCode
        Name = instance.Name
        LedgerName = instance.LedgerName
        AccountNumber = instance.AccountNumber
        CrOrDr = instance.CrOrDr
        BranchCode = instance.BranchCode
        IFSCCode = instance.IFSCCode
        MICRCode = instance.MICRCode
        Status = instance.Status
        OpeningBalance = instance.OpeningBalance
        Address = instance.Address
        City = instance.City
        State = instance.State
        Country = instance.Country
        PostalCode = instance.PostalCode
        Phone = instance.Phone
        Mobile = instance.Mobile
        Email = instance.Email
        Notes = instance.Notes
        CreatedUserID = instance.CreatedUserID
        Action = "D"

        AccountGroupUnder = 8

        if AccountLedger.objects.filter(BranchID=BranchID,LedgerName=LedgerName).using(DataBase).exists():
            account_ledger = AccountLedger.objects.using(DataBase).get(BranchID=BranchID,LedgerName=LedgerName)
            LedgerID = account_ledger.LedgerID
            if not LedgerPosting.objects.using(DataBase).filter(LedgerID=LedgerID,BranchID=BranchID).exists():
                instance.delete()
                account_ledger.delete()

                Bank_Log.objects.using(DataBase).create(
                    BranchID=BranchID,
                    TransactionID=BankID,
                    LedgerCode=LedgerCode,
                    Name=Name,
                    LedgerName=LedgerName,
                    AccountNumber=AccountNumber,
                    CrOrDr=CrOrDr,
                    BranchCode=BranchCode,
                    IFSCCode=IFSCCode,
                    MICRCode=MICRCode,
                    Status=Status,
                    OpeningBalance=OpeningBalance,
                    Address=Address,
                    City=City,
                    State=State,
                    Country=Country,
                    PostalCode=PostalCode,
                    Phone=Phone,
                    Mobile=Mobile,
                    Email=Email,
                    Notes=Notes,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=Action,
                    )

                AccountLedger_Log.objects.using(DataBase).create(
                    BranchID=BranchID,
                    TransactionID=LedgerID,
                    LedgerName=LedgerName,
                    LedgerCode=LedgerCode,
                    AccountGroupUnder=AccountGroupUnder,
                    OpeningBalance=OpeningBalance,
                    CrOrDr=CrOrDr,
                    Notes=Notes,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=Action,
                    )
               

                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Deleted")),
                    "message" : str(_("Bank Deleted Successfully.")),
                    "redirect" : "true",
                    "redirect_url" : reverse('accounts:banks')
                }
                return HttpResponse(json.dumps(response_data), content_type='application/javascript')
            else:
                response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("can't delete this Bank")),
                "message" : str(_("Can't delete this Bank! data exist in Ledgerposting with LedgerID"))
                }
                return HttpResponse(json.dumps(response_data), content_type='application/javascript')

        else:
            response_data = {
            'status' : 'false',
            'stable' : 'true',
            'title' : str(_("can't delete this Bank")),
            "message" : str(_("Can't delete this Bank!"))
            }
            return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        response_data = {
        'status' : 'false',
        'stable' : 'true',
        'title' : str(_("Bank is Not Fount!")),
        "message" : str(_("Bank is Not Fount!"))
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
        # bank ends here


@login_required
def create_customer(request):
    DataBase = get_DataBase(request)

    today = datetime.date.today()
    if request.method == 'POST':

        form = CustomerForm(request.POST,request.FILES)
        if form.is_valid(): 
            CrODr = request.POST.get('CrODr')
            BranchID = 1
            Action = 'A'
            PartyType = "customer"
            AccountGroupUnder = 10

            LedgerID = get_auto_idLedger(AccountLedger,BranchID,DataBase)
            PartyCode = get_PartyCode(Parties, BranchID,DataBase, PartyType)
            PartyID = get_auto_partyID(Parties,BranchID,DataBase)
            CreatedUserID = request.user.id

            # form_img = form.cleaned_data['img']
            # print("''''''''''''''''''''''''''")
            # print(form_img)
            # encoded_string = get_base64_file(form_img)

            data = form.save(commit=False)
            # data.img = encoded_string
            LedgerName = data.FirstName
            is_nameExist = False
            FirstNameLow = data.FirstName.lower()
            parties = Parties.objects.using(DataBase).filter(BranchID=BranchID)
            for party in parties:
                party_name = party.FirstName

                party_FirstName = party_name.lower()

                if FirstNameLow == party_FirstName:
                    is_nameExist = True


            if not is_nameExist:

                is_LedgernameExist = False

                LedgerNameLow = LedgerName.lower()

                accountLedgers = AccountLedger.objects.using(DataBase).filter(BranchID=BranchID)

                for accountLedger in accountLedgers:
                    ledger_name = accountLedger.LedgerName

                    ledgerName = ledger_name.lower()

                    if LedgerNameLow == ledgerName:
                        is_LedgernameExist = True

                if not is_LedgernameExist:
                    AccountLedger.objects.using(DataBase).create(
                        LedgerID=LedgerID,
                        BranchID=BranchID,
                        LedgerName=LedgerName,
                        LedgerCode=PartyCode,
                        AccountGroupUnder=AccountGroupUnder,
                        OpeningBalance=data.OpeningBalance,
                        CrOrDr=CrODr,
                        IsActive=data.IsActive,
                        CreatedDate=today,
                        UpdatedDate=today,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        )

                    AccountLedger_Log.objects.using(DataBase).create(
                        TransactionID=LedgerID,
                        BranchID=BranchID,
                        LedgerName=LedgerName,
                        LedgerCode=PartyCode,
                        AccountGroupUnder=AccountGroupUnder,
                        OpeningBalance=data.OpeningBalance,
                        CrOrDr=CrODr,
                        IsActive=data.IsActive,
                        CreatedDate=today,
                        UpdatedDate=today,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        )

                    if float(data.OpeningBalance) > 0:
                        Credit = 0
                        Debit = 0

                        if CrODr == "Cr":
                            Credit = data.OpeningBalance

                        elif CrODr == "Dr":
                            Debit = data.OpeningBalance

                        VoucherType = "LOB"

                        LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

                        LedgerPosting.objects.using(DataBase).create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=today,
                            VoucherMasterID=LedgerID,
                            VoucherType=VoucherType,
                            LedgerID=LedgerID,
                            Debit=Debit,
                            Credit=Credit,
                            IsActive=data.IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            )

                        LedgerPosting_Log.objects.using(DataBase).create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=today,
                            VoucherMasterID=LedgerID,
                            VoucherType=VoucherType,
                            LedgerID=LedgerID,
                            Debit=Debit,
                            Credit=Credit,
                            IsActive=data.IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            )

                else:
                    response_data = {
                        "status" : "false",
                        "title" : str(_("Customer Already Exist")),
                        "message" : str(_("Customer Name is Already exist with in the BranchID")),
                        "redirect" : "true",
                        "redirect_url" : reverse('accounts:create_customer')
                    }

                data.PartyID = PartyID
                data.PartyCode = PartyCode
                data.PartyType = PartyType
                data.BranchID = BranchID
                data.LedgerID = LedgerID
                data.CreatedDate = today
                data.UpdatedDate = today
                data.CreatedUserID = CreatedUserID
                data.Action = Action

                Parties_Log.objects.using(DataBase).create(
                    TransactionID=PartyID,
                    BranchID=BranchID,
                    PartyType=PartyType,
                    LedgerID=LedgerID,
                    PartyCode=PartyCode,
                    FirstName=data.FirstName,
                    LastName=data.LastName,
                    ContactPerson=data.ContactPerson,
                    Address1=data.Address1,
                    Address2=data.Address2,
                    Address3=data.Address3,
                    Address4=data.Address4,
                    City=data.City,
                    State=data.State,
                    Country=data.Country,
                    PostalCode=data.PostalCode,
                    OfficePhone=data.OfficePhone,
                    WorkPhone=data.WorkPhone,
                    Mobile=data.Mobile,
                    WebURL=data.WebURL,
                    Email=data.Email,
                    IsBillwiseApplicable=data.IsBillwiseApplicable,
                    CreditPeriod=data.CreditPeriod,
                    CreditLimit=data.CreditLimit,
                    PriceCategoryID=data.PriceCategoryID,
                    CurrencyID=data.CurrencyID,
                    InterestOrNot=data.InterestOrNot,
                    RouteID=data.RouteID,
                    VATNumber=data.VATNumber,
                    GSTNumber=data.GSTNumber,
                    Tax1Number=data.Tax1Number,
                    Tax2Number=data.Tax2Number,
                    Tax3Number=data.Tax3Number,
                    PanNumber=data.PanNumber,
                    BankName1=data.BankName1,
                    AccountName1=data.AccountName1,
                    AccountNo1=data.AccountNo1,
                    IBANOrIFSCCode1=data.IBANOrIFSCCode1,
                    BankName2=data.BankName2,
                    AccountName2=data.AccountName2,
                    AccountNo2=data.AccountNo2,
                    IBANOrIFSCCode2=data.IBANOrIFSCCode2,
                    IsActive=data.IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    OpeningBalance=data.OpeningBalance,
                    PartyImage=data.PartyImage
                    )
                data.save(using=DataBase)
                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("Customer Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('accounts:customers')
                }
            else:
                response_data = {
                    "status" : "false",
                    "title" : str(_("Customer Already Exist")),
                    "message" : str(_("Customer Name is Already exist with in the BranchID")),
                    "redirect" : "true",
                    "redirect_url" : reverse('accounts:create_customer')
                }
        else:
            print(form.errors)
            message = generate_form_errors(form,formset=False)
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("Form validation error")),
                "message" : str(message)
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = CustomerForm()
        countries = Country.objects.all()
        context = {
            "is_need_flatpickr" : False,
            "is_need_apexcharts" : False,
            "is_need_selectize" : False,
            "is_need_dashboard" : False,
            "is_need_bootstrap_wizard" : True,
            "is_need_form_wizard" : True,

            "title" : "Create Customer",
            "form" : form,
            "countries" : countries,
        }
        return render(request,"accounts/master/create_customer.html",context)

@login_required
def customers(request):
    DataBase = get_DataBase(request)
    instances = Parties.objects.using(DataBase).filter(BranchID=1,PartyType = "customer")
    context = {
        "is_need_flatpickr" : False,
        "is_need_apexcharts" : False,
        "is_need_selectize" : False,
        "is_need_dashboard" : False,

        'instances' : instances,
        'title' : 'Customers'
    }
    return render(request,"accounts/master/customers.html",context)


@login_required
def view_customer(request,pk):

    DataBase = get_DataBase(request)

    instance = Parties.objects.using(DataBase).get(pk=pk)

    context = {
        "is_need_flatpickr" : False,
        "is_need_apexcharts" : False,
        "is_need_selectize" : False,
        "is_need_dashboard" : False,

        'instance' : instance,
        'title' : 'Customer'
    }
    return render(request,"accounts/master/customer.html",context)


@login_required
def edit_customer(request,pk):
    DataBase = get_DataBase(request)

    instance = Parties.objects.using(DataBase).get(pk=pk)
    LedgerID = instance.LedgerID
    instanceFirstName = instance.FirstName
    BranchID = instance.BranchID
    accountLedgerInstance = AccountLedger.objects.using(DataBase).get(LedgerID=LedgerID,BranchID=BranchID)
    LedgerCode = accountLedgerInstance.LedgerCode

    if LedgerPosting.objects.using(DataBase).filter(LedgerID=LedgerID,BranchID=BranchID,VoucherType="LOB").exists():
        ledgerPostInstance = LedgerPosting.objects.using(DataBase).get(LedgerID=LedgerID,BranchID=BranchID,VoucherType="LOB")
        ledgerPostInstance.delete()

    PartyID = instance.PartyID
    PartyCode = instance.PartyCode
    PartyType = instance.PartyType
    CreatedUserID = request.user.id

    Action = 'M'

    today = datetime.date.today()
    if request.method == 'POST':

        form = CustomerForm(request.POST,request.FILES,instance=instance)
        if form.is_valid(): 
            CrODr = request.POST.get('CrODr')
            AccountGroupUnder = 10

            data = form.save(commit=False)
            LedgerName = data.FirstName
            is_nameExist = False
            party_ok = False

            FirstNameLow = data.FirstName.lower()

            parties = Parties.objects.using(DataBase).filter(BranchID=BranchID)

            for party in parties:
                party_name = party.FirstName

                party_FirstName = party_name.lower()

                if FirstNameLow == party_FirstName:
                    is_nameExist = True

                if instanceFirstName.lower() == FirstNameLow:

                    party_ok = True


            if  party_ok:

                accountLedgerInstance.LedgerName = LedgerName
                            # accountLedgerInstance.LedgerCode = LedgerCode
                accountLedgerInstance.AccountGroupUnder = AccountGroupUnder
                accountLedgerInstance.OpeningBalance = data.OpeningBalance
                accountLedgerInstance.CrOrDr = CrODr
                accountLedgerInstance.IsActive = data.IsActive
                accountLedgerInstance.Action = Action
                accountLedgerInstance.CreatedUserID = CreatedUserID
                accountLedgerInstance.UpdatedDate = today
                accountLedgerInstance.save()

                AccountLedger_Log.objects.using(DataBase).create(
                    BranchID=BranchID,
                    TransactionID=LedgerID,
                    LedgerName=LedgerName,
                    LedgerCode=LedgerCode,
                    AccountGroupUnder=AccountGroupUnder,
                    OpeningBalance=data.OpeningBalance,
                    CrOrDr=CrODr,
                    IsActive=data.IsActive,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    Action=Action,
                    )

                if float(data.OpeningBalance) > 0:
                    Credit = 0
                    Debit = 0

                    if CrODr == "Cr":
                        Credit = data.OpeningBalance

                    elif CrODr == "Dr":
                        Debit = data.OpeningBalance

                    VoucherType = "LOB"

                    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

                    LedgerPosting.objects.using(DataBase).create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=today,
                        VoucherMasterID=LedgerID,
                        VoucherType=VoucherType,
                        LedgerID=LedgerID,
                        Debit=Debit,
                        Credit=Credit,
                        IsActive=data.IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        )

                    LedgerPosting_Log.objects.using(DataBase).create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=today,
                        VoucherMasterID=LedgerID,
                        VoucherType=VoucherType,
                        LedgerID=LedgerID,
                        Debit=Debit,
                        Credit=Credit,
                        IsActive=data.IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        )

                data.UpdatedDate = today
                data.CreatedUserID = CreatedUserID
                data.Action = Action
                data.PartyID = PartyID
                data.PartyCode = PartyCode
                data.PartyType = PartyType
                data.BranchID = BranchID
                data.LedgerID = LedgerID
                Parties_Log.objects.using(DataBase).create(
                    TransactionID=PartyID,
                    BranchID=BranchID,
                    PartyType=PartyType,
                    LedgerID=LedgerID,
                    PartyCode=PartyCode,
                    FirstName=data.FirstName,
                    LastName=data.LastName,
                    ContactPerson=data.ContactPerson,
                    Address1=data.Address1,
                    Address2=data.Address2,
                    Address3=data.Address3,
                    Address4=data.Address4,
                    City=data.City,
                    State=data.State,
                    Country=data.Country,
                    PostalCode=data.PostalCode,
                    OfficePhone=data.OfficePhone,
                    WorkPhone=data.WorkPhone,
                    Mobile=data.Mobile,
                    WebURL=data.WebURL,
                    Email=data.Email,
                    IsBillwiseApplicable=data.IsBillwiseApplicable,
                    CreditPeriod=data.CreditPeriod,
                    CreditLimit=data.CreditLimit,
                    PriceCategoryID=data.PriceCategoryID,
                    CurrencyID=data.CurrencyID,
                    InterestOrNot=data.InterestOrNot,
                    RouteID=data.RouteID,
                    VATNumber=data.VATNumber,
                    GSTNumber=data.GSTNumber,
                    Tax1Number=data.Tax1Number,
                    Tax2Number=data.Tax2Number,
                    Tax3Number=data.Tax3Number,
                    PanNumber=data.PanNumber,
                    BankName1=data.BankName1,
                    AccountName1=data.AccountName1,
                    AccountNo1=data.AccountNo1,
                    IBANOrIFSCCode1=data.IBANOrIFSCCode1,
                    BankName2=data.BankName2,
                    AccountName2=data.AccountName2,
                    AccountNo2=data.AccountNo2,
                    IBANOrIFSCCode2=data.IBANOrIFSCCode2,
                    IsActive=data.IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    OpeningBalance=data.OpeningBalance,
                    PartyImage=data.PartyImage
                    )
                data.save(using=DataBase)
                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Updated")),
                    "message" : str(_("Customer Updated Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('accounts:customers')
                }
            else:
                if is_nameExist:
                    response_data = {
                        "status" : "false",
                        "title" : str(_("Customer Already Exist")),
                        "message" : str(_("Customer Name is Already exist with in the BranchID")),
                        "redirect" : "true",
                        "redirect_url" : reverse('accounts:edit_customer',kwargs={"pk":instance.pk}),
                    }

                else:
                    accountLedgerInstance.LedgerName = LedgerName
                    # accountLedgerInstance.LedgerCode = LedgerCode
                    accountLedgerInstance.AccountGroupUnder = AccountGroupUnder
                    accountLedgerInstance.OpeningBalance = data.OpeningBalance
                    accountLedgerInstance.CrOrDr = CrODr
                    accountLedgerInstance.IsActive = data.IsActive
                    accountLedgerInstance.Action = Action
                    accountLedgerInstance.CreatedUserID = CreatedUserID
                    accountLedgerInstance.UpdatedDate = today
                    accountLedgerInstance.save()

                    AccountLedger_Log.objects.using(DataBase).create(
                        BranchID=BranchID,
                        TransactionID=LedgerID,
                        LedgerName=LedgerName,
                        LedgerCode=LedgerCode,
                        AccountGroupUnder=AccountGroupUnder,
                        OpeningBalance=data.OpeningBalance,
                        CrOrDr=CrODr,
                        IsActive=data.IsActive,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        Action=Action,
                        )

                    if float(data.OpeningBalance) > 0:
                        Credit = 0
                        Debit = 0

                        if CrODr == "Cr":
                            Credit = data.OpeningBalance

                        elif CrODr == "Dr":
                            Debit = data.OpeningBalance

                        VoucherType = "LOB"

                        LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

                        LedgerPosting.objects.using(DataBase).create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=today,
                            VoucherMasterID=LedgerID,
                            VoucherType=VoucherType,
                            LedgerID=LedgerID,
                            Debit=Debit,
                            Credit=Credit,
                            IsActive=data.IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            )

                        LedgerPosting_Log.objects.using(DataBase).create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=today,
                            VoucherMasterID=LedgerID,
                            VoucherType=VoucherType,
                            LedgerID=LedgerID,
                            Debit=Debit,
                            Credit=Credit,
                            IsActive=data.IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            )

                    data.UpdatedDate = today
                    data.CreatedUserID = CreatedUserID
                    data.Action = Action
                    data.PartyID = PartyID
                    data.PartyCode = PartyCode
                    data.PartyType = PartyType
                    data.BranchID = BranchID
                    data.LedgerID = LedgerID

                    Parties_Log.objects.using(DataBase).create(
                        TransactionID=PartyID,
                        BranchID=BranchID,
                        PartyType=PartyType,
                        LedgerID=LedgerID,
                        PartyCode=PartyCode,
                        FirstName=data.FirstName,
                        LastName=data.LastName,
                        ContactPerson=data.ContactPerson,
                        Address1=data.Address1,
                        Address2=data.Address2,
                        Address3=data.Address3,
                        Address4=data.Address4,
                        City=data.City,
                        State=data.State,
                        Country=data.Country,
                        PostalCode=data.PostalCode,
                        OfficePhone=data.OfficePhone,
                        WorkPhone=data.WorkPhone,
                        Mobile=data.Mobile,
                        WebURL=data.WebURL,
                        Email=data.Email,
                        IsBillwiseApplicable=data.IsBillwiseApplicable,
                        CreditPeriod=data.CreditPeriod,
                        CreditLimit=data.CreditLimit,
                        PriceCategoryID=data.PriceCategoryID,
                        CurrencyID=data.CurrencyID,
                        InterestOrNot=data.InterestOrNot,
                        RouteID=data.RouteID,
                        VATNumber=data.VATNumber,
                        GSTNumber=data.GSTNumber,
                        Tax1Number=data.Tax1Number,
                        Tax2Number=data.Tax2Number,
                        Tax3Number=data.Tax3Number,
                        PanNumber=data.PanNumber,
                        BankName1=data.BankName1,
                        AccountName1=data.AccountName1,
                        AccountNo1=data.AccountNo1,
                        IBANOrIFSCCode1=data.IBANOrIFSCCode1,
                        BankName2=data.BankName2,
                        AccountName2=data.AccountName2,
                        AccountNo2=data.AccountNo2,
                        IBANOrIFSCCode2=data.IBANOrIFSCCode2,
                        IsActive=data.IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        OpeningBalance=data.OpeningBalance,
                        PartyImage=data.PartyImage
                        )
                    data.save(using=DataBase)
                    response_data = {
                        "status" : "true",
                        "title" : str(_("Successfully Updated")),
                        "message" : str(_("Customer Updated Successfully!")),
                        "redirect" : "true",
                        "redirect_url" : reverse('accounts:customers')
                    }
        else:
            print(form.errors)
            message = generate_form_errors(form,formset=False)
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("Form validation error")),
                "message" : str(message)
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = CustomerForm(instance=instance)
        countries = Country.objects.all()
        context = {
            "is_need_flatpickr" : False,
            "is_need_apexcharts" : False,
            "is_need_selectize" : False,
            "is_need_dashboard" : False,
            "is_need_bootstrap_wizard" : True,
            "is_need_form_wizard" : True,

            "title" : "Create Customer",
            "is_edit" : True,
            "form" : form,
            "countries" : countries,
            "instance" : instance
        }
        return render(request,"accounts/master/create_customer.html",context)


@login_required
def delete_customer(request,pk):
    today = datetime.date.today()
    DataBase = get_DataBase(request)
    Action = "D"
    if Parties.objects.using(DataBase).filter(pk=pk).exists():
        instance = Parties.objects.using(DataBase).get(pk=pk)

        Parties_Log.objects.using(DataBase).create(
            TransactionID=instance.PartyID,
            BranchID=instance.BranchID,
            PartyType=instance.PartyType,
            LedgerID=instance.LedgerID,
            PartyCode=instance.PartyCode,
            FirstName=instance.FirstName,
            LastName=instance.LastName,
            ContactPerson=instance.ContactPerson,
            Address1=instance.Address1,
            Address2=instance.Address2,
            Address3=instance.Address3,
            Address4=instance.Address4,
            City=instance.City,
            State=instance.State,
            Country=instance.Country,
            PostalCode=instance.PostalCode,
            OfficePhone=instance.OfficePhone,
            WorkPhone=instance.WorkPhone,
            Mobile=instance.Mobile,
            WebURL=instance.WebURL,
            Email=instance.Email,
            IsBillwiseApplicable=instance.IsBillwiseApplicable,
            CreditPeriod=instance.CreditPeriod,
            CreditLimit=instance.CreditLimit,
            PriceCategoryID=instance.PriceCategoryID,
            CurrencyID=instance.CurrencyID,
            InterestOrNot=instance.InterestOrNot,
            RouteID=instance.RouteID,
            VATNumber=instance.VATNumber,
            GSTNumber=instance.GSTNumber,
            Tax1Number=instance.Tax1Number,
            Tax2Number=instance.Tax2Number,
            Tax3Number=instance.Tax3Number,
            PanNumber=instance.PanNumber,
            BankName1=instance.BankName1,
            AccountName1=instance.AccountName1,
            AccountNo1=instance.AccountNo1,
            IBANOrIFSCCode1=instance.IBANOrIFSCCode1,
            BankName2=instance.BankName2,
            AccountName2=instance.AccountName2,
            AccountNo2=instance.AccountNo2,
            IBANOrIFSCCode2=instance.IBANOrIFSCCode2,
            IsActive=instance.IsActive,
            Action=Action,
            CreatedUserID=user.id,
            CreatedDate=today,
            UpdatedDate=today,
            OpeningBalance=instance.OpeningBalance,
            PartyImage=instance.PartyImage
            )
        instance.delete()

        if AccountLedger.objects.using(DataBase).filter(LedgerID=instance.LedgerID,BranchID=instance.BranchID).exists():
            accountLedgerInstance = AccountLedger.objects.using(DataBase).get(LedgerID=instance.LedgerID,BranchID=instance.BranchID)

            LedgerName = accountLedgerInstance.LedgerName
            LedgerCode = accountLedgerInstance.LedgerCode
            AccountGroupUnder = accountLedgerInstance.AccountGroupUnder
            OpeningBalance = accountLedgerInstance.OpeningBalance
            CrOrDr = accountLedgerInstance.CrOrDr
            Notes = accountLedgerInstance.Notes
            IsActive = accountLedgerInstance.IsActive
            IsDefault = accountLedgerInstance.IsDefault

            AccountLedger_Log.objects.using(DataBase).create(
                BranchID=instance.BranchID,
                TransactionID=instance.LedgerID,
                LedgerName=LedgerName,
                LedgerCode=LedgerCode,
                AccountGroupUnder=AccountGroupUnder,
                OpeningBalance=OpeningBalance,
                CrOrDr=CrOrDr,
                Notes=Notes,
                IsActive=IsActive,
                IsDefault=IsDefault,
                CreatedUserID=user.id,
                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                )

            accountLedgerInstance.delete()

        if LedgerPosting.objects.using(DataBase).filter(LedgerID=instance.LedgerID,BranchID=instance.BranchID).exists():
            ledgerPostInstance = LedgerPosting.objects.using(DataBase).get(LedgerID=instance.LedgerID,BranchID=instance.BranchID)

            LedgerPostingID = ledgerPostInstance.LedgerPostingID
            VoucherType = ledgerPostInstance.VoucherType
            Debit = ledgerPostInstance.Debit
            Credit = ledgerPostInstance.Credit
            IsActive = ledgerPostInstance.IsActive

            ledgerPostInstance.delete()

            LedgerPosting_Log.objects.using(DataBase).create(
                TransactionID=LedgerPostingID,
                BranchID=instance.BranchID,
                Date=today,
                VoucherMasterID=instance.LedgerID,
                VoucherType=VoucherType,
                LedgerID=instance.LedgerID,
                Debit=Debit,
                Credit=Credit,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=user.id,
                CreatedDate=today,
                UpdatedDate=today,
                )
               

        response_data = {
            "status" : "true",
            "title" : str(_("Successfully Deleted")),
            "message" : str(_("Customer Deleted Successfully.")),
            "redirect" : "true",
            "redirect_url" : reverse('accounts:customers')
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
            

    else:
        response_data = {
        'status' : 'false',
        'stable' : 'true',
        'title' : str(_("Customer is Not Fount!")),
        "message" : str(_("Customer is Not Fount!"))
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
        # bank ends here


@login_required
def create_supplier(request):
    DataBase = get_DataBase(request)

    today = datetime.date.today()
    if request.method == 'POST':

        form = CustomerForm(request.POST,request.FILES)
        if form.is_valid(): 
            CrODr = request.POST.get('CrODr')
            BranchID = 1
            Action = 'A'
            PartyType = "supplier"
            AccountGroupUnder = 29

            LedgerID = get_auto_idLedger(AccountLedger,BranchID,DataBase)
            PartyCode = get_PartyCode(Parties, BranchID,DataBase, PartyType)
            PartyID = get_auto_partyID(Parties,BranchID,DataBase)
            CreatedUserID = user.id

            data = form.save(commit=False)
            LedgerName = data.FirstName
            is_nameExist = False
            FirstNameLow = data.FirstName.lower()
            parties = Parties.objects.using(DataBase).filter(BranchID=BranchID)
            for party in parties:
                party_name = party.FirstName

                party_FirstName = party_name.lower()

                if FirstNameLow == party_FirstName:
                    is_nameExist = True


            if not is_nameExist:

                is_LedgernameExist = False

                LedgerNameLow = LedgerName.lower()

                accountLedgers = AccountLedger.objects.using(DataBase).filter(BranchID=BranchID)

                for accountLedger in accountLedgers:
                    ledger_name = accountLedger.LedgerName

                    ledgerName = ledger_name.lower()

                    if LedgerNameLow == ledgerName:
                        is_LedgernameExist = True

                if not is_LedgernameExist:
                    AccountLedger.objects.using(DataBase).create(
                        LedgerID=LedgerID,
                        BranchID=BranchID,
                        LedgerName=LedgerName,
                        LedgerCode=PartyCode,
                        AccountGroupUnder=AccountGroupUnder,
                        OpeningBalance=data.OpeningBalance,
                        CrOrDr=CrODr,
                        IsActive=data.IsActive,
                        CreatedDate=today,
                        UpdatedDate=today,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        )

                    AccountLedger_Log.objects.using(DataBase).create(
                        TransactionID=LedgerID,
                        BranchID=BranchID,
                        LedgerName=LedgerName,
                        LedgerCode=PartyCode,
                        AccountGroupUnder=AccountGroupUnder,
                        OpeningBalance=data.OpeningBalance,
                        CrOrDr=CrODr,
                        IsActive=data.IsActive,
                        CreatedDate=today,
                        UpdatedDate=today,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        )

                    if float(data.OpeningBalance) > 0:
                        Credit = 0
                        Debit = 0

                        if CrODr == "Cr":
                            Credit = data.OpeningBalance

                        elif CrODr == "Dr":
                            Debit = data.OpeningBalance

                        VoucherType = "LOB"

                        LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

                        LedgerPosting.objects.using(DataBase).create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=today,
                            VoucherMasterID=LedgerID,
                            VoucherType=VoucherType,
                            LedgerID=LedgerID,
                            Debit=Debit,
                            Credit=Credit,
                            IsActive=data.IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            )

                        LedgerPosting_Log.objects.using(DataBase).create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=today,
                            VoucherMasterID=LedgerID,
                            VoucherType=VoucherType,
                            LedgerID=LedgerID,
                            Debit=Debit,
                            Credit=Credit,
                            IsActive=data.IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            )

                else:
                    response_data = {
                        "status" : "false",
                        "title" : str(_("Supplier Already Exist")),
                        "message" : str(_("Supplier Name is Already exist with in the BranchID")),
                        "redirect" : "true",
                        "redirect_url" : reverse('accounts:create_supplier')
                    }

                data.PartyID = PartyID
                data.PartyCode = PartyCode
                data.PartyType = PartyType
                data.BranchID = BranchID
                data.LedgerID = LedgerID
                data.CreatedDate = today
                data.UpdatedDate = today
                data.CreatedUserID = CreatedUserID
                data.Action = Action

                Parties_Log.objects.using(DataBase).create(
                    TransactionID=PartyID,
                    BranchID=BranchID,
                    PartyType=PartyType,
                    LedgerID=LedgerID,
                    PartyCode=PartyCode,
                    FirstName=data.FirstName,
                    LastName=data.LastName,
                    ContactPerson=data.ContactPerson,
                    Address1=data.Address1,
                    Address2=data.Address2,
                    Address3=data.Address3,
                    Address4=data.Address4,
                    City=data.City,
                    State=data.State,
                    Country=data.Country,
                    PostalCode=data.PostalCode,
                    OfficePhone=data.OfficePhone,
                    WorkPhone=data.WorkPhone,
                    Mobile=data.Mobile,
                    WebURL=data.WebURL,
                    Email=data.Email,
                    IsBillwiseApplicable=data.IsBillwiseApplicable,
                    CreditPeriod=data.CreditPeriod,
                    CreditLimit=data.CreditLimit,
                    PriceCategoryID=data.PriceCategoryID,
                    CurrencyID=data.CurrencyID,
                    InterestOrNot=data.InterestOrNot,
                    RouteID=data.RouteID,
                    VATNumber=data.VATNumber,
                    GSTNumber=data.GSTNumber,
                    Tax1Number=data.Tax1Number,
                    Tax2Number=data.Tax2Number,
                    Tax3Number=data.Tax3Number,
                    PanNumber=data.PanNumber,
                    BankName1=data.BankName1,
                    AccountName1=data.AccountName1,
                    AccountNo1=data.AccountNo1,
                    IBANOrIFSCCode1=data.IBANOrIFSCCode1,
                    BankName2=data.BankName2,
                    AccountName2=data.AccountName2,
                    AccountNo2=data.AccountNo2,
                    IBANOrIFSCCode2=data.IBANOrIFSCCode2,
                    IsActive=data.IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    OpeningBalance=data.OpeningBalance,
                    PartyImage=data.PartyImage
                    )
                data.save(using=DataBase)
                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("Supplier Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('accounts:suppliers')
                }
            else:
                response_data = {
                    "status" : "false",
                    "title" : str(_("Supplier Already Exist")),
                    "message" : str(_("Supplier Name is Already exist with in the BranchID")),
                    "redirect" : "true",
                    "redirect_url" : reverse('accounts:create_supplier')
                }
        else:
            print(form.errors)
            message = generate_form_errors(form,formset=False)
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("Form validation error")),
                "message" : str(message)
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = CustomerForm()
        countries = Country.objects.all()
        context = {
            "is_need_flatpickr" : False,
            "is_need_apexcharts" : False,
            "is_need_selectize" : False,
            "is_need_dashboard" : False,
            "is_need_bootstrap_wizard" : True,
            "is_need_form_wizard" : True,

            "title" : "Create Customer",
            "form" : form,
            "countries" : countries,
        }
        return render(request,"accounts/master/create_supplier.html",context)

@login_required
def suppliers(request):
    DataBase = get_DataBase(request)
    instances = Parties.objects.using(DataBase).filter(BranchID=1,PartyType="supplier")
    context = {
        "is_need_flatpickr" : False,
        "is_need_apexcharts" : False,
        "is_need_selectize" : False,
        "is_need_dashboard" : False,

        'instances' : instances,
        'title' : 'Supplier'
    }
    return render(request,"accounts/master/suppliers.html",context)


@login_required
def view_supplier(request,pk):
    DataBase = get_DataBase(request)

    instance = Parties.objects.using(DataBase).get(pk=pk)
    context = {
        "is_need_flatpickr" : False,
        "is_need_apexcharts" : False,
        "is_need_selectize" : False,
        "is_need_dashboard" : False,

        'instance' : instance,
        'title' : 'Supplier'
    }
    return render(request,"accounts/master/supplier.html",context)


@login_required
def edit_supplier(request,pk):
    DataBase = get_DataBase(request)

    instance = Parties.objects.using(DataBase).get(pk=pk)
    LedgerID = instance.LedgerID
    instanceFirstName = instance.FirstName
    BranchID = instance.BranchID
    accountLedgerInstance = AccountLedger.objects.using(DataBase).get(LedgerID=LedgerID,BranchID=BranchID)
    LedgerCode = accountLedgerInstance.LedgerCode

    if LedgerPosting.objects.using(DataBase).filter(LedgerID=LedgerID,BranchID=BranchID,VoucherType="LOB").exists():
        ledgerPostInstance = LedgerPosting.objects.using(DataBase).get(LedgerID=LedgerID,BranchID=BranchID,VoucherType="LOB")
        ledgerPostInstance.delete()

    PartyID = instance.PartyID
    PartyCode = instance.PartyCode
    PartyType = instance.PartyType
    CreatedUserID = user.id

    Action = 'M'

    today = datetime.date.today()
    if request.method == 'POST':

        form = CustomerForm(request.POST,request.FILES,instance=instance)
        if form.is_valid(): 
            CrODr = request.POST.get('CrODr')
            AccountGroupUnder = 10

            data = form.save(commit=False)
            LedgerName = data.FirstName
            is_nameExist = False
            party_ok = False

            FirstNameLow = data.FirstName.lower()

            parties = Parties.objects.using(DataBase).filter(BranchID=BranchID)

            for party in parties:
                party_name = party.FirstName

                party_FirstName = party_name.lower()

                if FirstNameLow == party_FirstName:
                    is_nameExist = True

                if instanceFirstName.lower() == FirstNameLow:

                    party_ok = True


            if  party_ok:

                accountLedgerInstance.LedgerName = LedgerName
                            # accountLedgerInstance.LedgerCode = LedgerCode
                accountLedgerInstance.AccountGroupUnder = AccountGroupUnder
                accountLedgerInstance.OpeningBalance = data.OpeningBalance
                accountLedgerInstance.CrOrDr = CrODr
                accountLedgerInstance.IsActive = data.IsActive
                accountLedgerInstance.Action = Action
                accountLedgerInstance.CreatedUserID = CreatedUserID
                accountLedgerInstance.UpdatedDate = today
                accountLedgerInstance.save()

                AccountLedger_Log.objects.using(DataBase).create(
                    BranchID=BranchID,
                    TransactionID=LedgerID,
                    LedgerName=LedgerName,
                    LedgerCode=LedgerCode,
                    AccountGroupUnder=AccountGroupUnder,
                    OpeningBalance=data.OpeningBalance,
                    CrOrDr=CrODr,
                    IsActive=data.IsActive,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    Action=Action,
                    )

                if float(data.OpeningBalance) > 0:
                    Credit = 0
                    Debit = 0

                    if CrODr == "Cr":
                        Credit = data.OpeningBalance

                    elif CrODr == "Dr":
                        Debit = data.OpeningBalance

                    VoucherType = "LOB"

                    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

                    LedgerPosting.objects.using(DataBase).create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=today,
                        VoucherMasterID=LedgerID,
                        VoucherType=VoucherType,
                        LedgerID=LedgerID,
                        Debit=Debit,
                        Credit=Credit,
                        IsActive=data.IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        )

                    LedgerPosting_Log.objects.using(DataBase).create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=today,
                        VoucherMasterID=LedgerID,
                        VoucherType=VoucherType,
                        LedgerID=LedgerID,
                        Debit=Debit,
                        Credit=Credit,
                        IsActive=data.IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        )

                data.UpdatedDate = today
                data.CreatedUserID = CreatedUserID
                data.Action = Action
                data.PartyID = PartyID
                data.PartyCode = PartyCode
                data.PartyType = PartyType
                data.BranchID = BranchID
                data.LedgerID = LedgerID
                Parties_Log.objects.using(DataBase).create(
                    TransactionID=PartyID,
                    BranchID=BranchID,
                    PartyType=PartyType,
                    LedgerID=LedgerID,
                    PartyCode=PartyCode,
                    FirstName=data.FirstName,
                    LastName=data.LastName,
                    ContactPerson=data.ContactPerson,
                    Address1=data.Address1,
                    Address2=data.Address2,
                    Address3=data.Address3,
                    Address4=data.Address4,
                    City=data.City,
                    State=data.State,
                    Country=data.Country,
                    PostalCode=data.PostalCode,
                    OfficePhone=data.OfficePhone,
                    WorkPhone=data.WorkPhone,
                    Mobile=data.Mobile,
                    WebURL=data.WebURL,
                    Email=data.Email,
                    IsBillwiseApplicable=data.IsBillwiseApplicable,
                    CreditPeriod=data.CreditPeriod,
                    CreditLimit=data.CreditLimit,
                    PriceCategoryID=data.PriceCategoryID,
                    CurrencyID=data.CurrencyID,
                    InterestOrNot=data.InterestOrNot,
                    RouteID=data.RouteID,
                    VATNumber=data.VATNumber,
                    GSTNumber=data.GSTNumber,
                    Tax1Number=data.Tax1Number,
                    Tax2Number=data.Tax2Number,
                    Tax3Number=data.Tax3Number,
                    PanNumber=data.PanNumber,
                    BankName1=data.BankName1,
                    AccountName1=data.AccountName1,
                    AccountNo1=data.AccountNo1,
                    IBANOrIFSCCode1=data.IBANOrIFSCCode1,
                    BankName2=data.BankName2,
                    AccountName2=data.AccountName2,
                    AccountNo2=data.AccountNo2,
                    IBANOrIFSCCode2=data.IBANOrIFSCCode2,
                    IsActive=data.IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    OpeningBalance=data.OpeningBalance,
                    PartyImage=data.PartyImage
                    )
                data.save(using=DataBase)
                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Updated")),
                    "message" : str(_("Suppliers Updated Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('accounts:suppliers')
                }
            else:
                if is_nameExist:
                    response_data = {
                        "status" : "false",
                        "title" : str(_("Suppliers Already Exist")),
                        "message" : str(_("Suppliers Name is Already exist with in the BranchID")),
                        "redirect" : "true",
                        "redirect_url" : reverse('accounts:edit_supplier',kwargs={"pk":instance.pk}),
                    }

                else:
                    accountLedgerInstance.LedgerName = LedgerName
                    # accountLedgerInstance.LedgerCode = LedgerCode
                    accountLedgerInstance.AccountGroupUnder = AccountGroupUnder
                    accountLedgerInstance.OpeningBalance = data.OpeningBalance
                    accountLedgerInstance.CrOrDr = CrODr
                    accountLedgerInstance.IsActive = data.IsActive
                    accountLedgerInstance.Action = Action
                    accountLedgerInstance.CreatedUserID = CreatedUserID
                    accountLedgerInstance.UpdatedDate = today
                    accountLedgerInstance.save()

                    AccountLedger_Log.objects.using(DataBase).create(
                        BranchID=BranchID,
                        TransactionID=LedgerID,
                        LedgerName=LedgerName,
                        LedgerCode=LedgerCode,
                        AccountGroupUnder=AccountGroupUnder,
                        OpeningBalance=data.OpeningBalance,
                        CrOrDr=CrODr,
                        IsActive=data.IsActive,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        Action=Action,
                        )

                    if float(data.OpeningBalance) > 0:
                        Credit = 0
                        Debit = 0

                        if CrODr == "Cr":
                            Credit = data.OpeningBalance

                        elif CrODr == "Dr":
                            Debit = data.OpeningBalance

                        VoucherType = "LOB"

                        LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

                        LedgerPosting.objects.using(DataBase).create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=today,
                            VoucherMasterID=LedgerID,
                            VoucherType=VoucherType,
                            LedgerID=LedgerID,
                            Debit=Debit,
                            Credit=Credit,
                            IsActive=data.IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            )

                        LedgerPosting_Log.objects.using(DataBase).create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=today,
                            VoucherMasterID=LedgerID,
                            VoucherType=VoucherType,
                            LedgerID=LedgerID,
                            Debit=Debit,
                            Credit=Credit,
                            IsActive=data.IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            )

                    data.UpdatedDate = today
                    data.CreatedUserID = CreatedUserID
                    data.Action = Action
                    data.PartyID = PartyID
                    data.PartyCode = PartyCode
                    data.PartyType = PartyType
                    data.BranchID = BranchID
                    data.LedgerID = LedgerID

                    Parties_Log.objects.using(DataBase).create(
                        TransactionID=PartyID,
                        BranchID=BranchID,
                        PartyType=PartyType,
                        LedgerID=LedgerID,
                        PartyCode=PartyCode,
                        FirstName=data.FirstName,
                        LastName=data.LastName,
                        ContactPerson=data.ContactPerson,
                        Address1=data.Address1,
                        Address2=data.Address2,
                        Address3=data.Address3,
                        Address4=data.Address4,
                        City=data.City,
                        State=data.State,
                        Country=data.Country,
                        PostalCode=data.PostalCode,
                        OfficePhone=data.OfficePhone,
                        WorkPhone=data.WorkPhone,
                        Mobile=data.Mobile,
                        WebURL=data.WebURL,
                        Email=data.Email,
                        IsBillwiseApplicable=data.IsBillwiseApplicable,
                        CreditPeriod=data.CreditPeriod,
                        CreditLimit=data.CreditLimit,
                        PriceCategoryID=data.PriceCategoryID,
                        CurrencyID=data.CurrencyID,
                        InterestOrNot=data.InterestOrNot,
                        RouteID=data.RouteID,
                        VATNumber=data.VATNumber,
                        GSTNumber=data.GSTNumber,
                        Tax1Number=data.Tax1Number,
                        Tax2Number=data.Tax2Number,
                        Tax3Number=data.Tax3Number,
                        PanNumber=data.PanNumber,
                        BankName1=data.BankName1,
                        AccountName1=data.AccountName1,
                        AccountNo1=data.AccountNo1,
                        IBANOrIFSCCode1=data.IBANOrIFSCCode1,
                        BankName2=data.BankName2,
                        AccountName2=data.AccountName2,
                        AccountNo2=data.AccountNo2,
                        IBANOrIFSCCode2=data.IBANOrIFSCCode2,
                        IsActive=data.IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        OpeningBalance=data.OpeningBalance,
                        PartyImage=data.PartyImage
                        )
                    data.save(using=DataBase)
                    response_data = {
                        "status" : "true",
                        "title" : str(_("Successfully Updated")),
                        "message" : str(_("Customer Updated Successfully!")),
                        "redirect" : "true",
                        "redirect_url" : reverse('accounts:suppliers')
                    }
        else:
            print(form.errors)
            message = generate_form_errors(form,formset=False)
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("Form validation error")),
                "message" : str(message)
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = CustomerForm(instance=instance)
        countries = Country.objects.all()
        context = {
            "is_need_flatpickr" : False,
            "is_need_apexcharts" : False,
            "is_need_selectize" : False,
            "is_need_dashboard" : False,
            "is_need_bootstrap_wizard" : True,
            "is_need_form_wizard" : True,

            "title" : "Create Supplier",
            "form" : form,
            "countries" : countries,
        }
        return render(request,"accounts/master/create_supplier.html",context)


@login_required
def delete_supplier(request,pk):
    today = datetime.date.today()
    DataBase = get_DataBase(request)
    Action = "D"
    if Parties.objects.using(DataBase).filter(pk=pk).exists():
        instance = Parties.objects.using(DataBase).get(pk=pk)

        Parties_Log.objects.using(DataBase).create(
            TransactionID=instance.PartyID,
            BranchID=instance.BranchID,
            PartyType=instance.PartyType,
            LedgerID=instance.LedgerID,
            PartyCode=instance.PartyCode,
            FirstName=instance.FirstName,
            LastName=instance.LastName,
            ContactPerson=instance.ContactPerson,
            Address1=instance.Address1,
            Address2=instance.Address2,
            Address3=instance.Address3,
            Address4=instance.Address4,
            City=instance.City,
            State=instance.State,
            Country=instance.Country,
            PostalCode=instance.PostalCode,
            OfficePhone=instance.OfficePhone,
            WorkPhone=instance.WorkPhone,
            Mobile=instance.Mobile,
            WebURL=instance.WebURL,
            Email=instance.Email,
            IsBillwiseApplicable=instance.IsBillwiseApplicable,
            CreditPeriod=instance.CreditPeriod,
            CreditLimit=instance.CreditLimit,
            PriceCategoryID=instance.PriceCategoryID,
            CurrencyID=instance.CurrencyID,
            InterestOrNot=instance.InterestOrNot,
            RouteID=instance.RouteID,
            VATNumber=instance.VATNumber,
            GSTNumber=instance.GSTNumber,
            Tax1Number=instance.Tax1Number,
            Tax2Number=instance.Tax2Number,
            Tax3Number=instance.Tax3Number,
            PanNumber=instance.PanNumber,
            BankName1=instance.BankName1,
            AccountName1=instance.AccountName1,
            AccountNo1=instance.AccountNo1,
            IBANOrIFSCCode1=instance.IBANOrIFSCCode1,
            BankName2=instance.BankName2,
            AccountName2=instance.AccountName2,
            AccountNo2=instance.AccountNo2,
            IBANOrIFSCCode2=instance.IBANOrIFSCCode2,
            IsActive=instance.IsActive,
            Action=Action,
            CreatedUserID=user.id,
            CreatedDate=today,
            UpdatedDate=today,
            OpeningBalance=instance.OpeningBalance,
            PartyImage=instance.PartyImage
            )
        instance.delete()

        if AccountLedger.objects.using(DataBase).filter(LedgerID=instance.LedgerID,BranchID=instance.BranchID).exists():
            accountLedgerInstance = AccountLedger.objects.using(DataBase).get(LedgerID=instance.LedgerID,BranchID=instance.BranchID)

            LedgerName = accountLedgerInstance.LedgerName
            LedgerCode = accountLedgerInstance.LedgerCode
            AccountGroupUnder = accountLedgerInstance.AccountGroupUnder
            OpeningBalance = accountLedgerInstance.OpeningBalance
            CrOrDr = accountLedgerInstance.CrOrDr
            Notes = accountLedgerInstance.Notes
            IsActive = accountLedgerInstance.IsActive
            IsDefault = accountLedgerInstance.IsDefault

            AccountLedger_Log.objects.using(DataBase).create(
                BranchID=instance.BranchID,
                TransactionID=instance.LedgerID,
                LedgerName=LedgerName,
                LedgerCode=LedgerCode,
                AccountGroupUnder=AccountGroupUnder,
                OpeningBalance=OpeningBalance,
                CrOrDr=CrOrDr,
                Notes=Notes,
                IsActive=IsActive,
                IsDefault=IsDefault,
                CreatedUserID=user.id,
                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                )

            accountLedgerInstance.delete()

        if LedgerPosting.objects.using(DataBase).filter(LedgerID=instance.LedgerID,BranchID=instance.BranchID).exists():
            ledgerPostInstance = LedgerPosting.objects.using(DataBase).get(LedgerID=instance.LedgerID,BranchID=instance.BranchID)

            LedgerPostingID = ledgerPostInstance.LedgerPostingID
            VoucherType = ledgerPostInstance.VoucherType
            Debit = ledgerPostInstance.Debit
            Credit = ledgerPostInstance.Credit
            IsActive = ledgerPostInstance.IsActive

            ledgerPostInstance.delete()

            LedgerPosting_Log.objects.using(DataBase).create(
                TransactionID=LedgerPostingID,
                BranchID=instance.BranchID,
                Date=today,
                VoucherMasterID=instance.LedgerID,
                VoucherType=VoucherType,
                LedgerID=instance.LedgerID,
                Debit=Debit,
                Credit=Credit,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=user.id,
                CreatedDate=today,
                UpdatedDate=today,
                )
               

        response_data = {
            "status" : "true",
            "title" : str(_("Successfully Deleted")),
            "message" : str(_("Supplier Deleted Successfully.")),
            "redirect" : "true",
            "redirect_url" : reverse('accounts:customers')
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
            

    else:
        response_data = {
        'status' : 'false',
        'stable' : 'true',
        'title' : str(_("Supplier is Not Fount!")),
        "message" : str(_("Supplier is Not Fount!"))
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
        # bank ends here


@login_required
def create_transactionType(request):
    DataBase = get_DataBase(request)
    today = datetime.date.today()

    if request.method == 'POST':
        form = TransactionTypesForm(request.POST)

        if form.is_valid(): 
            data = form.save(commit=False)

            is_nameExist = False
            NameLow = data.Name.lower()
            transactions = TransactionTypes.objects.using(DataBase).filter(BranchID=1)

            for trans in transactions:
                trans_name = trans.Name
                Name = trans_name.lower()

                if NameLow == Name:
                    is_nameExist = True

            if not is_nameExist:
                data.BranchID = 1
                data.CreatedDate = today
                data.UpdatedDate=today
                data.Action = "A"
                data.CreatedUserID = user.id
                data.TransactionTypesID = get_auto_TransactionTypesID(TransactionTypes,DataBase,data.BranchID)

                TransactionTypes_Log.objects.using(DataBase).create(
                    TransactionID=data.TransactionTypesID,
                    BranchID=data.BranchID,
                    Action="A",
                    MasterTypeID=data.MasterTypeID,
                    Name=data.Name,
                    Notes=data.Notes,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=data.CreatedUserID,
                    IsDefault=data.IsDefault
                    )

                data.save(using=DataBase)

                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("Transaction Types Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('accounts:transactionTypes')
                }
            else:
                response_data = {
                    "status" : "false",
                    "title" : str(_("Transaction Type Already Exist")),
                    "message" : str(_("Transaction Type Name is Already exist with in the BranchID")),
                    "redirect" : "true",
                    "redirect_url" : reverse('accounts:create_transactionType')
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
        form = TransactionTypesForm()
        context = {
            "is_need_flatpickr" : False,
            "is_need_apexcharts" : False,
            "is_need_selectize" : False,
            "is_need_dashboard" : False,

            "title" : "Create Transaction Type",
            "form" : form,
        }
        return render(request,"accounts/master/create_transaction_type.html",context)


@login_required
def transactionTypes(request):
    DataBase = get_DataBase(request)

    instances = TransactionTypes.objects.using(DataBase).filter(BranchID=1)
    query = request.GET.get("q")
    if query:
        instances = instances.filter(Q(Name__icontains=query))
    context = {
        "is_need_flatpickr" : False,
        "is_need_apexcharts" : False,
        "is_need_selectize" : False,
        "is_need_dashboard" : False,

        'instances' : instances,
        'title' : 'Transaction Types'
    }
    return render(request,"accounts/master/transactionTypes.html",context)


@login_required
def view_transactionType(request,pk):
    DataBase = get_DataBase(request)

    instance = TransactionTypes.objects.using(DataBase).get(pk=pk)
    context = {
        "is_need_flatpickr" : False,
        "is_need_apexcharts" : False,
        "is_need_selectize" : False,
        "is_need_dashboard" : False,

        'instance' : instance,
        'title' : 'TransactionType'
    }
    return render(request,"accounts/master/transactionType.html",context)


@login_required
def edit_transactionType(request,pk):
    DataBase = get_DataBase(request)
    today = datetime.date.today()

    instance = TransactionTypes.objects.using(DataBase).get(pk=pk)
    TransactionTypesID = instance.TransactionTypesID
    BranchID = instance.BranchID
    instanceName = instance.Name
    if request.method == 'POST':
        form = TransactionTypesForm(request.POST,instance=instance)

        if form.is_valid(): 
            data = form.save(commit=False)
            Name = data.Name
            is_nameExist = False
            trans_ok = False

            NameLow = data.Name.lower()
            trans = TransactionTypes.objects.using(DataBase).filter(BranchID=BranchID)

            for tran in trans:
                tran_name = tran.Name
                Name = tran_name.lower()

                if NameLow == Name:
                    is_nameExist = True

                if instanceName.lower() == NameLow:
                    trans_ok = True

            if trans_ok:
                data.UpdatedDate=today
                data.Action = "M"
                data.CreatedUserID = user.id

                TransactionTypes_Log.objects.using(DataBase).create(
                    TransactionID=TransactionTypesID,
                    BranchID=BranchID,
                    Action="M",
                    MasterTypeID=data.MasterTypeID,
                    Name=data.Name,
                    Notes=data.Notes,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=data.CreatedUserID,
                    IsDefault=data.IsDefault
                    )

                data.save(using=DataBase)

                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Updated")),
                    "message" : str(_("Transaction Types Updated Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('accounts:transactionTypes')
                }
            else:
                response_data = {
                    "status" : "false",
                    "title" : str(_("Transaction Type Already Exist")),
                    "message" : str(_("Transaction Type Name is Already exist with in the BranchID")),
                    "redirect" : "true",
                    "redirect_url" : reverse('accounts:edit_transactionType',kwargs={"pk":instance.pk}),
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
        form = TransactionTypesForm(instance=instance)
        context = {
            "is_need_flatpickr" : False,
            "is_need_apexcharts" : False,
            "is_need_selectize" : False,
            "is_need_dashboard" : False,

            "title" : "Create Transaction Type",
            "form" : form,
        }
        return render(request,"accounts/master/create_transaction_type.html",context)


@login_required
def delete_transactionType(request,pk):
    DataBase = get_DataBase(request)

    today = datetime.date.today()    
    instance = TransactionTypes.objects.using(DataBase).get(pk=pk)

    TransactionTypes_Log.objects.using(DataBase).create(
        TransactionID=instance.TransactionTypesID,
        BranchID=instance.BranchID,
        Action="D",
        MasterTypeID=instance.MasterTypeID,
        Name=instance.Name,
        Notes=instance.Notes,
        CreatedDate=today,
        UpdatedDate=today,
        CreatedUserID=user.id,
        IsDefault=instance.IsDefault
        )
    instance.delete()
    
    response_data = {
        "status" : "true",
        "title" : str(_("Successfully Deleted")),
        "message" : str(_("Transaction Types Deleted Successfully.")),
        "redirect" : "true",
        "redirect_url" : reverse('accounts:transactionTypes')
    }
    return HttpResponse(json.dumps(response_data), content_type='application/javascript')


@login_required
def trialBalance_webView(request):
    DataBase = get_DataBase(request)
    today = datetime.date.today()
    ToDate = request.GET.get('ToDate')
    if ToDate == None:
        ToDate = today

    test_arr = []
    TotalDebit = 0
    TotalCredit = 0
    instances = LedgerPosting.objects.using(DataBase).filter(BranchID=1,Date__lte=ToDate)
    for i in instances:
        TotalDebit += i.Debit
        TotalCredit += i.Credit
    ledger_ids = instances.values_list('LedgerID')
    for ledger_id in ledger_ids:
        if ledger_id[0] not in test_arr:
            test_arr.append(ledger_id[0])

    account_ledgers = AccountLedger.objects.using(DataBase).filter(LedgerID__in=test_arr).order_by('id')
    
    context = {
        "instances" : instances,
        "account_ledgers" : account_ledgers,
        "ToDate" : ToDate,
        "TotalDebit" : TotalDebit,
        "TotalCredit" : TotalCredit,
        "title" : "Trial Balance",       
    }
    return render(request,'accounts/reports/trialBalance.html',context)


@login_required
def ledgerReport_webView(request):
    DataBase = get_DataBase(request)
    # LedgerID = request.GET.get('LedgerID')
    FromDate = request.GET.get('FromDate')
    ToDate = request.GET.get('ToDate')
    Ledger = request.GET.get('Ledger')
    # pk = request.GET.get('pk')

    test_arr = []
    TotalDebit = 0
    TotalCredit = 0
    is_LedgerWise = False
    instances = None
    BalanceArray = []
    ledgerWiseList = AccountLedger.objects.using(DataBase).filter(BranchID=1)

    if LedgerPosting.objects.using(DataBase).filter(BranchID=1).exists():
        instances = LedgerPosting.objects.using(DataBase).filter(BranchID=1)
        ledger_ids = instances.values_list('LedgerID')
        for ledger_id in ledger_ids:
            if ledger_id[0] not in test_arr:
                test_arr.append(ledger_id[0])
        
    account_ledgers = AccountLedger.objects.using(DataBase).filter(LedgerID__in=test_arr).order_by('id')
    Balance = 0
    for i in account_ledgers:
        LedgerID = i.LedgerID
        BranchID = i.BranchID
        
        ledgerPostInstances = LedgerPosting.objects.using(DataBase).filter(LedgerID=LedgerID,BranchID=BranchID).order_by('id')

        # if not pk == "all":
        try:
            if ledgerPostInstances.using(DataBase).filter(Date__gte=FromDate,Date__lte=ToDate,LedgerID=Ledger).exists():
                ledgerPostInstances = ledgerPostInstances.using(DataBase).filter(Date__gte=FromDate,Date__lte=ToDate,LedgerID=Ledger).order_by('id')
            else:
                is_LedgerWise = True
        except:
            pass

        Debit = 0
        Credit = 0
        for lp in ledgerPostInstances:
            Debit += lp.Debit
            Credit += lp.Credit

        Balance = (float(Balance) + float(Debit)) - float(Credit)
        BalanceArray.append(Balance)

    
    context = {
        "instances" : instances,
        "FromDate" : FromDate,
        "ToDate" : ToDate,
        "TotalDebit" : TotalDebit,
        "TotalCredit" : TotalCredit,
        "account_ledgers" : account_ledgers,
        "is_LedgerWise" : is_LedgerWise,
        "ledgerWiseList" : ledgerWiseList,
        "data" : zip(account_ledgers, BalanceArray),
        "title" : "Ledger Report",       
    }
    return render(request,'accounts/reports/ledgerReport.html',context)


@login_required
def ledgerReport_LedgerWise(request):
    user = request.user
    customer_instance = get_object_or_404(CustomerUser.objects.using(DataBase).filter(user=user))
    db_id = customer_instance.databaseid
    datastore = get_object_or_404(DatabaseStore.using(DataBase).objects.filter(id=db_id))
    DataBase = datastore.DefaultDatabase
    FromDate = request.GET.get('FromDate')
    ToDate = request.GET.get('ToDate')
    Ledger = request.GET.get('Ledger')

    ledger = AccountLedger.objects.get(BranchID=1,LedgerID=Ledger)
    ledgerName = ledger.LedgerName
    ledgerId = ledger.LedgerID
    

    ledgerWiseList = AccountLedger.objects.using(DataBase).filter(BranchID=1)
    BalanceArray = []
    Balance = 0
    is_LedgerWise = False
    ledgerPostInstances = []
    
    try:
        if LedgerPosting.objects.using(DataBase).filter(Date__gte=FromDate,Date__lte=ToDate,LedgerID=Ledger).exists():
            ledgerPostInstances = LedgerPosting.objects.using(DataBase).filter(Date__gte=FromDate,Date__lte=ToDate,LedgerID=Ledger).order_by('id')
            
            for i in ledgerPostInstances:
                Debit = i.Debit
                Credit = i.Credit
                Balance = (float(Balance) + float(Debit)) - float(Credit)
                BalanceArray.append(Balance)
            is_LedgerWise = True
        else:
            is_LedgerWise = False
            ledgerPostInstances = []
    except:
        pass

    context = {
        "FromDate" : FromDate,
        "is_LedgerWise" : is_LedgerWise,
        "ToDate" : ToDate,
        "ledger_name" : ledgerName,
        "ledgerId" : ledgerId,
        "ledgerPostInstances" : ledgerPostInstances,
        "ledgerWiseList" : ledgerWiseList,
        "BalanceArray" : BalanceArray,
        "data" : zip(ledgerPostInstances, BalanceArray),
        "title" : "Ledger Report Ledgerwise", 
    }
    return render(request,'accounts/reports/ledgerReportExp.html',context)


@login_required
def profitAndLoss_webView(request):
    DataBase = get_DataBase(request)
    FromDate = request.GET.get('FromDate')
    ToDate = request.GET.get('ToDate')

    test_arr = []
    TotalDebit = 0
    TotalCredit = 0
    instances = None
    ledgerPostInstances = []

    direct_expenses = []
    in_direct_expenses = []
    direct_income = []
    in_direct_income = []


    if not FromDate == None and not ToDate == None:
        if LedgerPosting.objects.using(DataBase).filter(BranchID=1,Date__gte=FromDate,Date__lte=ToDate).exists():
            ledgerPostInstances = LedgerPosting.objects.using(DataBase).filter(BranchID=1,Date__gte=FromDate,Date__lte=ToDate).order_by('id')
            ledger_ids = ledgerPostInstances.values_list('LedgerID')
            for ledger_id in ledger_ids:
                if ledger_id[0] not in test_arr:
                    test_arr.append(ledger_id[0])
        else:
            ledgerPostInstances = []
            
        account_ledgers = AccountLedger.objects.using(DataBase).filter(LedgerID__in=test_arr).order_by('id')

        for i in account_ledgers:
            LedgerID = i.LedgerID
            BranchID = i.BranchID
            AccountGroupUnder = i.AccountGroupUnder

            check = check_groupforProfitandLoss(AccountGroupUnder)

            if check == "Indirect Expenses":
                indirect_expense = ledgerPostInstances.using(DataBase).filter(LedgerID=LedgerID,BranchID=BranchID)
                in_direct_expenses.append(indirect_expense)

    else:
        ledger_all = LedgerPosting.objects.using(DataBase).filter(BranchID=1)
        ledger_ids = ledger_all.values_list('LedgerID')

        for ledger_id in ledger_ids:
            if ledger_id[0] not in test_arr:
                test_arr.append(ledger_id[0])

        account_ledgers = AccountLedger.objects.using(DataBase).filter(LedgerID__in=test_arr).order_by('id')

        for i in account_ledgers:
            LedgerID = i.LedgerID
            BranchID = i.BranchID
            AccountGroupUnder = i.AccountGroupUnder

            check = check_groupforProfitandLoss(AccountGroupUnder)

            if check == "Indirect Expenses":
                indirect_expense = ledger_all.using(DataBase).filter(LedgerID=LedgerID,BranchID=BranchID)
                in_direct_expenses.append(indirect_expense)

            elif check == "Direct Expenses":
                direct_expense = ledger_all.using(DataBase).filter(LedgerID=LedgerID,BranchID=BranchID)
                direct_expenses.append(direct_expense)

            elif check == "Direct Income":
                direct_Income = ledger_all.using(DataBase).filter(LedgerID=LedgerID,BranchID=BranchID)
                direct_income.append(direct_Income)

            elif check == "Indirect Income":
                indirect_income = ledger_all.using(DataBase).filter(LedgerID=LedgerID,BranchID=BranchID)
                in_direct_income.append(indirect_income)

  
    context = {
        "in_direct_expenses" : in_direct_expenses,
        "direct_expenses" : direct_expenses,
        "direct_income" : direct_income,
        "in_direct_income" : in_direct_income,
        "FromDate" : FromDate,
        "ToDate" : ToDate,
        "title" : "Profit and Loss",       
    }
    return render(request,'accounts/reports/profitAndLoss.html',context)


@login_required
def create_cash_payment(request):
    from api.v1.payments.functions import get_auto_id, get_auto_idMaster
    DataBase = get_DataBase(request)

    PaymentDetailsFormset = formset_factory(PaymentDetailsForm)
    today = datetime.date.today()
    if request.method == 'POST':
        form = PaymentMasterForm(request.POST,request.FILES)
        payment_details_formset = PaymentDetailsFormset(request.POST,prefix='payment_details_formset')
        if form.is_valid() and payment_details_formset.is_valid(): 
            data = form.save(commit=False)
            BranchID = 1
            data.BranchID = BranchID
            data.Action = 'A'
            data.PaymentMasterID = get_auto_idMaster(PaymentMaster,BranchID,DataBase)
            data.FinancialYearID = 1
            data.VoucherType = 'CP'
            data.VoucherNo  = generateVoucherNo(data.VoucherType, data.BranchID, DataBase)
            data.EmployeeID = request.user.id
            data.CreatedUserID = request.user.id
            data.CreatedDate = today
            data.UpdatedDate = today

            VoucherNoLow = data.VoucherNo.lower()
            is_voucherExist = False
            insts = PaymentMaster.objects.using(DataBase).filter(BranchID=BranchID)
            if insts:
                for i in insts:
                    voucher_no = i.VoucherNo
                    voucherNo = voucher_no.lower()
                    if VoucherNoLow == voucherNo:
                        is_voucherExist = True

            if not is_voucherExist:

                
                PaymentMaster_Log.objects.using(DataBase).create(
                    TransactionID=data.PaymentMasterID,
                    BranchID=data.BranchID,
                    Action=data.Action,
                    VoucherNo=data.VoucherNo,
                    VoucherType=data.VoucherType,
                    LedgerID=data.LedgerID,
                    EmployeeID=data.EmployeeID,
                    PaymentNo=data.VoucherNo,
                    FinancialYearID=data.FinancialYearID,
                    Date=data.Date,
                    TotalAmount=data.TotalAmount,
                    Notes=data.Notes,
                    IsActive=data.IsActive,
                    CreatedDate=data.CreatedDate,
                    UpdatedDate=data.UpdatedDate,
                    CreatedUserID=data.CreatedUserID
                    )
                data.save(using=DataBase)

                for f in payment_details_formset:
                    PaymentGateway = f.cleaned_data['PaymentGateway']
                    RefferenceNo = f.cleaned_data['RefferenceNo']
                    CardNetwork = f.cleaned_data['CardNetwork']
                    PaymentStatus = f.cleaned_data['PaymentStatus']
                    DueDate = f.cleaned_data['DueDate']
                    LedgerID = f.cleaned_data['LedgerID']
                    Amount = f.cleaned_data['Amount']
                    Balance = f.cleaned_data['Balance']
                    Discount = f.cleaned_data['Discount']
                    NetAmount = f.cleaned_data['NetAmount']
                    Narration = f.cleaned_data['Narration']

                    transactionType = TransactionTypes.objects.using(DataBase).get(Name="Cash")
                    transactionTypeID = transactionType.TransactionTypesID
                    PaymentGateway = transactionTypeID
                    PaymentDetailsID = get_auto_id(PaymentDetails,BranchID,DataBase)
                
                    PaymentDetails.objects.using(DataBase).create(
                        PaymentDetailsID=PaymentDetailsID,
                        BranchID=BranchID,
                        Action=data.Action,
                        PaymentMasterID=data.PaymentMasterID,
                        payment_master=data,
                        PaymentGateway=PaymentGateway,
                        RefferenceNo=RefferenceNo,
                        CardNetwork=CardNetwork,
                        PaymentStatus=PaymentStatus,
                        DueDate=DueDate,
                        LedgerID=LedgerID,
                        Amount=Amount,
                        Balance=Balance,
                        Discount=Discount,
                        NetAmount=NetAmount,
                        Narration=Narration,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        CreatedUserID=data.CreatedUserID,
                        )
                    PaymentDetails_Log.objects.using(DataBase).create(
                        TransactionID=PaymentDetailsID,
                        BranchID=data.BranchID,
                        Action=data.Action,
                        PaymentMasterID=data.PaymentMasterID,
                        PaymentGateway=PaymentGateway,
                        RefferenceNo=RefferenceNo,
                        CardNetwork=CardNetwork,
                        PaymentStatus=PaymentStatus,
                        DueDate=DueDate,
                        LedgerID=LedgerID,
                        Amount=Amount,
                        Balance=Balance,
                        Discount=Discount,
                        NetAmount=NetAmount,
                        Narration=Narration,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        CreatedUserID=data.CreatedUserID,
                        )

                    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)


                    LedgerPosting.objects.using(DataBase).create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.PaymentMasterID,
                        VoucherDetailID=PaymentDetailsID,
                        VoucherType=data.VoucherType,
                        VoucherNo=data.VoucherNo,
                        LedgerID=data.LedgerID,
                        Debit=Amount,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        )

                    LedgerPosting_Log.objects.using(DataBase).create(
                        TransactionID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.PaymentMasterID,
                        VoucherDetailID=PaymentDetailsID,
                        VoucherNo=data.VoucherNo,
                        VoucherType=data.VoucherType,
                        LedgerID=data.LedgerID,
                        Debit=Amount,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        )

                    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

                    LedgerPosting.objects.using(DataBase).create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.PaymentMasterID,
                        VoucherDetailID=PaymentDetailsID,
                        VoucherType=data.VoucherType,
                        VoucherNo=data.VoucherNo,
                        LedgerID=data.LedgerID,
                        Credit=NetAmount,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        )

                    LedgerPosting_Log.objects.using(DataBase).create(
                        TransactionID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.PaymentMasterID,
                        VoucherDetailID=PaymentDetailsID,
                        VoucherNo=data.VoucherNo,
                        VoucherType=data.VoucherType,
                        LedgerID=data.LedgerID,
                        Credit=NetAmount,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        )

                    if float(Discount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

                        LedgerPosting.objects.using(DataBase).create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=data.BranchID,
                            Date=data.Date,
                            VoucherMasterID=data.PaymentMasterID,
                            VoucherDetailID=PaymentDetailsID,
                            VoucherType=data.VoucherType,
                            VoucherNo=data.VoucherNo,
                            LedgerID=82,
                            Credit=Discount,
                            IsActive=data.IsActive,
                            Action=data.Action,
                            CreatedUserID=data.CreatedUserID,
                            CreatedDate=data.CreatedDate,
                            UpdatedDate=data.UpdatedDate,
                            )

                        LedgerPosting_Log.objects.using(DataBase).create(
                            TransactionID=LedgerPostingID,
                            BranchID=data.BranchID,
                            Date=data.Date,
                            VoucherMasterID=data.PaymentMasterID,
                            VoucherDetailID=PaymentDetailsID,
                            VoucherNo=data.VoucherNo,
                            VoucherType=data.VoucherType,
                            LedgerID=82,
                            Credit=Discount,
                            IsActive=data.IsActive,
                            Action=data.Action,
                            CreatedUserID=data.CreatedUserID,
                            CreatedDate=data.CreatedDate,
                            UpdatedDate=data.UpdatedDate,
                            )


                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("Cash Payment Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('accounts:cash_payments')
                }
            else:
                message = generate_form_errors(form,formset=False)
                response_data = {
                    'status' : 'false',
                    'stable' : 'true',
                    'title' : str(_("Name Already Exist")),
                    "message" : str("Product Name Already Exist in this Branch!!!")
                }

        else:
            print(payment_details_formset.errors)
            # message = generate_form_errors(form,formset=False)
            message = generate_form_errors(payment_details_formset,formset=True)
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("Form validation error")),
                "message" : str(message)
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = PaymentMasterForm()
        payment_details_formset = PaymentDetailsFormset(prefix='payment_details_formset')

        context = {
            "title" : "Create Cash Payment",
            "form" : form,
            "payment_details_formset" : payment_details_formset,
            "is_need_formset" : True
        }
        return render(request,"accounts/transactions/create_cash_payment.html",context)


@login_required
def cash_payments(request):
    DataBase = get_DataBase(request)

    instances = PaymentMaster.objects.using(DataBase).filter(VoucherType='CP',BranchID=1)

    context = {
        'instances' : instances,
        'title' : 'Cash Payment'
    }
    return render(request,"accounts/transactions/cash_payments.html",context)  


@login_required
def cash_payment(request,pk):
    DataBase = get_DataBase(request)

    instance = PaymentMaster.objects.using(DataBase).get(pk=pk)
    payment_details = PaymentDetails.objects.using(DataBase).filter(payment_master=instance)
    context = {
        'instance' : instance,
        'payment_details' : payment_details,
        'title' : 'Cash Payment'
    }
    return render(request,"accounts/transactions/cash_payment.html",context)


@login_required
def edit_cash_payment(request,pk):
    from api.v1.payments.functions import get_auto_id, get_auto_idMaster
    today = datetime.date.today()
    DataBase = get_DataBase(request)


    instance = PaymentMaster.objects.using(DataBase).get(pk=pk)

    PaymentMasterID = instance.PaymentMasterID
    BranchID = instance.BranchID
    VoucherNo = instance.VoucherNo
    PaymentNo = instance.PaymentNo
    FinancialYearID = instance.FinancialYearID
    VoucherType = instance.VoucherType
    EmployeeID = instance.EmployeeID
    CreatedUserID = instance.CreatedUserID
    CreatedDate = instance.CreatedDate
    UpdatedDate = today

    Action = 'M'

    
    if PaymentDetails.objects.using(DataBase).filter(payment_master=instance).exists():
        extra = 0
    else:
        extra = 1
        
    PaymentDetailsFormset = inlineformset_factory(
                                            PaymentMaster, 
                                            PaymentDetails,
                                            can_delete=True,
                                            form=PaymentDetailsForm,
                                            extra=extra,
                                            )

    if request.method == 'POST':
        payment_details_formset = PaymentDetailsFormset(request.POST,request.FILES,prefix='payment_details_formset',instance=instance)
            
        form = PaymentMasterForm(request.POST,instance=instance)
        
        if form.is_valid(): 
            data = form.save(commit=False)
            BranchID = 1
            data.BranchID = BranchID
            data.Action = 'A'
            data.PaymentMasterID = get_auto_idMaster(PaymentMaster,BranchID,DataBase)
            data.FinancialYearID = 1
            data.VoucherType = 'CP'
            data.VoucherNo  = generateVoucherNo(data.VoucherType, data.BranchID, DataBase)
            data.EmployeeID = request.user.id
            data.CreatedUserID = request.user.id
            data.CreatedDate = today
            data.UpdatedDate = today

            VoucherNoLow = data.VoucherNo.lower()
            is_voucherExist = False
            insts = PaymentMaster.objects.using(DataBase).filter(BranchID=BranchID)
            if insts:
                for i in insts:
                    voucher_no = i.VoucherNo
                    voucherNo = voucher_no.lower()
                    if VoucherNoLow == voucherNo:
                        is_voucherExist = True

            if not is_voucherExist:

                
                PaymentMaster_Log.objects.using(DataBase).create(
                    TransactionID=data.PaymentMasterID,
                    BranchID=data.BranchID,
                    Action=data.Action,
                    VoucherNo=data.VoucherNo,
                    VoucherType=data.VoucherType,
                    LedgerID=data.LedgerID,
                    EmployeeID=data.EmployeeID,
                    PaymentNo=data.VoucherNo,
                    FinancialYearID=data.FinancialYearID,
                    Date=data.Date,
                    TotalAmount=data.TotalAmount,
                    Notes=data.Notes,
                    IsActive=data.IsActive,
                    CreatedDate=data.CreatedDate,
                    UpdatedDate=data.UpdatedDate,
                    CreatedUserID=data.CreatedUserID
                    )
                data.save(using=DataBase)

                payment_detail_items = payment_details_formset.save(commit=False)
                for item in payment_detail_items:
                    PaymentGateway = item.cleaned_data['PaymentGateway']
                    RefferenceNo = item.cleaned_data['RefferenceNo']
                    CardNetwork = item.cleaned_data['CardNetwork']
                    PaymentStatus = item.cleaned_data['PaymentStatus']
                    DueDate = item.cleaned_data['DueDate']
                    LedgerID = item.cleaned_data['LedgerID']
                    Amount = item.cleaned_data['Amount']
                    Balance = item.cleaned_data['Balance']
                    Discount = item.cleaned_data['Discount']
                    NetAmount = item.cleaned_data['NetAmount']
                    Narration = item.cleaned_data['Narration']

                    transactionType = TransactionTypes.objects.using(DataBase).get(Name="Cash")
                    transactionTypeID = transactionType.TransactionTypesID
                    PaymentGateway = transactionTypeID
                    PaymentDetailsID = get_auto_id(PaymentDetails,BranchID,DataBase)
                
                    PaymentDetails.objects.using(DataBase).create(
                        PaymentDetailsID=PaymentDetailsID,
                        BranchID=BranchID,
                        Action=data.Action,
                        PaymentMasterID=data.PaymentMasterID,
                        payment_master=data,
                        PaymentGateway=PaymentGateway,
                        RefferenceNo=RefferenceNo,
                        CardNetwork=CardNetwork,
                        PaymentStatus=PaymentStatus,
                        DueDate=DueDate,
                        LedgerID=LedgerID,
                        Amount=Amount,
                        Balance=Balance,
                        Discount=Discount,
                        NetAmount=NetAmount,
                        Narration=Narration,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        CreatedUserID=data.CreatedUserID,
                        )
                    PaymentDetails_Log.objects.using(DataBase).create(
                        TransactionID=PaymentDetailsID,
                        BranchID=data.BranchID,
                        Action=data.Action,
                        PaymentMasterID=data.PaymentMasterID,
                        PaymentGateway=PaymentGateway,
                        RefferenceNo=RefferenceNo,
                        CardNetwork=CardNetwork,
                        PaymentStatus=PaymentStatus,
                        DueDate=DueDate,
                        LedgerID=LedgerID,
                        Amount=Amount,
                        Balance=Balance,
                        Discount=Discount,
                        NetAmount=NetAmount,
                        Narration=Narration,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        CreatedUserID=data.CreatedUserID,
                        )

                    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)


                    LedgerPosting.objects.using(DataBase).update(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.PaymentMasterID,
                        VoucherDetailID=PaymentDetailsID,
                        VoucherType=data.VoucherType,
                        VoucherNo=data.VoucherNo,
                        LedgerID=data.LedgerID,
                        Debit=Amount,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        )

                    LedgerPosting_Log.objects.using(DataBase).create(
                        TransactionID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.PaymentMasterID,
                        VoucherDetailID=PaymentDetailsID,
                        VoucherNo=data.VoucherNo,
                        VoucherType=data.VoucherType,
                        LedgerID=data.LedgerID,
                        Debit=Amount,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        )

                    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

                    LedgerPosting.objects.using(DataBase).update(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.PaymentMasterID,
                        VoucherDetailID=PaymentDetailsID,
                        VoucherType=data.VoucherType,
                        VoucherNo=data.VoucherNo,
                        LedgerID=data.LedgerID,
                        Credit=NetAmount,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        )

                    LedgerPosting_Log.objects.using(DataBase).create(
                        TransactionID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.PaymentMasterID,
                        VoucherDetailID=PaymentDetailsID,
                        VoucherNo=data.VoucherNo,
                        VoucherType=data.VoucherType,
                        LedgerID=data.LedgerID,
                        Credit=NetAmount,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        )

                    if float(Discount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

                        LedgerPosting.objects.using(DataBase).update(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=data.BranchID,
                            Date=data.Date,
                            VoucherMasterID=data.PaymentMasterID,
                            VoucherDetailID=PaymentDetailsID,
                            VoucherType=data.VoucherType,
                            VoucherNo=data.VoucherNo,
                            LedgerID=82,
                            Credit=Discount,
                            IsActive=data.IsActive,
                            Action=data.Action,
                            CreatedUserID=data.CreatedUserID,
                            CreatedDate=data.CreatedDate,
                            UpdatedDate=data.UpdatedDate,
                            )

                        LedgerPosting_Log.objects.using(DataBase).create(
                            TransactionID=LedgerPostingID,
                            BranchID=data.BranchID,
                            Date=data.Date,
                            VoucherMasterID=data.PaymentMasterID,
                            VoucherDetailID=PaymentDetailsID,
                            VoucherNo=data.VoucherNo,
                            VoucherType=data.VoucherType,
                            LedgerID=82,
                            Credit=Discount,
                            IsActive=data.IsActive,
                            Action=data.Action,
                            CreatedUserID=data.CreatedUserID,
                            CreatedDate=data.CreatedDate,
                            UpdatedDate=data.UpdatedDate,
                            )
                for obj in payment_details_formset.deleted_objects:
                    obj.delete()


                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("Cash Payment Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('accounts:cash_payments')
                }
            else:
                message = generate_form_errors(form,formset=False)
                response_data = {
                    'status' : 'false',
                    'stable' : 'true',
                    'title' : str(_("Name Already Exist")),
                    "message" : str("Cash Payment Already Exist in this Branch!!!")
                }
        else:
            message = generate_form_errors(form,formset=True) 
            message = generate_form_errors(pricelist_formset,formset=True)     
                    
            response_data = {
                "status" : "false",
                "stable" : "true",
                "title" : "Form validation error",
                "message" : message
            }  
            
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')

    else: 
        instance = PaymentMaster.objects.using(DataBase).get(pk=pk)
        form = PaymentMasterForm(instance=instance)
        payment_details_formset = PaymentDetailsFormset(prefix='payment_details_formset',instance=instance)

        context = {
            "form" : form,
            "title" : "Edit Cash Payment : " + str(instance.PaymentMasterID),
            "instance" : instance,
            "payment_details_formset" : payment_details_formset,
            "redirect" : True,
            "is_need_formset" : True

        }
    return render(request,"accounts/transactions/create_cash_payment.html",context)


@login_required
def delete_cash_payment(request,pk):
    DataBase = get_DataBase(request)


    today = datetime.date.today()
    # instance = None
    ledgerPostInstances = None
    if PaymentMaster.objects.using(DataBase).filter(pk=pk).exists():
        instance = PaymentMaster.objects.using(DataBase).get(pk=pk)
        PaymentMasterID = instance.PaymentMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        VoucherType = instance.VoucherType
        LedgerID = instance.LedgerID
        EmployeeID = instance.EmployeeID
        PaymentNo = instance.PaymentNo
        FinancialYearID = instance.FinancialYearID
        Date = instance.Date
        TotalAmount = instance.TotalAmount
        Notes = instance.Notes
        IsActive = instance.IsActive
        Action = "D"

        PaymentMaster_Log.objects.using(DataBase).create(
            TransactionID=PaymentMasterID,
            BranchID=BranchID,
            Action=Action,
            VoucherNo=VoucherNo,
            VoucherType=VoucherType,
            LedgerID=LedgerID,
            EmployeeID=EmployeeID,
            PaymentNo=PaymentNo,
            FinancialYearID=FinancialYearID,
            Date=Date,
            TotalAmount=TotalAmount,
            Notes=Notes,
            IsActive=IsActive,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=request.user.id
            )


        detail_instances = PaymentDetails.objects.using(DataBase).filter(PaymentMasterID=PaymentMasterID,BranchID=BranchID)
        for detail_instance in detail_instances:

            PaymentDetailsID = detail_instance.PaymentDetailsID
            BranchID = detail_instance.BranchID
            PaymentMasterID = detail_instance.PaymentMasterID
            payment_master = detail_instance.payment_master
            PaymentGateway = detail_instance.PaymentGateway
            RefferenceNo = detail_instance.RefferenceNo
            CardNetwork = detail_instance.CardNetwork
            PaymentStatus = detail_instance.PaymentStatus
            DueDate = detail_instance.DueDate
            LedgerID = detail_instance.LedgerID
            Amount = detail_instance.Amount
            Balance = detail_instance.Balance
            Discount = detail_instance.Discount
            NetAmount = detail_instance.NetAmount
            Narration = detail_instance.Narration
            CreatedUserID = detail_instance.CreatedUserID

            detail_instance.delete()

            PaymentDetails_Log.objects.using(DataBase).create(
                TransactionID=PaymentDetailsID,
                BranchID=BranchID,
                Action=Action,
                PaymentMasterID=PaymentMasterID,
                PaymentGateway=PaymentGateway,
                RefferenceNo=RefferenceNo,
                CardNetwork=CardNetwork,
                PaymentStatus=PaymentStatus,
                DueDate=DueDate,
                LedgerID=LedgerID,
                Amount=Amount,
                Balance=Balance,
                Discount=Discount,
                NetAmount=NetAmount,
                Narration=Narration,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                )

            

            if LedgerPosting.objects.using(DataBase).filter(VoucherMasterID=PaymentMasterID,BranchID=BranchID,VoucherType="CP").exists():
                ledgerPostInstances = LedgerPosting.objects.using(DataBase).filter(VoucherMasterID=PaymentMasterID,BranchID=BranchID,VoucherType="CP")
                
                for ledgerPostInstance in ledgerPostInstances:

                    LedgerPostingID = ledgerPostInstance.LedgerPostingID
                    VoucherType = ledgerPostInstance.VoucherType
                    Debit = ledgerPostInstance.Debit
                    Credit = ledgerPostInstance.Credit
                    IsActive = ledgerPostInstance.IsActive
                    Date = ledgerPostInstance.Date
                    LedgerID = ledgerPostInstance.LedgerID
                    CreatedUserID = ledgerPostInstance.CreatedUserID

                    LedgerPosting_Log.objects.using(DataBase).create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PaymentMasterID,
                        VoucherDetailID=PaymentDetailsID,
                        VoucherNo=VoucherNo,
                        VoucherType=VoucherType,
                        LedgerID=LedgerID,
                        Debit=Debit,
                        Credit=Credit,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        )

                    ledgerPostInstance.delete()
        instance.delete()

        response_data = {
            "status" : "true",
            "title" : str(_("Successfully Deleted")),
            "message" : str(_("Cash Payment Deleted Successfully.")),
            "redirect" : "true",
            "redirect_url" : reverse('accounts:cash_payments')
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')


@login_required
def create_cash_receipt(request):
    from api.v1.receipts.functions import get_auto_id, get_auto_idMaster
    DataBase = get_DataBase(request)

    ReceiptDetailsFormset = formset_factory(ReceiptDetailsForm)
    today = datetime.date.today()
    if request.method == 'POST':
        form = ReceiptMasterForm(request.POST,request.FILES)
        receipt_details_formset = ReceiptDetailsFormset(request.POST,prefix='receipt_details_formset')
        if form.is_valid() and receipt_details_formset.is_valid(): 
            data = form.save(commit=False)
            BranchID = 1
            data.BranchID = BranchID
            data.Action = 'A'
            data.ReceiptMasterID = get_auto_idMaster(ReceiptMaster,BranchID,DataBase)
            data.FinancialYearID = 1
            data.VoucherType = "CR"
            data.VoucherNo  = generateVoucherNo(data.VoucherType, data.BranchID, DataBase)
            data.ReceiptNo = str(data.VoucherType) + str(data.VoucherNo)
            data.EmployeeID = request.user.id
            data.CreatedUserID = request.user.id
            data.CreatedDate = today
            data.UpdatedDate = today


            VoucherNoLow = data.VoucherNo.lower()
            is_voucherExist = False
            insts = ReceiptMaster.objects.using(DataBase).filter(BranchID=BranchID)
            if insts:
                for i in insts:
                    voucher_no = i.VoucherNo
                    voucherNo = voucher_no.lower()
                    if VoucherNoLow == voucherNo:
                        is_voucherExist = True

            if not is_voucherExist:

                
                ReceiptMaster_Log.objects.using(DataBase).create(
                    TransactionID=data.ReceiptMasterID,
                    BranchID=data.BranchID,
                    Action=data.Action,
                    VoucherNo=data.VoucherNo,
                    VoucherType=data.VoucherType,
                    ReceiptNo=data.ReceiptNo,
                    LedgerID=data.LedgerID,
                    EmployeeID=data.EmployeeID,
                    FinancialYearID=data.FinancialYearID,
                    Date=data.Date,
                    TotalAmount=data.TotalAmount,
                    Notes=data.Notes,
                    IsActive=data.IsActive,
                    CreatedDate=data.CreatedDate,
                    UpdatedDate=data.UpdatedDate,
                    CreatedUserID=data.CreatedUserID
                    )
                data.save(using=DataBase)

                for f in receipt_details_formset:
                    PaymentGateway = f.cleaned_data['PaymentGateway']
                    RefferenceNo = f.cleaned_data['RefferenceNo']
                    CardNetwork = f.cleaned_data['CardNetwork']
                    PaymentStatus = f.cleaned_data['PaymentStatus']
                    DueDate = f.cleaned_data['DueDate']
                    LedgerID = f.cleaned_data['LedgerID']
                    Amount = f.cleaned_data['Amount']
                    Balance = f.cleaned_data['Balance']
                    Discount = f.cleaned_data['Discount']
                    NetAmount = f.cleaned_data['NetAmount']
                    Narration = f.cleaned_data['Narration']

                    transactionType = TransactionTypes.objects.using(DataBase).get(Name="Cash")
                    transactionTypeID = transactionType.TransactionTypesID
                    PaymentGateway = transactionTypeID
                    ReceiptDetailID = get_auto_id(ReceiptDetails,BranchID,DataBase)
                
                    ReceiptDetails.objects.using(DataBase).create(
                        ReceiptDetailID=ReceiptDetailID,
                        BranchID=BranchID,
                        Action=data.Action,
                        ReceiptMasterID=data.ReceiptMasterID,
                        VoucherType=data.VoucherType,
                        receipt_master=data,
                        PaymentGateway=PaymentGateway,
                        RefferenceNo=RefferenceNo,
                        CardNetwork=CardNetwork,
                        PaymentStatus=PaymentStatus,
                        DueDate=DueDate,
                        LedgerID=LedgerID,
                        Amount=Amount,
                        Balance=Balance,
                        Discount=Discount,
                        NetAmount=NetAmount,
                        Narration=Narration,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        CreatedUserID=data.CreatedUserID,
                        )

                    ReceiptDetails_Log.objects.using(DataBase).create(
                        TransactionID=ReceiptDetailID,
                        BranchID=data.BranchID,
                        Action=data.Action,
                        ReceiptMasterID=data.ReceiptMasterID,
                        VoucherType=data.VoucherType,
                        PaymentGateway=PaymentGateway,
                        RefferenceNo=RefferenceNo,
                        CardNetwork=CardNetwork,
                        PaymentStatus=PaymentStatus,
                        DueDate=DueDate,
                        LedgerID=LedgerID,
                        Amount=Amount,
                        Balance=Balance,
                        Discount=Discount,
                        NetAmount=NetAmount,
                        Narration=Narration,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        CreatedUserID=data.CreatedUserID,
                        )

                    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)


                    LedgerPosting.objects.using(DataBase).create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.ReceiptMasterID,
                        VoucherDetailID=ReceiptDetailID,
                        VoucherType=data.VoucherType,
                        VoucherNo=data.VoucherNo,
                        LedgerID=data.LedgerID,
                        Credit=Amount,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        )


                    LedgerPosting_Log.objects.using(DataBase).create(
                        TransactionID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.ReceiptMasterID,
                        VoucherDetailID=ReceiptDetailID,
                        VoucherNo=data.VoucherNo,
                        VoucherType=data.VoucherType,
                        LedgerID=data.LedgerID,
                        Credit=Amount,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        )

                    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

                    LedgerPosting.objects.using(DataBase).create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.ReceiptMasterID,
                        VoucherDetailID=ReceiptDetailID,
                        VoucherType=data.VoucherType,
                        VoucherNo=data.VoucherNo,
                        LedgerID=data.LedgerID,
                        Debit=NetAmount,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        )

                    LedgerPosting_Log.objects.using(DataBase).create(
                        TransactionID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.ReceiptMasterID,
                        VoucherDetailID=ReceiptDetailID,
                        VoucherNo=data.VoucherNo,
                        VoucherType=data.VoucherType,
                        LedgerID=data.LedgerID,
                        Debit=NetAmount,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        )

                    if float(Discount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

                        LedgerPosting.objects.using(DataBase).create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=data.BranchID,
                            Date=data.Date,
                            VoucherMasterID=data.ReceiptMasterID,
                            VoucherDetailID=ReceiptDetailID,
                            VoucherType=data.VoucherType,
                            VoucherNo=data.VoucherNo,
                            LedgerID=82,
                            Debit=Discount,
                            IsActive=data.IsActive,
                            Action=data.Action,
                            CreatedUserID=data.CreatedUserID,
                            CreatedDate=data.CreatedDate,
                            UpdatedDate=data.UpdatedDate,
                            )

                        LedgerPosting_Log.objects.using(DataBase).create(
                            TransactionID=LedgerPostingID,
                            BranchID=data.BranchID,
                            Date=data.Date,
                            VoucherMasterID=data.ReceiptMasterID,
                            VoucherDetailID=ReceiptDetailID,
                            VoucherNo=data.VoucherNo,
                            VoucherType=data.VoucherType,
                            LedgerID=82,
                            Debit=Discount,
                            IsActive=data.IsActive,
                            Action=data.Action,
                            CreatedUserID=data.CreatedUserID,
                            CreatedDate=data.CreatedDate,
                            UpdatedDate=data.UpdatedDate,
                            )


                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("Cash Receipt Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('accounts:cash_receipts')
                }
            else:
                message = generate_form_errors(form,formset=False)
                response_data = {
                    'status' : 'false',
                    'stable' : 'true',
                    'title' : str(_("Name Already Exist")),
                    "message" : str("Voucher Number Already Exist in this Branch!!!")
                }

        else:
            print(receipt_details_formset.errors)
            # message = generate_form_errors(form,formset=False)
            message = generate_form_errors(receipt_details_formset,formset=True)
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("Form validation error")),
                "message" : str(message)
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = ReceiptMasterForm()
        receipt_details_formset = ReceiptDetailsFormset(prefix='receipt_details_formset')

        context = {
            "title" : "Create Cash Receipt",
            "form" : form,
            "receipt_details_formset" : receipt_details_formset,
            "is_need_formset" : True
        }
        return render(request,"accounts/transactions/create_cash_receipt.html",context)


@login_required
def cash_receipts(request):
    DataBase = get_DataBase(request)

    BranchID = 1
    VoucherType = 'CR'
    instances = ReceiptMaster.objects.using(DataBase).filter(BranchID=BranchID, VoucherType=VoucherType)

    context = {
        'instances' : instances,
        'title' : 'Cash Receipt'
    }
    return render(request,"accounts/transactions/cash_receipts.html",context)  


@login_required
def cash_receipt(request, pk):
    DataBase = get_DataBase(request)

    instance = ReceiptMaster.objects.using(DataBase).get(pk=pk)
    receipt_details = ReceiptDetails.objects.using(DataBase).filter(receipt_master=instance)
    context = {
        'instance' : instance,
        'receipt_details' : receipt_details,
        'title' : 'Receipt'
    }
    return render(request,"accounts/transactions/cash_receipt.html",context)


@login_required
def edit_cash_receipt(request,pk):
    from api.v1.receipts.functions import get_auto_id, get_auto_idMaster
    today = datetime.date.today()
    DataBase = get_DataBase(request)


    instance = ReceiptMaster.objects.using(DataBase).get(pk=pk)

    ReceiptMasterID = instance.ReceiptMasterID
    BranchID = instance.BranchID
    VoucherNo = instance.VoucherNo
    ReceiptNo = instance.ReceiptNo
    FinancialYearID = instance.FinancialYearID
    VoucherType = instance.VoucherType
    EmployeeID = instance.EmployeeID
    CreatedUserID = instance.CreatedUserID
    CreatedDate = instance.CreatedDate
    UpdatedDate = today

    Action = 'M'

    
    if ReceiptDetails.objects.using(DataBase).filter(receipt_master=instance).exists():
        extra = 0
    else:
        extra = 1
        
    ReceiptDetailsFormset = inlineformset_factory(
                                            ReceiptMaster, 
                                            ReceiptDetails,
                                            can_delete=True,
                                            form=ReceiptDetailsForm,
                                            extra=extra,
                                            )

    if request.method == 'POST':
        receipt_details_formset = ReceiptDetailsFormset(request.POST,request.FILES,prefix='receipt_details_formset',instance=instance)
            
        form = ReceiptMasterForm(request.POST,instance=instance)
        
        if form.is_valid(): 
            data = form.save(commit=False)
            BranchID = 1
            data.BranchID = BranchID
            data.Action = 'A'
            data.ReceiptMasterID = instance.ReceiptMasterID
            data.FinancialYearID = 1
            data.VoucherType = VoucherType
            data.VoucherNo  = instance.VoucherNo
            data.EmployeeID = request.user.id
            data.CreatedUserID = request.user.id
            data.CreatedDate = today
            data.UpdatedDate = today

                
            ReceiptMaster_Log.objects.using(DataBase).create(
                TransactionID=data.ReceiptMasterID,
                BranchID=data.BranchID,
                Action=data.Action,
                VoucherNo=data.VoucherNo,
                VoucherType=data.VoucherType,
                LedgerID=data.LedgerID,
                EmployeeID=data.EmployeeID,
                ReceiptNo=data.ReceiptNo,
                FinancialYearID=data.FinancialYearID,
                Date=data.Date,
                TotalAmount=data.TotalAmount,
                Notes=data.Notes,
                IsActive=data.IsActive,
                CreatedDate=data.CreatedDate,
                UpdatedDate=data.UpdatedDate,
                CreatedUserID=data.CreatedUserID
                )

            receipt_detail_items = receipt_details_formset.save(commit=False)
            for item in receipt_detail_items:
                PaymentGateway = item.cleaned_data['PaymentGateway']
                RefferenceNo = item.cleaned_data['RefferenceNo']
                CardNetwork = item.cleaned_data['CardNetwork']
                PaymentStatus = item.cleaned_data['PaymentStatus']
                DueDate = item.cleaned_data['DueDate']
                LedgerID = item.cleaned_data['LedgerID']
                Amount = item.cleaned_data['Amount']
                Balance = item.cleaned_data['Balance']
                Discount = item.cleaned_data['Discount']
                NetAmount = item.cleaned_data['NetAmount']
                Narration = item.cleaned_data['Narration']

                transactionType = TransactionTypes.objects.using(DataBase).get(Name="Cash")
                transactionTypeID = transactionType.TransactionTypesID
                PaymentGateway = transactionTypeID
                ReceiptDetailsID = get_auto_id(ReceiptDetails,BranchID,DataBase)
            
                ReceiptDetails.objects.using(DataBase).create(
                    ReceiptDetailsID=ReceiptDetailsID,
                    BranchID=BranchID,
                    Action=data.Action,
                    ReceiptMasterID=data.ReceiptMasterID,
                    receipt_master=data,
                    PaymentGateway=PaymentGateway,
                    RefferenceNo=RefferenceNo,
                    CardNetwork=CardNetwork,
                    PaymentStatus=PaymentStatus,
                    DueDate=DueDate,
                    LedgerID=LedgerID,
                    Amount=Amount,
                    Balance=Balance,
                    Discount=Discount,
                    NetAmount=NetAmount,
                    Narration=Narration,
                    CreatedDate=data.CreatedDate,
                    UpdatedDate=data.UpdatedDate,
                    CreatedUserID=data.CreatedUserID,
                    )
                ReceiptDetails_Log.objects.using(DataBase).create(
                    TransactionID=ReceiptDetailsID,
                    BranchID=data.BranchID,
                    Action=data.Action,
                    ReceiptMasterID=data.ReceiptMasterID,
                    PaymentGateway=PaymentGateway,
                    RefferenceNo=RefferenceNo,
                    CardNetwork=CardNetwork,
                    PaymentStatus=PaymentStatus,
                    DueDate=DueDate,
                    LedgerID=LedgerID,
                    Amount=Amount,
                    Balance=Balance,
                    Discount=Discount,
                    NetAmount=NetAmount,
                    Narration=Narration,
                    CreatedDate=data.CreatedDate,
                    UpdatedDate=data.UpdatedDate,
                    CreatedUserID=data.CreatedUserID,
                    )

                LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)


                LedgerPosting.objects.using(DataBase).update(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=data.BranchID,
                    Date=data.Date,
                    VoucherMasterID=data.ReceiptMasterID,
                    VoucherDetailID=ReceiptDetailsID,
                    VoucherType=data.VoucherType,
                    VoucherNo=data.VoucherNo,
                    LedgerID=data.LedgerID,
                    Credit=Amount,
                    IsActive=data.IsActive,
                    Action=data.Action,
                    CreatedUserID=data.CreatedUserID,
                    CreatedDate=data.CreatedDate,
                    UpdatedDate=data.UpdatedDate,
                    )

                LedgerPosting_Log.objects.using(DataBase).create(
                    TransactionID=LedgerPostingID,
                    BranchID=data.BranchID,
                    Date=data.Date,
                    VoucherMasterID=data.ReceiptMasterID,
                    VoucherDetailID=ReceiptDetailsID,
                    VoucherNo=data.VoucherNo,
                    VoucherType=data.VoucherType,
                    LedgerID=data.LedgerID,
                    Credit=Amount,
                    IsActive=data.IsActive,
                    Action=data.Action,
                    CreatedUserID=data.CreatedUserID,
                    CreatedDate=data.CreatedDate,
                    UpdatedDate=data.UpdatedDate,
                    )

                LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

                LedgerPosting.objects.using(DataBase).update(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=data.BranchID,
                    Date=data.Date,
                    VoucherMasterID=data.ReceiptMasterID,
                    VoucherDetailID=ReceiptDetailsID,
                    VoucherType=data.VoucherType,
                    VoucherNo=data.VoucherNo,
                    LedgerID=data.LedgerID,
                    Debit=NetAmount,
                    IsActive=data.IsActive,
                    Action=data.Action,
                    CreatedUserID=data.CreatedUserID,
                    CreatedDate=data.CreatedDate,
                    UpdatedDate=data.UpdatedDate,
                    )

                LedgerPosting_Log.objects.using(DataBase).create(
                    TransactionID=LedgerPostingID,
                    BranchID=data.BranchID,
                    Date=data.Date,
                    VoucherMasterID=data.ReceiptMasterID,
                    VoucherDetailID=ReceiptDetailsID,
                    VoucherNo=data.VoucherNo,
                    VoucherType=data.VoucherType,
                    LedgerID=data.LedgerID,
                    Debit=NetAmount,
                    IsActive=data.IsActive,
                    Action=data.Action,
                    CreatedUserID=data.CreatedUserID,
                    CreatedDate=data.CreatedDate,
                    UpdatedDate=data.UpdatedDate,
                    )

                if float(Discount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

                    LedgerPosting.objects.using(DataBase).update(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.ReceiptMasterID,
                        VoucherDetailID=ReceiptDetailsID,
                        VoucherType=data.VoucherType,
                        VoucherNo=data.VoucherNo,
                        LedgerID=82,
                        Debit=Discount,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        )

                    LedgerPosting_Log.objects.using(DataBase).create(
                        TransactionID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.ReceiptMasterID,
                        VoucherDetailID=ReceiptDetailsID,
                        VoucherNo=data.VoucherNo,
                        VoucherType=data.VoucherType,
                        LedgerID=82,
                        Debit=Discount,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        )

            data.save(using=DataBase)
            for obj in receipt_details_formset.deleted_objects:
                obj.delete()


            response_data = {
                "status" : "true",
                "title" : str(_("Successfully Created")),
                "message" : str(_("Cash Receipt Created Successfully!")),
                "redirect" : "true",
                "redirect_url" : reverse('accounts:cash_receipts')
            }

        else:
            message = generate_form_errors(form,formset=False) 
            message = generate_form_errors(receipt_details_formset,formset=True)     
                    
            response_data = {
                "status" : "false",
                "stable" : "true",
                "title" : "Form validation error",
                "message" : message
            }  
            
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')

    else: 
        instance = ReceiptMaster.objects.using(DataBase).get(pk=pk)
        form = ReceiptMasterForm(instance=instance)
        receipt_details_formset = ReceiptDetailsFormset(prefix='receipt_details_formset',instance=instance)

        context = {
            "form" : form,
            "title" : "Edit Cash Receipt : " + str(instance.ReceiptMasterID),
            "instance" : instance,
            "receipt_details_formset" : receipt_details_formset,
            "redirect" : True,
            "is_need_formset" : True

        }
    return render(request,"accounts/transactions/create_cash_receipt.html",context)


@login_required
def delete_cash_receipt(request,pk):
    DataBase = get_DataBase(request)


    today = datetime.date.today()
    # instance = None
    ledgerPostInstances = None
    if ReceiptMaster.objects.using(DataBase).filter(pk=pk).exists():
        instance = ReceiptMaster.objects.using(DataBase).get(pk=pk)
        ReceiptMasterID = instance.ReceiptMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        VoucherType = instance.VoucherType
        LedgerID = instance.LedgerID
        EmployeeID = instance.EmployeeID
        ReceiptNo = instance.ReceiptNo
        FinancialYearID = instance.FinancialYearID
        Date = instance.Date
        TotalAmount = instance.TotalAmount
        Notes = instance.Notes
        IsActive = instance.IsActive
        Action = "D"

        ReceiptMaster_Log.objects.using(DataBase).create(
            TransactionID=ReceiptMasterID,
            BranchID=BranchID,
            Action=Action,
            VoucherNo=VoucherNo,
            VoucherType=VoucherType,
            ReceiptNo=ReceiptNo,
            LedgerID=LedgerID,
            EmployeeID=EmployeeID,
            FinancialYearID=FinancialYearID,
            Date=Date,
            TotalAmount=TotalAmount,
            Notes=Notes,
            IsActive=IsActive,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=request.user.id
            )


        detail_instances = ReceiptDetails.objects.using(DataBase).filter(ReceiptMasterID=ReceiptMasterID,BranchID=BranchID)
        for detail_instance in detail_instances:

            ReceiptDetailID = detail_instance.ReceiptDetailID
            BranchID = detail_instance.BranchID
            ReceiptMasterID = detail_instance.ReceiptMasterID
            receipt_master = detail_instance.receipt_master
            PaymentGateway = detail_instance.PaymentGateway
            RefferenceNo = detail_instance.RefferenceNo
            CardNetwork = detail_instance.CardNetwork
            PaymentStatus = detail_instance.PaymentStatus
            DueDate = detail_instance.DueDate
            LedgerID = detail_instance.LedgerID
            Amount = detail_instance.Amount
            Balance = detail_instance.Balance
            Discount = detail_instance.Discount
            NetAmount = detail_instance.NetAmount
            Narration = detail_instance.Narration
            CreatedUserID = detail_instance.CreatedUserID

            detail_instance.delete()

            ReceiptDetails_Log.objects.using(DataBase).create(
                TransactionID=ReceiptDetailID,
                BranchID=BranchID,
                Action=Action,
                ReceiptMasterID=ReceiptMasterID,
                PaymentGateway=PaymentGateway,
                RefferenceNo=RefferenceNo,
                CardNetwork=CardNetwork,
                PaymentStatus=PaymentStatus,
                DueDate=DueDate,
                LedgerID=LedgerID,
                Amount=Amount,
                Balance=Balance,
                Discount=Discount,
                NetAmount=NetAmount,
                Narration=Narration,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                )

            

            if LedgerPosting.objects.using(DataBase).filter(VoucherMasterID=ReceiptMasterID,BranchID=BranchID,VoucherType="CP").exists():
                ledgerPostInstances = LedgerPosting.objects.using(DataBase).filter(VoucherMasterID=ReceiptMasterID,BranchID=BranchID,VoucherType="CP")
                
                for ledgerPostInstance in ledgerPostInstances:

                    LedgerPostingID = ledgerPostInstance.LedgerPostingID
                    VoucherType = ledgerPostInstance.VoucherType
                    Debit = ledgerPostInstance.Debit
                    Credit = ledgerPostInstance.Credit
                    IsActive = ledgerPostInstance.IsActive
                    Date = ledgerPostInstance.Date
                    LedgerID = ledgerPostInstance.LedgerID
                    CreatedUserID = ledgerPostInstance.CreatedUserID

                    LedgerPosting_Log.objects.using(DataBase).create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ReceiptMasterID,
                        VoucherDetailID=PaymentDetailsID,
                        VoucherNo=VoucherNo,
                        VoucherType=VoucherType,
                        LedgerID=LedgerID,
                        Debit=Debit,
                        Credit=Credit,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        )

                    ledgerPostInstance.delete()
        instance.delete()

    response_data = {
        "status" : "true",
        "title" : str(_("Successfully Deleted")),
        "message" : str(_("Cash Receipt Deleted Successfully.")),
        "redirect" : "true",
        "redirect_url" : reverse('accounts:cash_receipts')
    }
    return HttpResponse(json.dumps(response_data), content_type='application/javascript')


@login_required
def create_journal_entry(request):
    from api.v1.journals.functions import get_auto_id, get_auto_idMaster
    DataBase = get_DataBase(request)

    JournalDetailsFormset = formset_factory(JournalDetailsForm)
    today = datetime.date.today()
    if request.method == 'POST':
        form = JournalMasterForm(request.POST,request.FILES)
        journal_details_formset = JournalDetailsFormset(request.POST,prefix='journal_details_formset')
        if form.is_valid() and journal_details_formset.is_valid(): 
            data = form.save(commit=False)
            BranchID = 1
            data.BranchID = BranchID
            data.Action = 'A'
            data.JournalMasterID = get_auto_idMaster(JournalMaster,BranchID,DataBase)
            data.FinancialYearID = 1
            data.VoucherType = "JL"
            data.VoucherNo  = generateVoucherNo(data.VoucherType, data.BranchID, DataBase)
            data.EmployeeID = request.user.id
            data.CreatedUserID = request.user.id
            data.CreatedDate = today
            data.UpdatedDate = today


            VoucherNoLow = data.VoucherNo.lower()
            is_voucherExist = False
            insts = JournalMaster.objects.using(DataBase).filter(BranchID=BranchID)
            if insts:
                for i in insts:
                    voucher_no = i.VoucherNo
                    voucherNo = voucher_no.lower()
                    if VoucherNoLow == voucherNo:
                        is_voucherExist = True

            if not is_voucherExist:


                JournalMaster_Log.objects.using(DataBase).create(
                    TransactionID=data.JournalMasterID,
                    BranchID=data.BranchID,
                    VoucherNo=data.VoucherNo,
                    Date=data.Date,
                    Notes=data.Notes,
                    TotalDebit=data.TotalDebit,
                    TotalCredit=data.TotalCredit,
                    Difference=data.Difference,
                    IsActive=data.IsActive,
                    Action=data.Action,
                    CreatedUserID=data.CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    )

                data.save(using=DataBase)
                for f in journal_details_formset:
                    LedgerID = f.cleaned_data['LedgerID']
                    Debit = f.cleaned_data['Debit']
                    Credit = f.cleaned_data['Credit']
                    Narration = f.cleaned_data['Narration']

                    JournalDetailsID = get_auto_id(JournalDetails,BranchID, DataBase)
                
                    JournalDetails.objects.using(DataBase).create(
                        JournalDetailsID=JournalDetailsID,
                        BranchID=data.BranchID,
                        JournalMasterID=data.JournalMasterID,
                        journal_master = data,
                        LedgerID=LedgerID,
                        Debit=Debit,
                        Credit=Credit,
                        Narration=Narration,
                        Action=data.Action,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=data.CreatedUserID,
                        )

                    JournalDetails_Log.objects.using(DataBase).create(
                        TransactionID=JournalDetailsID,
                        BranchID=data.BranchID,
                        JournalMasterID=data.JournalMasterID,
                        LedgerID=LedgerID,
                        Debit=Debit,
                        Credit=Credit,
                        Narration=Narration,
                        Action=data.Action,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=data.CreatedUserID,
                        )

                    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID, DataBase)


                    LedgerPosting.objects.using(DataBase).create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.JournalMasterID,
                        VoucherType=data.VoucherType,
                        VoucherNo=data.VoucherNo,
                        LedgerID=LedgerID,
                        Debit=Debit,
                        Credit=Credit,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        )

                    LedgerPosting_Log.objects.using(DataBase).create(
                        TransactionID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.JournalMasterID,
                        VoucherType=data.VoucherType,
                        VoucherNo=data.VoucherNo,
                        LedgerID=LedgerID,
                        Debit=Debit,
                        Credit=Credit,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        )


                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("Journal Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('accounts:journal_entries')
                }
                return HttpResponse(json.dumps(response_data), content_type='application/javascript')
            else:
                message = generate_form_errors(form,formset=False)
                response_data = {
                    'status' : 'false',
                    'stable' : 'true',
                    'title' : str(_("Name Already Exist")),
                    "message" : str("Voucher Number Already Exist in this Branch!!!")
                }

        else:
            print(journal_details_formset.errors)
            # message = generate_form_errors(form,formset=False)
            message = generate_form_errors(journal_details_formset,formset=True)
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("Form validation error")),
                "message" : str(message)
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = JournalMasterForm()
        journal_details_formset = JournalDetailsFormset(prefix='journal_details_formset')

        context = {
            "title" : "Create Journal",
            "form" : form,
            "journal_details_formset" : journal_details_formset,
            "is_need_formset" : True
        }
        return render(request,"accounts/transactions/create_journal_entry.html",context)


@login_required
def journal_entries(request):
    DataBase = get_DataBase(request)

    BranchID = 1
    instances = JournalMaster.objects.using(DataBase).filter(BranchID=BranchID)

    context = {
        'instances' : instances,
        'title' : 'Journal Entry'
    }
    return render(request,"accounts/transactions/journal_entries.html",context)  


@login_required
def journal_entry(request, pk):
    DataBase = get_DataBase(request)

    instance = JournalMaster.objects.using(DataBase).get(pk=pk)
    journal_details = JournalDetails.objects.using(DataBase).filter(journal_master=instance)
    context = {
        'instance' : instance,
        'journal_details' : journal_details,
        'title' : 'Journal Entry'
    }
    return render(request,"accounts/transactions/journal_entry.html",context)


@login_required
def edit_journal_entry(request,pk):
    from api.v1.receipts.functions import get_auto_id, get_auto_idMaster
    today = datetime.date.today()
    DataBase = get_DataBase(request)


    instance = JournalMaster.objects.using(DataBase).get(pk=pk)

    JournalMasterID = instance.JournalMasterID
    BranchID = instance.BranchID
    VoucherNo = instance.VoucherNo
    Action = 'M'
    CreatedDate = today
    UpdatedDate = today
    CreatedUserID = request.user.id
    
    if JournalDetails.objects.using(DataBase).filter(journal_master=instance).exists():
        extra = 0
    else:
        extra = 1
        
    JournalDetailsFormset = inlineformset_factory(
                                            JournalMaster, 
                                            JournalDetails,
                                            can_delete=True,
                                            form=JournalDetailsForm,
                                            extra=extra,
                                            )

    if request.method == 'POST':
        journal_details_formset = JournalDetailsFormset(request.POST,request.FILES,prefix='journal_details_formset',instance=instance)
            
        form = JournalMasterForm(request.POST,instance=instance)
        
        if form.is_valid(): 
            data = form.save(commit=False)
            data.JournalMasterID = JournalMasterID
            data.BranchID = BranchID
            data.VoucherNo = VoucherNo
            data.Action = Action
            data.CreatedDate = CreatedDate
            data.UpdatedDate = UpdatedDate
            data.CreatedUserID = CreatedUserID

                
            JournalMaster_Log.objects.using(DataBase).create(
                TransactionID = data.JournalMasterID,
                BranchID = data.BranchID,
                VoucherNo = data.VoucherNo,
                Date = data.Date,
                Notes = data.Notes,
                TotalDebit = data.TotalDebit,
                TotalCredit = data.TotalCredit,
                Difference = data.Difference,
                IsActive = data.IsActive,
                Action = data.Action,
                CreatedDate = data.CreatedDate,
                UpdatedDate = data.UpdatedDate,
                CreatedUserID = data.CreatedUserID,
                )

            journal_detail_items = journal_details_formset.save(commit=False)
            for item in journal_detail_items:


                LedgerID = item.cleaned_data['LedgerID']
                Debit = item.cleaned_data['Debit']
                Credit = item.cleaned_data['Credit']
                Narration = item.cleaned_data['Narration']

                JournalDetailsID = get_auto_id(JournalDetails,BranchID, DataBase)
            
                JournalDetails.objects.using(DataBase).create(
                    JournalDetailsID = JournalDetailsID,
                    BranchID = data.BranchID,
                    JournalMasterID = data.JournalMasterID,
                    journal_master = data,
                    LedgerID = LedgerID,
                    Debit = Debit,
                    Credit = Credit,
                    Narration = Narration,
                    Action = data.Action,
                    CreatedDate = today,
                    UpdatedDate = today,
                    CreatedUserID = request.user.id,
                    )
                JournalDetails_Log.objects.using(DataBase).create(
                    TransactionID = JournalDetailsID,
                    BranchID = data.BranchID,
                    JournalMasterID = data.JournalMasterID,
                    LedgerID = LedgerID,
                    Debit = Debit,
                    Credit = Credit,
                    Narration = Narration,
                    Action = data.Action,
                    CreatedDate = today,
                    UpdatedDate = today,
                    CreatedUserID = request.user.id,
                    )

                LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID, DataBase)


                LedgerPosting.objects.using(DataBase).create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=data.BranchID,
                    Date=data.Date,
                    VoucherMasterID=data.JournalMasterID,
                    VoucherType=data.VoucherType,
                    VoucherNo=data.VoucherNo,
                    LedgerID=LedgerID,
                    Debit=Debit,
                    Credit=Credit,
                    IsActive=data.IsActive,
                    Action=data.Action,
                    CreatedUserID=data.CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    )

                LedgerPosting_Log.objects.using(DataBase).create(
                    TransactionID=LedgerPostingID,
                    BranchID=data.BranchID,
                    Date=data.Date,
                    VoucherMasterID=data.JournalMasterID,
                    VoucherType=data.VoucherType,
                    VoucherNo=data.VoucherNo,
                    LedgerID=LedgerID,
                    Debit=Debit,
                    Credit=Credit,
                    IsActive=data.IsActive,
                    Action=data.Action,
                    CreatedUserID=data.CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    )

            data.save(using=DataBase)
            for obj in journal_details_formset.deleted_objects:
                obj.delete()


            response_data = {
                "status" : "true",
                "title" : str(_("Successfully Created")),
                "message" : str(_("Cash Receipt Created Successfully!")),
                "redirect" : "true",
                "redirect_url" : reverse('accounts:journal_entries')
            }

        else:
            message = generate_form_errors(form,formset=False) 
            message = generate_form_errors(journal_details_formset,formset=True)     
                    
            response_data = {
                "status" : "false",
                "stable" : "true",
                "title" : "Form validation error",
                "message" : message
            }  
            
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')

    else: 
        instance = JournalMaster.objects.using(DataBase).get(pk=pk)
        form = JournalMasterForm(instance=instance)
        journal_details_formset = JournalDetailsFormset(prefix='journal_details_formset',instance=instance)

        context = {
            "form" : form,
            "title" : "Edit Cash Journal : " + str(instance.JournalMasterID),
            "instance" : instance,
            "journal_details_formset" : journal_details_formset,
            "redirect" : True,
            "is_need_formset" : True

        }
    return render(request,"accounts/transactions/create_journal_entry.html",context)


@login_required
def delete_journal_entry(request,pk):
    DataBase = get_DataBase(request)


    today = datetime.date.today()
    # instance = None
    if JournalMaster.objects.using(DataBase).filter(pk=pk).exists():
        instance = JournalMaster.objects.using(DataBase).get(pk=pk)
        JournalMasterID = instance.JournalMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        Date = instance.Date
        Notes = instance.Notes
        TotalDebit = instance.TotalDebit
        TotalCredit = instance.TotalCredit
        Difference = instance.Difference
        IsActive = instance.IsActive
        Action = 'D'
        CreatedDate = today
        UpdatedDate = today
        CreatedUserID = request.user.id

        JournalMaster_Log.objects.using(DataBase).create(
            TransactionID = JournalMasterID,
            BranchID = BranchID,
            VoucherNo = VoucherNo,
            Date = Date,
            Notes = Notes,
            TotalDebit = TotalDebit,
            TotalCredit = TotalCredit,
            Difference = Difference,
            IsActive = IsActive,
            Action = Action,
            CreatedDate = CreatedDate,
            UpdatedDate = UpdatedDate,
            CreatedUserID = CreatedUserID,
            )


        detail_instances = JournalDetails.objects.using(DataBase).filter(journal_master=instance,BranchID=BranchID)
        for detail_instance in detail_instances:

            JournalDetailsID = detail_instance.JournalDetailsID
            BranchID = detail_instance.BranchID
            JournalMasterID = detail_instance.JournalMasterID
            LedgerID = detail_instance.LedgerID
            Debit = detail_instance.Debit
            Credit = detail_instance.Credit
            Narration = detail_instance.Narration
            CreatedUserID = detail_instance.CreatedUserID


            JournalDetails_Log.objects.using(DataBase).create(
                TransactionID = JournalDetailsID,
                BranchID = BranchID,
                JournalMasterID = JournalMasterID,
                LedgerID = LedgerID,
                Debit = Debit,
                Credit = Credit,
                Narration = Narration,
                Action = Action,
                CreatedDate = today,
                UpdatedDate = today,
                CreatedUserID = request.user.id,
                )

        instance.delete()
            

    response_data = {
        "status" : "true",
        "title" : str(_("Successfully Deleted")),
        "message" : str(_("Journal Entry Deleted Successfully.")),
        "redirect" : "true",
        "redirect_url" : reverse('accounts:journal_entries')
    }
    return HttpResponse(json.dumps(response_data), content_type='application/javascript')


@login_required
def create_bank_payment(request):
    from api.v1.payments.functions import get_auto_id, get_auto_idMaster
    user = request.user
    customer_instance = get_object_or_404(CustomerUser.objects.filter(user=user))
    db_id = customer_instance.databaseid
    datastore = get_object_or_404(DatabaseStore.objects.filter(id=db_id))
    DataBase = datastore.DefaultDatabase

    PaymentDetailsFormset = formset_factory(PaymentDetailsForm)
    today = datetime.date.today()
    if request.method == 'POST':
        form = PaymentMasterForm(request.POST,request.FILES)
        payment_details_formset = PaymentDetailsFormset(request.POST,prefix='payment_details_formset')
        if form.is_valid() and payment_details_formset.is_valid(): 
            data = form.save(commit=False)
            BranchID = 1
            data.BranchID = BranchID
            data.Action = 'A'
            data.PaymentMasterID = get_auto_idMaster(PaymentMaster,BranchID,DataBase)
            data.FinancialYearID = 1
            data.VoucherType = 'BP'
            data.VoucherNo  = generateVoucherNo(data.VoucherType, data.BranchID, DataBase)
            data.EmployeeID = request.user.id
            data.CreatedUserID = request.user.id
            data.CreatedDate = today
            data.UpdatedDate = today

            VoucherNoLow = data.VoucherNo.lower()
            is_voucherExist = False
            insts = PaymentMaster.objects.using(DataBase).filter(BranchID=BranchID)
            if insts:
                for i in insts:
                    voucher_no = i.VoucherNo
                    voucherNo = voucher_no.lower()
                    if VoucherNoLow == voucherNo:
                        is_voucherExist = True

            if not is_voucherExist:

                
                PaymentMaster_Log.objects.using(DataBase).create(
                    TransactionID=data.PaymentMasterID,
                    BranchID=data.BranchID,
                    Action=data.Action,
                    VoucherNo=data.VoucherNo,
                    VoucherType=data.VoucherType,
                    LedgerID=data.LedgerID,
                    EmployeeID=data.EmployeeID,
                    PaymentNo=data.VoucherNo,
                    FinancialYearID=data.FinancialYearID,
                    Date=data.Date,
                    TotalAmount=data.TotalAmount,
                    Notes=data.Notes,
                    IsActive=data.IsActive,
                    CreatedDate=data.CreatedDate,
                    UpdatedDate=data.UpdatedDate,
                    CreatedUserID=data.CreatedUserID
                    )
                data.save(using=DataBase)

                for f in payment_details_formset:
                    PaymentGateway = f.cleaned_data['PaymentGateway']
                    RefferenceNo = f.cleaned_data['RefferenceNo']
                    CardNetwork = f.cleaned_data['CardNetwork']
                    PaymentStatus = f.cleaned_data['PaymentStatus']
                    DueDate = f.cleaned_data['DueDate']
                    LedgerID = f.cleaned_data['LedgerID']
                    Amount = f.cleaned_data['Amount']
                    Balance = f.cleaned_data['Balance']
                    Discount = f.cleaned_data['Discount']
                    NetAmount = f.cleaned_data['NetAmount']
                    Narration = f.cleaned_data['Narration']

                    PaymentDetailsID = get_auto_id(PaymentDetails,BranchID,DataBase)
                
                    PaymentDetails.objects.using(DataBase).create(
                        PaymentDetailsID=PaymentDetailsID,
                        BranchID=BranchID,
                        Action=data.Action,
                        PaymentMasterID=data.PaymentMasterID,
                        payment_master=data,
                        PaymentGateway=PaymentGateway,
                        RefferenceNo=RefferenceNo,
                        CardNetwork=CardNetwork,
                        PaymentStatus=PaymentStatus,
                        DueDate=DueDate,
                        LedgerID=LedgerID,
                        Amount=Amount,
                        Balance=Balance,
                        Discount=Discount,
                        NetAmount=NetAmount,
                        Narration=Narration,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        CreatedUserID=data.CreatedUserID,
                        )
                    PaymentDetails_Log.objects.using(DataBase).create(
                        TransactionID=PaymentDetailsID,
                        BranchID=data.BranchID,
                        Action=data.Action,
                        PaymentMasterID=data.PaymentMasterID,
                        PaymentGateway=PaymentGateway,
                        RefferenceNo=RefferenceNo,
                        CardNetwork=CardNetwork,
                        PaymentStatus=PaymentStatus,
                        DueDate=DueDate,
                        LedgerID=LedgerID,
                        Amount=Amount,
                        Balance=Balance,
                        Discount=Discount,
                        NetAmount=NetAmount,
                        Narration=Narration,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        CreatedUserID=data.CreatedUserID,
                        )

                    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)


                    LedgerPosting.objects.using(DataBase).create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.PaymentMasterID,
                        VoucherDetailID=PaymentDetailsID,
                        VoucherType=data.VoucherType,
                        VoucherNo=data.VoucherNo,
                        LedgerID=data.LedgerID,
                        Debit=Amount,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        )

                    LedgerPosting_Log.objects.using(DataBase).create(
                        TransactionID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.PaymentMasterID,
                        VoucherDetailID=PaymentDetailsID,
                        VoucherNo=data.VoucherNo,
                        VoucherType=data.VoucherType,
                        LedgerID=data.LedgerID,
                        Debit=Amount,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        )

                    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

                    LedgerPosting.objects.using(DataBase).create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.PaymentMasterID,
                        VoucherDetailID=PaymentDetailsID,
                        VoucherType=data.VoucherType,
                        VoucherNo=data.VoucherNo,
                        LedgerID=data.LedgerID,
                        Credit=NetAmount,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        )

                    LedgerPosting_Log.objects.using(DataBase).create(
                        TransactionID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.PaymentMasterID,
                        VoucherDetailID=PaymentDetailsID,
                        VoucherNo=data.VoucherNo,
                        VoucherType=data.VoucherType,
                        LedgerID=data.LedgerID,
                        Credit=NetAmount,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        )

                    if float(Discount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

                        LedgerPosting.objects.using(DataBase).create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=data.BranchID,
                            Date=data.Date,
                            VoucherMasterID=data.PaymentMasterID,
                            VoucherDetailID=PaymentDetailsID,
                            VoucherType=data.VoucherType,
                            VoucherNo=data.VoucherNo,
                            LedgerID=82,
                            Credit=Discount,
                            IsActive=data.IsActive,
                            Action=data.Action,
                            CreatedUserID=data.CreatedUserID,
                            CreatedDate=data.CreatedDate,
                            UpdatedDate=data.UpdatedDate,
                            )

                        LedgerPosting_Log.objects.using(DataBase).create(
                            TransactionID=LedgerPostingID,
                            BranchID=data.BranchID,
                            Date=data.Date,
                            VoucherMasterID=data.PaymentMasterID,
                            VoucherDetailID=PaymentDetailsID,
                            VoucherNo=data.VoucherNo,
                            VoucherType=data.VoucherType,
                            LedgerID=82,
                            Credit=Discount,
                            IsActive=data.IsActive,
                            Action=data.Action,
                            CreatedUserID=data.CreatedUserID,
                            CreatedDate=data.CreatedDate,
                            UpdatedDate=data.UpdatedDate,
                            )


                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("Bank Payment Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('accounts:bank_payments')
                }
            else:
                message = generate_form_errors(form,formset=False)
                response_data = {
                    'status' : 'false',
                    'stable' : 'true',
                    'title' : str(_("Name Already Exist")),
                    "message" : str("Product Name Already Exist in this Branch!!!")
                }

        else:
            print(payment_details_formset.errors)
            # message = generate_form_errors(form,formset=False)
            message = generate_form_errors(payment_details_formset,formset=True)
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("Form validation error")),
                "message" : str(message)
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = PaymentMasterForm()
        payment_details_formset = PaymentDetailsFormset(prefix='payment_details_formset')

        context = {
            "title" : "Create Bank Payment",
            "form" : form,
            "payment_details_formset" : payment_details_formset,
            "is_need_formset" : True
        }
        return render(request,"accounts/transactions/create_bank_payment.html",context)


@login_required
def bank_payments(request):
    user = request.user
    customer_instance = get_object_or_404(CustomerUser.objects.filter(user=user))
    db_id = customer_instance.databaseid
    datastore = get_object_or_404(DatabaseStore.objects.filter(id=db_id))
    DataBase = datastore.DefaultDatabase

    BranchID = 1
    instances = PaymentMaster.objects.using(DataBase).filter(VoucherType='BP',BranchID=1)

    context = {
        'instances' : instances,
        'title' : 'Bank Payment'
    }
    return render(request,"accounts/transactions/bank_payments.html",context)  


@login_required
def bank_payment(request,pk):
    user = request.user
    customer_instance = get_object_or_404(CustomerUser.objects.filter(user=user))
    db_id = customer_instance.databaseid
    datastore = get_object_or_404(DatabaseStore.objects.filter(id=db_id))
    DataBase = datastore.DefaultDatabase

    instance = PaymentMaster.objects.using(DataBase).get(pk=pk)
    payment_details = PaymentDetails.objects.using(DataBase).filter(payment_master=instance)
    context = {
        'instance' : instance,
        'payment_details' : payment_details,
        'title' : 'Bank Payment'
    }
    return render(request,"accounts/transactions/bank_payment.html",context)


@login_required
def edit_bank_payment(request,pk):
    from api.v1.payments.functions import get_auto_id, get_auto_idMaster
    today = datetime.date.today()
    user = request.user
    customer_instance = get_object_or_404(CustomerUser.objects.filter(user=user))
    db_id = customer_instance.databaseid
    datastore = get_object_or_404(DatabaseStore.objects.filter(id=db_id))
    DataBase = datastore.DefaultDatabase


    instance = PaymentMaster.objects.using(DataBase).get(pk=pk)

    PaymentMasterID = instance.PaymentMasterID
    BranchID = instance.BranchID
    VoucherNo = instance.VoucherNo
    PaymentNo = instance.PaymentNo
    FinancialYearID = instance.FinancialYearID
    VoucherType = instance.VoucherType
    EmployeeID = instance.EmployeeID
    CreatedUserID = instance.CreatedUserID
    CreatedDate = instance.CreatedDate
    UpdatedDate = today

    Action = 'M'

    
    if PaymentDetails.objects.using(DataBase).filter(payment_master=instance).exists():
        extra = 0
    else:
        extra = 1
        
    PaymentDetailsFormset = inlineformset_factory(
                                            PaymentMaster, 
                                            PaymentDetails,
                                            can_delete=True,
                                            form=PaymentDetailsForm,
                                            extra=extra,
                                            )

    if request.method == 'POST':
        payment_details_formset = PaymentDetailsFormset(request.POST,request.FILES,prefix='payment_details_formset',instance=instance)
            
        form = PaymentMasterForm(request.POST,instance=instance)
        
        if form.is_valid(): 
            data = form.save(commit=False)
            BranchID = 1
            data.BranchID = BranchID
            data.Action = 'A'
            data.PaymentMasterID = get_auto_idMaster(PaymentMaster,BranchID,DataBase)
            data.FinancialYearID = 1
            data.VoucherType = 'BP'
            data.VoucherNo  = generateVoucherNo(data.VoucherType, data.BranchID, DataBase)
            data.EmployeeID = request.user.id
            data.CreatedUserID = request.user.id
            data.CreatedDate = today
            data.UpdatedDate = today

            VoucherNoLow = data.VoucherNo.lower()
            is_voucherExist = False
            insts = PaymentMaster.objects.using(DataBase).filter(BranchID=BranchID)
            if insts:
                for i in insts:
                    voucher_no = i.VoucherNo
                    voucherNo = voucher_no.lower()
                    if VoucherNoLow == voucherNo:
                        is_voucherExist = True

            if not is_voucherExist:

                
                PaymentMaster_Log.objects.using(DataBase).create(
                    TransactionID=data.PaymentMasterID,
                    BranchID=data.BranchID,
                    Action=data.Action,
                    VoucherNo=data.VoucherNo,
                    VoucherType=data.VoucherType,
                    LedgerID=data.LedgerID,
                    EmployeeID=data.EmployeeID,
                    PaymentNo=data.VoucherNo,
                    FinancialYearID=data.FinancialYearID,
                    Date=data.Date,
                    TotalAmount=data.TotalAmount,
                    Notes=data.Notes,
                    IsActive=data.IsActive,
                    CreatedDate=data.CreatedDate,
                    UpdatedDate=data.UpdatedDate,
                    CreatedUserID=data.CreatedUserID
                    )
                data.save(using=DataBase)

                payment_detail_items = payment_details_formset.save(commit=False)
                for item in payment_detail_items:
                    PaymentGateway = item.cleaned_data['PaymentGateway']
                    RefferenceNo = item.cleaned_data['RefferenceNo']
                    CardNetwork = item.cleaned_data['CardNetwork']
                    PaymentStatus = item.cleaned_data['PaymentStatus']
                    DueDate = item.cleaned_data['DueDate']
                    LedgerID = item.cleaned_data['LedgerID']
                    Amount = item.cleaned_data['Amount']
                    Balance = item.cleaned_data['Balance']
                    Discount = item.cleaned_data['Discount']
                    NetAmount = item.cleaned_data['NetAmount']
                    Narration = item.cleaned_data['Narration']

                    transactionType = TransactionTypes.objects.using(DataBase).get(Name="Bank")
                    transactionTypeID = transactionType.TransactionTypesID
                    PaymentGateway = transactionTypeID
                    PaymentDetailsID = get_auto_id(PaymentDetails,BranchID,DataBase)
                
                    PaymentDetails.objects.using(DataBase).create(
                        PaymentDetailsID=PaymentDetailsID,
                        BranchID=BranchID,
                        Action=data.Action,
                        PaymentMasterID=data.PaymentMasterID,
                        payment_master=data,
                        PaymentGateway=PaymentGateway,
                        RefferenceNo=RefferenceNo,
                        CardNetwork=CardNetwork,
                        PaymentStatus=PaymentStatus,
                        DueDate=DueDate,
                        LedgerID=LedgerID,
                        Amount=Amount,
                        Balance=Balance,
                        Discount=Discount,
                        NetAmount=NetAmount,
                        Narration=Narration,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        CreatedUserID=data.CreatedUserID,
                        )
                    PaymentDetails_Log.objects.using(DataBase).create(
                        TransactionID=PaymentDetailsID,
                        BranchID=data.BranchID,
                        Action=data.Action,
                        PaymentMasterID=data.PaymentMasterID,
                        PaymentGateway=PaymentGateway,
                        RefferenceNo=RefferenceNo,
                        CardNetwork=CardNetwork,
                        PaymentStatus=PaymentStatus,
                        DueDate=DueDate,
                        LedgerID=LedgerID,
                        Amount=Amount,
                        Balance=Balance,
                        Discount=Discount,
                        NetAmount=NetAmount,
                        Narration=Narration,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        CreatedUserID=data.CreatedUserID,
                        )

                    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)


                    LedgerPosting.objects.using(DataBase).update(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.PaymentMasterID,
                        VoucherDetailID=PaymentDetailsID,
                        VoucherType=data.VoucherType,
                        VoucherNo=data.VoucherNo,
                        LedgerID=data.LedgerID,
                        Debit=Amount,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        )

                    LedgerPosting_Log.objects.using(DataBase).create(
                        TransactionID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.PaymentMasterID,
                        VoucherDetailID=PaymentDetailsID,
                        VoucherNo=data.VoucherNo,
                        VoucherType=data.VoucherType,
                        LedgerID=data.LedgerID,
                        Debit=Amount,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        )

                    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

                    LedgerPosting.objects.using(DataBase).update(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.PaymentMasterID,
                        VoucherDetailID=PaymentDetailsID,
                        VoucherType=data.VoucherType,
                        VoucherNo=data.VoucherNo,
                        LedgerID=data.LedgerID,
                        Credit=NetAmount,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        )

                    LedgerPosting_Log.objects.using(DataBase).create(
                        TransactionID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.PaymentMasterID,
                        VoucherDetailID=PaymentDetailsID,
                        VoucherNo=data.VoucherNo,
                        VoucherType=data.VoucherType,
                        LedgerID=data.LedgerID,
                        Credit=NetAmount,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        )

                    if float(Discount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

                        LedgerPosting.objects.using(DataBase).update(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=data.BranchID,
                            Date=data.Date,
                            VoucherMasterID=data.PaymentMasterID,
                            VoucherDetailID=PaymentDetailsID,
                            VoucherType=data.VoucherType,
                            VoucherNo=data.VoucherNo,
                            LedgerID=82,
                            Credit=Discount,
                            IsActive=data.IsActive,
                            Action=data.Action,
                            CreatedUserID=data.CreatedUserID,
                            CreatedDate=data.CreatedDate,
                            UpdatedDate=data.UpdatedDate,
                            )

                        LedgerPosting_Log.objects.using(DataBase).create(
                            TransactionID=LedgerPostingID,
                            BranchID=data.BranchID,
                            Date=data.Date,
                            VoucherMasterID=data.PaymentMasterID,
                            VoucherDetailID=PaymentDetailsID,
                            VoucherNo=data.VoucherNo,
                            VoucherType=data.VoucherType,
                            LedgerID=82,
                            Credit=Discount,
                            IsActive=data.IsActive,
                            Action=data.Action,
                            CreatedUserID=data.CreatedUserID,
                            CreatedDate=data.CreatedDate,
                            UpdatedDate=data.UpdatedDate,
                            )
                for obj in payment_details_formset.deleted_objects:
                    obj.delete()


                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("Bank Payment Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('accounts:bank_payments')
                }
            else:
                message = generate_form_errors(form,formset=False)
                response_data = {
                    'status' : 'false',
                    'stable' : 'true',
                    'title' : str(_("Name Already Exist")),
                    "message" : str("Bank Payment Already Exist in this Branch!!!")
                }
        else:
            message = generate_form_errors(form,formset=True) 
            message = generate_form_errors(pricelist_formset,formset=True)     
                    
            response_data = {
                "status" : "false",
                "stable" : "true",
                "title" : "Form validation error",
                "message" : message
            }  
            
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')

    else: 
        instance = PaymentMaster.objects.using(DataBase).get(pk=pk)
        form = PaymentMasterForm(instance=instance)
        payment_details_formset = PaymentDetailsFormset(prefix='payment_details_formset',instance=instance)

        context = {
            "form" : form,
            "title" : "Edit Bank Payment : " + str(instance.PaymentMasterID),
            "instance" : instance,
            "payment_details_formset" : payment_details_formset,
            "redirect" : True,
            "is_need_formset" : True

        }
    return render(request,"accounts/transactions/create_bank_payment.html",context)


@login_required
def delete_bank_payment(request,pk):
    user = request.user
    customer_instance = get_object_or_404(CustomerUser.objects.filter(user=user))
    db_id = customer_instance.databaseid
    datastore = get_object_or_404(DatabaseStore.objects.filter(id=db_id))
    DataBase = datastore.DefaultDatabase


    today = datetime.date.today()
    # instance = None
    ledgerPostInstances = None
    if PaymentMaster.objects.using(DataBase).filter(pk=pk).exists():
        instance = PaymentMaster.objects.using(DataBase).get(pk=pk)
        PaymentMasterID = instance.PaymentMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        VoucherType = instance.VoucherType
        LedgerID = instance.LedgerID
        EmployeeID = instance.EmployeeID
        PaymentNo = instance.PaymentNo
        FinancialYearID = instance.FinancialYearID
        Date = instance.Date
        TotalAmount = instance.TotalAmount
        Notes = instance.Notes
        IsActive = instance.IsActive
        Action = "D"

        PaymentMaster_Log.objects.using(DataBase).create(
            TransactionID=PaymentMasterID,
            BranchID=BranchID,
            Action=Action,
            VoucherNo=VoucherNo,
            VoucherType=VoucherType,
            LedgerID=LedgerID,
            EmployeeID=EmployeeID,
            PaymentNo=PaymentNo,
            FinancialYearID=FinancialYearID,
            Date=Date,
            TotalAmount=TotalAmount,
            Notes=Notes,
            IsActive=IsActive,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=request.user.id
            )


        detail_instances = PaymentDetails.objects.using(DataBase).filter(PaymentMasterID=PaymentMasterID,BranchID=BranchID)
        for detail_instance in detail_instances:

            PaymentDetailsID = detail_instance.PaymentDetailsID
            BranchID = detail_instance.BranchID
            PaymentMasterID = detail_instance.PaymentMasterID
            payment_master = detail_instance.payment_master
            PaymentGateway = detail_instance.PaymentGateway
            RefferenceNo = detail_instance.RefferenceNo
            CardNetwork = detail_instance.CardNetwork
            PaymentStatus = detail_instance.PaymentStatus
            DueDate = detail_instance.DueDate
            LedgerID = detail_instance.LedgerID
            Amount = detail_instance.Amount
            Balance = detail_instance.Balance
            Discount = detail_instance.Discount
            NetAmount = detail_instance.NetAmount
            Narration = detail_instance.Narration
            CreatedUserID = detail_instance.CreatedUserID

            detail_instance.delete()

            PaymentDetails_Log.objects.using(DataBase).create(
                TransactionID=PaymentDetailsID,
                BranchID=BranchID,
                Action=Action,
                PaymentMasterID=PaymentMasterID,
                PaymentGateway=PaymentGateway,
                RefferenceNo=RefferenceNo,
                CardNetwork=CardNetwork,
                PaymentStatus=PaymentStatus,
                DueDate=DueDate,
                LedgerID=LedgerID,
                Amount=Amount,
                Balance=Balance,
                Discount=Discount,
                NetAmount=NetAmount,
                Narration=Narration,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                )

            

            if LedgerPosting.objects.using(DataBase).filter(VoucherMasterID=PaymentMasterID,BranchID=BranchID,VoucherType="BP").exists():
                ledgerPostInstances = LedgerPosting.objects.using(DataBase).filter(VoucherMasterID=PaymentMasterID,BranchID=BranchID,VoucherType="BP")
                
                for ledgerPostInstance in ledgerPostInstances:

                    LedgerPostingID = ledgerPostInstance.LedgerPostingID
                    VoucherType = ledgerPostInstance.VoucherType
                    Debit = ledgerPostInstance.Debit
                    Credit = ledgerPostInstance.Credit
                    IsActive = ledgerPostInstance.IsActive
                    Date = ledgerPostInstance.Date
                    LedgerID = ledgerPostInstance.LedgerID
                    CreatedUserID = ledgerPostInstance.CreatedUserID

                    LedgerPosting_Log.objects.using(DataBase).create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PaymentMasterID,
                        VoucherDetailID=PaymentDetailsID,
                        VoucherNo=VoucherNo,
                        VoucherType=VoucherType,
                        LedgerID=LedgerID,
                        Debit=Debit,
                        Credit=Credit,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        )

                    ledgerPostInstance.delete()
        instance.delete()

        response_data = {
            "status" : "true",
            "title" : str(_("Successfully Deleted")),
            "message" : str(_("Bank Payment Deleted Successfully.")),
            "redirect" : "true",
            "redirect_url" : reverse('accounts:bank_payments')
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')


@login_required
def create_bank_receipt(request):
    from api.v1.receipts.functions import get_auto_id, get_auto_idMaster
    DataBase = get_DataBase(request)

    ReceiptDetailsFormset = formset_factory(ReceiptDetailsForm)
    today = datetime.date.today()
    if request.method == 'POST':
        form = ReceiptMasterForm(request.POST,request.FILES)
        receipt_details_formset = ReceiptDetailsFormset(request.POST,prefix='receipt_details_formset')
        if form.is_valid() and receipt_details_formset.is_valid(): 
            data = form.save(commit=False)
            BranchID = 1
            data.BranchID = BranchID
            data.Action = 'A'
            data.ReceiptMasterID = get_auto_idMaster(ReceiptMaster,BranchID,DataBase)
            data.FinancialYearID = 1
            data.VoucherType = "BR"
            data.VoucherNo  = generateVoucherNo(data.VoucherType, data.BranchID, DataBase)
            data.ReceiptNo = str(data.VoucherType) + str(data.VoucherNo)
            data.EmployeeID = request.user.id
            data.CreatedUserID = request.user.id
            data.CreatedDate = today
            data.UpdatedDate = today


            VoucherNoLow = data.VoucherNo.lower()
            is_voucherExist = False
            insts = ReceiptMaster.objects.using(DataBase).filter(BranchID=BranchID)
            if insts:
                for i in insts:
                    voucher_no = i.VoucherNo
                    voucherNo = voucher_no.lower()
                    if VoucherNoLow == voucherNo:
                        is_voucherExist = True

            if not is_voucherExist:

                
                ReceiptMaster_Log.objects.using(DataBase).create(
                    TransactionID=data.ReceiptMasterID,
                    BranchID=data.BranchID,
                    Action=data.Action,
                    VoucherNo=data.VoucherNo,
                    VoucherType=data.VoucherType,
                    ReceiptNo=data.ReceiptNo,
                    LedgerID=data.LedgerID,
                    EmployeeID=data.EmployeeID,
                    FinancialYearID=data.FinancialYearID,
                    Date=data.Date,
                    TotalAmount=data.TotalAmount,
                    Notes=data.Notes,
                    IsActive=data.IsActive,
                    CreatedDate=data.CreatedDate,
                    UpdatedDate=data.UpdatedDate,
                    CreatedUserID=data.CreatedUserID
                    )
                data.save(using=DataBase)

                for f in receipt_details_formset:
                    PaymentGateway = f.cleaned_data['PaymentGateway']
                    RefferenceNo = f.cleaned_data['RefferenceNo']
                    CardNetwork = f.cleaned_data['CardNetwork']
                    PaymentStatus = f.cleaned_data['PaymentStatus']
                    DueDate = f.cleaned_data['DueDate']
                    LedgerID = f.cleaned_data['LedgerID']
                    Amount = f.cleaned_data['Amount']
                    Balance = f.cleaned_data['Balance']
                    Discount = f.cleaned_data['Discount']
                    NetAmount = f.cleaned_data['NetAmount']
                    Narration = f.cleaned_data['Narration']

                    transactionType = TransactionTypes.objects.using(DataBase).get(Name="Cash")
                    transactionTypeID = transactionType.TransactionTypesID
                    PaymentGateway = transactionTypeID
                    ReceiptDetailID = get_auto_id(ReceiptDetails,BranchID,DataBase)
                
                    ReceiptDetails.objects.using(DataBase).create(
                        ReceiptDetailID=ReceiptDetailID,
                        BranchID=BranchID,
                        Action=data.Action,
                        ReceiptMasterID=data.ReceiptMasterID,
                        VoucherType=data.VoucherType,
                        receipt_master=data,
                        PaymentGateway=PaymentGateway,
                        RefferenceNo=RefferenceNo,
                        CardNetwork=CardNetwork,
                        PaymentStatus=PaymentStatus,
                        DueDate=DueDate,
                        LedgerID=LedgerID,
                        Amount=Amount,
                        Balance=Balance,
                        Discount=Discount,
                        NetAmount=NetAmount,
                        Narration=Narration,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        CreatedUserID=data.CreatedUserID,
                        )

                    ReceiptDetails_Log.objects.using(DataBase).create(
                        TransactionID=ReceiptDetailID,
                        BranchID=data.BranchID,
                        Action=data.Action,
                        ReceiptMasterID=data.ReceiptMasterID,
                        VoucherType=data.VoucherType,
                        PaymentGateway=PaymentGateway,
                        RefferenceNo=RefferenceNo,
                        CardNetwork=CardNetwork,
                        PaymentStatus=PaymentStatus,
                        DueDate=DueDate,
                        LedgerID=LedgerID,
                        Amount=Amount,
                        Balance=Balance,
                        Discount=Discount,
                        NetAmount=NetAmount,
                        Narration=Narration,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        CreatedUserID=data.CreatedUserID,
                        )

                    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)


                    LedgerPosting.objects.using(DataBase).create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.ReceiptMasterID,
                        VoucherDetailID=ReceiptDetailID,
                        VoucherType=data.VoucherType,
                        VoucherNo=data.VoucherNo,
                        LedgerID=data.LedgerID,
                        Credit=Amount,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        )


                    LedgerPosting_Log.objects.using(DataBase).create(
                        TransactionID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.ReceiptMasterID,
                        VoucherDetailID=ReceiptDetailID,
                        VoucherNo=data.VoucherNo,
                        VoucherType=data.VoucherType,
                        LedgerID=data.LedgerID,
                        Credit=Amount,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        )

                    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

                    LedgerPosting.objects.using(DataBase).create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.ReceiptMasterID,
                        VoucherDetailID=ReceiptDetailID,
                        VoucherType=data.VoucherType,
                        VoucherNo=data.VoucherNo,
                        LedgerID=data.LedgerID,
                        Debit=NetAmount,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        )

                    LedgerPosting_Log.objects.using(DataBase).create(
                        TransactionID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.ReceiptMasterID,
                        VoucherDetailID=ReceiptDetailID,
                        VoucherNo=data.VoucherNo,
                        VoucherType=data.VoucherType,
                        LedgerID=data.LedgerID,
                        Debit=NetAmount,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        )

                    if float(Discount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

                        LedgerPosting.objects.using(DataBase).create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=data.BranchID,
                            Date=data.Date,
                            VoucherMasterID=data.ReceiptMasterID,
                            VoucherDetailID=ReceiptDetailID,
                            VoucherType=data.VoucherType,
                            VoucherNo=data.VoucherNo,
                            LedgerID=82,
                            Debit=Discount,
                            IsActive=data.IsActive,
                            Action=data.Action,
                            CreatedUserID=data.CreatedUserID,
                            CreatedDate=data.CreatedDate,
                            UpdatedDate=data.UpdatedDate,
                            )

                        LedgerPosting_Log.objects.using(DataBase).create(
                            TransactionID=LedgerPostingID,
                            BranchID=data.BranchID,
                            Date=data.Date,
                            VoucherMasterID=data.ReceiptMasterID,
                            VoucherDetailID=ReceiptDetailID,
                            VoucherNo=data.VoucherNo,
                            VoucherType=data.VoucherType,
                            LedgerID=82,
                            Debit=Discount,
                            IsActive=data.IsActive,
                            Action=data.Action,
                            CreatedUserID=data.CreatedUserID,
                            CreatedDate=data.CreatedDate,
                            UpdatedDate=data.UpdatedDate,
                            )


                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("Cash Receipt Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('accounts:cash_receipts')
                }
            else:
                message = generate_form_errors(form,formset=False)
                response_data = {
                    'status' : 'false',
                    'stable' : 'true',
                    'title' : str(_("Name Already Exist")),
                    "message" : str("Voucher Number Already Exist in this Branch!!!")
                }

        else:
            print(receipt_details_formset.errors)
            # message = generate_form_errors(form,formset=False)
            message = generate_form_errors(receipt_details_formset,formset=True)
            response_data = {
                'status' : 'false',
                'stable' : 'true',
                'title' : str(_("Form validation error")),
                "message" : str(message)
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        form = ReceiptMasterForm()
        receipt_details_formset = ReceiptDetailsFormset(prefix='receipt_details_formset')

        context = {
            "title" : "Create Cash Receipt",
            "form" : form,
            "receipt_details_formset" : receipt_details_formset,
            "is_need_formset" : True
        }
        return render(request,"accounts/transactions/create_bank_receipt.html",context)


@login_required
def bank_receipts(request):
    DataBase = get_DataBase(request)

    BranchID = 1
    VoucherType = 'BR'
    instances = ReceiptMaster.objects.using(DataBase).filter(BranchID=BranchID, VoucherType=VoucherType)

    context = {
        'instances' : instances,
        'title' : 'Cash Receipt'
    }
    return render(request,"accounts/transactions/cash_receipts.html",context)  


@login_required
def bank_receipt(request, pk):
    DataBase = get_DataBase(request)

    instance = ReceiptMaster.objects.using(DataBase).get(pk=pk)
    receipt_details = ReceiptDetails.objects.using(DataBase).filter(receipt_master=instance)
    context = {
        'instance' : instance,
        'receipt_details' : receipt_details,
        'title' : 'Receipt'
    }
    return render(request,"accounts/transactions/cash_receipt.html",context)


@login_required
def edit_bank_receipt(request,pk):
    from api.v1.receipts.functions import get_auto_id, get_auto_idMaster
    today = datetime.date.today()
    DataBase = get_DataBase(request)


    instance = ReceiptMaster.objects.using(DataBase).get(pk=pk)

    ReceiptMasterID = instance.ReceiptMasterID
    BranchID = instance.BranchID
    VoucherNo = instance.VoucherNo
    ReceiptNo = instance.ReceiptNo
    FinancialYearID = instance.FinancialYearID
    VoucherType = instance.VoucherType
    EmployeeID = instance.EmployeeID
    CreatedUserID = instance.CreatedUserID
    CreatedDate = instance.CreatedDate
    UpdatedDate = today

    Action = 'M'

    
    if ReceiptDetails.objects.using(DataBase).filter(receipt_master=instance).exists():
        extra = 0
    else:
        extra = 1
        
    ReceiptDetailsFormset = inlineformset_factory(
                                            ReceiptMaster, 
                                            ReceiptDetails,
                                            can_delete=True,
                                            form=ReceiptDetailsForm,
                                            extra=extra,
                                            )

    if request.method == 'POST':
        receipt_details_formset = ReceiptDetailsFormset(request.POST,request.FILES,prefix='receipt_details_formset',instance=instance)
            
        form = ReceiptMasterForm(request.POST,instance=instance)
        
        if form.is_valid(): 
            data = form.save(commit=False)
            BranchID = 1
            data.BranchID = BranchID
            data.Action = 'A'
            data.ReceiptMasterID = instance.ReceiptMasterID
            data.FinancialYearID = 1
            data.VoucherType = VoucherType
            data.VoucherNo  = instance.VoucherNo
            data.EmployeeID = request.user.id
            data.CreatedUserID = request.user.id
            data.CreatedDate = today
            data.UpdatedDate = today

                
            ReceiptMaster_Log.objects.using(DataBase).create(
                TransactionID=data.ReceiptMasterID,
                BranchID=data.BranchID,
                Action=data.Action,
                VoucherNo=data.VoucherNo,
                VoucherType=data.VoucherType,
                LedgerID=data.LedgerID,
                EmployeeID=data.EmployeeID,
                ReceiptNo=data.ReceiptNo,
                FinancialYearID=data.FinancialYearID,
                Date=data.Date,
                TotalAmount=data.TotalAmount,
                Notes=data.Notes,
                IsActive=data.IsActive,
                CreatedDate=data.CreatedDate,
                UpdatedDate=data.UpdatedDate,
                CreatedUserID=data.CreatedUserID
                )

            receipt_detail_items = receipt_details_formset.save(commit=False)
            for item in receipt_detail_items:
                PaymentGateway = item.cleaned_data['PaymentGateway']
                RefferenceNo = item.cleaned_data['RefferenceNo']
                CardNetwork = item.cleaned_data['CardNetwork']
                PaymentStatus = item.cleaned_data['PaymentStatus']
                DueDate = item.cleaned_data['DueDate']
                LedgerID = item.cleaned_data['LedgerID']
                Amount = item.cleaned_data['Amount']
                Balance = item.cleaned_data['Balance']
                Discount = item.cleaned_data['Discount']
                NetAmount = item.cleaned_data['NetAmount']
                Narration = item.cleaned_data['Narration']

                transactionType = TransactionTypes.objects.using(DataBase).get(Name="Cash")
                transactionTypeID = transactionType.TransactionTypesID
                PaymentGateway = transactionTypeID
                ReceiptDetailsID = get_auto_id(ReceiptDetails,BranchID,DataBase)
            
                ReceiptDetails.objects.using(DataBase).create(
                    ReceiptDetailsID=ReceiptDetailsID,
                    BranchID=BranchID,
                    Action=data.Action,
                    ReceiptMasterID=data.ReceiptMasterID,
                    receipt_master=data,
                    PaymentGateway=PaymentGateway,
                    RefferenceNo=RefferenceNo,
                    CardNetwork=CardNetwork,
                    PaymentStatus=PaymentStatus,
                    DueDate=DueDate,
                    LedgerID=LedgerID,
                    Amount=Amount,
                    Balance=Balance,
                    Discount=Discount,
                    NetAmount=NetAmount,
                    Narration=Narration,
                    CreatedDate=data.CreatedDate,
                    UpdatedDate=data.UpdatedDate,
                    CreatedUserID=data.CreatedUserID,
                    )
                ReceiptDetails_Log.objects.using(DataBase).create(
                    TransactionID=ReceiptDetailsID,
                    BranchID=data.BranchID,
                    Action=data.Action,
                    ReceiptMasterID=data.ReceiptMasterID,
                    PaymentGateway=PaymentGateway,
                    RefferenceNo=RefferenceNo,
                    CardNetwork=CardNetwork,
                    PaymentStatus=PaymentStatus,
                    DueDate=DueDate,
                    LedgerID=LedgerID,
                    Amount=Amount,
                    Balance=Balance,
                    Discount=Discount,
                    NetAmount=NetAmount,
                    Narration=Narration,
                    CreatedDate=data.CreatedDate,
                    UpdatedDate=data.UpdatedDate,
                    CreatedUserID=data.CreatedUserID,
                    )

                LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)


                LedgerPosting.objects.using(DataBase).update(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=data.BranchID,
                    Date=data.Date,
                    VoucherMasterID=data.ReceiptMasterID,
                    VoucherDetailID=ReceiptDetailsID,
                    VoucherType=data.VoucherType,
                    VoucherNo=data.VoucherNo,
                    LedgerID=data.LedgerID,
                    Credit=Amount,
                    IsActive=data.IsActive,
                    Action=data.Action,
                    CreatedUserID=data.CreatedUserID,
                    CreatedDate=data.CreatedDate,
                    UpdatedDate=data.UpdatedDate,
                    )

                LedgerPosting_Log.objects.using(DataBase).create(
                    TransactionID=LedgerPostingID,
                    BranchID=data.BranchID,
                    Date=data.Date,
                    VoucherMasterID=data.ReceiptMasterID,
                    VoucherDetailID=ReceiptDetailsID,
                    VoucherNo=data.VoucherNo,
                    VoucherType=data.VoucherType,
                    LedgerID=data.LedgerID,
                    Credit=Amount,
                    IsActive=data.IsActive,
                    Action=data.Action,
                    CreatedUserID=data.CreatedUserID,
                    CreatedDate=data.CreatedDate,
                    UpdatedDate=data.UpdatedDate,
                    )

                LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

                LedgerPosting.objects.using(DataBase).update(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=data.BranchID,
                    Date=data.Date,
                    VoucherMasterID=data.ReceiptMasterID,
                    VoucherDetailID=ReceiptDetailsID,
                    VoucherType=data.VoucherType,
                    VoucherNo=data.VoucherNo,
                    LedgerID=data.LedgerID,
                    Debit=NetAmount,
                    IsActive=data.IsActive,
                    Action=data.Action,
                    CreatedUserID=data.CreatedUserID,
                    CreatedDate=data.CreatedDate,
                    UpdatedDate=data.UpdatedDate,
                    )

                LedgerPosting_Log.objects.using(DataBase).create(
                    TransactionID=LedgerPostingID,
                    BranchID=data.BranchID,
                    Date=data.Date,
                    VoucherMasterID=data.ReceiptMasterID,
                    VoucherDetailID=ReceiptDetailsID,
                    VoucherNo=data.VoucherNo,
                    VoucherType=data.VoucherType,
                    LedgerID=data.LedgerID,
                    Debit=NetAmount,
                    IsActive=data.IsActive,
                    Action=data.Action,
                    CreatedUserID=data.CreatedUserID,
                    CreatedDate=data.CreatedDate,
                    UpdatedDate=data.UpdatedDate,
                    )

                if float(Discount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,DataBase)

                    LedgerPosting.objects.using(DataBase).update(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.ReceiptMasterID,
                        VoucherDetailID=ReceiptDetailsID,
                        VoucherType=data.VoucherType,
                        VoucherNo=data.VoucherNo,
                        LedgerID=82,
                        Debit=Discount,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        )

                    LedgerPosting_Log.objects.using(DataBase).create(
                        TransactionID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=data.Date,
                        VoucherMasterID=data.ReceiptMasterID,
                        VoucherDetailID=ReceiptDetailsID,
                        VoucherNo=data.VoucherNo,
                        VoucherType=data.VoucherType,
                        LedgerID=82,
                        Debit=Discount,
                        IsActive=data.IsActive,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=data.CreatedDate,
                        UpdatedDate=data.UpdatedDate,
                        )

            data.save(using=DataBase)
            for obj in receipt_details_formset.deleted_objects:
                obj.delete()


            response_data = {
                "status" : "true",
                "title" : str(_("Successfully Created")),
                "message" : str(_("Cash Receipt Created Successfully!")),
                "redirect" : "true",
                "redirect_url" : reverse('accounts:cash_receipts')
            }

        else:
            message = generate_form_errors(form,formset=False) 
            message = generate_form_errors(receipt_details_formset,formset=True)     
                    
            response_data = {
                "status" : "false",
                "stable" : "true",
                "title" : "Form validation error",
                "message" : message
            }  
            
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')

    else: 
        instance = ReceiptMaster.objects.using(DataBase).get(pk=pk)
        form = ReceiptMasterForm(instance=instance)
        receipt_details_formset = ReceiptDetailsFormset(prefix='receipt_details_formset',instance=instance)

        context = {
            "form" : form,
            "title" : "Edit Cash Receipt : " + str(instance.ReceiptMasterID),
            "instance" : instance,
            "receipt_details_formset" : receipt_details_formset,
            "redirect" : True,
            "is_need_formset" : True

        }
    return render(request,"accounts/transactions/create_bank_receipt.html",context)


@login_required
def delete_bank_receipt(request,pk):
    DataBase = get_DataBase(request)


    today = datetime.date.today()
    # instance = None
    ledgerPostInstances = None
    if ReceiptMaster.objects.using(DataBase).filter(pk=pk).exists():
        instance = ReceiptMaster.objects.using(DataBase).get(pk=pk)
        ReceiptMasterID = instance.ReceiptMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        VoucherType = instance.VoucherType
        LedgerID = instance.LedgerID
        EmployeeID = instance.EmployeeID
        ReceiptNo = instance.ReceiptNo
        FinancialYearID = instance.FinancialYearID
        Date = instance.Date
        TotalAmount = instance.TotalAmount
        Notes = instance.Notes
        IsActive = instance.IsActive
        Action = "D"

        ReceiptMaster_Log.objects.using(DataBase).create(
            TransactionID=ReceiptMasterID,
            BranchID=BranchID,
            Action=Action,
            VoucherNo=VoucherNo,
            VoucherType=VoucherType,
            ReceiptNo=ReceiptNo,
            LedgerID=LedgerID,
            EmployeeID=EmployeeID,
            FinancialYearID=FinancialYearID,
            Date=Date,
            TotalAmount=TotalAmount,
            Notes=Notes,
            IsActive=IsActive,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=request.user.id
            )


        detail_instances = ReceiptDetails.objects.using(DataBase).filter(ReceiptMasterID=ReceiptMasterID,BranchID=BranchID)
        for detail_instance in detail_instances:

            ReceiptDetailID = detail_instance.ReceiptDetailID
            BranchID = detail_instance.BranchID
            ReceiptMasterID = detail_instance.ReceiptMasterID
            receipt_master = detail_instance.receipt_master
            PaymentGateway = detail_instance.PaymentGateway
            RefferenceNo = detail_instance.RefferenceNo
            CardNetwork = detail_instance.CardNetwork
            PaymentStatus = detail_instance.PaymentStatus
            DueDate = detail_instance.DueDate
            LedgerID = detail_instance.LedgerID
            Amount = detail_instance.Amount
            Balance = detail_instance.Balance
            Discount = detail_instance.Discount
            NetAmount = detail_instance.NetAmount
            Narration = detail_instance.Narration
            CreatedUserID = detail_instance.CreatedUserID

            detail_instance.delete()

            ReceiptDetails_Log.objects.using(DataBase).create(
                TransactionID=ReceiptDetailID,
                BranchID=BranchID,
                Action=Action,
                ReceiptMasterID=ReceiptMasterID,
                PaymentGateway=PaymentGateway,
                RefferenceNo=RefferenceNo,
                CardNetwork=CardNetwork,
                PaymentStatus=PaymentStatus,
                DueDate=DueDate,
                LedgerID=LedgerID,
                Amount=Amount,
                Balance=Balance,
                Discount=Discount,
                NetAmount=NetAmount,
                Narration=Narration,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                )

            

            if LedgerPosting.objects.using(DataBase).filter(VoucherMasterID=ReceiptMasterID,BranchID=BranchID,VoucherType="CP").exists():
                ledgerPostInstances = LedgerPosting.objects.using(DataBase).filter(VoucherMasterID=ReceiptMasterID,BranchID=BranchID,VoucherType="CP")
                
                for ledgerPostInstance in ledgerPostInstances:

                    LedgerPostingID = ledgerPostInstance.LedgerPostingID
                    VoucherType = ledgerPostInstance.VoucherType
                    Debit = ledgerPostInstance.Debit
                    Credit = ledgerPostInstance.Credit
                    IsActive = ledgerPostInstance.IsActive
                    Date = ledgerPostInstance.Date
                    LedgerID = ledgerPostInstance.LedgerID
                    CreatedUserID = ledgerPostInstance.CreatedUserID

                    LedgerPosting_Log.objects.using(DataBase).create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ReceiptMasterID,
                        VoucherDetailID=PaymentDetailsID,
                        VoucherNo=VoucherNo,
                        VoucherType=VoucherType,
                        LedgerID=LedgerID,
                        Debit=Debit,
                        Credit=Credit,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        )

                    ledgerPostInstance.delete()
        instance.delete()

    response_data = {
        "status" : "true",
        "title" : str(_("Successfully Deleted")),
        "message" : str(_("Cash Receipt Deleted Successfully.")),
        "redirect" : "true",
        "redirect_url" : reverse('accounts:cash_receipts')
    }
    return HttpResponse(json.dumps(response_data), content_type='application/javascript')