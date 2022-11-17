from django import forms
from django.forms.widgets import TextInput, Textarea, FileInput, Select, RadioSelect, DateInput, CheckboxInput
from django.forms.models import ModelChoiceField
from django.utils.translation import ugettext_lazy as _
from brands.models import Brand, Branch, AccountLedger, Bank, Color, Designation, Employee, Flavours, Kitchen, Product,ProductGroup,\
ProductCategory, TaxCategory, PriceList, Route, Warehouse, PurchaseMaster, PurchaseDetails



TAX_TYPES = (
    ('VAT', 'VAT'),
    ('GST', 'GST'),
    ('Tax1', 'Tax1'),
    ('Tax2', 'Tax2'),
    ('Tax3', 'Tax3'),
)


class DateInput(forms.DateInput):
    input_type = 'date'



class BrandForm(forms.ModelForm):

    class Meta:
        model = Brand
        exclude = ['BrandID','CreatedDate','UpdatedDate','Action','BranchID','CreatedUserID']
        widgets = {
            'BrandName': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('BrandName')}),
            'Notes': Textarea(attrs={'rows':'2','class' :'form-control form', 'placeholder' : _('Notes')}),
        }
        error_messages = {
        'BrandName' : {
            'required' : _("BrandName field is required."),
        },
        
    }


class FlavoursForm(forms.ModelForm):

    class Meta:
        model = Flavours
        exclude = ['FlavourID','BranchID','Action','CreatedDate','UpdatedDate']
        widgets = {
            'FlavourName': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('FlavourName')}),
            'BgColor': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('BgColor')}),
            'IsActive': CheckboxInput(attrs={'class' :'', 'placeholder' : 'IsActive','autocomplete' : 'off'}),
        }
        error_messages = {
        'FlavourName' : {
            'required' : _("FlavourName field is required."),
        },
        
    }

class RouteForm(forms.ModelForm):

        class Meta:
            model = Route
            exclude = ['FlavourID','BranchID','Action','CreatedDate','UpdatedDate','RouteID','CreatedUserID']
            widgets = {
                'RouteName': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('Route Name')}),
                'Notes': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('Notes')}),
            }
            error_messages = {
            'RouteName' : {
                'required' : _("Route Name field is required."),
            },
            'Notes' : {
                'required' : _("Notes field is required."),
            },
            
        }


class KitchenForm(forms.ModelForm):

        class Meta:
            model = Kitchen
            exclude = ['KitchenID','BranchID','Action','CreatedUserID','CreatedDate','UpdatedDate']
            widgets = {
                'KitchenName': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('KitchenName')}),
                'PrinterName': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('PrinterName')}),
                'IsActive': CheckboxInput(attrs={'class' :'', 'placeholder' : 'IsActive','autocomplete' : 'off'}),
                'Notes': Textarea(attrs={'rows':'2','class' :'form-control form', 'placeholder' : _('Notes')}),
            }
            error_messages = {
            'KitchenName' : {
                'required' : _("KitchenName field is required."),
            },
            
        }


class ProductForm(forms.ModelForm):

        class Meta:
            model = Product
            exclude = ['ProductID','BranchID','Action','GST','VatID','Tax1','Tax2','Tax3','CreatedUserID','CreatedDate','UpdatedDate','ProductCode']
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


class PriceListForm(forms.ModelForm):

        class Meta:
            model = PriceList
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


class ProductGroupForm(forms.ModelForm):

    class Meta:
        model = ProductGroup
        exclude = ['ProductGroupID','CategoryID','BranchID','CreatedUserID','CreatedDate','UpdatedDate','Action']
        widgets = {
            'GroupName': TextInput(attrs={'class' :'required form-control form','placeholder' : _('GroupName')}),
            'Notes': Textarea(attrs={'rows':'2','class' :'form-control form', 'placeholder' : _('Notes')}),
            
        }
        error_messages = {
        'GroupName' : {
            'required' : _("GroupName field is required."),
        }
    }


class TaxCategoryForm(forms.ModelForm):

    class Meta:
        model = TaxCategory
        exclude = ['TaxID','BranchID','CreatedUserID','CreatedDate','UpdatedDate','Action']
        widgets = {
                'TaxName': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('TaxName')}),
                'TaxType': Select(attrs={'class' :'required form-control form custom-select', 'placeholder' : _('TaxType')}, choices=TAX_TYPES),
                'PurchaseTax': TextInput(attrs={'class' :'required form-control form','placeholder' : _('PurchaseTax')}),
                'SalesTax': TextInput(attrs={'class' :'required form-control form','placeholder' : _('SalesTax')}),
                'Inclusive': CheckboxInput(attrs={'class' :'', 'placeholder' : 'Inclusive','autocomplete' : 'off'}),
                
            }
        error_messages = {
        'TaxName' : {
            'required' : _("TaxName field is required."),
        }
    }


class ProductCategoryForm(forms.ModelForm):

    class Meta:
        model = ProductCategory
        exclude = ['ProductCategoryID','BranchID','CreatedUserID','CreatedDate','UpdatedDate','Action']
        widgets = {
                'CategoryName': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('CategoryName')}),
                'Notes': Textarea(attrs={'rows':'2','class' :'form-control form', 'placeholder' : _('Notes')}),
            }
        error_messages = {
        'CategoryName' : {
            'required' : _("CategoryName field is required."),
        }
    }

class WarehouseForm(forms.ModelForm):

        class Meta:
            model = Warehouse
            exclude = ['WarehouseID','BranchID','Action','CreatedDate','UpdatedDate','CreatedUserID']
            widgets = {
                'WarehouseName': TextInput(attrs={'class' :'required form-control form', 'placeholder' : _('Warehouse Name')}),
                'Notes': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('Notes')}),
            }
            error_messages = {
            'WarehouseName' : {
                'required' : _("Route Name field is required."),
            },
            'Notes' : {
                'required' : _("Notes field is required."),
            },
            
        }


class PurchaseMasterForm(forms.ModelForm):

        class Meta:
            model = PurchaseMaster
            exclude = ['PurchaseMasterID','BranchID','PurchaseAccount','AdditionalCost','LedgerID','PriceCategoryID','EmployeeID','TransactionTypeID','FinacialYearID','TaxType','TaxID','WarehouseID','Action','CreatedDate','UpdatedDate','CreatedUserID']
            widgets = {
                'RefferenceBillNo': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('RefferenceBillNo')}),
                'Date': DateInput(attrs={'class' :'form-control form','placeholder' : _('Date'),'required' : True}),
                'VenderInvoiceDate': DateInput(attrs={'class' :'form-control form', 'placeholder' : _('VenderInvoiceDate')}),
                'CreditPeriod': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('CreditPeriod')}),                
                'VoucherNo': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('VoucherNo'),'required' : True}),                
                'CustomerName': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('CustomerName')}),
                'Address1': Textarea(attrs={'rows':'2','class' :'form-control form', 'placeholder' : _('Address1')}),
                'Address2': Textarea(attrs={'rows':'2','class' :'form-control form', 'placeholder' : _('Address2')}),
                'Address3': Textarea(attrs={'rows':'2','class' :'form-control form', 'placeholder' : _('Address3')}),
                'Notes': Textarea(attrs={'rows':'2','class' :'form-control form', 'placeholder' : _('Notes')}),
                'TotalGrossAmt': TextInput(attrs={'class' :'form-control form TotalGrossAmt','id':'TotalGrossAmt', 'placeholder' : _('TotalGrossAmt'),'readonly' : True}),
                'AddlDiscAmt': TextInput(attrs={'class' :'form-control form AddlDiscAmt','id':'AddlDiscAmt', 'placeholder' : _('AddlDiscAmt')}),
                'AddlDiscPercent': TextInput(attrs={'class' :'form-control form AddlDiscPercent','id':'AddlDiscPercent', 'placeholder' : _('AddlDiscPercent')}),
                'IsActive': CheckboxInput(attrs={'class' :'required', 'placeholder' : _('IsActive')}),
                'TotalTax': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('TotalTax'),'readonly' : True}),
                'NetTotal': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('NetTotal'),'readonly' : True}),
                'TotalDiscount': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('TotalDiscount'),'readonly' : True}),
                'GrandTotal': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('GrandTotal'),'readonly' : True}),
                'RoundOff': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('RoundOff')}),
                'VATAmount': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('VATAmount'),'readonly' : True}),
                'SGSTAmount': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('SGSTAmount'),'readonly' : True}),
                'CGSTAmount': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('CGSTAmount'),'readonly' : True}),
                'IGSTAmount': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('IGSTAmount'),'readonly' : True}),
                'TAX1Amount': TextInput(attrs={'class' :'form-control form TAX1Amount','id':'TAX1Amount', 'placeholder' : _('TAX1Amount'),'readonly' : True}),
                'TAX2Amount': TextInput(attrs={'class' :'form-control form TAX2Amount','id':'TAX2Amount', 'placeholder' : _('TAX2Amount'),'readonly' : True}),
                'TAX3Amount': TextInput(attrs={'class' :'form-control form TAX3Amount','id':'TAX3Amount', 'placeholder' : _('TAX3Amount'),'readonly' : True}),
                'BillDiscPercent': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('BillDiscPercent')}),
                'BillDiscAmt': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('BillDiscAmt')}),
                'Balance': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('Balance')}),
  
            }
            error_messages = {
            'CustomerName' : {
                'required' : _("Customer Name field is required."),
            },
            
        }


class PurchaseDetailsForm(forms.ModelForm):

        class Meta:
            model = PurchaseDetails
            exclude = ['PurchaseDetailsID','BranchID','Action','PurchaseMasterID','purchase_master','CreatedDate','UpdatedDate']
            widgets = {
                'GrossAmount': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('GrossAmount'),'readonly' : True}),
                'Qty': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('Qty')}),
                'FreeQty': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('FreeQty'),'value' : '0'}),
                'UnitPrice': TextInput(attrs={'class' :'form-control form unitAmount', 'placeholder' : _('UnitPrice'),'readonly' : True}),
                'RateWithTax': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('RateWithTax'),'readonly' : True}),
                'CostPerItem': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('CostPerItem'),'readonly' : True}),
                'DiscountPerc': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('DiscountPerc')}),
                'DiscountAmount': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('DiscountAmount')}),
                'AddlDiscPerc': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('AddlDiscPerc'),'readonly' : True}),
                'AddlDiscAmt': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('AddlDiscAmt'),'readonly' : True}),
                'TaxableAmount': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('TaxableAmount'),'readonly' : True}),
                'VATPerc': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('VATPerc'),'readonly' : True}),
                'VATAmount': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('VATAmount'),'readonly' : True}),
                'SGSTPerc': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('SGSTPerc'),'readonly' : True}),
                'SGSTAmount': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('SGSTAmount'),'readonly' : True}),
                'CGSTPerc': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('CGSTPerc'),'readonly' : True}),
                'CGSTAmount': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('CGSTAmount'),'readonly' : True}),
                'IGSTPerc': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('IGSTPerc'),'readonly' : True}),
                'IGSTAmount': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('IGSTAmount'),'readonly' : True}),
                'NetAmount': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('NetAmount'),'readonly' : True}),
                'TAX1Perc': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('TAX1Perc'),'readonly' : True}),
                'TAX1Amount': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('TAX1Amount'),'readonly' : True}),
                'TAX2Perc': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('TAX2Perc'),'readonly' : True}),
                'TAX2Amount': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('TAX2Amount'),'readonly' : True}),
                'TAX3Perc': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('TAX3Perc'),'readonly' : True}),
                'TAX3Amount': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('TAX3Amount'),'readonly' : True}),
                'ProductID': TextInput(attrs={'class' :'form-control form', 'placeholder' : _('ProductID'),'readonly' : True}),
                'PriceListID': TextInput(attrs={'class' :'form-control form PriceListID', 'placeholder' : _('PriceListID'),'readonly' : True}),
                
            }

            

