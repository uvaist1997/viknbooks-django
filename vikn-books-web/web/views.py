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
from brands.models import Brand, AccountGroup, Branch, Brand_Log, Branch_Log, AccountLedger, AccountGroup, AccountLedger_Log, LedgerPosting, LedgerPosting_Log,\
 Parties, Parties_Log, PurchaseOrderMaster, SalesOrderMaster, Employee, Bank, Bank_Log
from web.forms import BrandForm, BranchForm, AccountLedgerForm, BankForm
from web.functions import generate_form_errors,get_auto_id, get_auto_Branchid, get_auto_LedgerID
from api.v1.accountLedgers.functions import get_LedgerCode, get_auto_LedgerPostid, get_auto_idfor_party
from api.v1.banks.functions import get_auto_Bankid
from django.utils.translation import gettext_lazy as _
import datetime


# ==============webbbbbbbb1111
def dashboard(request):
    context = {
        "title" : "dashboard"
    }
    return render(request,"dashboard.html",context)


def home(request):
    context = {
        "title" : "viknbooks"
    }
    return render(request,"web/index.html",context)


def create_brand(request):
    today = datetime.date.today()
    if request.method == 'POST':
        form = BrandForm(request.POST)
        if form.is_valid(): 
            data = form.save(commit=False)
            BrandName = data.BrandName

            is_nameExist = False
            BrandNameLow = BrandName.lower()
            brands = Brand.objects.filter(BranchID=1)

            for brand in brands:
                brand_name = brand.BrandName
                brandName = brand_name.lower()

                if BrandNameLow == brandName:
                    is_nameExist = True

            if not is_nameExist:
                data.CreatedDate = today
                data.Action = "A"
                data.BranchID = 1
                data.CreatedUserID = 1
                data.BrandID = get_auto_id(Brand,data.BranchID)
                Brand_Log.objects.create(
                    BranchID=data.BranchID,
                    TransactionID=data.BrandID,
                    BrandName=data.BrandName,
                    Notes=data.Notes,
                    CreatedDate=today,
                    CreatedUserID=1,
                    Action=data.Action,
                    )
                data.save()

                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("Brand Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('web:brands')
                }
            else:
                response_data = {
                    "status" : "false",
                    "title" : str(_("Brand Already Exist")),
                    "message" : str(_("Brand Name is Already exist with in the BranchID")),
                    "redirect" : "true",
                    "redirect_url" : reverse('web:create_brand')
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
        form = BrandForm()
        context = {
            "title" : "create Brand",
            "form" : form
        }
        return render(request,"entry_brand.html",context)


def brands(request):
    instances = Brand.objects.all()
    context = {
        'instances' : instances,
    }
    return render(request,"brands.html",context)



def edit_brand(request,pk):
    today = datetime.date.today()
    instance = Brand.objects.get(pk=pk)
    instanceBrandName = instance.BrandName
    if request.method == 'POST':
        form = BrandForm(request.POST,instance=instance)
        if form.is_valid(): 
            data = form.save(commit=False)
            BrandName = data.BrandName
            is_nameExist = False
            brand_ok = False

            BrandNameLow = BrandName.lower()

            brands = Brand.objects.filter(BranchID=1)

            for brand in brands:
                brand_name = brand.BrandName

                brandName = brand_name.lower()

                if BrandNameLow == brandName:
                    is_nameExist = True

                if instanceBrandName.lower() == BrandNameLow:
                    brand_ok = True
            if brand_ok:
                data.CreatedDate = today
                data.Action = "M"
                data.BranchID = 1
                data.CreatedUserID = 1
                data.BrandID = get_auto_id(Brand,data.BranchID)
                Brand_Log.objects.create(
                    BranchID=data.BranchID,
                    TransactionID=data.BrandID,
                    BrandName=data.BrandName,
                    Notes=data.Notes,
                    CreatedDate=today,
                    CreatedUserID=1,
                    Action=data.Action,
                    )
                data.save()

                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("Brand Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('web:brands')
                }
            else:
                if is_nameExist:
                    response_data = {
                        "status" : "false",
                        "title" : str(_("Brand Already Exist")),
                        "message" : str(_("Brand Name is Already exist with in the BranchID")),
                        "redirect" : "true",
                        "redirect_url" : reverse('web:create_brand')
                    }
                else:
                    data.CreatedDate = today
                    data.Action = "M"
                    data.BranchID = 1
                    data.CreatedUserID = 1
                    data.BrandID = get_auto_id(Brand,data.BranchID)
                    Brand_Log.objects.create(
                        BranchID=data.BranchID,
                        TransactionID=data.BrandID,
                        BrandName=data.BrandName,
                        Notes=data.Notes,
                        CreatedDate=today,
                        CreatedUserID=1,
                        Action=data.Action,
                        )
                    data.save()

                    response_data = {
                        "status" : "true",
                        "title" : str(_("Successfully Updated")),
                        "message" : str(_("Branch Updated Successfully!")),
                        "redirect" : "true",
                        "redirect_url" : reverse('web:brands')
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
        form = BrandForm(instance=instance)
        context = {
            "title" : "Edit Brand",
            "form" : form
        }
        return render(request,"entry_brand.html",context)


def delete_brand(request,pk):
    today = datetime.date.today()    
    instance = Brand.objects.get(pk=pk)
    if pk == "1":
        response_data = {
            'status' : 'false',
            'stable' : 'true',
            'title' : str(_("can't delete this brand")),
            "message" : str(_("Can't delete this brand! this is default brand!"))
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        instance.delete()
        Brand_Log.objects.create(
            BranchID=instance.BranchID,
            TransactionID=instance.BrandID,
            BrandName=instance.BrandName,
            Notes=instance.Notes,
            CreatedDate=today,
            CreatedUserID=1,
            Action="D",
            )
        
        response_data = {
            "status" : "true",
            "title" : str(_("Successfully Deleted")),
            "message" : str(_("Brand Deleted Successfully.")),
            "redirect" : "true",
            "redirect_url" : reverse('web:brands')
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')


def account_groups(request):
    instances = AccountGroup.objects.all()
    context = {
        'instances' : instances,
    }
    return render(request,"account_groups.html",context)


def create_branch(request):
    today = datetime.date.today()
    if request.method == 'POST':
        form = BranchForm(request.POST)
        if form.is_valid(): 
            data = form.save(commit=False)
            data.CreatedDate = today
            data.Action = "A"
            data.CreatedUserID = 1
            data.BranchID = get_auto_Branchid(Branch)
            Branch_Log.objects.create(
                TransactionID=data.BranchID,
                BranchName=data.BranchName,
                BranchLocation=data.BranchLocation,
                Action=data.Action,
                CreatedUserID=data.CreatedUserID,
                CreatedDate=today,
                )
            data.save()

            response_data = {
                "status" : "true",
                "title" : str(_("Successfully Created")),
                "message" : str(_("Branch Created Successfully!")),
                "redirect" : "true",
                "redirect_url" : reverse('web:branchs')
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
            "title" : "create Branch",
            "form" : form
        }
        return render(request,"entry_branch.html",context)


def branchs(request):
    instances = Branch.objects.all()
    context = {
        'instances' : instances,
    }
    return render(request,"branchs.html",context)


def edit_branch(request,pk):
    today = datetime.date.today()
    instance = Branch.objects.get(pk=pk)
    if request.method == 'POST':
        form = BranchForm(request.POST,instance=instance)
        if form.is_valid(): 
            data = form.save(commit=False)
            data.CreatedDate = today
            data.Action = "M"
            data.BranchID = 1
            data.CreatedUserID = 1
            data.BranchID = get_auto_Branchid(Branch)
            Branch_Log.objects.create(
                TransactionID=data.BranchID,
                BranchName=data.BranchName,
                BranchLocation=data.BranchLocation,
                Action=data.Action,
                CreatedUserID=data.CreatedUserID,
                CreatedDate=today,
                )
            data.save()

            response_data = {
                "status" : "true",
                "title" : str(_("Successfully Updated")),
                "message" : str(_("Branch Updated Successfully!")),
                "redirect" : "true",
                "redirect_url" : reverse('web:branchs')
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
            "title" : "Edit Branch",
            "form" : form
        }
        return render(request,"entry_branch.html",context)


def delete_branch(request,pk):
    today = datetime.date.today()    
    instance = Branch.objects.get(pk=pk)
    if pk == "1":
        response_data = {
            'status' : 'false',
            'stable' : 'true',
            'title' : str(_("can't delete this brand")),
            "message" : str(_("Can't delete this brand! this is default brand!"))
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        instance.delete()
        Branch_Log.objects.create(
            TransactionID=instance.BranchID,
            BranchName=instance.BranchName,
            BranchLocation=instance.BranchLocation,
            Action=instance.Action,
            CreatedUserID=instance.CreatedUserID,
            CreatedDate=today,
            )
        
        response_data = {
            "status" : "true",
            "title" : str(_("Successfully Deleted")),
            "message" : str(_("Branch Deleted Successfully.")),
            "redirect" : "true",
            "redirect_url" : reverse('web:branchs')
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')


def create_accountLedger(request):
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
            ledgers = AccountLedger.objects.filter(BranchID=1)

            for ledger in ledgers:
                ledger_name = ledger.LedgerName
                LedgerName = ledger_name.lower()

                if LedgerNameLow == LedgerName:
                    is_nameExist = True

            if not is_nameExist:
                data.CreatedDate = today
                data.Action = "A"
                data.BranchID = 1
                data.AccountGroupUnder = account_group
                data.CrOrDr = CrOrDr
                data.CreatedUserID = 1
                data.LedgerID = get_auto_LedgerID(AccountLedger,data.BranchID)
                data.LedgerCode = get_LedgerCode(AccountLedger, data.BranchID)
                AccountLedger_Log.objects.create(
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

                    LedgerPosting.objects.create(
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
                        )

                    LedgerPosting_Log.objects.create(
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
                        )

                if account_group == "10" or account_group == "29":
                    PartyName = data.LedgerName
                    if account_group == "10":
                        PartyType = "customer"


                    elif account_group == "29":
                        PartyType = "supplier"

                    PartyID = get_auto_idfor_party(Parties,data.BranchID)
                    PartyCode = data.LedgerCode

                    Parties.objects.create(
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
                        OpeningBalance=data.OpeningBalance,
                        )

                    Parties_Log.objects.create(
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
                        OpeningBalance=data.OpeningBalance,
                        )
                data.save()

                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("AccountLedger Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('web:accountLedgers')
                }
            else:
                response_data = {
                    "status" : "false",
                    "title" : str(_("AccountLedger Already Exist")),
                    "message" : str(_("AccountLedger Name is Already exist with in the BranchID")),
                    "redirect" : "true",
                    "redirect_url" : reverse('web:create_accountLedger')
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
        accountGroups = AccountGroup.objects.all()
        context = {
            "title" : "create AccountLedger",
            "form" : form,
            "accountGroups" : accountGroups
        }
        return render(request,"entry_accountLedger.html",context)


def accountLedgers(request):
    instances = AccountLedger.objects.all()
    context = {
        'instances' : instances,
    }
    return render(request,"accountLedgers.html",context)


def edit_accountLedger(request,pk):
    today = datetime.date.today()
    instance = AccountLedger.objects.get(pk=pk)
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

            ledegrs = AccountLedger.objects.filter(BranchID=1)

            for ledger in ledegrs:
                ledger_name = ledger.LedgerName

                ledgerName = ledger_name.lower()

                if LedgerNameLow == ledgerName:
                    is_nameExist = True

                if instanceLedgerName.lower() == LedgerNameLow:
                    ledger_ok = True
            if ledger_ok:
                data.CreatedDate = today
                data.Action = "M"
                data.BranchID = 1
                data.AccountGroupUnder = account_group
                data.CrOrDr = CrOrDr
                data.CreatedUserID = 1
                AccountLedger_Log.objects.create(
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
                    Action="M",
                    CreatedUserID=1,
                    )

                if LedgerPosting.objects.filter(LedgerID=LedgerID,BranchID=data.BranchID,VoucherMasterID=LedgerID,VoucherType="LOB").exists():
                    ledgerPostInstance = LedgerPosting.objects.get(LedgerID=LedgerID,BranchID=data.BranchID,VoucherMasterID=LedgerID,VoucherType="LOB")
                    ledgerPostInstance.delete()

                if float(data.OpeningBalance) > 0:
                    Credit = 0.00
                    Debit = 0.00

                    if CrOrDr == "Cr":
                        Credit = data.OpeningBalance

                    elif CrOrDr == "Dr":
                        Debit = data.OpeningBalance

                    VoucherType = "LOB"

                    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,data.BranchID)

                    LedgerPosting.objects.create(
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
                        )

                    LedgerPosting_Log.objects.create(
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
                        )
                data.save()

                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("AccountLedger Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('web:accountLedgers')
                }
            else:
                if is_nameExist:
                    response_data = {
                        "status" : "false",
                        "title" : str(_("AccountLedger Already Exist")),
                        "message" : str(_("AccountLedger Name is Already exist with in the BranchID")),
                        "redirect" : "true",
                        "redirect_url" : reverse('web:create_brand')
                    }
                else:
                    data.CreatedDate = today
                    data.Action = "M"
                    data.BranchID = 1
                    data.AccountGroupUnder = account_group
                    data.CrOrDr = CrOrDr
                    data.CreatedUserID = 1
                    AccountLedger_Log.objects.create(
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
                        Action="M",
                        CreatedUserID=1,
                        )

                    if LedgerPosting.objects.filter(LedgerID=LedgerID,BranchID=data.BranchID,VoucherMasterID=LedgerID,VoucherType="LOB").exists():
                        ledgerPostInstance = LedgerPosting.objects.get(LedgerID=LedgerID,BranchID=data.BranchID,VoucherMasterID=LedgerID,VoucherType="LOB")
                        ledgerPostInstance.delete()

                    if float(data.OpeningBalance) > 0:
                        Credit = 0.00
                        Debit = 0.00

                        if CrOrDr == "Cr":
                            Credit = data.OpeningBalance

                        elif CrOrDr == "Dr":
                            Debit = data.OpeningBalance

                        VoucherType = "LOB"

                        LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,data.BranchID)

                        LedgerPosting.objects.create(
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
                            )

                        LedgerPosting_Log.objects.create(
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
                            )
                    data.save()

                    response_data = {
                        "status" : "true",
                        "title" : str(_("Successfully Updated")),
                        "message" : str(_("AccountLedger Updated Successfully!")),
                        "redirect" : "true",
                        "redirect_url" : reverse('web:accountLedgers')
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
        accountGroups = AccountGroup.objects.all()
        context = {
            "title" : "Edit Brand",
            "form" : form,
            "accountGroups" : accountGroups,
            "is_edit" : True,
            "instance" : instance
        }
        return render(request,"entry_accountLedger.html",context)


def delete_accountLedger(request,pk):
    today = datetime.date.today()
    instance = None
    ledgerPostInstance = None
    LPInstances = None
    purchaseOrderMaster_exist = None
    salesOrderMaster_exist = None
    parties_exist = None
    employees_exist = None
    if AccountLedger.objects.filter(pk=pk).exists():
        instance = AccountLedger.objects.get(pk=pk)

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
        
        LPInstances = LedgerPosting.objects.filter(BranchID=BranchID,LedgerID=LedgerID).exclude(VoucherType="LOB")
            
        purchaseOrderMaster_exist = PurchaseOrderMaster.objects.filter(BranchID=BranchID,LedgerID=LedgerID).exists()
        salesOrderMaster_exist = SalesOrderMaster.objects.filter(BranchID=BranchID,LedgerID=LedgerID).exists()
        parties_exist = Parties.objects.filter(BranchID=BranchID,LedgerID=LedgerID).exists()
        employees_exist = Employee.objects.filter(BranchID=BranchID,LedgerID=LedgerID).exists()


        if not employees_exist and not parties_exist and not salesOrderMaster_exist and not purchaseOrderMaster_exist and not LPInstances:
        # if not LPInstances:
            instance.delete()

            AccountLedger_Log.objects.create(
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
                Action=Action,
                )

            if LedgerPosting.objects.filter(LedgerID=LedgerID,BranchID=BranchID).exists():
                ledgerPostInstances = LedgerPosting.objects.filter(LedgerID=LedgerID,BranchID=BranchID)
                
                for ledgerPostInstance in ledgerPostInstances:
                    LedgerPostingID = ledgerPostInstance.LedgerPostingID
                    VoucherType = ledgerPostInstance.VoucherType
                    Debit = ledgerPostInstance.Debit
                    Credit = ledgerPostInstance.Credit
                    IsActive = ledgerPostInstance.IsActive
                    CreatedUserID = ledgerPostInstance.CreatedUserID

                    ledgerPostInstance.delete()

                    LedgerPosting_Log.objects.create(
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
                        )

            response_data = {
                "status" : "true",
                "title" : str(_("Successfully Deleted")),
                "message" : str(_("AccountLedger Deleted Successfully.")),
                "redirect" : "true",
                "redirect_url" : reverse('web:accountLedgers')
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


def create_bank(request):
    today = datetime.date.today()
    if request.method == 'POST':
        form = BankForm(request.POST)
        CrOrDr = request.POST.get('crOdr')
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
                data.Action = "A"
                data.BranchID = 1
                data.CreatedUserID = 1
                data.CrOrDr = CrOrDr
                data.LedgerName = LedgerName
                data.BankID = get_auto_Bankid(Bank,data.BranchID)
                data.LedgerCode = get_LedgerCode(AccountLedger, data.BranchID)
                LedgerID = get_auto_LedgerID(AccountLedger,data.BranchID)
                Bank_Log.objects.create(
                    BranchID=data.BranchID,
                    TransactionID=data.BankID,
                    LedgerCode=data.LedgerCode,
                    Name=data.Name,
                    LedgerName=LedgerName,
                    AccountNumber=data.AccountNumber,
                    CrOrDr=CrOrDr,
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
                    Action=data.Action,
                    )

                AccountLedger.objects.create(
                    LedgerID=LedgerID,
                    BranchID=data.BranchID,
                    LedgerName=data.Name,
                    LedgerCode=data.LedgerCode,
                    AccountGroupUnder=AccountGroupUnder,
                    OpeningBalance=data.OpeningBalance,
                    CrOrDr=CrOrDr,
                    CreatedDate=today,
                    Notes=data.Notes,
                    Action=data.Action,
                    CreatedUserID=data.CreatedUserID,
                    )

                AccountLedger_Log.objects.create(
                    TransactionID=LedgerID,
                    BranchID=data.BranchID,
                    LedgerName=data.Name,
                    LedgerCode=data.LedgerCode,
                    AccountGroupUnder=AccountGroupUnder,
                    OpeningBalance=data.OpeningBalance,
                    CrOrDr=CrOrDr,
                    CreatedDate=today,
                    Notes=data.Notes,
                    Action=data.Action,
                    CreatedUserID=data.CreatedUserID,
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

                    LedgerPosting.objects.create(
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
                        )

                    LedgerPosting_Log.objects.create(
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
                        )
                data.save()

                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("Bank Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('web:banks')
                }
            else:
                response_data = {
                    "status" : "false",
                    "title" : str(_("Bank Already Exist")),
                    "message" : str(_("Bank Name is Already exist with in the BranchID")),
                    "redirect" : "true",
                    "redirect_url" : reverse('web:create_bank')
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
            "title" : "create Brand",
            "form" : form,
            "accountGroups" : accountGroups
        }
        return render(request,"entry_bank.html",context)


def banks(request):
    instances = Bank.objects.all()
    context = {
        'instances' : instances,
    }
    return render(request,"banks.html",context)


def edit_bank(request,pk):
    today = datetime.date.today()
    instance = Bank.objects.get(pk=pk)
    instanceLedgerName = instance.LedgerName
    LedgerCode = instance.LedgerCode
    BankID = instance.BankID
    if request.method == 'POST':
        form = BankForm(request.POST,instance=instance)
        CrOrDr = request.POST.get('crOdr')
        if form.is_valid():
            data = form.save(commit=False)
            LedgerName = data.Name
            is_nameExist = False
            ledger_ok = False

            LedgerNameLow = LedgerName.lower()

            ledegrs = AccountLedger.objects.filter(BranchID=1)

            for ledger in ledegrs:
                ledger_name = ledger.LedgerName

                ledgerName = ledger_name.lower()

                if LedgerNameLow == ledgerName:
                    is_nameExist = True

                if instanceLedgerName.lower() == LedgerNameLow:
                    ledger_ok = True
            if ledger_ok:
                data.CreatedDate = today
                data.Action = "M"
                data.BranchID = 1
                data.CreatedUserID = 1
                data.CrOrDr = CrOrDr
                data.LedgerName = LedgerName
                Bank_Log.objects.create(
                    BranchID=data.BranchID,
                    TransactionID=BankID,
                    LedgerCode=LedgerCode,
                    Name=data.Name,
                    LedgerName=LedgerName,
                    AccountNumber=data.AccountNumber,
                    CrOrDr=CrOrDr,
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
                    Action=data.Action,
                    )

                AccountGroupUnder = 8

                if AccountLedger.objects.filter(LedgerName=instanceLedgerName,BranchID=data.BranchID).exists():
                    account_ledger = AccountLedger.objects.get(LedgerName=instanceLedgerName,BranchID=data.BranchID)
                    LedgerID = account_ledger.LedgerID
                    account_ledger.LedgerName = data.Name
                    account_ledger.OpeningBalance = data.OpeningBalance
                    account_ledger.CrOrDr = CrOrDr
                    account_ledger.CreatedDate = today
                    account_ledger.Notes = data.Notes
                    account_ledger.Action = data.Action
                    account_ledger.save()

                    AccountLedger_Log.objects.create(
                        BranchID=data.BranchID,
                        TransactionID=LedgerID,
                        LedgerName=data.Name,
                        LedgerCode=LedgerCode,
                        AccountGroupUnder=AccountGroupUnder,
                        OpeningBalance=data.OpeningBalance,
                        CrOrDr=CrOrDr,
                        CreatedDate=today,
                        Notes=data.Notes,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        )
                if LedgerPosting.objects.filter(LedgerID=LedgerID,BranchID=data.BranchID,VoucherMasterID=LedgerID,VoucherType="LOB").exists():
                    ledgerPostInstance = LedgerPosting.objects.get(LedgerID=LedgerID,BranchID=data.BranchID,VoucherMasterID=LedgerID,VoucherType="LOB")
                    ledgerPostInstance.delete()

                if float(data.OpeningBalance) > 0:
                    Credit = 0.00
                    Debit = 0.00

                    if CrOrDr == "Cr":
                        Credit = data.OpeningBalance

                    elif CrOrDr == "Dr":
                        Debit = data.OpeningBalance

                    VoucherType = "LOB"

                    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,data.BranchID)

                    LedgerPosting.objects.create(
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
                        )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=data.BranchID,
                        Date=today,
                        VoucherMasterID=LedgerID,
                        VoucherType=VoucherType,
                        LedgerID=data.LedgerID,
                        Debit=Debit,
                        Credit=Credit,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        CreatedDate=today,
                        )
                data.save()

                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("AccountLedger Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('web:accountLedgers')
                }
            else:
                if is_nameExist:
                    response_data = {
                        "status" : "false",
                        "title" : str(_("AccountLedger Already Exist")),
                        "message" : str(_("AccountLedger Name is Already exist with in the BranchID")),
                        "redirect" : "true",
                        "redirect_url" : reverse('web:create_brand')
                    }
                else:
                    data.CreatedDate = today
                    data.Action = "M"
                    data.BranchID = 1
                    data.CreatedUserID = 1
                    data.CrOrDr = CrOrDr
                    data.LedgerName = LedgerName
                    Bank_Log.objects.create(
                        BranchID=data.BranchID,
                        TransactionID=BankID,
                        LedgerCode=LedgerCode,
                        Name=data.Name,
                        LedgerName=LedgerName,
                        AccountNumber=data.AccountNumber,
                        CrOrDr=CrOrDr,
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
                        Action=data.Action,
                        )

                    AccountGroupUnder = 8

                    if AccountLedger.objects.filter(LedgerName=instanceLedgerName,BranchID=data.BranchID).exists():
                        account_ledger = AccountLedger.objects.get(LedgerName=instanceLedgerName,BranchID=data.BranchID)
                        LedgerID = account_ledger.LedgerID
                        account_ledger.LedgerName = data.Name
                        account_ledger.OpeningBalance = data.OpeningBalance
                        account_ledger.CrOrDr = CrOrDr
                        account_ledger.CreatedDate = today
                        account_ledger.Notes = data.Notes
                        account_ledger.Action = data.Action
                        account_ledger.save()

                        AccountLedger_Log.objects.create(
                            BranchID=data.BranchID,
                            TransactionID=LedgerID,
                            LedgerName=data.Name,
                            LedgerCode=LedgerCode,
                            AccountGroupUnder=AccountGroupUnder,
                            OpeningBalance=data.OpeningBalance,
                            CrOrDr=CrOrDr,
                            CreatedDate=today,
                            Notes=data.Notes,
                            Action=data.Action,
                            CreatedUserID=data.CreatedUserID,
                            )
                    
                    if LedgerPosting.objects.filter(LedgerID=LedgerID,BranchID=data.BranchID,VoucherMasterID=LedgerID,VoucherType="LOB").exists():
                        ledgerPostInstance = LedgerPosting.objects.get(LedgerID=LedgerID,BranchID=data.BranchID,VoucherMasterID=LedgerID,VoucherType="LOB")
                        ledgerPostInstance.delete()

                    if float(data.OpeningBalance) > 0:
                        Credit = 0.00
                        Debit = 0.00

                        if CrOrDr == "Cr":
                            Credit = data.OpeningBalance

                        elif CrOrDr == "Dr":
                            Debit = data.OpeningBalance

                        VoucherType = "LOB"

                        LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,data.BranchID)

                        LedgerPosting.objects.create(
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
                            )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=data.BranchID,
                            Date=today,
                            VoucherMasterID=LedgerID,
                            VoucherType=VoucherType,
                            LedgerID=data.LedgerID,
                            Debit=Debit,
                            Credit=Credit,
                            Action=data.Action,
                            CreatedUserID=data.CreatedUserID,
                            CreatedDate=today,
                            )
                    data.save()

                    response_data = {
                        "status" : "true",
                        "title" : str(_("Successfully Updated")),
                        "message" : str(_("Bank Updated Successfully!")),
                        "redirect" : "true",
                        "redirect_url" : reverse('web:banks')
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
        accountGroups = AccountGroup.objects.all()
        context = {
            "title" : "Edit Brand",
            "form" : form,
            "accountGroups" : accountGroups,
            "is_edit" : True,
            "instance" : instance
        }
        return render(request,"entry_bank.html",context)
