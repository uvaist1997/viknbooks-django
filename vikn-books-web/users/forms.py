from registration.forms import RegistrationForm
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
# from users.models import DatabaseStore, Customer, CustomerUser, CompanyEmployee, CompanyFinancialYear
from brands.models import Country
from django.forms.widgets import TextInput, DateInput, Textarea, Select
from django.contrib.auth.forms import UserModel , UsernameField


try:
    country_datas = Country.objects.all()
    country =  [(country_data.CountryID, country_data.Country_Name) for country_data in country_datas]
except:
    country = [(None, None)]

class DateInput(forms.DateInput):
    input_type = 'date'


class DatabaseStoreForm(forms.ModelForm):

    class Meta:
        # model = DatabaseStore
        exclude = ['DefaultDatabase', 'DatabaseName', 'username', 'password', 'customerid', 'CreatedDate', 'host', 'port', 'is_process','DefaultDatabase']
        widgets = {
            'CompanyName': TextInput(attrs={'class': 'required form-control','placeholder' : 'CompanyName'}),
            'Address1': TextInput(attrs={'class': 'required form-control','placeholder' : 'Address1'}),
            'Address2': TextInput(attrs={'class': 'required form-control','placeholder' : 'Address2'}),
            'Address3': TextInput(attrs={'class': 'required form-control','placeholder' : 'Address3'}),
            'city': TextInput(attrs={'class': 'required form-control','placeholder' : 'city'}),
            'state': TextInput(attrs={'class': 'required form-control','placeholder' : 'state'}),
            'country': Select(attrs={'class': 'required form-control custom-select','placeholder' : 'country'}, choices=country),
            'postalcode': TextInput(attrs={'class': 'required form-control','placeholder' : 'postalcode'}),
            'phone': TextInput(attrs={'class': 'required form-control','placeholder' : 'phone'}),
            'mobile': TextInput(attrs={'class': 'required form-control','placeholder' : 'mobile'}),
            'email': TextInput(attrs={'class': 'required form-control','placeholder' : 'email'}),
            'website': TextInput(attrs={'class': 'required form-control','placeholder' : 'website'}),
            'currency': TextInput(attrs={'class': 'required form-control','placeholder' : 'currency'}),
            'fractionalunit': TextInput(attrs={'class': 'required form-control','placeholder' : 'fractionalunit'}),
            'vatnumber': TextInput(attrs={'class': 'required form-control','placeholder' : 'vatnumber'}),
            'gstnumber': TextInput(attrs={'class': 'required form-control','placeholder' : 'gstnumber'}),
            'tax1': TextInput(attrs={'class': 'required form-control','placeholder' : 'tax1'}),
            'tax2': TextInput(attrs={'class': 'required form-control','placeholder' : 'tax2'}),
            'tax3': TextInput(attrs={'class': 'required form-control','placeholder' : 'tax3'}),
        }
        error_messages = {
            'CompanyName' : {
                'required' : _("Company Name field is required."),
            },
            'Address1' : {
                'required' : _("Address1 field is required."),
            },
            'Address2' : {
                'required' : _("Address2 field is required."),
            },
            'Address3' : {
                'required' : _("Address3 field is required."),
            },
            'city' : {
                'required' : _("city field is required."),
            },
            'state' : {
                'required' : _("state field is required."),
            },
            'country' : {
                'required' : _("country field is required."),
            },
            'postalcode' : {
                'required' : _("postalcode field is required."),
            },
            'phone' : {
                'required' : _("phone field is required."),
            },
            'mobile' : {
                'required' : _("mobile field is required."),
            },
            'email' : {
                'required' : _("email field is required."),
            },
            'website' : {
                'required' : _("website field is required."),
            },
            'currency' : {
                'required' : _("currency field is required."),
            },
            'fractionalunit' : {
                'required' : _("fractionalunit field is required."),
            },
            'vatnumber' : {
                'required' : _("vatnumber field is required."),
            },
            'gstnumber' : {
                'required' : _("gstnumber field is required."),
            },
            'tax1' : {
                'required' : _("tax1 field is required."),
            },
            'tax2' : {
                'required' : _("tax2 field is required."),
            },
            'tax3' : {
                'required' : _("tax3 field is required."),
            }
        }
        labels = {
            "CompanyName" : "CompanyName",
            "Address1" : "Address1",
            "Address2" : "Address2",
            "Address3" : "Address3",
            "city" : "city",
            "state" : "state",
            "country" : "country",
            "postalcode" : "postalcode",
            "phone" : "phone",
            "mobile" : "mobile",
            "email" : "email",
            "website" : "website",
            "currency" : "currency",
            "fractionalunit" : "fractionalunit",
            "vatnumber" : "vatnumber",
            "gstnumber" : "gstnumber",
            "tax1" : "tax1",
            "tax2" : "tax2",
            "tax3" : "tax3",
        }


class LoginForm(forms.Form):
    username = UsernameField(
        max_length=254,
        widget=forms.TextInput(attrs={'autofocus': True,'placeholder': 'Enter username','class':'required form-control'}),
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter username','class':'required form-control'}),
    )

    error_messages = {
        'invalid_login': _(
            "Please enter a correct %(username)s and password. Note that both "
            "fields may be case-sensitive."
        ),
        'inactive': _("This account is inactive."),
    }

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class UserForm(RegistrationForm):
    
    username = forms.CharField(label=_("Username"), 
                               max_length=254,
                               widget=forms.TextInput(
                                    attrs={'placeholder': 'Enter username','class':'required form-control'})
                               )
    email = forms.EmailField(label=_("Email"), 
                             max_length=254,
                             widget=forms.TextInput(
                                attrs={'placeholder': 'Enter email','class':'required form-control'})
                             )
    password1 = forms.CharField(label=_("Password"), 
                               widget=forms.PasswordInput(
                                    attrs={'placeholder': 'Enter password','class':'required form-control'})
                               )
    password2 = forms.CharField(label=_("Repeat Password"), 
                               widget=forms.PasswordInput(
                                    attrs={'placeholder': 'Enter password again','class':'required form-control'})
                               )
  
    bad_domains = ['guerrillamail.com']
    
    def clean_email(self):
        email_domain = self.cleaned_data['email'].split('@')[1]
        if User.objects.filter(email__iexact=self.cleaned_data['email'],is_active=True):
            raise forms.ValidationError(_("This email address is already in use."))        
        elif email_domain in self.bad_domains:
            raise forms.ValidationError(_("Registration using %s email addresses is not allowed. Please supply a different email address." %email_domain))
        return self.cleaned_data['email']
    
    min_password_length = 6
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1', '')
        if len(password1) < self.min_password_length:
            raise forms.ValidationError("Password must have at least %i characters" % self.min_password_length)
        else:
            return password1
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2
        
    min_username_length = 6

    def clean_username(self):
        username = self.cleaned_data['username']
        existing = User.objects.filter(username__iexact=self.cleaned_data['username'])
        if existing.exists():
            raise forms.ValidationError(_("A user with that username already exists."))
        elif len(username) < self.min_username_length:
            raise forms.ValidationError("Username must have at least %i characters" % self.min_password_length)
        else:
            return self.cleaned_data['username']  


class CompanyEmployeeForm(forms.ModelForm):

    class Meta:
        # model = CompanyEmployee
        exclude = ['ID','TransactionID','EmployeeID','CompanyID','BranchID','Action','EmployeeCode','LedgerID','ProbationPeriod','periodType','NoCasualLeave','DateOfJoining','Salary','Notes','Qualification','BloodGroup','DateOfBirth','Nationality','PassportNo','PassportExpiryDate','VisaDetails','VisaExpiryDate','Address1','Address2','Address3','State','Post','Phone','Mobile','CreatedDate','UpdatedDate','CreatedUserID',]
        widgets = {
            'FirstName': TextInput(attrs={'class': 'required form-control','placeholder' : 'FirstName'}),
            'LastName': TextInput(attrs={'class': 'required form-control','placeholder' : 'LastName'}),
            'DesignationID': TextInput(attrs={'class': 'required form-control','placeholder' : 'DesignationID'}),
            'DepartmentID': TextInput(attrs={'class': 'required form-control','placeholder' : 'DepartmentID'}),
            'Gender': TextInput(attrs={'class': 'required form-control','placeholder' : 'Gender'}),
            'Email': TextInput(attrs={'class': 'required form-control','placeholder' : 'Email'}),
            
        }
        error_messages = {
            'FirstName' : {
                'required' : _("First Name field is required."),
            },
            'LastName' : {
                'required' : _("Last Name field is required."),
            },
            'DesignationID' : {
                'required' : _("Designation ID field is required."),
            },
            'DepartmentID' : {
                'required' : _("Department ID field is required."),
            },
            'Gender' : {
                'required' : _("Gender field is required."),
            },
            'Email' : {
                'required' : _("Email field is required."),
            },
        }
        labels = {
            "FirstName" : "First Name",
            "LastName" : "Last Name",
            "DesignationID" : "Designation",
            "DepartmentID" : "Department",
            "Gender" : "Gender",
            "Email" : "Email",
        }


class CompanyFinancialYearForm(forms.ModelForm):

    class Meta:

        # model = CompanyFinancialYear
        exclude = ['FinancialYearID','CompanyID','Action','CreatedDate','UpdatedDate','CreatedUserID','IsClosed']
        widgets = {
            'FromDate': DateInput(attrs={'class' :'required form-control form dateinput', 'placeholder' : _('From Date')}),
            'ToDate': DateInput(attrs={'class' :'required form-control form dateinput', 'placeholder' : _('To Date')}),
            'Notes': Textarea(attrs={'class': 'required form-control','placeholder' : 'Notes'}),
            
        }
        error_messages = {
            'From Date' : {
                'required' : _("From Date field is required."),
            },
            'To Date' : {
                'required' : _("To Date field is required."),
            },
            'Close' : {
                'required' : _("Close field is required."),
            },
            'Notes' : {
                'required' : _("Notes field is required."),
            },
        }
        labels = {
            "FromDate" : "From Date",
            "ToDate" : "To Date",
            "Notes" : "Notes",
        }