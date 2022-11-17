from django import forms
from django.forms.widgets import TextInput, Textarea, FileInput, Select, RadioSelect, DateInput, CheckboxInput
from django.forms.models import ModelChoiceField
from django.utils.translation import ugettext_lazy as _
from brands.models import Brand, Branch, AccountLedger, Bank, Color, Designation, Employee, LedgerPosting, Country, AccountGroup,\
Parties, TransactionTypes, MasterType, PaymentDetails, PaymentMaster, ReceiptMaster, ReceiptDetails, JournalMaster, JournalDetails
# brands models

try:
    country_datas = Country.objects.all()
    country =  [(country_data.Country_Name, country_data.Country_Name) for country_data in country_datas]
except:
    country = [(None, None)]

try:
    masterType_datas = MasterType.objects.filter(BranchID=1)
    masterType =  [(masterType_data.MasterTypeID, masterType_data.Name) for masterType_data in masterType_datas]
except:
    masterType = [(None, None)]


CREDIT_DEBIT_CHOICES = (
        ('Cr', 'Credit'),
        ('Dr', 'Debit'),
    )


class DateInput(forms.DateInput):
    input_type = 'date'


class AccountGroupForm(forms.ModelForm):

        class Meta:
            model = AccountGroup
            exclude = ['AccountGroupID','CreatedUserID','CreatedDate','UpdatedDate','Action','AccountGroupUnder']
            widgets = {
                'AccountGroupName': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('AccountGroupName')}),
                'GroupCode': TextInput(attrs={'class' :'required form-control form','placeholder' : _('GroupCode'),'readonly' : True}),
                'Notes': Textarea(attrs={'rows':'2','class' :'form-control form', 'placeholder' : _('Notes')}),
                'IsActive': CheckboxInput(attrs={'class' :'', 'placeholder' : 'IsActive','autocomplete' : 'off'}),
                'IsDefault': CheckboxInput(attrs={'class' :'', 'placeholder' : 'IsDefault','autocomplete' : 'off'}),
                
            }
            error_messages = {
            'AccountGroupName' : {
                'required' : _("AccountGroupName field is required."),
            }
        }

class AccountLedgerForm(forms.ModelForm):

        class Meta:
            model = AccountLedger
            exclude = ['LedgerID','CreatedDate','UpdatedDate','Action','BranchID','CreatedUserID','LedgerCode','AccountGroupUnder','CrOrDr']
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

# branch form

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

# branch form ends

# bank form

class BankForm(forms.ModelForm):

        class Meta:
            model = Bank
            exclude = ['BankID','CreatedDate','UpdatedDate','Action','BranchID','CreatedUserID','LedgerCode','LedgerName']
            widgets = {
                'Name': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('Name')}),
                'AccountNumber': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('AccountNumber')}),
                'BranchCode': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('BranchCode')}),
                'IFSCCode': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('IFSCCode')}),
                'MICRCode': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('MICRCode')}),
                'Status': CheckboxInput(attrs={'class' :'', 'placeholder' : 'Status','autocomplete' : 'off'}),
                'OpeningBalance': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('OpeningBalance')}),
                'CrOrDr': Select(attrs={'class' :'required form-control form custom-select', 'placeholder' : _('Credit or Debit')}, choices=CREDIT_DEBIT_CHOICES),
                'Address': Textarea(attrs={'rows':'2','class' :'form-control form', 'placeholder' : _('Notes')}),
                'Notes': Textarea(attrs={'rows':'2','class' :'form-control form', 'placeholder' : _('Notes')}),
                'City': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('City')}),
                'State': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('State')}),
                'Country' : Select(attrs={'class' :'required form-control form custom-select', 'placeholder' : _('Country')}, choices=country),
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

# bankform ends

class CustomerForm(forms.ModelForm):

        class Meta:
            model = Parties
            exclude = ['PartyID','PartyType','BranchID','LedgerID','PartyCode','CreatedDate','UpdatedDate','CreatedUserID','Action']
            widgets = {
                'FirstName': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('FirstName')}),
                'LastName': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('LastName')}),
                'OpeningBalance': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('OpeningBalance')}),
                'ContactPerson': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('ContactPerson')}),
                'Address1': Textarea(attrs={'rows':'2','class' :'form-control form', 'placeholder' : _('Address1')}),
                'Address2': Textarea(attrs={'rows':'2','class' :'form-control form', 'placeholder' : _('Address2')}),
                'Address3': Textarea(attrs={'rows':'2','class' :'form-control form', 'placeholder' : _('Address3')}),
                'Address4': Textarea(attrs={'rows':'2','class' :'form-control form', 'placeholder' : _('Address4')}),
                'City': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('City')}),
                'State': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('State')}),
                'Country' : Select(attrs={'class' :'required form-control form custom-select', 'placeholder' : _('Country')}, choices=country),
                'PostalCode': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('PostalCode')}),
                'OfficePhone': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('OfficePhone')}),
                'WorkPhone': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('WorkPhone')}),
                'Mobile': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('Mobile')}),
                'WebURL': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('WebURL')}),
                'Email': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('Email')}),
                'IsBillwiseApplicable': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('IsBillwiseApplicable')}),
                'CreditPeriod': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('CreditPeriod')}),
                'CreditLimit': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('CreditLimit')}),
                'PriceCategoryID': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('PriceCategoryID')}),
                'CurrencyID': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('CurrencyID')}),
                'InterestOrNot': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('InterestOrNot')}),
                'RouteID': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('RouteID')}),
                'VATNumber': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('VATNumber')}),
                'GSTNumber': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('GSTNumber')}),
                'Tax1Number': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('Tax1Number')}),
                'Tax2Number': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('Tax2Number')}),
                'Tax3Number': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('Tax3Number')}),
                'PanNumber': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('PanNumber')}),
                'BankName1': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('BankName1')}),
                'AccountName1': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('AccountName1')}),
                'AccountNo1': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('AccountNo1')}),
                'IBANOrIFSCCode1': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('IBANOrIFSCCode1')}),
                'BankName2': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('BankName2')}),
                'AccountName2': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('AccountName2')}),
                'AccountNo2': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('AccountNo2')}),
                'IBANOrIFSCCode2': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('IBANOrIFSCCode2')}),
                'IsActive': CheckboxInput(attrs={'class' :'', 'placeholder' : 'IsActive','autocomplete' : 'off'}),
                'PartyImage': FileInput(attrs={'class' :'form-control form', 'placeholder' : _('PartyImage')}),
                'img': FileInput(attrs={'class' :'form-control form', 'placeholder' : _('img')}),
            }
            error_messages = {
            'FirstName' : {
                'required' : _("FirstName field is required."),
            },
        }


class LedgerPostingForm(forms.ModelForm):

        class Meta:
            model = LedgerPosting
            exclude = ['LedgerID','CreatedDate','UpdatedDate','Action','BranchID','CreatedUserID','LedgerCode','AccountGroupUnder','CrOrDr']
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


class TransactionTypesForm(forms.ModelForm):

        class Meta:
            model = TransactionTypes
            exclude = ['TransactionTypesID','BranchID','Action','CreatedDate','UpdatedDate','CreatedUserID']
            widgets = {
                'MasterTypeID' : Select(attrs={'class' :'required form-control form custom-select', 'placeholder' : _('MasterType')}, choices=masterType),
                'Name': TextInput(attrs={'class' :'required form-control form','placeholder' : _('Name')}),
                'Notes': Textarea(attrs={'rows':'2','class' :'form-control form', 'placeholder' : _('Notes')}),
                'IsDefault': CheckboxInput(attrs={'class' :'', 'placeholder' : 'IsDefault','autocomplete' : 'off'}),
                
            }
            error_messages = {
            'Name' : {
                'required' : _("Name field is required."),
            }
        }

class PaymentDetailsForm(forms.ModelForm):

        class Meta:
            model = PaymentDetails
            exclude = ['BranchID','CreatedUserID','Action','CreatedDate','PaymentMasterID','payment_master','PaymentDetailsID']
            widgets = {
                'PaymentGateway': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('PaymentGateway')}),
                'RefferenceNo': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('RefferenceNo')}),
                'CardNetwork': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('CardNetwork')}),
                'PaymentStatus': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('PaymentStatus')}),
                'DueDate': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('DueDate')}),
                'LedgerID': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('LedgerID')}),
                'Amount ': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('Amount ')}),
                'Balance': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('Balance')}),
                'Discount': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('Discount')}),
                'NetAmount ': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('NetAmount ')}),
                'Narration': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('Narration')}),
            }
            error_messages = {
            'PaymentGateway' : {
                'required' : _("PaymentGateway field is required."),
            },
            
        }

class PaymentMasterForm(forms.ModelForm):

        class Meta:
            model = PaymentMaster
            exclude = ['BranchID','CreatedUserID','Action','CreatedDate','UpdatedDate','PaymentMasterID','VoucherNo','FinancialYearID','EmployeeID','VoucherType']
            widgets = {
                'VoucherNo': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('VoucherNo')}),
                'VoucherType': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('VoucherType')}),
                'LedgerID': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('LedgerID')}),
                'EmployeeID': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('EmployeeID')}),
                'PaymentNo': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('PaymentNo')}),
                'Date': DateInput(attrs={'class' :'required form-control form', 'placeholder' : _('Date')}),
                'TotalAmount ': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('TotalAmount ')}),
                'Notes': Textarea(attrs={'class' :'required form-control form', 'placeholder' : _('Notes')}),
            }
            error_messages = {
            'BranchName' : {
                'required' : _("BranchName field is required."),
            },
            
        }


class ReceiptMasterForm(forms.ModelForm):

        class Meta:
            model = ReceiptMaster
            exclude = ['ReceiptMasterID','BranchID','Action','VoucherNo','VoucherType','ReceiptNo','EmployeeID','FinancialYearID','CreatedDate','UpdatedDate','CreatedUserID',]
            widgets = {
                'LedgerID': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('LedgerID')}),
                'Date': DateInput(attrs={'class' :'required form-control form', 'placeholder' : _('Date')}),
                'TotalAmount': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('TotalAmount')}),
                'Notes': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('Notes')}),
            }
            error_messages = {
            'LedgerID' : {
                'required' : _("LedgerID field is required."),
            },
            
        }

class ReceiptDetailsForm(forms.ModelForm):

        class Meta:
            model = ReceiptDetails
            exclude = ['ReceiptDetailID','BranchID','Action','ReceiptMasterID','receipt_master','VoucherType','CreatedDate','UpdatedDate','CreatedUserID',]
            widgets = {
                'PaymentGateway': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('PaymentGateway')}),
                'RefferenceNo': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('RefferenceNo')}),
                'CardNetwork': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('CardNetwork')}),
                'PaymentStatus': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('PaymentStatus')}),
                'DueDate': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('DueDate')}),
                'LedgerID': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('LedgerID')}),
                'Amount': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('Amount')}),
                'Balance': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('Balance')}),
                'Discount': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('Discount')}),
                'NetAmount': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('NetAmount')}),
                'Narration': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('Narration')}),
                
            }
            error_messages = {
            'PaymentGateway' : {
                'required' : _("PaymentGateway field is required."),
            },
        }

class JournalMasterForm(forms.ModelForm):

        class Meta:
            model = JournalMaster
            exclude = ['JournalMasterID','BranchID','VoucherNo','Action','CreatedDate','UpdatedDate','CreatedUserID',]
            widgets = {
                'Date': DateInput(attrs={'class' :'required form-control form', 'placeholder' : _('Date')}),
                'Notes': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('Notes')}),
                'TotalDebit': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('TotalDebit')}),
                'TotalCredit': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('TotalCredit')}),
                'Difference': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('Difference')}),
            }
            error_messages = {
            'LedgerID' : {
                'required' : _("LedgerID field is required."),
            },
            
        }

class JournalDetailsForm(forms.ModelForm):

        class Meta:
            model = JournalDetails
            exclude = ['JournalDetailsID','BranchID','JournalMasterID','journal_master','Action','CreatedDate','UpdatedDate','CreatedUserID',]
            widgets = {
                'LedgerID': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('PaymentGateway')}),
                'Debit': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('PaymentGateway')}),
                'Credit': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('PaymentGateway')}),
                'Narration': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('PaymentGateway')}),
                
            }
            error_messages = {
            'PaymentGateway' : {
                'required' : _("PaymentGateway field is required."),
            },
        }