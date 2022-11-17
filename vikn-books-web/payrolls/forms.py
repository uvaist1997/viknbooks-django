from django import forms
from django.forms.widgets import TextInput, Textarea, FileInput, Select, RadioSelect, DateInput, CheckboxInput
from django.forms.models import ModelChoiceField
from django.utils.translation import ugettext_lazy as _
from brands.models import Brand, Branch, AccountLedger, Bank, Color, Designation, Employee, Department, Designation, Country
# brands models#


try:
    designation_datas = Designation.objects.all()
    designation_group_under = [(designation_data.DesignationID, designation_data.DesignationName) for designation_data in designation_datas]
except:
    designation_group_under = [(None, None)]

try:
    department_datas = Department.objects.all()
    department_id = [(department_data.DepartmentID, department_data.DepartmentName) for department_data in department_datas]
except:
    department_id = [(None, None)]

try:
    designation_datas = Designation.objects.all()
    designation_id =  [(designation_data.DesignationID, designation_data.DesignationName) for designation_data in designation_datas]
except:
    designation_id = [(None, None)]

try:
    country_datas = Country.objects.all()
    country =  [(country_data.CountryID, country_data.Country_Name) for country_data in country_datas]
except:
    country = [(None, None)]

GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )

GENDER_CHOICES = (
        ('hour', 'Hour'),
        ('month', 'Day'),
        ('day', 'Month'),
    )

BLOOD_GROUP_CHOICES = (
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    )


class DateInput(forms.DateInput):
    input_type = 'date'

class DesignationForm(forms.ModelForm):

        class Meta:
            model = Designation
            exclude = ['DesignationID','BranchID','CreatedUserID','CreatedDate','UpdatedDate','Action']
            widgets = {
                'DesignationName': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('DesignationName')}),
                'ShortName': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('Short Name')}),
                'DesignationUnder': Select(attrs={'class' :'required form-control form custom-select ', 'placeholder' : _('Designation Under')}, choices=designation_group_under),
                'Notes': Textarea(attrs={'rows':'2','class' :'form-control form', 'placeholder' : _('Notes')}),
            }
            error_messages = {
                'DesignationName' : {
                    'required' : _("DesignationName field is required."),
                },
            }
            labels = {
                "FirstName" : "First Name",
            }


class EmployeeForm(forms.ModelForm):

        class Meta:
            model = Employee
            exclude = ['EmployeeID','BranchID','Action','EmployeeCode','LedgerID','CreatedDate','UpdatedDate','CreatedUserID','CompanyID']

            widgets = {
                'FirstName': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('First Name')}),
                'LastName': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('Last Name')}),
                'ProbationPeriod': TextInput(attrs={'class' :' form-control form', 'placeholder' : _('Probation Period')}),
                'periodType': Select(attrs={'class' :' form-control form custom-select', 'placeholder' : _('Period Type')}, choices=GENDER_CHOICES),
                'NoCasualLeave': TextInput(attrs={'class' :' form-control form', 'placeholder' : _('No. of Casual Leave')}),
                'DepartmentID': Select(attrs={'class' :'required form-control form custom-select', 'placeholder' : _('Department')}, choices=department_id),
                'DesignationID': Select(attrs={'class' :'required form-control form custom-select', 'placeholder' : _('Designation')}, choices=designation_id),
                'DateOfJoining': DateInput(attrs={'class' :'form-control form dateinput', 'placeholder' : _('Date Of Joining')}),
                'Salary': TextInput(attrs={'class' :' form-control form', 'placeholder' : _('Salary')}),
                'AccountHolderName': TextInput(attrs={'class' :' form-control form', 'placeholder' : _('AccountHolderName')}),
                'AccountName': TextInput(attrs={'class' :' form-control form', 'placeholder' : _('AccountName')}),
                'AccountBranch': TextInput(attrs={'class' :' form-control form', 'placeholder' : _('AccountBranch')}),
                'AccountIFSC': TextInput(attrs={'class' :' form-control form', 'placeholder' : _('AccountIFSC')}),
                'Notes': Textarea(attrs={'rows':'2','class' :'form-control form', 'placeholder' : _('Notes')}),
                'Qualification': TextInput(attrs={'class' :' form-control form', 'placeholder' : _('Qualification')}),
                'EmergencyContactNumber': TextInput(attrs={'class' :' form-control form', 'placeholder' : _('Emergency Contact Number')}),
                'EmergencyEmail': TextInput(attrs={'class' :' form-control form', 'placeholder' : _('Emergency Email')}),
                'EmergencyAddress': TextInput(attrs={'class' :' form-control form', 'placeholder' : _('Emergency Address')}),
                'DateOfBirth': DateInput(attrs={'class' :'form-control form dateinput', 'placeholder' : _('Date Of Birth')}),
                'Gender': Select(attrs={'class' :'form-control form custom-select', 'placeholder' : _('Gender')}, choices=GENDER_CHOICES),
                'BloodGroup': Select(attrs={'class' :' form-control custom-select form', 'placeholder' : _('Blood Group')}, choices=BLOOD_GROUP_CHOICES),
                'PassportNo': TextInput(attrs={'class' :' form-control form', 'placeholder' : _('AccountIFSC')}),
                'PassportExpiryDate': DateInput(attrs={'class' :'form-control form dateinput', 'placeholder' : _('Passport ExpiryDate')}),
                'VisaDetails': TextInput(attrs={'class' :' form-control form', 'placeholder' : _('Visa Details')}),
                'VisaExpiryDate': DateInput(attrs={'class' :'form-control form dateinput', 'placeholder' : _('Visa Expiry Date')}),
                'Address1': Textarea(attrs={'rows':'2','class' :'form-control form', 'placeholder' : _('Address 1')}),
                'Address2': Textarea(attrs={'rows':'2','class' :'form-control form', 'placeholder' : _('Address 2')}),
                'Address3': Textarea(attrs={'rows':'2','class' :'form-control form', 'placeholder' : _('Address 3')}),
                'Nationality' : Select(attrs={'class' :'required form-control form custom-select', 'placeholder' : _('Nationality')}, choices=country),
                'State': TextInput(attrs={'class' :' form-control form', 'placeholder' : _('State')}),      
                'Post': TextInput(attrs={'class' :' form-control form', 'placeholder' : _('Post')}),
                'Phone': TextInput(attrs={'class' :' form-control form', 'placeholder' : _('Phone')}),
                'Mobile': TextInput(attrs={'class' :' form-control form', 'placeholder' : _('Mobile')}),
                'Email': TextInput(attrs={'class' :' form-control form', 'placeholder' : _('Email')}),
            }
            error_messages = {
            'EmployeeName' : {
                'required' : _("EmployeeName field is required."),
            }
            }
            labels = {
                "FirstName" : "First Name",
                "LastName" : "Last Name",
                "ProbationPeriod" : "Probation Period",
                "periodType" : "Period Type",
                "NoCasualLeave" : "No. of Casual Leave",
                "DepartmentID" : "Department",
                "DesignationID" : "Designation",
                "DateOfJoining" : "Date Of Joining",
                "Salary" : "Salary",
                "Notes" : "Notes",
                "Qualification" : "Qualification",
                "AccountHolderName" : "Account Holder Name",
                "AccountName" : "Account Name",
                "AccountBranch" : "Account Branch",
                "AccountIFSC" : "AccountIFSC",
                "EmergencyContactNumber" : "Emergency Contact Number",
                "EmergencyEmail" : "Emergency Email",
                "EmergencyAddress" : "Emergency Address",

                "DateOfBirth" : "Date Of Birth",
                "PassportNo" : "Passport No.",
                "PassportExpiryDate" : "Passport Expiry Date",
                "VisaDetails" : "Visa Details",
                "VisaExpiryDate" : "Visa Expiry Date",
                "Address1" : "Address 1",
                "Address2" : "Address 2",
                "Address3" : "Address 3",
                "Nationality" : "Nationality",
                "State" : "State",
                "Post" : "Post",
                "Phone" : "Phone",
                "Mobile" : "Mobile",
                "Email" : "Email",
            }


class DepartmentForm(forms.ModelForm):

        class Meta:
            model = Department
            exclude = ['DepartmentID','BranchID','CreatedUserID','CreatedDate','UpdatedDate','Action']
            widgets = {
                'DepartmentName': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('Department Name')}),
                'Notes': Textarea(attrs={'rows':'2','class' :'form-control form', 'placeholder' : _('Notes')}),
            }
            error_messages = {
                'DepartmentName' : {
                    'required' : _("DepartmentName field is required."),
                },
            }
            labels = {
                "DepartmentName" : "Department Name",
            }