from django import forms
from django.forms.widgets import TextInput, Textarea, FileInput, Select, RadioSelect, DateInput, CheckboxInput
from django.forms.models import ModelChoiceField
from django.utils.translation import ugettext_lazy as _
from brands.models import Brand, Branch, AccountLedger, Bank


class BrandForm(forms.ModelForm):

        class Meta:
            model = Brand
            exclude = ['BrandID','CreatedDate','Action','BranchID','CreatedUserID']
            widgets = {
                'BrandName': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('BrandName')}),
                'Notes': Textarea(attrs={'rows':'2','class' :'form-control form', 'placeholder' : _('Notes')}),
            }
            error_messages = {
            'BrandName' : {
                'required' : _("BrandName field is required."),
            },
            
        }


class BranchForm(forms.ModelForm):

        class Meta:
            model = Branch
            exclude = ['BranchID','CreatedUserID','Action','CreatedDate']
            widgets = {
                'BranchName': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('BranchName')}),
                'BranchLocation': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('BranchLocation')}),
            }
            error_messages = {
            'BranchName' : {
                'required' : _("BranchName field is required."),
            },
            
        }


class AccountLedgerForm(forms.ModelForm):

        class Meta:
            model = AccountLedger
            exclude = ['LedgerID','CreatedDate','Action','BranchID','CreatedUserID','LedgerCode','AccountGroupUnder','CrOrDr']
            widgets = {
                'LedgerName': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('LedgerName')}),
                'OpeningBalance': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('OpeningBalance')}),
                'Notes': Textarea(attrs={'rows':'2','class' :'form-control form', 'placeholder' : _('Notes')}),
                'IsActive': CheckboxInput(attrs={'class' :'', 'placeholder' : 'IsActive','autocomplete' : 'off'}),
                'IsDefault': CheckboxInput(attrs={'class' :'', 'placeholder' : 'IsDefault','autocomplete' : 'off'}),
                
            }
            error_messages = {
            'LedgerName' : {
                'required' : _("LedgerName field is required."),
            }
        }


class BankForm(forms.ModelForm):

        class Meta:
            model = Bank
            exclude = ['BankID','CreatedDate','Action','BranchID','CreatedUserID','LedgerCode','CrOrDr','LedgerName']
            widgets = {
                'Name': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('Name')}),
                'AccountNumber': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('AccountNumber')}),
                'BranchCode': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('BranchCode')}),
                'IFSCCode': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('IFSCCode')}),
                'MICRCode': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('MICRCode')}),
                'Status': CheckboxInput(attrs={'class' :'', 'placeholder' : 'Status','autocomplete' : 'off'}),
                'OpeningBalance': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('OpeningBalance')}),
                'Address': Textarea(attrs={'rows':'2','class' :'form-control form', 'placeholder' : _('Notes')}),
                'Notes': Textarea(attrs={'rows':'2','class' :'form-control form', 'placeholder' : _('Notes')}),
                'City': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('City')}),
                'State': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('State')}),
                'Country': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('Country')}),
                'PostalCode': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('PostalCode')}),
                'Phone': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('Phone')}),
                'Mobile': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('Mobile')}),
                'Email': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('Email')}),
            }
            error_messages = {
            'Name' : {
                'required' : _("Name field is required."),
            },
            'AccountNumber' : {
                'required' : _("AccountNumber field is required."),
            },
        }
