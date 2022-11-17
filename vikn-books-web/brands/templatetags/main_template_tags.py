from django.template import Library
from django.template.defaultfilters import stringfilter
from brands.models import LedgerPosting, AccountLedger, AccountGroup, MasterType, ProductCategory, Brand, GeneralSettings, TransactionTypes
from django import template

register = template.Library()


@register.filter
def TotalDebit(instance):
    LedgerID = instance.LedgerID
    BranchID = instance.BranchID
    TotalDebit = 0
    if LedgerPosting.objects.filter(LedgerID=LedgerID,BranchID=BranchID).exists():
        Ledger_instances = LedgerPosting.objects.filter(LedgerID=LedgerID,BranchID=BranchID)
        for i in Ledger_instances:
            TotalDebit += i.Debit
        return TotalDebit
    else:
        return ""


@register.filter
def TotalCredit(instance):
    LedgerID = instance.LedgerID
    BranchID = instance.BranchID
    TotalCredit = 0
    if LedgerPosting.objects.filter(LedgerID=LedgerID,BranchID=BranchID).exists():
        Ledger_instances = LedgerPosting.objects.filter(LedgerID=LedgerID,BranchID=BranchID)
        for i in Ledger_instances:
            TotalCredit += i.Credit
        return TotalCredit
    else:
        return ""


@register.filter
def to_fixed_two(value):
    return "{:10.2f}".format(value)


@register.filter
def VoucherType(voucher):
    if voucher == 'JL':
        VoucherType = 'Journal'
    elif voucher == 'SI':
        VoucherType = 'Sales Invoice'
    elif voucher == 'PI':  
        VoucherType = 'Purchase Invoice'
    elif voucher == 'SR':
        VoucherType = 'Sales Return'
    elif voucher == 'PR':
        VoucherType = 'Purchase Return'
    elif voucher == 'SO':
        VoucherType = 'Sales Order'
    elif voucher == 'PO':
        VoucherType = 'Purchase Order'
    elif voucher == 'CP':
        VoucherType = 'Cash Payment'
    elif voucher == 'BP':
        VoucherType = 'Bank Payment'
    elif voucher == 'CR':
        VoucherType = 'Cash Receipt'
    elif voucher == 'BR':
        VoucherType = 'Bank Receipt'
    elif voucher == 'LOB':
        VoucherType = 'Ledger Opening Balance'
    return VoucherType



@register.filter
def LedgerName(instance):
    for i in instance:
        LedgerID = i.LedgerID
        BranchID = i.BranchID
    if AccountLedger.objects.filter(LedgerID=LedgerID,BranchID=BranchID).exists():
        Ledger_instance = AccountLedger.objects.get(LedgerID=LedgerID,BranchID=BranchID)
        LedgerName = Ledger_instance.LedgerName
            
        return LedgerName
    else:
        return ""

@register.filter
def BrandName(BrandID):
    
    if Brand.objects.filter(BrandID=BrandID,BranchID=1).exists():
        Brand_instance = Brand.objects.get(BrandID=BrandID,BranchID=1)
        BrandName = Brand_instance.BrandName
            
        return BrandName
    else:
        return ""


@register.filter
def MasterName(MasterTypeID):
    if MasterType.objects.filter(MasterTypeID=MasterTypeID).exists():
        master_instance = MasterType.objects.get(MasterTypeID=MasterTypeID)
        MasterName = master_instance.Name
            
        return MasterName
    else:
        return ""


@register.filter
def CategoryName(instance,DataBase):
    CategoryID = instance.CategoryID
    BranchID = instance.BranchID
    if ProductCategory.objects.using(DataBase).filter(ProductCategoryID=CategoryID,BranchID=BranchID).exists():
        category_instance = ProductCategory.objects.using(DataBase).get(ProductCategoryID=CategoryID,BranchID=BranchID)
        CategoryName = category_instance.CategoryName
            
        return CategoryName
    else:
        return ""


@register.filter
def TaxID(instance,DataBase):
    TaxType = instance.TaxType
    BranchID = instance.BranchID
    is_VAT = False
    is_GST = False
    if GeneralSettings.objects.using(DataBase).filter(SettingsType='VAT',SettingsValue=True).exists():
        is_VAT = True
    if GeneralSettings.objects.using(DataBase).filter(SettingsType='GST',SettingsValue=True).exists():
        is_GST = True

    taxType_data = None
    if is_VAT:
        if TransactionTypes.objects.using(DataBase).filter(BranchID=BranchID,MasterTypeID=8,Name=TaxType).exists():
            taxType_data = TransactionTypes.objects.using(DataBase).get(BranchID=BranchID,MasterTypeID=8,Name=TaxType)
    if is_GST:
        if TransactionTypes.objects.using(DataBase).filter(BranchID=BranchID,MasterTypeID=7,Name=TaxType).exists():
            taxType_data = TransactionTypes.objects.using(DataBase).get(BranchID=BranchID,MasterTypeID=7,Name=TaxType)
    
    if taxType_data:
        TaxID = taxType_data.id
        return TaxID
    else:
        return ""

# @register.filter
# def Balance(account_ledger):
    
#     ledgerPostInstances = LedgerPosting.objects.filter(BranchID=account_ledger.BranchID,LedgerID=account_ledger.LedgerID)

#     Balance = 0
#     for ledgerPostInstance in ledgerPostInstances:
#         Debit = ledgerPostInstance.Debit
#         Credit = ledgerPostInstance.Credit
#         Balance = (float(Balance) + float(Debit)) - float(Credit)

#     return Balance


@register.filter
def Balance(instance):
    for i in instance:
        Debit = i.Debit
        Credit = i.Credit
        Balance = Debit - Credit

    return Balance


@register.filter
def AccountGroupName(instance):
    AccountGroupUnder = instance.AccountGroupUnder
    if AccountGroup.objects.filter(AccountGroupID=AccountGroupUnder).exists():
        group_instance = AccountGroup.objects.get(AccountGroupID=AccountGroupUnder)
        AccountGroupName = group_instance.AccountGroupName
            
        return AccountGroupName
    else:
        return ""


# @register.filter
# def DesignationName(instance):
#     DesignationID = instance.DesignationID
#     BranchID = instance.BranchID
#     if Designation.objects.filter(DesignationID=DesignationID,BranchID=BranchID).exists():
#         designation_instance = Designation.objects.get(DesignationID=DesignationID,BranchID=BranchID)
#         DesignationName = designation_instance.DesignationName
#         return DesignationName
#     else:
#         return ""


@register.filter    
def check_default(value):
    result = value
    if value == "default":
        result = "-"
    return result