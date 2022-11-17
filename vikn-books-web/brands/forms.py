from django import forms
from django.forms.widgets import TextInput, Textarea, FileInput, Select, RadioSelect, DateInput, CheckboxInput
from django.forms.models import ModelChoiceField
from django.utils.translation import ugettext_lazy as _
from brands.models import Brand, Branch, AccountLedger, Bank, Color, Designation, Employee, Flavours, Kitchen, Product,ProductGroup,\
ProductCategory, TaxCategory, PriceList, Route, Warehouse, PurchaseMaster, PurchaseDetails,TestFormModel,TestFormSetModel



class TestFormModelForm(forms.ModelForm):

        class Meta:
            model = TestFormModel
            exclude = ['ProductID','BranchID','Action','CreatedUserID','CreatedDate','UpdatedDate','ProductCode']
            widgets = {
                'ProductName': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('ProductName')}),
                'DisplayName': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('DisplayName')}),
                'Description': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('Description')}),
                'ProductGroupID': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('ProductGroupID')}),
                'BrandID': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('BrandID')}),
                'InventoryType': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('InventoryType')}),
                'VatID': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('VatID')}),
                'StockMinimum': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('StockMinimum')}),
                'StockReOrder': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('StockReOrder')}),
                'StockMaximum': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('StockMaximum')}),
                'MarginPercent': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('MarginPercent')}),
                'ProductImage': FileInput(attrs={'class' :'form-control form', 'placeholder' : _('ProductImage')}),
                'Active': CheckboxInput(attrs={'class' :'', 'placeholder' : _('Active')}),
                'IsWeighingScale': CheckboxInput(attrs={'class' :'', 'placeholder' : _('IsWeighingScale')}),
                'IsRawMaterial': CheckboxInput(attrs={'class' :'', 'placeholder' : _('IsRawMaterial')}),
                'IsFinishedProduct': CheckboxInput(attrs={'class' :'', 'placeholder' : _('IsFinishedProduct')}),
                'IsSales': CheckboxInput(attrs={'class' :'', 'placeholder' : _('IsSales')}),
                'IsPurchase': CheckboxInput(attrs={'class' :'', 'placeholder' : _('IsPurchase')}),
                'WeighingCalcType': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('WeighingCalcType')}),
                'PLUNo': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('PLUNo')}),
                'IsFavourite': CheckboxInput(attrs={'class' :'', 'placeholder' : _('IsFavourite')}),
                'GST': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('GST')}),
                'Tax1': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('Tax1')}),
                'Tax2': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('Tax2')}),
                'Tax3': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('Tax3')}),
                'IsActive': CheckboxInput(attrs={'class' :'', 'placeholder' : 'IsActive','autocomplete' : 'off'}),
                'Notes': Textarea(attrs={'rows':'2','class' :'form-control form', 'placeholder' : _('Notes')}),
            }
            error_messages = {
                'ProductName' : {
                    'required' : _("Product Name field is required."),
                },
            
            }
            labels = {
                "ProductName" : "Product Name",
                "DisplayName" : "Display Name",
                "Description" : "Description",
                "ProductGroupID" : "Product Group",
                "BrandID" : "Brand",
                "InventoryType" : "Inventory Type",
                "VatID" : "VAT",
                "StockMinimum" : "Stock Minimum",
                "StockReOrder" : "Stock ReOrder",
                "StockMaximum" : "Stock Maximum",
                "MarginPercent" : "Margin Percent",
                "ProductImage" : "Product Image",
                "Active" : "Active",
                "IsWeighingScale" : "Weighing Scale",
                "IsRawMaterial" : "Raw Material",
                "IsFinishedProduct" : "Finished Product",
                "IsSales" : "Sales",
                "IsPurchase" : "Purchase",
                "WeighingCalcType" : "Weighing Calc Type",
                "PLUNo" : "PLUNo",
                "IsFavourite" : "Favourite",
                "GST" : "GST",
                "Tax1" : "Tax1",
                "Tax2" : "Tax2",
                "Tax3" : "Tax3",
                "IsActive" : "Active",
                "Notes" : "Notes",
            }


class TestFormSetModelForm(forms.ModelForm):

        class Meta:
            model = TestFormSetModel
            exclude = ['ProductID','DefaultUnit','product','AutoBarcode','PriceListID','BranchID','Action','CreatedUserID','CreatedDate','UpdatedDate']
            widgets = {
                'UnitName': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('UnitName')}),
                'SalesPrice': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('SalesPrice')}),
                'PurchasePrice': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('PurchasePrice')}),
                'MultiFactor': TextInput(attrs={'value':'1','class' :'form-control form', 'placeholder' : _('MultiFactor')}),
                'Barcode': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('Barcode')}),
                'SalesPrice1': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('SalesPrice1')}),
                'SalesPrice2': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('SalesPrice2')}),
                'SalesPrice3': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('SalesPrice3')}),
                'MRP': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('MRP')}),
                }
            error_messages = {
            'UnitName' : {
                'required' : _("UnitName field is required."),
            },
            
        }

