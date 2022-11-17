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
from brands.models import Designation, Designation_Log, Employee, Employee_Log, AccountLedger, Country, AccountLedger_Log, LedgerPosting, Department, Department_Log
from users.models import CustomerUser, DatabaseStore
from payrolls.forms import DesignationForm, EmployeeForm, DepartmentForm
from api.v1.accountLedgers.functions import get_LedgerCode
from accounts.functions import generate_form_errors, get_auto_LedgerID
from api.v1.designation.functions import get_auto_id
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
import datetime


@login_required
def create_designation(request):
    user = request.user
    customer_instance = get_object_or_404(CustomerUser.objects.filter(user=user))
    db_id = customer_instance.databaseid
    datastore = get_object_or_404(DatabaseStore.objects.filter(id=db_id))
    DataBase = datastore.DefaultDatabase


    today = datetime.date.today()
    if request.method == 'POST':
        form = DesignationForm(request.POST)
        if form.is_valid(): 
            data = form.save(commit=False)
            DesignationName = data.DesignationName

            is_nameExist = False
            DesignationNameLow = DesignationName.lower()
            designations = Designation.objects.using(DataBase).filter(BranchID=1)

            for designation in designations:
                designation_name = designation.DesignationName
                designationName = designation_name.lower()

                if DesignationNameLow == designationName:
                    is_nameExist = True

            if not is_nameExist:
                data.CreatedDate = today
                data.UpdatedDate = today
                data.Action = "A"
                data.BranchID = 1
                data.CreatedUserID = 1
                data.DesignationID = get_auto_id(Designation,data.BranchID, DataBase)
                Designation_Log.objects.using(DataBase).create(
                    BranchID=data.BranchID,
                    TransactionID=data.DesignationID,
                    DesignationName=data.DesignationName,
                    Notes=data.Notes,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=data.Action,
                    CreatedUserID=data.CreatedUserID,
                    )
                data.save(using=DataBase)

                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("Designation Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('payrolls:designations')
                }
            else:
                response_data = {
                    "status" : "false",
                    "title" : str(_("Designation Already Exist")),
                    "message" : str(_("Designation Name is Already exist with in the BranchID")),
                    "redirect" : "true",
                    "redirect_url" : reverse('payrolls:create_designation')
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
        form = DesignationForm()
        context = {
            "is_need_flatpickr" : False,
            "is_need_apexcharts" : False,
            "is_need_selectize" : False,
            "is_need_dashboard" : False,

            "title" : "Create Designation",
            "form" : form
        }
        return render(request,"payrolls/masters/create_designation.html",context)


@login_required
def view_designation(request,pk):
    user = request.user
    customer_instance = get_object_or_404(CustomerUser.objects.filter(user=user))
    db_id = customer_instance.databaseid
    datastore = get_object_or_404(DatabaseStore.objects.filter(id=db_id))
    DataBase = datastore.DefaultDatabase
    instance = Designation.objects.using(DataBase).get(pk=pk)
    context = {
        "is_need_flatpickr" : False,
        "is_need_apexcharts" : False,
        "is_need_selectize" : False,
        "is_need_dashboard" : False,

        'instance' : instance,
        'title' : 'Designation'
    }
    return render(request,"payrolls/masters/designation.html",context)


@login_required
def designations(request):
    user = request.user
    customer_instance = get_object_or_404(CustomerUser.objects.filter(user=user))
    db_id = customer_instance.databaseid
    datastore = get_object_or_404(DatabaseStore.objects.filter(id=db_id))
    DataBase = datastore.DefaultDatabase
    instances = Designation.objects.using(DataBase).all()
    context = {
        "is_need_flatpickr" : False,
        "is_need_apexcharts" : False,
        "is_need_selectize" : False,
        "is_need_dashboard" : False,

        'instances' : instances,
        'title' : 'Designations'
    }
    return render(request,"payrolls/masters/designations.html",context)


@login_required
def edit_designation(request,pk):
    user = request.user
    customer_instance = get_object_or_404(CustomerUser.objects.filter(user=user))
    db_id = customer_instance.databaseid
    datastore = get_object_or_404(DatabaseStore.objects.filter(id=db_id))
    DataBase = datastore.DefaultDatabase


    today = datetime.date.today()
    instance = Designation.objects.using(DataBase).get(pk=pk)
    instanceDesignationName = instance.DesignationName
    DesignationID = instance.DesignationID
    if request.method == 'POST':
        form = DesignationForm(request.POST,instance=instance)
        if form.is_valid(): 
            data = form.save(commit=False)
            DesignationName = data.DesignationName
            is_nameExist = False
            designaion_ok = False

            DesignationNameLow = DesignationName.lower()

            designations = Designation.objects.using(DataBase).filter(BranchID=1)

            for designation in designations:
                designation_name = designation.DesignationName

                designationName = designation_name.lower()

                if DesignationNameLow == designationName:
                    is_nameExist = True

                if instanceDesignationName.lower() == DesignationNameLow:
                    designaion_ok = True
            if designaion_ok:
                data.CreatedDate = today
                data.UpdatedDate = today
                data.Action = "M"
                data.BranchID = 1
                data.CreatedUserID = 1
                Designation_Log.objects.using(DataBase).create(
                    BranchID=data.BranchID,
                    TransactionID=DesignationID,
                    DesignationName=data.DesignationName,
                    Notes=data.Notes,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=data.Action,
                    CreatedUserID=data.CreatedUserID,
                    )
                data.save(using=DataBase)

                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Updated")),
                    "message" : str(_("Designation Updated Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('payrolls:view_designation',kwargs={'pk':instance.pk})
                }
            else:
                if is_nameExist:
                    response_data = {
                        "status" : "false",
                        "title" : str(_("Designation Already Exist")),
                        "message" : str(_("Designation Name is Already exist with in the BranchID")),
                        "redirect" : "true",
                        "redirect_url" : reverse('payrolls:edit_designation',kwargs={'pk':instance.pk})
                    }
                else:
                    data.CreatedDate = today
                    data.UpdatedDate = today
                    data.Action = "M"
                    data.BranchID = 1
                    data.CreatedUserID = 1
                    Designation_Log.objects.using(DataBase).create(
                        BranchID=data.BranchID,
                        TransactionID=DesignationID,
                        DesignationName=data.DesignationName,
                        Notes=data.Notes,
                        CreatedDate=today,
                        UpdatedDate=today,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        )
                    data.save(using=DataBase)

                    response_data = {
                        "status" : "true",
                        "title" : str(_("Successfully Updated")),
                        "message" : str(_("Designation Updated Successfully!")),
                        "redirect" : "true",
                        "redirect_url" : reverse('payrolls:view_designation',kwargs={'pk':instance.pk})
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
        form = DesignationForm(instance=instance)
        context = {
            "is_need_flatpickr" : False,
            "is_need_apexcharts" : False,
            "is_need_selectize" : False,
            "is_need_dashboard" : False,

            "title" : "Edit Designation",
            "form" : form
        }
        return render(request,"payrolls/masters/create_designation.html",context)


@login_required
def delete_designation(request,pk):
    user = request.user
    customer_instance = get_object_or_404(CustomerUser.objects.filter(user=user))
    db_id = customer_instance.databaseid
    datastore = get_object_or_404(DatabaseStore.objects.filter(id=db_id))
    DataBase = datastore.DefaultDatabase


    today = datetime.date.today()    
    instance = Designation.objects.using(DataBase).get(pk=pk)
    if pk == "1":
        response_data = {
            'status' : 'false',
            'stable' : 'true',
            'title' : str(_("can't delete this Designation")),
            "message" : str(_("Can't delete this Designation! this is default Designation!"))
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        Designation_Log.objects.using(DataBase).create(
            BranchID=instance.BranchID,
            TransactionID=instance.DesignationID,
            DesignationName=instance.DesignationName,
            Notes=instance.Notes,
            CreatedDate=today,
            UpdatedDate=today,
            Action='D',
            CreatedUserID=instance.CreatedUserID,
            )
        instance.delete()
        
        response_data = {
            "status" : "true",
            "title" : str(_("Successfully Deleted")),
            "message" : str(_("Designation Deleted Successfully.")),
            "redirect" : "true",
            "redirect_url" : reverse('payrolls:designations')
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')


@login_required
def create_employee(request):
    from api.v1.employees.functions import get_auto_id
    from api.v1.accountLedgers.functions import get_LedgerCode
    from web.functions import get_auto_LedgerID


    user = request.user
    customer_instance = get_object_or_404(CustomerUser.objects.filter(user=user))
    db_id = customer_instance.databaseid
    datastore = get_object_or_404(DatabaseStore.objects.filter(id=db_id))
    DataBase = datastore.DefaultDatabase

    today = datetime.date.today()
    if request.method == 'POST':

        form = EmployeeForm(request.POST)
        if form.is_valid(): 
            # CompanyName = form.cleaned_data['CompanyName']
            BranchID = 2
            Action = 'A'
            EmployeeID = get_auto_id(Employee,BranchID,DataBase)
            LedgerCode = get_LedgerCode(AccountLedger, BranchID,DataBase)
            LedgerID = get_auto_LedgerID(AccountLedger,BranchID,DataBase)
            CreatedUserID = 1
            data = form.save(commit=False)
            data.EmployeeCode = get_LedgerCode(AccountLedger, BranchID,DataBase)
            data.EmployeeID = EmployeeID
            data.BranchID = BranchID
            data.LedgerID = LedgerID
            data.CreatedDate = today
            data.UpdatedDate = today
            data.CreatedUserID = request.user.id
            data.Action = Action

            FirstName = data.FirstName
            LastName = data.LastName
            DesignationID = data.DesignationID
            DepartmentID = data.DepartmentID
            DateOfBirth = data.DateOfBirth
            Gender = data.Gender
            BloodGroup = data.BloodGroup
            Nationality = data.Nationality
            State = data.State
            Address1 = data.Address1
            Address2 = data.Address2
            Address3 = data.Address3
            Post = data.Post
            Phone = data.Phone
            Mobile = data.Mobile
            Email = data.Email
            PassportNo = data.PassportNo
            PassportExpiryDate = data.PassportExpiryDate
            VisaDetails = data.VisaDetails
            VisaExpiryDate = data.VisaExpiryDate
            ProbationPeriod = data.ProbationPeriod
            periodType = data.periodType
            DateOfJoining = data.DateOfJoining
            Salary = data.Salary
            AccountHolderName = data.AccountHolderName
            AccountName = data.AccountName
            AccountBranch = data.AccountBranch
            AccountIFSC = data.AccountIFSC
            NoCasualLeave = data.NoCasualLeave
            Notes = data.Notes
            Qualification = data.Qualification
            EmergencyContactNumber = data.EmergencyContactNumber
            EmergencyEmail = data.EmergencyEmail
            EmergencyAddress = data.EmergencyAddress
            LedgerName = data.FirstName

            is_nameExist = False
            LedgerNameLow = LedgerName.lower()
            if AccountLedger.objects.using(DataBase).filter(BranchID=BranchID).exists():
                account_ledgers = AccountLedger.objects.using(DataBase).filter(BranchID=BranchID)
                for account_ledger in account_ledgers:
                    ledger_name = account_ledger.LedgerName
                    ledgerName = ledger_name.lower()
                    if LedgerNameLow == ledgerName:
                        is_nameExist = True

            if not is_nameExist:
                data.save(using=DataBase)

                Employee_Log.objects.using(DataBase).create(
                    TransactionID = EmployeeID,
                    FirstName = FirstName,
                    LastName = LastName,
                    DesignationID = DesignationID,
                    DepartmentID = DepartmentID,
                    DateOfBirth = DateOfBirth,
                    Gender = Gender,
                    BloodGroup = BloodGroup,
                    Nationality = Nationality,
                    State = State,
                    Address1 = Address1,
                    Address2 = Address2,
                    Address3 = Address3,
                    Post = Post,
                    Phone = Phone,
                    Mobile = Mobile,
                    Email = Email,
                    PassportNo = PassportNo,
                    PassportExpiryDate = PassportExpiryDate,
                    VisaDetails = VisaDetails,
                    VisaExpiryDate = VisaExpiryDate,
                    ProbationPeriod = ProbationPeriod,
                    periodType = periodType,
                    DateOfJoining = DateOfJoining,
                    Salary = Salary,
                    AccountHolderName = AccountHolderName,
                    AccountName = AccountName,
                    AccountBranch = AccountBranch,
                    AccountIFSC = AccountIFSC,
                    NoCasualLeave = NoCasualLeave,
                    Notes = Notes,
                    Qualification = Qualification,
                    EmergencyContactNumber = EmergencyContactNumber,
                    EmergencyEmail = EmergencyEmail,
                    EmergencyAddress = EmergencyAddress,
                    EmployeeCode = LedgerCode,
                    BranchID = 1,
                    LedgerID = LedgerID,
                    CreatedDate = today,
                    UpdatedDate = today,
                    CreatedUserID = CreatedUserID,
                    Action = Action,
                    )

                AccountLedger.objects.using(DataBase).create(
                    LedgerID=LedgerID,
                    BranchID=BranchID,
                    LedgerName=LedgerName,
                    LedgerCode=LedgerCode,
                    AccountGroupUnder=32,
                    OpeningBalance=0,
                    CrOrDr="Dr",
                    Notes=Notes,
                    IsActive=True,
                    IsDefault=False,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    )

                AccountLedger_Log.objects.using(DataBase).create(
                    BranchID=BranchID,
                    TransactionID=LedgerID,
                    LedgerName=LedgerName,
                    LedgerCode=LedgerCode,
                    AccountGroupUnder=32,
                    OpeningBalance=0,
                    CrOrDr="Dr",
                    Notes=Notes,
                    IsActive=True,
                    IsDefault=False,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    )

                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("Employee Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('payrolls:employees')
                }
            else:
                response_data = {
                    "status" : "false",
                    "title" : str(_("Designation Already Exist")),
                    "message" : str(_("Designation Name is Already exist with in the BranchID")),
                    "redirect" : "true",
                    "redirect_url" : reverse('payrolls:create_employee')
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
        form = EmployeeForm()
        countries = Country.objects.all()
        designations = Designation.objects.all()
        context = {
            "is_need_flatpickr" : False,
            "is_need_apexcharts" : False,
            "is_need_selectize" : False,
            "is_need_dashboard" : False,
            "is_need_bootstrap_wizard" : True,
            "is_need_form_wizard" : True,

            "title" : "Create Employee",
            "form" : form,
            "countries" : countries,
            "designations" : designations,
        }
        return render(request,"payrolls/masters/create_employee.html",context)


@login_required
def view_employee(request,pk):
    user = request.user
    customer_instance = get_object_or_404(CustomerUser.objects.filter(user=user))
    db_id = customer_instance.databaseid
    datastore = get_object_or_404(DatabaseStore.objects.filter(id=db_id))
    DataBase = datastore.DefaultDatabase

    instance = Employee.objects.using(DataBase).get(pk=pk)
    context = {
        "is_need_flatpickr" : False,
        "is_need_apexcharts" : False,
        "is_need_selectize" : False,
        "is_need_dashboard" : False,

        'instance' : instance,
        'title' : 'Employee'
    }
    return render(request,"payrolls/masters/employee.html",context)


@login_required
def employees(request):
    user = request.user
    customer_instance = get_object_or_404(CustomerUser.objects.filter(user=user))
    db_id = customer_instance.databaseid
    datastore = get_object_or_404(DatabaseStore.objects.filter(id=db_id))
    DataBase = datastore.DefaultDatabase
    instances = Employee.objects.using(DataBase).all()
    context = {
        "is_need_flatpickr" : False,
        "is_need_apexcharts" : False,
        "is_need_selectize" : False,
        "is_need_dashboard" : False,

        'instances' : instances,
        'title' : 'Employees'
    }
    return render(request,"payrolls/masters/employees.html",context)


@login_required
def edit_employee(request,pk):
    from api.v1.employees.functions import get_auto_id
    from api.v1.accountLedgers.functions import get_LedgerCode
    from web.functions import get_auto_LedgerID


    user = request.user
    customer_instance = get_object_or_404(CustomerUser.objects.filter(user=user))
    db_id = customer_instance.databaseid
    datastore = get_object_or_404(DatabaseStore.objects.filter(id=db_id))
    DataBase = datastore.DefaultDatabase
    instance = Employee.objects.using(DataBase).get(pk=pk)

    today = datetime.date.today()
    if request.method == 'POST':

        form = EmployeeForm(request.POST)
        if form.is_valid(): 
            # CompanyName = form.cleaned_data['CompanyName']
            BranchID = 2
            Action = 'M'
            EmployeeID = get_auto_id(Employee,BranchID,DataBase)
            LedgerCode = get_LedgerCode(AccountLedger, BranchID,DataBase)
            LedgerID = get_auto_LedgerID(AccountLedger,BranchID,DataBase)
            CreatedUserID = 1
            data = form.save(commit=False)
            data.EmployeeCode = get_LedgerCode(AccountLedger, BranchID,DataBase)
            data.EmployeeID = EmployeeID
            data.BranchID = BranchID
            data.LedgerID = LedgerID
            data.CreatedDate = today
            data.UpdatedDate = today
            data.CreatedUserID = request.user.id
            data.Action = Action

            FirstName = data.FirstName
            LastName = data.LastName
            DesignationID = data.DesignationID
            DepartmentID = data.DepartmentID
            DateOfBirth = data.DateOfBirth
            Gender = data.Gender
            BloodGroup = data.BloodGroup
            Nationality = data.Nationality
            State = data.State
            Address1 = data.Address1
            Address2 = data.Address2
            Address3 = data.Address3
            Post = data.Post
            Phone = data.Phone
            Mobile = data.Mobile
            Email = data.Email
            PassportNo = data.PassportNo
            PassportExpiryDate = data.PassportExpiryDate
            VisaDetails = data.VisaDetails
            VisaExpiryDate = data.VisaExpiryDate
            ProbationPeriod = data.ProbationPeriod
            periodType = data.periodType
            DateOfJoining = data.DateOfJoining
            Salary = data.Salary
            AccountHolderName = data.AccountHolderName
            AccountName = data.AccountName
            AccountBranch = data.AccountBranch
            AccountIFSC = data.AccountIFSC
            NoCasualLeave = data.NoCasualLeave
            Notes = data.Notes
            Qualification = data.Qualification
            EmergencyContactNumber = data.EmergencyContactNumber
            EmergencyEmail = data.EmergencyEmail
            EmergencyAddress = data.EmergencyAddress
            LedgerName = data.FirstName

            is_nameExist = False
            employee_ok = False

            LedgerNameLow = LedgerName.lower()

            account_ledgers = AccountLedger.objects.using(DataBase).filter(BranchID=BranchID)

            for account_ledger in account_ledgers:

                ledger_name = account_ledger.LedgerName
                ledgerName = ledger_name.lower()

                if LedgerNameLow == ledgerName:
                    is_nameExist = True

                if instanceLedgerName.lower() == LedgerNameLow:

                    employee_ok = True

            if  employee_ok:

                Employee_Log.objects.using(DataBase).create(
                    TransactionID = EmployeeID,
                    FirstName = FirstName,
                    LastName = LastName,
                    DesignationID = DesignationID,
                    DepartmentID = DepartmentID,
                    DateOfBirth = DateOfBirth,
                    Gender = Gender,
                    BloodGroup = BloodGroup,
                    Nationality = Nationality,
                    State = State,
                    Address1 = Address1,
                    Address2 = Address2,
                    Address3 = Address3,
                    Post = Post,
                    Phone = Phone,
                    Mobile = Mobile,
                    Email = Email,
                    PassportNo = PassportNo,
                    PassportExpiryDate = PassportExpiryDate,
                    VisaDetails = VisaDetails,
                    VisaExpiryDate = VisaExpiryDate,
                    ProbationPeriod = ProbationPeriod,
                    periodType = periodType,
                    DateOfJoining = DateOfJoining,
                    Salary = Salary,
                    AccountHolderName = AccountHolderName,
                    AccountName = AccountName,
                    AccountBranch = AccountBranch,
                    AccountIFSC = AccountIFSC,
                    NoCasualLeave = NoCasualLeave,
                    Notes = Notes,
                    Qualification = Qualification,
                    EmergencyContactNumber = EmergencyContactNumber,
                    EmergencyEmail = EmergencyEmail,
                    EmergencyAddress = EmergencyAddress,
                    EmployeeCode = LedgerCode,
                    BranchID = 1,
                    LedgerID = LedgerID,
                    CreatedDate = today,
                    UpdatedDate = today,
                    CreatedUserID = CreatedUserID,
                    Action = Action,
                    )
                data.save(using=DataBase)

                if AccountLedger.objects.using(DataBase).filter(BranchID=BranchID,LedgerID=LedgerID).exists():
                    accountLedgerInstance = AccountLedger.objects.using(DataBase).get(BranchID=BranchID,LedgerID=LedgerID)
                    accountLedgerInstance.LedgerName = LedgerName
                    accountLedgerInstance.Notes = Notes
                    accountLedgerInstance.UpdatedDate = today
                    accountLedgerInstance.CreatedUserID = CreatedUserID
                    accountLedgerInstance.Action = "M"
                    accountLedgerInstance.save()

                AccountLedger_Log.objects.using(DataBase).create(
                    BranchID=BranchID,
                    TransactionID=LedgerID,
                    LedgerName=LedgerName,
                    LedgerCode=accountLedgerInstance.LedgerCode,
                    AccountGroupUnder=accountLedgerInstance.AccountGroupUnder,
                    OpeningBalance=accountLedgerInstance.OpeningBalance,
                    CrOrDr=accountLedgerInstance.CrOrDr,
                    Notes=Notes,
                    IsActive=accountLedgerInstance.IsActive,
                    IsDefault=accountLedgerInstance.IsDefault,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action="M",
                    CreatedUserID=CreatedUserID,
                    )

                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("Employee Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('payrolls:employees')
                }
            else:
                if is_nameExist:

                    response_data = {
                        "status" : "false",
                        "title" : str(_("Employee Already Exist")),
                        "message" : str(_("Employee Name Already exist with this Branch ID")),
                        "redirect" : "true",
                        "redirect_url" : reverse('payrolls:create_employee')
                    }
                else:

                    Employee_Log.objects.using(DataBase).create(
                        TransactionID = EmployeeID,
                        FirstName = FirstName,
                        LastName = LastName,
                        DesignationID = DesignationID,
                        DepartmentID = DepartmentID,
                        DateOfBirth = DateOfBirth,
                        Gender = Gender,
                        BloodGroup = BloodGroup,
                        Nationality = Nationality,
                        State = State,
                        Address1 = Address1,
                        Address2 = Address2,
                        Address3 = Address3,
                        Post = Post,
                        Phone = Phone,
                        Mobile = Mobile,
                        Email = Email,
                        PassportNo = PassportNo,
                        PassportExpiryDate = PassportExpiryDate,
                        VisaDetails = VisaDetails,
                        VisaExpiryDate = VisaExpiryDate,
                        ProbationPeriod = ProbationPeriod,
                        periodType = periodType,
                        DateOfJoining = DateOfJoining,
                        Salary = Salary,
                        AccountHolderName = AccountHolderName,
                        AccountName = AccountName,
                        AccountBranch = AccountBranch,
                        AccountIFSC = AccountIFSC,
                        NoCasualLeave = NoCasualLeave,
                        Notes = Notes,
                        Qualification = Qualification,
                        EmergencyContactNumber = EmergencyContactNumber,
                        EmergencyEmail = EmergencyEmail,
                        EmergencyAddress = EmergencyAddress,
                        EmployeeCode = LedgerCode,
                        BranchID = 1,
                        LedgerID = LedgerID,
                        CreatedDate = today,
                        UpdatedDate = today,
                        CreatedUserID = CreatedUserID,
                        Action = Action,
                    )

                    data.save(using=DataBase)
                    if AccountLedger.objects.using(DataBase).filter(BranchID=BranchID,LedgerID=LedgerID).exists():
                        accountLedgerInstance = AccountLedger.objects.using(DataBase).get(BranchID=BranchID,LedgerID=LedgerID)
                        accountLedgerInstance.LedgerName = LedgerName
                        accountLedgerInstance.Notes = Notes
                        accountLedgerInstance.UpdatedDate = today
                        accountLedgerInstance.CreatedUserID = CreatedUserID
                        accountLedgerInstance.Action = "M"
                        accountLedgerInstance.save()

                        AccountLedger_Log.objects.using(DataBase).create(
                            BranchID=BranchID,
                            TransactionID=LedgerID,
                            LedgerName=LedgerName,
                            LedgerCode=accountLedgerInstance.LedgerCode,
                            AccountGroupUnder=accountLedgerInstance.AccountGroupUnder,
                            OpeningBalance=accountLedgerInstance.OpeningBalance,
                            CrOrDr=accountLedgerInstance.CrOrDr,
                            Notes=Notes,
                            IsActive=accountLedgerInstance.IsActive,
                            IsDefault=accountLedgerInstance.IsDefault,
                            CreatedDate=today,
                            UpdatedDate=today,
                            Action="M",
                            CreatedUserID=CreatedUserID,
                            )
                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("Employee Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('payrolls:employees')
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
        form = EmployeeForm(instance=instance)
        countries = Country.objects.all()
        designations = Designation.objects.all()
        context = {
            "is_need_flatpickr" : False,
            "is_need_apexcharts" : False,
            "is_need_selectize" : False,
            "is_need_dashboard" : False,
            "is_need_bootstrap_wizard" : True,
            "is_need_form_wizard" : True,

            "title" : "Create Employee",
            "form" : form,
            "countries" : countries,
            "designations" : designations,
        }
        return render(request,"payrolls/masters/create_employee.html",context)


@login_required
def delete_employee(request,pk):
    user = request.user
    customer_instance = get_object_or_404(CustomerUser.objects.filter(user=user))
    db_id = customer_instance.databaseid
    datastore = get_object_or_404(DatabaseStore.objects.filter(id=db_id))
    DataBase = datastore.DefaultDatabase

    today = datetime.date.today()
    instance = None
    if Employee.objects.using(DataBase).filter(pk=pk).exists():
        instance = Employee.objects.using(DataBase).get(pk=pk)
        FirstName = instance.FirstName
        LastName = instance.LastName
        DesignationID = instance.DesignationID
        DepartmentID = instance.DepartmentID
        DateOfBirth = instance.DateOfBirth
        Gender = instance.Gender
        BloodGroup = instance.BloodGroup
        Country = instance.Country
        Nationality = instance.Nationality
        State = instance.State
        Address1 = instance.Address1
        Address2 = instance.Address2
        Address3 = instance.Address3
        Post = instance.Post
        Phone = instance.Phone
        Mobile = instance.Mobile
        Email = instance.Email
        PassportNo = instance.PassportNo
        PassportExpiryDate = instance.PassportExpiryDate
        VisaDetails = instance.VisaDetails
        VisaExpiryDate = instance.VisaExpiryDate
        ProbationPeriod = instance.ProbationPeriod
        periodType = instance.periodType
        DateOfJoining = instance.DateOfJoining
        Salary = instance.Salary
        AccountHolderName = instance.AccountHolderName
        AccountName = instance.AccountName
        AccountBranch = instance.AccountBranch
        AccountIFSC = instance.AccountIFSC
        NoCasualLeave = instance.NoCasualLeave
        Notes = instance.Notes
        Qualification = instance.Qualification
        EmergencyContactNumber = instance.EmergencyContactNumber
        EmergencyEmail = instance.EmergencyEmail
        EmergencyAddress = instance.EmergencyAddress
        EmployeeCode = instance.EmployeeCode
        EmployeeID = instance.EmployeeID
        BranchID = instance.BranchID
        LedgerID = instance.LedgerID
        CreatedDate = instance.CreatedDate
        UpdatedDate = instance.UpdatedDate
        CreatedUserID = instance.CreatedUserID
        Action = instance.Action

        instance.delete()
    
        Employee_Log.objects.using(DataBase).create(
            TransactionID = EmployeeID,
            FirstName = FirstName,
            LastName = LastName,
            DesignationID = DesignationID,
            DepartmentID = DepartmentID,
            DateOfBirth = DateOfBirth,
            Gender = Gender,
            BloodGroup = BloodGroup,
            Nationality = Nationality,
            State = State,
            Address1 = Address1,
            Address2 = Address2,
            Address3 = Address3,
            Post = Post,
            Phone = Phone,
            Mobile = Mobile,
            Email = Email,
            PassportNo = PassportNo,
            PassportExpiryDate = PassportExpiryDate,
            VisaDetails = VisaDetails,
            VisaExpiryDate = VisaExpiryDate,
            ProbationPeriod = ProbationPeriod,
            periodType = periodType,
            DateOfJoining = DateOfJoining,
            Salary = Salary,
            AccountHolderName = AccountHolderName,
            AccountName = AccountName,
            AccountBranch = AccountBranch,
            AccountIFSC = AccountIFSC,
            NoCasualLeave = NoCasualLeave,
            Notes = Notes,
            Qualification = Qualification,
            EmergencyContactNumber = EmergencyContactNumber,
            EmergencyEmail = EmergencyEmail,
            EmergencyAddress = EmergencyAddress,
            EmployeeCode = EmployeeCode,
            BranchID = 1,
            LedgerID = LedgerID,
            CreatedDate = today,
            UpdatedDate = today,
            CreatedUserID = CreatedUserID,
            Action = 'D',
        )
        if not LedgerPosting.objects.using(DataBase).filter(BranchID=BranchID,LedgerID=LedgerID).exists():

            if AccountLedger.objects.using(DataBase).filter(BranchID=BranchID,LedgerID=LedgerID).exists():
                accountLedgerInstance = AccountLedger.objects.using(DataBase).get(BranchID=BranchID,LedgerID=LedgerID)
                
                accountLedgerInstance.delete()

                AccountLedger_Log.objects.using(DataBase).create(
                    BranchID=BranchID,
                    TransactionID=LedgerID,
                    LedgerName=accountLedgerInstance.LedgerName,
                    LedgerCode=accountLedgerInstance.LedgerCode,
                    AccountGroupUnder=accountLedgerInstance.AccountGroupUnder,
                    OpeningBalance=accountLedgerInstance.OpeningBalance,
                    CrOrDr=accountLedgerInstance.CrOrDr,
                    Notes=accountLedgerInstance.Notes,
                    IsActive=accountLedgerInstance.IsActive,
                    IsDefault=accountLedgerInstance.IsDefault,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action="D",
                    CreatedUserID=CreatedUserID,
                    )
    
    response_data = {
        "status" : "true",
        "title" : str(_("Successfully Deleted")),
        "message" : str(_("Employee Deleted Successfully.")),
        "redirect" : "true",
        "redirect_url" : reverse('payrolls:employees')
    }
    return HttpResponse(json.dumps(response_data), content_type='application/javascript')


@login_required
def create_department(request):
    from payrolls.functions import get_auto_id_department
    user = request.user
    customer_instance = get_object_or_404(CustomerUser.objects.filter(user=user))
    db_id = customer_instance.databaseid
    datastore = get_object_or_404(DatabaseStore.objects.filter(id=db_id))
    DataBase = datastore.DefaultDatabase


    today = datetime.date.today()
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid(): 
            data = form.save(commit=False)
            DepartmentName = data.DepartmentName

            is_nameExist = False
            DepartmentNameLow = DepartmentName.lower()
            departments = Department.objects.using(DataBase).filter(BranchID=1)

            for department in departments:
                department_name = department.DepartmentName
                departmentName = department_name.lower()

                if DepartmentNameLow == departmentName:
                    is_nameExist = True

            if not is_nameExist:
                data.CreatedDate = today
                data.UpdatedDate = today
                data.Action = "A"
                data.BranchID = 1
                data.CreatedUserID = 1
                data.DepartmentID = get_auto_id_department(Department,data.BranchID, DataBase)
                Department_Log.objects.using(DataBase).create(
                    BranchID=data.BranchID,
                    TransactionID=data.DepartmentID,
                    DepartmentName=data.DepartmentName,
                    Notes=data.Notes,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=data.Action,
                    CreatedUserID=data.CreatedUserID,
                    )
                data.save(using=DataBase)

                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Created")),
                    "message" : str(_("Department Created Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('payrolls:departments')
                }
            else:
                response_data = {
                    "status" : "false",
                    "title" : str(_("Department Already Exist")),
                    "message" : str(_("Department Name is Already exist with in the BranchID")),
                    "redirect" : "true",
                    "redirect_url" : reverse('payrolls:create_department')
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
        form = DepartmentForm()
        context = {
            "is_need_flatpickr" : False,
            "is_need_apexcharts" : False,
            "is_need_selectize" : False,
            "is_need_dashboard" : False,

            "title" : "Create Department",
            "form" : form
        }
        return render(request,"payrolls/masters/create_department.html",context)


@login_required
def view_department(request,pk):
    user = request.user
    customer_instance = get_object_or_404(CustomerUser.objects.filter(user=user))
    db_id = customer_instance.databaseid
    datastore = get_object_or_404(DatabaseStore.objects.filter(id=db_id))
    DataBase = datastore.DefaultDatabase
    instance = Department.objects.using(DataBase).get(pk=pk)
    context = {
        "is_need_flatpickr" : False,
        "is_need_apexcharts" : False,
        "is_need_selectize" : False,
        "is_need_dashboard" : False,

        'instance' : instance,
        'title' : 'Department'
    }
    return render(request,"payrolls/masters/department.html",context)


@login_required
def departments(request):
    user = request.user
    customer_instance = get_object_or_404(CustomerUser.objects.filter(user=user))
    db_id = customer_instance.databaseid
    datastore = get_object_or_404(DatabaseStore.objects.filter(id=db_id))
    DataBase = datastore.DefaultDatabase
    instances = Department.objects.using(DataBase).all()
    context = {
        "is_need_flatpickr" : False,
        "is_need_apexcharts" : False,
        "is_need_selectize" : False,
        "is_need_dashboard" : False,

        'instances' : instances,
        'title' : 'Departments'
    }
    return render(request,"payrolls/masters/departments.html",context)


@login_required
def edit_department(request,pk):
    user = request.user
    customer_instance = get_object_or_404(CustomerUser.objects.filter(user=user))
    db_id = customer_instance.databaseid
    datastore = get_object_or_404(DatabaseStore.objects.filter(id=db_id))
    DataBase = datastore.DefaultDatabase


    today = datetime.date.today()
    instance = Department.objects.using(DataBase).get(pk=pk)
    instanceDepartmentName = instance.DepartmentName
    DepartmentID = instance.DepartmentID
    if request.method == 'POST':
        form = DepartmentForm(request.POST,instance=instance)
        if form.is_valid(): 
            data = form.save(commit=False)
            DepartmentName = data.DepartmentName
            is_nameExist = False
            department_ok = False

            DepartmentNameLow = DepartmentName.lower()

            departments = Department.objects.using(DataBase).filter(BranchID=1)

            for department in departments:
                department_name = department.DepartmentName

                departmentName = department_name.lower()

                if DepartmentNameLow == departmentName:
                    is_nameExist = True

                if instanceDepartmentName.lower() == DepartmentNameLow:
                    department_ok = True
            if department_ok:
                data.CreatedDate = today
                data.UpdatedDate = today
                data.Action = "M"
                data.BranchID = 1
                data.CreatedUserID = 1
                Department_Log.objects.using(DataBase).create(
                    BranchID=data.BranchID,
                    TransactionID=DepartmentID,
                    DepartmentName=data.DepartmentName,
                    Notes=data.Notes,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=data.Action,
                    CreatedUserID=data.CreatedUserID,
                    )
                data.save(using=DataBase)

                response_data = {
                    "status" : "true",
                    "title" : str(_("Successfully Updated")),
                    "message" : str(_("Department Updated Successfully!")),
                    "redirect" : "true",
                    "redirect_url" : reverse('payrolls:view_department',kwargs={'pk':instance.pk})
                }
            else:
                if is_nameExist:
                    response_data = {
                        "status" : "false",
                        "title" : str(_("Department Already Exist")),
                        "message" : str(_("Department Name is Already exist with in the BranchID")),
                        "redirect" : "true",
                        "redirect_url" : reverse('payrolls:edit_department',kwargs={'pk':instance.pk})
                    }
                else:
                    data.CreatedDate = today
                    data.UpdatedDate = today
                    data.Action = "M"
                    data.BranchID = 1
                    data.CreatedUserID = 1
                    Department_Log.objects.using(DataBase).create(
                        BranchID=data.BranchID,
                        TransactionID=DepartmentID,
                        DepartmentName=data.DepartmentName,
                        Notes=data.Notes,
                        CreatedDate=today,
                        UpdatedDate=today,
                        Action=data.Action,
                        CreatedUserID=data.CreatedUserID,
                        )
                    data.save(using=DataBase)

                    response_data = {
                        "status" : "true",
                        "title" : str(_("Successfully Updated")),
                        "message" : str(_("Department Updated Successfully!")),
                        "redirect" : "true",
                        "redirect_url" : reverse('payrolls:view_department',kwargs={'pk':instance.pk})
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
        form = DepartmentForm(instance=instance)
        context = {
            "is_need_flatpickr" : False,
            "is_need_apexcharts" : False,
            "is_need_selectize" : False,
            "is_need_dashboard" : False,

            "title" : "Edit Department",
            "form" : form
        }
        return render(request,"payrolls/masters/create_department.html",context)


@login_required
def delete_department(request,pk):
    user = request.user
    customer_instance = get_object_or_404(CustomerUser.objects.filter(user=user))
    db_id = customer_instance.databaseid
    datastore = get_object_or_404(DatabaseStore.objects.filter(id=db_id))
    DataBase = datastore.DefaultDatabase


    today = datetime.date.today()    
    instance = Department.objects.using(DataBase).get(pk=pk)
    if pk == "1":
        response_data = {
            'status' : 'false',
            'stable' : 'true',
            'title' : str(_("can't delete this Department")),
            "message" : str(_("Can't delete this Department! this is default Department!"))
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    else:
        Department_Log.objects.using(DataBase).create(
            BranchID=instance.BranchID,
            TransactionID=instance.DepartmentID,
            DepartmentName=instance.DepartmentName,
            Notes=instance.Notes,
            CreatedDate=today,
            UpdatedDate=today,
            Action='D',
            CreatedUserID=instance.CreatedUserID,
            )
        instance.delete()
        
        response_data = {
            "status" : "true",
            "title" : str(_("Successfully Deleted")),
            "message" : str(_("Department Deleted Successfully.")),
            "redirect" : "true",
            "redirect_url" : reverse('payrolls:departments')
        }
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')