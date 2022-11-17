from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid
# 

class DatabaseStore(models.Model):
    DefaultDatabase = models.TextField(blank=True,null=True)
    DatabaseName = models.TextField(blank=True,null=True)
    CompanyName = models.TextField(blank=True,null=True)
    Address1 = models.TextField(blank=True,null=True)
    Address2 = models.TextField(blank=True,null=True)
    Address3 = models.TextField(blank=True,null=True)
    username = models.TextField(blank=True,null=True)
    password = models.TextField(blank=True,null=True)
    city = models.TextField(blank=True,null=True)
    state = models.TextField(blank=True,null=True)
    country = models.TextField(blank=True,null=True)
    postalcode = models.TextField(blank=True,null=True)
    phone = models.TextField(blank=True,null=True)
    mobile = models.TextField(blank=True,null=True)
    email = models.EmailField(max_length=128,blank=True,null=True)
    website = models.TextField(blank=True,null=True)
    currency = models.BigIntegerField(blank=True,null=True)
    fractionalunit = models.BigIntegerField(blank=True,null=True)
    vatnumber = models.BigIntegerField(blank=True,null=True)
    gstnumber = models.BigIntegerField(blank=True,null=True)
    tax1 = models.BigIntegerField(blank=True,null=True)
    tax2 = models.BigIntegerField(blank=True,null=True)
    tax3 = models.BigIntegerField(blank=True,null=True)
    customerid = models.PositiveIntegerField(db_index=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    host = models.TextField(blank=True,null=True)
    port = models.TextField(blank=True,null=True)
    is_process = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)
    is_financial_year = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'db_store'
        verbose_name = _('db_store')
        verbose_name_plural = _('db_stores')
        

    def __str__(self):
        return self.CompanyName


# class Customer(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     Email = models.EmailField(max_length=128,blank=True,null=True)
#     FirstName = models.TextField(blank=True,null=True)
#     LastName = models.TextField(blank=True,null=True)
#     Country = models.TextField(blank=True,null=True)
#     MobileNumber = models.TextField(blank=True,null=True)
#     Password = models.TextField(blank=True,null=True)
#     RegistrationDate = models.DateTimeField(auto_now_add=True)
#     IsRegistered = models.BooleanField(default=False)
#     ExpiryDate = models.DateTimeField()
#     NoOfDb = models.PositiveIntegerField()
#     NoOfUsers = models.PositiveIntegerField()
    
#     class Meta:
#         db_table = 'customer'
#         verbose_name = _('customer')
#         verbose_name_plural = _('customers')
        

    # def __str__(self):
    #     return self.FirstName


class CustomerUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    databaseid = models.TextField(blank=True,null=True)
    email = models.EmailField(max_length=128,blank=True,null=True)
    username  = models.TextField(blank=True,null=True)
    password  = models.TextField(blank=True,null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField("auth.user",blank=True,null=True, on_delete=models.CASCADE)

    class Meta:
        db_table = 'customer_user'
        verbose_name = _('customer user')
        verbose_name_plural = _('customer users')
        

    def __str__(self):
        return self.username


class CompanyEmployee(models.Model):
    EmployeeID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    CompanyID = models.BigIntegerField()
    Action = models.CharField(max_length=128,blank=True,null=True,default="A")
    FirstName = models.CharField(max_length=128,blank=True,null=True)
    LastName = models.CharField(max_length=128,blank=True,null=True)
    DesignationID = models.BigIntegerField(blank=True,null=True)
    DepartmentID = models.BigIntegerField(blank=True,null=True)
    Gender = models.CharField(max_length=128,blank=True,null=True)
    Email = models.EmailField(blank=True,null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True,null=True)
    CreatedUserID = models.BigIntegerField(blank=True,null=True)
    EmployeeCode = models.CharField(max_length=128,blank=True,null=True)


    class Meta:
        db_table = 'users_employees'
        verbose_name = _('user employees')
        verbose_name_plural = _('user employeess')
        ordering = ('-CreatedDate','EmployeeID')

    def __unicode__(self):
        return str(self.EmployeeID)

class CompanyAccountLedger(models.Model):
    CompanyID = models.BigIntegerField()
    LedgerID = models.BigIntegerField()
    BranchID = models.BigIntegerField()
    LedgerName  = models.CharField(max_length=128)
    LedgerCode  = models.CharField(max_length=128,blank=True,null=True)
    AccountGroupUnder = models.BigIntegerField(blank=True,null=True)
    OpeningBalance = models.DecimalField(default=0.00,max_digits=20,decimal_places=8,blank=True,null=True)
    CrOrDr  = models.CharField(max_length=128,blank=True,null=True)
    Notes = models.TextField(blank=True,null=True)
    IsActive = models.BooleanField(default=True)
    IsDefault = models.BooleanField(default=False)
    CreatedUserID = models.BigIntegerField(blank=True,null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True,null=True)
    Action = models.CharField(max_length=128,blank=True,null=True,default="A")

    class Meta:
        db_table = 'users_company_AccountLedger'
        verbose_name = _('account Ledger')
        verbose_name_plural = _('account Ledgers')
        unique_together = (('LedgerID', 'BranchID'),)
        ordering = ('-CreatedDate','LedgerID')

    def __unicode__(self):
        return str(self.LedgerID)


class CompanyFinancialYear(models.Model):
    FinancialYearID = models.BigIntegerField()
    CompanyID = models.BigIntegerField()
    Action = models.CharField(max_length=128,blank=True,null=True,default="A")
    FromDate = models.DateField(blank=True,null=True)
    ToDate = models.DateField(blank=True,null=True)
    IsClosed = models.BooleanField(default=False)
    Notes = models.TextField(blank=True,null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(blank=True,null=True)
    CreatedUserID = models.BigIntegerField(blank=True,null=True)

    
    class Meta:
        db_table = 'company_financialYear_financialYear'
        verbose_name = _('companyfinancialYear')
        verbose_name_plural = _('companyfinancialYears')
        ordering = ('-FinancialYearID',)

    def __unicode__(self):
        return str(self.FinancialYearID)

# class CustomerUser(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     BranchID = models.BigIntegerField(blank=True,null=True)
#     UserTypeID = models.BigIntegerField(blank=True,null=True)
#     Action  = models.TextField(blank=True,null=True)
#     UserName  = models.TextField(blank=True,null=True)
#     Password  = models.TextField(blank=True,null=True)
#     EmployeeID = models.BigIntegerField(blank=True,null=True)
#     Cash_Account = models.BigIntegerField(blank=True,null=True)
#     Bank_Account = models.BigIntegerField(blank=True,null=True)
#     Warehouse = models.BigIntegerField(blank=True,null=True)
#     Sales_Account = models.BigIntegerField(blank=True,null=True)
#     Sales_Return_Account = models.BigIntegerField(blank=True,null=True)
#     Purchase_Account = models.BigIntegerField(blank=True,null=True)
#     Purchase_Return_Account = models.BigIntegerField(blank=True,null=True)
#     Sales_GST_Type = models.BigIntegerField(blank=True,null=True)
#     Purchase_GST_Type = models.BigIntegerField(blank=True,null=True)
#     VAT_Type = models.BigIntegerField(blank=True,null=True)
#     IsActive = models.BooleanField(default=False)
#     CreatedUserID = models.BigIntegerField(blank=True,null=True)
#     ExpiryDate = models.DateField()
#     CreatedDate = models.DateTimeField(auto_now_add=True)
#     user=models.OneToOneField("auth.user",blank=True,null=True, on_delete=models.CASCADE)
    
#     class Meta:
#         db_table = 'customer_user'
#         verbose_name = _('customer_user')
#         verbose_name_plural = _('customer_users')
        

#     def __str__(self):
#         return self.UserName